#!/usr/bin/env python3
"""Clean up the low-resolution Usta Ghazi badge without redrawing it.

The supplied crop is a ~93px JPEG, so more than half its pixels are neither
the mark's cream nor its red but compression mush between the two. Nothing can
invent detail that was never captured, but two things are recoverable:

  1. Upscale first, so the tone decision is made on a smooth interpolation
     rather than on 93 hard pixels.
  2. Re-quantise toward the two colours the mark is actually drawn in, with a
     soft transition band that keeps edges anti-aliased instead of jagged.

Shapes, proportions and letterforms are untouched — this only restores the
flat colour the artwork had before JPEG smeared it.

    python3 tools/enhance_logo.py
"""
from pathlib import Path
from PIL import Image, ImageFilter
import base64
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "menu" / "logo.png"
OUT = ROOT / "menu" / "logo.png"
SVG = ROOT / "menu" / "logo.svg"

SCALE = 4
CREAM = (247, 243, 236)
RED = (170, 26, 22)

# Luminance below LO reads as red, above HI as cream; between the two the
# pixel is a genuine edge and keeps a proportional blend.
LO, HI = 118.0, 208.0


def smoothstep(t: float) -> float:
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    w0, h0 = im.size

    im = im.resize((w0 * SCALE, h0 * SCALE), Image.LANCZOS)
    w, h = im.size
    px = im.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            t = smoothstep((0.299 * r + 0.587 * g + 0.114 * b - LO) / (HI - LO))
            px[x, y] = (
                round(RED[0] + (CREAM[0] - RED[0]) * t),
                round(RED[1] + (CREAM[1] - RED[1]) * t),
                round(RED[2] + (CREAM[2] - RED[2]) * t),
                a,
            )

    # Take the ragged JPEG edge off the alpha channel, then firm it back up.
    alpha = im.getchannel("A").filter(ImageFilter.GaussianBlur(SCALE * 0.35))
    alpha = alpha.point(lambda v: 0 if v < 90 else (255 if v > 165 else int((v - 90) * 255 / 75)))
    im.putalpha(alpha)

    im.save(OUT)
    print(f"{w0}x{h0} -> {w}x{h}, {OUT.stat().st_size:,} B", file=sys.stderr)

    b64 = base64.b64encode(OUT.read_bytes()).decode()
    SVG.write_text(
        f"""<!-- ────────────────────────────────────────────────────────────────────────────
     Usta Ghazi logo — the restaurant's own mark, taken from the artwork they
     supplied. The mark is not redrawn: the menu background around it (black
     header band, gold strip, red field) was flood-filled away, and the JPEG
     colour mush was re-quantised to the cream and red it is drawn in.

     Detail is still limited by the {w0}x{h0} px source. Replace this file with
     the original vector or high-resolution logo when it is available and
     re-run `python3 menu/build.py` — both sheets are inlined from here.
     ──────────────────────────────────────────────────────────────────────── -->
<svg class="logo" viewBox="0 0 {w} {h}" role="img" aria-label="شعار أسطا غازي — Usta Ghazi">
  <image href="data:image/png;base64,{b64}" x="0" y="0" width="{w}" height="{h}"/>
</svg>
""",
        encoding="utf-8",
    )
    print(f"logo.svg written ({len(b64):,} B base64)", file=sys.stderr)


if __name__ == "__main__":
    main()
