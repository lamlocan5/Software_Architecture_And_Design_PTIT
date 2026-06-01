"""
seeds/import_neo4j.py - Import dữ liệu từ CSV vào Neo4j Knowledge Graph.
Chạy: python seeds/import_neo4j.py
"""
import os
import csv
import sys
from pathlib import Path
from neo4j import GraphDatabase

# Thư mục gốc chứa file data_user500.csv
BASE_DIR = Path(__file__).resolve().parent

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Danh sách 30 sản phẩm
PRODUCTS = [
    (1,  "iPhone 15 Pro Max",            "Điện thoại"),
    (2,  "Samsung Galaxy S24 Ultra",      "Điện thoại"),
    (3,  "Xiaomi 14 Pro",                 "Điện thoại"),
    (4,  "OPPO Find X7 Pro",              "Điện thoại"),
    (5,  "Realme GT 5 Pro",               "Điện thoại"),
    (6,  "MacBook Air M3",                "Laptop"),
    (7,  "Dell XPS 15",                   "Laptop"),
    (8,  "Lenovo ThinkPad X1 Carbon",     "Laptop"),
    (9,  "ASUS ZenBook 14 OLED",          "Laptop"),
    (10, "HP Spectre x360 14",            "Laptop"),
    (11, "iPad Pro M4 12.9 inch",         "Máy tính bảng"),
    (12, "Samsung Galaxy Tab S9 Ultra",   "Máy tính bảng"),
    (13, "Lenovo Tab P12 Pro",            "Máy tính bảng"),
    (14, "AirPods Pro 2",                 "Tai nghe"),
    (15, "Sony WH-1000XM5",              "Tai nghe"),
    (16, "Samsung Galaxy Buds 2 Pro",    "Tai nghe"),
    (17, "Apple Watch Series 9",         "Đồng hồ thông minh"),
    (18, "Samsung Galaxy Watch 6 Classic","Đồng hồ thông minh"),
    (19, "Garmin Venu 3",                "Đồng hồ thông minh"),
    (20, "Sony PlayStation 5",           "Gaming"),
    (21, "Nintendo Switch OLED",         "Gaming"),
    (22, "Logitech MX Keys S",           "Phụ kiện"),
    (23, "Logitech MX Master 3S",        "Phụ kiện"),
    (24, "Màn hình Dell 27 inch 4K",     "Phụ kiện"),
    (25, "SSD Samsung 990 Pro 2TB",      "Lưu trữ"),
    (26, "GPU NVIDIA RTX 4070 Super",    "Linh kiện PC"),
    (27, "RAM Corsair Vengeance 32GB DDR5","Linh kiện PC"),
    (28, "Bàn phím cơ Keychron Q3",     "Phụ kiện"),
    (29, "Webcam Logitech Brio 4K",      "Phụ kiện"),
    (30, "Loa Bluetooth JBL Charge 5",   "Âm thanh"),
]


def reset_graph(session):
    print("Xóa toàn bộ graph cũ...")
    session.run("MATCH (n) DETACH DELETE n")
    # Tạo constraints (tùy chọn nhưng tốt cho hiệu suất)
    try:
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")
    except Exception as e:
        print("Bỏ qua tạo constraint:", e)


def create_products(session):
    print("Tạo 30 Product nodes...")
    query = """
    UNWIND $products AS row
    MERGE (p:Product {id: row.id})
    SET p.name = row.name, p.category = row.category
    """
    products_data = [{"id": p[0], "name": p[1], "category": p[2]} for p in PRODUCTS]
    session.run(query, products=products_data)


def import_csv_to_graph(session, csv_file_path):
    print(f"Đọc file CSV: {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print("LỖI: Không tìm thấy file CSV!")
        sys.exit(1)

    print("Đang xử lý dữ liệu và tạo Relationships (tốn khoảng 5-10 giây)...")
    
    # Chúng ta batch bằng Python thay vì Neo4j LOAD CSV cho dễ xử lý file path
    batch = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                user_id = int(row['user_id'])
                product_id = int(row['product_id'])
                if product_id > 30: continue
                action = row['action'].strip().upper()  # VIEW, CLICK, ADD_TO_CART
                timestamp = row['timestamp']
                
                batch.append({
                    "u_id": user_id,
                    "p_id": product_id,
                    "action": action,
                    "time": timestamp
                })
            except Exception:
                continue

    # Xử lý từng lô (batch) 1000 dòng để tránh đầy bộ nhớ
    batch_size = 1000
    total = len(batch)
    processed = 0

    query = """
    UNWIND $batch AS row
    MERGE (u:User {id: row.u_id})
    WITH u, row
    MATCH (p:Product {id: row.p_id})
    
    // Tạo quan hệ động dựa theo biến
    CALL apoc.create.relationship(u, row.action, {timestamp: row.time}, p) YIELD rel
    RETURN count(rel)
    """

    # Do APOC có thể không có sẵn trong Docker neo4j chuẩn nếu không enable, 
    # Ta chia thành 3 query cứng cho 3 loại relationship để không phụ thuộc APOC
    query_view = """
    UNWIND $batch AS row
    MERGE (u:User {id: row.u_id})
    WITH u, row MATCH (p:Product {id: row.p_id})
    CREATE (u)-[:VIEW {timestamp: row.time}]->(p)
    """
    query_click = """
    UNWIND $batch AS row
    MERGE (u:User {id: row.u_id})
    WITH u, row MATCH (p:Product {id: row.p_id})
    CREATE (u)-[:CLICK {timestamp: row.time}]->(p)
    """
    query_add = """
    UNWIND $batch AS row
    MERGE (u:User {id: row.u_id})
    WITH u, row MATCH (p:Product {id: row.p_id})
    CREATE (u)-[:ADD_TO_CART {timestamp: row.time}]->(p)
    """

    views = [b for b in batch if b['action'] == 'VIEW']
    clicks = [b for b in batch if b['action'] == 'CLICK']
    adds = [b for b in batch if b['action'] == 'ADD_TO_CART']

    print(f"Có {len(views)} VIEW, {len(clicks)} CLICK, {len(adds)} ADD_TO_CART")

    def run_batch(q, data, label):
        for i in range(0, len(data), batch_size):
            chunk = data[i:i+batch_size]
            session.run(q, batch=chunk)
            print(f" - Đã import {min(i+batch_size, len(data))}/{len(data)} {label}...")

    run_batch(query_view, views, "VIEW")
    run_batch(query_click, clicks, "CLICK")
    run_batch(query_add, adds, "ADD_TO_CART")

    print(f"✅ Hoàn tất import {total} relationships!")


def main():
    print("="*50)
    print("🚀 Bắt đầu import Knowledge Graph vào Neo4j")
    print("="*50)
    
    csv_file_path = BASE_DIR / 'data_user500.csv'
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ Kết nối Neo4j thành công!")
    except Exception as e:
        print("❌ LỖI: Không thể kết nối tới Neo4j. Bạn đã chạy 'docker compose up -d' chưa?")
        print(f"Chi tiết: {e}")
        sys.exit(1)

    with driver.session() as session:
        reset_graph(session)
        create_products(session)
        import_csv_to_graph(session, csv_file_path)

    driver.close()
    print("="*50)
    print("🎉 Mọi thứ đã sẵn sàng!")
    print("Mở browser để xem graph: http://localhost:7474")


if __name__ == "__main__":
    main()
