#!/usr/bin/env python3
"""يبني مخرجين من قالب واحد:
   index.html        صفحة كاملة مستقلة (للاستضافة)
   build/artifact.html  جزء الصفحة فقط (لنشرها كـ Artifact)
"""
import base64, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
tpl  = (ROOT / "build/template.html").read_text(encoding="utf-8")

def data_uri(rel, mime="image/webp"):
    return f"data:{mime};base64," + base64.b64encode((ROOT / rel).read_bytes()).decode()

tpl = (tpl.replace("{{LOGO_BADGE}}", data_uri("assets/logo-badge.webp"))
          .replace("{{LOGO_HYRAX}}", data_uri("assets/logo-hyrax.webp")))
assert "{{" not in tpl, "placeholder left unresolved"

head, body = tpl.split("<!--@@BODY@@-->", 1)

(ROOT / "build/artifact.html").write_text(head + body, encoding="utf-8")

(ROOT / "index.html").write_text(
    "<!doctype html>\n<html lang=\"ar\" dir=\"rtl\">\n<head>\n"
    + head.strip() + "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n",
    encoding="utf-8")

for f in ("index.html", "build/artifact.html"):
    print(f"{f}: {(ROOT / f).stat().st_size:,} bytes")
