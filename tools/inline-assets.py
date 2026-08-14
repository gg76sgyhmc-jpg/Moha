#!/usr/bin/env python3
"""يدمج أي ملف في assets/ مشار إليه داخل index.html كـ data: URI،
حتى يبقى الموقع ملفًا واحدًا مستقلًا لا يحتاج أي مورد خارجي.

الاستخدام:  python3 tools/inline-assets.py
"""
import base64
import mimetypes
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"

html = PAGE.read_text(encoding="utf-8")
refs = sorted(set(re.findall(r'"(assets/[^"]+)"', html)))

if not refs:
    print("لا توجد مسارات assets/ غير مدمجة — الملف مكتفٍ بذاته.")
    sys.exit(0)

for ref in refs:
    path = ROOT / ref
    if not path.exists():
        print(f"⚠️  غير موجود: {ref}")
        continue
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    uri = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    html = html.replace(f'"{ref}"', f'"{uri}"')
    print(f"✓ {ref}  ({path.stat().st_size / 1024:.0f} KB)")

PAGE.write_text(html, encoding="utf-8")
print(f"\nindex.html = {PAGE.stat().st_size / 1024:.0f} KB")
