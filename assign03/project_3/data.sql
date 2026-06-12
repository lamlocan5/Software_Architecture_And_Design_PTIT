-- =======================================================================================
-- DATABASE SCHEMA CHO HỆ THỐNG BÁN SÁCH ONLINE
-- TỔNG HỢP: > 50 BẢNG (TABLES)
-- PHÂN HỆ: SẢN PHẨM, NGƯỜI DÙNG, ĐƠN HÀNG, KHO VẬN, MARKETING
-- =======================================================================================

DROP DATABASE IF EXISTS bookstore_db;
CREATE DATABASE bookstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_db;

-- =======================================================================================
-- MODULE 1: PRODUCT CATALOG (QUẢN LÝ SẢN PHẨM)
-- =======================================================================================

-- 1. Nhà xuất bản
CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_email VARCHAR(100),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tác giả
CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    biography TEXT,
    website VARCHAR(255),
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Danh mục sách (Đệ quy cho danh mục cha - con)
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- 4. Bộ sách / Series
CREATE TABLE series (
    series_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_volumes INT DEFAULT 0
);

-- 5. Ngôn ngữ
CREATE TABLE languages (
    lang_code VARCHAR(10) PRIMARY KEY, -- VN, EN, JP...
    name VARCHAR(50) NOT NULL,
    flag_icon VARCHAR(255)
);

-- 6. Bảng Sách (Bảng chính - Base Table)
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publisher_id INT,
    series_id INT NULL,
    category_id INT,
    lang_code VARCHAR(10),
    publication_date DATE,
    description TEXT,
    base_price DECIMAL(15, 2) NOT NULL,
    current_status ENUM('Available', 'Out_of_stock', 'Discontinued') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id),
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (lang_code) REFERENCES languages(lang_code)
);

-- 7. Sách vật lý (Kế thừa Book)
CREATE TABLE physical_books (
    book_id INT PRIMARY KEY,
    weight_gram DECIMAL(10, 2),
    dimensions VARCHAR(50), -- VD: 20x30x2 cm
    cover_type ENUM('Hardcover', 'Paperback'),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- 8. E-Book (Kế thừa Book)
CREATE TABLE ebooks (
    book_id INT PRIMARY KEY,
    file_size_mb DECIMAL(10, 2),
    format VARCHAR(20), -- PDF, EPUB, MOBI
    download_url VARCHAR(500),
    is_drm_protected BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- 9. Audio Book (Kế thừa Book)
CREATE TABLE audio_books (
    book_id INT PRIMARY KEY,
    duration_minutes INT,
    narrator_name VARCHAR(255),
    sample_url VARCHAR(500),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- 10. Bảng trung gian Sách - Tác giả (N-N)
CREATE TABLE book_authors (
    book_id INT,
    author_id INT,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

-- 11. Hình ảnh sách
CREATE TABLE book_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    alt_text VARCHAR(255),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- 12. Thẻ / Tags
CREATE TABLE tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    color_code VARCHAR(20)
);

-- 13. Bảng trung gian Sách - Tags (N-N)
CREATE TABLE book_tags (
    book_id INT,
    tag_id INT,
    PRIMARY KEY (book_id, tag_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- 14. Thống kê đánh giá (Aggregated Data)
CREATE TABLE rating_statistics (
    book_id INT PRIMARY KEY,
    average_rating DECIMAL(3, 2) DEFAULT 0,
    total_reviews INT DEFAULT 0,
    star_5_count INT DEFAULT 0,
    star_1_count INT DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- =======================================================================================
-- MODULE 2: USER & IAM (QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN)
-- =======================================================================================

-- 15. Hạng thành viên
CREATE TABLE membership_tiers (
    tier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- Bronze, Silver, Gold
    min_points INT NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0
);

-- 16. Vai trò (Roles)
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL, -- Admin, Staff, Customer
    description TEXT
);

-- 17. Quyền hạn (Permissions)
CREATE TABLE permissions (
    perm_id INT AUTO_INCREMENT PRIMARY KEY,
    perm_key VARCHAR(50) UNIQUE NOT NULL, -- USER_READ, ORDER_WRITE
    module VARCHAR(50)
);

-- 18. Phân quyền cho Vai trò (N-N)
CREATE TABLE role_permissions (
    role_id INT,
    perm_id INT,
    PRIMARY KEY (role_id, perm_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (perm_id) REFERENCES permissions(perm_id) ON DELETE CASCADE
);

-- 19. Người dùng (User Base)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    role_id INT, -- Main role
    status ENUM('Active', 'Banned', 'Unverified') DEFAULT 'Unverified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- 20. Khách hàng (Mở rộng User)
CREATE TABLE customers (
    user_id INT PRIMARY KEY,
    loyalty_points INT DEFAULT 0,
    tier_id INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES membership_tiers(tier_id)
);

-- 21. Nhân viên (Mở rộng User)
CREATE TABLE staff (
    user_id INT PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE,
    department VARCHAR(50),
    salary_grade INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 22. Hồ sơ chi tiết
CREATE TABLE profiles (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender ENUM('Male', 'Female', 'Other'),
    dob DATE,
    avatar_url VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 23. Tỉnh / Thành phố
CREATE TABLE cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20)
);

-- 24. Quận / Huyện
CREATE TABLE districts (
    district_id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- 25. Phường / Xã
CREATE TABLE wards (
    ward_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

-- 26. Sổ địa chỉ người dùng
CREATE TABLE user_addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    receiver_name VARCHAR(100),
    phone VARCHAR(20),
    ward_id INT,
    specific_address TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);

-- 27. Đánh giá (Reviews)
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    rating TINYINT CHECK (rating BETWEEN 1 AND 5),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 28. Bình luận (Comments - Hỗ trợ phân cấp)
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    parent_comment_id INT NULL, -- Cho phép reply
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
);

-- =======================================================================================
-- MODULE 3: ORDER & PAYMENT (ĐƠN HÀNG VÀ THANH TOÁN)
-- =======================================================================================

-- 29. Giỏ hàng
CREATE TABLE carts (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 30. Chi tiết giỏ hàng
CREATE TABLE cart_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT,
    book_id INT,
    quantity INT DEFAULT 1,
    is_selected BOOLEAN DEFAULT TRUE, -- Chọn để thanh toán
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 31. Đơn hàng
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Confirmed', 'Shipping', 'Completed', 'Cancelled', 'Returned') DEFAULT 'Pending',
    shipping_address_id INT, -- Snapshot address tại thời điểm đặt
    shipping_fee DECIMAL(15, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 32. Chi tiết đơn hàng
CREATE TABLE order_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    book_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL, -- Giá tại thời điểm mua
    subtotal DECIMAL(15, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 33. Lịch sử trạng thái đơn hàng
CREATE TABLE order_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    status VARCHAR(50),
    changed_by INT, -- User ID của người thay đổi (Admin/Staff/System)
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 34. Phương thức thanh toán
CREATE TABLE payment_methods (
    method_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- COD, Banking, Momo, Visa
    config_json JSON NULL, -- Lưu cấu hình API key nếu cần (bảo mật)
    is_active BOOLEAN DEFAULT TRUE
);

-- 35. Thanh toán
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    method_id INT,
    amount DECIMAL(15, 2) NOT NULL,
    status ENUM('Pending', 'Success', 'Failed', 'Refunded') DEFAULT 'Pending',
    payment_time DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (method_id) REFERENCES payment_methods(method_id)
);

-- 36. Giao dịch (Log chi tiết từ cổng thanh toán)
CREATE TABLE transactions (
    trans_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT,
    gateway_trans_id VARCHAR(100), -- Mã GD từ phía Momo/VNPAY
    response_code VARCHAR(20),
    log_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

-- 37. Hóa đơn điện tử
CREATE TABLE invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    tax_code VARCHAR(50),
    company_name VARCHAR(255),
    company_address TEXT,
    issued_date DATETIME,
    file_url VARCHAR(500), -- Link file PDF
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 38. Yêu cầu hoàn tiền / Khiếu nại
CREATE TABLE refund_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    user_id INT,
    reason TEXT,
    evidence_image_url VARCHAR(500),
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- =======================================================================================
-- MODULE 4: INVENTORY & LOGISTICS (KHO VẬN)
-- =======================================================================================

-- 39. Kho hàng
CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    manager_name VARCHAR(100)
);

-- 40. Tồn kho
CREATE TABLE stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id INT,
    book_id INT,
    quantity INT DEFAULT 0,
    reserved_quantity INT DEFAULT 0, -- Hàng đang được giữ cho đơn chưa ship
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 41. Nhà cung cấp
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)
);

-- 42. Phiếu nhập kho
CREATE TABLE import_slips (
    slip_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id INT,
    supplier_id INT,
    staff_id INT, -- Người lập phiếu
    import_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_cost DECIMAL(15, 2),
    status ENUM('Draft', 'Completed', 'Cancelled') DEFAULT 'Draft',
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (staff_id) REFERENCES users(user_id)
);

-- 43. Chi tiết phiếu nhập
CREATE TABLE import_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    slip_id INT,
    book_id INT,
    quantity INT NOT NULL,
    import_price DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (slip_id) REFERENCES import_slips(slip_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 44. Đơn vị vận chuyển
CREATE TABLE shipping_providers (
    provider_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- GHN, GHTK, ViettelPost
    api_endpoint VARCHAR(255),
    api_key VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- 45. Vận đơn (Shipment)
CREATE TABLE shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE,
    provider_id INT,
    tracking_number VARCHAR(100), -- Mã vận đơn
    status VARCHAR(50) DEFAULT 'Ready_to_pick',
    cod_amount DECIMAL(15, 2),
    weight_gram INT,
    estimated_delivery DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (provider_id) REFERENCES shipping_providers(provider_id)
);

-- 46. Nhật ký vận chuyển
CREATE TABLE shipment_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id INT,
    location VARCHAR(255),
    status VARCHAR(50), -- Picked, Hub_In, Hub_Out, Delivering
    scan_time DATETIME,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
);

-- =======================================================================================
-- MODULE 5: MARKETING & SYSTEM (HỆ THỐNG & KHUYẾN MÃI)
-- =======================================================================================

-- 47. Chương trình khuyến mãi
CREATE TABLE promotions (
    promo_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATETIME,
    end_date DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

-- 48. Mã giảm giá (Coupon)
CREATE TABLE coupons (
    coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    promo_id INT,
    discount_type ENUM('Percent', 'Fixed_Amount'),
    discount_value DECIMAL(15, 2),
    min_order_value DECIMAL(15, 2) DEFAULT 0,
    max_usage INT, -- Tổng số lần dùng tối đa
    usage_count INT DEFAULT 0,
    FOREIGN KEY (promo_id) REFERENCES promotions(promo_id)
);

-- 49. Kho mã giảm giá của User
CREATE TABLE user_coupons (
    uc_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    coupon_id INT,
    is_used BOOLEAN DEFAULT FALSE,
    used_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id)
);

-- 50. Danh sách yêu thích
CREATE TABLE wishlists (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) DEFAULT 'My Wishlist',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 51. Mục yêu thích
CREATE TABLE wishlist_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    wishlist_id INT,
    book_id INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 52. Thông báo
CREATE TABLE notifications (
    notif_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    message TEXT,
    type VARCHAR(50), -- Order, Promo, System
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 53. Nhật ký hệ thống (Audit Logs)
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    actor_id INT, -- User thực hiện
    action VARCHAR(100), -- CREATE, UPDATE, DELETE
    table_name VARCHAR(50),
    record_id INT,
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 54. Cấu hình hệ thống
CREATE TABLE system_configs (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 55. Mô hình gợi ý (AI Model Metadata)
CREATE TABLE recommendation_models (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(50),
    algorithm_type VARCHAR(100), -- Collaborative Filtering, Content-Based
    trained_at DATETIME,
    status ENUM('Active', 'Training', 'Deprecated')
);

-- 56. Kết quả gợi ý (Cache)
CREATE TABLE recommendation_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    model_id INT,
    recommended_book_ids JSON, -- Lưu mảng ID sách [1, 5, 9]
    confidence_score DECIMAL(5, 4), -- 0.0000 -> 1.0000
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES recommendation_models(model_id)
);