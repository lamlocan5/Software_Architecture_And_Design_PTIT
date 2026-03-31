import requests
import time

BASE_URL = "http://localhost:8000/api"

LAPTOPS = [
    {"model_name": "MacBook Pro M3", "cpu": "Apple M3 Pro", "ram_gb": 18, "price": 1999.00},
    {"model_name": "Dell XPS 15", "cpu": "Intel Core i7-13700H", "ram_gb": 16, "price": 1750.00},
    {"model_name": "ThinkPad X1 Carbon Gen 11", "cpu": "Intel Core i7-1355U", "ram_gb": 32, "price": 1890.00},
    {"model_name": "ASUS ROG Zephyrus G14", "cpu": "AMD Ryzen 9 7940HS", "ram_gb": 16, "price": 1600.00},
    {"model_name": "Acer Swift Go 14", "cpu": "Intel Core Ultra 7", "ram_gb": 16, "price": 999.00},
]

MOBILES = [
    {"model_name": "iPhone 15 Pro", "chipset": "A17 Pro", "storage_gb": 256, "price": 1099.00},
    {"model_name": "Samsung Galaxy S24 Ultra", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 512, "price": 1299.00},
    {"model_name": "Google Pixel 8 Pro", "chipset": "Tensor G3", "storage_gb": 128, "price": 999.00},
    {"model_name": "Xiaomi 14 Ultra", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 512, "price": 1150.00},
    {"model_name": "OnePlus 12", "chipset": "Snapdragon 8 Gen 3", "storage_gb": 256, "price": 799.00},
]

STAFFS = [
    {"full_name": "Alice Admin", "position": "Manager", "email": "alice@admin.com", "username": "admin_alice", "password": "password123"},
    {"full_name": "Bob Staff", "position": "Sales", "email": "bob@staff.com", "username": "staff_bob", "password": "password123"}
]

CUSTOMERS = [
    {"full_name": "Charlie Customer", "phone": "123456789", "email": "charlie@cus.com", "username": "cus_charlie", "password": "password123"},
    {"full_name": "Dave Buyer", "phone": "987654321", "email": "dave@cus.com", "username": "cus_dave", "password": "password123"}
]

def seed_data():
    print("Seeding Laptops...")
    for item in LAPTOPS:
        try:
            r = requests.post(f"{BASE_URL}/laptop/products/create/", json=item)
            if r.status_code == 201:
                print(f"Created laptop: {item['model_name']}")
            else:
                with open("error.html", "w", encoding="utf-8") as f:
                    f.write(r.text)
                print(f"Failed laptop {item['model_name']}, error saved to error.html")
                break

        except requests.exceptions.ConnectionError:
            print("Gateway not reachable. Is the docker-compose up?")

    print("\nSeeding Mobiles...")
    for item in MOBILES:
        try:
            r = requests.post(f"{BASE_URL}/moblie/products/create/", json=item)
            if r.status_code == 201:
                print(f"Created mobile: {item['model_name']}")
            else:
                print(f"Failed to create mobile {item['model_name']}: {r.status_code} {r.text}")
        except requests.exceptions.ConnectionError:
            print("Gateway not reachable.")

    print("\nSeeding Staffs...")
    for item in STAFFS:
        try:
            r = requests.post(f"{BASE_URL}/staff/register/", json=item)
            if r.status_code == 201:
                print(f"Created staff: {item['username']}")
            else:
                print(f"Failed to create staff {item['username']}: {r.status_code} {r.text}")
        except requests.exceptions.ConnectionError:
            print("Gateway not reachable.")

    print("\nSeeding Customers...")
    for item in CUSTOMERS:
        try:
            r = requests.post(f"{BASE_URL}/customer/register/", json=item)
            if r.status_code == 201:
                print(f"Created customer: {item['username']}")
            else:
                print(f"Failed to create customer {item['username']}: {r.status_code} {r.text}")
        except requests.exceptions.ConnectionError:
            print("Gateway not reachable.")

if __name__ == "__main__":
    seed_data()
