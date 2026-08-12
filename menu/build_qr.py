#!/usr/bin/env python3
"""Generate the QR code that opens the Usta Ghazi menu PDF.

The PDF has to be reachable before a code can point at it: the deploy workflow
publishes it at MENU_URL, and this points there. Encoding, the centred mark and
the verification live in tools/qr.py, shared with the Raham code.

    python3 menu/build_qr.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import qr as qrlib  # noqa: E402
import sites  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "qr"
MENU_URL = sites.url("usta-ghazi", "menu.pdf")

INK = "#101010"    # the black band on the menu
CREAM = "#FBF5EC"  # the menu's paper


def main() -> None:
    OUT.mkdir(exist_ok=True)
    symbol, png, svg = qrlib.make(MENU_URL, dark=INK, light=CREAM, logo=HERE / "logo.png")

    print(f"url      {MENU_URL}", file=sys.stderr)
    print(f"symbol   version {symbol.version} · level {symbol.error.upper()} · "
          f"{symbol.symbol_size(scale=1, border=0)[0]} modules", file=sys.stderr)
    print(f"contrast {qrlib.contrast(INK, CREAM):.1f}:1  ({INK} on {CREAM})", file=sys.stderr)

    png_path = OUT / "menu-qr.png"
    png.save(png_path, optimize=True)
    (OUT / "menu-qr.svg").write_text(svg, encoding="utf-8")

    got = qrlib.verify(png_path, MENU_URL)
    print(f"decoded  {got}\nverify   OK — scans back to the exact URL", file=sys.stderr)

    foot = sites.display("usta-ghazi", "menu.pdf")
    if sites.stamp_card(OUT / "card.html", foot):
        print(f"card     footer restamped to {foot} — re-export card.pdf", file=sys.stderr)
    print(f"wrote    qr/menu-qr.png ({png_path.stat().st_size/1024:.0f} KB), qr/menu-qr.svg",
          file=sys.stderr)


if __name__ == "__main__":
    main()
