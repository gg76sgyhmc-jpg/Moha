#!/usr/bin/env python3
"""Render the Elegance Bar site from the salon's own live data.

Every service name, price, duration, description and photo comes from
data/catalogue.json, and every business detail from data/tenant.json — both
pulled from the salon's booking profile by pull_catalogue.py. Nothing on the
page is written by hand except section headings and labels.

Outputs:
  site/index.html       the deployable site (links assets/ alongside it)
  site/standalone.html  the same page with fonts and photos inlined, for
                        preview links and offline viewing

    python3 site/build.py
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
BOOK_URL = "https://s-lon-h-n-l-n-k-lns-y.naeem.sa/services"
MAP_TMPL = "https://www.google.com/maps/search/?api=1&query={lat},{lng}"

SOCIAL_ICONS = {
    "instagram": '<path d="M12 2.2c3.2 0 3.6 0 4.8.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.42.4.68.8.9 1.4.17.4.37 1 .42 2.2.07 1.2.07 1.6.07 4.8s0 3.6-.07 4.8c-.05 1.2-.25 1.8-.42 2.2-.22.6-.48 1-.9 1.4-.4.42-.8.68-1.4.9-.4.17-1 .37-2.2.42-1.2.07-1.6.07-4.8.07s-3.6 0-4.8-.07c-1.2-.05-1.8-.25-2.2-.42-.6-.22-1-.48-1.4-.9-.42-.4-.68-.8-.9-1.4-.17-.4-.37-1-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.8c.05-1.2.25-1.8.42-2.2.22-.6.48-1 .9-1.4.4-.42.8-.68 1.4-.9.4-.17 1-.37 2.2-.42C8.4 2.2 8.8 2.2 12 2.2Zm0 5.8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm0 6.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2Zm5.1-6.75a.94.94 0 1 1-1.87 0 .94.94 0 0 1 1.87 0Z"/>',
    "snapchat": '<path d="M12 2.4c2.9 0 5 2.2 5 5.2 0 .8-.05 1.5-.1 2 .3.15.7.2 1.1.1.5-.15.9.1 1 .5.1.4-.1.8-.6 1-.5.2-1.3.4-1.5.9-.15.4.4 1.3 1 2 .6.7 1.4 1.3 2.3 1.6.4.15.5.5.4.8-.2.5-1 .8-2.1 1-.15.3-.2.7-.3 1-.1.3-.3.4-.6.35-.4-.05-1-.2-1.8-.05-.8.15-1.5.9-2.9.9s-2.1-.75-2.9-.9c-.8-.15-1.4 0-1.8.05-.3.05-.5-.05-.6-.35-.1-.3-.15-.7-.3-1-1.1-.2-1.9-.5-2.1-1-.1-.3 0-.65.4-.8.9-.3 1.7-.9 2.3-1.6.6-.7 1.15-1.6 1-2-.2-.5-1-.7-1.5-.9-.5-.2-.7-.6-.6-1 .1-.4.5-.65 1-.5.4.1.8.05 1.1-.1-.05-.5-.1-1.2-.1-2 0-3 2.1-5.2 5-5.2Z"/>',
    "tiktok": '<path d="M16.6 5.8a4.6 4.6 0 0 1-1.1-3H12.5v12.2a2.6 2.6 0 1 1-2.2-2.57V9.3a5.7 5.7 0 1 0 5.3 5.68V9.16a7.6 7.6 0 0 0 4.4 1.4V7.5a4.6 4.6 0 0 1-3.4-1.7Z"/>',
    "twitter": '<path d="M18.9 2.5h3.3l-7.2 8.2 8.4 11.1h-6.6l-5.2-6.8-5.9 6.8H2.4l7.7-8.8L2 2.5h6.8l4.7 6.2 5.4-6.2Zm-1.2 17.4h1.8L7.4 4.3H5.5l12.2 15.6Z"/>',
    "facebook": '<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.3v7A10 10 0 0 0 22 12Z"/>',
    "whatsapp": '<path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3.1.8.8-3-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1-.2.2-.6.8-.8 1-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.6-1.2.1-.2 0-.4 0-.5L9.4 8c-.2-.4-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.4-.3.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5 0 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.2-.3-.2-.5-.3Z"/>',
}
SOCIAL_LABEL = {"instagram": "إنستقرام", "snapchat": "سناب شات", "tiktok": "تيك توك",
                "twitter": "إكس", "facebook": "فيسبوك", "whatsapp": "واتساب"}

CLOCK = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>')
CHEV = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="m6 9 6 6 6-6"/></svg>')
DOT = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
       'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
       '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>')


def money(v) -> str:
    """Prices arrive as strings like '103.5' or '34'; trim a trailing .0 only."""
    f = float(v)
    return f"{f:.2f}".rstrip("0").rstrip(".")


def slugify(name: str) -> str:
    return re.sub(r"[^\w]+", "-", name, flags=re.U).strip("-")


def card_html(svc: dict, cat: dict, idx: int) -> str:
    name = svc["name"] or ""
    details = (svc.get("details") or "").strip()
    # The listing shows the first paragraph; the rest sits behind a toggle.
    head = details.split("\n\n")[0].strip() if details else ""
    photo = svc.get("image")
    stem = Path(photo).stem if photo else None

    media = (
        f'<img src="assets/services/{stem}.webp" alt="{escape(name)}" loading="lazy" '
        f'decoding="async" width="480" height="360">'
        if stem else
        '<div class="card__media--empty" style="height:100%">'
        '<svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.2" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
        '<path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg></div>'
    )
    dur = (f'<span class="card__dur">{CLOCK}{svc["duration"]} د</span>'
           if svc.get("duration") else "")

    more = ""
    if details and details != head:
        fid = f"d{svc['id']}"
        more = (
            f'<button class="card__more" aria-expanded="false" aria-controls="{fid}">'
            f'<span>تفاصيل الخدمة</span>{CHEV}</button>'
            f'<div class="card__full" id="{fid}">{escape(details)}</div>'
        )

    search = f'{name} {cat["name"]} {head}'
    return f'''      <article class="card rv" data-cat="{cat['slug']}" data-search="{escape(search)}">
        <div class="card__media">{media}{dur}</div>
        <div class="card__body">
          <p class="card__cat">{escape(cat['name'])}</p>
          <h3 class="card__name">{escape(name)}</h3>
          {f'<p class="card__desc">{escape(head)}</p>' if head else ''}
          {more}
          <div class="card__foot">
            <p class="card__price">{money(svc['price'])}<small>ر.س</small></p>
            <a class="btn btn--ghost" style="min-height:40px;padding:0 18px;font-size:14px"
               href="{BOOK_URL}" target="_blank" rel="noopener">احجزي</a>
          </div>
        </div>
      </article>'''


def main() -> None:
    catalogue = json.loads((HERE / "data" / "catalogue.json").read_text(encoding="utf-8"))
    tenant = json.loads((HERE / "data" / "tenant.json").read_text(encoding="utf-8"))
    t = tenant[1]["state"]["$stenant"]
    branch, cfg = t["branch"], t["config"]

    for c in catalogue:
        c["slug"] = slugify(c["name"])

    services = [s for c in catalogue for s in c["services"]]

    # ── chips ──
    chips = [f'<button class="chip" data-cat="all" aria-pressed="true">الكل'
             f'<span class="chip__n">{len(services)}</span></button>']
    for c in catalogue:
        chips.append(f'<button class="chip" data-cat="{c["slug"]}" aria-pressed="false">'
                     f'{escape(c["name"].strip())}'
                     f'<span class="chip__n">{len(c["services"])}</span></button>')

    # ── cards ──
    cards, i = [], 0
    for c in catalogue:
        for s in c["services"]:
            cards.append(card_html(s, c, i))
            i += 1

    # ── policies, split out of the salon's own instructions string ──
    raw = cfg.get("general_instructions", "")
    rules = [re.sub(r"^[-ـ\s]+", "", p).strip() for p in re.split(r"\s+[-ـ]\s*", raw) if p.strip()]
    rules = [r for r in rules if len(r) > 8]
    policies = "\n".join(
        f'      <div class="pol__item">{DOT}<p>{escape(r)}</p></div>' for r in rules
    )

    # ── socials, only the ones actually configured ──
    socials = "\n".join(
        f'          <a href="{escape(url)}" target="_blank" rel="noopener" '
        f'aria-label="{SOCIAL_LABEL.get(k, k)}">'
        f'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        f'{SOCIAL_ICONS[k]}</svg></a>'
        for k, url in (t.get("socials") or {}).items() if url and k in SOCIAL_ICONS
    )

    phone = branch.get("phone", "")
    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*@FONTS@*/", (HERE / "fonts.css").read_text(encoding="utf-8"))
    for key, val in {
        "@BOOKURL@": BOOK_URL,
        "@WELCOME@": escape(cfg.get("welcoming_msg", "").strip()),
        "@N_SERVICES@": str(len(services)),
        "@N_CATS@": str(len(catalogue)),
        "@N_DAYS@": str(cfg.get("AvailableDays", "")),
        "@CR@": escape(branch.get("cr", "")),
        "@PHONE@": escape(phone),
        "@PHONE_RAW@": re.sub(r"\D", "", phone),
        "@MAPURL@": MAP_TMPL.format(lat=branch["lat"], lng=branch["lng"]),
    }.items():
        html = html.replace(key, val)
    html = html.replace("<!--@CHIPS@-->", "\n".join("      " + c for c in chips).lstrip())
    html = html.replace("<!--@CARDS@-->", "\n".join(cards).lstrip())
    html = html.replace("<!--@POLICIES@-->", policies.lstrip())
    html = html.replace("<!--@SOCIALS@-->", socials.lstrip())

    leftover = re.findall(r"@[A-Z_]+@|<!--@[A-Z]+@-->", html)
    assert not leftover, f"unfilled placeholders: {set(leftover)}"

    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"index.html      {out.stat().st_size/1024:6.0f} KB  "
          f"({len(services)} services, {len(catalogue)} categories, {len(rules)} policies)",
          file=sys.stderr)

    # ── standalone: same page, every asset inlined ──
    def data_uri(path: Path) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"

    sa = html
    for rel in sorted(set(re.findall(r'(?:src=|url\()"?(assets/[\w./-]+)', sa)), key=len, reverse=True):
        f = HERE / rel
        if f.exists():
            sa = sa.replace(rel, data_uri(f))
    sa_path = HERE / "standalone.html"
    sa_path.write_text(sa, encoding="utf-8")
    print(f"standalone.html {sa_path.stat().st_size/1024/1024:6.1f} MB  (assets inlined)",
          file=sys.stderr)

    # ── preview.html: the same inlined page as body content only, for hosts
    #    that supply their own document skeleton. Those hosts own <html>, so
    #    RTL is asserted from the stylesheet and re-asserted on the root
    #    element at parse time.
    pv = re.sub(r"^.*?<title>", "<title>", sa, flags=re.S)
    pv = pv.replace("Elegance Bar Ladies Salon — إيليجانس بار صالون سيدات",
                    "Elegance Bar Ladies Salon", 1)
    pv = pv.replace("</head>\n", "", 1).replace("<body>", "", 1)
    pv = pv.replace("</body>\n</html>", "").rstrip() + "\n"
    pv = pv.replace("<style>", "<style>\n:root, body { direction: rtl; }\n", 1)
    pv = ('<script>document.documentElement.setAttribute("dir","rtl");'
          'document.documentElement.setAttribute("lang","ar");</script>\n' + pv)
    pv_path = HERE / "preview.html"
    pv_path.write_text(pv, encoding="utf-8")
    print(f"preview.html    {pv_path.stat().st_size/1024/1024:6.1f} MB  (body-only)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
