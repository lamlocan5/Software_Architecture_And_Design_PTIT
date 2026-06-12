import os
import sys
import hashlib
import base64

db_host = 'localhost'
db_port = '5432'
db_user = 'postgres'
db_password = '1234'

mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'root'
mysql_password = '123456789'

if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == 'DB_HOST':
                    db_host = val
                elif key == 'DB_PORT':
                    db_port = val
                elif key == 'DB_USER':
                    db_user = val
                elif key == 'DB_PASSWORD':
                    db_password = val

if db_host == 'host.docker.internal':
    db_host = 'localhost'

try:
    import psycopg2
except ImportError:
    print("psycopg2 is not installed. Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

try:
    import pymysql
except ImportError:
    print("pymysql is not installed. Installing pymysql...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql

def connect_pg(db_name):
    return psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )

def connect_mysql(db_name):
    return pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=db_name
    )

def make_django_password(password):
    salt = "bookstore_seeding_salt"
    iterations = 360000
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    hash_b64 = base64.b64encode(hash_bytes).decode('utf-8')
    return f"pbkdf2_sha256${iterations}${salt}${hash_b64}"

def feed_products():
    print("Feeding bookstore_product...")
    conn = connect_pg("bookstore_product")
    cursor = conn.cursor()
    
    # 1. Clear existing data
    cursor.execute("TRUNCATE TABLE app_product, app_publisher, app_category RESTART IDENTITY CASCADE;")
    
    # 2. Insert Publishers
    publishers = [
        ("Nhà xuất bản Trẻ", "Hồ Chí Minh", "tre@nxb.com"),
        ("Nhà xuất bản Kim Đồng", "Hà Nội", "kimdong@nxb.com"),
        ("Nhà xuất bản Nhã Nam", "Hà Nội", "nhanam@nxb.com"),
        ("Nhà xuất bản Phụ Nữ", "Hà Nội", "phunuvn@nxb.com"),
        ("Nhà xuất bản Lao Động", "Hồ Chí Minh", "laodong@nxb.com")
    ]
    
    publisher_ids = {}
    for name, address, mail in publishers:
        cursor.execute(
            "INSERT INTO app_publisher (name, address, mail) VALUES (%s, %s, %s) RETURNING id;",
            (name, address, mail)
        )
        pub_id = cursor.fetchone()[0]
        publisher_ids[name] = pub_id
        
    # 3. Insert Categories
    categories = [
        ("Áo Nam", "Thời trang áo nam đa dạng, phong cách", "clothing"),
        ("Quần Nam", "Quần nam kaki, jean, jogger", "clothing"),
        ("Thời Trang Nữ", "Váy đầm, áo thun, chân váy nữ thời thượng", "clothing"),
        ("Phụ Kiện", "Thắt lưng, mũ, tất, ví da", "clothing"),
        ("Điện thoại & Máy tính bảng", "Smartphones và Tablets chính hãng", "electronic"),
        ("Máy tính & Laptop", "Laptops văn phòng, gaming và phụ kiện máy tính", "electronic"),
        ("Thiết bị Âm thanh", "Loa Bluetooth, tai nghe không dây", "electronic"),
        ("Phụ kiện công nghệ", "Sạc dự phòng, cáp sạc, giá đỡ", "electronic")
    ]
    
    category_ids = {}
    for name, desc, ctype in categories:
        cursor.execute(
            "INSERT INTO app_category (name, description, category_type) VALUES (%s, %s, %s) RETURNING id;",
            (name, desc, ctype)
        )
        cat_id = cursor.fetchone()[0]
        category_ids[name] = cat_id

    # 4. Insert Products (Books)
    books = [
        ("Đắc Nhân Tâm", "Dale Carnegie", 86000.00, 120, "Nhà xuất bản Trẻ"),
        ("Số Đỏ", "Vũ Trọng Phụng", 65000.00, 50, "Nhà xuất bản Trẻ"), 
        ("Chí Phèo", "Nam Cao", 45000.00, 80, "Nhà xuất bản Kim Đồng"),
        ("Dế Mèn Phiêu Lưu Ký", "Tô Hoài", 55000.00, 200, "Nhà xuất bản Kim Đồng"),
        ("Đất Rừng Phương Nam", "Đoàn Giỏi", 72000.00, 150, "Nhà xuất bản Trẻ"),
        ("Tắt Đèn", "Ngô Tất Tố", 48000.00, 90, "Nhà xuất bản Lao Động"),
        ("Lão Hạc", "Nam Cao", 35000.00, 110, "Nhà xuất bản Lao Động"),
        ("Mắt Biếc", "Nguyễn Nhật Ánh", 110000.00, 180, "Nhà xuất bản Trẻ"),
        ("Cho Tôi Xin Một Vé Đi Tuổi Thơ", "Nguyễn Nhật Ánh", 95000.00, 250, "Nhà xuất bản Trẻ"),
        ("Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "Nguyễn Nhật Ánh", 125000.00, 160, "Nhà xuất bản Trẻ"),
        ("Độc Giả Thứ 7", "Lôi Mễ", 115000.00, 45, "Nhà xuất bản Nhã Nam"),
        ("Đề Thi Đẫm Máu", "Lôi Mễ", 145000.00, 30, "Nhà xuất bản Nhã Nam")
    ]
    
    for title, author, price, stock, pub_name in books:
        pub_id = publisher_ids.get(pub_name) or list(publisher_ids.values())[0]
        # Store attributes as JSON
        import json
        attrs = json.dumps({"author": author, "publisher_id": pub_id})
        cursor.execute(
            "INSERT INTO app_product (name, product_type, price, stock, attributes) VALUES (%s, 'book', %s, %s, %s);",
            (title, price, stock, attrs)
        )
        
    # 5. Insert Products (Clothing)
    clothes = [
        ("Áo thun nam Polo cotton", "L", "Xanh Navy", 189000.00, 100, "Áo Nam"),
        ("Áo sơ mi nam công sở trắng", "XL", "Trắng", 250000.00, 60, "Áo Nam"),
        ("Quần Jean nam Slimfit co giãn", "32", "Xanh nhạt", 350000.00, 45, "Quần Nam"),
        ("Váy hoa nhí dáng dài Hàn Quốc", "M", "Vàng", 290000.00, 35, "Thời Trang Nữ"),
        ("Áo khoác gió unisex chống nước", "XXL", "Đen", 450000.00, 70, "Áo Nam"),
        ("Mũ trùm đầu đen thêu chữ", "F", "Đen", 99000.00, 150, "Phụ Kiện")
    ]
    
    for name, size, color, price, stock, cat_name in clothes:
        cat_id = category_ids.get(cat_name)
        import json
        attrs = json.dumps({"size": size, "color": color, "category_id": cat_id})
        cursor.execute(
            "INSERT INTO app_product (name, product_type, price, stock, attributes) VALUES (%s, 'clothing', %s, %s, %s);",
            (name, price, stock, attrs)
        )

    # 6. Insert Products (Electronics)
    electronics = [
        ("iPhone 15 Pro Max 256GB", "Apple", "Titan Tự Nhiên", 29990000.00, 15, "Điện thoại & Máy tính bảng"),
        ("Samsung Galaxy S24 Ultra 512GB", "Samsung", "Xám Titan", 27500000.00, 20, "Điện thoại & Máy tính bảng"),
        ("Laptop Asus Zenbook 14 OLED", "Asus", "UX3405", 21990000.00, 12, "Máy tính & Laptop"),
        ("Laptop Gaming Lenovo Legion 5", "Lenovo", "Legion 5 15IAH7", 24500000.00, 8, "Máy tính & Laptop"),
        ("Tai nghe True Wireless Sony WF-1000XM5", "Sony", "WF-1000XM5 Black", 5490000.00, 30, "Thiết bị Âm thanh"),
        ("Sạc dự phòng Anker 20000mAh", "Anker", "PowerCore 20K", 650000.00, 80, "Phụ kiện công nghệ")
    ]
    
    for name, brand, model, price, stock, cat_name in electronics:
        cat_id = category_ids.get(cat_name)
        import json
        attrs = json.dumps({"brand": brand, "model": model, "category_id": cat_id})
        cursor.execute(
            "INSERT INTO app_product (name, product_type, price, stock, attributes) VALUES (%s, 'electronic', %s, %s, %s);",
            (name, price, stock, attrs)
        )
        
    conn.commit()
    cursor.close()
    conn.close()
    print("bookstore_product fed successfully!")

def feed_users():
    print("Feeding bookstore_user (MySQL)...")
    conn = connect_mysql("bookstore_user")
    cursor = conn.cursor()
    
    # Disable foreign keys temporarily to truncate safely
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE app_customer;")
    cursor.execute("TRUNCATE TABLE app_staff;")
    cursor.execute("TRUNCATE TABLE app_manager;")
    cursor.execute("TRUNCATE TABLE auth_user_groups;")
    cursor.execute("TRUNCATE TABLE auth_group;")
    cursor.execute("TRUNCATE TABLE auth_user;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    # 1. Insert Groups
    cursor.execute("INSERT INTO auth_group (id, name) VALUES (1, 'staff'), (2, 'manager');")
    
    # 2. Hashed Passwords
    hashed_admin = make_django_password("admin123")
    hashed_staff = make_django_password("staff123")
    hashed_manager = make_django_password("manager123")
    hashed_customer = make_django_password("customer123")
    
    # 3. Create Admin (Superuser)
    cursor.execute(
        "INSERT INTO auth_user (id, username, password, email, is_superuser, is_staff, is_active, date_joined, first_name, last_name) "
        "VALUES (1, 'admin', %s, 'admin@bookstore.com', 1, 1, 1, NOW(), 'Admin', '');",
        (hashed_admin,)
    )
    
    # 4. Feed Staff
    staffs = [
        (2, "Trần Văn Tùng", "tungtv@bookstore.com"),
        (3, "Phan Thị Mai", "maipt@bookstore.com"),
        (4, "Nguyễn Đức Anh", "anhnd@bookstore.com")
    ]
    for uid, name, email in staffs:
        cursor.execute(
            "INSERT INTO auth_user (id, username, password, email, is_superuser, is_staff, is_active, date_joined, first_name, last_name) "
            "VALUES (%s, %s, %s, %s, 0, 1, 1, NOW(), %s, '');",
            (uid, email, hashed_staff, email, name)
        )
        cursor.execute("INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, 1);", (uid,))
        cursor.execute("INSERT INTO app_staff (name, email, active, created_at, user_id) VALUES (%s, %s, 1, NOW(), %s);", (name, email, uid))
        
    # 5. Feed Managers
    managers = [
        (5, "Lê Minh Triết", "trietlm@bookstore.com"),
        (6, "Nguyễn Thị Kim Dung", "dungntk@bookstore.com")
    ]
    for uid, name, email in managers:
        cursor.execute(
            "INSERT INTO auth_user (id, username, password, email, is_superuser, is_staff, is_active, date_joined, first_name, last_name) "
            "VALUES (%s, %s, %s, %s, 0, 1, 1, NOW(), %s, '');",
            (uid, email, hashed_manager, email, name)
        )
        cursor.execute("INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, 2);", (uid,))
        cursor.execute("INSERT INTO app_manager (name, email, active, created_at, user_id) VALUES (%s, %s, 1, NOW(), %s);", (name, email, uid))
        
    # 6. Feed Customers
    customers = [
        (7, "Nguyễn Văn Hùng", "hungnv@gmail.com"),
        (8, "Trần Thị Lan", "lantt@yahoo.com"),
        (9, "Phạm Minh Đức", "ducpm@outlook.com"),
        (10, "Lê Thị Hồng", "hongle@gmail.com"),
        (11, "Hoàng Anh Tuấn", "tuanha@gmail.com")
    ]
    for uid, name, email in customers:
        cursor.execute(
            "INSERT INTO auth_user (id, username, password, email, is_superuser, is_staff, is_active, date_joined, first_name, last_name) "
            "VALUES (%s, %s, %s, %s, 0, 0, 1, NOW(), %s, '');",
            (uid, email, hashed_customer, email, name)
        )
        cursor.execute("INSERT INTO app_customer (name, email, user_id) VALUES (%s, %s, %s);", (name, email, uid))
        # PyMySQL cursor.execute doesn't support RETURNING like PG.
        # But wait, since we truncated with CASCADE or sequentially, the generated IDs will be 1, 2, 3, 4, 5.
        # Let's get the last insert ID.
        cust_id = cursor.lastrowid or (uid - 6)
        
        # Call cart-service to create a cart for each customer (best-effort)
        try:
            import requests
            requests.post("http://localhost:8003/carts/", json={"customer_id": cust_id}, timeout=1)
        except Exception:
            pass

    conn.commit()
    cursor.close()
    conn.close()
    print("bookstore_user (MySQL) fed successfully!")

def feed_reviews():
    print("Feeding bookstore_review...")
    conn = connect_pg("bookstore_review")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE app_review RESTART IDENTITY CASCADE;")
    
    reviews = [
        (1, 1, "Nguyễn Văn Hùng", "Đắc Nhân Tâm", 5, "Sách cực kỳ hay, khuyên mọi người nên đọc ít nhất một lần trong đời!"),
        (1, 2, "Trần Thị Lan", "Đắc Nhân Tâm", 4, "Nội dung rất ý nghĩa, dịch giả dịch mượt mà, trình bày đẹp."),
        (2, 3, "Phạm Minh Đức", "Số Đỏ", 5, "Một tác phẩm châm biếm sâu sắc của Vũ Trọng Phụng. Đọc rất thấm."),
        (8, 4, "Lê Thị Hồng", "Mắt Biếc", 5, "Truyện tình buồn nhưng đẹp đẽ vô cùng, giọng văn Nguyễn Nhật Ánh đong đầy cảm xúc."),
        (9, 5, "Hoàng Anh Tuấn", "Cho Tôi Xin Một Vé Đi Tuổi Thơ", 5, "Đọc truyện này như thấy lại chính mình ngày nhỏ. Rất đáng yêu và hài hước.")
    ]
    
    for book_id, customer_id, name, book_title, rating, comment in reviews:
        cursor.execute(
            "INSERT INTO app_review (book_id, customer_id, customer_name, book_title, rating, comment, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW());",
            (book_id, customer_id, name, book_title, rating, comment)
        )
        
    conn.commit()
    cursor.close()
    conn.close()
    print("bookstore_review fed successfully!")

if __name__ == "__main__":
    try:
        feed_products()
        feed_users()
        feed_reviews()
        print("\nAll database feeds executed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)
