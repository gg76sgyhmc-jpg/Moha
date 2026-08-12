# قهوة رهم — Raham Coffee

Two pages for the café in Al Khobar:

- **`index.html`** — the links page: menu, Instagram, TikTok, Snapchat, delivery, map.
- **`menu.html`** — the menu, rebuilt: 23 items across 2 categories with prices,
  descriptions, calories and photos.

## Run it

```bash
python3 -m http.server -d raham 8080     # http://localhost:8080
```

Deploy by uploading the `raham/` folder to any static host. There is no build
step at serve time and no third-party requests — fonts and photos are local.
`standalone-links.html` and `standalone-menu.html` are single-file copies with
everything inlined, for sending as an attachment.

## Where the content came from

Nothing here is written to fill space. The café's own listings were the source:

| Fact | Source |
|------|--------|
| 23 menu items: names, prices, descriptions, calories, photos | HungerStation vendor record |
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
| `--sage` | `#A3AE84` | the green behind the logo's calligraphy — 70% of the logo file's pixels |
| `--cream` | `#F3EEC6` | the ink of that same calligraphy |
| `--coffee` | `#4F3629` | quantised from their cup photograph |

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
