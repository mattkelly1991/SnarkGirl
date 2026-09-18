<#
.SYNOPSIS
    Brings a stack of PRs up to date with its base, bottom-up.

.DESCRIPTION
    Discovers the PR stack containing -Pr from open GitHub PRs (a PR whose base is another open PR's head is
    stacked on it). Walks the stack from the root: fetches, checks out each PR head, and merges its base into it
    with git's default merge message ("Merge branch 'dev' into <branch>"). Clean merges are pushed immediately.
    On conflicts the script stops with exit code 2 and leaves the merge in progress; resolve the conflicts, review,
    then re-run with -Continue to commit (--no-edit), push, and carry on with the rest of the stack.

    Position is derived from git state on every run — there is no ledger. Re-running is always safe.

.PARAMETER Pr
    Any PR number in the stack.

.PARAMETER Continue
    A merge is in progress and its conflicts have been resolved and approved: stage, commit with the default
    message, push, then continue up the stack.

.PARAMETER Remote
    Remote name (default: origin).

.PARAMETER DryRun
    Print the discovered stack and planned actions without touching the working tree.

.EXAMPLE
    .\sync-pr-stack.ps1 -Pr 3499

.EXAMPLE
    .\sync-pr-stack.ps1 -Pr 3499 -Continue

.EXAMPLE
    .\sync-pr-stack.ps1 -Pr 3499 -DryRun
#>

param(
    [Parameter(Mandatory=$true)]
    [int]$Pr,

    [switch]$Continue,

    [string]$Remote = "origin",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProtectedBranches = @("dev", "main", "master")

function Write-Step([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }
function Write-Ok([string]$Message) { Write-Host "    $Message" -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host "    $Message" -ForegroundColor Yellow }
function Fail([string]$Message, [int]$Code = 1) { Write-Host "ERROR: $Message" -ForegroundColor Red; exit $Code }

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$GitArgs)
    # git writes progress to stderr; under Stop, 2>&1 would turn that into a terminating error.
    $ErrorActionPreference = "Continue"
    $output = & git @GitArgs 2>&1
    $script:GitExitCode = $LASTEXITCODE
    return @($output | ForEach-Object { "$_" })
}

function Assert-Git {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$GitArgs)
    $output = Invoke-Git @GitArgs
    if ($script:GitExitCode -ne 0) {
        Fail "git $($GitArgs -join ' ') failed:`n$($output -join "`n")"
    }
    return $output
}

function Get-HeadSubject {
    return @(Assert-Git log -1 "--format=%s")[0]
}

function Get-ConflictedFiles {
    return @(Invoke-Git diff --name-only --diff-filter=U | Where-Object { $_ })
}

function Test-MergeInProgress {
    $gitDir = @(Assert-Git rev-parse --git-dir)[0]
    return Test-Path (Join-Path $gitDir "MERGE_HEAD")
}

function Get-Stack {
    $json = & gh pr list --state open --limit 200 --json number,baseRefName,headRefName
    if ($LASTEXITCODE -ne 0) { Fail "gh pr list failed" }
    if (-not $json) { Fail "gh pr list returned nothing (auth or repo detection failed?)" }
    $prs = $json | ConvertFrom-Json
    $byNumber = @{}
    $byHead = @{}
    foreach ($p in $prs) {
        $byNumber[[int]$p.number] = $p
        if ($byHead.ContainsKey($p.headRefName)) {
            Fail "Two open PRs share head branch '$($p.headRefName)' (#$($byHead[$p.headRefName].number), #$($p.number))"
        }
        $byHead[$p.headRefName] = $p
    }

    if (-not $byNumber.ContainsKey($Pr)) { Fail "PR #$Pr is not an open PR" }

    # Walk down to the root
    $stack = New-Object System.Collections.Generic.List[object]
    $current = $byNumber[$Pr]
    $seen = @{}
    while ($true) {
        if ($seen.ContainsKey([int]$current.number)) { Fail "Cycle detected in PR stack at #$($current.number)" }
        $seen[[int]$current.number] = $true
        $stack.Insert(0, $current)
        if ($byHead.ContainsKey($current.baseRefName)) {
            $current = $byHead[$current.baseRefName]
        } else {
            break
        }
    }

    # Walk up through children
    $current = $stack[$stack.Count - 1]
    while ($true) {
        $children = @($prs | Where-Object { $_.baseRefName -eq $current.headRefName })
        if ($children.Count -eq 0) { break }
        if ($children.Count -gt 1) {
            $list = ($children | ForEach-Object { "#$($_.number) ($($_.headRefName))" }) -join ", "
            Fail "Stack forks at '$($current.headRefName)': $list. Sync one branch of the fork by passing its PR number."
        }
        $current = $children[0]
        if ($seen.ContainsKey([int]$current.number)) { Fail "Cycle detected in PR stack at #$($current.number)" }
        $seen[[int]$current.number] = $true
        $stack.Add($current)
    }

    return $stack
}

function Show-Stack($stack) {
    Write-Host ""
    Write-Host "  $($stack[0].baseRefName)" -ForegroundColor DarkGray
    foreach ($p in $stack) {
        Write-Host "   -> #$($p.number)  $($p.headRefName)"
    }
    Write-Host ""
}

function Sync-Head([string]$Head) {
    if ($ProtectedBranches -contains $Head) { Fail "Refusing to touch protected branch '$Head'" }

    Assert-Git fetch $Remote $Head | Out-Null
    $remoteRef = "$Remote/$Head"
    Invoke-Git rev-parse --verify --quiet "refs/heads/$Head" | Out-Null
    $localExists = $script:GitExitCode -eq 0

    if ($localExists) {
        Invoke-Git merge-base --is-ancestor $Head $remoteRef | Out-Null
        if ($script:GitExitCode -ne 0) {
            Fail "Local '$Head' has commits that are not on $remoteRef. Push or reset them first."
        }
    }

    Assert-Git checkout -B $Head $remoteRef | Out-Null
}

function Update-BaseRef([string]$Base, [string]$Head) {
    # Update the local base ref so the merge message reads "Merge branch '<base>' into <head>", matching GitHub.
    Assert-Git fetch $Remote "${Base}:${Base}" | Out-Null
}

function Complete-Merge([string]$Head) {
    $conflicts = Get-ConflictedFiles
    if ($conflicts.Count -gt 0) {
        Write-Warn "Conflicts remain in '$Head':"
        $conflicts | ForEach-Object { Write-Host "      $_" }
        exit 2
    }
    Assert-Git add -A | Out-Null
    Assert-Git commit --no-edit | Out-Null
    Write-Ok "Committed: $(Get-HeadSubject)"
    Assert-Git push $Remote $Head | Out-Null
    Write-Ok "Pushed $Head"
}

# --- Main ---

Assert-Git rev-parse --is-inside-work-tree | Out-Null

$stack = Get-Stack
Write-Step "Stack for #$Pr"
Show-Stack $stack

if ($DryRun) {
    foreach ($p in $stack) {
        Write-Host "  would merge '$($p.baseRefName)' into '$($p.headRefName)' and push"
    }
    exit 0
}

$currentBranch = @(Assert-Git branch --show-current)[0]

if (Test-MergeInProgress) {
    if (-not $Continue) {
        $conflicts = Get-ConflictedFiles
        if ($conflicts.Count -gt 0) {
            Write-Warn "A merge with conflicts is in progress on '$currentBranch':"
            $conflicts | ForEach-Object { Write-Host "      $_" }
            Write-Warn "Resolve them, review, then re-run with -Continue."
        } else {
            Write-Warn "A resolved merge is in progress on '$currentBranch'. Re-run with -Continue to commit and push."
        }
        exit 2
    }
    $onStack = $stack | Where-Object { $_.headRefName -eq $currentBranch }
    if (-not $onStack) { Fail "Merge in progress on '$currentBranch', which is not part of this stack." }
    Write-Step "Completing merge on '$currentBranch'"
    Complete-Merge $currentBranch
} else {
    if ($Continue) { Write-Warn "No merge in progress; ignoring -Continue." }
    $dirty = @(Invoke-Git status --porcelain | Where-Object { $_ })
    if ($dirty.Count -gt 0) { Fail "Working tree is not clean. Commit or stash your changes first." }
}

foreach ($p in $stack) {
    $head = $p.headRefName
    $base = $p.baseRefName
    Write-Step "#$($p.number)  $base -> $head"

    Sync-Head $head
    Update-BaseRef $base $head

    Invoke-Git merge-base --is-ancestor $base HEAD | Out-Null
    if ($script:GitExitCode -eq 0) {
        Write-Ok "Already up to date"
        continue
    }

    Invoke-Git merge --no-edit $base | Out-Null
    if ($script:GitExitCode -ne 0) {
        $conflicts = Get-ConflictedFiles
        if ($conflicts.Count -eq 0) { Fail "git merge $base failed for a reason other than conflicts." }
        Write-Warn "Conflicts merging '$base' into '$head':"
        $conflicts | ForEach-Object { Write-Host "      $_" }
        Write-Warn "Resolve them, review, then re-run with -Continue."
        exit 2
    }

    Write-Ok "Merged: $(Get-HeadSubject)"
    Assert-Git push $Remote $head | Out-Null
    Write-Ok "Pushed $head"
}

Write-Step "Stack is up to date"
exit 0
