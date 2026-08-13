#!/usr/bin/env python3
"""يجلب مقاطع الخطوط المطلوبة من Google Fonts ويحوّلها إلى data URI.

يُنتج build/fonts-inline.css الذي يحقنه build.py في الصفحة. سياسة الأمان في
بيئة النشر تمنع تحميل الخطوط من نطاق خارجي، فلا بديل عن تضمينها في الملف.

نكتفي بمقطعي «arabic» و«latin» وبالأوزان المستعملة فعلاً في التصميم، لأن كل
مقطع إضافي يزيد حجم الصفحة بلا مقابل.
"""
import base64
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).parent
OUT_DIR = ROOT / "build"

FAMILIES = "family=Aref+Ruqaa:wght@700&family=IBM+Plex+Sans+Arabic:wght@300;400"
API = f"https://fonts.googleapis.com/css2?{FAMILIES}&display=swap"
# مرجع متصفح حديث، وإلا ردّت الخدمة بصيغة ttf الأثقل بدل woff2
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

KEEP_SUBSETS = {"arabic", "latin"}
KEEP_WEIGHTS = {"Aref Ruqaa": {"700"}, "IBM Plex Sans Arabic": {"300", "400"}}


def fetch(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> None:
    css = fetch(API, {"User-Agent": UA}).decode("utf-8")
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    if not blocks:
        raise SystemExit("لم تُعِد الخدمة أي كتلة @font-face")

    out, total = [], 0
    for subset, block in blocks:
        if subset not in KEEP_SUBSETS:
            continue
        family = re.search(r"font-family: '([^']+)'", block).group(1)
        weight = re.search(r"font-weight: (\d+)", block).group(1)
        if weight not in KEEP_WEIGHTS.get(family, set()):
            continue

        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        data = fetch(url)
        total += len(data)
        block = block.replace(url, "data:font/woff2;base64," + base64.b64encode(data).decode())
        # block بدل swap: الصفحة تنتظر الخطوط قبل الإقلاع، فلا وميض بخط بديل
        block = re.sub(r"font-display: swap;", "font-display: block;", block)
        out.append(block)
        print(f"  {family} {weight} [{subset}] — {len(data) // 1024} KB", file=sys.stderr)

    if not out:
        raise SystemExit("لم يُطابق أي خط المرشّحات")

    OUT_DIR.mkdir(exist_ok=True)
    target = OUT_DIR / "fonts-inline.css"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n{target.relative_to(ROOT)} — {os.path.getsize(target) // 1024} KB "
          f"(أصل الخطوط {total // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
