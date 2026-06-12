"""
Update SQL script to set default images
Run this after running model.sql:
mysql -u root -p123456789 bookstore_db < update_default_images.sql
"""

USE bookstore_db;

-- Update all books to use default cover image
UPDATE Book 
SET CoverImage = 'books/default.png' 
WHERE CoverImage IS NULL OR CoverImage = '';

-- Update all customers to use default avatar
UPDATE Customer 
SET Avatar = 'avatars/default.png' 
WHERE Avatar IS NULL OR Avatar = '';

-- Show results
SELECT 'Books with cover images:', COUNT(*) FROM Book WHERE CoverImage IS NOT NULL AND CoverImage != '';
SELECT 'Customers with avatars:', COUNT(*) FROM Customer WHERE Avatar IS NOT NULL AND Avatar != '';

SELECT '✅ Default images updated successfully!' AS Status;
