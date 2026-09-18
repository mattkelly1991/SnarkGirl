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
5. **Always provide the Marketplace publish link** after the release succeeds:
   `https://github.com/mattkelly1991/SnarkGirl/releases/edit/vX.Y.Z`
   Publishing to the Marketplace is a manual web-UI step with no API or `gh` equivalent: the user opens that
   page, ticks **"Publish this Action to the GitHub Marketplace"** at the top, and clicks **Update release**.
   Say so explicitly every time; do not just paste the link. Use the release's full 40-char commit SHA for
   `--target` — `gh release create` rejects short SHAs with `target_commitish is invalid`.

## Descriptions

The `description` field must stay in sync across all plugin files. If you update the description in one, update it in all of them:

- `package.json` → `description`
- `.claude-plugin/plugin.json` → `description`
- `.claude-plugin/marketplace.json` → plugin `description`
- `.codex-plugin/plugin.json` → `description`, `shortDescription`, `longDescription`
- `.cursor-plugin/plugin.json` → `description`