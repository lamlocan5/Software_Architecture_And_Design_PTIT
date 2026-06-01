"""
KB Seeder — Nhồi toàn bộ dữ liệu vào ChromaDB
"""
import os
import sys

# Đảm bảo thư mục gốc của project (/app) trong sys.path
# để Python tìm được module 'config' dù script chạy từ thư mục api/
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.chroma_client import get_laptop_collection, get_mobile_collection, get_advisory_collection
from api.kb_laptops import LAPTOPS
from api.kb_mobiles import MOBILES
from api.kb_advisory import ADVISORY_DOCS


def format_laptop_doc(l: dict) -> str:
    price_m = l['price_vnd'] / 1_000_000
    return (
        f"Laptop: {l['name']}. "
        f"Thương hiệu: {l['brand']}. "
        f"Giá: {price_m:.1f} triệu đồng. "
        f"CPU: {l['cpu']}. "
        f"RAM: {l['ram_gb']}GB. "
        f"Bộ nhớ: {l['storage_gb']}GB SSD. "
        f"GPU: {l['gpu']}. "
        f"Màn hình: {l['display']}. "
        f"Pin: {l['battery_h']} giờ. "
        f"Cân nặng: {l['weight_kg']}kg. "
        f"Hệ điều hành: {l['os']}. "
        f"Phù hợp cho: {', '.join(l['use_cases'])}. "
        f"Điểm nổi bật: {l['highlights']}."
    )


def format_mobile_doc(m: dict) -> str:
    price_m = m['price_vnd'] / 1_000_000
    return (
        f"Điện thoại: {m['name']}. "
        f"Thương hiệu: {m['brand']}. "
        f"Giá: {price_m:.1f} triệu đồng. "
        f"Chip: {m['chip']}. "
        f"RAM: {m['ram_gb']}GB. "
        f"Bộ nhớ: {m['storage_gb']}GB. "
        f"Pin: {m['battery_mah']}mAh. "
        f"Màn hình: {m['display']}. "
        f"Camera: {m['camera_mp']}. "
        f"Hệ điều hành: {m['os']}. "
        f"Phù hợp cho: {', '.join(m['use_cases'])}. "
        f"Điểm nổi bật: {m['highlights']}."
    )


def seed_laptops():
    col = get_laptop_collection()
    existing = set(col.get()['ids'])
    new_docs = [l for l in LAPTOPS if l['id'] not in existing]
    if not new_docs:
        print(f"✅ Laptop KB đã có {len(existing)} docs, không cần seed lại.")
        return
    col.add(
        documents=[format_laptop_doc(l) for l in new_docs],
        ids=[l['id'] for l in new_docs],
        metadatas=[{
            'brand': l['brand'],
            'price_vnd': l['price_vnd'],
            'type': 'laptop',
            'use_cases': ','.join(l['use_cases']),
            'ram_gb': l['ram_gb'],
            'has_gpu': 'RTX' in l['gpu'] or 'GTX' in l['gpu'] or 'AMD RX' in l['gpu'],
        } for l in new_docs]
    )
    print(f"✅ Seeded {len(new_docs)} laptop docs vào ChromaDB.")


def seed_mobiles():
    col = get_mobile_collection()
    existing = set(col.get()['ids'])
    new_docs = [m for m in MOBILES if m['id'] not in existing]
    if not new_docs:
        print(f"✅ Mobile KB đã có {len(existing)} docs, không cần seed lại.")
        return
    col.add(
        documents=[format_mobile_doc(m) for m in new_docs],
        ids=[m['id'] for m in new_docs],
        metadatas=[{
            'brand': m['brand'],
            'price_vnd': m['price_vnd'],
            'type': 'mobile',
            'use_cases': ','.join(m['use_cases']),
            'ram_gb': m['ram_gb'],
        } for m in new_docs]
    )
    print(f"✅ Seeded {len(new_docs)} mobile docs vào ChromaDB.")


def seed_advisory():
    col = get_advisory_collection()
    existing = set(col.get()['ids'])
    new_docs = [d for d in ADVISORY_DOCS if d['id'] not in existing]
    if not new_docs:
        print(f"✅ Advisory KB đã có {len(existing)} docs, không cần seed lại.")
        return
    col.add(
        documents=[d['content'] for d in new_docs],
        ids=[d['id'] for d in new_docs],
        metadatas=[{
            'title': d['title'],
            'category': d['category'],
        } for d in new_docs]
    )
    print(f"✅ Seeded {len(new_docs)} advisory docs vào ChromaDB.")


def seed_all():
    print("🚀 Bắt đầu seed Knowledge Base...")
    seed_laptops()
    seed_mobiles()
    seed_advisory()
    print("🎉 Hoàn tất seed KB!")
    print(f"   📊 Stats: {len(LAPTOPS)} laptops | {len(MOBILES)} mobiles | {len(ADVISORY_DOCS)} advisory docs")


if __name__ == '__main__':
    seed_all()
