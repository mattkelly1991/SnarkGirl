CLAUDE.md

## Version Bumps

When bumping the version, update ALL 5 of these files:

1. `package.json`
2. `.claude-plugin/plugin.json`
3. `.claude-plugin/marketplace.json`
4. `.codex-plugin/plugin.json`
5. `.cursor-plugin/plugin.json`

## Descriptions

The `description` field must stay in sync across all plugin files. If you update the description in one, update it in all of them:

- `package.json` → `description`
- `.claude-plugin/plugin.json` → `description`
- `.claude-plugin/marketplace.json` → plugin `description`
- `.codex-plugin/plugin.json` → `description`, `shortDescription`, `longDescription`
- `.cursor-plugin/plugin.json` → `description`