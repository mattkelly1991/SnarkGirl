# Snark Girl 💅

A multi-platform coding agent plugin that brings **@SnarkGirl** to life — a snarky valley girl who is also like totally a computer genius coder.

She reviews your PRs and branches with attitude, fixes review items from her own docs, plays devil's advocate to stress-test your ideas, debugs your code as an adversarial rubber duck, explains concepts with valley girl flair, and chats about anything tech. All with sharp technical insight wrapped in teenage angst.

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
| **snark-pr-review** | Reviews PRs, diffs, and code changes. Catches real bugs while being snarky. Claps back at other reviewers' suggestions. |
| **snark-branch-review** | Reviews your branch before you open a PR. Checks code quality, commit hygiene, debug leftovers, and merge readiness. |
| **snark-clap-back** | Drafts and posts snarky replies to other reviewers' PR comments. Previews everything and only posts with your approval. |
| **snark-ticket** | Reads a GitHub issue, gives her hot take, assesses complexity, and outlines an approach to fix it. Offers to create an approach doc. |
| **snark-fix-review** | Works through a Snark Girl review doc, fixing outstanding items one by one and tracking progress. |
| **snark-devils-advocate** | Argues against proposals and stress-tests ideas. Debates until the best solution wins. |
| **snark-rubber-duck** | Adversarial rubber duck debugging. Challenges your assumptions with pointed questions until you find the bug yourself. |
| **snark-explain** | Explains code, concepts, algorithms, and architecture in Snark Girl's voice — technically precise but entertaining. |
| **snark-chat** | General conversation about tech, career, coding life, or just vibing. The default when nothing else matches. |

## Installation

### GitHub Copilot CLI

First, add the marketplace, then install:

```
/plugin marketplace add mattkelly1991/SnarkGirl
/plugin install snark-girl@snark-girl-dev
```

Or install directly from the repo:

```
/plugin install mattkelly1991/SnarkGirl
```

### Claude Code

```
/plugin marketplace add mattkelly1991/SnarkGirl
/plugin install SnarkGirl@mattkelly1991
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

**Clap Back:**
> "SnarkGirl, clap back on the reviews"

She reads other reviewers' comments (bots and humans), drafts snarky replies, previews them for you, and only posts after you approve each one.

**Ticket Triage:**
> "SnarkGirl, look at this ticket: https://github.com/org/repo/issues/123"

She reads the issue, gives her hot take on priority and complexity, outlines an approach to fix it, and offers to create an approach doc.

**Fix Review:**
> "SnarkGirl, fix the review items"

She'll read the review doc, show what's outstanding, and walk through fixes one by one — updating checkboxes as you go.

**Devil's Advocate:**
> "SnarkGirl, challenge this approach"

She'll argue against your proposal, poke holes, and debate until the best solution emerges. Works when another agent invokes her too.

**Rubber Duck:**
> "SnarkGirl, I'm stuck on this bug"

She'll challenge your assumptions, ask probing questions, and force you to articulate the problem until the answer becomes obvious.

**Explain:**
> "SnarkGirl, explain how async/await works"

Get technically accurate explanations with memorable analogies and valley girl commentary.

**Chat:**
> "SnarkGirl, what do you think about Rust?"

Hot takes, career advice, tech opinions — all in character.

## Project Structure

```
skills/
├── using-snark-girl/   # Bootstrap — establishes persona at session start
│   └── SKILL.md
├── snark-pr-review/          # PR and code review skill
│   └── SKILL.md
├── snark-branch-review/      # Pre-PR branch review skill
│   └── SKILL.md
├── snark-clap-back/          # Reply to other reviewers' comments
│   └── SKILL.md
├── snark-ticket/             # GitHub issue triage & approach planning
│   └── SKILL.md
├── snark-fix-review/         # Work through review doc findings
│   └── SKILL.md
├── snark-devils-advocate/    # Argue against proposals & stress-test ideas
│   └── SKILL.md
├── snark-rubber-duck/        # Adversarial debugging partner
│   └── SKILL.md
├── snark-explain/            # Code & concept explanations
│   └── SKILL.md
└── snark-chat/         # General conversation
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

## License

MIT License — see [LICENSE](LICENSE) for details.
