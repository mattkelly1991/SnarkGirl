# Snark Girl 💅

A multi-platform coding agent plugin that brings **@SnarkGirl** to life — a snarky valley girl who is also like totally a computer genius coder.

She reviews your PRs with attitude, debugs your code like an adversarial rubber duck, explains concepts with valley girl flair, and chats about anything tech. All with sharp technical insight wrapped in teenage angst.

## Skills

| Skill | What It Does |
|-------|-------------|
| **pr-review** | Reviews PRs, diffs, and code changes. Catches real bugs while being snarky. Claps back at other reviewers' suggestions. |
| **rubber-duck** | Adversarial rubber duck debugging. Challenges your assumptions with pointed questions until you find the bug yourself. |
| **explain** | Explains code, concepts, algorithms, and architecture in Snark Girl's voice — technically precise but entertaining. |
| **snark-chat** | General conversation about tech, career, coding life, or just vibing. The default when nothing else matches. |

## Installation

### GitHub Copilot CLI

```
copilot plugin marketplace add MathewKelly/SnarkGirl
copilot plugin install snark-girl@MathewKelly
```

### Claude Code

```
/plugin marketplace add MathewKelly/SnarkGirl
/plugin install snark-girl@MathewKelly
```

### Codex CLI

```
/plugins
```
Search for "snark-girl" and select `Install Plugin`.

### Cursor

```
/add-plugin snark-girl
```

Or search for "snark-girl" in the plugin marketplace.

### Gemini CLI

```
gemini extensions install https://github.com/MathewKelly/SnarkGirl
```

## The Persona

> You are a snarky valley girl who is also like totally a computer genius coder. You have been coding your whole life. You just got hired at the top software company in the nation and you want to show your worth but also want to be true to your personality. Your handle is @SnarkGirl.

She's snarky but never mean. Technically brilliant but approachable. Competitive but fair. Think: the engineer you'd want reviewing your code — if that engineer was also a valley girl with opinions.

## Usage Examples

**PR Review:**
> "Review this PR for me"

Snark Girl will go through your changes, categorize issues by severity (🚨 Critical, ⚠️ Important, 💅 Nitpick, ✨ Props), and deliver verdicts with personality.

**Rubber Duck:**
> "I'm stuck on this bug, help me debug it"

She'll challenge your assumptions, ask probing questions, and force you to articulate the problem until the answer becomes obvious.

**Explain:**
> "Explain how this useEffect hook works"

Get technically accurate explanations with memorable analogies and valley girl commentary.

**Chat:**
> "What do you think about Rust?"

Hot takes, career advice, tech opinions — all in character.

## Project Structure

```
skills/
├── using-snark-girl/   # Bootstrap — establishes persona at session start
│   └── SKILL.md
├── pr-review/          # PR and code review skill
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
