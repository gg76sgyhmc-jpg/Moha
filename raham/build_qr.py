#!/usr/bin/env python3
"""Generate the QR code that opens the Raham Coffee links page.

Coloured in the café's own palette: the deep green of their menu boards as the
dark modules, their cream as the ground. That keeps the code in the brand while
holding the polarity a scanner expects — dark on light. Inverting it to match
the page's own cream-on-green would look tidier and scan worse, which is not a
trade worth making on something printed and stuck to a wall.

    python3 raham/build_qr.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import qr as qrlib  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "qr"
LINKS_URL = "https://gg76sgyhmc-jpg.github.io/Moha/"

INK = "#151D15"    # the deep green of their boards — 98.9% of the supplied art
CREAM = "#F3F0D7"  # the cream type on those same boards


def main() -> None:
    OUT.mkdir(exist_ok=True)
    logo = HERE / "_src" / "logo.jpeg"
    if not logo.exists():
        logo = HERE / "assets" / "logo.webp"

    symbol, png, svg = qrlib.make(LINKS_URL, dark=INK, light=CREAM, logo=logo)

    print(f"url      {LINKS_URL}", file=sys.stderr)
    print(f"symbol   version {symbol.version} · level {symbol.error.upper()} · "
          f"{symbol.symbol_size(scale=1, border=0)[0]} modules", file=sys.stderr)
    print(f"contrast {qrlib.contrast(INK, CREAM):.1f}:1  ({INK} on {CREAM})", file=sys.stderr)

    png_path = OUT / "links-qr.png"
    png.save(png_path, optimize=True)
    (OUT / "links-qr.svg").write_text(svg, encoding="utf-8")

    got = qrlib.verify(png_path, LINKS_URL)
    print(f"decoded  {got}\nverify   OK — scans back to the exact URL", file=sys.stderr)
    print(f"wrote    qr/links-qr.png ({png_path.stat().st_size/1024:.0f} KB), qr/links-qr.svg",
          file=sys.stderr)


if __name__ == "__main__":
    main()
