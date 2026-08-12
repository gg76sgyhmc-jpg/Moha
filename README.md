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

## MCP servers

Configured in [`.mcp.json`](.mcp.json) at project scope, so anyone working in this repo
gets the same servers. Claude Code asks for approval the first time it sees them.

### 21st

[21st.dev](https://21st.dev) component and design MCP server, over HTTP.

Authentication reads the `API_KEY_21ST` environment variable — the key itself is **not**
stored in the repo, only the `${API_KEY_21ST}` reference. Export it before starting
Claude Code:

```bash
export API_KEY_21ST="your-key-here"
```

Put it in your shell profile (or a git-ignored `.env`) rather than committing it. Without
it, `claude mcp list` reports `Missing environment variables: API_KEY_21ST` and the server
returns HTTP 401.

## Menu — أسطا غازي

Redesign of the Usta Ghazi Shawarma menu, in [`menu/`](menu/):

| File | What it is |
|------|-----------|
| `menu/index.html` | The menu — one self-contained file, no network needed |
| `menu/usta-ghazi-menu.pdf` | Print-ready A4, 2 pages |
| `menu/template.html` | Layout and design tokens |
| `menu/logo.svg` | The emblem — **replace with the restaurant's own logo file** |
| `menu/build.py` | Menu data (prices live here) + build step |
| `menu/fonts.css` | Cairo + Tajawal, inlined as base64 |

To change a price, edit the tables at the top of `menu/build.py`, then:

```bash
python3 menu/build.py     # rewrites menu/index.html
```

Both sheets are laid out to fill exactly one A4 page each (1123px at 96dpi),
so printing gives two pages with no overflow. Open `index.html` and print to
PDF to regenerate the PDF.

The emblem in `menu/logo.svg` is traced from the existing menu artwork, not the
original file. Drop the real logo in as `menu/logo.svg` (or wrap a PNG in
`<image href="data:image/png;base64,...">`) and re-run the build — it is inlined
into both sheets from that one file.

To refresh the embedded fonts, re-run `tools/embed_fonts.py` (needs network).
