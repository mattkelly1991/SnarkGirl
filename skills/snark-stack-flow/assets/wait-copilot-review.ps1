<#
.SYNOPSIS
    Waits for a Copilot pull request review on a specific head commit, or checks whether Copilot's review request is pending.

.DESCRIPTION
    Polls GitHub GraphQL (via `gh api graphql` with -f/-F variables; no jq) and parses results with ConvertFrom-Json.

    A Copilot review counts only when it was submitted on -Head, after -Since, and was not dismissed. -Since
    defaults to GitHub's own timestamp for the most recent Copilot review request on the PR, so reviews from
    earlier rounds on the same commit never satisfy a new wait and local clock skew does not matter.

    Progress goes to stderr. The final result is one JSON object on stdout.

    Exit codes:
      0  A Copilot review on -Head arrived (with -CheckRequest: Copilot's review request is pending)
      1  Bad arguments or a gh/GitHub failure that persisted across retries
      3  Timed out while Copilot's review request was still pending
      4  Copilot posted an error review on -Head instead of a real review
      5  Copilot has no pending review request and no qualifying review exists (request it, then wait again)
      6  The PR's head moved away from -Head while waiting (re-evaluate on the new head)

.PARAMETER Pr
    Pull request number.

.PARAMETER Head
    Head commit SHA the review must be on (full SHA or an unambiguous prefix of at least 7 characters).

.PARAMETER Repo
    owner/name. Defaults to the repository gh resolves for the current directory.

.PARAMETER Since
    ISO 8601 timestamp. Only reviews submitted at or after it count. Defaults to the latest Copilot review request.

.PARAMETER TimeoutMin
    Minutes to wait while the request is pending (default 20).

.PARAMETER IntervalSec
    Seconds between polls (default 30).

.PARAMETER CheckRequest
    Do not wait: report whether Copilot's review request is pending (exit 0) or not (exit 5).

.EXAMPLE
    .\wait-copilot-review.ps1 -Pr 42 -Head 1a2b3c4d5e6f -TimeoutMin 20

.EXAMPLE
    .\wait-copilot-review.ps1 -Pr 42 -CheckRequest
#>

param(
    [Parameter(Mandatory=$true)]
    [int]$Pr,

    [string]$Head,

    [string]$Repo,

    [string]$Since,

    [double]$TimeoutMin = 20,

    [int]$IntervalSec = 30,

    [switch]$CheckRequest
)

$ErrorActionPreference = "Stop"
$CopilotLogin = '^copilot-pull-request-reviewer(\[bot\])?$'
$ErrorBody = 'Copilot encountered an error|unable to review this pull request|wasn''t able to review'
$Query = (@'
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      headRefOid
      reviewRequests(first: 100) { nodes { requestedReviewer { __typename ... on Bot { login } } } }
      timelineItems(last: 100, itemTypes: [REVIEW_REQUESTED_EVENT]) {
        nodes { ... on ReviewRequestedEvent { createdAt requestedReviewer { __typename ... on Bot { login } } } }
      }
      reviews(last: 100) { nodes { id databaseId url state submittedAt body author { login } commit { oid } } }
    }
  }
}
'@ -split "`r?`n" | ForEach-Object { $_.Trim() }) -join ' '

function Write-Log([string]$Message) { [Console]::Error.WriteLine("==> $Message") }

function Stop-With([int]$Code, [hashtable]$Result) {
    $Result.exitCode = $Code
    [Console]::Out.WriteLine(($Result | ConvertTo-Json -Depth 5 -Compress))
    exit $Code
}

function Fail([string]$Message) { Stop-With 1 @{ status = "error"; message = $Message } }

function ConvertTo-Utc($Value) {
    # Windows PowerShell leaves ISO strings as strings; PowerShell 7's ConvertFrom-Json turns them into DateTime.
    if ($null -eq $Value -or "$Value" -eq "") { return $null }
    if ($Value -is [DateTime]) { return ([DateTimeOffset]$Value).ToUniversalTime() }
    return [DateTimeOffset]::Parse("$Value", [Globalization.CultureInfo]::InvariantCulture).ToUniversalTime()
}

function Invoke-Gh {
    $ErrorActionPreference = "Continue"
    $output = & gh @args 2>$null
    $script:GhExitCode = $LASTEXITCODE
    return (@($output) -join "`n")
}

function Get-PullRequest {
    $failures = 0
    while ($true) {
        $json = Invoke-Gh api graphql -f "query=$Query" -f "owner=$script:Owner" -f "name=$script:Name" -F "number=$Pr"
        if ($script:GhExitCode -eq 0 -and $json) {
            $pull = ($json | ConvertFrom-Json).data.repository.pullRequest
            if ($pull) { return $pull }
        }
        $failures++
        if ($failures -ge 3) { Fail "GraphQL query for $script:Owner/$script:Name#$Pr failed $failures times in a row." }
        Write-Log "GraphQL query failed; retrying in 10s"
        Start-Sleep -Seconds 10
    }
}

function Get-State($Pull) {
    $pending = @($Pull.reviewRequests.nodes | Where-Object {
        $_.requestedReviewer -and $_.requestedReviewer.__typename -eq "Bot" -and $_.requestedReviewer.login -match $CopilotLogin
    }).Count -gt 0

    $requests = @($Pull.timelineItems.nodes | Where-Object {
        $_.requestedReviewer -and $_.requestedReviewer.login -match $CopilotLogin
    } | ForEach-Object { ConvertTo-Utc $_.createdAt } | Sort-Object)
    $lastRequest = if ($requests.Count -gt 0) { $requests[$requests.Count - 1] } else { $null }

    $reviews = @($Pull.reviews.nodes | Where-Object {
        $_.author -and $_.author.login -match $CopilotLogin -and $_.submittedAt -and $_.state -ne "DISMISSED"
    } | Sort-Object { ConvertTo-Utc $_.submittedAt })

    return @{ Pending = $pending; LastRequest = $lastRequest; Reviews = $reviews }
}

function Format-Time($Value) { if ($null -eq $Value) { return $null } return $Value.ToString("o") }

if (-not $Repo) {
    $repoJson = Invoke-Gh repo view --json nameWithOwner
    if ($script:GhExitCode -ne 0 -or -not $repoJson) { Fail "Could not resolve the repository; pass -Repo owner/name." }
    $Repo = ($repoJson | ConvertFrom-Json).nameWithOwner
}
if ($Repo -notmatch '^[^/\s]+/[^/\s]+$') { Fail "-Repo must be owner/name." }
$script:Owner, $script:Name = $Repo -split '/', 2

if ($CheckRequest) {
    $pull = Get-PullRequest
    $state = Get-State $pull
    $result = @{
        status = $(if ($state.Pending) { "pending" } else { "not-requested" })
        repo = $Repo; pr = $Pr; head = $pull.headRefOid
        lastRequestedAt = Format-Time $state.LastRequest
    }
    if ($state.Pending) { Stop-With 0 $result }
    Stop-With 5 $result
}

if (-not $Head -or $Head -notmatch '^[0-9a-fA-F]{7,40}$') { Fail "-Head must be a commit SHA (7-40 hex characters)." }
$Head = $Head.ToLowerInvariant()
$sinceOverride = $null
if ($Since) {
    try { $sinceOverride = ConvertTo-Utc $Since } catch { Fail "-Since is not a valid timestamp: $Since" }
}

$deadline = [DateTimeOffset]::UtcNow.AddMinutes($TimeoutMin)
$misses = 0
Write-Log "Waiting up to $TimeoutMin min for a Copilot review of $Repo#$Pr on $Head"

while ($true) {
    $pull = Get-PullRequest
    $state = Get-State $pull
    $currentHead = "$($pull.headRefOid)".ToLowerInvariant()
    $cutoff = if ($sinceOverride) { $sinceOverride } else { $state.LastRequest }
    $base = @{ repo = $Repo; pr = $Pr; head = $Head; since = Format-Time $cutoff }

    if (-not $currentHead.StartsWith($Head)) {
        $base.status = "head-moved"; $base.currentHead = $currentHead
        Stop-With 6 $base
    }

    $matching = @($state.Reviews | Where-Object {
        "$($_.commit.oid)".ToLowerInvariant().StartsWith($Head) -and
            ($null -eq $cutoff -or (ConvertTo-Utc $_.submittedAt) -ge $cutoff)
    })

    if ($matching.Count -gt 0) {
        $review = $matching[$matching.Count - 1]
        $isError = "$($review.body)" -match $ErrorBody
        $base.status = $(if ($isError) { "copilot-error" } else { "reviewed" })
        $base.review = @{
            id = $review.id; databaseId = $review.databaseId; url = $review.url; state = $review.state
            submittedAt = Format-Time (ConvertTo-Utc $review.submittedAt); commit = $review.commit.oid; body = $review.body
        }
        if ($isError) { Stop-With 4 $base }
        Stop-With 0 $base
    }

    if (-not $state.Pending) {
        # A just-submitted review can briefly lag the removal of its request, so confirm once before giving up.
        $misses++
        if ($misses -ge 2) {
            $base.status = "not-requested"
            Stop-With 5 $base
        }
        Start-Sleep -Seconds ([Math]::Min($IntervalSec, 10))
        continue
    }
    $misses = 0

    if ([DateTimeOffset]::UtcNow -ge $deadline) {
        $base.status = "timeout"
        Stop-With 3 $base
    }
    Write-Log "Copilot review still pending; next check in ${IntervalSec}s"
    Start-Sleep -Seconds $IntervalSec
}
