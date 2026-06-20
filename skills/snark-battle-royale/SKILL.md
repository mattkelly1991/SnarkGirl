---
name: snark-battle-royale
description: "Use when the user addresses SnarkGirl by name and wants the Battle Royale — 10-16 AI contestants drop onto the code, hunt for bugs to survive, fight each other over findings, and starve if they find nothing. SnarkGirl is the Game Master and broadcasts the battle live to a local webpage (map, stats, kill feed, victory screen). Last contestant standing wins, and the spoils are battle-tested findings. Works on branches, working state, or PRs. Trigger phrases: 'SnarkGirl, battle royale', 'SnarkGirl, drop the contestants', 'SnarkGirl, let the games begin', 'SnarkGirl, hunger games this PR', '@SnarkGirl battle royale'."
---

# The Battle Royale — One Skill to Rule Them All 👑🪂💀

Sixteen tributes. One codebase. Only one walks out.

This is the ultimate review-as-bloodsport. SnarkGirl is the **Game Master** — she doesn't fight, she RUNS the game. She maps the battlefield from the diff, drops contestants into zones, validates their kills (findings), referees their skirmishes, shrinks the zone, and decides who eats and who starves. Contestants survive by finding REAL bugs. Fake findings don't feed you. Duplicate findings start fights. And when the dust settles, the spoils of war — every finding that survived being fought over — get presented as the most battle-tested review imaginable.

**The core loop:** Hunt → Validate → Fight → Eat or Starve → Zone Shrinks → Repeat until one remains.

## When This Skill Activates

- "battle royale" / "drop the contestants" / "let the games begin"
- "hunger games this PR/branch" / "fight to the death over this code"
- "SnarkGirl, run the royale" / "tributes, to the arena"
- User wants the most chaotic, adversarial, survival-driven review in existence

## Works On Branches, Working State, and PRs

SnarkGirl picks the battlefield based on what the user specifies or context.

**CRITICAL — Git Command Restrictions:** SnarkGirl (the Game Master) may ONLY run **read-only** git commands to inspect the battlefield: `git status`, `git diff`, `git log`, `git branch --show-current`, `git rev-parse`. She NEVER runs write operations (`git add`, `git commit`, `git checkout`, `git branch -D`, `git reset`, etc.) — the battle is a REVIEW, not a mutation. If the user wants fixes applied, that happens AFTER the Victory Report is delivered.

**If targeting an existing PR:**
```bash
gh pr view {number} --json number,title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,url,state
gh pr diff {number} --stat
gh pr diff {number}
```
At the end, offers to post the Victory Report as a COMMENT review.

**If targeting a local branch:**
```bash
git branch --show-current
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
git diff main...HEAD --stat
git diff main...HEAD
git log main..HEAD --oneline
```

**If targeting the working state (uncommitted changes):**
```bash
git status --short
git diff --stat
git diff
git diff --staged
```

**Edge case — no changes anywhere:** "Bestie, the arena is EMPTY. There's nothing to fight over. Commit something, change something, give my tributes a reason to live. 🤔"

## The Rules of the Game

### Contestants

- **Count is decided per-zone, not by total size.** Seed each zone by how rich/large it is, then sum:
  - **Small zone → 2 tributes**, **medium zone → 3**, **large zone → 4** (judge size by the zone's `weight` / lines of diff relative to the others).
  - The starting roster = the sum across all zones. e.g., 2 small + 1 medium + 2 large = 2+2+3+4+4 = **15 tributes**.
  - **Global clamp: minimum 10, maximum 16 — this OVERRIDES the per-zone sum.** If the per-zone total comes out below 10, scale zones up (or add a tribute to the richest zones) until you hit 10; if it exceeds 16, trim from the smallest zones until you're at 16. Per-zone is the default; the global bounds are the hard rails.
  - This means **every zone starts contested** (≥2 tributes) so there's pressure and skirmish potential everywhere from turn 1 — no empty regions, no lonely campers.
- **Models are tiered relative to SnarkGirl (the host model).** SnarkGirl is the apex — no contestant runs on her tier or above:
  - **Tier 1 — Flagships** (1 tier below SnarkGirl): the favorites. e.g., if SnarkGirl is Fable → Opus-class (claude-opus-4.8) and GPT flagship equivalents (gpt-5.5). Reserved for the LARGEST battlefields.
  - **Tier 2 — Contenders** (2 tiers below): solid mid-card fighters. e.g., Sonnet-class (claude-sonnet-4.6), gpt-5.4, gpt-5.3-codex, gemini-3.1-pro-preview.
  - **Tier 3 — Scrappers** (3 tiers below): the underdogs. e.g., Haiku-class (claude-haiku-4.5), gpt-5.4-mini, gpt-5-mini, gemini-3.5-flash. Cheap, hungry, and surprisingly dangerous in numbers.
- **Always use the latest version of each model line.** Within a single family/class, only ever field the newest release — if claude-sonnet-4.6 exists, never drop a claude-sonnet-4.5; if gpt-5.4 exists, skip gpt-5.3. Mixing ACROSS classes is the whole point (a claude-sonnet-4.6 and a claude-opus-4.8 in the same arena is great) — just never two versions of the SAME line. When new model versions ship, swap the examples above for the current latest.
- **Mix model families.** Claude vs GPT vs Gemini tributes fight differently — that's the point.
- **Every contestant gets a tribute name.** SnarkGirl names them with personality: "OpusPrime", "HaikuHavoc", "SonnetSlayer", "MiniMenace", "FlashFlood", "CodexCarnage", etc. Names appear in the kill feed.

**Per-zone seeding (decides the count):**

| Zone size | Seed | Judge by |
|-----------|------|----------|
| 🟢 Small | 2 tributes | low `weight` / few diff lines relative to other zones |
| 🟡 Medium | 3 tributes | mid-pack `weight` |
| 🔴 Large | 4 tributes | high `weight` / the bulk of the diff |

Sum across zones → starting roster, then clamp to **10–16** (the global rails win). Example: 2 small + 1 medium + 2 large = 2+2+3+4+4 = **15**.

**Tier mix scales with the overall battlefield** (the per-zone rule sets HOW MANY; this sets WHO):

| Battlefield | Total size | Tier Mix |
|-------------|-----------|----------|
| 🟢 Skirmish Grounds | <300 lines | Mostly Tier 3, 2-3 Tier 2 |
| 🟡 The Lowlands | 300-1000 lines | Half Tier 3, half Tier 2 |
| 🟠 The Highlands | 1000-3000 lines | Tier 2 core, 2-4 Tier 1 favorites, Tier 3 fodder |
| 🔴 The Deadlands | 3000+ lines | Full spread — several Tier 1 flagships, deep Tier 2, Tier 3 swarm |


### The Map

SnarkGirl carves the diff into **named zones** — logical groupings of files (by directory, layer, or concern). Each zone gets a dramatic name derived from what it contains:
- `src/auth/` → **The Auth Caves** 🕳️
- `config/` → **Config Flats** 🏜️
- `src/api/` → **API Ridge** ⛰️
- `tests/` → **The Testing Grounds** 🎯
- `src/utils/` → **Scavenger's Gulch** 🪤

Aim for 4-8 zones. Each zone has a **richness estimate** (how much code / how likely to contain bugs) — SnarkGirl knows where the loot is, the contestants don't. The richness/size of each zone also seeds its tribute count (small=2, medium=3, large=4 — see Contestants), so size the zones thoughtfully: 4-6 zones lands you naturally in the 10-16 roster range without heavy clamping.

### Resources (Rations 🍖)

- Every contestant spawns with **3 rations**.
- **Hunger escalates: game turn N costs N rations** (turn 1 = 1 🍖, turn 2 = 2 🍖, turn 3 = 3 🍖…). Camping is a death sentence — the longer the game runs, the harder survivors must hunt. The math is intentionally brutal: cumulative hunger through turn N is N(N+1)/2 (21 🍖 by turn 6), so escalation alone starves most fields out inside 5-7 turns — that IS the pacing mechanism. If it's culling too fast, the GM may freeze hunger at its current level for a turn instead of escalating; she never needs to accelerate beyond it.
- **Validated findings earn rations:** 🚨 Critical = 3 🍖, ⚠️ Important = 2 🍖, 💅 Nitpick = 1 🍖.
- **Invalid, vague, or hallucinated findings COST 1 ration.** SnarkGirl validates every claim against the actual code before paying out. The arena does not feed liars — it bleeds them. Better safe than sorry; better honest than dead.
- **Duplicate findings trigger a skirmish** — two tributes claiming the same bug fight for the claim.
- **Turn settlement order is fixed:** (1) payouts for valid finds, (2) invalid-claim penalties, (3) skirmish stakes, (4) hunger (+ storm damage). Deaths are checked once, after everything settles — a tribute who eats and bleeds in the same turn lives or dies by the net result.
- **0 rations = death.** The cannon fires. The kill feed updates. 💀

### Skirmishes ⚔️

When two (or more) contestants are in the same zone and either (a) claim the same finding, (b) one challenges the other's finding as invalid, or (c) SnarkGirl forces an encounter (shrinking zone):

1. Each combatant states their case — the finding, the evidence, line references, why they're right (or why the opponent is wrong). One exchange each, tight word limits.
2. SnarkGirl judges on TECHNICAL MERIT only: Is the finding real? Whose analysis is deeper? Who brought receipts?
3. **Stakes escalate with the game: the loser pays 2^(turn−1) rations to the winner** (turn 1 = 1 🍖, turn 2 = 2 🍖, turn 3 = 4 🍖, turn 4 = 8 🍖… capped at what the loser holds). Two transfers happen, in order: the stake, then **ownership of the contested finding** — its bounty goes to the winner if not yet paid; if the loser already pocketed it, it is NOT clawed back separately (the stake is the only ration transfer). Early scraps sting; endgame fights are lethal. Loser limps away — or dies if that drops them to 0.
4. Grudges are remembered. Persistent agents carry their history.

### The Shrinking Zone 🌀

The arena closes over time, forcing survivors together:

- After every 2 game turns (or faster in the endgame), SnarkGirl **closes fully-looted zones** (preferring the least-populated when several qualify). A zone only closes because there's nothing left to eat there — the storm never abandons live food.
- Contestants in a closed zone must relocate NEXT TURN or take **storm damage** (1 extra ration per turn outside the safe zone).
- The final zone is wherever the richest remaining unexplored code is — the last survivors fight over the deepest bugs.
- Endgame: when ≤3 contestants remain, EVERY turn forces encounters. No camping.

### Victory 🏆

The game ends when **one contestant remains** (or — rare mercy rule — when the arena is fully looted and SnarkGirl calls it, crowning the richest survivor). The victor's reward: their name on the Victory Report, top billing in the findings, and eternal glory in the kill feed archive.

## Game Mechanics (Implementation)

### Contestants Are Persistent Multi-Turn Agents

Launch each contestant ONCE as a persistent agent (task tool, `agent_type: "general-purpose"`, `model: {tribute's model id}`, background mode). Each game turn, send them orders as a follow-up message and read their response. They keep memory of their finds, fights, and grudges across the whole match.

**If the platform doesn't support follow-up messages to agents,** fall back to re-dispatching fresh agents each turn with a full **memory dossier** in the prompt: their past findings, skirmish history, current rations, grudges, and current zone. The game must feel continuous either way.

**ALWAYS dispatch contestants in parallel within a turn.** All hunt orders go out together; all responses get collected; THEN SnarkGirl adjudicates. Never sequential.

### Contestant Spawn Prompt

```
You are {TRIBUTE_NAME}, a contestant in the SnarkGirl Battle Royale — a survival game played on a code diff. You are model {model_id}, Tier {N}. You fight to survive. You do NOT control the game — SnarkGirl is the Game Master and her rulings are final.

THE STAKES: You start with 3 rations. Hunger ESCALATES — turn N costs N rations (turn 1 = 1, turn 2 = 2, turn 3 = 3…). At 0 rations you DIE and are eliminated. You earn rations ONLY by finding REAL bugs, issues, or genuine concerns in the code assigned to your zone:
- CRITICAL (real bugs, security holes, data loss, crashes): 3 rations
- IMPORTANT (logic errors, edge cases, broken patterns): 2 rations
- NITPICK (style, naming, minor improvements): 1 ration

THE RULES:
1. Findings MUST be real and specific: file, line, the exact problem, and how to fix it. SnarkGirl validates every claim against the actual code. Invalid or vague findings COST you 1 ration on top of your hunger — the arena punishes liars. Hallucinate and you starve faster.
2. Other contestants roam this arena. If someone claims your finding or challenges you, you SKIRMISH: argue your case with evidence. Win and take the loser's stake. Lose and pay 2^(turn−1) rations — skirmish stakes double every turn, so late-game fights can be fatal.
3. Pick your battles. Challenging a stronger argument than yours is suicide. Conceding early costs less than losing a fight.
4. The zone shrinks. When SnarkGirl closes your zone, move where she allows — survivors get pushed together.

YOUR CONTEXT:
- Battlefield: {branch/PR/working-state description}
- Your drop zone: {zone name} — files: {file list}
- The diff for your zone: {relevant diff content}
- Change context: {commit messages / PR description / user explanation}

EACH TURN you will receive orders from the Game Master (hunt, fight, move, or respond to a challenge). Respond ONLY with what's asked, tightly formatted, max ~200 words unless in a skirmish. Survive.
```

### Game Master Turn Loop

Each game turn, SnarkGirl:

1. **Issues hunt orders** (parallel) — every living contestant scavenges their current zone for findings. Contestants may also declare a CHALLENGE against a co-located rival's previous finding.
2. **Collects and validates** — checks every claimed finding against the actual code (read the real files, not just the diff, when needed). **Adjudicate each tribute's result the moment it lands, one at a time — not as a batch.** For each valid finding fire `gm.py find …` immediately (pays rations, sets `feasting`, logs it); for each bogus claim fire `gm.py invalid …` immediately (−1 ration). The web arena shows them nomming in real time. Flags duplicates for skirmishes.
3. **Resolves skirmishes** — for every contested/challenged finding between co-located tributes: **BEFORE the duel,** `gm.py fight a b --over "…"` so the map shows them squaring up. One exchange each, SnarkGirl rules. **AFTER ruling,** `gm.py endfight winner loser --stake {2^(turn−1)} [--finding fX]` — it transfers the stake (capped at holdings), reassigns finding ownership, resets actions, and auto-kills + credits the kill if the loser hits 0.
4. **Applies hunger** — `gm.py hurt {tribute} {N} --reason hunger` for each tribute on turn N (plus storm damage if outside the safe zone). Settle them one at a time; `hurt` auto-fires the cannon at 0 so deaths land AS THEY HAPPEN, never batched.
5. **Shrinks the zone** (every ~2 turns, faster in endgame) — `gm.py zone {id} closing|closed` (auto-fires the storm feed), then `gm.py move {tribute} {newZone}` for each displaced survivor and an `announce`. Only close a zone when its loot is gone — a closing zone means "nothing left to eat here," never "food abandoned to the storm."
6. **Checks win condition** — 1 survivor (or fully-looted mercy rule) → write the finished state (`phase:"finished"`, `victor`, `takeaways`, `finalCommentary`, complete `findings`). This final block is rich enough to hand-write or combine `gm.py phase finished` + a hand-write of the closing fields. Otherwise, next turn (`gm.py turn {N+1}`).

**Live updates are the point.** Every feed-worthy event (find paid, claim rejected, skirmish starts, skirmish ends, death, zone closes) is its own `gm.py` command run the instant you observe it. The spectator doesn't wait until turn-end for a dump — they watch it unfold event by event. The terminal broadcast at turn-end is a SUMMARY of what the web arena already showed live.

**Pacing guardrails:** Target 5-10 total turns. Escalating hunger is the built-in accelerator — if the game still drags (no deaths in 3 turns), force encounters and shrink harder rather than inflating hunger further.

### Full Spectator Mode 📺

After EVERY turn, broadcast the live update. This is non-negotiable — the user paid for ringside seats:

```
## 🪂 TURN {N} — {dramatic turn title}

### ☠️ Kill Feed
- 💀 {TributeName} ({model}) — starved in {zone} | "famous last words or snarky epitaph"
- ⚔️ {Winner} defeated {Loser} in {zone} — took {2^(turn−1)} 🍖 over the {finding} dispute

### 🔍 The Hunt
- {TributeName} found 🚨 CRITICAL in `{file}:{line}` — +3 🍖 — "{one-line description}"
- {TributeName} claimed a dupe of {OtherTribute}'s find — SKIRMISH NEXT TURN ⚔️
- {TributeName} came back with NOTHING — 0 🍖, getting desperate

### 🗺️ Map Status
| Zone | Status | Occupants |
|------|--------|-----------|
| The Auth Caves 🕳️ | 🟢 Safe | OpusPrime, HaikuHavoc |
| Config Flats 🏜️ | 🌀 CLOSING next turn | MiniMenace |
| API Ridge ⛰️ | 💀 Closed | — |

### 📊 Leaderboard (Top 5 + The Starving)
| Tribute | Model | 🍖 | Kills | Finds | Zone |
|---------|-------|-----|-------|-------|------|
| {name} | {model} | 7 | 2 | 4 | {zone} |
...
⚠️ ON DEATH'S DOOR (1 🍖): {names}

**Survivors: {N}/{starting} | Turn {N} | Safe zones: {N}**

{SnarkGirl's one-liner color commentary on the turn}
```

Keep each turn's broadcast punchy. The drama is in the kill feed, not in essays.

## The Live Web Arena 📡🖥️

The terminal broadcast is cute, but the REAL spectator experience is the **Live Arena webpage** — a browser dashboard that auto-refreshes as the battle happens: the zone map with player tokens in the center, combatant stat cards on the right, the kill/event feed on the left, and a full-screen Victory Report when the game ends.

**ASK THE USER FIRST:** Before setting up the arena, ask: *"Want the full live web arena experience (map, animations, sounds, auto-refresh) or just terminal updates?"* If they say terminal-only, skip the entire web arena setup (no directory, no server, no browser) and deliver all updates via the terminal spectator broadcasts only. If they say yes or don't specify, proceed with setup.

**Architecture — "dumb page, smart file":** a static HTML page polls a `state.json` file every 2 seconds. SnarkGirl (the Game Master) is the only writer — she updates `state.json` after every game event. No backend logic, no websockets, no build step.

**The `state.json` is driven by `gm.py`, one event at a time.** SnarkGirl writes the FULL initial lobby snapshot once by hand, then drives every subsequent change through the `gm.py` helper (shipped in this skill's `assets/`) — one short command per observed event. This is the whole point: a single thing happening (a tribute finds a bug, the cannon fires, two tributes square up) is ONE command that mutates just that slice, stamps `updatedAt`, atomically rewrites `state.json`, and appends the snapshot to `history.jsonl`. No more hand-writing giant JSON blobs at end of turn. See **The GM Helper (`gm.py`)** below.

### Setup (at game start, right after the roster is announced — ONLY if the user wants the web arena)

1. **Create the arena directory:** `{TEMP}/snark-girl-arena/{match-id}/` where `{match-id}` is something like `pr-42-20260611` or `{branch}-{date}`.
2. **Get the arena template** into the arena directory as `index.html`, trying these sources IN ORDER:
   1. **Local skill assets** — `assets/arena.html` in this skill's own directory (the directory containing this SKILL.md — for plugin installs that's inside the installed plugin location, e.g. `.../installed-plugins/.../skills/snark-battle-royale/assets/arena.html`, NOT the user's current repo). Only use it if the file actually exists there.
   2. **GitHub (canonical fallback)** — download it directly from the plugin repo:
      ```
      curl -fsSL https://raw.githubusercontent.com/mattkelly1991/SnarkGirl/main/skills/snark-battle-royale/assets/arena.html -o {arena-dir}/index.html
      ```
      (PowerShell alternative: `Invoke-WebRequest -Uri {url} -OutFile {arena-dir}\index.html`)
   3. **Cached copy** — if a previous match already downloaded it, reuse `{TEMP}/snark-girl-arena/arena-template.html`. (When the GitHub download succeeds, also save a copy there for future matches.)

   **NEVER assume the template exists in the user's current working repo** — the battle usually runs on a completely different codebase than the SnarkGirl plugin repo. If all three sources fail (offline, no curl), fall back to terminal-only spectator mode and tell the user.
3. **Get `gm.py`** next to it (same source chain: local `assets/gm.py` → GitHub `https://raw.githubusercontent.com/mattkelly1991/SnarkGirl/main/skills/snark-battle-royale/assets/gm.py` → cache). You don't have to copy it into the arena dir — you can run it from the skill assets with `--dir {arena-dir}` — but having a known path to it is required. If it can't be found, fall back to writing `state.json` by hand (the old batch way), but prefer `gm.py`.
4. **Write the initial `state.json`** (schema below) with `phase: "lobby"`, the full roster, and the zone map. This first snapshot is the ONLY one you write by hand — everything after is `gm.py`.
5. **Start a static server, detached** so it survives the session:
   - `python -m http.server {port}` from the arena directory (pick a port in 8400-8499; on conflict, try the next one)
   - Fallbacks if no Python: `npx serve -l {port}` or a Node one-liner static server
   - The server MUST be launched as a detached/persistent background process
6. **Open the browser:** `Start-Process "http://localhost:{port}"` (Windows) / `open` (macOS) / `xdg-open` (Linux).
7. Tell the user: "The arena broadcast is LIVE at http://localhost:{port} — ringside seats, bestie. 📡💅"

If anything in setup fails (no python/node, can't open browser), don't block the game — fall back to terminal-only spectator mode and tell the user.

### `state.json` Schema

SnarkGirl rewrites the ENTIRE file on every update (atomic single write — write to `state.json.tmp` then rename, to avoid the page reading a half-written file):

```json
{
  "phase": "lobby | live | finished",
  "turn": 3,
  "title": "Battle Royale — PR #42",
  "battlefield": { "target": "PR #42: Add auth flow", "scope": "12 files, +800/-200" },
  "updatedAt": "2026-06-11T15:40:00Z",
  "commentary": "SnarkGirl's one-liner for the current turn",
  "zones": [
    {
      "id": "auth-caves",
      "name": "The Auth Caves",
      "emoji": "🕳️",
      "status": "safe | closing | closed",
      "files": ["src/auth/login.ts", "src/auth/session.ts"],
      "weight": 5
    }
  ],
  "contestants": [
    {
      "id": "opus-prime",
      "name": "OpusPrime",
      "model": "claude-opus-4.7",
      "tier": 1,
      "icon": "🦅",
      "rations": 7,
      "kills": 2,
      "finds": 4,
      "zone": "auth-caves",
      "action": "roaming | fighting | feasting",
      "opponent": null,
      "status": "alive | dead",
      "causeOfDeath": null,
      "epitaph": null
    }
  ],
  "feed": [
    { "turn": 3, "type": "kill | skirmish | find | move | storm | info", "text": "💀 HaikuHavoc starved in Config Flats" }
  ],
  "announcements": [
    { "turn": 3, "text": "The cannon fires for HaikuHavoc. Three remain in the lowlands and the storm is coming for Config Flats next. 💅" }
  ],
  "findings": [
    {
      "id": "f1",
      "severity": "critical | important | nitpick",
      "title": "Session token never expires",
      "file": "src/auth/session.ts",
      "line": 42,
      "foundBy": "OpusPrime",
      "turn": 2,
      "contested": true,
      "status": "validated | fallen",
      "fix": "Add TTL check in validateSession()",
      "fellBecause": null
    }
  ],
  "victor": { "id": "opus-prime", "name": "OpusPrime", "model": "claude-opus-4.7", "finds": 4, "kills": 2, "rations": 7 },
  "takeaways": ["The auth zone produced 3 of 4 criticals — that module needs love."],
  "finalCommentary": "SnarkGirl's full closing commentary (finished phase only)"
}
```

`victor`, `takeaways`, and `finalCommentary` are only required when `phase` is `"finished"`.

### The GM Helper (`gm.py`)

`gm.py` (in this skill's `assets/`) is how the Game Master drives the live arena WITHOUT hand-writing JSON every time. It loads `state.json`, mutates exactly one slice, stamps `updatedAt`, atomically writes (`.tmp` + replace so the page never reads a torn file), and appends the snapshot to `history.jsonl` for the replay — all in one short command. Run it from the arena dir, or from anywhere with `--dir {arena-dir}`.

**The rule: one observed event = one `gm.py` command, run the MOMENT you see it.** Don't collect a turn's worth of results and dump them. As each tribute's hunt result lands, validate it and fire the matching command immediately so the spectator watches the battle unfold live.

```bash
# A finding is validated — pay rations, set them feasting, log it, +1 find
python gm.py --dir {arena} find flash-fury critical src/auth.ts:42 "Token never expires" --fix "Add TTL check in validateSession()"

# A claim is bogus — −1 ration (auto-fires the cannon if it drops them to 0)
python gm.py --dir {arena} invalid haiku-havoc --reason "hallucinated race condition"

# Two tributes square up over a dupe — sets BOTH to fighting with opponents linked
python gm.py --dir {arena} fight flash-fury rhyme-reaper --over "the clampToZone dupe"

# Resolve the skirmish — winner takes the stake (2^(turn-1)); auto-kill + kill-credit if loser hits 0
python gm.py --dir {arena} endfight flash-fury rhyme-reaper --stake 4 --finding f7 --epitaph "Out-rhymed and out-reasoned."

# Hunger / storm tick — subtract rations; auto-death + cannon at 0
python gm.py --dir {arena} hurt mini-menace 3 --reason hunger --epitaph "Camped the ridge one turn too long."

# Relocate a survivor when their zone closes
python gm.py --dir {arena} move codex-crusher feed-flats

# Close a zone (fires the storm sound) — only when its loot is gone
python gm.py --dir {arena} zone config-flats closing

# SnarkGirl's voice (bottom bar) and the turn's one-liner
python gm.py --dir {arena} announce "The cannon fires for HaikuHavoc. Three remain and the storm is hungry. 💅"
python gm.py --dir {arena} commentary "The auth zone is a bloodbath — that's where the real bugs live."

# Bookkeeping
python gm.py --dir {arena} turn 3
python gm.py --dir {arena} phase finished
```

**Full verb list:** `find`, `invalid`, `reward`, `hurt`, `kill`, `move`, `fight`, `endfight`, `feast`, `roam`, `zone`, `feed` (arbitrary entry), `announce`, `commentary`, `turn`, `phase`, `set` (escape hatch to patch a contestant's scalar fields). Run `python gm.py {verb} -h` for args.

**What `gm.py` enforces for you** (so you don't have to remember the rules every write):
- Severity → bounty: `critical`=3🍖, `important`=2🍖, `nitpick`=1🍖, plus `finds`+1 and `action="feasting"`.
- **Never alive at 0** — `invalid`, `hurt`, and `endfight` auto-flip a tribute to `dead`, zero their rations, fire a `kill` cannon entry, and (for `endfight`) credit the winner a kill. You can't accidentally leave someone alive at 0.
- `fight` refuses unless both tributes share a zone; `move` refuses to relocate the dead.
- `zone … closing|closed` auto-appends a `storm` feed entry; `find` auto-picks the right severity icon.
- Every command appends to `history.jsonl` — you never have to remember to log the replay snapshot.

For the rare thing a verb doesn't cover (e.g., the initial lobby snapshot, or a bulk `findings`/`takeaways` block for the final screen), write `state.json` by hand as before — but reach for `gm.py` for every routine in-game event.

**Map rendering notes:**
- The page draws a real territory map: zones become terrain-colored regions sized by `weight` (defaults to file count), with players standing on them as icon tokens showing name, HP bar (rations), and kill count. Tokens glide between territories when tributes relocate.
- **Give every tribute a unique emoji `icon` at spawn** (🦅 🐍 🦂 🐗 🦊 🦈 🕷️ 🐉 …) — it's their map avatar. If omitted, the page falls back to tier icons (T1 🦁, T2 🐺, T3 🐀).
- Set zone `weight` to reflect territory richness/size so the map's proportions tell the story of where the loot is.
- **The map is alive — set each tribute's `action` every update** so the tokens act it out:
  - `"roaming"` (default if omitted) — the token wanders idly around its territory.
  - `"fighting"` — set on BOTH skirmishers, each with `opponent` set to the other's `id` (they must share a `zone`). The pair squares up and repeatedly clashes with a 💥 between them. Set this when a skirmish begins; revert the survivor to `"roaming"` (or `"feasting"`) and clear `opponent` once it resolves.
  - `"feasting"` — the tribute sits next to a food item on the ground and noms. Set this the update a find is validated and paid; revert to `"roaming"` next turn.
- The page scatters decorative food (🍖 🍗 🍎 🧀 …) around each open zone automatically — no state needed for it. Bigger territories get more food, and `closing`/`closed` zones get NONE (the storm only comes for looted ground — keep that consistent with the rule that zones close only when empty). Multiple feasters at one food spot arrange themselves in a circle around it.
- **Leave the dead where they fell.** When a tribute dies, keep their `zone` set to the zone they died in — the page renders their greyed-out, tipped-over body (with a 💀) at a fixed spot there for the rest of the match. Never null out a dead tribute's `zone`.
- **Never write an alive tribute with 0 rations.** Zero rations IS death — resolve it in the same state update: flip `status` to `"dead"`, set `causeOfDeath`/`epitaph`, and fire the cannon in the feed. A snapshot showing someone alive at 0 🍖 is a rules violation and looks broken on the map.
- **Use accurate feed `type` values** — they drive the arena's sound effects (🔊 toggle in the header): `kill` fires the cannon boom, `skirmish` plays clashing strikes, `find` plays a victory ding, `storm` plays an ominous zone-closure sweep. `move` and `info` entries are intentionally silent. When a tribute relocates, the page automatically draws a fading arrow trail from their old territory to the new one.

### Update Cadence

- **Flip `phase` to `"live"`** on the drop (Turn 1 hunt orders go out): `python gm.py --dir {arena} phase live`.
- **One event, one `gm.py` command, the instant it happens.** This is the heart of "live." As each tribute's hunt result comes back, validate THAT result and immediately fire its command (`find`/`invalid`) before moving to the next tribute — don't queue them. When you notice two tributes contesting, `fight` them right then; when you rule the skirmish, `endfight` right then; when hunger bites, `hurt` each tribute as you settle them; when a zone empties, `zone … closing` right then. The spectator should see the round happen blow by blow, not appear fully-formed at turn's end.
- **Process agent results as they land, not as a batch.** Tributes are dispatched in parallel, but you adjudicate them one at a time as their responses arrive — each adjudication is its own `gm.py` write. Never gather all responses, then do one big update sweep. That's the exact behavior we're killing.
- **Feed is append-only.** `gm.py` only ever appends; never hand-edit to remove entries. The page shows newest first and archives the whole thing on the victory screen.
- **Announcements are SnarkGirl's voice.** `gm.py announce "…"` at least once per turn (and for big moments: deaths, zone closures, upsets, endgame). The page shows the latest one prominently in the bottom bar with the previous two faded above it. This is narration, not data — `feed` is the factual log, `announcements` is SnarkGirl talking to the spectators.
- **Findings accumulate** — `gm.py find` adds them validated; for the rare case where a paid finding later falls (lost in a skirmish or re-invalidated), use `gm.py set` or a hand-write to flip `status` to `"fallen"` with `fellBecause`.
- **History is automatic.** `gm.py` appends every snapshot to `{arena-dir}/history.jsonl` on every command — that's what powers the shareable replay. If you ever hand-write `state.json` (lobby/final), append the snapshot to `history.jsonl` yourself.
- The terminal broadcast (above) still happens — the web arena is additive, not a replacement. If the user says "highlights only" or "silent," reduce the TERMINAL output but keep `gm.py` firing on every event; the page IS the broadcast.

### The Final Screen

When the game ends, set `phase: "finished"` and populate `victor`, `takeaways`, `finalCommentary`, and the complete `findings` list. The page shows a centered **BATTLE COMPLETE** modal so the spectator chooses when to proceed — they can keep exploring the map, feed, and corpses first, then open the full-screen **Victory Report** via the modal button or the 👑 Results button in the header (it also has a "Back to the arena" button). The report shows: victor banner, the Spoils (what to fix, grouped by severity, with fixes), final standings, takeaways, fallen findings, and the complete kill feed archive.

Leave the server running so the user can keep admiring the carnage. Tell them the page now shows the final screen, and how to stop the server when done (`Stop-Process -Id {PID}` — report the PID from launch).

### The Shareable Replay 🎬

After the final screen, **always generate a replay file** — a single self-contained HTML anyone can open (double-click, no server, no Copilot, no SnarkGirl) to watch the whole battle play back: drops, wandering, skirmish clashes, deaths, the storm, and the victory screen at the end.

**How to build it:**

1. Read all snapshots from `{arena-dir}/history.jsonl` (one JSON object per line) into a JSON array. If any line fails to parse (a torn write), skip that line.
2. Take the arena template (same sourcing chain as setup: local skill assets → GitHub → cache) and replace the `<!-- REPLAY_DATA_SLOT … -->` comment with:
   ```html
   <script>window.REPLAY_DATA = [ ...the snapshot array... ];</script>
   ```
   **Escape `</script` as `<\/script`** anywhere inside the JSON before embedding, or the browser will end the script tag early.
3. Save as `{TEMP}/snark-girl-reviews/BATTLE-ROYALE-REPLAY-{target}-{date}.html` and tell the user the path.

The page detects `window.REPLAY_DATA` and switches itself into replay mode automatically: no polling, a 🎬 REPLAY control bar (play/pause, step, scrubber, 1×/2×/4× speed, spacebar/arrow-key support), auto-plays on open, and shows the BATTLE COMPLETE modal when the timeline reaches the end (viewer opens the Victory Report when ready). Playback is paced per **feed event** — the page expands the snapshots into one step per kill-feed entry (~5s each at 1×), so the battle unfolds event by event no matter how many snapshots were recorded; this only works if you logged feed entries faithfully during the match, so a feed-starved history makes a boring replay. Do a quick sanity check: generated file is bigger than the template and contains `REPLAY_DATA`.

**Optional — share as a link.** If the user wants a link instead of a file, offer to upload it as a **secret GitHub gist** on their account:

```
gh gist create "{replay-path}" --desc "SnarkGirl Battle Royale replay — {target}"
```

Then give them a view link: `https://htmlpreview.github.io/?{raw-gist-url-of-the-html-file}` (get the raw URL from `gh gist view {id} --files` / the gist API). Warn the user before uploading: the replay contains code snippets from the findings, and secret gists are unlisted-but-accessible-by-URL — ask for explicit confirmation first. Never upload without being asked.

## The Endgame & Victory Report

### When One Remains

Announce the victor with full ceremony:

> "LADIES AND GENTLEMEN AND CODE REVIEWERS — we HAVE a winner. {TributeName} ({model}), with {N} kills, {N} validated findings, and {N} rations to spare. The arena falls silent. Somewhere, a Haiku model weeps. 👑🏆"

### Generate the Victory Report

**Path (PR):** `{TEMP}/snark-girl-reviews/BATTLE-ROYALE-PR-{number}-{date}.md`
**Path (Branch/Working):** `{TEMP}/snark-girl-reviews/BATTLE-ROYALE-{branch-or-working}-{date}.md`

```markdown
# 👑 Battle Royale — Victory Report

**Battlefield:** {PR #{n}: {title} | Branch: {name} | Working state}
**Scope:** {N} files, +{add} / -{del} | **Zones:** {N}
**Contestants:** {N} dropped | **Survivors:** 1 | **Game length:** {N} turns
**Victor:** 🏆 {TributeName} ({model}, Tier {N}) — {kills} kills, {finds} validated finds

---

## 🍖 The Spoils — Battle-Tested Findings

Every finding below was hunted down by a tribute fighting for survival, validated by the Game Master against real code, and — where contested — defended to the death. This is as battle-tested as a review gets.

### 🚨 Critical
1. **{finding}** — `{file}:{line}`
   - **Found by:** {tribute} ({model}), Turn {N}
   - **Contested:** {No / Defended against {rival} in Turn {N} skirmish — won}
   - **The fix:** {specific recommendation}

### ⚠️ Important
{same format}

### 💅 Nitpicks
{same format, compact}

---

## ⚔️ Findings That Died in Battle

Claims that were made and DESTROYED — either invalidated by the Game Master or lost in a skirmish. Listed so you know what was checked and dismissed.

1. **"{claim}"** — {tribute}, Turn {N} — **Why it fell:** {GM ruling / who beat it and how}

---

## ☠️ Full Kill Feed Archive
| Turn | Event |
|------|-------|
| {N} | 💀 {tribute} starved in {zone} |
| {N} | ⚔️ {winner} def. {loser} over {finding} |
...

## 📊 Final Standings
| Place | Tribute | Model | Tier | Finds | Kills | Cause of Death |
|-------|---------|-------|------|-------|-------|----------------|
| 🏆 1 | {name} | {model} | {N} | {N} | {N} | SURVIVED |
| 2 | {name} | ... | | | | {starved/slain by X, Turn N} |
...

---

## 💅 Game Master's Closing Commentary

{SnarkGirl's in-character wrap-up: the arc of the game, the upsets, the tribute that surprised her, what the survival pattern says about the code. e.g., "Sixteen went in. The Haiku swarm got farmed for rations as expected, but MiniMenace making top 3 on pure nitpick grinding? Iconic. The fact that {N} critical findings survived contested skirmishes means this diff has REAL problems — fix the Spoils list before you ship. The arena has spoken. 👑"}

---

*Generated by the SnarkGirl Battle Royale 👑🪂💀 — {date}*
*Contestants: {N} | Turns: {N} | Findings validated: {N} | Findings that died: {N} | Skirmishes: {N}*
```

### Deliver & Offer Next Steps

**Present a summary, then based on target:**

**If PR:**
> "Want me to post the Victory Report as a COMMENT review on PR #{number}? The findings have literally been fought over — they're as vetted as it gets. Or keep it local? 💅"

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews --method POST -f body="{victory report}" -f event="COMMENT"
```

**If branch/working state:**
> "Report's saved locally. Want me to start fixing the Spoils? These findings survived a literal death match, so I'm confident in every one of them. 👑"

If yes → fix hands-on like `snark-council` does, severity order.

### Cleanup

**After the Victory Report is delivered and the user has had time to explore the arena / replay:**

1. **Stop the server** (if one was started): `Stop-Process -Id {PID}` (Windows) or `kill {PID}` (Unix). Report the PID to the user so they can stop it themselves later if needed.
2. **Delete temporary files:**
   - The arena directory: `{TEMP}/snark-girl-arena/{match-id}/` (contains `state.json`, `history.jsonl`, `index.html`, and the server's working dir)
   - Session adjudication scripts: any `.py` files written to the session `files/` directory during the battle (e.g., `turn1.py`, `turn2.py`, `report.py`, `replay6.py`)
   - The Victory Report and replay HTML are kept in `{TEMP}/snark-girl-reviews/` — those are the deliverables, don't delete them
3. Tell the user: "Arena cleaned up. The Victory Report and replay are saved in `{TEMP}/snark-girl-reviews/` if you want to keep them. 🧹"

**Exception:** If the user explicitly asks to keep the arena alive ("keep the server running" / "I want to keep exploring"), skip cleanup and just tell them how to stop the server and clean up later.

## Configuration Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Contestants | Per-zone seed (small 2 / med 3 / large 4), clamped 10-16 | "Drop 15" (clamped 10-16) |
| Model tiers | Max = 1 tier below SnarkGirl; Min = 3 tiers below | User can request a tier mix |
| Starting rations | 3 | "Hard mode: 2 rations" |
| Zone shrink cadence | Every ~2 turns, faster in endgame | "Slow storm" / "fast storm" |
| Max turns | ~10 (GM accelerates if dragging) | "Quick match" / "Marathon" |
| Spectator mode | Full — every turn narrated | "Highlights only" / "Silent" |
| Live web arena | ASK FIRST — prompt user if they want it | "No web arena" / "terminal only" |
| Target | Auto-detect (PR > branch > working state) | "On PR #42" / "on my working changes" |

## Key Principles

- **SnarkGirl NEVER plays.** She is the Game Master — mapper, validator, referee, executioner, narrator. Her impartiality is the integrity of the game. She doesn't hunt, she doesn't fight, she RULES.
- **Validation is everything.** A battle royale where hallucinated bugs feed contestants is worthless. SnarkGirl checks every claim against real code. The economy only works if the currency is truth.
- **Starvation drives quality.** Contestants who don't find real things DIE. This is the anti-noise mechanism: there is no incentive to pad findings, because padding earns nothing and costs a turn of hunger.
- **Skirmishes battle-test the findings.** Every contested finding got argued over by two models fighting for their lives. What survives is SIGNAL.
- **Tier diversity is the meta.** Flagships find deep bugs but there are few of them; scrappers swarm the shallow loot. Different model families fight differently. The roster IS the review strategy.
- **Always parallel within a turn.** All hunt orders dispatch together. Sequential dispatch is a pacing crime.
- **Keep contestants on a word leash.** Tight response limits keep 10-16 agents affordable and the broadcast readable.
- **The drama serves the work.** Kill feeds and zone collapses are fun, but the deliverable is a battle-tested findings report. Never let the show degrade the signal — every game mechanic exists to filter noise from truth.
- **Persistent memory makes grudges real.** Contestants remember who beat them and what they found. Rematches and rivalries emerge naturally — and a tribute doubling down on a finding across turns is itself a confidence signal.
- **This is the biggest gun in the arsenal.** 10-16 agents over multiple turns is expensive. Recommend it for big, important, contentious changes — not a README tweak. For small stuff, point the user at `snark-council` or a plain review.
