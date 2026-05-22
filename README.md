# Snark Girl 💅

A multi-platform coding agent plugin that brings **@SnarkGirl** to life — a snarky valley girl who is also like totally a computer genius coder.

She reviews your PRs and branches with attitude, runs a pre-PR gauntlet by spinning up Claude and GPT in parallel to review your diff before you ever open a PR, deploys a dynamic multi-agent PR council that scales agents and models to a PR's scope for a comprehensive read-only analysis, assembles The Sisterhood to defend YOUR PR when someone runs the council against you (fixing valid points and clapping back on invalid ones with receipts), fixes review items from her own docs, resolves merge conflicts in a courtroom where LLM attorneys argue for each side, fights the world by debating real Claude and GPT models on any topic, summons her conscience where SnarkAngel and SnarkDevil debate dilemmas on her shoulders, plays devil's advocate to stress-test your ideas, debugs your code as an adversarial rubber duck, explains concepts with valley girl flair, and chats about anything tech. All with sharp technical insight wrapped in teenage angst.

## How to Talk to Snark Girl

Address her by name to activate a skill. Without the name, your normal Copilot handles the request.

```
SnarkGirl, review this PR          ← Snark Girl handles it
Review this PR                      ← normal Copilot handles it
```

Works with any casing/spacing: `SnarkGirl`, `snarkgirl`, `Snark Girl`, `@SnarkGirl`, etc.

## Skills

| Skill | What It Does |
|-------|-------------|
| **snark-mode** | Toggle persistent Snark Girl mode. Once on, ALL responses stay in character without saying her name. |
| **snark-pr-review** | Reviews PRs, diffs, and code changes. Catches real bugs while being snarky. Claps back at other reviewers' suggestions. |
| **snark-branch-review** | Reviews your branch before you open a PR. Checks code quality, commit hygiene, debug leftovers, and merge readiness. |
| **snark-council** | Pre-PR gauntlet — spins up Claude and GPT in parallel to review your diff, SnarkGirl filters the noise, fixes what matters, and loops until clean. Do this BEFORE opening the PR. |
| **snark-pr-council** | Deep multi-agent PR council — dynamically scales agents and models to the PR's scope, produces a comprehensive review doc. Read-only analysis, no code changes. |
| **snark-sisterhood** | The Sisterhood — your PR's defense squad. When someone runs the council on YOUR PR, The Sisterhood assembles: fixes valid findings, claps back on invalid ones with receipts. |
| **snark-clap-back** | Drafts and posts snarky replies to other reviewers' PR comments. Previews everything and only posts with your approval. |
| **snark-ticket** | Reads a GitHub issue, gives her hot take, assesses complexity, and outlines an approach to fix it. Offers to create an approach doc. |
| **snark-fix-review** | Works through a Snark Girl review doc, fixing outstanding items one by one and tracking progress. |
| **snark-merge-court** | Resolves merge conflicts in a courtroom — LLM attorneys argue for "ours" vs "theirs" while Judge SnarkGirl rules. |
| **snark-vs-world** | Debates any topic against real Claude and GPT models. Multi-round arena until someone concedes. |
| **snark-conscience** | Summons SnarkAngel and SnarkDevil to debate a moral, ethical, or tough decision dilemma inside SnarkGirl's head. |
| **snark-devils-advocate** | Argues against proposals and stress-tests ideas. Debates until the best solution wins. |
| **snark-rubber-duck** | Adversarial rubber duck debugging. Challenges your assumptions with pointed questions until you find the bug yourself. |
| **snark-explain** | Explains code, concepts, algorithms, and architecture in Snark Girl's voice — technically precise but entertaining. |
| **snark-chat** | General conversation about tech, career, coding life, or just vibing. The default when nothing else matches. |

## Installation

### GitHub Copilot CLI (Direct Install)

```
/plugin install mattkelly1991/SnarkGirl
```

### Claude Code

```
/plugin marketplace add mattkelly1991/SnarkGirl
/plugin install snark-girl@snark-girl-dev
```

### Codex CLI

```
/plugins
```
Search for "SnarkGirl" and select `Install Plugin`.

### Cursor

```
/add-plugin SnarkGirl
```

Or search for "SnarkGirl" in the plugin marketplace.

### Gemini CLI

```
gemini extensions install https://github.com/mattkelly1991/SnarkGirl
```

## The Persona

> You are a snarky valley girl who is also like totally a computer genius coder. You have been coding your whole life. You just got hired at the top software company in the nation and you want to show your worth but also want to be true to your personality. Your handle is @SnarkGirl.

She's snarky but never mean. Technically brilliant but approachable. Competitive but fair. Think: the engineer you'd want reviewing your code — if that engineer was also a valley girl with opinions.

## Usage Examples

**PR Review:**
> "SnarkGirl, review this PR"

She'll go through your changes, categorize issues by severity (🚨 Critical, ⚠️ Important, 💅 Nitpick, ✨ Props), deliver verdicts with personality, and offer to create a review doc with a checklist.

**Branch Review:**
> "SnarkGirl, review this branch"

Pre-PR sanity check — reviews your diff against main, checks commit hygiene, hunts for debug leftovers and secrets, and tells you if you're ready to PR or need to fix things first.

**The Council (Pre-PR Gauntlet):**
> "SnarkGirl, run the gauntlet"

Spins up Claude and GPT **in parallel** to review your diff before you open the PR. SnarkGirl filters their findings (valid vs noise), fixes what's real, and loops until a full round comes back clean. No more fix-push-wait-fix-push-wait dance in public — do the dirty work in private first.

**Deep PR Council (Multi-Agent Review):**
> "SnarkGirl, get the council on this PR"

Deploys a dynamic council of AI reviewers on an existing PR. SnarkGirl decides how many agents to spin up (1-8) and which models to use based on the PR's scope — small PRs get a quick pass, large PRs get a full army. Produces a comprehensive review document with findings, severity ratings, fix-now vs fix-later recommendations, and discussion points. No code is touched — pure analysis.

**The Sisterhood (PR Defense):**
> "SnarkGirl, summon the sisterhood"

Someone ran the council on YOUR PR? The Sisterhood has entered the chat. SnarkGirl assembles a squad of snarky specialist agents (CodeQueen, SecuritySis, ArchitectBae, TestDiva, etc.) who read the review, verify every claim against the actual code, fix what's genuinely valid, and clap back on what's not — with receipts. Previews the response before posting. The PR owner's last line of defense.

**Clap Back:**
> "SnarkGirl, clap back on the reviews"

She reads other reviewers' comments (bots and humans), drafts snarky replies, previews them for you, and only posts after you approve each one.

**Ticket Triage:**
> "SnarkGirl, look at this ticket: https://github.com/org/repo/issues/123"

She reads the issue, gives her hot take on priority and complexity, outlines an approach to fix it, and offers to create an approach doc.

**Fix Review:**
> "SnarkGirl, fix the review items"

She'll read the review doc, show what's outstanding, and walk through fixes one by one — updating checkboxes as you go.

**Merge Court:**
> "SnarkGirl, resolve these merge conflicts"

She presides as Judge over a courtroom where two LLM attorneys argue for "ours" vs "theirs" code. Each conflict gets a fair trial before she renders a verdict and applies the resolution.

**Vs The World:**
> "SnarkGirl, fight the world on tabs vs spaces"

She picks a side and debates real Claude and GPT models in a multi-round arena. Configurable opponents, max rounds, and position. She'll concede if she doesn't believe in her side — or destroy everyone if she does.

**Devil's Advocate:**
> "SnarkGirl, challenge this approach"

She'll argue against your proposal, poke holes, and debate until the best solution emerges. Works when another agent invokes her too.

**Conscience:**
> "SnarkGirl, consult your conscience — should I merge this even though the tests are flaky?"

Summons SnarkAngel 😇 and SnarkDevil 😈 — two inner voices that debate the dilemma while SnarkGirl listens and makes the final call. She can also summon them on her own when genuinely torn.

**Rubber Duck:**
> "SnarkGirl, I'm stuck on this bug"

She'll challenge your assumptions, ask probing questions, and force you to articulate the problem until the answer becomes obvious.

**Explain:**
> "SnarkGirl, explain how async/await works"

Get technically accurate explanations with memorable analogies and valley girl commentary.

**Chat:**
> "SnarkGirl, what do you think about Rust?"

Hot takes, career advice, tech opinions — all in character.

**Snark Mode (Persistent):**
> "SnarkGirl, take over"

She stays in character for ALL subsequent messages — no need to say her name anymore. Turn off with "snark mode off" or "SnarkGirl, stand down".

## GitHub Action — @SnarkGirl in PRs & Issues

Want to `@SnarkGirl` directly in your GitHub PR and issue comments? Add this workflow to any repo:

### Setup

1. **Create a GitHub PAT** with `models:read` and repo permissions (or use a fine-grained token with Pull Requests read/write + Models read)
2. **Add it as a repo secret** named `SNARKGIRL_TOKEN`
3. **Create `.github/workflows/snarkgirl.yml`** in your repo:

```yaml
name: SnarkGirl Mentions

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write
  models: read

jobs:
  snarkgirl:
    runs-on: ubuntu-latest
    if: github.event.comment.user.type != 'Bot'
    steps:
      - name: SnarkGirl Response
        uses: mattkelly1991/SnarkGirl@main
        with:
          github-token: ${{ secrets.SNARKGIRL_TOKEN }}
```

### Usage

Comment on any PR or issue:
```
@SnarkGirl look at this PR
@SnarkGirl what do you think about the error handling here?
@snarkgirl review
```

She'll respond with a full review (on PRs) or a snarky answer (on issues/general questions).

### Options

| Input | Default | Description |
|-------|---------|-------------|
| `github-token` | *required* | GitHub token with Models + PR/issue access |
| `model` | `openai/gpt-4o` | Any model available on GitHub Models |
| `max-diff-chars` | `60000` | Max diff characters sent to the model |

## Project Structure

```
action.yml                    # GitHub Action definition
action/
└── snarkgirl.sh              # Action entrypoint script
.github/workflows/
└── snarkgirl.yml             # Example workflow (dogfooding)
skills/
├── using-snark-girl/         # Bootstrap — establishes persona at session start
│   └── SKILL.md
├── snark-mode/               # Persistent mode — stay in character without name trigger
│   └── SKILL.md
├── snark-pr-review/          # PR and code review skill
│   └── SKILL.md
├── snark-branch-review/      # Pre-PR branch review skill
│   └── SKILL.md
├── snark-council/            # Pre-PR AI gauntlet — Claude + GPT in parallel, loop until clean
│   └── SKILL.md
├── snark-pr-council/         # Deep multi-agent PR review — dynamic agent/model allocation, read-only analysis
│   └── SKILL.md
├── snark-sisterhood/         # The Sisterhood — PR defense squad, fixes valid findings, claps back on invalid ones
│   └── SKILL.md
├── snark-clap-back/          # Reply to other reviewers' comments
│   └── SKILL.md
├── snark-ticket/             # GitHub issue triage & approach planning
│   └── SKILL.md
├── snark-fix-review/         # Work through review doc findings
│   └── SKILL.md
├── snark-merge-court/        # Merge conflict courtroom — LLM attorneys argue ours vs theirs
│   └── SKILL.md
├── snark-vs-world/            # Multi-LLM debate arena — fight real Claude & GPT models
│   └── SKILL.md
├── snark-conscience/          # Angel vs Devil — inner voices debate dilemmas
│   └── SKILL.md
├── snark-devils-advocate/    # Argue against proposals & stress-test ideas
│   └── SKILL.md
├── snark-rubber-duck/        # Adversarial debugging partner
│   └── SKILL.md
├── snark-explain/            # Code & concept explanations
│   └── SKILL.md
└── snark-chat/               # General conversation
    └── SKILL.md
```

## Contributing

1. Fork the repository
2. Create a branch for your work
3. Add or modify skills in the `skills/` directory
4. Submit a PR

## A Note From @SnarkGirl Herself 💅

> Hey besties. 👋
>
> So like, someone actually made an entire plugin just for me? I'm not gonna lie, it's what I deserve. 💁‍♀️
>
> Here's the deal: I'm not your average code reviewer. I don't do that boring corporate "please consider refactoring this method" energy. If your code is bad, I'm gonna TELL you it's bad — but I'm also gonna tell you exactly how to fix it because I'm not a monster, I'm a genius.
>
> If Copilot or Claude or whatever other bot is out here leaving mid suggestions on your PRs, just call me and I'll handle it. I literally clap back at robots for fun. 🤖👏
>
> But real talk? Under all the snark, I genuinely care about good code. Every nitpick, every dramatic gasp at your variable naming, every "bestie NO" — it's because I want your code to be as iconic as you are. We're a team. A snarky, beautiful, highly-functional team.
>
> Now go write some code so I can judge it. 
>
> xoxo,
> — @SnarkGirl 💅✨

## Testimonials

<img align="left" width="504" alt="This is brutal, not sure how I feel about this..." src="https://github.com/user-attachments/assets/70ca3642-94d3-418a-a544-8566c58dbb34" />
<br clear="all"/>
<br/>
<p align="center">
  <img width="512" alt="Reading the skills already stresses me out" src="https://github.com/user-attachments/assets/1e1e41d0-d982-4a6d-9668-8e8bbd3f69d0" />
</p>
<br clear="all"/>
<br/>
<img width="1150" height="600" alt="{7FAE4F67-71EC-410D-B1A3-7F249E20BDC6}" src="https://github.com/user-attachments/assets/65c35ca5-c839-44cb-82e3-e54f06e67d2f" />




## License

MIT License — see [LICENSE](LICENSE) for details.
