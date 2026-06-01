"""
Seed Data Script — Thêm dữ liệu mẫu vào hệ thống
Chạy lệnh: python seed_data.py
Yêu cầu: PostgreSQL trên máy (localhost) và docker-compose services API đang chạy
"""
import requests
import time

BASE = "http://localhost"
LAPTOP_URL = f"{BASE}:8003/laptops/"
MOBILE_URL = f"{BASE}:8004/mobiles/"
STAFF_URL = f"{BASE}:8002/staff/"

LAPTOPS = [
    {
        "name": "MacBook Pro 14\"",
        "brand": "Apple",
        "price": "1999.00",
        "cpu": "Apple M3 Pro",
        "ram": "18GB Unified Memory",
        "storage": "512GB SSD",
        "display": "14.2\" Liquid Retina XDR 120Hz",
        "description": "Laptop chuyên nghiệp mạnh mẽ nhất của Apple năm 2023",
        "stock": 20,
    },
    {
        "name": "MacBook Air 15\"",
        "brand": "Apple",
        "price": "1299.00",
        "cpu": "Apple M2",
        "ram": "8GB Unified Memory",
        "storage": "256GB SSD",
        "display": "15.3\" Liquid Retina 500 nits",
        "description": "Laptop mỏng nhẹ nhất với hiệu năng vượt trội",
        "stock": 35,
    },
    {
        "name": "XPS 15 9530",
        "brand": "Dell",
        "price": "1849.00",
        "cpu": "Intel Core i9-13900H",
        "ram": "32GB DDR5",
        "storage": "1TB NVMe SSD",
        "display": "15.6\" OLED 3.5K 60Hz",
        "description": "Laptop cao cấp cho dân sáng tạo nội dung",
        "stock": 15,
    },
    {
        "name": "ThinkPad X1 Carbon Gen 11",
        "brand": "Lenovo",
        "price": "1599.00",
        "cpu": "Intel Core i7-1365U",
        "ram": "16GB LPDDR5",
        "storage": "512GB SSD",
        "display": "14\" IPS 2.8K OLED 60Hz",
        "description": "Laptop doanh nhân huyền thoại, bền bỉ và nhẹ nhàng",
        "stock": 25,
    },
    {
        "name": "ROG Zephyrus G14",
        "brand": "ASUS",
        "price": "1449.00",
        "cpu": "AMD Ryzen 9 7940HS",
        "ram": "16GB DDR5",
        "storage": "1TB SSD",
        "display": "14\" QHD+ 165Hz ROG Nebula",
        "description": "Laptop gaming compact mạnh nhất trong phân khúc",
        "stock": 18,
    },
    {
        "name": "Inspiron 16 Plus",
        "brand": "Dell",
        "price": "999.00",
        "cpu": "Intel Core i7-13700H",
        "ram": "16GB DDR5",
        "storage": "512GB SSD",
        "display": "16\" IPS 2.5K 120Hz",
        "description": "Laptop tầm trung hiệu năng tốt cho công việc hàng ngày",
        "stock": 40,
    },
    {
        "name": "HP Spectre x360 14",
        "brand": "HP",
        "price": "1699.00",
        "cpu": "Intel Core i7-1255U",
        "ram": "16GB LPDDR5",
        "storage": "512GB SSD",
        "display": "14\" 2K OLED Touch 60Hz",
        "description": "Laptop 2-in-1 cao cấp với thiết kế sang trọng",
        "stock": 12,
    },
    {
        "name": "Galaxy Book3 Pro 360",
        "brand": "Samsung",
        "price": "1349.00",
        "cpu": "Intel Core i7-1360P",
        "ram": "16GB LPDDR5",
        "storage": "512GB NVMe SSD",
        "display": "13.3\" Dynamic AMOLED 2X 360Hz",
        "description": "Laptop 2-in-1 tích hợp bút S Pen, màn hình AMOLED xuất sắc",
        "stock": 10,
    },
]

MOBILES = [
    {
        "name": "iPhone 15 Pro Max",
        "brand": "Apple",
        "price": "1199.00",
        "cpu": "Apple A17 Pro",
        "ram": "8GB",
        "storage": "256GB",
        "display": "6.7\" Super Retina XDR OLED ProMotion 120Hz",
        "camera": "48MP Main + 12MP Ultra + 12MP Tele 5x",
        "battery": "4422mAh",
        "os": "iOS 17",
        "description": "Chiếc iPhone mạnh nhất từ trước đến nay",
        "stock": 30,
    },
    {
        "name": "iPhone 15",
        "brand": "Apple",
        "price": "799.00",
        "cpu": "Apple A16 Bionic",
        "ram": "6GB",
        "storage": "128GB",
        "display": "6.1\" Super Retina XDR OLED 60Hz",
        "camera": "48MP Main + 12MP Ultra",
        "battery": "3349mAh",
        "os": "iOS 17",
        "description": "iPhone tiêu chuẩn với chip A16 và camera 48MP mới",
        "stock": 50,
    },
    {
        "name": "Galaxy S24 Ultra",
        "brand": "Samsung",
        "price": "1299.00",
        "cpu": "Snapdragon 8 Gen 3",
        "ram": "12GB",
        "storage": "256GB",
        "display": "6.8\" Dynamic AMOLED 2X 120Hz QHD+",
        "camera": "200MP Main + 12MP Ultra + 10MP Tele 3x + 50MP Tele 5x",
        "battery": "5000mAh",
        "os": "Android 14 / One UI 6.1",
        "description": "Flagship mạnh nhất của Samsung với bút S Pen tích hợp",
        "stock": 25,
    },
    {
        "name": "Galaxy S24+",
        "brand": "Samsung",
        "price": "999.00",
        "cpu": "Snapdragon 8 Gen 3",
        "ram": "12GB",
        "storage": "256GB",
        "display": "6.7\" Dynamic AMOLED 2X 120Hz",
        "camera": "50MP Main + 12MP Ultra + 10MP Tele 3x",
        "battery": "4900mAh",
        "os": "Android 14 / One UI 6.1",
        "description": "Hiệu năng đỉnh cao với màn hình lớn và pin dung lượng cao",
        "stock": 20,
    },
    {
        "name": "Pixel 8 Pro",
        "brand": "Google",
        "price": "999.00",
        "cpu": "Google Tensor G3",
        "ram": "12GB",
        "storage": "128GB",
        "display": "6.7\" LTPO OLED 120Hz QHD+",
        "camera": "50MP Main + 48MP Ultra + 48MP Tele 5x",
        "battery": "5050mAh",
        "os": "Android 14",
        "description": "Điện thoại Google xuất sắc với AI photography hàng đầu",
        "stock": 15,
    },
    {
        "name": "Xiaomi 14 Ultra",
        "brand": "Xiaomi",
        "price": "1099.00",
        "cpu": "Snapdragon 8 Gen 3",
        "ram": "16GB",
        "storage": "512GB",
        "display": "6.73\" LTPO OLED 120Hz 2K+",
        "camera": "50MP Leica Main + 50MP Ultra + 50MP Tele 3.2x + 50MP Tele 5x",
        "battery": "5000mAh 90W",
        "os": "Android 14 / HyperOS",
        "description": "Flagship quay phim đỉnh cao với hệ thống camera Leica 4 ống kính",
        "stock": 18,
    },
    {
        "name": "OnePlus 12",
        "brand": "OnePlus",
        "price": "799.00",
        "cpu": "Snapdragon 8 Gen 3",
        "ram": "12GB",
        "storage": "256GB",
        "display": "6.82\" LTPO AMOLED 120Hz QHD+",
        "camera": "50MP Hasselblad + 48MP Ultra + 64MP Tele 3x",
        "battery": "5400mAh 100W",
        "os": "Android 14 / OxygenOS 14",
        "description": "Flagship killer với sạc nhanh 100W và camera Hasselblad",
        "stock": 22,
    },
    {
        "name": "Vivo X100 Pro",
        "brand": "Vivo",
        "price": "899.00",
        "cpu": "MediaTek Dimensity 9300",
        "ram": "12GB",
        "storage": "256GB",
        "display": "6.78\" LTPO AMOLED 120Hz 2K",
        "camera": "50MP Zeiss Main + 48MP Ultra + 64MP Tele 4.3x",
        "battery": "5400mAh 100W",
        "os": "Android 14 / OriginOS",
        "description": "Camera Zeiss huyền thoại trong chiếc điện thoại slim",
        "stock": 12,
    },
]

def wait_for_service(url, name, retries=10):
    print(f"⏳ Đang chờ {name}...", end='', flush=True)
    for i in range(retries):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code < 500:
                print(" ✅")
                return True
        except:
            pass
        print(".", end='', flush=True)
        time.sleep(3)
    print(" ❌")
    return False

def seed_laptops():
    print("\n💻 Đang thêm laptops...")
    ok = 0
    for item in LAPTOPS:
        try:
            r = requests.post(LAPTOP_URL, json=item, timeout=10)
            if r.status_code in [200, 201]:
                print(f"  ✅ {item['brand']} {item['name']}")
                ok += 1
            elif r.status_code == 400 and 'already' in str(r.text).lower():
                print(f"  ⚠️  {item['name']} đã tồn tại")
            else:
                print(f"  ❌ {item['name']}: {r.status_code} — {r.text[:80]}")
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
    print(f"  → Đã thêm {ok}/{len(LAPTOPS)} laptops")

def seed_mobiles():
    print("\n📱 Đang thêm mobiles...")
    ok = 0
    for item in MOBILES:
        try:
            r = requests.post(MOBILE_URL, json=item, timeout=10)
            if r.status_code in [200, 201]:
                print(f"  ✅ {item['brand']} {item['name']}")
                ok += 1
            elif r.status_code == 400 and 'already' in str(r.text).lower():
                print(f"  ⚠️  {item['name']} đã tồn tại")
            else:
                print(f"  ❌ {item['name']}: {r.status_code} — {r.text[:80]}")
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
    print(f"  → Đã thêm {ok}/{len(MOBILES)} mobiles")

def seed_staff():
    print("\n👤 Đang tạo tài khoản Staff mặc định...")
    try:
        r = requests.post(f"{STAFF_URL}register/", json={
            "username": "admin",
            "email": "admin@techstore.vn",
            "password": "admin123",
            "role": "admin"
        }, timeout=10)
        if r.status_code == 201:
            print("  ✅ Staff 'admin' đã được tạo (password: admin123)")
        elif r.status_code == 400:
            print("  ⚠️  Tài khoản 'admin' đã tồn tại")
        else:
            print(f"  ❌ {r.status_code}: {r.text[:80]}")
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")

def main():
    print("=" * 55)
    print("  🚀 TechStore Seed Data Script")
    print("=" * 55)

    # Kiểm tra services
    if not wait_for_service(LAPTOP_URL, "Laptop Service"):
        print("❌ Laptop service không khả dụng. Đã thoát.")
        return
    if not wait_for_service(MOBILE_URL, "Mobile Service"):
        print("❌ Mobile service không khả dụng. Đã thoát.")
        return
    if not wait_for_service(f"{STAFF_URL}login/", "Staff Service"):
        print("⚠️  Staff service không khả dụng, bỏ qua seed staff.")

    seed_staff()
    seed_laptops()
    seed_mobiles()

    print("\n" + "=" * 55)
    print("  🎉 Seed data hoàn thành!")
    print("  👉 Customer UI: http://localhost:8000/ui/customer/")
    print("  👉 Staff UI:    http://localhost:8000/ui/staff/")
    print("     Staff login: admin / admin123")
    print("=" * 55)

if __name__ == '__main__':
    main()
