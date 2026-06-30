CLAUDE.md

## Version Bumps

A version bump is a full release. When bumping the version, do ALL of the following:

1. **Update the version in all 5 files** (keep them identical):
   - `package.json`
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `.codex-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
2. **Add a `CHANGELOG.md` entry** for the new version (Keep a Changelog format) summarizing what changed.
3. **Generate release notes** for the version.
4. **Publish the release** — tag the commit and create the GitHub Release (`gh release create vX.Y.Z`), and refresh the GitHub Marketplace listing if the Action metadata changed.

## Descriptions

The `description` field must stay in sync across all plugin files. If you update the description in one, update it in all of them:

- `package.json` → `description`
- `.claude-plugin/plugin.json` → `description`
- `.claude-plugin/marketplace.json` → plugin `description`
- `.codex-plugin/plugin.json` → `description`, `shortDescription`, `longDescription`
- `.cursor-plugin/plugin.json` → `description`