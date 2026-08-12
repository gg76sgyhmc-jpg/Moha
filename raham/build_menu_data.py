#!/usr/bin/env python3
"""Rebuild data/menu.json from the café's own in-store menu boards.

The first version of this page took its catalogue from the HungerStation
delivery listing, which is the only machine-readable source. The owner then
supplied photographs of the printed in-store menu, and those are authoritative:
different prices (delivery carries a markup), a different item list, and an
English name for every line, which the delivery listing does not have.

Prices and names below are transcribed from those boards. Descriptions,
calorie figures and photographs are carried across from the delivery record by
id, since those are per-item facts the boards do not print.

    python3 raham/build_menu_data.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE / "data" / "menu.json"
OUT = HERE / "data" / "menu.json"

# (Arabic, English, price, id in the delivery record or None for items the
#  boards carry that delivery does not). Order follows the boards.
BOARDS = [
    ("المشروبات", "DRINKS", [
        ("قهوة اليوم",        "Coffee Day",       "5",    102902489),
        ("قهوة مقطرة",        "Drip Coffee",      "9.90", 104286929),
        ("شاي مثلج",          "Ice Tea",          "10",   102902491),
        ("كركديه",            "Ice Roselle",      "7",    102902492),
        ("كرتادو",            "Cortado",          "8",    102902493),
        ("فلات وايت",         "Flatewhite",       "9",    102902494),
        ("كابتشينو",          "Cappuccino",       "10",   102902495),
        ("لاتيه",             "Latte",            "9",    102902496),
        ("امريكانو",          "Americano",        "8",    102902497),
        ("سبانش لاتيه",       "Spanish latte",    "10",   102902498),
        ("اسبريسو",           "Espresso",         "7",    102902499),
        ("اسبريسو الفريدو",   "Espresso alfredo", "10",   102902500),
        ("ماتشا",             "Matcha",           "12",   102902501),
    ]),
    ("الحلا", "DESSERT", [
        ("رهم تشوكلت كيك",    "Raham Chocolate cake", "14", 102902502),
        ("براونيز",           "Brownies",             "9",  None),
        ("كوكيز رهم",         "Chocolate Cookies",    "7",  102902504),
        ("بستاشيو كنافة",     "Pistachio Kunafa",     "9",  102902505),
        ("ماجيك بار",         "Magic Bar",            "8",  102902506),
        ("كندر كنافة",        "Kinder Kunafa",        "9",  None),
        ("بيكان تشوكلت بار",  "Pecan Chocolate bar",  "9",  102902508),
        ("كرات الطاقه",       "Energy Balls",         "10", None),
    ]),
]


def main() -> None:
    prior = {}
    if OLD.exists():
        for g in json.loads(OLD.read_text(encoding="utf-8")):
            for it in g["items"]:
                prior[it["id"]] = it

    out, kept, fresh = [], 0, 0
    for name_ar, name_en, rows in BOARDS:
        items = []
        for ar, en, price, old_id in rows:
            base = prior.get(old_id, {}) if old_id else {}
            if base:
                kept += 1
            else:
                fresh += 1
            items.append({
                "id": old_id if old_id else "b" + str(abs(hash(ar)) % 10**8),
                "name": ar,
                "name_en": en,
                "price": price,
                "desc": base.get("desc", ""),
                "calories": base.get("calories"),
                "image": base.get("image"),
            })
        out.append({"name": name_ar, "name_en": name_en, "items": items})
        print(f"{name_ar:12} {len(items):3} items", file=sys.stderr)

    dropped = set(prior) - {i["id"] for g in out for i in g["items"]}
    for d in sorted(dropped, key=str):
        print(f"  not on the boards, dropped: {prior[d]['name']}", file=sys.stderr)

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(g["items"]) for g in out)
    print(f"\n{total} items ({kept} carried photos/descriptions, {fresh} new) -> {OUT.name}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
