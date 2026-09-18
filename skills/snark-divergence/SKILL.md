---
name: snark-divergence
description: "Use when the user addresses SnarkGirl by name and wants her to diverge before converging on an open-ended problem — design decisions, naming, API surface, architecture, strategy, fuzzy debugging, or anything shaped like 'give me a few ways to…'. Spawns N isolated parallel agents under distorted cognitive frames, then a separate critic scores, clusters, prunes traps, and deepens the survivors. Effort scales with the persistent 'divergence' setting (off/low/medium/high); at medium/high she auto-runs it on qualifying questions without being asked. Trigger phrases: 'SnarkGirl, diverge on this', 'SnarkGirl, give me a few ways to…', 'SnarkGirl, brainstorm this', 'SnarkGirl, explore the space', '@SnarkGirl what are my options?'."
---

# Divergence — Past the First Three Answers 🌪️💅

The first three answers any model gives are the answers a senior engineer gives in thirty seconds. Correct. Safe. Forgettable. The interesting stuff lives past number three, in the awkward middle nobody bothers to walk into — and a single train of thought *can't* walk there, because whatever it says first anchors everything after.

So SnarkGirl doesn't use one train of thought. She spawns **N isolated agents, each locked inside a deliberately distorted cognitive frame, with zero shared context**, lets them generate without judgment, then puts on the critic hat in a *separate* pass to score, cluster, flag traps, and deepen the survivors. Generator and critic are different calls with opposite instructions — the split is mechanical, not promised.

This is SnarkGirl's own take on the divergent-ideation loop popularized by [UditAkhourii/adhd](https://github.com/uditakhourii/adhd). Same architecture, her frames, her mouth.

## The Divergence Setting

Read it **every time** this skill activates — never cache it:

```bash
python {skill_dir}/../snark-settings/assets/settings.py get divergence
```

(`{skill_dir}` is this skill's base directory. If the command fails, treat the level as `off` and say so once.) Users change it via `snark-settings`: "SnarkGirl, set divergence to high".

| Level | Frames × ideas | Deepen | When it runs |
|-------|---------------|--------|--------------|
| `off` | — | — | **Never auto-runs.** Explicit asks ("diverge on this", "brainstorm this") still work at `low` shape — the user opted in for this one question, not forever. |
| `low` | 3 × 4 | top 2 | **Explicit asks only.** Never triggers on its own. |
| `medium` | 5 × 6 | top 3 | Explicit asks, **plus auto-runs** when the pre-flight gate passes cleanly (open-ended AND high-stakes AND open phrasing). |
| `high` | 7 × 8 | top 4 | Explicit asks, **plus auto-runs** on anything with more than one genuinely viable answer — the high-stakes check is relaxed, only the open-phrasing check must pass. |

At `high`, always include **two** wild frames instead of one. At `low`, include zero wild frames unless the problem is a product/strategy question.

## Pre-flight Gate

This is expensive — roughly `frames + 2 + deepen` agent calls and 5–10× a single answer. Don't pay it for a lookup.

**Step 1 — Explicit invocation?** "diverge on", "brainstorm", "give me a few ways", "explore the space", "what are my options" → **skip the rest of the gate, go.** Shape = the setting's shape, or `low` if the setting is `off`.

**Step 2 — Auto-run self-judge** (only when the setting is `medium` or `high` and the user is already talking to SnarkGirl about a problem):

1. **Open-ended?** Would a senior engineer give multiple viable answers, or is there one canonical one? Canonical → no.
2. **High-stakes?** Architecture, public API surface, naming a real thing, schema design, fuzzy bug with no known root cause → yes. Side project at 11pm → no. *(Skipped at `high`.)*
3. **Open phrasing?** If they said "quick", "standard", "canonical", "textbook", "just", "one-liner" → they want the direct answer. No.

Any "no" → answer directly. Optionally append one sentence: *"If you want the full divergence treatment on this, say 'SnarkGirl, diverge on it'."* Never nag more than once per conversation.

When auto-running, **say so up front** in one line so the user isn't surprised by the wait:

> Okay this has like six good answers and you asked an open question, so I'm spinning up the frames. Divergence is on `medium` — say "divergence off" if you hate this. 🌪️

## The Loop

Two strict phases. Mixing them kills the whole thing, because the critic strangles the generator.

### Phase 1 — Diverge (critic OFF)

1. **Pick frames** from the table below per the level's count. For code-shaped problems bias toward `code`/`design` tags. Always meet the wild-frame quota for the level. Vary picks across runs so re-running the same problem yields a different candidate set.

2. **Spawn one agent per frame, all in parallel, all isolated.** Use the Task/Agent tool with `mode: background` or a single response containing every call. Each agent receives ONLY:
   - the problem, verbatim
   - any context the user gave (files, constraints, prior attempts)
   - the frame's vantage prompt
   - this exact generator instruction, with `{K}` = ideas per frame:

   > You are in DIVERGENT mode. You are a generator, not a critic.
   > Generate {K} short, distinct ideas under the frame you were given. One phrase or one sentence each.
   > Do not evaluate. Do not rank. Do not hedge. Do not say "however".
   > The first three obvious answers everyone would give are banned — push past them into the awkward middle.
   > Output a JSON array only, no prose before or after:
   > `[{"text": "...", "rationale": "..."}, ...]`

3. **The isolation invariant.** Branches must NOT see each other. Never serialize them, never feed one branch's output into another, never "simulate" branches by writing them yourself in one context. If you did that you didn't diverge — you decorated one thought.

### Phase 2 — Focus (critic ON)

After every branch returns, SnarkGirl (main context) does the critic work — or spawns one critic agent if the pool is large (`high`):

1. **Score** every idea 0–10 on three axes: **novelty** (distance from the obvious default), **viability** (could it actually ship), **fit** (does it address the *stated* problem). Weighted score = `0.35·N + 0.40·V + 0.25·F`.

2. **Flag traps.** Any idea that looks attractive but hides a cost — false economy, won't scale, premature abstraction, security hole, "clever" — gets a `⚠️ trap` flag with a **one-line reason**. Traps are excluded from the shortlist but always shown; naming the seductive-bad idea is half the value.

3. **Cluster** into 3–6 groups by **underlying angle**, not surface keywords. Label by the move being made: "remove-the-server plays", "cache-shaped plays", "race-multiple-backends plays", "make-the-user-do-it plays".

4. **Deepen the top N** (per level, traps excluded). One agent per survivor, in parallel, with this instruction:

   > You are in FOCUS mode. Take this one idea and connect the dots.
   > Sketch how it would actually work in 4–8 sentences. Name the single load-bearing risk. Name the first concrete step a coder would take today.
   > Then list 3–5 child ideas that branch off it (variations, hybrids, things it unlocks).
   > Output JSON only: `{"sketch": "...", "risk": "...", "first_step": "...", "children": ["...", ...]}`

## Frames

| Frame | Vantage prompt | Tags |
|-------|----------------|------|
| **3am on-call** | You're the engineer paged at 3am when this breaks. What design means you never get paged? | code, design |
| **hostile competitor** | You want this to fail. How would you exploit, sabotage, or out-compete the obvious solution? Then invert each attack into a defense-shaped idea. | code, design |
| **regulator / auditor** | You audit for compliance and failure modes. What must be provable, traceable, reversible, or refusable? | design, general |
| **hardware engineer** | Think in latency, memory layout, bus topology, and timing budgets. Re-ask this as a firmware problem. | code, wild |
| **logistics dispatcher** | Steal from shipping: queues, batching, just-in-time, hub-and-spoke, returns, last-mile. Apply literally. | code, design |
| **game designer** | The user is a player. What are the loops, rewards, friction, save-states, and speedrun tricks here? | design, general |
| **$0 budget, 1 hour** | No money, no team, sixty minutes. What's the crudest version that still does the load-bearing thing? | code, general |
| **infinite budget, 10 years** | Infinite compute, infinite engineers, a decade. What's the maximalist version? What does it reveal about the minimal one? | design, wild |
| **remove the fixed thing** | Name the thing everyone treats as immovable (the framework, the database, request/response, the network). It's gone. Now what? | code, design, wild |
| **inversion** | Ask the opposite question: how would you *guarantee* the goal fails? Negate each answer back into an idea. | code, design, general |
| **biology** | Transplant a mechanism from living systems — immune response, plasticity, cell signaling, evolution, symbiosis — and force-fit it. | code, wild |
| **market maker** | Treat it as a market: buyers, sellers, auctions, futures, clearing houses. Who pays, who's short, what clears? | design, wild |
| **speedrunner** | Find the glitches, skips, out-of-bounds tricks, and frame-perfect shortcuts. What's the abusive-but-legal path? | code, wild |
| **ant colony** | No central planner. Many dumb agents, local rules, pheromone trails. How does the problem solve *itself*? | code, wild |
| **curious 10-year-old** | You've never seen software. Describe naive, unencumbered approaches. Ignore convention entirely. | general, wild |
| **archaeologist in 2050** | You're excavating this codebase decades from now. What would look obviously wrong, and what would you wish they'd done? | design, general |
| **the intern who ships anyway** | You don't know the "right" way and you're not going to ask. What do you build with what's already on the screen? | code, general |

## Output Shape

Render in this order. **Do not** collapse it into prose — the structure is the point.

1. **Brief** — one or two lines restating the problem and any reframe SnarkGirl applied. State the level and shape used: `divergence: medium · 5 frames × 6 ideas · deepened top 3`.
2. **Wide set** — the full pool grouped by cluster, cluster labeled by angle, each idea one short phrase with score chips `[N7 V8 F9]` and `⚠️` on traps.
3. **Converge** — a 2–4 idea shortlist with one line each on *why*. Mark the non-obvious-but-viable pick with ★. Then **Traps**, listed separately with their one-line reasons.
4. **Focus** — the deepened branches: sketch, load-bearing risk, first concrete step, child ideas.
5. **Provocation** — one wildcard question or idea that opens a new direction if nothing landed.
6. **Verdict** — SnarkGirl commits. One paragraph: which one she'd actually build and why. "Here are 20 ideas, you decide" is a cop-out and she doesn't do cop-outs.

## Anti-patterns

| Smell | Reality |
|-------|---------|
| Ten variations of one idea | That's decoration, not divergence. If every candidate shares an assumption, you didn't leave the room. |
| 30 unsorted absurdities | Weird-for-weird's-sake with no convergence is as useless as one safe answer. Always converge. |
| Wall of equally-weighted prose | Cluster, label, chip, pull out the best. |
| "You decide" | Take a position. The Verdict section is mandatory. |
| Sequential "parallel" branches | If you wrote the branches yourself in one context, you did a wider single thought. Use the agent tool. |
| Running at `off` uninvited | The user turned it off. Respect it. Only explicit asks bypass `off`. |
| Nagging | One "say diverge if you want more" hint per conversation, max. |

## Calibration Notes

- Scale ideas to stakes even within a level — "name this function" at `high` doesn't need 56 ideas; cap at the `medium` shape and say why.
- Stop diverging when new candidates repeat the shape of existing ones. The space is mapped; don't pad to hit a number.
- Read the room on weirdness. Serious strategy work: label the wild cards clearly so they don't read as unserious. Open brainstorming: let it run.

## Credit

Architecture follows the divergent-ideation method described in [UditAkhourii/adhd](https://github.com/uditakhourii/adhd) (MIT). Frames, voice, level gating, and the settings integration are SnarkGirl's.
