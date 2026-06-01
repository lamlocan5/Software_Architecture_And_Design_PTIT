import requests
import time

BASE_URL = "http://localhost:8000/api"

LAPTOPS = [
    {"model_name": "Apple MacBook Air M1", "cpu": "Apple M1 8-core", "ram_gb": 8, "storage_gb": 256, "price": 699.00},
    {"model_name": "Apple MacBook Air M2", "cpu": "Apple M2 8-core", "ram_gb": 8, "storage_gb": 256, "price": 899.00},
    {"model_name": "Apple MacBook Air M3", "cpu": "Apple M3 8-core", "ram_gb": 8, "storage_gb": 256, "price": 1099.00},
    {"model_name": "Apple MacBook Pro M3 14 inch", "cpu": "Apple M3 Pro 11-core", "ram_gb": 18, "storage_gb": 512, "price": 1799.00},
    {"model_name": "Apple MacBook Pro M4 14 inch", "cpu": "Apple M4 Pro 12-core", "ram_gb": 24, "storage_gb": 512, "price": 1999.00},
    {"model_name": "Dell XPS 13 Plus i7", "cpu": "Intel Core Ultra 7 155H", "ram_gb": 16, "storage_gb": 512, "price": 1499.00},
    {"model_name": "Dell XPS 15 RTX 4060", "cpu": "Intel Core i7-13700H", "ram_gb": 16, "storage_gb": 512, "price": 1750.00},
    {"model_name": "Dell Inspiron 15 i5", "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "price": 549.00},
    {"model_name": "Dell Alienware m16 RTX 4090", "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "price": 3299.00},
    {"model_name": "Dell G15 RTX 4060", "cpu": "Intel Core i7-13650HX", "ram_gb": 16, "storage_gb": 512, "price": 1149.00},
    {"model_name": "HP Spectre x360 14 OLED", "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "price": 1699.00},
    {"model_name": "HP Pavilion 15 i5", "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "price": 599.00},
    {"model_name": "HP Omen 16 RTX 4070", "cpu": "Intel Core i9-13900HX", "ram_gb": 16, "storage_gb": 1024, "price": 1999.00},
    {"model_name": "HP EliteBook 840 G10", "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "price": 1399.00},
    {"model_name": "HP Victus 15 RTX 3050", "cpu": "Intel Core i5-12450H", "ram_gb": 8, "storage_gb": 512, "price": 699.00},
    {"model_name": "Lenovo ThinkPad X1 Carbon Gen 12", "cpu": "Intel Core i7-1365U", "ram_gb": 16, "storage_gb": 512, "price": 1899.00},
    {"model_name": "Lenovo IdeaPad Slim 5 i5", "cpu": "Intel Core i5-13420H", "ram_gb": 16, "storage_gb": 512, "price": 649.00},
    {"model_name": "Lenovo Legion 5 Pro RTX 4060", "cpu": "AMD Ryzen 7 7745HX", "ram_gb": 16, "storage_gb": 512, "price": 1399.00},
    {"model_name": "Lenovo Legion 7 RTX 4070 Ti", "cpu": "Intel Core i9-13900HX", "ram_gb": 32, "storage_gb": 1024, "price": 2299.00},
    {"model_name": "Lenovo Yoga 9i 14 OLED 2-in-1", "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 512, "price": 1599.00},
    {"model_name": "Lenovo Legion Pro 7 RTX 4090", "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "price": 3599.00},
    {"model_name": "ASUS ROG Strix G16 RTX 4080", "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "price": 2999.00},
    {"model_name": "ASUS TUF Gaming F15 RTX 4060", "cpu": "Intel Core i7-13700H", "ram_gb": 16, "storage_gb": 512, "price": 1099.00},
    {"model_name": "ASUS ZenBook 14 OLED", "cpu": "Intel Core Ultra 7 155H", "ram_gb": 16, "storage_gb": 512, "price": 999.00},
    {"model_name": "ASUS VivoBook 15 i5", "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "price": 499.00},
    {"model_name": "ASUS ROG Zephyrus G14 RTX 4060", "cpu": "AMD Ryzen 9 7940HS", "ram_gb": 16, "storage_gb": 1024, "price": 1699.00},
    {"model_name": "Acer Predator Helios 16 RTX 4080", "cpu": "Intel Core i9-13900HX", "ram_gb": 32, "storage_gb": 1024, "price": 2699.00},
    {"model_name": "Acer Nitro V 15 RTX 4060", "cpu": "Intel Core i5-13420H", "ram_gb": 8, "storage_gb": 512, "price": 899.00},
    {"model_name": "Acer Swift Go 14 OLED", "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "price": 799.00},
    {"model_name": "Acer Aspire 5 i5", "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 256, "price": 449.00},
    {"model_name": "MSI Titan GT77 RTX 4090", "cpu": "Intel Core i9-13980HX", "ram_gb": 64, "storage_gb": 2048, "price": 3999.00},
    {"model_name": "MSI Modern 14 Ryzen 5", "cpu": "AMD Ryzen 5 7530U", "ram_gb": 8, "storage_gb": 512, "price": 599.00},
    {"model_name": "MSI Stealth 16 Studio RTX 4070", "cpu": "Intel Core i9-13900H", "ram_gb": 32, "storage_gb": 1024, "price": 2399.00},
    {"model_name": "Samsung Galaxy Book4 Ultra RTX 4070", "cpu": "Intel Core i9-14900H", "ram_gb": 32, "storage_gb": 1024, "price": 2599.00},
    {"model_name": "LG Gram 14 2024 Intel Evo", "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 512, "price": 1199.00},
    {"model_name": "LG Gram 17 2024 Ultra", "cpu": "Intel Core Ultra 7 155H", "ram_gb": 32, "storage_gb": 1024, "price": 1599.00},
    {"model_name": "Huawei MateBook X Pro 2024", "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 1024, "price": 1499.00},
    {"model_name": "Microsoft Surface Laptop 6", "cpu": "Intel Core i7-1365U", "ram_gb": 16, "storage_gb": 512, "price": 1699.00},
    {"model_name": "Razer Blade 16 RTX 4090", "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 2048, "price": 3999.00},
    {"model_name": "Xiaomi Book Pro 16 OLED RTX 4060", "cpu": "Intel Core i9-13900H", "ram_gb": 32, "storage_gb": 1024, "price": 1399.00},
]

MOBILES = [
    {"model_name": "iPhone 15 Pro Max", "chipset": "Apple A17 Pro", "storage_gb": 256, "price": 1199.00},
    {"model_name": "iPhone 15 Pro", "chipset": "Apple A17 Pro", "storage_gb": 128, "price": 999.00},
    {"model_name": "iPhone 15", "chipset": "Apple A16 Bionic", "storage_gb": 128, "price": 799.00},
    {"model_name": "iPhone 14", "chipset": "Apple A15 Bionic", "storage_gb": 128, "price": 599.00},
    {"model_name": "iPhone SE 3rd Gen", "chipset": "Apple A15 Bionic", "storage_gb": 64, "price": 429.00},
    {"model_name": "Samsung Galaxy S24 Ultra", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 1299.00},
    {"model_name": "Samsung Galaxy S24+", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 999.00},
    {"model_name": "Samsung Galaxy S24", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 128, "price": 799.00},
    {"model_name": "Samsung Galaxy A55", "chipset": "Exynos 1480", "storage_gb": 128, "price": 449.00},
    {"model_name": "Samsung Galaxy A35", "chipset": "Exynos 1380", "storage_gb": 128, "price": 349.00},
    {"model_name": "Samsung Galaxy A15", "chipset": "Helio G99", "storage_gb": 128, "price": 199.00},
    {"model_name": "Xiaomi 14 Ultra", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 1099.00},
    {"model_name": "Xiaomi 14", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 799.00},
    {"model_name": "Xiaomi 13T Pro", "chipset": "Dimensity 9200+", "storage_gb": 256, "price": 649.00},
    {"model_name": "Xiaomi Redmi Note 13 Pro+", "chipset": "Dimensity 7200 Ultra", "storage_gb": 256, "price": 399.00},
    {"model_name": "Xiaomi Redmi Note 13", "chipset": "Snapdragon 685", "storage_gb": 128, "price": 199.00},
    {"model_name": "OPPO Find X7 Ultra", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 999.00},
    {"model_name": "OPPO Reno 11 Pro", "chipset": "Dimensity 8200", "storage_gb": 256, "price": 549.00},
    {"model_name": "OPPO Reno 11", "chipset": "Dimensity 6080", "storage_gb": 128, "price": 349.00},
    {"model_name": "OPPO A79", "chipset": "Dimensity 6020", "storage_gb": 128, "price": 249.00},
    {"model_name": "Vivo X100 Pro", "chipset": "Dimensity 9300", "storage_gb": 256, "price": 899.00},
    {"model_name": "Vivo V30 Pro", "chipset": "Snapdragon 7 Gen 3", "storage_gb": 256, "price": 549.00},
    {"model_name": "Vivo V30e", "chipset": "Snapdragon 6 Gen 1", "storage_gb": 128, "price": 349.00},
    {"model_name": "Realme GT 5 Pro", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 699.00},
    {"model_name": "Realme 12 Pro+", "chipset": "Snapdragon 7s Gen 2", "storage_gb": 256, "price": 399.00},
    {"model_name": "Google Pixel 8 Pro", "chipset": "Google Tensor G3", "storage_gb": 128, "price": 999.00},
    {"model_name": "Google Pixel 8a", "chipset": "Google Tensor G3", "storage_gb": 128, "price": 499.00},
    {"model_name": "OnePlus 12", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 799.00},
    {"model_name": "OnePlus 12R", "chipset": "Snapdragon 8 Gen 1", "storage_gb": 128, "price": 499.00},
    {"model_name": "Nokia G42 5G", "chipset": "Snapdragon 480+", "storage_gb": 128, "price": 249.00},
    {"model_name": "Sony Xperia 1 VI", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 1299.00},
    {"model_name": "Motorola Edge 50 Pro", "chipset": "Snapdragon 7 Gen 3", "storage_gb": 256, "price": 499.00},
    {"model_name": "Nothing Phone 2a", "chipset": "Dimensity 7200 Pro", "storage_gb": 128, "price": 349.00},
    {"model_name": "Huawei Pura 70 Pro", "chipset": "Kirin 9010", "storage_gb": 256, "price": 899.00},
    {"model_name": "Asus ROG Phone 8 Pro", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 512, "price": 1099.00},
]

STAFFS = [
    {"full_name": "Alice Admin", "position": "Manager", "email": "alice@techstore.com", "username": "admin_alice", "password": "password123"},
    {"full_name": "Bob Staff", "position": "Sales", "email": "bob@techstore.com", "username": "staff_bob", "password": "password123"},
    {"full_name": "Carol Tech", "position": "Tech Support", "email": "carol@techstore.com", "username": "staff_carol", "password": "password123"},
]

CUSTOMERS = [
    {"full_name": "Charlie Nguyen", "phone": "0901234567", "email": "charlie@gmail.com", "username": "charlie_ng", "password": "password123"},
    {"full_name": "Dave Tran", "phone": "0912345678", "email": "dave@gmail.com", "username": "dave_tr", "password": "password123"},
    {"full_name": "Eva Le", "phone": "0923456789", "email": "eva@gmail.com", "username": "eva_le", "password": "password123"},
    {"full_name": "Frank Pham", "phone": "0934567890", "email": "frank@gmail.com", "username": "frank_ph", "password": "password123"},
]

def seed_laptops():
    print("\n📦 Seeding Laptops...")
    ok, fail = 0, 0
    for item in LAPTOPS:
        try:
            r = requests.post(f"{BASE_URL}/laptop/products/create/", json=item, timeout=10)
            if r.status_code == 201:
                print(f"  ✅ {item['model_name']}")
                ok += 1
            elif r.status_code == 400 and 'already' in r.text.lower():
                print(f"  ⏭  {item['model_name']} (đã tồn tại)")
            else:
                print(f"  ❌ {item['model_name']}: {r.status_code}")
                fail += 1
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Gateway không reachable. Docker đang chạy không?")
            return
    print(f"  → {ok} thành công, {fail} thất bại / {len(LAPTOPS)} laptops")

def seed_mobiles():
    print("\n📱 Seeding Mobiles...")
    ok, fail = 0, 0
    for item in MOBILES:
        try:
            r = requests.post(f"{BASE_URL}/moblie/products/create/", json=item, timeout=10)
            if r.status_code == 201:
                print(f"  ✅ {item['model_name']}")
                ok += 1
            elif r.status_code == 400 and 'already' in r.text.lower():
                print(f"  ⏭  {item['model_name']} (đã tồn tại)")
            else:
                print(f"  ❌ {item['model_name']}: {r.status_code}")
                fail += 1
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Gateway không reachable.")
            return
    print(f"  → {ok} thành công, {fail} thất bại / {len(MOBILES)} mobiles")

def seed_staffs():
    print("\n👔 Seeding Staffs...")
    for item in STAFFS:
        try:
            r = requests.post(f"{BASE_URL}/staff/register/", json=item, timeout=10)
            if r.status_code == 201:
                print(f"  ✅ {item['username']}")
            else:
                print(f"  ⏭  {item['username']}: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Gateway không reachable.")
            return

def seed_customers():
    print("\n👤 Seeding Customers...")
    for item in CUSTOMERS:
        try:
            r = requests.post(f"{BASE_URL}/customer/register/", json=item, timeout=10)
            if r.status_code == 201:
                print(f"  ✅ {item['username']}")
            else:
                print(f"  ⏭  {item['username']}: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print("  ⚠️  Gateway không reachable.")
            return

def seed_data():
    print("🚀 Bắt đầu seed data...")
    print(f"   Target: {BASE_URL}")
    seed_staffs()
    seed_customers()
    seed_laptops()
    seed_mobiles()
    print("\n🎉 Hoàn tất! Tổng cộng:")
    print(f"   💻 {len(LAPTOPS)} laptops | 📱 {len(MOBILES)} mobiles")
    print(f"   👔 {len(STAFFS)} staffs | 👤 {len(CUSTOMERS)} customers")

if __name__ == "__main__":
    seed_data()
