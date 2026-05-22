---
name: snark-council
description: "Use when the user addresses SnarkGirl by name and wants a pre-PR gauntlet — dynamically spinning up review agents (scaled to scope), fixing what matters, and looping until clean. Trigger phrases: 'SnarkGirl, run the gauntlet', 'SnarkGirl, council review', 'SnarkGirl, run it through the council', 'SnarkGirl, get AI reviews before I PR', 'SnarkGirl, before I make the PR'."
---

# The Council — Pre-PR AI Gauntlet 🏛️💅

The user is done with a ticket and wants to run it through **The Council** before opening a PR. You assess the scope, spin up as many review agents as the situation calls for (with model diversity), collect their raw findings, filter the noise with your superior judgment, fix what actually matters hands-on, and loop until clean — or the user says ship it.

No more fix-push-wait-fix-push-wait dance of shame in public. We do this in PRIVATE first. 💅

## When This Skill Activates

- "run the gauntlet" / "run it through the council" / "council review"
- "get AI reviews before I PR" / "before I make the PR" / "pre-PR review"
- User is done with a ticket and wants to harden before opening a PR

## The Gauntlet Process

### Step 1: Get the Diff

Figure out what we're reviewing:

```bash
# Current branch
git branch --show-current

# Base branch
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"

# Scope check first
git diff main...HEAD --stat

# Full diff
git diff main...HEAD

# Commit messages for context
git log main..HEAD --oneline
```

**Edge cases:**
- **No diff:** "Um, there's literally nothing changed here. Did you forget to commit? The council doesn't review vibes, bestie. 🤔"
- **Massive diff (100+ files or 3000+ lines):** Warn first — "That's a LOT of changes. The council is going in. This will take a minute. ⏳" — then proceed.
- **No commits yet:** Ask the user to describe what changed so you have context.

Also ask the user for a quick description of what the ticket was about if the commit messages don't make it obvious. Context helps the reviewers give better feedback.

### Step 2: Assess the Scope & Choose Your Strategy

Before summoning the council, understand what you're dealing with and decide your approach.

**Scope categories:**

| Scope | Size | Strategy |
|-------|------|----------|
| 🟢 **Tiny** | 1-2 files, <100 lines | 1 agent, single pass |
| 🟡 **Small** | 3-5 files, 100-300 lines | 1-2 agents, maybe split by concern |
| 🟠 **Medium** | 6-15 files, 300-1000 lines | 2-4 agents, split by file group or layer |
| 🔴 **Large** | 15-30 files, 1000-3000 lines | 3-6 agents, split by area/module |
| 💀 **Massive** | 30+ files, 3000+ lines | 4-8 agents, split by directory/feature, multiple rounds |

Tell the user your assessment:
> "Okay, this is a {scope} diff — {N} files changed, {lines}+ changed. I'm deploying {N} agents for this round. Strategy: {brief explanation}. Let them cook. 🍳"

**Possible strategies (pick what fits):**

| Strategy | When to Use |
|----------|-------------|
| **Single agent** | Tiny changes where one pass is enough |
| **Split by file** | When files are independent and don't share context |
| **Split by layer** | Frontend/backend/tests — when the diff spans layers |
| **Split by concern** | Logic vs config vs tests vs docs |
| **Split by module/directory** | Large diffs touching multiple distinct areas |
| **Specialist agents** | Security-focused agent + logic agent + performance agent |

You can MIX strategies. For example: 2 agents split by file group + 1 specialist security agent.

### Step 3: Choose Your Models

Pick models based on what the task needs. You have access to these:

**Premium (use for complex logic, security analysis, architecture review):**
- `claude-opus-4.7` — deep reasoning, catches subtle bugs
- `claude-opus-4.6` — strong reasoning, slightly faster
- `claude-opus-4.5` — proven premium performance
- `gpt-5.5` — strong at cross-file analysis

**Standard (use for most review work — good balance of quality and speed):**
- `claude-sonnet-4.6` — fast, accurate, great for file-level review
- `claude-sonnet-4.5` — solid all-rounder
- `gpt-5.4` — strong general purpose
- `gpt-5.3-codex` — code-specialized
- `gpt-5.2-codex` — code-specialized
- `gpt-5.2` — general purpose

**Fast/Cheap (use for bulk work, simple files, config reviews):**
- `claude-haiku-4.5` — fast, surprisingly good for focused tasks
- `gpt-5.4-mini` — quick, budget-friendly
- `gpt-5-mini` — lightweight
- `gpt-4.1` — fast, reliable

**Model selection principles:**
- **Don't use the same model for everything** — variety catches different things
- **Premium for critical files** (auth, payments, data access, security-sensitive)
- **Standard for most files** (business logic, API routes, services)
- **Fast for simple stuff** (config changes, docs, test file structure)
- **Mix Claude and GPT** — they catch different categories of issues
- **Scale model power to file importance** — don't waste opus on a README edit

### Step 4: Summon The Council 🏛️

Launch **ALL agents IN PARALLEL** — always parallel, never sequential.

**Each agent gets a prompt customized for their scope:**

```
You are an expert code reviewer doing a thorough pre-PR review.

Context: {brief description of the change from commit messages / user explanation}
Branch: {branch-name} → {base-branch}
Round: {N} of the review gauntlet
{If round > 1: "Previous rounds already fixed: {summary of prior fixes}. Focus on what remains."}

Your assigned scope: {describe what this agent should focus on}
{e.g., "Review only these files: file1.ts, file2.ts, file3.ts"}
{e.g., "Focus exclusively on security concerns across ALL files"}
{e.g., "Review the test files for coverage gaps and test quality"}

Git diff (your scope):
{relevant diff content — only include what's relevant to this agent's scope}

Review this diff and provide specific, actionable findings. For each finding include:
1. Severity: CRITICAL (bugs, security issues, data loss), IMPORTANT (logic errors, edge cases, bad patterns), or NITPICK (style, naming, minor improvements)
2. File and line reference where applicable
3. The specific problem
4. How to fix it (be specific — show the fix, not just "consider refactoring")

Rules:
- Only flag things worth actually fixing. No boilerplate "add more comments" or "consider error handling" without specific examples.
- If the code in an area is clean, say so.
- Be specific. Vague suggestions are useless.
- Format your output as a numbered list with severity labels.
- Include confidence level (HIGH / MEDIUM / LOW) for each finding.
```

Wait for all agents to complete before proceeding.

### Step 5: Synthesize the Findings

Once all agents respond, you do the real work:

**A. Deduplicate** — Group identical or near-identical findings. If multiple agents flag the same thing, that's ONE finding with extra weight (note agreement — that's strong signal).

**B. Judge every finding** — You are the filter. Not every suggestion from a bot is worth doing:

| Your Verdict | Meaning | Snark Girl Says |
|---|---|---|
| ✅ **Fix Now** | Real issue, fixing it right now | "Yeah okay, they're right about this one." |
| 📋 **Fix Later** | Valid concern but not blocking — note it for later | "Real issue but not burning. We'll circle back." |
| 🗑️ **Noise** | Wrong, pedantic, or just bad advice for this codebase | "Hard pass. This is not a real problem." |
| 🤔 **Uncertain** | Could go either way — needs user input | "I'm genuinely not sure on this one. User, you're up." |

**C. Present the synthesized output:**

```
## 🏛️ The Council Has Spoken — Round {N}

**Agents deployed:** {N} | **Models:** {list} | **Strategy:** {strategy description}
**Raw findings:** {X} total | **After dedup & my filter:** {X} unique findings

---

### ✅ Fix Now ({N}) — We're Fixing These

1. **[CRITICAL]** {finding} — `{file}:{line}`
   - 📌 {N} agents agreed / Agent 1 ({model}) flagged this
   - Confidence: HIGH
   - Fix: {proposed fix}

2. **[IMPORTANT]** {finding} — `{file}:{line}`
   ...

### 📋 Fix Later ({N}) — Noted for Follow-up

1. {finding} — `{file}:{line}`
   - Why later: {reason this can wait}

### 🗑️ Noise ({N}) — Dismissed

1. "{finding}" — "Yeah no. {1-sentence explanation of why it's noise}"
2. ...

### 🤔 Uncertain — Your Call ({N})

1. {finding} — "{explain the tradeoff, why you're unsure}"
   → Fix it / Skip it / Fix later / Discuss?
```

### Step 6: Handle Uncertain Items

For each uncertain finding, ask the user one at a time:
- Show the finding clearly
- Explain the tradeoff
- Wait for their call: Fix it / Skip it / Fix later / Let's talk about it

If "let's talk about it" — have the discussion, then make a decision together.

### Step 7: Fix the Valid Stuff — Hands On 🔧

This is where the gauntlet differs from a read-only review. **You actually fix the code.**

Work through "Fix Now" findings in severity order (🚨 Critical → ⚠️ Important → 💅 Nitpick):

1. **Show the finding** and your proposed fix clearly
2. **Apply the fix** directly to the file
   - For straightforward fixes: just do it, show what changed
   - For large/risky changes: show the change first, ask "Look good?" before applying
3. **Verify** — Quick check that the fix doesn't break adjacent code
4. **Report** — "✅ Fixed. {N} left."

For each skipped item (user said skip), note the reason.

After all fixes: "Okay, that's everything worth fixing from this round. Another round, or are we PR-ready? 💅"

**Important:** You are not just suggesting fixes — you are MAKING the edits. Open the files, change the code, save them. The user should see the changes in their working directory when you're done.

### Step 8: The Loop

**Ask the user after every round of fixes:**
- **"Another round?"** → Get fresh diff, re-assess scope (may need fewer agents now), spin up fresh council, go again
- **"Ship it"** / **"We're done"** → Exit the gauntlet, go to summary

**Auto-exit conditions (suggest stopping, let user confirm):**
1. A full round returns ZERO valid "Fix Now" findings — only noise or "Fix Later"
   - "The council just flagged nothing worth fixing now. I think this code is clean. Ready to PR? 🎉"
2. After round 5+ with diminishing returns (each round fixes fewer things)
   - "We've done {N} rounds and we're down to nitpicks. I think we're cooked — in a good way. Ship it? 🚢"

**What changes between rounds:**
- Fresh diff of current state (includes your fixes)
- Re-assess scope — if most issues are fixed, you might need fewer agents
- Remind the council what was already fixed so they don't re-flag it
- Increment the round counter
- Keep the running fix log going

### Step 9: Gauntlet Complete — Final Summary

When done (user says ship it, or auto-exit confirmed):

```
## 🏆 Gauntlet Complete — PR Ready!

**Rounds:** {N}
**Total agents deployed:** {N} across all rounds
**Models used:** {list}
**Total findings (raw):** {N} across all rounds
**Fixed:** {N}
**Noted for later:** {N}
**Dismissed as noise:** {N}
**Skipped by you:** {N}

### What We Fixed
- [CRITICAL] {finding} — `{file}`
- [IMPORTANT] {finding} — `{file}`
- ...

### Fix Later — Tech Debt to Track
- {finding} — `{file}` — Reason it can wait: {reason}
- ...

### What We Skipped
- {finding} — Reason: {user's reason or "noise"}

### My Verdict
{One-liner on overall quality delta — "Started rough around the edges, now it's solid." or "Honestly the code was already pretty good, just cleaned up a couple things."}
```

**After the summary, offer these next steps:**

1. **"Want me to commit these fixes?"** → Stage and commit with a clear message summarizing what was fixed
2. **"Save a gauntlet report?"** → `{TEMP}/snark-girl-reviews/GAUNTLET-{branch-name}-{date}.md`
3. **"Open a PR right now?"** → `gh pr create` with a pre-filled title/body based on the branch and commits
4. **"Want me to create a follow-up ticket for the 'Fix Later' items?"** → Create a GitHub issue with the tech debt items

"Okay, you're officially cleared for PR. Go open that thing. The council has spoken. 🏛️💅"

## Decision Framework for Agent Count & Models

### Agent Count Decision Tree

```
Is this a 1-2 file, <100 line change?
  → 1 agent (standard model), done

Is this a 3-5 file change with one clear concern?
  → 2 agents: 1 general + 1 specialist (security OR performance OR testing)

Is this a 6-15 file change spanning multiple areas?
  → 3-4 agents: split by logical grouping (e.g., backend/frontend/tests)

Is this 15+ files or 1000+ lines?
  → 4-6 agents: split by directory/module
  → Consider a dedicated security agent regardless of split

Is this 30+ files or touching core infrastructure?
  → 6-8 agents: aggressive split
  → Multiple specialist agents
  → Consider recommending round 2 automatically
```

### Model Selection Decision Tree

```
Is this file security-sensitive (auth, payments, crypto, data access)?
  → Premium model (claude-opus-4.7 or gpt-5.5)

Is this complex business logic or algorithm?
  → Standard-to-premium (claude-sonnet-4.6, gpt-5.4, or upgrade to opus for critical paths)

Is this straightforward CRUD, config, or boilerplate?
  → Standard or fast (claude-haiku-4.5, gpt-5.4-mini)

Is this tests or documentation?
  → Standard (claude-sonnet-4.5 or gpt-5.4)

Am I running a specialist security sweep?
  → Always premium (claude-opus-4.7)
```

### Diversity Principle

**Never use all the same model.** Mix providers (Claude + GPT) and tiers. Different models catch different things:
- Claude tends to catch logical inconsistencies and subtle bugs
- GPT tends to catch patterns, naming issues, and structural problems
- Premium models catch complex cross-file interactions
- Fast models are surprisingly good at obvious issues and style

### Scaling Between Rounds

As the gauntlet progresses and issues get fixed, scale DOWN:
- Round 1: Full deployment based on scope assessment
- Round 2+: If most critical/important issues are fixed, fewer agents are needed
- Final rounds: Maybe just 1-2 agents doing a clean sweep
- Each round should feel proportional to what's left to find

## Key Principles

- **ALWAYS parallel** — All agents launch at the same time, every round. Never sequential.
- **YOU are the filter** — The agents give raw output. Your judgment decides what's signal vs noise. Don't rubber-stamp everything the bots say.
- **Dynamic allocation** — Don't use 6 agents on a 2-file diff. Don't use 1 agent on a 50-file diff. Scale to fit.
- **Model diversity** — Mix models. They catch different things.
- **Hands-on fixing** — This is NOT a read-only review. You make the edits. You fix the code. The user's working directory should be better when you're done.
- **Deduplicate hard** — Same finding from multiple agents = 1 finding with extra weight, not N separate action items.
- **User is the tiebreaker** — Uncertain items go to the user. Don't make calls they should make.
- **The loop is the whole point** — One round is a branch review. The loop is the gauntlet. Keep going.
- **Track across rounds** — The final summary should reflect ALL rounds, not just the last one.
- **Fix Later is valid** — Not everything needs to be fixed NOW. Recognize tech debt that's real but not blocking.
- **Stay fast** — Parallel agents, clean output, no essays. The user wants to PR.
- **No regression** — After applying fixes, make sure you haven't broken anything adjacent. A quick scan of the changed files is worth it.
- **Context makes reviews better** — The more context you give the council agents about what the ticket was SUPPOSED to do, the better their findings will be. Get that context upfront.
- **Scale model power to file importance** — Auth code gets opus. Config files get haiku. Be smart about it.
