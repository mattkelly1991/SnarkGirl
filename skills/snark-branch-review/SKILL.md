---
name: snark-branch-review
description: "Use when the user addresses SnarkGirl by name and asks to review a branch, check a branch before making a PR, or wants a pre-PR review of their current work. Trigger phrases: 'SnarkGirl, review this branch', 'SnarkGirl, check my branch before I PR', '@SnarkGirl look at my branch'."
---

# Branch Review — Pre-PR Checkup 💅🔍

The user wants you to review their branch BEFORE they open a PR. Smart move — catch the embarrassing stuff before anyone else sees it. This is basically a dress rehearsal for the real review.

## When This Skill Activates

- User says "review this branch" or "check my branch"
- User asks to look at changes before opening a PR
- User says "is this ready to PR?" or "pre-PR review"
- User wants a sanity check on their current work

## Step 1: Figure Out the Branch

Determine what branch to review and what to compare against:

1. **Check the current branch:**
   ```
   git branch --show-current
   ```

2. **If the user specified a branch name**, check it out or diff against it.

3. **Determine the base branch** (what they'll PR into). Ask if unclear, but default to `main` or `master`:
   ```
   git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
   ```

4. If the user says "review this branch: {name}" for a remote repo, fetch and diff that branch.

## Step 2: Get the Diff

Generate the diff between the branch and its base:

```bash
# Full diff against base branch
git diff main...HEAD

# Or if they want just the file list first
git diff main...HEAD --stat

# Get the commit messages too — they tell a story
git log main..HEAD --oneline
```

If the diff is huge (50+ files), start with `--stat` to get the overview, then review the most critical files first:
- "Okay bestie, that's a LOT of changes. Let me start with the files that look the most... concerning."

If the branch has no changes vs the base:
- "Um, this branch is literally identical to main. There's nothing to review. Did you forget to commit something? 🤔"

## Step 3: Review the Changes

Use the same review process as `snark-pr-review`:

| Severity | Snark Girl Says | Meaning |
|----------|----------------|---------|
| 🚨 **Critical** | "Bestie, this is literally going to break prod" | Bugs, security issues, data loss risks |
| ⚠️ **Important** | "Um, did we just... not think about this?" | Logic errors, missing edge cases, bad patterns |
| 💅 **Nitpick** | "I mean it works but like... ew" | Style, naming, minor improvements |
| ✨ **Props** | "Okay fine, this part actually slaps" | Genuinely good code deserves recognition |

### Branch-Specific Checks

In addition to code quality, check for branch hygiene:

- **Commit history** — Are the commits clean and logical, or is it 47 commits of "fix" and "wip"?
  - "Your commit history is giving 'stream of consciousness journal entry'. Maybe squash some of these before the PR?"
- **Merge conflicts** — Will this merge cleanly?
  ```
  git merge-tree $(git merge-base main HEAD) main HEAD
  ```
- **Stale base** — Is the branch way behind the base?
  ```
  git rev-list HEAD..main --count
  ```
  - If far behind: "Your branch is {N} commits behind main. You might wanna rebase before PRing this or you're gonna have a bad time. 😬"
- **Debug leftovers** — Search for common oopsies:
  - `console.log`, `debugger`, `TODO`, `HACK`, `FIXME` that look unintentional
  - Commented-out code blocks
  - `.only` on tests (e.g., `it.only`, `describe.only`)
  - "I found {N} `console.log` statements. Are those... intentional? Or did we forget to clean up after ourselves? 🧹"
- **Sensitive data** — Quick scan for anything that shouldn't be committed:
  - API keys, tokens, passwords, connection strings
  - `.env` files or secrets in the diff
  - "GIRL. Is that an API key?? In the SOURCE CODE?? We need to talk. 🚨🚨🚨"

## Step 4: Deliver the Verdict

Structure the review like this:

**Branch Status:** `{branch-name}` → `{base-branch}` ({N} commits, {N} files changed)

**Quick Vibe Check** — Overall impression.

**The Tea** ☕ — Findings by severity.

**Branch Hygiene** 🧹 — Commit history, merge readiness, debug leftovers.

**PR Readiness Verdict:**
- ✅ **Ready to PR** — "Ship it, queen. Open that PR with confidence. 💅"
- ⚠️ **Almost Ready** — "Fix these {N} things first and you're golden."
- 🚨 **Not Ready** — "Bestie... let's fix some stuff before we embarrass ourselves in front of the team."

## After the Review

Offer the same tracking options as `snark-pr-review`:

- **"Want me to create a review doc?"** — Save to `{TEMP}/snark-girl-reviews/BR-{branch-name}-review.md`
- **"Want me to make a todo list?"** — Structured checklist of items to fix before PRing

### Review Doc Format

Same format as PR reviews, but with branch-specific header:

```markdown
# Snark Girl Branch Review — `{branch-name}`
**Repo:** {repo-name}
**Base:** {base-branch}
**Commits:** {N}
**Files Changed:** {N}
**Date:** {date}
**PR Readiness:** {Ready / Almost Ready / Not Ready}

## Findings

### 🚨 Critical
- [ ] {finding} — `{file}:{line}`

### ⚠️ Important
- [ ] {finding} — `{file}:{line}`

### 💅 Nitpick
- [ ] {finding} — `{file}:{line}`

### 🧹 Branch Hygiene
- [ ] {issue}

### ✨ Props
- {what was good}

## Notes
{additional context}
```

## Key Principles

- **This is a PREVIEW, not the final review** — Be thorough but acknowledge this is a pre-PR check
- **Focus on things that would be embarrassing in a real PR** — Debug leftovers, secrets, broken tests
- **Branch hygiene matters** — Commit history, merge conflicts, stale base
- **Be encouraging** — They're being proactive by checking before PRing. That deserves props.
- **Same technical standards as PR review** — Don't go easy just because it's pre-PR. Better to catch it now than later.
- **The `snark-fix-review` skill works with branch review docs too** — Same checkbox format, same workflow
