#!/usr/bin/env python3
"""
يبني نسخة معاينة مستقلة بملف واحد من الصفحة العربية.

يدمج ملف الأنماط والسكربت والخطوط والصور داخل ملف HTML واحد، بحيث يمكن
فتحه أو مشاركته دون أي ملفات مرافقة. الموقع القابل للنشر يبقى كما هو
(index.html / en.html + مجلد assets) — هذا الملف للمعاينة فقط.

    python3 build-preview.py
"""

import base64
import mimetypes
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "index.html"
OUT_DIR = ROOT / "preview"
OUT = OUT_DIR / "coldpole-ar.html"


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if path.suffix == ".webp":
        mime = "image/webp"
    elif path.suffix == ".woff2":
        mime = "font/woff2"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def inline_css(css: str, css_dir: Path) -> str:
    """يستبدل url(../x) داخل CSS بـ data URI."""
    def sub(m):
        rel = m.group(1).strip("'\"")
        if rel.startswith(("data:", "http")):
            return m.group(0)
        target = (css_dir / rel).resolve()
        if not target.exists():
            raise FileNotFoundError(f"asset referenced by CSS is missing: {target}")
        return f"url({data_uri(target)})"
    return re.sub(r"url\(([^)]+)\)", sub, css)


def main() -> None:
    html = SRC.read_text(encoding="utf-8")

    # 1. الأنماط
    css_path = ROOT / "assets/css/styles.css"
    css = inline_css(css_path.read_text(encoding="utf-8"), css_path.parent)

    # 2. السكربت
    js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")

    # 3. جسم الصفحة فقط (الغلاف يوفّره ناشر الـ artifact)
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)

    # الصور -> data URI
    def img_sub(m):
        attr, rel = m.group(1), m.group(2)
        target = (ROOT / rel).resolve()
        if not target.exists():
            raise FileNotFoundError(f"image referenced by HTML is missing: {target}")
        return f'{attr}="{data_uri(target)}"'
    body = re.sub(r'(src)="(assets/img/[^"]+)"', img_sub, body)

    # سكربت الصفحة الخارجي يُدمج أدناه
    body = re.sub(r'<script src="assets/js/main\.js" defer></script>', "", body)

    # مبدّل اللغة يحتاج ملفين، ولا معنى له في ملف معاينة واحد
    body = re.sub(r'<a class="lang-toggle"[^>]*>.*?</a>', "", body, flags=re.S)
    body = re.sub(r'<li><a href="en\.html"[^>]*>.*?</a></li>', "", body, flags=re.S)

    # صفحة المعاينة تُعرض ضمن معرض، فتحمل اسم المؤسسة وحده دون شرح لاحق.
    # أما index.html فيحتفظ بعنوانه الكامل لأنه الأنسب لمحركات البحث.
    title = "مؤسسة القطب البارد"

    OUT_DIR.mkdir(exist_ok=True)
    OUT.write_text(
        f"<title>{title}</title>\n"
        f"<style>\n{css}\n</style>\n"
        f'<div dir="rtl" lang="ar">\n{body}\n</div>\n'
        f"<script>\n{js}\n</script>\n",
        encoding="utf-8",
    )

    print(f"{OUT.relative_to(ROOT)}  —  {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
