-- Tạo 4 databases riêng biệt cho từng service
CREATE DATABASE IF NOT EXISTS db_patient CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_clinical CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cấp quyền cho root user từ mọi host
GRANT ALL PRIVILEGES ON db_patient.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_clinical.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_billing.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_inventory.* TO 'root'@'%';
FLUSH PRIVILEGES;
