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
| `menu/logo.svg` | The restaurant's logo, inlined into both sheets |
| `menu/logo.png` | The cleaned-up logo bitmap |
| `menu/build.py` | Menu data (prices live here) + build step |
| `menu/fonts.css` | Cairo + Tajawal, inlined as base64 |

To change a price, edit the tables at the top of `menu/build.py`, then:

```bash
python3 menu/build.py     # rewrites menu/index.html
```

Both sheets are laid out to fill exactly one A4 page each (1123px at 96dpi),
so printing gives two pages with no overflow. Open `index.html` and print to
PDF to regenerate the PDF.

### The logo

`menu/logo.svg` carries the restaurant's own mark, recovered from the supplied
artwork by `tools/extract_logo.py` (removes the menu background around it) and
`tools/enhance_logo.py` (upscales 4x and restores the flat cream/red the JPEG
had smeared). The mark itself is not redrawn — shapes, proportions and
letterforms are the original.

Detail is still bounded by the 93x104 px source. When the original vector or
high-resolution logo turns up, replace `menu/logo.svg` with it and re-run the
build; both sheets are inlined from that one file.

To refresh the embedded fonts, re-run `tools/embed_fonts.py` (needs network).

## Elegance Bar — website

A rebuild of the Elegance Bar Ladies Salon site, in [`site/`](site/). Open
`site/index.html`, or serve the folder:

```bash
python3 -m http.server -d site 8080
```

All 78 services, their prices, durations, photos and the booking policies are
pulled from the salon's own live booking profile — see
[`site/README.md`](site/README.md) for the data source, rebuild steps, and the
details the source data does not carry.

## قهوة رهم — Raham Coffee

A links page and a rebuilt menu for the café in Al Khobar, in [`raham/`](raham/):

```bash
python3 -m http.server -d raham 8080
```

All 23 menu items, their prices, descriptions and photos, plus the rating and
every link, come from the café's own public listings. No phone number is
published on any of them, so none is shown — see [`raham/README.md`](raham/README.md)
for how to add it, and for the two-location caveat.
