"""
seeds/seed_all.py - Seed data vào tất cả databases.

Chạy: python seeds/seed_all.py
"""
import os, sys, csv, django, datetime
from pathlib import Path

# ========== SEED PRODUCT DB ==========
def seed_products():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'product_project.settings'
    sys.path.insert(0, str(Path(__file__).parent.parent / 'product-service'))
    django.setup()

    from products.models import Product
    from django.utils import timezone

    PRODUCTS = [
        (1,  "iPhone 15 Pro Max",            "Điện thoại",         29990000, "Chip A17 Pro, camera 48MP titanium, màn hình 6.7\" Super Retina XDR"),
        (2,  "Samsung Galaxy S24 Ultra",      "Điện thoại",         28990000, "AI Galaxy, bút S Pen tích hợp, camera 200MP, Snapdragon 8 Gen 3"),
        (3,  "Xiaomi 14 Pro",                 "Điện thoại",         18990000, "Màn hình LTPO AMOLED 120Hz, Leica optics, Snapdragon 8 Gen 3"),
        (4,  "OPPO Find X7 Pro",              "Điện thoại",         22990000, "Camera Hasselblad, sạc nhanh 100W, màn hình AMOLED 120Hz"),
        (5,  "Realme GT 5 Pro",               "Điện thoại",         12990000, "Sạc siêu nhanh 240W, Snapdragon 8 Gen 3, pin 5400mAh"),
        (6,  "MacBook Air M3",                "Laptop",             32990000, "Chip Apple M3, màn hình Liquid Retina 13.6\", pin 18 giờ"),
        (7,  "Dell XPS 15",                   "Laptop",             42990000, "Màn hình OLED 4K touch, RTX 4060, Core i9, 32GB RAM"),
        (8,  "Lenovo ThinkPad X1 Carbon",     "Laptop",             38990000, "Chuẩn MIL-SPEC, Core i7 thế hệ 13, 16GB RAM"),
        (9,  "ASUS ZenBook 14 OLED",          "Laptop",             22990000, "Màn hình OLED 2.8K 120Hz, Intel Core Ultra 7"),
        (10, "HP Spectre x360 14",            "Laptop",             35990000, "2-in-1 OLED cảm ứng, Core i7-1355U"),
        (11, "iPad Pro M4 12.9 inch",         "Máy tính bảng",      28990000, "Chip M4, màn hình Liquid Retina XDR, Apple Pencil Pro"),
        (12, "Samsung Galaxy Tab S9 Ultra",   "Máy tính bảng",      26990000, "AMOLED 14.6\", Snapdragon 8 Gen 2, kèm S Pen, IP68"),
        (13, "Lenovo Tab P12 Pro",            "Máy tính bảng",      15990000, "AMOLED 12.6\" 120Hz, loa JBL 4 loa"),
        (14, "AirPods Pro 2",                 "Tai nghe",            6490000, "Chip H2, ANC thế hệ 2, âm thanh không gian"),
        (15, "Sony WH-1000XM5",              "Tai nghe",            8490000, "ANC tốt nhất, pin 30 giờ, multipoint 2 thiết bị"),
        (16, "Samsung Galaxy Buds 2 Pro",    "Tai nghe",            4490000, "ANC thích ứng, Hi-Fi 24bit, IPX7"),
        (17, "Apple Watch Series 9",         "Đồng hồ thông minh", 10990000, "Chip S9, Double Tap, màn hình luôn bật"),
        (18, "Samsung Galaxy Watch 6 Classic","Đồng hồ thông minh",  7990000, "Vòng xoay cơ bezel, BioActive Sensor"),
        (19, "Garmin Venu 3",                "Đồng hồ thông minh",  9490000, "GPS, pin 14 ngày, theo dõi sức khỏe toàn diện"),
        (20, "Sony PlayStation 5",           "Gaming",             13990000, "SSD NVMe, ray tracing, DualSense haptic, 4K 120fps"),
        (21, "Nintendo Switch OLED",         "Gaming",              8990000, "Màn hình OLED 7\", chế độ handheld/TV/tabletop"),
        (22, "Logitech MX Keys S",           "Phụ kiện",            2890000, "Bàn phím wireless, backlight thích ứng, kết nối 3 thiết bị"),
        (23, "Logitech MX Master 3S",        "Phụ kiện",            2490000, "Chuột flagship, cuộn MagSpeed, 8000 DPI"),
        (24, "Màn hình Dell 27 inch 4K",     "Phụ kiện",           18990000, "IPS 4K UHD, sRGB 99%, USB-C 90W"),
        (25, "SSD Samsung 990 Pro 2TB",      "Lưu trữ",             4990000, "NVMe PCIe 4.0, đọc 7450MB/s"),
        (26, "GPU NVIDIA RTX 4070 Super",    "Linh kiện PC",       18990000, "DLSS 3, ray tracing, 12GB GDDR6X"),
        (27, "RAM Corsair Vengeance 32GB DDR5","Linh kiện PC",       3490000, "DDR5 6000MHz, Intel XMP 3.0"),
        (28, "Bàn phím cơ Keychron Q3",     "Phụ kiện",            3990000, "TKL nhôm, gasket mount, Gateron G Pro, hot-swap"),
        (29, "Webcam Logitech Brio 4K",      "Phụ kiện",            4490000, "4K Ultra HD, HDR, autofocus"),
        (30, "Loa Bluetooth JBL Charge 5",   "Âm thanh",            3990000, "IP67, pin 20 giờ, sạc thiết bị khác"),
    ]

    print("\n📦 [product-service] Seeding 30 sản phẩm...")
    for pid, name, cat, price, desc in PRODUCTS:
        Product.objects.update_or_create(
            id=pid,
            defaults={
                'name': name, 'category': cat, 'price': price,
                'description': desc,
                'image_url': f'https://picsum.photos/seed/product{pid}/400/300'
            }
        )
    print(f"  ✅ {Product.objects.count()} sản phẩm trong product_db")


# ========== SEED BEHAVIOR DB ==========
def seed_behaviors():
    # Reset Django apps cho service khác
    import importlib
    for key in list(sys.modules.keys()):
        if 'django' in key or 'product' in key or 'behavior' in key:
            del sys.modules[key]

    os.environ['DJANGO_SETTINGS_MODULE'] = 'behavior_project.settings'
    sys.path.insert(0, str(Path(__file__).parent.parent / 'behavior-service'))

    import django as _django
    _django.setup()

    from behaviors.models import UserBehavior, UserProfile

    # Seed user profiles
    import random
    FIRST = ['An', 'Bảo', 'Chi', 'Dũng', 'Phú', 'Giang', 'Hải', 'Khoa', 'Lan', 'Minh', 'Nam', 'Oanh', 'Phương', 'Quân', 'Sơn', 'Uyên', 'Vân', 'Xuân']
    LAST  = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Đặng', 'Bùi', 'Hồ', 'Ngô', 'Dương']

    print("\n👤 [behavior-service] Seeding 500 user profiles...")
    for uid in range(1, 501):
        UserProfile.objects.get_or_create(
            id=uid,
            defaults={'name': f"{random.choice(LAST)} {random.choice(FIRST)} {uid}", 'email': f"user{uid}@ecom.vn"}
        )
    print(f"  ✅ {UserProfile.objects.count()} users trong behavior_db")

    # Import behaviors từ CSV
    csv_path = Path(__file__).parent / 'data_user500.csv'
    if not csv_path.exists():
        print(f"  ⚠️  Không tìm thấy CSV: {csv_path}")
        return

    print(f"\n📋 [behavior-service] Import behaviors từ CSV...")
    UserBehavior.objects.all().delete()

    from django.utils import timezone
    rows = []
    with open(csv_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                ts = datetime.datetime.strptime(row['timestamp'].strip(), '%Y-%m-%d %H:%M:%S')
                ts = timezone.make_aware(ts, datetime.timezone.utc)
                pid = int(row['product_id'])
                if 1 <= pid <= 30:
                    rows.append(UserBehavior(
                        user_id=int(row['user_id']),
                        product_id=pid,
                        action=row['action'].strip(),
                        timestamp=ts
                    ))
            except Exception:
                continue

    UserBehavior.objects.bulk_create(rows, batch_size=500)
    print(f"  ✅ {len(rows)} behaviors trong behavior_db")


if __name__ == '__main__':
    print("=" * 55)
    print("🚀 SEED DATA CHO MICROSERVICES")
    print("=" * 55)
    print("⚠️  Chạy lần lượt: product-service trước, rồi behavior-service")
    print()
    print("Vui lòng chạy từng script riêng:")
    print("  python seeds/seed_products.py")
    print("  python seeds/seed_behaviors.py")
    print("=" * 55)
