<#
.SYNOPSIS
    Snapshots every open piece of PR feedback from every reviewer: any bot, app, or human.

.DESCRIPTION
    Queries GitHub GraphQL (via `gh api graphql` with -f/-F variables; no jq) with full pagination and parses results
    with ConvertFrom-Json. Nothing is filtered by reviewer identity: every author's feedback is returned.

    The snapshot contains:
      - unresolvedThreads: every unresolved review thread, outdated or not, from any author
      - reviews: submitted, non-dismissed reviews with a body or CHANGES_REQUESTED state (at or after -Since when given)
      - comments: non-minimized PR conversation comments (created or edited at or after -Since when given)
      - checks: pending, failed, and succeeded check runs and commit statuses on the head
      - pendingReviewers: review requests still outstanding (bots, users, teams)
      - codeScanning: open code-scanning alerts for the PR ref, when the repository exposes them
      - byAuthor: how many returned items each author has

    Progress goes to stderr. The result is one JSON object on stdout.

    Exit codes:
      0  Snapshot taken
      1  Bad arguments or a gh/GitHub failure that persisted across retries
      6  The PR's head moved away from -Head (re-evaluate on the new head)

.PARAMETER Pr
    Pull request number.

.PARAMETER Head
    Expected head commit SHA (full or a prefix of at least 7 characters). Optional; when given, a moved head exits 6.

.PARAMETER Repo
    owner/name. Defaults to the repository gh resolves for the current directory.

.PARAMETER Since
    ISO 8601 timestamp. Reviews and conversation comments older than this are omitted. Unresolved threads are always
    returned in full, because they are open work regardless of age.

.EXAMPLE
    .\pr-feedback-snapshot.ps1 -Pr 42

.EXAMPLE
    .\pr-feedback-snapshot.ps1 -Pr 42 -Head 1a2b3c4d5e6f -Since 2026-01-01T00:00:00Z
#>

param(
    [Parameter(Mandatory=$true)]
    [int]$Pr,

    [string]$Head,

    [string]$Repo,

    [string]$Since
)

$ErrorActionPreference = "Stop"

function Compress-Query([string]$Text) { return (($Text -split "`r?`n" | ForEach-Object { $_.Trim() }) -join ' ') }

$MetaQuery = Compress-Query @'
query($owner: String!, $name: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      headRefOid
      reviewRequests(first: 100) {
        nodes { requestedReviewer { __typename ... on Bot { login } ... on User { login } ... on Mannequin { login } ... on Team { slug } } }
      }
    }
  }
}
'@

$ChecksQuery = Compress-Query @'
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      commits(last: 1) { nodes { commit { oid statusCheckRollup {
        contexts(first: 100, after: $after) {
          pageInfo { hasNextPage endCursor }
          nodes {
            __typename
            ... on CheckRun { name status conclusion detailsUrl databaseId checkSuite { app { slug } } }
            ... on StatusContext { context state targetUrl }
          }
        }
      } } } }
    }
  }
}
'@

$ThreadsQuery = Compress-Query @'
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line originalLine
          comments(first: 1) { totalCount nodes { databaseId url body createdAt author { __typename login } } }
          latest: comments(last: 1) { nodes { author { login } } }
        }
      }
    }
  }
}
'@

$ReviewsQuery = Compress-Query @'
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { id databaseId url state submittedAt updatedAt body author { __typename login } commit { oid } }
      }
    }
  }
}
'@

$CommentsQuery = Compress-Query @'
query($owner: String!, $name: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      comments(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { id databaseId url body createdAt updatedAt isMinimized minimizedReason author { __typename login } }
      }
    }
  }
}
'@

function Write-Log([string]$Message) { [Console]::Error.WriteLine("==> $Message") }

function Stop-With([int]$Code, [hashtable]$Result) {
    $Result.exitCode = $Code
    [Console]::Out.WriteLine(($Result | ConvertTo-Json -Depth 10 -Compress))
    exit $Code
}

function Fail([string]$Message) { Stop-With 1 @{ status = "error"; message = $Message } }

function ConvertTo-Utc($Value) {
    # Windows PowerShell leaves ISO strings as strings; PowerShell 7's ConvertFrom-Json turns them into DateTime.
    if ($null -eq $Value -or "$Value" -eq "") { return $null }
    if ($Value -is [DateTime]) { return ([DateTimeOffset]$Value).ToUniversalTime() }
    return [DateTimeOffset]::Parse("$Value", [Globalization.CultureInfo]::InvariantCulture).ToUniversalTime()
}

function Format-Time($Value) { if ($null -eq $Value) { return $null } return (ConvertTo-Utc $Value).ToString("o") }

function Invoke-Gh {
    $ErrorActionPreference = "Continue"
    $output = & gh @args 2>$null
    $script:GhExitCode = $LASTEXITCODE
    return (@($output) -join "`n")
}

function Invoke-GraphQL([string]$Query, [string]$After) {
    $failures = 0
    while ($true) {
        $ghArgs = @("api", "graphql", "-f", "query=$Query", "-f", "owner=$script:Owner", "-f", "name=$script:Name", "-F", "number=$Pr")
        if ($After) { $ghArgs += @("-f", "after=$After") }
        $json = Invoke-Gh @ghArgs
        if ($script:GhExitCode -eq 0 -and $json) {
            $parsed = $json | ConvertFrom-Json
            if ($parsed.data -and $parsed.data.repository -and $parsed.data.repository.pullRequest) { return $parsed.data }
        }
        $failures++
        if ($failures -ge 3) { Fail "GraphQL query for $script:Owner/$script:Name#$Pr failed $failures times in a row." }
        Write-Log "GraphQL query failed; retrying in 10s"
        Start-Sleep -Seconds 10
    }
}

function Get-AllNodes([string]$Query, [scriptblock]$Connection) {
    $nodes = @()
    $after = $null
    while ($true) {
        $data = Invoke-GraphQL $Query $after
        $conn = & $Connection $data
        if (-not $conn) { return $nodes }
        $nodes += @($conn.nodes | Where-Object { $_ })
        if (-not $conn.pageInfo.hasNextPage) { return $nodes }
        $after = $conn.pageInfo.endCursor
    }
}

function Get-CodeScanning {
    $json = Invoke-Gh api "repos/$script:Owner/$script:Name/code-scanning/alerts?ref=refs/pull/$Pr/head&state=open&per_page=100"
    if ($script:GhExitCode -ne 0 -or -not $json) { return @{ available = $false; alerts = @() } }
    # Windows PowerShell emits a parsed JSON array as one pipeline object, so enumerate it explicitly.
    $parsed = $json | ConvertFrom-Json
    $alerts = @($parsed | Where-Object { $_ } | ForEach-Object {
        $location = $_.most_recent_instance.location
        @{
            number = $_.number; url = $_.html_url; tool = $_.tool.name
            rule = $_.rule.id; severity = $(if ($_.rule.security_severity_level) { $_.rule.security_severity_level } else { $_.rule.severity })
            description = $_.rule.description; message = $_.most_recent_instance.message.text
            path = $location.path; line = $location.start_line
        }
    })
    return @{ available = $true; alerts = $alerts; truncated = ($alerts.Count -ge 100) }
}

function Get-Snapshot {
    $meta = Invoke-GraphQL $MetaQuery $null
    $viewer = $meta.viewer.login
    $pull = $meta.repository.pullRequest

    $pendingReviewers = @($pull.reviewRequests.nodes | Where-Object { $_.requestedReviewer } | ForEach-Object {
        $r = $_.requestedReviewer
        @{ type = $r.__typename; login = $(if ($r.login) { $r.login } else { $r.slug }) }
    })

    $contexts = Get-AllNodes $ChecksQuery {
        param($d)
        $commit = @($d.repository.pullRequest.commits.nodes)[0].commit
        if ($commit -and $commit.statusCheckRollup) { $commit.statusCheckRollup.contexts }
    }
    $pendingChecks = @(); $failedChecks = @(); $succeeded = 0
    foreach ($c in $contexts) {
        if ($c.__typename -eq "CheckRun") {
            $app = $(if ($c.checkSuite -and $c.checkSuite.app) { $c.checkSuite.app.slug } else { $null })
            $entry = @{ name = $c.name; app = $app; url = $c.detailsUrl; checkRunId = $c.databaseId; status = $c.status; conclusion = $c.conclusion }
            if ($c.status -ne "COMPLETED") { $pendingChecks += $entry }
            elseif (@("SUCCESS", "NEUTRAL", "SKIPPED") -contains $c.conclusion) { $succeeded++ }
            else { $failedChecks += $entry }
        }
        elseif ($c.__typename -eq "StatusContext") {
            $entry = @{ name = $c.context; url = $c.targetUrl; state = $c.state }
            if (@("PENDING", "EXPECTED") -contains $c.state) { $pendingChecks += $entry }
            elseif ($c.state -eq "SUCCESS") { $succeeded++ }
            else { $failedChecks += $entry }
        }
    }

    $threads = Get-AllNodes $ThreadsQuery { param($d) $d.repository.pullRequest.reviewThreads }
    $unresolved = @()
    foreach ($t in $threads) {
        if ($t.isResolved) { continue }
        $latest = @($t.latest.nodes)[0]
        $first = @($t.comments.nodes)[0]
        $unresolved += @{
            id = $t.id; path = $t.path; line = $(if ($t.line) { $t.line } else { $t.originalLine }); isOutdated = $t.isOutdated
            author = $(if ($first -and $first.author) { $first.author.login } else { $null })
            authorType = $(if ($first -and $first.author) { $first.author.__typename } else { $null })
            commentId = $(if ($first) { $first.databaseId } else { $null }); url = $(if ($first) { $first.url } else { $null })
            body = $(if ($first) { $first.body } else { $null }); createdAt = $(if ($first) { Format-Time $first.createdAt } else { $null })
            commentCount = $t.comments.totalCount
            latestAuthor = $(if ($latest -and $latest.author) { $latest.author.login } else { $null })
        }
    }

    $reviewNodes = Get-AllNodes $ReviewsQuery { param($d) $d.repository.pullRequest.reviews }
    $reviews = @()
    foreach ($r in $reviewNodes) {
        if (-not $r.submittedAt) { continue }
        $login = $(if ($r.author) { $r.author.login } else { $null })
        if ($r.state -eq "DISMISSED") { continue }
        if (-not "$($r.body)".Trim() -and $r.state -ne "CHANGES_REQUESTED") { continue }
        if ($script:SinceUtc -and (ConvertTo-Utc $r.submittedAt) -lt $script:SinceUtc) { continue }
        $reviews += @{
            id = $r.id; databaseId = $r.databaseId; url = $r.url; state = $r.state; author = $login
            authorType = $(if ($r.author) { $r.author.__typename } else { $null })
            submittedAt = Format-Time $r.submittedAt; commit = $(if ($r.commit) { $r.commit.oid } else { $null }); body = $r.body
        }
    }

    $commentNodes = Get-AllNodes $CommentsQuery { param($d) $d.repository.pullRequest.comments }
    $comments = @()
    foreach ($c in $commentNodes) {
        $login = $(if ($c.author) { $c.author.login } else { $null })
        if ($c.isMinimized) { continue }
        if ($script:SinceUtc -and (ConvertTo-Utc $c.updatedAt) -lt $script:SinceUtc) { continue }
        $comments += @{
            id = $c.id; databaseId = $c.databaseId; url = $c.url; author = $login
            authorType = $(if ($c.author) { $c.author.__typename } else { $null })
            createdAt = Format-Time $c.createdAt; updatedAt = Format-Time $c.updatedAt; body = $c.body
        }
    }

    $byAuthor = @{}
    foreach ($item in @($unresolved) + @($reviews) + @($comments)) {
        $key = $(if ($item.author) { $item.author } else { "(unknown)" })
        $byAuthor[$key] = 1 + $(if ($byAuthor.ContainsKey($key)) { $byAuthor[$key] } else { 0 })
    }

    return @{
        repo = "$script:Owner/$script:Name"; pr = $Pr; head = $pull.headRefOid; viewer = $viewer
        snapshotAt = [DateTimeOffset]::UtcNow.ToString("o"); since = Format-Time $script:SinceUtc
        checks = @{ pending = $pendingChecks; failed = $failedChecks; succeeded = $succeeded }
        pendingReviewers = $pendingReviewers
        unresolvedThreads = $unresolved; reviews = $reviews; comments = $comments
        codeScanning = Get-CodeScanning
        byAuthor = $byAuthor
    }
}

if (-not $Repo) {
    $repoJson = Invoke-Gh repo view --json nameWithOwner
    if ($script:GhExitCode -ne 0 -or -not $repoJson) { Fail "Could not resolve the repository; pass -Repo owner/name." }
    $Repo = ($repoJson | ConvertFrom-Json).nameWithOwner
}
if ($Repo -notmatch '^[^/\s]+/[^/\s]+$') { Fail "-Repo must be owner/name." }
$script:Owner, $script:Name = $Repo -split '/', 2

if ($Head) {
    if ($Head -notmatch '^[0-9a-fA-F]{7,40}$') { Fail "-Head must be a commit SHA (7-40 hex characters)." }
    $Head = $Head.ToLowerInvariant()
}
$script:SinceUtc = $null
if ($Since) {
    try { $script:SinceUtc = ConvertTo-Utc $Since } catch { Fail "-Since is not a valid timestamp: $Since" }
}

$snap = Get-Snapshot
if ($Head -and -not "$($snap.head)".ToLowerInvariant().StartsWith($Head)) {
    $snap.status = "head-moved"; $snap.expectedHead = $Head
    Stop-With 6 $snap
}
$snap.status = "snapshot"
Stop-With 0 $snap
