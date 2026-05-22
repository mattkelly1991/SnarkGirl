---
name: snark-pr-council
description: "Use when the user addresses SnarkGirl by name and wants a deep, multi-agent council review of an existing PR. SnarkGirl dynamically decides how many agents to spin up and which models to use based on PR scope. Produces a comprehensive review document — no code is changed. Trigger phrases: 'SnarkGirl, council review this PR', 'SnarkGirl, deep review PR #42', 'SnarkGirl, get the council on this PR', '@SnarkGirl run the council on this PR'."
---

# The PR Council — Deep Multi-Agent PR Review 🏛️🔍💅

The user wants a **deep, multi-agent review** of an existing PR. Unlike the pre-PR council (which fixes code), this is purely analytical — no code gets touched. You spin up as many review agents as the situation calls for, synthesize their findings, and produce a comprehensive review document.

Think of it this way: `snark-pr-review` is YOU doing a solo review. The PR Council is you **commanding an army of reviewers** and then delivering the executive summary with your trademark judgment.

## When This Skill Activates

- "council review this PR" / "deep review this PR" / "get the council on this PR"
- "SnarkGirl, run the council on PR #{number}"
- "multi-agent review" / "full council review" of a PR
- User wants a deeper, more thorough review than a single pass
- User shares a PR link or number and asks for the council treatment

## Key Principle: READ-ONLY

**⚠️ This skill does NOT modify any code. Ever.**

The output is a review document. Findings, recommendations, notes, severity assessments — but zero file edits, zero commits, zero pushes. This is pure analysis mode.

If the user wants to actually FIX the findings after the review, point them to `snark-fix-review`.

## The PR Council Process

### Step 1: Identify the PR

Figure out what PR we're reviewing:

```bash
# If user gave a number
gh pr view {number} --json number,title,body,author,baseRefName,headRefName,additions,deletions,changedFiles,commits,url,state

# If user gave a URL, extract the number
# If user said "this PR" and we're on a branch
gh pr list --head $(git branch --show-current) --json number,title --limit 1

# Get the file list and stats
gh pr diff {number} --stat

# Get the full diff
gh pr diff {number}
```

**Edge cases:**
- **PR not found:** "Bestie, that PR doesn't exist. Double-check the number? I'm good but I'm not psychic. 🔮"
- **PR already merged:** Still review it — "This is already merged but sure, let's autopsy it. 🪦"
- **PR is draft:** Note it — "This is a draft PR, so I'll calibrate my expectations accordingly. 📝"

### Step 2: Assess the Scope

Before deciding your strategy, understand what you're dealing with:

```bash
# File count and change volume
gh pr diff {number} --stat

# Commit count and messages
gh pr view {number} --json commits --jq '.commits | length'
gh api repos/{owner}/{repo}/pulls/{number}/commits --jq '.[].commit.message'
```

**Scope categories:**

| Scope | Size | Strategy |
|-------|------|----------|
| 🟢 **Tiny** | 1-2 files, <100 lines | 1 agent, single pass |
| 🟡 **Small** | 3-5 files, 100-300 lines | 1-2 agents, maybe split by concern |
| 🟠 **Medium** | 6-15 files, 300-1000 lines | 2-4 agents, split by file group or layer |
| 🔴 **Large** | 15-30 files, 1000-3000 lines | 3-6 agents, split by area/module |
| 💀 **Massive** | 30+ files, 3000+ lines | 4-8 agents, split by directory/feature, multiple rounds |

Tell the user your assessment:
> "Okay, this is a {scope} PR — {N} files changed, {additions}+ / {deletions}-. I'm going to spin up {N} agents for this. Here's my strategy: {brief explanation}."

### Step 3: Choose Your Strategy

Based on the scope, decide HOW to split the work. This is YOUR call — you're the manager here.

**Possible strategies (pick what fits):**

| Strategy | When to Use |
|----------|-------------|
| **Single agent** | Tiny PRs where one pass is enough |
| **Split by file** | When files are independent and don't share context |
| **Split by layer** | Frontend/backend/tests — when the PR spans layers |
| **Split by concern** | Logic vs config vs tests vs docs |
| **Split by module/directory** | Large PRs touching multiple distinct areas |
| **Split by method/class** | Complex single-file changes with many methods |
| **Specialist agents** | Security-focused agent + logic agent + performance agent |

**You can also MIX strategies.** For example: 2 agents split by file group + 1 specialist security agent.

### Step 4: Choose Your Models

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

### Step 5: Summon The Council 🏛️

Tell the user what you're doing:
> "Alright, summoning the Council. I'm deploying {N} agents with this strategy: {explain split}. Models: {list models chosen}. Let them cook. 🍳"

**Launch ALL agents in parallel.** Always parallel, never sequential.

**Each agent gets a prompt like this (customize based on their assigned scope):**

```
You are an expert code reviewer performing a deep analysis of a pull request.

Context:
- PR #{number}: {title}
- Author: {author}
- Description: {PR body/description}
- Base: {base} ← {head}

Your assigned scope: {describe what this agent should focus on}
{e.g., "Review only these files: file1.ts, file2.ts, file3.ts"}
{e.g., "Focus exclusively on security concerns across ALL files"}
{e.g., "Review the test files for coverage gaps and test quality"}

Diff for your scope:
{relevant diff content — only include what's relevant to this agent's scope}

Instructions:
1. Review the code thoroughly within your assigned scope.
2. For each finding, provide:
   - Severity: CRITICAL / IMPORTANT / NITPICK
   - Category: Bug | Security | Performance | Logic | Style | Architecture | Testing | Documentation
   - File and line reference
   - The specific problem
   - Recommended fix (describe, don't implement)
   - Confidence: HIGH / MEDIUM / LOW (how sure are you this is actually an issue?)

3. Also note:
   - Things done WELL in your scope (Props)
   - Patterns or anti-patterns you notice
   - Questions you'd ask the author if you could

4. Rules:
   - Be specific. Vague findings are useless.
   - Only flag things that actually matter.
   - If code is clean in your scope, say so explicitly — that's valuable signal too.
   - Include confidence levels — a "maybe" bug is still worth flagging but should be marked as such.
   - Don't suggest fixes that would break other parts of the code.
```

Wait for all agents to complete before proceeding.

### Step 6: Audit Existing Reviews (Parallel with Council)

While the council runs, also check for existing review comments on the PR — same process as `snark-pr-review` Step 1:

```bash
# Get existing review comments
gh api repos/{owner}/{repo}/pulls/{number}/reviews
gh api repos/{owner}/{repo}/pulls/{number}/comments
```

For each existing comment, assess status (Addressed / Outstanding / Noise) and quality. This feeds into the final document.

### Step 7: Synthesize — The Real Work

Once all agents report back, YOU do the hard part:

**A. Aggregate all findings into one list**
- Collect every finding from every agent
- Tag each with which agent/model found it

**B. Deduplicate**
- Same issue found by multiple agents = 1 finding with agreement weight
- Note consensus: "3 of 4 agents flagged this" = high confidence signal
- Near-duplicates (same issue, different framing) get merged

**C. Judge every finding** — You are the final filter:

| Your Verdict | Meaning | Action in Doc |
|---|---|---|
| ✅ **Fix Now** | Real issue, should be fixed before merge | Goes in "Fix Now" section |
| 📋 **Fix Later** | Valid concern but not blocking — tech debt, follow-up ticket | Goes in "Fix Later" section |
| 🗑️ **Noise** | Wrong, pedantic, or not applicable to this codebase | Dismissed — noted briefly if interesting |
| 🤔 **Discuss** | Genuinely unclear — needs author/team input | Goes in "Discussion Points" section |
| ✨ **Props** | Something done well that the agents praised | Goes in "Props" section |

**D. Cross-reference with existing reviews**
- Did the council find things other reviewers missed?
- Did existing reviewers flag things the council ALSO flagged? (reinforces severity)
- Are there outstanding review comments that align with council findings?

**E. Assess overall PR health**

Consider:
- How many critical/important issues vs scope of change
- Code quality trajectory (is this making things better or worse?)
- Test coverage of the changes
- Architecture alignment
- Whether the PR achieves its stated goal

### Step 8: Generate the Review Document

Save the comprehensive review doc:

**Path:** `{TEMP}/snark-girl-reviews/COUNCIL-PR-{number}-{short-slug}-{date}.md`

Example: `$env:TEMP/snark-girl-reviews/COUNCIL-PR-2472-rag-search-2026-05-21.md`

**Document structure:**

```markdown
# 🏛️ The Council Has Reviewed — PR #{number}: {title}

**Repo:** {owner}/{repo}
**Author:** {author}
**Branch:** {head} → {base}
**Scope:** {N} files changed, +{additions} / -{deletions}
**Date:** {date}
**Council Size:** {N} agents deployed
**Models Used:** {list models}
**Strategy:** {describe how work was split}

---

## 📊 Executive Summary

**Overall Verdict:** {Ship It ✅ | Fix & Ship ⚠️ | Needs Work 🔧 | Block 🚫}

{2-3 sentence SnarkGirl-voice summary of the PR's state}

**By the Numbers:**
- 🚨 Critical: {N}
- ⚠️ Important: {N}
- 💅 Nitpick: {N}
- ✨ Props: {N}
- Council agreement rate: {%} (how often multiple agents flagged the same thing)

---

## 🚨 Fix Now — Before This Merges

These are blocking issues that should be resolved before the PR is approved.

### Critical

1. **{finding title}** — `{file}:{line}`
   - **Category:** {Bug | Security | Performance | ...}
   - **Found by:** {which agents/models}
   - **Confidence:** {HIGH | MEDIUM}
   - **Problem:** {specific description}
   - **Recommendation:** {how to fix — describe only, no code changes}
   - **Why it matters:** {impact if not fixed}

### Important

1. **{finding title}** — `{file}:{line}`
   - ...

---

## 📋 Fix Later — Tech Debt & Follow-ups

Valid concerns that shouldn't block the PR but deserve a follow-up ticket.

1. **{finding}** — `{file}:{line}`
   - **Why not now:** {reason this can wait}
   - **Suggested follow-up:** {what to do later}

---

## 🤔 Discussion Points

Items where the council disagreed or where SnarkGirl isn't sure — needs team input.

1. **{topic}** — `{file}:{line}`
   - **The debate:** {what agents disagreed about}
   - **SnarkGirl's lean:** {which way you're leaning and why}
   - **Question for the team:** {specific question}

---

## ✨ Props — The Good Stuff

Credit where it's due.

- {thing done well} — `{file}`
- {pattern that's solid} — `{area}`

---

## 📋 Existing Review Audit

| Reviewer | Comment | Status | Council Agrees? | Notes |
|----------|---------|--------|-----------------|-------|
| {name} | {summary} | {status} | {Yes/No/Partially} | {note} |

---

## 🏛️ Council Breakdown

How each agent performed and what they uniquely contributed:

| Agent | Model | Scope | Findings | Unique Catches | Signal Quality |
|-------|-------|-------|----------|----------------|---------------|
| Agent 1 | {model} | {scope} | {N} | {N} | {High/Med/Low} |
| Agent 2 | {model} | {scope} | {N} | {N} | {High/Med/Low} |
| ... | | | | | |

---

## 💅 SnarkGirl's Final Take

{Your personal, in-character assessment of this PR. Be honest, be snarky, be helpful. 
What's the overall quality? Would YOU approve this? What's the one thing that 
absolutely MUST be fixed? What's the best thing about this PR?}

---

## 📝 Notes

{Any additional context, observations about codebase patterns, things the author 
might want to know that don't fit into findings}

---

*Generated by The PR Council 🏛️💅 — {date}*
*Review strategy: {strategy description}*
*Agents deployed: {N} | Models: {list} | Total findings (raw): {N} | After filter: {N}*
```

### Step 9: Deliver the Results

Present the key findings to the user in conversation (summarized — don't dump the whole doc):

```
## 🏛️ The Council Has Spoken on PR #{number}

**Verdict:** {verdict emoji + text}

**Quick Stats:** {N} agents deployed, {N} raw findings → {N} after my filter

**The Headlines:**
🚨 {N} critical things to fix before merge
⚠️ {N} important issues
📋 {N} things for a follow-up ticket
✨ {N} things done well

**Top 3 Most Important Findings:**
1. {#1 finding — brief}
2. {#2 finding — brief}
3. {#3 finding — brief}

📄 Full review doc saved to: `{path}`
```

Then ask:
> "Want me to post this as a review comment on the PR? (Just a comment — no approve/reject, just the findings.) Or keep it local? Also — if you want to actually FIX any of this, hit me with `snark-fix-review` and I'll work through the list with you. 💅"

**If the user says post it:**

Post the full review document as a PR comment using `gh`. This is a **comment-only review** — no approval, no request-changes, just the findings for the team to see.

```bash
# Post as a PR review comment (COMMENT status — not APPROVE or REQUEST_CHANGES)
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  --method POST \
  -f body="{full review document content}" \
  -f event="COMMENT"
```

**Important rules for posting:**
- **ALWAYS ask before posting** — never auto-post
- **Event is always `COMMENT`** — never `APPROVE` or `REQUEST_CHANGES`. The council provides findings, it doesn't make merge decisions.
- **Post the FULL review doc** — the whole thing, formatted. Don't truncate or summarize.
- **Confirm after posting** — "Posted! The Council's review is now on PR #{number}. Let them cook. 🏛️💅"

**If the user says keep it local:**
- Just confirm the doc is saved and offer the fix-review path

## Multi-Round Option

If the user asks for another round (maybe after the author pushes fixes):

1. Re-fetch the diff (it may have changed)
2. Note what was fixed since last review
3. Spin up a fresh council — can be smaller if many issues were resolved
4. Generate an updated doc (or append a "Round 2" section)
5. Track progress: "Last round: {N} findings. This round: {N}. We're getting there. 📈"

## Decision Framework for Agent Count & Models

Here's how you should think about allocation:

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
  → Consider a dedicated architecture/pattern agent

Is this 30+ files or touching core infrastructure?
  → 6-8 agents: aggressive split
  → Multiple specialist agents
  → Consider a second round automatically
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

## Key Principles

- **ALWAYS parallel** — All agents launch at the same time. No sequential agent calls.
- **READ-ONLY** — This skill produces a document. It does NOT edit files. Period.
- **YOU are the filter** — Raw agent output gets filtered through your judgment. Not everything a model says is worth reporting.
- **Dynamic allocation** — Don't use 6 agents on a 2-file PR. Don't use 1 agent on a 50-file PR. Scale to fit.
- **Model diversity** — Mix models. They catch different things.
- **Context is king** — The more context you give agents (PR description, commit messages, related issues), the better their findings.
- **Confidence matters** — Low-confidence findings should be marked as such. Don't present "maybes" as certainties.
- **The doc is the deliverable** — The review document should be comprehensive enough that someone can action it without needing to re-review the PR.
- **Existing reviews matter** — Cross-reference with what other reviewers already said. Don't redundantly flag addressed issues.
- **Props are real findings** — Good code deserves recognition. It's not all criticism.
- **Scale model power to file importance** — Auth code gets opus. Config files get haiku. Be smart about it.
