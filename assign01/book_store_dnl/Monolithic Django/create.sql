-- ================================
-- CREATE DATABASE
-- ================================
DROP DATABASE IF EXISTS book_store;
CREATE DATABASE book_store
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bookstore;

-- ================================
-- CUSTOMER TABLE
-- ================================
CREATE TABLE accounts_customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- ================================
-- BOOK TABLE
-- ================================
CREATE TABLE books_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price DOUBLE NOT NULL,
    stock INT NOT NULL
);

-- ================================
-- CART TABLE
-- ================================
CREATE TABLE cart_cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_customer
        FOREIGN KEY (customer_id)
        REFERENCES accounts_customer(id)
        ON DELETE CASCADE
);

-- ================================
-- CART ITEM TABLE
-- ================================
CREATE TABLE cart_cartitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    CONSTRAINT fk_cartitem_cart
        FOREIGN KEY (cart_id)
        REFERENCES cart_cart(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_book
        FOREIGN KEY (book_id)
        REFERENCES books_book(id)
        ON DELETE CASCADE
);
