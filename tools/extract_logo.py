#!/usr/bin/env python3
"""Lift the Usta Ghazi badge out of the supplied crop without redrawing it.

The crop carries menu background on three sides: the black header band along
the top, the gold strip along the bottom, and the red field all around. Only
that background is removed — by flood-filling inward from the border, which
stops at the badge's white outline and so never touches the red inside the
mark (its line work and the wordmark).
"""
from PIL import Image, ImageDraw
import sys

SRC = "/root/.claude/uploads/2e0f12fc-3d78-5146-8cd4-1faea51065d8/15d27bc8-IMG_1221.jpeg"
OUT = "/tmp/claude-0/-home-user-Moha/2e0f12fc-3d78-5146-8cd4-1faea51065d8/scratchpad/logo-cut.png"

im = Image.open(SRC).convert("RGBA")
w, h = im.size

# Trim the two horizontal bleeds first (measured from the row averages:
# dark band above y=5, gold strip below y=117).
im = im.crop((0, 5, w, 117))
w, h = im.size

# Flood the surrounding red from every border pixel. Tolerance covers the
# JPEG noise in what should be one flat colour.
seen = set()
for x in range(w):
    for y in (0, h - 1):
        if im.getpixel((x, y))[3]:
            ImageDraw.floodfill(im, (x, y), (0, 0, 0, 0), thresh=62)
for y in range(h):
    for x in (0, w - 1):
        if im.getpixel((x, y))[3]:
            ImageDraw.floodfill(im, (x, y), (0, 0, 0, 0), thresh=62)

# Two specks of the gold strip survive as islands the border flood cannot
# reach. Drop anything not part of the badge's own connected body.
px = im.load()
w2, h2 = im.size
seen = [[False] * h2 for _ in range(w2)]
islands = []
for sx in range(w2):
    for sy in range(h2):
        if seen[sx][sy] or px[sx, sy][3] < 40:
            continue
        stack, body = [(sx, sy)], []
        seen[sx][sy] = True
        while stack:
            x, y = stack.pop()
            body.append((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w2 and 0 <= ny < h2 and not seen[nx][ny] and px[nx, ny][3] >= 40:
                    seen[nx][ny] = True
                    stack.append((nx, ny))
        islands.append(body)
islands.sort(key=len, reverse=True)
for stray in islands[1:]:
    print(f"dropping {len(stray)}px speck", file=sys.stderr)
    for x, y in stray:
        px[x, y] = (0, 0, 0, 0)

# Crop to what survived, so the badge sits flush in its box.
bbox = im.getbbox()
im = im.crop(bbox)
print(f"cut to {im.size[0]}x{im.size[1]} (from {w}x{h}), bbox={bbox}", file=sys.stderr)

opaque = sum(1 for p in im.getdata() if p[3] > 200)
print(f"{opaque} opaque px of {im.size[0]*im.size[1]}", file=sys.stderr)

im.save(OUT)
im.resize((im.width * 5, im.height * 5), Image.LANCZOS).save(OUT.replace(".png", "-zoom.png"))
