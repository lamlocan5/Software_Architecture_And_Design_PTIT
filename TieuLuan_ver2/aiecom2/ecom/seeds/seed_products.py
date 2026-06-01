"""
seeds/seed_products.py - Seed product_db cho product-service
Chạy từ thư mục ecom/:  python seeds/seed_products.py
"""
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'product-service'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'product_project.settings'

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / 'product-service' / '.env')

import django
django.setup()

from products.models import Product

PRODUCTS = [
    (1,"iPhone 15 Pro Max","Điện thoại",29990000,"Chip A17 Pro, camera 48MP titanium, màn hình 6.7\" Super Retina XDR"),
    (2,"Samsung Galaxy S24 Ultra","Điện thoại",28990000,"AI Galaxy, bút S Pen tích hợp, camera 200MP"),
    (3,"Xiaomi 14 Pro","Điện thoại",18990000,"Màn hình LTPO AMOLED 120Hz, Leica optics"),
    (4,"OPPO Find X7 Pro","Điện thoại",22990000,"Camera Hasselblad, sạc nhanh 100W"),
    (5,"Realme GT 5 Pro","Điện thoại",12990000,"Sạc siêu nhanh 240W, Snapdragon 8 Gen 3"),
    (6,"MacBook Air M3","Laptop",32990000,"Chip Apple M3, màn hình Liquid Retina 13.6\", pin 18 giờ"),
    (7,"Dell XPS 15","Laptop",42990000,"Màn hình OLED 4K touch, RTX 4060, Core i9"),
    (8,"Lenovo ThinkPad X1 Carbon","Laptop",38990000,"Chuẩn MIL-SPEC, Core i7 thế hệ 13, 16GB RAM"),
    (9,"ASUS ZenBook 14 OLED","Laptop",22990000,"Màn hình OLED 2.8K 120Hz, Intel Core Ultra 7"),
    (10,"HP Spectre x360 14","Laptop",35990000,"2-in-1 OLED cảm ứng, Core i7-1355U"),
    (11,"iPad Pro M4 12.9 inch","Máy tính bảng",28990000,"Chip M4, màn hình Liquid Retina XDR"),
    (12,"Samsung Galaxy Tab S9 Ultra","Máy tính bảng",26990000,"AMOLED 14.6\", Snapdragon 8 Gen 2, kèm S Pen"),
    (13,"Lenovo Tab P12 Pro","Máy tính bảng",15990000,"AMOLED 12.6\" 120Hz, loa JBL 4 loa"),
    (14,"AirPods Pro 2","Tai nghe",6490000,"Chip H2, ANC thế hệ 2, âm thanh không gian"),
    (15,"Sony WH-1000XM5","Tai nghe",8490000,"ANC tốt nhất, pin 30 giờ, multipoint"),
    (16,"Samsung Galaxy Buds 2 Pro","Tai nghe",4490000,"ANC thích ứng, Hi-Fi 24bit, IPX7"),
    (17,"Apple Watch Series 9","Đồng hồ thông minh",10990000,"Chip S9, Double Tap, màn hình luôn bật"),
    (18,"Samsung Galaxy Watch 6 Classic","Đồng hồ thông minh",7990000,"Vòng xoay cơ bezel, BioActive Sensor"),
    (19,"Garmin Venu 3","Đồng hồ thông minh",9490000,"GPS, pin 14 ngày, theo dõi sức khỏe"),
    (20,"Sony PlayStation 5","Gaming",13990000,"SSD NVMe, ray tracing, DualSense haptic"),
    (21,"Nintendo Switch OLED","Gaming",8990000,"Màn hình OLED 7\", handheld/TV/tabletop"),
    (22,"Logitech MX Keys S","Phụ kiện",2890000,"Bàn phím wireless, backlight, 3 thiết bị"),
    (23,"Logitech MX Master 3S","Phụ kiện",2490000,"Chuột flagship, MagSpeed, 8000 DPI"),
    (24,"Màn hình Dell 27 inch 4K","Phụ kiện",18990000,"IPS 4K UHD, sRGB 99%, USB-C 90W"),
    (25,"SSD Samsung 990 Pro 2TB","Lưu trữ",4990000,"NVMe PCIe 4.0, đọc 7450MB/s"),
    (26,"GPU NVIDIA RTX 4070 Super","Linh kiện PC",18990000,"DLSS 3, ray tracing, 12GB GDDR6X"),
    (27,"RAM Corsair Vengeance 32GB DDR5","Linh kiện PC",3490000,"DDR5 6000MHz, Intel XMP 3.0"),
    (28,"Bàn phím cơ Keychron Q3","Phụ kiện",3990000,"TKL nhôm, gasket mount, hot-swap, RGB"),
    (29,"Webcam Logitech Brio 4K","Phụ kiện",4490000,"4K Ultra HD, HDR, autofocus"),
    (30,"Loa Bluetooth JBL Charge 5","Âm thanh",3990000,"IP67, pin 20 giờ, sạc thiết bị khác"),
]

print("Seeding product_db (product-service)...")
for pid, name, cat, price, desc in PRODUCTS:
    Product.objects.update_or_create(
        id=pid,
        defaults={
            'name': name, 'category': cat, 'price': price,
            'description': desc,
            'image_url': f'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&q=80&w=400&h=300' # Default tech
        }
    )
    
    # Gán ảnh cụ thể theo từ khóa để trông thật hơn
    keywords = {
        "iPhone": "iphone,smartphone",
        "Samsung": "samsung,phone",
        "MacBook": "laptop,macbook",
        "Dell": "laptop,computer",
        "iPad": "tablet",
        "Sony": "headphones",
        "Watch": "smartwatch",
        "PlayStation": "gaming,console",
        "Logitech": "mouse,keyboard",
        "Màn hình": "monitor",
        "SSD": "hardware",
        "GPU": "gpu,pc",
        "RAM": "ram,memory",
        "Bàn phím": "keyboard",
        "Webcam": "camera",
        "Loa": "speaker"
    }
    
    keyword = "tech"
    for k, v in keywords.items():
        if k.lower() in name.lower():
            keyword = v
            break
            
    img_url = f"https://loremflickr.com/400/300/{keyword}?lock={pid}"
    Product.objects.filter(id=pid).update(image_url=img_url)
print(f"Done: Seeded {Product.objects.count()} products into product_db")
