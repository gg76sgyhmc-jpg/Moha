#!/usr/bin/env python3
"""Fetch the site's webfonts as local files so the site has no third-party calls.

Writes site/assets/fonts/*.woff2 plus a fonts.css that references them
relatively. The standalone build inlines the same files as data: URIs.

Only the arabic and latin subsets are kept, and only the weights the design
actually uses — Almarai carries the display line, Tajawal the text, and
Cormorant Garamond the Latin display accents that echo the logo's script.

    python3 site/build_fonts.py        (needs network)
"""
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets" / "fonts"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
KEEP = {"arabic", "latin"}

FAMILIES = [
    ("Almarai", "wght@800"),
    ("Tajawal", "wght@300;400;500;700"),
    ("Cormorant+Garamond", "wght@300;400;500"),
]

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
    groups: dict[str, dict] = {}

    for family, axis in FAMILIES:
        css = fetch(f"https://fonts.googleapis.com/css2?family={family}:{axis}&display=swap").decode()
        for subset, face in BLOCK.findall(css):
            if subset not in KEEP:
                continue
            m = URL.search(face)
            if not m:
                continue
            # Google serves one variable file per (family, subset); the same URL
            # comes back for every requested weight, so group by URL and declare
            # the range it covers rather than downloading it once per weight.
            g = groups.setdefault(m.group(1), {"face": face, "weights": set(),
                                               "family": family.replace("+", ""), "subset": subset})
            g["weights"].update(int(w) for w in WEIGHT.findall(face))

    chunks, total = [], 0
    for url, g in groups.items():
        data = fetch(url)
        total += len(data)
        name = f"{g['family']}-{g['subset']}-{min(g['weights'])}.woff2"
        (OUT / name).write_bytes(data)
        lo, hi = min(g["weights"]), max(g["weights"])
        face = WEIGHT.sub(f"font-weight: {lo} {hi}" if lo != hi else f"font-weight: {lo}",
                          g["face"], count=1)
        chunks.append(URL.sub(f"url(assets/fonts/{name})", face))
        print(f"  {g['family']:18} {g['subset']:7} {lo}-{hi:<4} {len(data):>7,} B", file=sys.stderr)

    (HERE / "fonts.css").write_text("\n".join(chunks) + "\n")
    print(f"\n{len(chunks)} faces, {total/1024:.0f} KB", file=sys.stderr)


if __name__ == "__main__":
    main()
