#!/usr/bin/env python3
"""Pull the live Elegance Bar catalogue and photos, so the site is built only
from the salon's own content.

Writes data/catalogue.json and the source photos into _src_images/ (which the
repo does not track — build_assets.py re-encodes them into assets/).

    python3 site/pull_catalogue.py
"""
import json
import subprocess
import sys

HERE = __import__("pathlib").Path(__file__).resolve().parent
SLUG = "s-lon-h-n-l-n-k-lns-y"
BASE = f"https://{SLUG}.naeem.sa/api/backend"
HDR = ["-H", "Accept: application/json", "-H", "Accept-Language: ar", "-H", "X-BRANCH-ID: 80"]


def get(path):
    out = subprocess.run(["curl", "-sS", "--fail", *HDR, f"{BASE}/{path}"],
                         capture_output=True, timeout=90)
    if out.returncode:
        sys.exit(f"failed {path}: {out.stderr.decode()[:200]}")
    return json.loads(out.stdout)


cats = get("get_categories")["data"]["data"]
catalogue = []
for c in cats:
    svcs = get(f"book/services/{SLUG}?category_id={c['id']}")["data"]
    rows = []
    for s in svcs:
        # `details` is the plain string; `description` is a language record.
        rows.append({
            "id": s.get("id"),
            "name": s.get("name") or s.get("item_name"),
            "details": (s.get("details") or "").strip(),
            "price": s.get("total_price") or s.get("cost"),
            "original_price": s.get("original_price"),
            "duration": s.get("duration") or s.get("full_duration"),
            "image": s.get("image"),
            "online": s.get("enable_online_booking"),
            "status": s.get("status"),
            "sort": s.get("sort"),
        })
    catalogue.append({"id": c["id"], "name": c["name"], "sort": c.get("sort"), "services": rows})
    print(f"{c['name']:32} {len(rows):3} services", file=sys.stderr)

(HERE / "data").mkdir(exist_ok=True)
json.dump(catalogue, open(HERE / "data" / "catalogue.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# Photos, straight from the salon's media library.
src = HERE / "_src_images"
src.mkdir(exist_ok=True)
photos = {s["image"] for c in catalogue for s in c["services"] if s["image"]}
for rel in sorted(photos):
    dst = src / rel.split("/")[-1]
    if dst.exists():
        continue
    subprocess.run(["curl", "-sS", "--fail", "-m", "60",
                    f"https://partners.naeem.cg.sa/storage/{rel}", "-o", str(dst)], timeout=90)
subprocess.run(["curl", "-sS", "--fail", "-m", "60",
                "https://partners.naeem.cg.sa/storage/branches/1701346262.jpg",
                "-o", str(src / "_logo.jpg")], timeout=90)
print(f"{len(photos)} photos -> _src_images/", file=sys.stderr)
total = sum(len(c["services"]) for c in catalogue)
print(f"\n{len(catalogue)} categories, {total} services -> catalogue.json", file=sys.stderr)
