# Contributing to Snark Girl 💅

## Adding a New Skill

1. Create a new folder: `skills/snark-{skill-name}/SKILL.md`
2. Add YAML frontmatter with `name` and `description` (include trigger phrases)
3. Write the skill procedures in the markdown body

### After Creating the Skill

Update **all** of the following files:

| File | What to Update |
|------|---------------|
| `skills/using-snark-girl/SKILL.md` | Add to "Available Skills" table AND "Skill Priority" numbered list |
| `CLAUDE.md` | Add to "Skill priority" numbered list |
| `README.md` | Add to Skills table, Usage Examples, and Project Structure tree |
| `package.json` | Update `description` and add to `keywords` |
| `.claude-plugin/plugin.json` | Update `description` and `keywords` |
| `.claude-plugin/marketplace.json` | Update plugin `description` |
| `.codex-plugin/plugin.json` | Update `description`, `shortDescription`, `longDescription`, `defaultPrompt`, and `keywords` |
| `.cursor-plugin/plugin.json` | Update `description` and `keywords` |

## Releasing a New Version

### Version Bump Checklist

When bumping the version, update it in **all 5 files**:

- [ ] `package.json`
- [ ] `.claude-plugin/plugin.json`
- [ ] `.claude-plugin/marketplace.json`
- [ ] `.codex-plugin/plugin.json`
- [ ] `.cursor-plugin/plugin.json`

### When to Bump

- **Patch** (`x.x.+1`) — Bug fixes, wording changes, small tweaks
- **Minor** (`x.+1.0`) — New skill added, significant feature changes
- **Major** (`+1.0.0`) — Breaking changes, major restructuring

### Release Steps

1. Make your changes
2. Bump version in all 5 files (see checklist above)
3. Update descriptions if a new skill was added (see table above)
4. Commit with a descriptive message
5. Push to `main`
6. In any Copilot CLI instances: `/plugin update snarkgirl`

## Skill Naming Convention

All skills MUST be prefixed with `snark-` to avoid collisions with built-in Copilot skills:

- ✅ `snark-pr-review`
- ✅ `snark-rubber-duck`
- ❌ `pr-review` (will collide with built-in)
- ❌ `explain` (too generic)

Exception: `using-snark-girl` (bootstrap) and `snark-chat` (already unique).

## Skill Description Format

Every skill's YAML `description` field should:

1. Start with "Use when the user addresses SnarkGirl by name and..."
2. End with trigger phrase examples: `Trigger phrases: 'SnarkGirl, ...', '@SnarkGirl ...'`

This helps the agent match user intent to the correct skill.

## Testing Changes

After pushing:

```
/plugin update snarkgirl
/skills
```

Verify all skills show up and descriptions look correct.
