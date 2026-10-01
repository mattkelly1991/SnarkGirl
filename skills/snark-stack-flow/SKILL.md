---
name: snark-stack-flow
description: "Use when the user addresses SnarkGirl by name and wants a whole stack of PRs taken to done, bottom-up: run the full PR feedback loop (open Copilot, Claude, CodeQL, and human findings; fix valid ones; rebut and resolve invalid ones; user commits and pushes; re-request Copilot) on one PR until it is done, sync that PR up through every PR above it (Merge Court on conflicts), then move to the next PR. Tracks progress in a resumable per-stack TODO table. Trigger phrases: 'SnarkGirl, run the stack flow', 'SnarkGirl, take the stack to done', 'SnarkGirl, slay the stack', '@SnarkGirl stack flow'."
---

# Stack Flow — Slay the Stack, One PR at a Time 🥞🔁💅

A stack of PRs is only as done as its lowest unfinished PR. This skill is a nested loop:

- **Outer loop:** walk the stack bottom-up. For each PR, run the inner loop until the PR is done, then sync it up through every PR above it. Only then move up.
- **Inner loop:** the `snark-pr-flow` cycle on exactly one PR. Gather, triage, fix, validate, user pushes, resolve, re-request Copilot, and repeat until the done condition holds on the current head commit.

This skill orchestrates. It does not reimplement anything:

- The inner loop follows `snark-pr-flow` (triage rules, reply format, minimization classifiers, validation scope, manual-test handoff, per-PR ledger). Everything below adds to or tightens that skill for stack use.
- Syncing uses `snark-stack-sync`'s script, `{skills_dir}/snark-stack-sync/assets/sync-pr-stack.ps1`, with the same exit-code contract (`0` done, `1` guard tripped, `2` conflict).
- Waiting for Copilot uses this skill's script, `{skill_dir}/assets/wait-copilot-review.ps1` (see Copilot Requests and Waits).
- Gathering feedback uses this skill's script, `{skill_dir}/assets/pr-feedback-snapshot.ps1` (see Step 1).
- Conflicts go to `snark-merge-court`.

## When This Skill Activates

- The user wants every PR in a stack driven to done, not just one PR's reviews handled and not just the stack merged up
- The user wants the review-fix-push-rereview cycle repeated per PR with syncs in between
- The user resumes a previously started stack flow

For a single PR, use `snark-pr-flow`. For a merge-up with no review work, use `snark-stack-sync`.

## Non-Negotiable Rules

1. **Bottom-up, one PR at a time.** Only the current PR (the lowest unfinished one) is worked on. Never triage, reply to, resolve, fix, hide, re-request reviews on, or declare done any PR above it. A sync changes every higher PR's head, so any review, approval, or green CI they had beforehand is stale.
2. **Only the user commits and pushes fixes.** SnarkGirl edits files, validates, and hands off. Stack Flow never commits fix work.
3. **Sync merges are the one exception.** The sync script may commit merges with `git commit --no-edit` (git's default merge message: no custom text, no trailers, no attribution) and push them, but only after user approval as described under Outer Loop.
4. **Never push to `dev`, `main`, or `master`,** and never merge the stack's base into the root once any PR is done (see Base Drift).
5. **Never create a worktree.** Work in the current checkout. Switching between branches of *this* stack is part of the flow and is allowed only when the tree is clean and the local branch has no commits missing from its remote. Otherwise stop and tell the user.
6. **Preserve unrelated local changes.** Same as `snark-pr-flow`.
7. **Never use `@` before a username in GitHub text.**
8. **Never hide the final Copilot review of a done PR.** The one exception is case C, described below.
9. **Waivers come only from the user.** SnarkGirl never waives a CI failure on her own authority.
10. **Every state change goes in the stack ledger before the turn ends.** If it isn't in the ledger, it didn't happen.

## The Stack Ledger (Persistent TODO Table)

One ledger per stack, stored in the user's home directory rather than the repository or a temp directory, so it survives breaks, restarts, temp cleanup, new sessions, and context resets:

`~/.copilot/snark-girl/stacks/{owner}-{repo}-stack-{root PR number}.md`

The root PR is the bottom of the stack when the run starts. The file keeps that name even if the root later merges. When the host also provides a session TODO store, mirror the table rows there, but the file is the source of truth.

Per-PR finding detail (thread IDs, verdicts, reply and resolution state, summary-comment node IDs) lives in each PR's `snark-pr-flow` ledger. During a stack flow, keep those ledgers next to the stack ledger instead of in a temp directory, at `~/.copilot/snark-girl/stacks/{owner}-{repo}-stack-{root PR number}/PR-{number}.md`. The stack ledger links to them instead of duplicating them.

### Ledger contents

1. **Header:** repository, stack base branch, root PR, run start time, and the base branch tip SHA at start.
2. **Stack table:** one row per PR, bottom to top, with these columns:

   | # | PR | Branch | Loop | Sync | Head SHA | Notes |
   |---|----|--------|------|------|----------|-------|

   - **Loop:** `pending`, `in progress (iter N)`, `awaiting push`, `awaiting Copilot`, `copilot unavailable`, `skipped (copilot unavailable)`, `done (A)`, `done (B)`, `done (C)`, `reopened`, or `merged`.
   - **Sync:** `pending`, `awaiting approval`, `in progress`, `in court`, `awaiting resolution approval`, `done`, `n/a` (top of stack), or `merged`.
   - **Head SHA:** the head commit on which the PR was declared done. Blank until done.
   - **Notes:** open thread IDs being worked, the per-PR ledger path, the time of the latest confirmed Copilot request, Copilot error counts, known issues, blockers, and user decisions.
3. **Current step pointer:** the PR and the exact step of the inner or outer loop that is next.
4. **Waived CI failures:** each entry records the check or job name, the exact failure signature taken from the completed run's failed-step log (the failing step, test, or rule identifier plus the normalized error text), the user's reason, and when it was granted. Waivers last for this run only.
5. **Loop guard:** for each invalid Copilot finding that recurs, a fingerprint (file, symbol, and the substance of the claim, not line numbers or wording), the Copilot review IDs and head SHAs where it appeared, and the count.
6. **Standing approvals:** whether the user pre-approved clean syncs for this run.

### Showing the table

Render the stack table in chat at every transition: when a PR's loop reaches done, when a sync completes, when the flow moves to the next PR, when a PR is reopened, when the flow starts or resumes, and when the stack is finished. Show only the table and a one-line status between transitions. The ledger holds the detail.

## Startup and Resume

1. Identify the repository and a PR in the stack. Use one the user supplied, or the current branch's PR, or ask.
2. Discover the stack with the sync script's `-DryRun` (no `-AboveOnly`). If the script refuses (fork, cycle, closed PR), relay it and stop.
3. Look for an existing ledger for this repository whose stack table contains any PR in the discovered stack.
   - **None found:** create the ledger with every PR set to `pending`, and set the top PR's Sync to `n/a`.
   - **Found:** resume. Reconcile the ledger against live GitHub and git state before doing anything:
     - PRs that have merged become `merged` in both columns and drop out of the working order.
     - A PR that is now in the stack but missing from the ledger, or a changed parent/child order, means the stack structure changed. Show the difference and ask how to proceed.
     - For every PR marked done, apply When Done Goes Stale, and move the current step pointer to the lowest reopened PR.
     - A PR marked `copilot unavailable` resumes at its Copilot request. A `skipped` PR stays skipped until the user asks to revisit it.
     - A merge in progress on a stack branch means the flow stopped mid-sync. Resume at the conflict or approval step for that sync.
     - Otherwise resume at the first unfinished step: the lowest PR whose Loop isn't done, or the lowest done PR whose Sync isn't done.
4. On a fresh run, if any PR in the stack doesn't contain its base tip, report which ones. Ask once whether to run a full stack sync (no `-AboveOnly`) first. This is the only point in the run where the root's base may be merged in, because no PR has been declared done yet.
5. Show the table and state where the flow is starting.

## Inner Loop — One PR to Done

Before the first iteration on a PR, check out its head branch (rule 5), confirm the local and remote heads match, and create or reopen its `snark-pr-flow` ledger.

### Step 1 — Gather

Every iteration starts from a fresh snapshot of the PR, never from what an earlier iteration saw. Copilot is the only reviewer the flow waits for, but feedback from every other reviewer counts once it appears. Other bots and humans post on their own schedules, often between Copilot rounds.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File {skill_dir}/assets/pr-feedback-snapshot.ps1 -Pr <N> -Head <sha> [-Since <previous snapshotAt>] [-Repo owner/name]
```

(Use `pwsh -NoProfile -File ...` where `powershell` isn't available.) The script pages through everything with GraphQL variables and `ConvertFrom-Json`, and prints one JSON object. Exit `0` is a snapshot. Exit `6` means the head moved; restart this step on the new head. Exit `1` is a persistent gh/GitHub failure; relay it and stop.

The snapshot is filtered by nothing except resolution state and time:

- `unresolvedThreads`: every unresolved review thread from every author (outdated threads included), regardless of age
- `reviews` and `comments`: review bodies and PR conversation comments from every author, at or after `-Since`. Pass the previous iteration's `snapshotAt` so nothing posted in between is skipped. Overlap is harmless because items are tracked by node ID in the per-PR ledger.
- `checks`: pending, failed, and succeeded checks and statuses on the head
- `codeScanning`: open code-scanning alerts for the PR, when the repository exposes them
- `pendingReviewers`: outstanding review requests
- `byAuthor`: who the returned items came from

Triage everything it returns, whoever posted it: Copilot, any other bot or app, and every human. Never narrow the gather to a fixed list of reviewers. Separately, parse the latest Copilot review's inline findings **and** the "Previously missed" items in its summary body. Each "Previously missed" item is a finding. Also include check annotations from failed checks.

Record the `snapshotAt` in the per-PR ledger.

If the PR has no Copilot review on its current head, request one (see Copilot Requests and Waits), triage whatever the snapshot already holds, and wait (Step 5).

### Step 2 — Triage and act

Triage every finding against current code, exactly as in `snark-pr-flow` Phase 3:

- **Valid:** fix locally and leave the thread open. When the correct fix belongs in code owned by a lower, already-done PR, stop and ask: fixing it there reopens that PR and every PR above it.
- **Invalid thread:** reply with a concise technical rebuttal in the `snark-pr-flow` reply format, then resolve it.
- **Invalid "Previously missed" item:** no reply. Record it in the per-PR ledger and the loop guard. It still counts toward the done check.
- **Duplicate / needs user decision:** as in `snark-pr-flow`.

Update the loop guard for every invalid Copilot finding. A finding matches an existing fingerprint when it makes the same substantive claim about the same code, even if the wording or line changed.

**CI failures:**

- Judge a run only after it has completed. While a run is in progress its logs are partial, so a signature search can report a false "no match". A run that is queued or in progress is pending, not failed and not waived.
- Take the signature from the completed run's failed-step log (for GitHub Actions, `gh run view <run id> --log-failed`), never from the full log of a run in progress.
- A failed run counts as waived only when **every** failing job in it matches a waiver, and each match is exact: the same check or job and the same failure signature. Anything else is a new failure. That includes the same check failing for a different reason, an extra failing job, or a check whose failure log can't be retrieved.
- A failure caused by the PR's code is a valid finding. Fix it in this iteration.
- A failure that appears unrelated (infrastructure, flakiness, a pre-existing break) gets investigated from its logs. Report it with evidence and ask the user whether to rerun it, waive it (record the signature), or fix it. Never rerun or waive on your own.

### Step 3 — Validate and hand off

If this iteration changed code:

1. Run the smallest relevant validation from `snark-pr-flow` Phase 4 (compile, build, targeted tests, scoped format verification).
2. Give the `snark-pr-flow` manual-test list.
3. Set Loop to `awaiting push`, record the open valid thread IDs in Notes, show the table, and **stop the turn**. The user commits and pushes.

If the user reports a manual-test failure, handle it as in `snark-pr-flow` Phase 6 and stay in this step.

If this iteration changed no code (every finding was invalid or already handled), skip the handoff and go to Step 4 with the current head.

### Step 4 — After the push: verify, resolve, hide, re-request

When the user confirms the push:

1. Refresh the remote head SHA. Confirm the remote head contains every fix recorded for this iteration. The local fix commits must be ancestors of the remote head, and the fixed issues must be absent in the remote head's code. If anything is missing, report it and return to Step 3's pause.
2. Resolve each fixed valid thread with no reply, as in `snark-pr-flow` Phase 7.
3. Minimize fully handled standalone and summary comments with the truthful classifier from `snark-pr-flow`.
4. Hide the superseded Copilot review summary as `RESOLVED` once all of its findings are handled. The summary becomes superseded the moment a new Copilot review is requested.
5. Request a new Copilot review for the current head and confirm it through GraphQL, as described in Copilot Requests and Waits.
6. Set Loop to `awaiting Copilot`.

With no code change, a new review targets the same head SHA. That is expected and is how case C accumulates evidence.

### Step 5 — Wait, then loop

Wait with the wait script (see Copilot Requests and Waits). Only a review on the current head that was submitted after the latest Copilot request counts. Reviews on older commits, or from earlier rounds on the same commit, don't count.

When CI on the head has completed and the review has arrived, return to Step 1 for a fresh snapshot. That snapshot picks up whatever any other reviewer posted while Copilot was working. Evaluate the done condition only after everything in it is triaged. If it isn't met, increment the iteration and continue the loop.

## Copilot Requests and Waits

Never hand-write a polling loop, and never embed `jq` expressions in PowerShell. Quoting breaks silently, and the loop polls nothing. Use the script, which passes GraphQL variables with `-f`/`-F` and parses results with `ConvertFrom-Json`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File {skill_dir}/assets/wait-copilot-review.ps1 -Pr <N> -CheckRequest
powershell -NoProfile -ExecutionPolicy Bypass -File {skill_dir}/assets/wait-copilot-review.ps1 -Pr <N> -Head <sha> [-TimeoutMin 20] [-IntervalSec 30] [-Since <ISO time>] [-Repo owner/name]
```

(Use `pwsh -NoProfile -File ...` where `powershell` isn't available.) The script prints one JSON object on stdout, including the review's ID, URL, state, commit, and body when there is one. Progress goes to stderr.

**Confirming a request.** The REST response to a reviewer request never lists the Copilot bot, so it proves nothing. After requesting, run `-CheckRequest`, which reads GraphQL `reviewRequests`:

- Exit `0`: Copilot is listed as a pending reviewer. Record GitHub's request time (`lastRequestedAt` in the output) in Notes.
- Exit `5`: Copilot isn't listed. Re-request once and check again. If it still isn't listed, report it and ask the user. Never wait on a request that didn't register.

**Waiting.** `-Since` defaults to GitHub's timestamp for the latest Copilot request, so leave it unset unless the ledger has a more precise reason to override it.

| Exit | Meaning | What SnarkGirl does |
|------|---------|---------------------|
| `0` | A Copilot review on the head arrived | Go to Step 1 with it |
| `3` | Timed out; the request is still pending | Update the ledger, report, and stop the turn. The next invocation resumes the wait |
| `4` | Copilot posted an error review instead of reviewing | Handle as Copilot unavailable, below |
| `5` | No pending request and no qualifying review | The request was dropped. Request and confirm again, then wait |
| `6` | The PR's head moved during the wait | Re-evaluate from Step 1 on the new head |
| `1` | Bad arguments or a persistent gh/GitHub failure | Relay the error and stop |

**Copilot unavailable.** An error review is not a review. It never counts toward any done case, and it never counts as a loop-guard repeat.

1. On the first error for this head, record it in Notes, re-request, confirm, and wait once more.
2. If Copilot errors again on the same head, set Loop to `copilot unavailable`, show the table, and ask the user to choose:
   - **Wait:** stop the turn. When the flow is invoked again, it re-requests, confirms, and waits.
   - **Skip:** set Loop to `skipped (copilot unavailable)`. The PR is never done while skipped. Continue to the sync step only if every other part of the done condition holds on the current head. Otherwise stay on the PR. Wrap-up lists every skipped PR as not done.

## Done Condition

A PR is done only when **all** of the following hold at the same moment, for the PR's current head SHA:

1. **CI:** every check has completed, and each one either succeeded or belongs to a failed run whose failing jobs all match waivers exactly (see CI failures in Step 2). Nothing is queued or in progress.
2. **Threads and feedback:** a snapshot taken on the current head, after the latest Copilot review arrived, shows no unresolved review threads from any author. Every review body, conversation comment, and code-scanning alert in it, whoever posted it, has been triaged and handled.
3. **Copilot:** the latest Copilot review was submitted on the current head SHA, and it satisfies one of these cases:
   - **A:** zero findings, where "Previously missed" items count as findings.
   - **B:** every finding is invalid (rebutted and resolved, or recorded when it's "Previously missed"), and the verdict is anything other than "Changes recommended". If no verdict can be identified, B doesn't apply.
   - **C:** Copilot is looping. The latest review repeats an invalid finding whose loop-guard fingerprint has appeared more than twice, and every other finding in that review is invalid.

A review or approval on any older commit never satisfies the condition, no matter how green it looked.

If the head moves at any point after evaluation (a new push, an external commit), re-evaluate from Step 1.

**On done:**

- **A or B:** leave the latest Copilot review visible. It is the proof.
- **C:** hide the latest Copilot review, and post one PR conversation comment in the SnarkGirl reply format stating that Copilot is repeating an already-rebutted finding and the review loop has been stopped. Name the finding in plain words. Don't use `@`.
- Record the case and the head SHA in the table, set Loop to `done (A|B|C)`, show the table, and move to the outer loop's sync step.

A `CHANGES_REQUESTED` review from a human that remains after all threads are resolved blocks done. Report it. Never dismiss another reviewer's review.

## When Done Goes Stale

A done PR is pinned to the Head SHA recorded when it was declared done. **Any** change to its remote head reopens it, whatever the cause: the PR's own new commits, a sync merge into it (including its base merged in by the flow, the user, or GitHub's update-branch button), a rebase, or a force push. Only moving the head matters. Reviews, CI, and approvals on the old head no longer count.

- The flow never moves a done PR's head itself. `-AboveOnly` only merges into PRs above the current one, and those are never done. Merging the base into the root is forbidden once any PR is done. So a moved head means a change from outside the flow, or a lower PR reopened and its sync cascaded up.
- Compare every done PR's recorded Head SHA with its remote head at every transition (before and after each sync, before moving to the next PR, at wrap-up) and on resume.
- A PR whose head moved gets Loop `reopened` and loses its done case and Head SHA. The lowest reopened PR becomes current. When its sync later pushes merges into done PRs above it, their heads move and they reopen by the same rule.

## Outer Loop — Sync Up, Then Move Up

After the current PR is done, or skipped by the user's choice (see Copilot unavailable):

1. **Top of stack:** there's nothing to sync. The stack is finished (see Wrap-Up).
2. **Otherwise, sync upward only.** Run the sync script with `-Pr <current> -AboveOnly`. That merges the current head into its child and on up the stack, and never touches the current PR or anything below it, so every done PR keeps the head SHA it was approved on.
   - Before the first push, show the `-DryRun -AboveOnly` plan and get the user's go-ahead. The plan marks each branch as up to date or needing a merge, and a merge anywhere means every branch above it needs one too. If every branch is already up to date, record the sync as `done` without asking. If the user granted standing approval for clean syncs this run, record it and proceed without asking. Conflict resolutions always need explicit approval.
   - **Exit `0`:** record the sync as `done`.
   - **Exit `2`:** set Sync to `in court` and resolve with `snark-merge-court`. Present the resolution, set `awaiting resolution approval`, show the table, and **stop the turn**. Only after the user explicitly approves, run the script again with `-Pr <current> -AboveOnly -Continue`. Repeat for each conflict further up.
   - **Exit `1`:** relay the guard error, record it as a blocker, and stop. Never work around a guard.
3. After the sync, the next PR up becomes current. Its previous Copilot reviews, approvals, and CI results are stale, and the inner loop starts fresh on it. Its first iteration needs a Copilot review on its new head.
4. Show the table and continue with the next PR's inner loop.

## Base Drift

Once any PR is done, the flow never merges the stack's base (e.g., `dev`) into the root. That would change every head and throw away every done result. If the base moves during the run, note it in the ledger header and report it at wrap-up. If branch protection or CI needs the root to be up to date with its base, surface that as a blocker and ask the user. A full sync from the root reopens every PR.

## Wrap-Up

When the top PR is done or skipped, show the final table and one short summary: each PR's done case, every skipped PR (not done), the syncs that needed court, active waivers, base drift, and anything left open. Keep the ledger file, since it records how the stack reached done.

## Things SnarkGirl Would Never Do

- Touch, review, or declare done any PR above the current one
- Count an approval or green CI from an older head commit
- Count a Copilot error review, or a skipped PR, as done
- Hand-write a Copilot polling loop or embed `jq` in PowerShell instead of using the wait script
- Gather only Copilot's feedback, or any fixed list of reviewers, instead of everything from every author
- Declare done from a snapshot taken before the latest Copilot review arrived
- Trust the REST response as proof that Copilot was requested
- Match a waiver against a run that hasn't completed
- Keep a PR done after its head moved
- Commit or push fix work for the user
- Continue a conflicted sync without the user approving the resolution
- Merge the base into the root after any PR has been declared done
- Hide the final Copilot review of a done PR except in case C
- Waive, ignore, or rerun a CI failure without the user's decision
- Leave the ledger out of date at the end of a turn
- Restart a stack from scratch when a ledger for it exists
- Use the `@` symbol before a username in anything posted to GitHub
