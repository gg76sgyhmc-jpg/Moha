#!/usr/bin/env python3
"""يبني الصفحة النهائية من المصدر بعد حقن الخطوط المضمّنة.

المخرجات:
  index.html        مستند كامل قائم بذاته — للاستضافة المباشرة
  dist/artifact.html  المحتوى فقط (بلا html/head/body) — لأداة النشر

الخطوط تُضمَّن كـ data URI لأن سياسة الأمان تمنع تحميلها من نطاق خارجي.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent
page = (ROOT / "src" / "page.html").read_text(encoding="utf-8")
fonts = (ROOT / "build" / "fonts-inline.css").read_text(encoding="utf-8")

if "/* @FONTS@ */" not in page:
    raise SystemExit("لم يُعثر على موضع حقن الخطوط في src/page.html")

content = page.replace("/* @FONTS@ */", fonts)

(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist" / "artifact.html").write_text(content, encoding="utf-8")

# المصدر يبدأ بـ <title> و<style> (محتوى الرأس) ثم <div class="page"> (محتوى الجسد)
split = content.index('<div class="page"')
head, body = content[:split].strip(), content[split:].strip()

DESCRIPTION = (
    "النجوم التي ما زال العالم ينطق أسماءها بالعربية: الدبران، رجل الجوزاء، "
    "النسر الواقع، الغول — وكيف انتقلت من مخطوطات القرن العاشر إلى خرائط السماء اليوم."
)

document = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{DESCRIPTION}">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#04050e">
{head}
</head>
<body>
{body}
</body>
</html>
"""

(ROOT / "index.html").write_text(document, encoding="utf-8")

kb = lambda p: (ROOT / p).stat().st_size // 1024
print(f"index.html          {kb('index.html')} KB")
print(f"dist/artifact.html  {kb('dist/artifact.html')} KB")
