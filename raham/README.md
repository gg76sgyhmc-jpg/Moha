# قهوة رهم — Raham Coffee

One page for the café in Al Khobar, holding two views:

- the **links** view — menu, Instagram, TikTok, Snapchat, delivery, map;
- the **menu** — 21 items across المشروبات and الحلا, priced as the in-store
  boards price them, with English names, descriptions, calories and photos.

Tapping المنيو swaps the view on the URL hash instead of loading a second
document, so the back button works, `#menu` is shareable, and the whole thing
is one file. Every other row is an ordinary external link that opens in a new
tab. With JavaScript off, a `:target` rule opens the menu from the same hash.

- **`index.html`** — the page, with `assets/` beside it so the browser caches them.
- **`raham-one-file.html`** — the same page with fonts and all 22 photos inlined:
  0.7MB, no other file needed. This is the one to email or drop on a host.

## Run it

```bash
python3 -m http.server -d raham 8080     # http://localhost:8080
```

Deploy by uploading the `raham/` folder to any static host — or just
`raham-one-file.html` on its own, which carries everything it needs. There is
no build step at serve time and no third-party requests: fonts and photos are
local either way.

## Files

| Path | What it is |
|------|-----------|
| `index.html` | The page. Generated — edit `template.html`, not this. |
| `raham-one-file.html` | The same page, fonts and photos inlined. One file, nothing else. |
| `template.html` | Both views, the design tokens, and the hash router. |
| `build.py` | Renders `template.html` + `data/` into the two outputs. |
| `data/menu.json` | 21 items, transcribed from the in-store boards. |
| `build_menu_data.py` | Rebuilds that file from the boards, carrying photos across. |
| `data/brand.json` | Links, rating, map, and the phone slot. |
| `assets/` | Logo, menu photos, webfonts. |
| `build_assets.py` | Trims the logo and re-encodes photos to WebP. |
| `build_fonts.py` | Fetches the webfont as local files (needs network). |

## Where the content came from

Nothing here is written to fill space. The café's own listings were the source:

| Fact | Source |
|------|--------|
| 21 menu items: Arabic and English names, prices | the café's printed in-store menu boards |
| Descriptions, calorie figures, photos | HungerStation vendor record, matched by item |
| Logo and cover photograph | HungerStation vendor record |
| Rating 4.7 from 249 reviews | HungerStation vendor record |
| Instagram, TikTok, Snapchat | the café's public accounts |
| Map pin | the Google Maps link supplied by the owner |

`data/menu.json` and `data/brand.json` hold all of it. Editing a price there and
re-running the build is the whole update path.

## Missing: the phone number

**No phone number is published on any listing that could be reached** — not the
Google Maps pin, not Snapchat, not the delivery listing, and Instagram blocks
automated reads. Rather than print a plausible-looking number, `brand.json` has
`"phone": null` and no call row is rendered.

To add it, set the number in `data/brand.json` and rebuild:

```json
"phone": "05XXXXXXXX",
```

The build inserts a call row directly under the menu on the links page, with a
`tel:` link. Nothing else needs changing.

## Two locations

The map pin supplied by the owner is in **الشفيه, Al Khobar**. The delivery
listing and the Snapchat place are a different address — **الصواري (العزيزية)**.
Both are linked, but the pages do not claim how many branches there are, since
that is not stated anywhere in the sources. The menu came from the delivery
listing, so confirm it matches the other location before printing it.

## Brand

The palette is the café's own, measured rather than chosen:

| Token | Value | Where it came from |
|-------|-------|--------------------|
| `--ink-900` | `#151D15` | the deep green of their menu boards — 98.9% of the supplied artwork's pixels |
| `--cream` | `#F3F0D7` | the cream type on those same boards |
| `--sage` | `#A3AE84` | the green behind the logo's calligraphy, kept as the accent |

Both views run cream on the deep green, which is how their printed menu reads.

## Prices

The boards are the price of record. The delivery listing carries a markup —
قهوة اليوم is 5 in-store and 7 on delivery — so the menu footer says so rather
than letting a visitor arrive expecting the wrong number.

Five items on the delivery listing are not on the boards and are not shown:
بوكس القهوه، كرانشي كيك، رمان تشوكلت بار، بستاشيو تشوكلت بار، تشيز كيك مدريد.
Three board items have no photo on file: براونيز، كندر كنافة، كرات الطاقه.

The logo is used exactly as supplied. `build_assets.py` only trims it to its own
edges; `logo-mark.webp` is the same mark with the sage keyed out, for the places
where the page's own green is already the ground — the same figure/ground the
original has. The calligraphy is never redrawn.

Type is IBM Plex Sans Arabic in three weights, carrying both pages on weight and
tracking alone. The logo is already a piece of calligraphy; a second display
face would compete with it.

## Rebuild

```bash
python3 raham/build.py           # after editing data/ or a template
python3 raham/build_assets.py    # re-encode photos (needs raham/_src/, untracked)
python3 raham/build_fonts.py     # refetch the webfont (needs network)
```

`build.py` asserts every placeholder was filled, so a typo fails the build
rather than shipping `@LIKE_THIS@` to the page.

## Note on the source photos

`raham/_src/` (the original full-size JPEGs, ~8.8MB) is not tracked. The
optimised WebP set in `assets/` is 0.31MB and is what the pages use.
