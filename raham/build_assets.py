#!/usr/bin/env python3
"""Prepare Raham Coffee assets.

The logo is used exactly as supplied — cream calligraphy on the brand's sage
green. It is only trimmed to its own edges and re-encoded; the mark itself is
untouched. A second cutout version (cream on transparent) is written for the
places where the page's own sage green is already the ground, which is the same
figure/ground relationship the original has.

    python3 raham/build_assets.py
"""
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src"
OUT = HERE / "assets"

CARD_W = 560
QUALITY = 76
SAGE = (163, 174, 132)   # #A3AE84 — sampled from the logo, 70% of its pixels


def main() -> None:
    if not SRC.exists():
        sys.exit(f"missing {SRC} — see raham/README.md")
    (OUT / "items").mkdir(parents=True, exist_ok=True)

    # ── logo, as-is: trim the flat surround so it sits tight in its badge ──
    logo = Image.open(SRC / "logo.jpeg").convert("RGB")
    w, h = logo.size
    px = logo.load()
    bbox = [w, h, 0, 0]
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - SAGE[0]) + abs(g - SAGE[1]) + abs(b - SAGE[2]) > 48:
                bbox = [min(bbox[0], x), min(bbox[1], y), max(bbox[2], x), max(bbox[3], y)]
    pad = 26
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
           min(w, bbox[2] + pad), min(h, bbox[3] + pad))
    logo.crop(box).save(OUT / "logo.webp", "WEBP", quality=92, method=6)
    print(f"logo   {w}x{h} -> {box[2]-box[0]}x{box[3]-box[1]}", file=sys.stderr)

    # ── cutout: same mark with the sage dropped to alpha ──
    cut = logo.crop(box).convert("RGBA")
    cp = cut.load()
    for y in range(cut.height):
        for x in range(cut.width):
            r, g, b, _ = cp[x, y]
            d = abs(r - SAGE[0]) + abs(g - SAGE[1]) + abs(b - SAGE[2])
            # Feather across the antialiased edge instead of hard-keying it,
            # or the calligraphy's thin strokes turn ragged.
            cp[x, y] = (r, g, b, 0 if d < 26 else (255 if d > 78 else int((d - 26) * 255 / 52)))
    cut.save(OUT / "logo-mark.webp", "WEBP", quality=92, method=6)

    # ── cover ──
    cover = Image.open(SRC / "cover.png").convert("RGB")
    cover.thumbnail((1400, 1400), Image.LANCZOS)
    cover.save(OUT / "cover.webp", "WEBP", quality=80, method=6)

    # ── menu photos ──
    tin = tout = 0
    for f in sorted((SRC / "items").glob("*")):
        if f.suffix.lower() not in {".jpeg", ".jpg", ".png", ".webp"}:
            continue
        tin += f.stat().st_size
        im = Image.open(f).convert("RGB")
        if im.width > CARD_W:
            im = im.resize((CARD_W, round(im.height * CARD_W / im.width)), Image.LANCZOS)
        dst = OUT / "items" / f"{f.stem}.webp"
        im.save(dst, "WEBP", quality=QUALITY, method=6)
        tout += dst.stat().st_size

    n = len(list((OUT / "items").glob("*.webp")))
    print(f"{n} photos  {tin/1e6:.1f}MB -> {tout/1e6:.2f}MB", file=sys.stderr)


if __name__ == "__main__":
    main()
