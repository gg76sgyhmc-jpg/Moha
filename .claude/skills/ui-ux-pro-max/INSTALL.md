# ui-ux-pro-max — install notes

Vendored from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).

- Version: 2.13.0
- Upstream commit: 97eb2a20032f0833e3d317162208a60385b0f96e (2026-08-12)
- License: MIT (see upstream repository)

## Local modifications

- Script paths in `SKILL.md` were rewritten from `${CLAUDE_PLUGIN_ROOT}/.claude/skills/...`
  (plugin-install layout) to the project-relative `.claude/skills/ui-ux-pro-max/...`,
  since this is a project-level skill rather than a marketplace plugin install.
- `scripts/tests/` was dropped; it is only needed for upstream development.

## Requirements

Python 3.x, standard library only. No external dependencies, no network calls.

## Verify

```bash
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "dark mode contrast" --domain ux -n 2
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "saas analytics dashboard" --design-system -p "Moha"
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "suspense streaming" --stack nextjs
```

## Updating

Re-copy `.claude/skills/ui-ux-pro-max/` from the upstream repository, then re-apply the
two modifications above. Alternatively use the upstream CLI (`npm install -g ui-ux-pro-max-cli`,
then `uipro init --ai claude`), which writes the project-relative paths directly.
