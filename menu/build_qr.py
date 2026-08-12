#!/usr/bin/env python3
"""Generate the Usta Ghazi menu QR code, and prove it scans back.

A QR code carries a URL, so the menu PDF has to be reachable first: the deploy
workflow publishes it at MENU_URL, and everything here points at that address.

Outputs, all in menu/qr/:
  menu-qr.svg   vector, for print at any size
  menu-qr.png   raster with the restaurant's mark in the middle
  card.html     a table card around the code, laid out for A6

The code is written at error-correction level H, which can lose 30% of itself
and still decode, so the mark can sit in the centre. The result is then decoded
again and checked against the URL — a QR that does not scan is worse than none.

    python3 menu/build_qr.py
"""
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

import segno
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "qr"
MENU_URL = "https://gg76sgyhmc-jpg.github.io/Moha/usta-ghazi/menu.pdf"

# The restaurant's own palette, taken from the menu this code opens.
INK = "#101010"
CREAM = "#FBF5EC"
RED = "#A6141C"
GOLD = "#F2B705"

# Past roughly a fifth of the width the mark starts eating into the recovery
# budget even at level H. Verified by decoding, not assumed.
LOGO_FRACTION = 0.19


def build_svg(scale: int = 16) -> str:
    qr = segno.make(MENU_URL, error="h")
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=scale, border=4, dark=INK, light=CREAM, xmldecl=False)
    svg = buf.getvalue().decode()

    logo = HERE / "logo.png"
    if not logo.exists():
        return svg

    side = qr.symbol_size(scale=scale, border=4)[0]
    box = side * LOGO_FRACTION
    pad = box * 0.16
    x = y = (side - box) / 2
    b64 = base64.b64encode(logo.read_bytes()).decode()
    # The cream plate matters as much as the mark: without it the logo blends
    # into the modules and the decoder loses the pattern.
    overlay = (
        f'<rect x="{x - pad:.1f}" y="{y - pad:.1f}" width="{box + 2 * pad:.1f}" '
        f'height="{box + 2 * pad:.1f}" rx="{box * .18:.1f}" fill="{CREAM}"/>'
        f'<image x="{x:.1f}" y="{y:.1f}" width="{box:.1f}" height="{box:.1f}" '
        f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64}"/>'
    )
    return svg.replace("</svg>", overlay + "</svg>")


def build_png(scale: int = 20) -> Path:
    qr = segno.make(MENU_URL, error="h")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=4, dark=INK, light=CREAM)
    buf.seek(0)
    im = Image.open(buf).convert("RGBA")

    logo = HERE / "logo.png"
    if logo.exists():
        side = im.width
        box = round(side * LOGO_FRACTION)
        pad = round(box * 0.16)
        mark = Image.open(logo).convert("RGBA")
        mark.thumbnail((box, box), Image.LANCZOS)

        plate = Image.new("RGBA", (box + 2 * pad, box + 2 * pad), CREAM)
        plate.paste(mark, ((plate.width - mark.width) // 2,
                           (plate.height - mark.height) // 2), mark)
        im.alpha_composite(plate, ((side - plate.width) // 2, (side - plate.height) // 2))

    dst = OUT / "menu-qr.png"
    im.convert("RGB").save(dst, optimize=True)
    return dst


def verify(path: Path) -> str:
    """Decode the finished image and return what a scanner would actually read."""
    import cv2

    img = cv2.imread(str(path))
    if img is None:
        sys.exit(f"could not read {path}")
    data, points, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if not data:
        sys.exit(f"FAILED: {path.name} does not decode — the code would not scan")
    return data


def main() -> None:
    OUT.mkdir(exist_ok=True)

    qr = segno.make(MENU_URL, error="h")
    print(f"url     {MENU_URL}", file=sys.stderr)
    print(f"symbol  version {qr.version} · error level {qr.error.upper()} "
          f"· {qr.symbol_size(scale=1, border=0)[0]} modules", file=sys.stderr)

    (OUT / "menu-qr.svg").write_text(build_svg(), encoding="utf-8")
    png = build_png()

    got = verify(png)
    ok = got == MENU_URL
    print(f"decoded {got}", file=sys.stderr)
    print(f"verify  {'OK — scans back to the exact URL' if ok else 'MISMATCH'}", file=sys.stderr)
    if not ok:
        sys.exit(1)

    print(f"wrote   qr/menu-qr.svg, qr/menu-qr.png ({png.stat().st_size/1024:.0f} KB)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
