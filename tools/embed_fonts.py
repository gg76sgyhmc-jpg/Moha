#!/usr/bin/env python3
"""Inline Google Fonts woff2 files as base64 data: URIs so the menu is self-contained."""
import base64
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
KEEP_SUBSETS = {"arabic", "latin"}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

BLOCK = re.compile(r"/\*\s*([\w\-\[\]]+)\s*\*/\s*(@font-face\s*\{.*?\})", re.S)
URL = re.compile(r"url\((https://[^)]+\.woff2)\)")


def fetch(url: str) -> bytes:
    out = subprocess.run(
        ["curl", "-sS", "--fail", "-A", UA, url], capture_output=True, timeout=60
    )
    if out.returncode != 0:
        sys.exit(f"failed to fetch {url}: {out.stderr.decode()[:200]}")
    return out.stdout


WEIGHT = re.compile(r"font-weight:\s*(\d+)")


def main() -> None:
    # Google serves one variable-font file per (family, subset); the same URL comes
    # back for every requested weight. Group by URL so each file is fetched and
    # embedded once, then declare it over the full weight range it actually covers.
    groups: dict[str, dict] = {}
    for css_file in sorted(HERE.glob("css_*.txt")):
        for subset, face in BLOCK.findall(css_file.read_text()):
            if subset not in KEEP_SUBSETS:
                continue
            m = URL.search(face)
            if not m:
                continue
            g = groups.setdefault(m.group(1), {"face": face, "weights": set(), "subset": subset,
                                               "family": css_file.stem[4:]})
            g["weights"].update(int(w) for w in WEIGHT.findall(face))

    chunks, total = [], 0
    for url, g in groups.items():
        data = fetch(url)
        total += len(data)
        b64 = base64.b64encode(data).decode()
        lo, hi = min(g["weights"]), max(g["weights"])
        face = WEIGHT.sub(f"font-weight: {lo} {hi}" if lo != hi else f"font-weight: {lo}",
                          g["face"], count=1)
        chunks.append(URL.sub(f"url(data:font/woff2;base64,{b64})", face))
        print(f"  {g['family']:8} {g['subset']:8} {lo}-{hi:<4} {len(data):>7,} B", file=sys.stderr)

    (HERE / "fonts.css").write_text("\n".join(chunks) + "\n")
    print(f"\n{len(chunks)} faces, {total:,} B raw -> fonts.css", file=sys.stderr)


if __name__ == "__main__":
    main()
