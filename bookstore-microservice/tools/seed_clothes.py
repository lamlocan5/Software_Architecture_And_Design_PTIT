import random
import sys
from typing import Dict, List, Optional

import requests


DEFAULT_BASE_URL = "http://localhost:8012"  # host -> docker-compose port for clothe-service


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
    """
    Returns mapping: category_name -> category_id
    """
    existing = _get(f"{base_url}/clothes/categories/", [])
    name_to_id: Dict[str, int] = {}
    if isinstance(existing, list):
        for c in existing:
            if isinstance(c, dict) and c.get("name") and c.get("id"):
                name_to_id[str(c["name"])] = int(c["id"])

    for c in categories:
        name = c["name"]
        if name in name_to_id:
            continue
        resp = _post(f"{base_url}/clothes/categories/", c)
        if resp is None:
            continue
        if resp.status_code in (200, 201):
            try:
                created = resp.json()
                if isinstance(created, dict) and created.get("id"):
                    name_to_id[name] = int(created["id"])
            except Exception:
                pass

    # refresh once
    existing = _get(f"{base_url}/clothes/categories/", [])
    if isinstance(existing, list):
        for c in existing:
            if isinstance(c, dict) and c.get("name") and c.get("id"):
                name_to_id[str(c["name"])] = int(c["id"])
    return name_to_id


def seed_clothes(base_url: str, items: List[dict]) -> int:
    existing = _get(f"{base_url}/clothes/", [])
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
        resp = _post(f"{base_url}/clothes/", it)
        if resp is None:
            continue
        if resp.status_code in (200, 201):
            created += 1
            existing_names.add(name_key)
    return created


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")

    # quick connectivity check
    ping = _get(f"{base_url}/clothes/", None)
    if ping is None:
        print(f"[seed_clothes] Cannot reach clothe-service at {base_url}")
        print("Tip: start docker first, e.g. `docker-compose up --build clothe-service`")
        sys.exit(1)

    categories = [
        {"name": "Áo thun", "description": "T-shirt / áo thun casual"},
        {"name": "Áo sơ mi", "description": "Áo sơ mi công sở"},
        {"name": "Áo khoác", "description": "Jacket / áo khoác"},
        {"name": "Quần jean", "description": "Denim / quần bò"},
        {"name": "Quần tây", "description": "Quần tây / chinos"},
        {"name": "Váy", "description": "Váy thời trang"},
        {"name": "Đầm", "description": "Đầm dự tiệc / công sở"},
        {"name": "Đồ thể thao", "description": "Activewear"},
    ]
    cat_map = seed_categories(base_url, categories)

    def cid(name: str) -> Optional[int]:
        return cat_map.get(name)

    rnd = random.Random(20260317)

    names = [
        ("Áo thun basic", "Áo thun", ["S", "M", "L", "XL"], ["Trắng", "Đen", "Xám"]),
        ("Áo thun oversize", "Áo thun", ["M", "L", "XL"], ["Đen", "Kem", "Navy"]),
        ("Áo thun thể thao", "Đồ thể thao", ["S", "M", "L"], ["Đỏ", "Xanh", "Đen"]),
        ("Áo sơ mi trắng", "Áo sơ mi", ["S", "M", "L", "XL"], ["Trắng"]),
        ("Áo sơ mi kẻ sọc", "Áo sơ mi", ["M", "L", "XL"], ["Xanh", "Đen"]),
        ("Áo khoác gió", "Áo khoác", ["M", "L", "XL"], ["Đen", "Xanh rêu"]),
        ("Áo khoác denim", "Áo khoác", ["M", "L"], ["Xanh denim"]),
        ("Quần jean slimfit", "Quần jean", ["28", "29", "30", "31", "32"], ["Xanh", "Đen"]),
        ("Quần jean ống rộng", "Quần jean", ["28", "30", "32"], ["Xanh nhạt", "Xanh đậm"]),
        ("Quần tây công sở", "Quần tây", ["29", "30", "31", "32"], ["Đen", "Xám", "Navy"]),
        ("Quần chinos", "Quần tây", ["29", "30", "31", "32"], ["Be", "Nâu", "Đen"]),
        ("Váy hoa nhí", "Váy", ["S", "M", "L"], ["Hồng", "Trắng"]),
        ("Váy chữ A", "Váy", ["S", "M", "L"], ["Đen", "Be"]),
        ("Đầm body", "Đầm", ["S", "M", "L"], ["Đỏ đô", "Đen"]),
        ("Đầm maxi", "Đầm", ["S", "M", "L"], ["Trắng", "Xanh biển"]),
        ("Set đồ tập yoga", "Đồ thể thao", ["S", "M", "L"], ["Đen", "Tím"]),
        ("Áo hoodie", "Áo khoác", ["M", "L", "XL"], ["Đen", "Xám", "Kem"]),
        ("Áo cardigan", "Áo khoác", ["M", "L"], ["Be", "Nâu"]),
        ("Áo polo", "Áo thun", ["S", "M", "L", "XL"], ["Trắng", "Xanh navy"]),
        ("Quần short thể thao", "Đồ thể thao", ["S", "M", "L"], ["Đen", "Xám"]),
        ("Quần short jean", "Quần jean", ["28", "29", "30", "31"], ["Xanh"]),
        ("Áo sơ mi denim", "Áo sơ mi", ["M", "L", "XL"], ["Xanh denim"]),
        ("Áo thun in hình", "Áo thun", ["S", "M", "L"], ["Trắng", "Đen"]),
        ("Quần tây lưng cao", "Quần tây", ["S", "M", "L"], ["Đen", "Kem"]),
        ("Váy xếp ly", "Váy", ["S", "M", "L"], ["Đen", "Trắng"]),
    ]

    items: List[dict] = []
    for base_name, cat_name, sizes, colors in names:
        size = rnd.choice(sizes)
        color = rnd.choice(colors)
        price = rnd.choice([99000, 149000, 199000, 249000, 299000, 349000, 399000])
        stock = rnd.randint(0, 50)
        items.append(
            {
                "name": f"{base_name} ({color})",
                "size": str(size),
                "color": color,
                "price": price,
                "stock": stock,
                "category": cid(cat_name),
            }
        )

    created = seed_clothes(base_url, items)
    print(f"[seed_clothes] Categories: {len(cat_map)} | Clothes created: {created} | Target: {base_url}")


if __name__ == "__main__":
    main()

