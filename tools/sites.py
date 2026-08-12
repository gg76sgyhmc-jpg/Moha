#!/usr/bin/env python3
"""Where each site lives.

Every printed URL and every QR code resolves through here, so moving to a real
domain is one edit — set DOMAIN, re-run the two build_qr.py scripts, and the
codes and the cards follow. Nothing else hardcodes an address.

Until a domain is pointed at GitHub Pages, DOMAIN stays None and everything
falls back to the project paths under github.io, which is where the sites are
served from today.

    python3 tools/sites.py     # print what every URL currently is
"""
from __future__ import annotations

import re
from pathlib import Path

# ── The one line to change ────────────────────────────────────────────────────
#
# Set this to the bare domain once its DNS points at GitHub Pages *and* each
# repo's Pages settings carry the matching custom domain. Setting it earlier
# bakes an address that does not resolve yet into printed cards.
DOMAIN: str | None = None          # e.g. "so-mr.com"
# ──────────────────────────────────────────────────────────────────────────────

GH_USER = "gg76sgyhmc-jpg"
GH_REPO = "Moha"

# `sub` is the subdomain the project gets once DOMAIN is set; `path` is where it
# sits under github.io until then. The two shapes differ — on github.io every
# site shares one host and is told apart by path, while a subdomain gives each
# site its own root — so both are recorded rather than derived from each other.
PROJECTS: dict[str, dict[str, str]] = {
    "raham":      {"sub": "raham",     "path": "/"},
    "usta-ghazi": {"sub": "ustaghazi", "path": "/usta-ghazi/"},
    "elegance":   {"sub": "elegance",  "path": "/elegance/"},
}


def root(project: str) -> str:
    """Base URL of a project, with a trailing slash."""
    if project not in PROJECTS:
        raise KeyError(f"unknown project {project!r}; known: {sorted(PROJECTS)}")
    p = PROJECTS[project]
    if DOMAIN:
        return f"https://{p['sub']}.{DOMAIN}/"
    return f"https://{GH_USER}.github.io/{GH_REPO}{p['path']}"


def url(project: str, file: str = "") -> str:
    """Absolute URL of a file inside a project."""
    return root(project) + file.lstrip("/")


def display(project: str, file: str = "") -> str:
    """The same address without the scheme — what goes on a printed card.

    A trailing slash is dropped too: `raham.so-mr.com` reads as an address,
    `raham.so-mr.com/` reads as a mistake.
    """
    return url(project, file).removeprefix("https://").rstrip("/")


_FOOT = re.compile(r'(<p class="foot">)([^<]*)(</p>)')


def stamp_card(card: Path, text: str) -> bool:
    """Write `text` into the card's footer line. Returns True if it changed.

    The address printed under a QR code has to be the address the code carries;
    a card still showing the old host after a move is worse than one showing
    none. Rather than trust the two to be edited together, the build stamps it.
    """
    html = card.read_text(encoding="utf-8")
    new, n = _FOOT.subn(lambda m: m[1] + text + m[3], html, count=1)
    if not n:
        raise RuntimeError(f'{card}: no <p class="foot"> to stamp')
    if new == html:
        return False
    card.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    where = f"the {DOMAIN} domain" if DOMAIN else "GitHub Pages (no domain set yet)"
    print(f"serving from {where}\n")
    width = max(len(p) for p in PROJECTS)
    for name in PROJECTS:
        print(f"  {name:<{width}}  {root(name)}")
    print(f"\n  {'menu pdf':<{width}}  {url('usta-ghazi', 'menu.pdf')}")


if __name__ == "__main__":
    main()
