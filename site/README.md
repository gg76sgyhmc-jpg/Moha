# Elegance Bar Ladies Salon — website

A rebuild of the salon's web presence. Every service, price, duration, photo and
policy on the page comes from the salon's own live booking profile — nothing is
written for effect.

## Run it

`site/index.html` is a static page. Open it directly, or serve the folder:

```bash
python3 -m http.server -d site 8080     # http://localhost:8080
```

Deploy by uploading the `site/` folder to any static host (Netlify, Vercel,
Cloudflare Pages, GitHub Pages, or plain nginx). There is no build step at
serve time and no third-party requests — fonts and images are local.

## Files

| Path | What it is |
|------|-----------|
| `index.html` | The site. Generated — edit `template.html`, not this. |
| `standalone.html` | Same page with fonts and photos inlined; one file, works offline. |
| `template.html` | Layout, design tokens, and the page's CSS/JS. |
| `build.py` | Renders `template.html` + `data/` into the two HTML outputs. |
| `data/catalogue.json` | 78 services across 11 categories, as published by the salon. |
| `data/tenant.json` | Branch record: phone, CR, coordinates, socials, booking policies. |
| `assets/` | Optimised photos, logo, and webfonts. |
| `pull_catalogue.py` | Re-fetches the catalogue and photos (needs network). |
| `build_assets.py` | Re-encodes photos to WebP and lifts the logo's white to alpha. |
| `build_fonts.py` | Fetches the webfonts as local files (needs network). |

## Rebuild

```bash
python3 site/build.py            # after editing template.html or data/
python3 site/pull_catalogue.py   # refresh services + prices from the salon
python3 site/build_assets.py     # re-encode photos after a refresh
```

`build.py` asserts that every placeholder was filled, so a typo in a token name
fails the build rather than shipping `@LIKE_THIS@` to the page.

## Where the content came from

The salon's booking site is a Nuxt app that renders its catalogue client-side,
so the data is not in its HTML. Its server-side payload carries the branch id
(80) and the API it proxies; `pull_catalogue.py` uses that to read the same
endpoints the salon's own site calls:

- `GET /api/backend/get_categories` — the 11 categories
- `GET /api/backend/book/services/<slug>?category_id=<id>` — services per category

## Brand

Colours are the salon's own: `#13445C` is the primary configured on their
booking profile, and the taupe/sand tones are sampled from the line-art face in
their logo. Type is Almarai (Arabic display), Tajawal (text), and Cormorant
Garamond for Latin display, chosen to sit with the logo's script.

Their profile also carries `secondaryColor: #0F0` — pure green, which does not
appear anywhere in their branding and looks like a placeholder left at default.
It is not used here.

## Known gaps

These are absent from the source data, so the page does not state them:

- **Opening hours.** The branch record returns "لا توجد مواعيد عمل متاحة."
  The `14:00–17:00` in the config is the online booking window, not opening
  hours, so it is not presented as such.
- **Street address.** The address field repeats the salon name. The map link
  uses the branch coordinates instead.
- **WhatsApp.** Not configured in their socials, so no WhatsApp link is shown.
