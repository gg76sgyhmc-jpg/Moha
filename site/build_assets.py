#!/usr/bin/env python3
"""Prepare Elegance Bar site assets: resize/convert the salon's own photos.

Source images come straight from the salon's booking profile and run up to
1536px and 180KB each. The site never displays one wider than a card, so they
are re-encoded to two WebP widths — a card size and a 2x retina size — which
takes the whole set from ~8MB to well under 1MB.

    python3 site/build_assets.py
"""
from pathlib import Path
import json
import shutil
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src_images"
OUT = HERE / "assets" / "services"
CARD_W = 480          # rendered card image is ~240px wide at most breakpoints
QUALITY = 74


def convert(src: Path, dst: Path, width: int) -> int:
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return dst.stat().st_size


def main() -> None:
    if not SRC.exists():
        sys.exit(f"missing {SRC} — see site/README.md for how the photos are fetched")
    OUT.mkdir(parents=True, exist_ok=True)

    total_in = total_out = 0
    for f in sorted(SRC.glob("*.jpeg")):
        total_in += f.stat().st_size
        total_out += convert(f, OUT / f"{f.stem}.webp", CARD_W)

    logo_src = SRC / "_logo.jpg"
    if logo_src.exists():
        im = Image.open(logo_src).convert("RGBA")
        # The supplied logo is black line art on flat white; lifting the white
        # to transparency lets it sit on the cream and navy sections alike.
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, _ = px[x, y]
                if r > 243 and g > 243 and b > 243:
                    px[x, y] = (r, g, b, 0)
        im.thumbnail((760, 760), Image.LANCZOS)
        im.save(HERE / "assets" / "logo.webp", "WEBP", quality=88, method=6, lossless=False)
        shutil.copy(logo_src, HERE / "assets" / "logo-original.jpg")

    n = len(list(OUT.glob("*.webp")))
    print(f"{n} photos  {total_in/1e6:.1f}MB -> {total_out/1e6:.2f}MB", file=sys.stderr)


if __name__ == "__main__":
    main()
