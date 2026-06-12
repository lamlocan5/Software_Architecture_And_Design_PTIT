-- ============================================
-- Django Bookstore Database Schema
-- MySQL Script
-- ============================================

-- Drop database if exists and create new one
DROP DATABASE IF EXISTS bookstore_db;
CREATE DATABASE bookstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_db;

-- ============================================
-- Customer Tables
-- ============================================

-- Customer Table
CREATE TABLE Customer (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    FullName VARCHAR(100) NOT NULL,
    Phone VARCHAR(20),
    Avatar VARCHAR(255),
    INDEX idx_username (Username),
    INDEX idx_email (Email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Address Table
CREATE TABLE Address (
    AddressID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    Street VARCHAR(255) NOT NULL,
    City VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    PostalCode VARCHAR(20) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    INDEX idx_customer (CustomerID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Book Catalog Tables
-- ============================================

-- Author Table
CREATE TABLE Author (
    AuthorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Biography TEXT,
    INDEX idx_name (Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Publisher Table
CREATE TABLE Publisher (
    PublisherID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    Email VARCHAR(100),
    Phone VARCHAR(20),
    INDEX idx_name (Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Category Table
CREATE TABLE Category (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    INDEX idx_name (Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Table
CREATE TABLE Book (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    ISBN VARCHAR(20) NOT NULL UNIQUE,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Stock INT NOT NULL DEFAULT 0,
    PublishedDate DATE,
    CoverImage VARCHAR(255),
    PublisherID INT,
    FOREIGN KEY (PublisherID) REFERENCES Publisher(PublisherID) ON DELETE SET NULL,
    INDEX idx_title (Title),
    INDEX idx_isbn (ISBN),
    INDEX idx_publisher (PublisherID),
    INDEX idx_price (Price),
    INDEX idx_published_date (PublishedDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BookAuthor Junction Table (Many-to-Many)
CREATE TABLE BookAuthor (
    BookID INT NOT NULL,
    AuthorID INT NOT NULL,
    PRIMARY KEY (BookID, AuthorID),
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    FOREIGN KEY (AuthorID) REFERENCES Author(AuthorID) ON DELETE CASCADE,
    INDEX idx_book (BookID),
    INDEX idx_author (AuthorID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- BookCategory Junction Table (Many-to-Many)
CREATE TABLE BookCategory (
    BookID INT NOT NULL,
    CategoryID INT NOT NULL,
    PRIMARY KEY (BookID, CategoryID),
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID) ON DELETE CASCADE,
    INDEX idx_book (BookID),
    INDEX idx_category (CategoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review Table
CREATE TABLE Review (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT NOT NULL,
    CustomerID INT NOT NULL,
    Rating INT NOT NULL CHECK (Rating >= 1 AND Rating <= 5),
    Comment TEXT,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    UNIQUE KEY unique_review (BookID, CustomerID),
    INDEX idx_book (BookID),
    INDEX idx_customer (CustomerID),
    INDEX idx_rating (Rating),
    INDEX idx_created_at (CreatedAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Order and Shopping Tables
-- ============================================

-- Order Table
CREATE TABLE `Order` (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    OrderDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    PaymentMethod VARCHAR(50) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    INDEX idx_customer (CustomerID),
    INDEX idx_order_date (OrderDate),
    INDEX idx_status (Status),
    CHECK (Status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- OrderItem Table
CREATE TABLE OrderItem (
    OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    BookID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    Price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    INDEX idx_order (OrderID),
    INDEX idx_book (BookID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart Table
CREATE TABLE Cart (
    CartID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    BookID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    AddedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (CustomerID, BookID),
    INDEX idx_customer (CustomerID),
    INDEX idx_book (BookID),
    INDEX idx_added_at (AddedAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Wishlist Table
CREATE TABLE Wishlist (
    WishlistID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    BookID INT NOT NULL,
    AddedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Book(BookID) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist_item (CustomerID, BookID),
    INDEX idx_customer (CustomerID),
    INDEX idx_book (BookID),
    INDEX idx_added_at (AddedAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Shipping Table
CREATE TABLE Shipping (
    ShippingID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL UNIQUE,
    AddressID INT,
    ShippingMethod VARCHAR(50) NOT NULL DEFAULT 'Standard',
    TrackingNumber VARCHAR(100),
    EstimatedDelivery DATE,
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (AddressID) REFERENCES Address(AddressID) ON DELETE SET NULL,
    INDEX idx_order (OrderID),
    INDEX idx_address (AddressID),
    INDEX idx_tracking (TrackingNumber),
    CHECK (ShippingMethod IN ('Standard', 'Express', 'Overnight'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Staff Table
-- ============================================

-- Staff Table
CREATE TABLE Staff (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    FullName VARCHAR(100) NOT NULL,
    Role VARCHAR(50) NOT NULL DEFAULT 'Sales',
    HireDate DATE NOT NULL,
    INDEX idx_username (Username),
    INDEX idx_email (Email),
    INDEX idx_role (Role),
    CHECK (Role IN ('Admin', 'Manager', 'Sales', 'Support'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Sample Data (Optional)
-- ============================================

-- Insert sample authors
INSERT INTO Author (Name, Biography) VALUES
('Nguyễn Nhật Ánh', 'Nhà văn Việt Nam nổi tiếng với nhiều tác phẩm văn học thiếu nhi'),
('Paulo Coelho', 'Brazilian lyricist and novelist, best known for The Alchemist'),
('J.K. Rowling', 'British author, best known for the Harry Potter series'),
('Haruki Murakami', 'Japanese writer, his books have been bestsellers in Japan');

-- Insert sample publishers
INSERT INTO Publisher (Name, Address, Email, Phone) VALUES
('NXB Trẻ', 'TP. Hồ Chí Minh, Việt Nam', 'nxbtre@example.com', '028-12345678'),
('NXB Kim Đồng', 'Hà Nội, Việt Nam', 'nxbkimdong@example.com', '024-98765432'),
('HarperCollins', 'New York, USA', 'info@harpercollins.com', '+1-212-555-0100'),
('Penguin Books', 'London, UK', 'info@penguin.com', '+44-20-7555-0100');

-- Insert sample categories
INSERT INTO Category (Name, Description) VALUES
('Văn học Việt Nam', 'Sách văn học của các tác giả Việt Nam'),
('Văn học nước ngoài', 'Sách văn học được dịch từ nước ngoài'),
('Thiếu nhi', 'Sách dành cho trẻ em và thanh thiếu niên'),
('Kỹ năng sống', 'Sách về phát triển bản thân và kỹ năng sống'),
('Tiểu thuyết', 'Tiểu thuyết các thể loại'),
('Triết học', 'Sách về triết học và tư tưởng');

-- Insert sample books
INSERT INTO Book (Title, ISBN, Description, Price, Stock, PublishedDate, PublisherID) VALUES
('Tôi Thấy Hoa Vàng Trên Cỏ Xanh', '978-604-1-00001-0', 'Tác phẩm văn học xuất sắc của Nguyễn Nhật Ánh', 85000, 100, '2010-12-01', 1),
('Mắt Biếc', '978-604-1-00002-7', 'Câu chuyện tình yêu thuở học trò đầy cảm xúc', 95000, 80, '2008-05-15', 1),
('The Alchemist', '978-0-06-112241-5', 'A philosophical story about following your dreams', 150000, 50, '1988-01-01', 3),
('Harry Potter and the Sorcerer''s Stone', '978-0-439-70818-8', 'The first book in the Harry Potter series', 180000, 75, '1997-06-26', 3),
('Norwegian Wood', '978-0-375-70427-7', 'A nostalgic story of loss and burgeoning sexuality', 165000, 60, '1987-09-04', 4);

-- Link books to authors
INSERT INTO BookAuthor (BookID, AuthorID) VALUES
(1, 1), (2, 1), (3, 2), (4, 3), (5, 4);

-- Link books to categories
INSERT INTO BookCategory (BookID, CategoryID) VALUES
(1, 1), (1, 5),
(2, 1), (2, 5),
(3, 2), (3, 6),
(4, 2), (4, 3), (4, 5),
(5, 2), (5, 5);

-- Insert sample staff
INSERT INTO Staff (Username, Password, Email, FullName, Role, HireDate) VALUES
('admin', 'pbkdf2_sha256$600000$dummy$hash', 'admin@bookstore.com', 'Administrator', 'Admin', '2023-01-01'),
('manager1', 'pbkdf2_sha256$600000$dummy$hash', 'manager@bookstore.com', 'Store Manager', 'Manager', '2023-02-15'),
('sales1', 'pbkdf2_sha256$600000$dummy$hash', 'sales@bookstore.com', 'Sales Staff', 'Sales', '2023-06-01');

-- ============================================
-- Views for Common Queries (Optional)
-- ============================================

-- View: Books with average rating
CREATE VIEW vw_books_with_rating AS
SELECT 
    b.BookID,
    b.Title,
    b.ISBN,
    b.Price,
    b.Stock,
    p.Name AS Publisher,
    COALESCE(AVG(r.Rating), 0) AS AvgRating,
    COUNT(r.ReviewID) AS ReviewCount
FROM Book b
LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
LEFT JOIN Review r ON b.BookID = r.BookID
GROUP BY b.BookID, b.Title, b.ISBN, b.Price, b.Stock, p.Name;

-- View: Customer order summary
CREATE VIEW vw_customer_orders AS
SELECT 
    c.CustomerID,
    c.Username,
    c.FullName,
    COUNT(o.OrderID) AS TotalOrders,
    COALESCE(SUM(o.TotalAmount), 0) AS TotalSpent
FROM Customer c
LEFT JOIN `Order` o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.Username, c.FullName;

-- ============================================
-- Stored Procedures (Optional)
-- ============================================

DELIMITER //

-- Procedure: Get book details with authors and categories
CREATE PROCEDURE sp_GetBookDetails(IN p_BookID INT)
BEGIN
    -- Book basic info
    SELECT 
        b.*,
        p.Name AS PublisherName,
        COALESCE(AVG(r.Rating), 0) AS AvgRating
    FROM Book b
    LEFT JOIN Publisher p ON b.PublisherID = p.PublisherID
    LEFT JOIN Review r ON b.BookID = r.BookID
    WHERE b.BookID = p_BookID
    GROUP BY b.BookID;
    
    -- Authors
    SELECT a.AuthorID, a.Name
    FROM Author a
    INNER JOIN BookAuthor ba ON a.AuthorID = ba.AuthorID
    WHERE ba.BookID = p_BookID;
    
    -- Categories
    SELECT c.CategoryID, c.Name
    FROM Category c
    INNER JOIN BookCategory bc ON c.CategoryID = bc.CategoryID
    WHERE bc.BookID = p_BookID;
END //

-- Procedure: Create order from cart
CREATE PROCEDURE sp_CreateOrderFromCart(
    IN p_CustomerID INT,
    IN p_AddressID INT,
    IN p_PaymentMethod VARCHAR(50),
    IN p_ShippingMethod VARCHAR(50),
    OUT p_OrderID INT
)
BEGIN
    DECLARE v_TotalAmount DECIMAL(10, 2);
    
    -- Start transaction
    START TRANSACTION;
    
    -- Calculate total from cart
    SELECT SUM(b.Price * c.Quantity) INTO v_TotalAmount
    FROM Cart c
    INNER JOIN Book b ON c.BookID = b.BookID
    WHERE c.CustomerID = p_CustomerID;
    
    -- Create order
    INSERT INTO `Order` (CustomerID, TotalAmount, PaymentMethod)
    VALUES (p_CustomerID, v_TotalAmount, p_PaymentMethod);
    
    SET p_OrderID = LAST_INSERT_ID();
    
    -- Create order items from cart
    INSERT INTO OrderItem (OrderID, BookID, Quantity, Price)
    SELECT p_OrderID, c.BookID, c.Quantity, b.Price
    FROM Cart c
    INNER JOIN Book b ON c.BookID = b.BookID
    WHERE c.CustomerID = p_CustomerID;
    
    -- Update book stock
    UPDATE Book b
    INNER JOIN Cart c ON b.BookID = c.BookID
    SET b.Stock = b.Stock - c.Quantity
    WHERE c.CustomerID = p_CustomerID;
    
    -- Create shipping record
    INSERT INTO Shipping (OrderID, AddressID, ShippingMethod)
    VALUES (p_OrderID, p_AddressID, p_ShippingMethod);
    
    -- Clear cart
    DELETE FROM Cart WHERE CustomerID = p_CustomerID;
    
    COMMIT;
END //

DELIMITER ;

-- ============================================
-- End of Script
-- ============================================

-- Show all tables
SHOW TABLES;

-- Display table structures (uncomment if needed)
-- DESCRIBE Customer;
-- DESCRIBE Book;
-- DESCRIBE `Order`;
