CREATE DATABASE IF NOT EXISTS product_db;
CREATE DATABASE IF NOT EXISTS behavior_db;

GRANT ALL PRIVILEGES ON product_db.* TO 'ecom_user'@'%';
GRANT ALL PRIVILEGES ON behavior_db.* TO 'ecom_user'@'%';
FLUSH PRIVILEGES;
