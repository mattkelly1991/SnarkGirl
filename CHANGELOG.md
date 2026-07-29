# Changelog

All notable changes to **SnarkGirl** are documented here. 💅

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to `1.15.1` were shipped untagged; their history below is
> reconstructed from git commits, so dates are accurate but per-patch detail is summarized.

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
