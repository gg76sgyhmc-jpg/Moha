#!/usr/bin/env python3
"""Build the TAYF site from src/index.template.html.

Produces two outputs from one source:
  index.html         a standalone document (GitHub Pages, local preview)
  dist/artifact.html a body fragment for publishing as a Claude Artifact

Fonts are inlined as base64 data URIs because the Artifact CSP blocks
requests to external hosts, including font CDNs.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "index.template.html"
FONT_DIR = ROOT / "assets" / "fonts"

# file, family, weight (a range for the variable face)
FACES = [
    ("plex-arabic-400.woff2", "IBM Plex Sans Arabic", "400"),
    ("plex-arabic-500.woff2", "IBM Plex Sans Arabic", "500"),
    ("plex-arabic-600.woff2", "IBM Plex Sans Arabic", "600"),
    ("plex-arabic-700.woff2", "IBM Plex Sans Arabic", "700"),
    ("sora-var.woff2", "Sora", "100 800"),
    ("plex-mono-500.woff2", "IBM Plex Mono", "500"),
]


def font_css() -> str:
    blocks = []
    for filename, family, weight in FACES:
        path = FONT_DIR / filename
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        blocks.append(
            '@font-face{font-family:"%s";font-style:normal;font-weight:%s;'
            'font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}'
            % (family, weight, b64)
        )
    return "\n".join(blocks)


def main() -> None:
    fragment = TEMPLATE.read_text(encoding="utf-8").replace("/*@FONTFACE@*/", font_css())

    # the fragment opens with <title> and <style>; everything after the first
    # </style> is body content.
    split_at = fragment.index("</style>") + len("</style>")
    head, body = fragment[:split_at], fragment[split_at:]

    document = "\n".join([
        "<!doctype html>",
        '<html lang="ar" dir="rtl">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="description" content="طيف — علامة صوتيات سعودية:'
        ' سماعات ومكبرات تُعاير نفسها على أذنك.">',
        '<meta name="theme-color" content="#05070e">',
        head,
        "</head>",
        "<body>",
        body.strip(),
        "</body>",
        "</html>",
        "",
    ])

    (ROOT / "index.html").write_text(document, encoding="utf-8")

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "artifact.html").write_text(fragment, encoding="utf-8")

    print(f"index.html          {len(document) / 1024:.0f} KB")
    print(f"dist/artifact.html  {len(fragment) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
