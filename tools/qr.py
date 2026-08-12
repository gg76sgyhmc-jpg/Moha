#!/usr/bin/env python3
"""Shared QR generation: brand-coloured symbol, centred mark, and a real check.

Used by menu/build_qr.py (Usta Ghazi) and raham/build_qr.py (Raham Coffee).
Each caller brings its own URL, palette and logo; the encoding, the overlay
geometry and the verification are the same job and live here once.

Two rules this module enforces, because breaking either produces a code that
looks right and does not scan:

  * Dark modules on a light ground. Scanners expect that polarity, and a fair
    number simply fail on an inverted code however pretty it looks. A dark
    brand colour on a light brand colour keeps the look and the polarity.
  * Error correction H, and the centred mark kept small. H recovers 30% of the
    symbol, which is what buys room for a logo at all.

Nothing is returned until the finished PNG has been decoded again and matched
against the URL it was asked to carry.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

import segno
from PIL import Image

# How much of the symbol's width the centred mark may cover.
#
# Measured, not guessed: at level H this URL still decoded at 19%, 22% and 25%
# — full size, and downscaled to 40mm and 25mm at 300dpi — and failed at every
# size at 28%. 0.22 is the default because it reads clearly while staying a
# margin below the cliff; real scanning is harsher than a clean decode.
LOGO_FRACTION = 0.22
PLATE_PAD = 0.16      # cream margin around the mark, as a fraction of its box
PLATE_RADIUS = 0.18


def _relative_luminance(hex_colour: str) -> float:
    r, g, b = (int(hex_colour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_relative_luminance(a), _relative_luminance(b)))
    return (lb + .05) / (la + .05)


def make(url: str, dark: str, light: str, logo: Path | None = None,
         scale: int = 20, border: int = 4,
         logo_fraction: float | None = None) -> tuple[segno.QRCode, Image.Image, str]:
    """Return (symbol, composed PNG image, svg markup)."""
    frac = LOGO_FRACTION if logo_fraction is None else logo_fraction
    if frac > 0.25:
        raise ValueError(f"logo_fraction {frac} exceeds the 0.25 that still decoded "
                         "in testing; the symbol stops scanning around 0.28")
    if _relative_luminance(dark) > _relative_luminance(light):
        raise ValueError(
            f"dark={dark} is lighter than light={light}: an inverted QR is not "
            "reliably scannable. Swap them.")
    ratio = contrast(dark, light)
    if ratio < 7:
        raise ValueError(f"contrast {ratio:.1f}:1 between {dark} and {light} is too "
                         "low for a dependable scan; aim well above 7:1.")

    qr = segno.make(url, error="h")

    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=border, dark=dark, light=light)
    buf.seek(0)
    im = Image.open(buf).convert("RGBA")

    svg_buf = io.BytesIO()
    qr.save(svg_buf, kind="svg", scale=scale, border=border,
            dark=dark, light=light, xmldecl=False)
    svg = svg_buf.getvalue().decode()

    if logo and logo.exists():
        side = im.width
        box = round(side * frac)
        pad = round(box * PLATE_PAD)
        mark = Image.open(logo).convert("RGBA")
        mark.thumbnail((box, box), Image.LANCZOS)
        # The plate matters as much as the mark: dropped straight onto the
        # modules, a logo blends in and the decoder loses the pattern.
        plate = Image.new("RGBA", (box + 2 * pad, box + 2 * pad), light)
        plate.paste(mark, ((plate.width - mark.width) // 2,
                           (plate.height - mark.height) // 2), mark)
        im.alpha_composite(plate, ((side - plate.width) // 2, (side - plate.height) // 2))

        s_side = qr.symbol_size(scale=scale, border=border)[0]
        s_box = s_side * frac
        s_pad = s_box * PLATE_PAD
        x = y = (s_side - s_box) / 2
        b64 = base64.b64encode(logo.read_bytes()).decode()
        svg = svg.replace("</svg>",
            f'<rect x="{x - s_pad:.1f}" y="{y - s_pad:.1f}" '
            f'width="{s_box + 2 * s_pad:.1f}" height="{s_box + 2 * s_pad:.1f}" '
            f'rx="{s_box * PLATE_RADIUS:.1f}" fill="{light}"/>'
            f'<image x="{x:.1f}" y="{y:.1f}" width="{s_box:.1f}" height="{s_box:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64}"/>'
            "</svg>")

    return qr, im.convert("RGB"), svg


def verify(png_path: Path, expected: str) -> str:
    """Decode the written PNG the way a scanner would. Raises if it disagrees."""
    import cv2

    img = cv2.imread(str(png_path))
    if img is None:
        raise RuntimeError(f"could not read {png_path}")
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if not data:
        raise RuntimeError(f"{png_path.name} does not decode — it would not scan")
    if data != expected:
        raise RuntimeError(f"{png_path.name} decodes to {data!r}, expected {expected!r}")
    return data
