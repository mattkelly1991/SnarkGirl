# Changelog

All notable changes to **SnarkGirl** are documented here. 💅

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to `1.15.1` were shipped untagged; their history below is
> reconstructed from git commits, so dates are accurate but per-patch detail is summarized.

## [1.19.2] - 2026-10-01

### Added
- `snark-stack-flow/assets/pr-feedback-snapshot.ps1` — paginated GraphQL snapshot of all
  PR feedback from every author (Copilot, any other bot or app, and humans): unresolved
  threads, review bodies, conversation comments, checks, pending reviewers, and open
  code-scanning alerts. `-Since` limits reviews/comments to new activity; `-Head` exits `6`
  if the head moved. No `jq`; parses with `ConvertFrom-Json`.

### Fixed
- Stack Flow missed feedback from Claude, code-quality, and other bots or humans posted
  between Copilot rounds. Every iteration now starts from a fresh snapshot of everything
  from every author, taken after the latest Copilot review, and done requires it to be clean.
- PR Flow's gather step now explicitly covers every author instead of a fixed reviewer list.

## [1.19.1] - 2026-09-29

### Added
- `snark-stack-flow/assets/wait-copilot-review.ps1` — tested poller that waits for a
  Copilot review on a given head (`-Pr N -Head <sha> -TimeoutMin 20`). Queries GraphQL
  with `-f`/`-F` variables and parses with `ConvertFrom-Json` (no `jq` inside PowerShell).
  Counts only reviews submitted after the latest Copilot request. Exit `0` review on head,
  `3` timeout, `4` Copilot errored, `5` not requested, `6` head moved. `-CheckRequest`
  confirms a request through GraphQL `reviewRequests`.

### Fixed
- `sync-pr-stack.ps1 -DryRun` now fetches remote refs and reports "up to date" when a
  branch already contains its base, instead of always printing "would merge".

### Changed
- Stack Flow: confirm Copilot requests via GraphQL (the REST response never lists the
  bot) and re-request once if missing; use the wait script instead of hand-rolled polls.
- Stack Flow: CI waivers are matched only against completed runs using `--log-failed`;
  a run is waived only when every failing job matches a waiver exactly.
- Stack Flow: new `copilot unavailable` / `skipped (copilot unavailable)` states — retry
  once on a Copilot error review, then ask the user to wait or skip. Never counted as done.
- Stack Flow: new "When Done Goes Stale" rules — any move of a done PR's head (its own
  commits, a sync or base merge, rebase, force push) reopens it; checked at every transition.
- Stack Flow: ledgers now live in `~/.copilot/snark-girl/stacks/` instead of the temp
  directory, so they survive restarts and cleanup.

## [1.19.0] - 2026-09-29

### Added
- **Stack Flow** skill (`snark-stack-flow`) — takes a whole PR stack to done, bottom-up,
  as a nested loop. The inner loop runs the `snark-pr-flow` cycle on one PR at a time:
  gather open Copilot (including "Previously missed"), Claude, CodeQL, and human findings
  plus CI; fix valid ones; rebut and resolve invalid ones; the user commits and pushes;
  verify the push, silently resolve fixed threads, hide the superseded Copilot summary,
  and re-request Copilot on the new head. A PR is done only when CI is green (or every
  failure matches a user-waived signature), no threads are open, and the latest Copilot
  review *on the current head* has zero findings, only invalid findings with a
  non-"Changes recommended" verdict, or is looping on the same rebutted finding more than
  twice (in which case it is hidden and a looping note is posted). The outer loop then
  syncs that PR up through every PR above it (Merge Court on conflicts, user approval
  before continuing) and moves up one PR. Progress lives in a resumable per-stack ledger
  outside the repo, shown at every transition; re-invoking resumes at the first
  unfinished step and reopens any done PR whose head moved.
- `sync-pr-stack.ps1 -AboveOnly` — syncs only the PRs stacked above `-Pr`, leaving `-Pr`
  and everything below it (including the root's base) untouched, so PRs already taken to
  done keep the head commit they were approved on.

### Fixed
- `sync-pr-stack.ps1 -Continue` refused to finish a merge whose conflicts had been
  resolved but not staged, because unmerged index entries were counted as conflicts
  before `git add` ran. A conflicted file now counts as resolved once it has no conflict
  markers left, so Merge Court's edits can be continued directly, as documented.

### Changed
- Skill routing (`using-snark-girl`, `CLAUDE.md`) gained `snark-stack-flow` right before
  `snark-pr-flow`.
- Plugin descriptions, keywords, and README mention Stack Flow.

## [1.18.1] - 2026-09-18

### Fixed
- `sync-pr-stack.ps1` — single-line git output (`branch --show-current`, `rev-parse --git-dir`,
  `log --format=%s`) was being unrolled by PowerShell on `return`, so `[0]` read the first
  *character* instead of the first line. The merge subject printed as `M` and, worse,
  `-Continue` saw the current branch as `3` and would have refused a legitimate resume.
  All three reads are now wrapped in `@()`.

## [1.18.0] - 2026-09-18

### Added
- **Stack Sync** skill (`snark-stack-sync`) — brings a stack of PRs up to date with its
  base, bottom-up: merge `dev` into the first PR, then each PR into the next.
  `assets/sync-pr-stack.ps1` discovers the chain from open PRs via `gh pr list` (any PR
  in the stack works as the entry point), refuses forks/cycles/dirty trees/unpushed local
  commits/protected branches, fetches and checks out each head, merges its base with
  `git merge --no-edit`, and pushes clean merges immediately. Merge messages are git's
  default `Merge branch 'dev' into <branch>` — identical to GitHub's "Update branch" —
  with no custom text or attribution. On conflicts the script exits `2` with the merge
  in progress; SnarkGirl runs Merge Court, the user approves the resolution, and
  `-Continue` commits (`--no-edit`), pushes, and finishes the stack. Stateless: position
  is re-derived from git every run, so re-running is always safe. `-DryRun` previews.

### Changed
- Skill routing (`using-snark-girl`, `CLAUDE.md`) gained `snark-stack-sync` right after
  `snark-merge-court`.
- Plugin descriptions and keywords across all manifests mention Stack Sync.

## [1.17.0] - 2026-09-17

### Added
- **Settings** skill (`snark-settings`) — SnarkGirl now has a persistent memory for
  preferences. Settings live in `~/.snarkgirl/settings.json` (override the directory
  with `SNARKGIRL_HOME`) and are managed only through `assets/settings.py`
  (`get` / `set` / `reset` / `list` / `describe` / `path`). Every setting is declared
  in a schema registry with its allowed values and default, so unknown keys and
  out-of-range values are rejected; writes are atomic. Any skill with a tunable reads
  its value fresh via `get` each time it runs.
- **Divergence** skill (`snark-divergence`) — SnarkGirl's own take on parallel divergent
  ideation, based on [UditAkhourii/adhd](https://github.com/UditAkhourii/adhd). For
  open-ended problems (design, naming, API surface, architecture, fuzzy bugs) she spawns
  N isolated agents under distorted cognitive frames with zero shared context, then a
  separate critic pass scores (novelty / viability / fit), clusters by angle, flags
  traps with reasons, deepens the survivors, and commits to a verdict.
- **`divergence` setting** — `off` (default) / `low` / `medium` / `high`. Controls the
  frames × ideas shape and whether Divergence auto-runs on qualifying questions
  (`medium`: open-ended + high-stakes + open phrasing; `high`: only the phrasing check).
  `off` never auto-runs but still honors explicit "diverge on this" requests.

### Changed
- Skill routing (`using-snark-girl`, `CLAUDE.md`) gained `snark-settings` (priority 2,
  right after `snark-mode`) and `snark-divergence`, plus a Persistent Settings section
  describing how skills read settings.
- Plugin descriptions and keywords across all manifests mention Divergence and settings.

## [1.16.1] - 2026-07-29

### Added
- **Handled review-summary minimization** to the PR Flow skill. SnarkGirl now tracks
  top-level Claude, bot, and human summary comments and minimizes them only after every
  represented finding is fully handled.
- Classifier-aware cleanup using `RESOLVED`, `OUTDATED`, `DUPLICATE`, or `OFF_TOPIC`
  according to the comment's actual final state, with GraphQL result verification.

### Changed
- Inline review comments continue to use normal thread resolution; minimization is
  reserved for standalone PR comments and aggregate review summaries.

## [1.16.0] - 2026-07-29

### Added
- **PR Flow** skill — an end-to-end workflow for existing pull requests that gathers
  unresolved Claude, Copilot, CodeQL, and human findings; triages them against current
  code; replies to and resolves invalid threads; and fixes valid findings in the current
  checkout without creating worktrees.
- A two-stage resolution gate for valid feedback: SnarkGirl validates the affected
  projects and hands off a focused manual test list, then waits for the user to commit and
  push before verifying the PR head and resolving the fixed threads without noisy replies.
- A temporary per-PR flow ledger so review-thread IDs, verdicts, fixes, validation, and
  post-push resolution state survive the manual-testing pause without polluting the repo.

### Changed
- Skill routing and documentation now distinguish the action-oriented `snark-pr-flow`
  lifecycle from review-only, clap-back, and review-document workflows.

## [1.15.3] - 2026-07-01

### Changed
- **World Cup now stores the tournament in the repo Wiki** instead of a portable token.
  The Wiki (its own git repo) holds a signed, human-readable page hierarchy —
  **World Cup → Season → Match**: a `Home` index of seasons, a `Season-{slug}` standings
  page each, and one `Season-{slug}-Match-{N}` report per PR. The user names the season
  (and its duration) at kickoff.
- Each wiki page carries a keyed **HMAC signature footer** covering the whole page, so a
  hand-edit in the GitHub wiki editor (e.g. changing a win from 3 to 4) is flagged
  **INVALID** by `wiki.py verify`. Export a private `SGWC_SECRET` for a real barrier.
- Resuming a season is now just "clone the wiki" — no HEAD memory or token paste needed.
- **The live pitch actually plays now.** Players roam their formation and pass the ball,
  holding their shape at each kickoff until someone takes it. A goal is scripted end-to-end:
  the ball is worked to the scorer (matched by name or id), who drives at the net and buries
  it. A red card sets up a **penalty kick** — a code red is converted, an agent red is saved
  by the keeper. Sent-off players walk to a **bench** at the edge (home top-left, away
  top-right). Card badges show only on booked players still on the pitch (a red badge is
  dropped once the player is benched). Runs on `requestAnimationFrame`, independent of the
  ~2s polls.
- **The trophy moved to the wiki.** Champion and awards present on the wiki season page; the
  live arena ends on the standings view (the trophy screen is now replay-only).

### Added
- `skills/snark-world-cup/assets/wiki.py` — renders/signs the Home index, season, and match
  pages; `verify`/`verify-all` for tamper checks; and `load-season` to resume standings.

### Removed
- `skills/snark-world-cup/assets/token.py` — the portable token chain, replaced by the
  wiki ledger.

## [1.15.2] - 2026-06-30

### Changed
- **World Cup** model redesign: a **team is now the person** (a persistent club, named
  consistently per handle), the **PR is the one-off opponent** (ranked off the table via
  `--away-ephemeral`), the home XI is named after the **agents** and the away XI after the
  **code units** (files / methods / assemblies).
- **Red cards no longer auto-lose.** A *code* red (committed secret / security hole) sends
  off the unit and adds a Critical to the scoreline; an *agent* red (a hallucinated or
  false-positive finding) benches the bot with no goal against the author. Results are now
  purely score-driven.
- Carding cuts both ways — SnarkGirl can book her own agents for bogus findings (and asks
  the user when she's unsure).

### Fixed
- Corrected inverted `SIDE_NAMES` in `gm.py` (home is the club, away is the PR) and removed
  the obsolete `--red-loser` auto-loss flag.

## [1.15.1] - 2026-06-30 — *First official release* 🎉

### Changed
- Rebranded the GitHub Action: renamed from `SnarkGirl Mentions` to `SnarkGirl`,
  refreshed the Marketplace description, and switched the branding icon to a purple star ⭐.
- Scoped goal-celebration CSS in the World Cup arena to avoid style bleed.

### Notes
- First tagged release and first published release notes. 21 skills across
  Claude, Codex, Cursor, and Gemini, plus the GitHub Action.

## [1.15.0] - 2026-06-30

### Added
- **World Cup** skill — a multiplayer PR-review football tournament played out live
  on an animated pitch, with standings and a tamper-evident token chained across
  ticket/PR comments so the season can travel.

## [1.14.2] - 2026-06-19

### Added
- `gm.py` Game Master helper for Battle Royale.

### Changed
- Seed contestant counts per-zone and clamp the roster to 10–16.

## [1.14.1] - 2026-06-17

### Changed
- Updated SKILL docs and metadata.

## [1.14.0] - 2026-06-17

### Added
- **Reality Check** skill — surfaces the real size and risk of a PR by cutting
  through misleading raw diff stats (read-only analysis).

## [1.13.1] - 2026-06-16

### Changed
- Expanded live-arena behavior in the Battle Royale SKILL docs.

## [1.13.0] - 2026-06-12

### Changed
- Battle Royale arena fixes and gameplay polish: tighter hunger rules and UI cleanup.

## [1.12.0] - 2026-06-11

### Added
- Battle Royale replays, animations, sound, and an improved arena UI.

## [1.11.1] - 2026-06-11

### Changed
- Improved arena template setup.

## [1.11.0] - 2026-06-11

### Added
- Live web arena spectator view for Battle Royale.

## [1.10.0] - 2026-06-11

### Added
- **Battle Royale** skill — 10–16 AI contestants drop onto your code, hunt real
  bugs to survive, fight each other, and starve if they find nothing. Last one standing wins.

## [1.9.1] - 2026-05-28

### Changed
- Clarified SKILL rules.

## [1.9.0] - 2026-05-25

### Added
- **The Gauntlet Supreme** skill — Council attacks, Sisterhood defends, repeat,
  then SnarkGirl delivers a final verdict.

## [1.8.1] - 2026-05-22

### Added
- PR comment posting support.

## [1.8.0] - 2026-05-21

### Added
- **The Sisterhood** skill — a squad that defends your PR against council reviews
  and heavy critique.

## [1.7.0] - 2026-05-21

### Added
- **PR Council** skill — deep multi-agent review of an existing PR.

## [1.6.0] - 2026-05-18

### Added
- **Council** skill — pre-PR AI gauntlet that scales agents to scope and loops until clean.

## [1.5.0] - 2026-05-08

### Added
- **Conscience** skill — SnarkAngel vs SnarkDevil debate a dilemma.

## [1.4.0] - 2026-05-07

### Added
- **Merge Court** skill — LLM attorneys argue *ours* vs *theirs* while SnarkGirl judges.

### Changed
- Removed `@` mentions from generated comments to avoid triggering notifications/bots.
- Clarified reply formatting.

## [1.3.0] - 2026-05-06

### Added
- **Snark Mode** skill — toggle persistent SnarkGirl so you don't have to say her name.

## [1.2.0] - 2026-05-06

### Added
- **vs The World** skill — SnarkGirl debates other real LLMs until someone concedes.

### Changed
- Quoting rules, staleness checks, and demo/example polish.

## [1.1.0] - 2026-05-04

### Added
- **Branch Review**, **Fix Review**, **Devil's Advocate**, **Clap Back**, and
  **Ticket** skills.
- GitHub Action for `@SnarkGirl` mentions in PRs and issues.

### Changed
- Renamed package to SnarkGirl, prefixed all skills with `snark-`, added the
  contributing guide and keyword/metadata sync.

## [1.0.0] - 2026-05-04 — *Initial commit*

### Added
- Initial Snark Girl plugin, core skills, and docs:
  **PR Review**, **Explain**, **Rubber Duck**, and **Chat**.

[1.15.1]: https://github.com/mattkelly1991/SnarkGirl/releases/tag/v1.15.1
