import random
import sys
from typing import Dict, List, Optional

import requests


DEFAULT_BASE_URL = "http://localhost:8013"  # host port for electronic-service


def _get(url: str, default):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code >= 400:
            return default
        return r.json()
    except Exception:
        return default


def _post(url: str, data: dict) -> Optional[requests.Response]:
    try:
        return requests.post(url, json=data, timeout=5)
    except Exception:
        return None


def seed_categories(base_url: str, categories: List[Dict[str, str]]) -> Dict[str, int]:
    existing = _get(f"{base_url}/electronics/categories/", [])
    name_to_id: Dict[str, int] = {}
    if isinstance(existing, list):
        for c in existing:
            if isinstance(c, dict) and c.get("name") and c.get("id"):
                name_to_id[str(c["name"])] = int(c["id"])

    for c in categories:
        name = c["name"]
        if name in name_to_id:
            continue
        resp = _post(f"{base_url}/electronics/categories/", c)
        if resp is None:
            continue
        if resp.status_code in (200, 201):
            try:
                created = resp.json()
                if isinstance(created, dict) and created.get("id"):
                    name_to_id[name] = int(created["id"])
            except Exception:
                pass

    existing = _get(f"{base_url}/electronics/categories/", [])
    if isinstance(existing, list):
        for c in existing:
            if isinstance(c, dict) and c.get("name") and c.get("id"):
                name_to_id[str(c["name"])] = int(c["id"])
    return name_to_id


def seed_electronics(base_url: str, items: List[dict]) -> int:
    existing = _get(f"{base_url}/electronics/", [])
    existing_names = set()
    if isinstance(existing, list):
        for it in existing:
            if isinstance(it, dict) and it.get("name"):
                existing_names.add(str(it["name"]).strip().lower())

    created = 0
    for it in items:
        name_key = str(it.get("name", "")).strip().lower()
        if not name_key:
            continue
        if name_key in existing_names:
            continue
        resp = _post(f"{base_url}/electronics/", it)
        if resp is None:
            continue
        if resp.status_code in (200, 201):
            created += 1
            existing_names.add(name_key)
    return created


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")

    ping = _get(f"{base_url}/electronics/", None)
    if ping is None:
        print(f"[seed_electronics] Cannot reach electronic-service at {base_url}")
        print("Tip: start docker first, e.g. `docker compose up --build electronic-service`")
        sys.exit(1)

    categories = [
        {"name": "Điện thoại", "description": "Smartphone / feature phone"},
        {"name": "Laptop", "description": "Laptop văn phòng, gaming"},
        {"name": "Tablet", "description": "Máy tính bảng"},
        {"name": "Tai nghe", "description": "Headphone / Earbuds"},
        {"name": "Màn hình", "description": "Màn hình máy tính"},
        {"name": "TV", "description": "Smart TV, TV thường"},
        {"name": "Phụ kiện", "description": "Sạc, cáp, chuột, bàn phím"},
        {"name": "Thiết bị mạng", "description": "Router, modem, wifi mesh"},
    ]
    cat_map = seed_categories(base_url, categories)

    def cid(name: str) -> Optional[int]:
        return cat_map.get(name)

    rnd = random.Random(20260317)

    names = [
        ("iPhone 14", "Apple", "14"),
        ("iPhone 14 Pro", "Apple", "14 Pro"),
        ("Galaxy S23", "Samsung", "S23"),
        ("Galaxy A54", "Samsung", "A54"),
        ("Xiaomi Redmi Note 13", "Xiaomi", "Note 13"),
        ("MacBook Air M2", "Apple", "Air M2"),
        ("MacBook Pro 14", "Apple", "Pro 14"),
        ("Asus TUF Gaming", "Asus", "TUF F15"),
        ("Dell XPS 13", "Dell", "XPS 13"),
        ("iPad 10.9", "Apple", "10th Gen"),
        ("iPad Pro 11", "Apple", "M2"),
        ("Galaxy Tab S9", "Samsung", "Tab S9"),
        ("AirPods Pro 2", "Apple", "Pro 2"),
        ("Sony WH-1000XM5", "Sony", "WH-1000XM5"),
        ("Logitech MX Master 3S", "Logitech", "MX Master 3S"),
        ("LG UltraGear 27\"", "LG", "27GN800"),
        ("Samsung Odyssey G5", "Samsung", "G5"),
        ("Smart TV 55\"", "Sony", "Bravia 55"),
        ("Router Wifi 6", "TP-Link", "Archer AX55"),
        ("Bàn phím cơ", "Keychron", "K2 V2"),
        ("Ổ cứng SSD 1TB", "Samsung", "980 Pro"),
        ("Chuột gaming", "Razer", "DeathAdder V3"),
        ("Tai nghe bluetooth", "Anker", "Soundcore Liberty"),
        ("Màn hình cong 34\"", "Xiaomi", "34 Curved"),
        ("Loa Bluetooth", "JBL", "Charge 5"),
    ]

    items: List[dict] = []
    for base_name, brand, model in names:
        # gán category theo loại sản phẩm
        name_lower = base_name.lower()
        if "iphone" in name_lower or "galaxy" in name_lower or "redmi" in name_lower:
            category_name = "Điện thoại"
        elif "macbook" in name_lower or "gaming" in name_lower or "xps" in name_lower:
            category_name = "Laptop"
        elif "ipad" in name_lower or "tab" in name_lower:
            category_name = "Tablet"
        elif "airpods" in name_lower or "tai nghe" in name_lower or "wh-1000xm5" in name_lower:
            category_name = "Tai nghe"
        elif "màn hình" in name_lower or "ultragear" in name_lower or "odyssey" in name_lower:
            category_name = "Màn hình"
        elif "tv" in name_lower:
            category_name = "TV"
        elif "router" in name_lower or "wifi" in name_lower:
            category_name = "Thiết bị mạng"
        else:
            category_name = "Phụ kiện"

        price = rnd.choice([
            1990000, 2990000, 3990000, 5990000,
            9990000, 14990000, 19990000, 24990000,
        ])
        stock = rnd.randint(0, 30)

        items.append(
            {
                "name": base_name,
                "brand": brand,
                "model": model,
                "price": price,
                "stock": stock,
                "category": cid(category_name),
            }
        )

    created = seed_electronics(base_url, items)
    print(f"[seed_electronics] Categories: {len(cat_map)} | Electronics created: {created} | Target: {base_url}")


if __name__ == "__main__":
    main()

