#!/usr/bin/env python3
"""Builds the Qasdir links + menu page with every asset inlined (artifact CSP blocks external hosts)."""
import base64, os, pathlib

HERE = pathlib.Path(__file__).parent
OUT  = HERE / "qasdir.html"

def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode((HERE / path).read_bytes()).decode()

def img(name):
    return b64(f"assets/{name}", "image/webp")

def png(name):
    return b64(f"assets/{name}", "image/png")

def font(name):
    return b64(f"fonts/{name}", "font/woff2")

# ---------------------------------------------------------------- fonts
FACES = []
for w in (500, 700):
    FACES.append(f"""@font-face{{font-family:'Rubik Ar';font-style:normal;font-weight:{w};font-display:swap;
src:url({font(f'Rubik-{w}-arabic.sub.woff2')}) format('woff2');
unicode-range:U+0600-06FF,U+0750-077F,U+08A0-08FF,U+FB50-FDFF,U+FE70-FEFF,U+200C-200F;}}""")
for w in (400, 500, 600):
    FACES.append(f"""@font-face{{font-family:'Plex Ar';font-style:normal;font-weight:{w};font-display:swap;
src:url({font(f'IBMPlexSansArabic-{w}-arabic.sub.woff2')}) format('woff2');
unicode-range:U+0600-06FF,U+0750-077F,U+08A0-08FF,U+FB50-FDFF,U+FE70-FEFF,U+200C-200F;}}
@font-face{{font-family:'Plex Ar';font-style:normal;font-weight:{w};font-display:swap;
src:url({font(f'IBMPlexSansArabic-{w}-latin.sub.woff2')}) format('woff2');
unicode-range:U+0000-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026;}}""")
FONT_CSS = "\n".join(FACES)

# ---------------------------------------------------------------- data
BRANCHES = [
    dict(city="الخبر", area="حي الشراع · طريق الملك فيصل بن عبدالعزيز",
         tel="+966566334077", show="٠٥٦ ٦٣٣ ٤٠٧٧", rate="٤٫٧", close="٤:٠٠ ص",
         map="https://www.google.com/maps/place/?q=place_id:ChIJheyT7xPbST4RHHJjvQN6ZZA",
         order="https://hungerstation.com/sa-ar/restaurant/al-khobar/al-khubar-ash-shamaliyah/122465"),
    dict(city="الرياض", area="حي قرطبة · شارع دباس بن راشد",
         tel="+966530106623", show="٠٥٣ ٠١٠ ٦٦٢٣", rate="٤٫٤", close="٢:٠٠ ص",
         map="https://www.google.com/maps/search/?api=1&query=24.8265519,46.7336606", order=None),
    dict(city="الجبيل", area="حي الفناتير · الشاطئ",
         tel="+966536783808", show="٠٥٣ ٦٧٨ ٣٨٠٨", rate="٤٫٣", close="٤:٠٠ ص",
         map="https://www.google.com/maps/search/?api=1&query=27.1332829,49.5683016", order=None),
    dict(city="الهفوف", area="جنوب الهفوف · المنذر بن أبي سيرة",
         tel="+966543220664", show="٠٥٤ ٣٢٢ ٠٦٦٤", rate="٤٫٢", close="٤:٠٠ ص",
         map="https://www.google.com/maps/search/?api=1&query=25.3097767,49.5558992",
         order="https://hungerstation.com/sa-ar/restaurant/%D8%A7%D9%84%D9%87%D9%81%D9%88%D9%81/%D8%AC%D9%86%D9%88%D8%A8-%D8%A7%D9%84%D9%87%D9%81%D9%88%D9%81/103013"),
]

MENU = [
    ("الصمونات", "صمونة", [
        ("صمونة كباب لحم",   "٢٢٣", "٩",  "kabab_lahm.webp",   "طحينة حمراء أو بيضاء"),
        ("صمونة شيش طاووق",  "٢١٩", "٩",  "shish_tawook.webp", None),
        ("صمونة كباب دجاج",  "٢٢٠", "٩",  "kabab_dajaj.webp",  None),
    ]),
    ("البوكسات", "بوكس", [
        ("فروجة قصدير",  "٩٢٠",  "٢٥", "frooja.webp", "نصف دجاجة بالخلطة السرية"),
        ("بوكس الجمعات", "٢٥٠٠", "٦٩", None,          None),
    ]),
    ("المقبلات", "مقبلات", [
        ("بطاطس قصدير", "٣٠٠", "٦",      "batates.webp", None),
        ("أجنحة قصدير", "٢٢٠", "٨ / ٢٢", "wings.webp",   "٦ قطع أو ١٨ قطعة"),
        ("حمص",         "٣٤٠", "٥",      "hummus.webp",  None),
    ]),
    ("الصوصات", "صوص", [
        ("صوص ثوم",   "٧٠", "٢", "sauce_thoom.webp", None),
        ("صوص قصدير", "٦٠", "٢", "sauce.webp",       None),
    ]),
    ("المشروبات", "مشروب", [
        ("فيمتو قصدير",    "١٣٠", "٣", None, None),
        ("مشروبات غازية",  "١٥٠", "٣", None, None),
        ("ماء",            None,  "١", None, None),
    ]),
]

ICON = {
"instagram":'<rect x="2" y="2" width="20" height="20" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r="1.2" fill="currentColor" stroke="none"/>',
"tiktok":'<path d="M15.2 3.2v10.9a4.1 4.1 0 1 1-3.4-4.03"/><path d="M15.2 3.2c.4 2.3 1.9 3.9 4.3 4.2"/>',
"menu":'<path d="M4 6.5h16M4 12h16M4 17.5h11"/>',
"phone":'<path d="M6.3 3.7h3l1.5 3.7-2 1.3a11.5 11.5 0 0 0 5.4 5.4l1.3-2 3.7 1.5v3a2 2 0 0 1-2.2 2A16.8 16.8 0 0 1 4.3 5.9a2 2 0 0 1 2-2.2Z"/>',
"pin":'<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
"bag":'<path d="M5.5 8h13l-1 12H6.5l-1-12Z"/><path d="M9 8V6.2a3 3 0 0 1 6 0V8"/>',
"star":'<path d="m12 3.6 2.5 5.2 5.7.8-4.1 4 1 5.7-5.1-2.7-5.1 2.7 1-5.7-4.1-4 5.7-.8Z"/>',
"clock":'<circle cx="12" cy="12" r="8.6"/><path d="M12 7.2V12l3.1 1.9"/>',
"arrow":'<path d="M14.5 6 8.5 12l6 6"/>',
"back":'<path d="M9.5 6l6 6-6 6"/>',
}
def svg(k, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>')

# ---------------------------------------------------------------- markup
def branch_card(b, i):
    order = (f'<a class="bx-act" href="{b["order"]}" target="_blank" rel="noopener">'
             f'{svg("bag","ic sm")}<span>توصيل</span></a>') if b["order"] else ""
    return f"""<article class="bx reveal" style="--d:{i*55}ms">
  <div class="bx-head">
    <h3 class="bx-city">{b['city']}</h3>
    <span class="bx-rate">{svg('star','ic xs')}<b>{b['rate']}</b></span>
  </div>
  <p class="bx-area">{b['area']}</p>
  <p class="bx-hrs">{svg('clock','ic xs')}<span>يسكّر <b>{b['close']}</b></span></p>
  <div class="bx-acts">
    <a class="bx-act" href="tel:{b['tel']}">{svg('phone','ic sm')}<span dir="ltr">{b['show']}</span></a>
    <a class="bx-act" href="{b['map']}" target="_blank" rel="noopener">{svg('pin','ic sm')}<span>الموقع</span></a>
    {order}
  </div>
</article>"""

def menu_item(name, cal, price, pic, note, idx):
    if pic:
        media = f'<img class="it-img" src="{img(pic)}" alt="{name}" loading="lazy" decoding="async">'
    else:
        media = '<span class="it-img it-blank" aria-hidden="true"></span>'
    meta = " · ".join(x for x in ((f"{cal} سعرة" if cal else None), note) if x)
    cals = f'<span class="it-cal">{meta}</span>' if meta else ""
    return f"""<li class="it reveal" style="--d:{idx*40}ms">
  {media}
  <span class="it-body"><span class="it-name">{name}</span>{cals}</span>
  <span class="it-price"><b dir="ltr">{price}</b><span>ريال</span></span>
</li>"""

sections, chips = [], []
for si, (title, kicker, items) in enumerate(MENU):
    sid = f"sec{si}"
    chips.append(f'<a class="chip" href="#{sid}">{title}</a>')
    lis = "\n".join(menu_item(*it, i) for i, it in enumerate(items))
    sections.append(f"""<section class="sec" id="{sid}">
  <header class="sec-h"><span class="sec-k">{kicker}</span><h2 class="sec-t">{title}</h2><span class="rule"></span></header>
  <ul class="items">{lis}</ul>
</section>""")

HTML = f"""<title>قصدير QASDIR</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
{FONT_CSS}

:root{{
  --ground:#E7E9EA; --surface:#FFFFFF; --surface-2:#F1F3F4;
  --ink:#0D0E0F; --ink-2:#51565A; --ink-3:#82888D;
  --onyx:#0D0E0F; --on-onyx:#F4F6F7;
  --steel:#4B5257;
  --foil-a:#9CA3A8; --foil-b:#FCFDFD; --foil-c:#7E868C;
  --line:rgba(13,14,15,.12); --line-2:rgba(13,14,15,.06);
  --shadow:0 1px 2px rgba(13,14,15,.05), 0 10px 26px -14px rgba(13,14,15,.30);
  --shadow-lift:0 2px 4px rgba(13,14,15,.07), 0 20px 40px -18px rgba(13,14,15,.38);
  --metal:linear-gradient(135deg,#8B9399 0%,#F3F6F7 26%,#AEB6BB 48%,#FAFCFC 66%,#969EA4 100%);
  --on-metal:#0C0D0E;
  --logo:url({png('logo_dark.png')});
  --r:16px; --r-lg:22px;
  --step:clamp(1rem,.86rem + .6vw,1.14rem);
}}
@media (prefers-color-scheme:dark){{
  :root:not([data-theme="light"]){{
    --ground:#0B0C0D; --surface:#161819; --surface-2:#1E2123;
    --ink:#EFF1F2; --ink-2:#A0A6AB; --ink-3:#767C81;
    --onyx:#E3E7E9; --on-onyx:#0D0E0F;
    --steel:#C3CACF;
    --foil-a:#5A6166; --foil-b:#C2C9CE; --foil-c:#41474B;
    --line:rgba(239,241,242,.14); --line-2:rgba(239,241,242,.07);
    --shadow:0 1px 2px rgba(0,0,0,.5), 0 12px 30px -16px rgba(0,0,0,.8);
    --shadow-lift:0 2px 6px rgba(0,0,0,.55), 0 24px 48px -20px rgba(0,0,0,.9);
    --logo:url({png('logo_cream.png')});
  }}
}}
:root[data-theme="dark"]{{
  --ground:#0B0C0D; --surface:#161819; --surface-2:#1E2123;
  --ink:#EFF1F2; --ink-2:#A0A6AB; --ink-3:#767C81;
  --onyx:#E3E7E9; --on-onyx:#0D0E0F;
  --steel:#C3CACF;
  --foil-a:#5A6166; --foil-b:#C2C9CE; --foil-c:#41474B;
  --line:rgba(239,241,242,.14); --line-2:rgba(239,241,242,.07);
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 12px 30px -16px rgba(0,0,0,.8);
  --shadow-lift:0 2px 6px rgba(0,0,0,.55), 0 24px 48px -20px rgba(0,0,0,.9);
  --logo:url({png('logo_cream.png')});
}}

*,*::before,*::after{{box-sizing:border-box}}
body{{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:'Plex Ar',system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:var(--step); line-height:1.65; direction:rtl;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}}
/* the white square tile of the shop wall, at 4% */
body::before{{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.5;
  background:
    linear-gradient(var(--line-2) 1px,transparent 1px) 0 0/56px 56px,
    linear-gradient(90deg,var(--line-2) 1px,transparent 1px) 0 0/56px 56px;
  -webkit-mask-image:radial-gradient(120% 70% at 50% 0%,#000 15%,transparent 78%);
          mask-image:radial-gradient(120% 70% at 50% 0%,#000 15%,transparent 78%);
}}
h1,h2,h3{{margin:0; font-family:'Rubik Ar','Plex Ar',system-ui,sans-serif; font-weight:700; text-wrap:balance; letter-spacing:-.01em}}
p{{margin:0}}
a{{color:inherit; text-decoration:none}}
img{{max-width:100%; display:block}}
ul{{margin:0; padding:0; list-style:none}}
:focus-visible{{outline:2.5px solid var(--steel); outline-offset:3px; border-radius:6px}}
.ic{{width:20px;height:20px;flex:none}} .ic.sm{{width:17px;height:17px}} .ic.xs{{width:14px;height:14px}}

.wrap{{position:relative; z-index:1; width:min(100% - 28px,540px); margin-inline:auto; padding-block:22px 56px}}

/* ---------- hero ---------- */
.hero{{position:relative; border-radius:var(--r-lg); overflow:hidden; background:var(--surface); box-shadow:var(--shadow)}}
.hero-shot{{position:relative; aspect-ratio:16/10; overflow:hidden; background:#0D0B0A}}
.hero-shot img{{width:100%;height:100%;object-fit:cover; transform:scale(1.06); animation:driftIn 1.6s cubic-bezier(.22,1,.36,1) both}}
.hero-shot::after{{content:""; position:absolute; inset:0;
  background:linear-gradient(to top,rgba(10,8,7,.96) 2%,rgba(10,8,7,.74) 34%,rgba(10,8,7,.34) 68%,rgba(10,8,7,.18) 100%)}}
.hero-glow{{position:absolute; inset:-30% -10% auto -10%; height:70%; pointer-events:none;
  background:radial-gradient(60% 60% at 50% 40%,rgba(226,186,128,.30),transparent 70%);
  animation:breathe 9s ease-in-out infinite}}
.lockup{{position:absolute; inset-inline:0; bottom:0; padding:0 22px 20px; z-index:2; text-align:center}}
.mark{{width:min(64%,226px); aspect-ratio:900/546; margin-inline:auto;
  -webkit-mask:var(--logo) no-repeat center/contain; mask:var(--logo) no-repeat center/contain;
  background:linear-gradient(100deg,#B9C0C5 16%,#FDFEFE 33%,#8C949A 50%,#FDFEFE 67%,#B9C0C5 84%);
  background-size:280% 100%; animation:foil 7s cubic-bezier(.5,0,.5,1) 1.1s infinite}}
.tag{{margin-top:9px; font-family:'Rubik Ar',sans-serif; font-weight:500; font-size:.95rem;
  color:#DDE2E5; letter-spacing:.01em; text-shadow:0 1px 12px rgba(0,0,0,.6)}}
.facts{{display:flex; flex-wrap:wrap; gap:8px; justify-content:center; padding:14px 16px 16px; background:var(--surface)}}
.fact{{display:inline-flex; align-items:center; gap:6px; padding:6px 11px; border-radius:999px;
  background:var(--surface-2); border:1px solid var(--line-2); font-size:.8rem; color:var(--ink-2); font-weight:500}}
.fact b{{color:var(--ink); font-variant-numeric:tabular-nums}}
.fact .ic{{color:var(--steel)}}

/* ---------- tabs ---------- */
.tabs{{position:sticky; top:10px; z-index:20; margin:18px 0 20px; padding:5px;
  display:grid; grid-template-columns:1fr 1fr; gap:4px; border-radius:999px;
  background:color-mix(in srgb,var(--surface) 82%,transparent);
  border:1px solid var(--line); box-shadow:var(--shadow); backdrop-filter:blur(14px) saturate(1.3)}}
.tabs{{overflow:hidden}}
.tabs::before{{content:""; position:absolute; z-index:0; top:5px; bottom:5px; inset-inline-start:5px; width:calc(50% - 7px);
  border-radius:999px; background:var(--onyx); transition:transform .42s cubic-bezier(.22,1,.36,1)}}
.tabs[data-at="menu"]::before{{transform:translateX(calc(-100% - 4px))}}
.tab{{position:relative; z-index:1; display:flex; align-items:center; justify-content:center; gap:8px;
  min-height:44px; border:0; background:none; cursor:pointer; border-radius:999px;
  font-family:'Rubik Ar',sans-serif; font-size:.95rem; font-weight:500; color:var(--ink-2);
  transition:color .3s ease}}
.tab[aria-selected="true"]{{color:var(--on-onyx)}}

/* ---------- views ---------- */
.view[hidden]{{display:none}}
.view{{animation:viewIn .46s cubic-bezier(.22,1,.36,1) both}}
.stack{{display:flex; flex-direction:column; gap:11px}}

/* ---------- link rows ---------- */
.row{{display:flex; align-items:center; gap:13px; padding:15px 17px; min-height:62px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r);
  box-shadow:var(--shadow); cursor:pointer; text-align:start;
  transition:transform .26s cubic-bezier(.22,1,.36,1), box-shadow .26s ease, border-color .26s ease}}
.row:hover{{transform:translateY(-2px); box-shadow:var(--shadow-lift); border-color:color-mix(in srgb,var(--steel) 34%,var(--line))}}
.row:active{{transform:translateY(0) scale(.988)}}
.row-ic{{display:grid; place-items:center; width:40px; height:40px; flex:none; border-radius:12px;
  background:var(--surface-2); color:var(--steel); border:1px solid var(--line-2)}}
.row-b{{flex:1; min-width:0}}
.row-t{{display:block; font-family:'Rubik Ar',sans-serif; font-weight:500; font-size:1rem; line-height:1.35}}
.row-s{{display:block; font-size:.8rem; color:var(--ink-3); margin-top:1px}}
.row-go{{color:var(--ink-3); transition:transform .26s cubic-bezier(.22,1,.36,1)}}
.row:hover .row-go{{transform:translateX(-4px); color:var(--steel)}}

.row.hero-row{{background:var(--metal); border-color:transparent; padding:17px}}
.hero-row .row-t,.hero-row .row-go{{color:var(--on-metal)}}
.hero-row .row-s{{color:color-mix(in srgb,var(--on-metal) 68%,transparent)}}
.hero-row .row-ic{{background:color-mix(in srgb,var(--on-metal) 12%,transparent); color:var(--on-metal); border-color:color-mix(in srgb,var(--on-metal) 14%,transparent)}}
.hero-row:hover{{border-color:transparent}}

/* ---------- group label ---------- */
.glabel{{display:flex; align-items:center; gap:11px; margin:26px 0 13px}}
.glabel span{{font-size:.74rem; font-weight:600; letter-spacing:.13em; color:var(--ink-3)}}
.rule{{flex:1; height:1px; background:linear-gradient(to left,var(--foil-a),var(--foil-b),transparent)}}

/* ---------- branch cards ---------- */
.bx{{padding:16px 17px; background:var(--surface); border:1px solid var(--line);
  border-radius:var(--r); box-shadow:var(--shadow);
  transition:transform .26s cubic-bezier(.22,1,.36,1), box-shadow .26s ease}}
.bx:hover{{transform:translateY(-2px); box-shadow:var(--shadow-lift)}}
.bx-head{{display:flex; align-items:center; justify-content:space-between; gap:10px}}
.bx-city{{font-size:1.12rem}}
.bx-rate{{display:inline-flex; align-items:center; gap:4px; font-size:.8rem; color:var(--steel); font-weight:600; font-variant-numeric:tabular-nums}}
.bx-area{{margin-top:3px; font-size:.85rem; color:var(--ink-2); line-height:1.5}}
.bx-hrs{{display:flex; align-items:center; gap:6px; margin-top:7px; font-size:.8rem; color:var(--ink-3)}}
.bx-hrs b{{color:var(--ink-2); font-variant-numeric:tabular-nums}}
.bx-acts{{display:flex; flex-wrap:wrap; gap:8px; margin-top:13px}}
.bx-act{{display:inline-flex; align-items:center; gap:7px; min-height:40px; padding:0 13px; border-radius:11px;
  background:var(--surface-2); border:1px solid var(--line-2); font-size:.85rem; font-weight:500; color:var(--ink);
  transition:background .22s ease, border-color .22s ease, transform .22s ease}}
.bx-act .ic{{color:var(--steel)}}
.bx-act:hover{{background:color-mix(in srgb,var(--steel) 12%,var(--surface-2)); border-color:color-mix(in srgb,var(--steel) 32%,transparent); transform:translateY(-1px)}}

/* ---------- menu ---------- */
.mhead{{text-align:center; padding:8px 0 4px}}
.mhead h2{{font-size:1.55rem}}
.mhead p{{margin-top:5px; font-size:.87rem; color:var(--ink-2)}}
.chips{{position:sticky; top:74px; z-index:15; display:flex; gap:7px; margin:16px -14px 6px; padding:9px 14px;
  overflow-x:auto; scrollbar-width:none; -webkit-overflow-scrolling:touch;
  background:linear-gradient(to bottom,var(--ground) 62%,transparent)}}
.chips::-webkit-scrollbar{{display:none}}
.chip{{flex:none; padding:8px 14px; min-height:38px; display:inline-flex; align-items:center; border-radius:999px;
  background:var(--surface); border:1px solid var(--line); font-size:.83rem; font-weight:500; color:var(--ink-2);
  transition:background .24s ease,color .24s ease,border-color .24s ease}}
.chip.on{{background:var(--onyx); color:var(--on-onyx); border-color:transparent}}
.sec{{margin-top:26px; scroll-margin-top:126px}}
.sec-h{{display:flex; align-items:baseline; gap:11px; margin-bottom:12px}}
.sec-k{{font-size:.68rem; font-weight:600; letter-spacing:.14em; color:var(--steel)}}
.sec-t{{font-size:1.18rem}}
.items{{display:flex; flex-direction:column; gap:9px}}
.it{{display:flex; align-items:center; gap:13px; padding:11px 13px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r); box-shadow:var(--shadow);
  transition:transform .26s cubic-bezier(.22,1,.36,1), box-shadow .26s ease}}
.it:hover{{transform:translateY(-2px); box-shadow:var(--shadow-lift)}}
.it-img{{width:62px; height:62px; flex:none; border-radius:12px; object-fit:cover; background:var(--surface-2)}}
.it-blank{{display:block; border:1px solid var(--line-2);
  background:
    var(--logo) no-repeat center/62% ,
    var(--metal);
  opacity:.5}}
.it-body{{flex:1; min-width:0}}
.it-name{{display:block; font-family:'Rubik Ar',sans-serif; font-weight:500; font-size:.99rem; line-height:1.35}}
.it-cal{{display:block; font-size:.74rem; color:var(--ink-3); margin-top:2px; font-variant-numeric:tabular-nums}}
.it-price{{display:flex; align-items:baseline; gap:4px; flex:none; color:var(--steel); font-variant-numeric:tabular-nums}}
.it-price b{{font-family:'Rubik Ar',sans-serif; font-size:1.16rem; font-weight:700; letter-spacing:-.02em}}
.it-price span{{font-size:.72rem; color:var(--ink-3); font-weight:500}}

.note{{margin-top:24px; padding:14px 16px; border-radius:var(--r); background:var(--surface-2);
  border:1px dashed var(--line); font-size:.8rem; color:var(--ink-2); line-height:1.7}}

/* ---------- footer ---------- */
.foot{{margin-top:34px; text-align:center}}
.foot-mark{{width:96px; aspect-ratio:900/546; margin-inline:auto; opacity:.3;
  -webkit-mask:var(--logo) no-repeat center/contain; mask:var(--logo) no-repeat center/contain; background:var(--ink)}}
.foot p{{margin-top:10px; font-size:.76rem; color:var(--ink-3)}}
.foot a{{color:var(--steel)}}

/* ---------- motion ---------- */
@keyframes viewIn{{from{{opacity:0; transform:translateY(9px)}} to{{opacity:1; transform:none}}}}
@keyframes riseIn{{from{{opacity:0; transform:translateY(15px)}} to{{opacity:1; transform:none}}}}
@keyframes driftIn{{from{{transform:scale(1.16)}} to{{transform:scale(1.06)}}}}
@keyframes breathe{{0%,100%{{opacity:.55}} 50%{{opacity:1}}}}
@keyframes foil{{0%,58%{{background-position:180% 0}} 100%{{background-position:-80% 0}}}}
.js .reveal{{opacity:0}}
.js .reveal.in{{animation:riseIn .52s cubic-bezier(.22,1,.36,1) var(--d,0ms) both}}

@media (prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation-duration:.001ms !important; animation-iteration-count:1 !important; transition-duration:.001ms !important}}
  .js .reveal{{opacity:1}}
  .hero-shot img{{transform:scale(1.02)}}
  .mark{{background:var(--foil-b)}}
}}
@media (min-width:600px){{ :root{{--step:1.05rem}} .hero-shot{{aspect-ratio:16/9}} }}
</style>
<script>document.documentElement.classList.add('js');</script>

<div class="wrap" dir="rtl" lang="ar">

  <header class="hero">
    <div class="hero-shot">
      <img src="{img('storefront.webp')}" alt="واجهة مطعم قصدير ليلاً واللوقو مضيء" fetchpriority="high" decoding="async">
      <span class="hero-glow" aria-hidden="true"></span>
      <div class="lockup">
        <h1 class="mark" role="img" aria-label="قصدير"></h1>
        <p class="tag">ترى وحدة ما تكفي!</p>
      </div>
    </div>
    <div class="facts">
      <span class="fact">{svg('star','ic xs')}<b>٤٫٧</b> قوقل</span>
      <span class="fact">{svg('clock','ic xs')}لين <b>٤:٠٠ ص</b></span>
      <span class="fact">{svg('pin','ic xs')}<b>٤</b> فروع</span>
    </div>
  </header>

  <nav class="tabs" id="tabs" data-at="links" role="tablist" aria-label="أقسام الصفحة">
    <button class="tab" id="t-links" role="tab" aria-selected="true"  aria-controls="v-links" type="button">{svg('pin','ic sm')}الروابط</button>
    <button class="tab" id="t-menu"  role="tab" aria-selected="false" aria-controls="v-menu"  type="button">{svg('menu','ic sm')}المنيو</button>
  </nav>

  <!-- ============ LINKS ============ -->
  <div class="view" id="v-links" role="tabpanel" aria-labelledby="t-links">
    <div class="stack">
      <button class="row hero-row reveal" style="--d:0ms" type="button" data-go="menu">
        <span class="row-ic">{svg('menu')}</span>
        <span class="row-b"><span class="row-t">المنيو والأسعار</span><span class="row-s">صمونات · بوكسات · مقبلات · مشروبات</span></span>
        {svg('arrow','ic row-go')}
      </button>

      <a class="row reveal" style="--d:60ms" href="https://www.instagram.com/qasdir.sa/" target="_blank" rel="noopener">
        <span class="row-ic">{svg('instagram')}</span>
        <span class="row-b"><span class="row-t">انستقرام</span><span class="row-s" dir="ltr">@qasdir.sa</span></span>
        {svg('arrow','ic row-go')}
      </a>

      <a class="row reveal" style="--d:110ms" href="https://www.tiktok.com/@qasdirsa" target="_blank" rel="noopener">
        <span class="row-ic">{svg('tiktok')}</span>
        <span class="row-b"><span class="row-t">تيك توك</span><span class="row-s" dir="ltr">@qasdirsa</span></span>
        {svg('arrow','ic row-go')}
      </a>

      <a class="row reveal" style="--d:160ms" href="https://hungerstation.com/sa-ar/restaurant/al-khobar/al-khubar-ash-shamaliyah/122465" target="_blank" rel="noopener">
        <span class="row-ic">{svg('bag')}</span>
        <span class="row-b"><span class="row-t">اطلب توصيل</span><span class="row-s">هنقرستيشن</span></span>
        {svg('arrow','ic row-go')}
      </a>
    </div>

    <div class="glabel"><span>الفروع</span><span class="rule"></span></div>
    <div class="stack">
      {chr(10).join(branch_card(b,i) for i,b in enumerate(BRANCHES))}
    </div>

    <div class="glabel"><span>قصدير خارج السعودية</span><span class="rule"></span></div>
    <div class="stack">
      <a class="row reveal" style="--d:0ms" href="https://www.instagram.com/qasdeer.kw/" target="_blank" rel="noopener">
        <span class="row-ic">{svg('instagram')}</span>
        <span class="row-b"><span class="row-t">قصدير الكويت</span><span class="row-s" dir="ltr">@qasdeer.kw</span></span>
        {svg('arrow','ic row-go')}
      </a>
    </div>
  </div>

  <!-- ============ MENU ============ -->
  <div class="view" id="v-menu" role="tabpanel" aria-labelledby="t-menu" hidden>
    <div class="mhead">
      <h2>منيو قصدير</h2>
      <p>الأسعار بالريال السعودي وشاملة الضريبة</p>
    </div>
    <div class="chips" id="chips">{"".join(chips)}</div>
    {chr(10).join(sections)}
    <p class="note">الأسعار منقولة من منيو الفرع نفسه — لا من تطبيقات التوصيل، لأن أسعارها أعلى. الصور من صور المطعم الرسمية، والأطباق اللي ما لها صورة معروضة بختم قصدير.</p>
  </div>

  <footer class="foot">
    <div class="foot-mark" role="img" aria-label="قصدير"></div>
    <p><a href="https://www.instagram.com/qasdir.sa/" target="_blank" rel="noopener"><span dir="ltr">@qasdir.sa</span></a> · ترى وحدة ما تكفي!</p>
  </footer>
</div>

<script>
(function(){{
  var tabs=document.getElementById('tabs'),
      tL=document.getElementById('t-links'), tM=document.getElementById('t-menu'),
      vL=document.getElementById('v-links'),  vM=document.getElementById('v-menu'),
      reduce=matchMedia('(prefers-reduced-motion: reduce)');

  function reveal(scope){{
    var els=scope.querySelectorAll('.reveal');
    if(reduce.matches){{ els.forEach(function(e){{e.classList.add('in')}}); return; }}
    els.forEach(function(e){{ e.classList.remove('in'); }});
    var io=new IntersectionObserver(function(es){{
      es.forEach(function(en){{ if(en.isIntersecting){{ en.target.classList.add('in'); io.unobserve(en.target); }} }});
    }},{{rootMargin:'0px 0px -8% 0px', threshold:.06}});
    els.forEach(function(e){{ io.observe(e); }});
  }}

  function show(which,push){{
    var toMenu = which==='menu';
    tabs.dataset.at = toMenu ? 'menu' : 'links';
    tM.setAttribute('aria-selected', toMenu);  tL.setAttribute('aria-selected', !toMenu);
    vM.hidden=!toMenu; vL.hidden=toMenu;
    reveal(toMenu?vM:vL);
    if(push){{
      history.replaceState(null,'', toMenu?'#menu':'#links');
      window.scrollTo({{top:0, behavior: reduce.matches?'auto':'smooth'}});
    }}
  }}

  tL.addEventListener('click',function(){{show('links',true)}});
  tM.addEventListener('click',function(){{show('menu',true)}});
  document.querySelectorAll('[data-go="menu"]').forEach(function(b){{
    b.addEventListener('click',function(){{show('menu',true)}});
  }});

  // keyboard: arrows move between tabs
  tabs.addEventListener('keydown',function(e){{
    if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight') return;
    var next = (tabs.dataset.at==='links') ? tM : tL;
    next.focus(); show(next===tM?'menu':'links',true); e.preventDefault();
  }});

  // menu category chips: smooth scroll + scroll-spy
  var chips=[].slice.call(document.querySelectorAll('.chip')),
      secs=chips.map(function(c){{return document.querySelector(c.getAttribute('href'))}});
  chips.forEach(function(c,i){{
    c.addEventListener('click',function(e){{
      e.preventDefault();
      secs[i].scrollIntoView({{behavior:reduce.matches?'auto':'smooth', block:'start'}});
    }});
  }});
  if('IntersectionObserver' in window){{
    var spy=new IntersectionObserver(function(es){{
      es.forEach(function(en){{
        if(!en.isIntersecting) return;
        var i=secs.indexOf(en.target); if(i<0) return;
        chips.forEach(function(c,j){{ c.classList.toggle('on', j===i); }});
        chips[i].scrollIntoView({{behavior:reduce.matches?'auto':'smooth', block:'nearest', inline:'center'}});
      }});
    }},{{rootMargin:'-124px 0px -62% 0px', threshold:0}});
    secs.forEach(function(s){{ if(s) spy.observe(s); }});
  }}
  if(chips[0]) chips[0].classList.add('on');

  show(location.hash==='#menu'?'menu':'links',false);
}})();
</script>
"""

OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT, round(OUT.stat().st_size/1024/1024, 2), "MB")
