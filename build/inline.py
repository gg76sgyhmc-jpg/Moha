#!/usr/bin/env python3
"""
يبني نسخة الملف الواحد من الموقع.

  dist/emaar-estethmaar.html  ملف HTML مستقل تماماً (خطوط وصور وأنماط مضمّنة)
  dist/artifact.html          نفس المحتوى بلا وسوم <html>/<head>/<body> لنشره كـ Artifact

التشغيل:  python3 build/inline.py
"""

import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MIMES = {
    ".woff2": "font/woff2",
    ".webp": "image/webp",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}


def data_uri(path: Path) -> str:
    mime = MIMES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return "data:%s;base64,%s" % (mime, base64.b64encode(path.read_bytes()).decode("ascii"))


def inline_css(css: str, css_dir: Path) -> str:
    """يستبدل كل url('../x') داخل CSS بـ data URI."""

    def sub(m):
        raw = m.group(2).strip()
        if raw.startswith(("data:", "http:", "https:", "#")):
            return m.group(0)
        target = (css_dir / raw).resolve()
        if not target.exists():
            print("  ! مفقود في CSS: %s" % raw, file=sys.stderr)
            return m.group(0)
        return "url(%s)" % data_uri(target)

    return re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", sub, css)


def build() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    css_path = ROOT / "assets" / "css" / "styles.css"
    css = inline_css(css_path.read_text(encoding="utf-8"), css_path.parent)
    js = (ROOT / "assets" / "js" / "site.js").read_text(encoding="utf-8")

    html = html.replace(
        '<link rel="stylesheet" href="./assets/css/styles.css">',
        "<style>\n%s\n</style>" % css,
    )
    html = html.replace(
        '<script src="./assets/js/site.js"></script>',
        "<script>\n%s\n</script>" % js,
    )

    # روابط تحميل الخطوط المسبق لم تعد لها فائدة بعد التضمين
    html = re.sub(r'\s*<link rel="preload"[^>]*>', "", html)

    # كل الصور المشار إليها من HTML
    used = sorted(set(re.findall(r'\./assets/img/([\w.\-]+)', html)))
    for name in used:
        path = ROOT / "assets" / "img" / name
        if not path.exists():
            print("  ! صورة مفقودة: %s" % name, file=sys.stderr)
            continue
        html = html.replace("./assets/img/%s" % name, data_uri(path))

    left = re.findall(r'\./assets/[\w./\-]+', html)
    if left:
        print("  ! مراجع خارجية متبقية: %s" % sorted(set(left)), file=sys.stderr)

    DIST.mkdir(exist_ok=True)
    standalone = DIST / "emaar-estethmaar.html"
    standalone.write_text(html, encoding="utf-8")

    # نسخة الـ Artifact: العنوان + الأنماط + المحتوى + السكربت، بلا هيكل الصفحة
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    style = re.search(r"<style>.*?</style>", html, re.S)
    body = re.search(r"<body>(.*?)</body>", html, re.S)
    if not (title and style and body):
        raise SystemExit("تعذّر تفكيك index.html")

    artifact = "<title>%s</title>\n%s\n%s\n" % (title.group(1), style.group(0), body.group(1).strip())
    (DIST / "artifact.html").write_text(artifact, encoding="utf-8")

    for f in (standalone, DIST / "artifact.html"):
        print("  ✓ %-34s %6.2f MB" % (f.relative_to(ROOT), f.stat().st_size / 1048576))


if __name__ == "__main__":
    build()
