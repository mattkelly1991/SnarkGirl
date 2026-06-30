# Changelog

All notable changes to **SnarkGirl** are documented here. 💅

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to `1.15.1` were shipped untagged; their history below is
> reconstructed from git commits, so dates are accurate but per-patch detail is summarized.

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
