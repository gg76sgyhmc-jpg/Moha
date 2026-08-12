#!/usr/bin/env python3
"""Render the Raham Coffee page from the café's own data.

One document holds both views: the links list and the menu. Tapping المنيو
swaps the view on the URL hash rather than loading a second page, so the whole
thing is a single file to host or send.

Every item, price, description, calorie figure and photo comes from
data/menu.json; every link and business fact from data/brand.json. Both were
pulled from the café's public listings — nothing here is written to fill space.

    python3 raham/build.py
"""
from __future__ import annotations

import base64
import json
import mimetypes
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

ICONS = {
    "menu": '<path d="M4 5h16M4 12h16M4 19h10"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.2" fill="currentColor" stroke="none"/>',
    "tiktok": '<path d="M16.6 5.8a4.6 4.6 0 0 1-1.1-3H12.5v12.2a2.6 2.6 0 1 1-2.2-2.57"/><path d="M12.5 9.1a5.7 5.7 0 1 0 3.1 5.1V9.16a7.6 7.6 0 0 0 4.4 1.4V7.5"/>',
    "snapchat": '<path d="M12 3c2.6 0 4.5 2 4.5 4.7 0 .8-.05 1.5-.1 2 .4.2.9.2 1.3.05.5-.15.9.1 1 .5.1.4-.15.8-.65 1-.6.25-1.5.5-1.7 1-.2.5.5 1.5 1.1 2.2.6.7 1.5 1.3 2.4 1.6.4.15.5.5.35.8-.25.5-1.1.85-2.3 1.05-.15.35-.2.75-.3 1.05-.1.3-.35.4-.65.35-.45-.05-1.1-.2-1.95-.05-.85.15-1.6.95-3 .95s-2.15-.8-3-.95c-.85-.15-1.5 0-1.95.05-.3.05-.55-.05-.65-.35-.1-.3-.15-.7-.3-1.05-1.2-.2-2.05-.55-2.3-1.05-.15-.3-.05-.65.35-.8.9-.3 1.8-.9 2.4-1.6.6-.7 1.3-1.7 1.1-2.2-.2-.5-1.1-.75-1.7-1-.5-.2-.75-.6-.65-1 .1-.4.5-.65 1-.5.4.15.9.15 1.3-.05-.05-.5-.1-1.2-.1-2C7.5 5 9.4 3 12 3Z"/>',
    "delivery": '<path d="M14 17V6a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v11h13Z"/><path d="M14 9h3.5a1 1 0 0 1 .8.4l2.5 3.3a1 1 0 0 1 .2.6V17h-7V9Z"/><circle cx="6" cy="18.5" r="2"/><circle cx="17.5" cy="18.5" r="2"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "star": '<path d="m12 3 2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.2l5.9-.8L12 3Z"/>',
    "cup": '<path d="M4 8h12v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8Z"/><path d="M16 9h1.8a2.7 2.7 0 0 1 0 5.4H16"/><path d="M7 2.5v2M11 2.5v2"/>',
}


# RTL: "forward" points to the inline start, i.e. leftward on screen.
CHEVRON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="m15 18-6-6 6-6"/></svg>')


def icon(key: str, size: int = 20, fill: str = "none", sw: float = 1.7) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[key]}</svg>')


def money(v) -> str:
    """Prices arrive as '7.0' / '16.25'; keep the halalas only when they exist."""
    f = float(v)
    return f"{f:.2f}".rstrip("0").rstrip(".")


def slug(s: str) -> str:
    return re.sub(r"[^\w]+", "-", s, flags=re.U).strip("-")


# ── links view ────────────────────────────────────────────────────────────────
def links_parts(brand: dict, menu: list) -> tuple[str, str]:
    n_items = sum(len(c["items"]) for c in menu)
    meta = []
    r = brand.get("rating")
    if r:
        meta.append(f'<span class="pill">{icon("star", 14, fill="currentColor", sw=0)}'
                    f'<b>{escape(r["value"])}</b> · {r["count"]} تقييم</span>')
    meta.append(f'<span class="pill">{icon("cup", 14)}{n_items} صنف</span>')
    meta.append(f'<span class="pill">{icon("pin", 14)}{escape(brand["map_label_ar"])}</span>')

    rows = []
    for l in brand["links"]:
        ext = l["href"].startswith("http")
        rows.append(
            f'''    <a class="row rise{' row--featured' if l.get('featured') else ''}"
       href="{escape(l['href'])}"{' target="_blank" rel="noopener"' if ext else ''}
       style="animation-delay:{.28 + .05 * len(rows):.2f}s">
      <span class="row__ic">{icon(l['icon'], 21)}</span>
      <span class="row__txt">
        <span class="row__label">{escape(l['label_ar'])}</span>
        <span class="row__sub">{escape(l['sub_ar'])}</span>
      </span>
      <span class="row__go">{CHEVRON}</span>
    </a>''')

    return "\n      ".join(meta), "\n".join(rows).lstrip()


# ── menu view ─────────────────────────────────────────────────────────────────
def menu_parts(brand: dict, menu: list) -> tuple[str, str]:
    photos = {p.stem for p in (HERE / "assets" / "items").glob("*.webp")}

    jump, sections = [], []
    for cat in menu:
        sid = slug(cat["name"])
        jump.append(f'      <a href="#{sid}">{escape(cat["name"])}'
                    f'<span>{len(cat["items"])}</span></a>')

        cards = []
        for it in cat["items"]:
            key = str(it["id"])
            media = (
                f'<img src="assets/items/{key}.webp" alt="{escape(it["name"])}" '
                f'loading="lazy" decoding="async" width="88" height="88">'
                if key in photos else
                f'<div class="item__media--none" style="width:100%;height:100%">{icon("cup", 26)}</div>'
            )
            cal = (f'<span class="item__cal">{it["calories"]} سعرة</span>'
                   if it.get("calories") else "")
            desc = (f'<p class="item__desc">{escape(it["desc"])}</p>'
                    if it.get("desc") else "")
            cards.append(f'''        <article class="item rv">
          <div class="item__media">{media}</div>
          <div class="item__body">
            <h3 class="item__name">{escape(it['name'])}</h3>
            {desc}
            <div class="item__foot">
              <p class="item__price">{money(it['price'])}<small>ر.س</small></p>
              {cal}
            </div>
          </div>
        </article>''')

        sections.append(f'''    <section class="sec" id="{sid}">
      <div class="sec__head rv">
        <h2>{escape(cat['name'])}</h2>
        <span>{len(cat['items'])} صنف</span>
        <span class="sec__rule"></span>
      </div>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </section>''')

    return "\n".join(jump).lstrip(), "\n".join(sections).lstrip()


def inline_assets(html: str) -> str:
    """Fold assets into the document as data: URIs for the standalone copy."""
    for rel in sorted(set(re.findall(r'(?:src=|url\()"?(assets/[\w./-]+)', html)),
                      key=len, reverse=True):
        f = HERE / rel
        if f.exists():
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            html = html.replace(rel, f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}")
    return html


def main() -> None:
    brand = json.loads((HERE / "data" / "brand.json").read_text(encoding="utf-8"))
    menu = json.loads((HERE / "data" / "menu.json").read_text(encoding="utf-8"))

    if brand.get("phone"):
        # No phone was published on any reachable listing. Setting one in
        # brand.json is all it takes: the row and its tel: link appear here.
        brand["links"].insert(1, {
            "key": "phone", "href": "tel:" + re.sub(r"\D", "", brand["phone"]),
            "label_ar": "اتصل بنا", "sub_ar": brand["phone"], "icon": "phone",
        })

    meta, rows = links_parts(brand, menu)
    jump, sections = menu_parts(brand, menu)
    delivery = next((l["href"] for l in brand["links"] if l["key"] == "hungerstation"), "#")

    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*@FONTS@*/", (HERE / "fonts.css").read_text(encoding="utf-8"))
    html = html.replace("<!--@META@-->", meta)
    html = html.replace("<!--@LINKS@-->", rows)
    html = html.replace("<!--@JUMP@-->", jump)
    html = html.replace("<!--@SECTIONS@-->", sections)
    html = html.replace("@N_ITEMS@", str(sum(len(c["items"]) for c in menu)))
    html = html.replace("@DELIVERY@", delivery)

    left = re.findall(r"@[A-Z_]+@|<!--@[A-Z]+@-->", html)
    assert not left, f"unfilled placeholders: {set(left)}"

    # Hosted copy: assets stay separate files so the browser can cache them.
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html          {(HERE / 'index.html').stat().st_size/1024:6.0f} KB"
          f"  (+ assets/)", file=sys.stderr)

    # The single file: fonts and every photo folded in, nothing else needed.
    one = HERE / "raham-one-file.html"
    one.write_text(inline_assets(html), encoding="utf-8")
    print(f"raham-one-file.html {one.stat().st_size/1024/1024:6.1f} MB  (self-contained)",
          file=sys.stderr)

    # Body-only copy, for hosts that supply their own document skeleton and so
    # cannot use the <html dir="rtl"> this page reads right-to-left from.
    pv = re.sub(r"^.*?<title>", "<title>", one.read_text(encoding="utf-8"), flags=re.S)
    pv = pv.replace("</head>\n", "", 1).replace("<body>", "", 1)
    pv = pv.replace("</body>\n</html>", "").rstrip() + "\n"
    pv = pv.replace("<style>", "<style>\n:root, body { direction: rtl; }\n", 1)
    pv = ('<script>document.documentElement.setAttribute("dir","rtl");'
          'document.documentElement.setAttribute("lang","ar");</script>\n' + pv)
    (HERE / "preview.html").write_text(pv, encoding="utf-8")
    print(f"preview.html        {(HERE / 'preview.html').stat().st_size/1024/1024:6.1f} MB  (body-only)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
