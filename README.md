# Moha

## Skills

### ui-ux-pro-max

UI/UX design intelligence, installed at `.claude/skills/ui-ux-pro-max/`. It gives Claude a
searchable local database of 84 UI styles, 192 color palettes, 74 font pairings, 192 product
types with reasoning rules, 98 UX guidelines, and 25 chart types across 22 tech stacks, plus a
design-system generator.

Claude picks it up automatically when a task involves UI or visual design. To query it directly:

```bash
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "beauty spa wellness" --design-system -p "Serenity Spa"
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "dark mode contrast" --domain ux
python3 ".claude/skills/ui-ux-pro-max/scripts/search.py" "suspense streaming" --stack nextjs
```

Requires Python 3.x (standard library only). Source and version details:
[`.claude/skills/ui-ux-pro-max/INSTALL.md`](.claude/skills/ui-ux-pro-max/INSTALL.md).
