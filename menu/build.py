#!/usr/bin/env python3
"""Build the Usta Ghazi menu into a single self-contained HTML file.

Menu data lives here as plain Python so prices can be corrected in one place;
the layout lives in template.html. Fonts are inlined from fonts.css (built by
tools/embed_fonts.py) so the result needs no network at print time.

    python3 menu/build.py
"""
from html import escape
from pathlib import Path

HERE = Path(__file__).parent

# ── Menu data ────────────────────────────────────────────────────────────────
# (Arabic name, English name, price in SAR)
# Ordered cheapest first within each group so the ladder reads plain/cheese →
# red bread → saroukh, instead of the original's jumbled order.
SANDWICHES = [
    ("شاورما عادي",                  "Shawarma Normal",              "7"),
    ("شاورما بالجبن",                "Shawarma Cheese",              "8"),
    ("شاورما خبز أحمر",              "Shawarma Red Bread",           "8"),
    ("شاورما خبز أحمر بالجبن",       "Shawarma Red Bread & Cheese",  "9"),
    ("شاورما صاروخ",                 "Shawarma Saroukh",             "13"),
    ("شاورما صاروخ بالجبن",          "Shawarma Saroukh & Cheese",    "14"),
    ("شاورما صاروخ خبز أحمر",        "Shawarma Saroukh Red Bread",   "14"),
    ("شاورما صاروخ خبز أحمر بالجبن", "Saroukh Red Bread & Cheese",   "15"),
]

# Piece counts, small → large (the original ran large → small, against the
# cheapest-first reading order used everywhere else on the sheet).
PIECES = ["6", "9", "12", "18", "24", "30"]

ARABI = [
    ("شاورما عربي",                "Shawarma Arabi",                   ["17", "25", "34", "47", "63", "75"]),
    ("شاورما عربي بالجبن",         "Shawarma Arabi & Cheese",          ["18", "26", "36", "49", "65", "80"]),
    ("شاورما عربي خبز أحمر",       "Shawarma Arabi Red Bread",         ["18", "26", "36", "49", "65", "80"]),
    ("شاورما عربي خبز أحمر بالجبن", "Arabi Red Bread & Cheese",        ["19", "27", "37", "50", "66", "85"]),
]

# Price is either a single string, or a list of (price, size-label) pairs for a
# dish sold in two sizes — the original listed fries twice as "7/13".
PLATES = [
    ("صحن شاورما",      "Shawarma Plate",     "30"),
    ("صحن شاورما كبير", "Shawarma Big Plate", "55"),
    ("بطاطس",           "French Fries",       [("7", "صغير"), ("13", "كبير")]),
]

DRINKS = [
    ("مشروبات غازية", "Soft Drinks", "3"),
    ("ماء",           "Water",       "1"),
]


def item_row(ar: str, en: str, price) -> str:
    """One dish row: name + dotted leader + price anchored on the far side."""
    if isinstance(price, str):
        cell = escape(price)
    else:
        cell = "".join(
            f'<span class="pv">{escape(p)}<sub>{escape(label)}</sub></span>'
            for p, label in price
        )
    return (
        '        <div class="item">\n'
        f'          <p class="item__name">{escape(ar)}</p>\n'
        f'          <p class="item__en">{escape(en)}</p>\n'
        '          <span class="item__leader" aria-hidden="true"></span>\n'
        f'          <p class="item__price">{cell}</p>\n'
        '        </div>'
    )


def main() -> None:
    html = (HERE / "template.html").read_text(encoding="utf-8")

    fonts = (HERE / "fonts.css").read_text(encoding="utf-8")
    html = html.replace("/*@FONTS@*/", fonts)

    # The emblem is sourced from one file so swapping in the restaurant's own
    # artwork is a single edit; both sheets pick it up from here.
    logo = (HERE / "logo.svg").read_text(encoding="utf-8")
    logo = logo[logo.index("<svg") :].strip()
    html = html.replace("<!--@LOGO@-->", logo)

    html = html.replace(
        "<!--@SANDWICHES@-->",
        "\n".join(item_row(*row) for row in SANDWICHES).lstrip(),
    )
    html = html.replace(
        "<!--@PIECEHEADS@-->",
        "\n".join(
            f'              <th scope="col">{p}<span>قطعة</span></th>' for p in PIECES
        ).lstrip(),
    )
    html = html.replace(
        "<!--@ARABI@-->",
        "\n".join(
            f'            <tr><td>{escape(ar)}<span>{escape(en)}</span></td>'
            + "".join(f'<td class="p">{p}</td>' for p in prices)
            + "</tr>"
            for ar, en, prices in ARABI
        ).lstrip(),
    )
    html = html.replace(
        "<!--@PLATES@-->",
        "\n".join(item_row(*row) for row in PLATES).lstrip(),
    )
    html = html.replace(
        "<!--@DRINKS@-->",
        "\n".join(item_row(*row) for row in DRINKS).lstrip(),
    )

    assert "@" not in html.split("<style>")[0], "unfilled placeholder in head"
    for marker in ("@SANDWICHES@", "@ARABI@", "@PLATES@", "@DRINKS@", "@PIECEHEADS@", "@FONTS@", "@LOGO@"):
        assert marker not in html, f"unfilled placeholder: {marker}"

    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out} — {len(html.encode()):,} bytes")


if __name__ == "__main__":
    main()
