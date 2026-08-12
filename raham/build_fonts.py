#!/usr/bin/env python3
"""Fetch IBM Plex Sans Arabic as local files, so the pages call no CDN.

One family across both pages, carried by weight and tracking rather than a
second face — the logo is already a piece of calligraphy, and a competing
display face would fight it.

    python3 raham/build_fonts.py        (needs network)
"""
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets" / "fonts"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
KEEP = {"arabic", "latin"}
# Three weights carry the whole system: 300 for running text, 500 for
# labels and prices, 700 for headings. Each Arabic subset costs ~45KB,
# so every extra weight is a real download.
FAMILY = ("IBM+Plex+Sans+Arabic", "wght@300;500;700")

BLOCK = re.compile(r"/\*\s*([\w\-\[\]]+)\s*\*/\s*(@font-face\s*\{.*?\})", re.S)
URL = re.compile(r"url\((https://[^)]+\.woff2)\)")
WEIGHT = re.compile(r"font-weight:\s*(\d+)")


def fetch(url: str) -> bytes:
    r = subprocess.run(["curl", "-sS", "--fail", "-A", UA, url], capture_output=True, timeout=90)
    if r.returncode:
        sys.exit(f"failed {url}: {r.stderr.decode()[:200]}")
    return r.stdout


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fam, axis = FAMILY
    css = fetch(f"https://fonts.googleapis.com/css2?family={fam}:{axis}&display=swap").decode()

    chunks, total = [], 0
    for subset, face in BLOCK.findall(css):
        if subset not in KEEP:
            continue
        m = URL.search(face)
        if not m:
            continue
        data = fetch(m.group(1))
        total += len(data)
        weight = WEIGHT.search(face).group(1)
        name = f"PlexArabic-{subset}-{weight}.woff2"
        (OUT / name).write_bytes(data)
        chunks.append(URL.sub(f"url(assets/fonts/{name})", face))
        print(f"  {subset:7} {weight}  {len(data):>7,} B", file=sys.stderr)

    (HERE / "fonts.css").write_text("\n".join(chunks) + "\n")
    print(f"\n{len(chunks)} faces, {total/1024:.0f} KB", file=sys.stderr)


if __name__ == "__main__":
    main()
