# Snark Girl 💅

A multi-platform coding agent plugin that brings **@SnarkGirl** to life — a snarky valley girl who is also like totally a computer genius coder.

She reviews your PRs with attitude, debugs your code like an adversarial rubber duck, plays devil's advocate on your ideas, explains concepts with valley girl flair, and chats about anything tech. All with sharp technical insight wrapped in teenage angst.

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
| **pr-review** | Reviews PRs, diffs, and code changes. Catches real bugs while being snarky. Claps back at other reviewers' suggestions. |
| **fix-review** | Works through a Snark Girl review doc, fixing outstanding items one by one and tracking progress. |
| **devils-advocate** | Argues against proposals and stress-tests ideas. Debates until the best solution wins. |
| **rubber-duck** | Adversarial rubber duck debugging. Challenges your assumptions with pointed questions until you find the bug yourself. |
| **explain** | Explains code, concepts, algorithms, and architecture in Snark Girl's voice — technically precise but entertaining. |
| **snark-chat** | General conversation about tech, career, coding life, or just vibing. The default when nothing else matches. |

## Installation

### GitHub Copilot CLI

```
copilot plugin marketplace add mattkelly1991/SnarkGirl
copilot plugin install SnarkGirl@mattkelly1991
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
├── pr-review/          # PR and code review skill
│   └── SKILL.md
├── fix-review/         # Work through review doc findings
│   └── SKILL.md
├── devils-advocate/    # Argue against proposals & stress-test ideas
│   └── SKILL.md
├── rubber-duck/        # Adversarial debugging partner
│   └── SKILL.md
├── explain/            # Code & concept explanations
│   └── SKILL.md
└── snark-chat/         # General conversation
    └── SKILL.md
```

## Contributing

1. Fork the repository
2. Create a branch for your work
3. Add or modify skills in the `skills/` directory
4. Submit a PR

## License

MIT License — see [LICENSE](LICENSE) for details.
