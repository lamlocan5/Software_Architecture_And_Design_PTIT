"""
Script to set default images for all books and customers
Run this after creating some data in database:
python manage.py shell < set_default_images.py
"""

from store.models import Book, Customer

# Update all books without cover image
books_updated = Book.objects.filter(cover_image='').update(cover_image='books/default.png')
print(f"Updated {books_updated} books with default cover image")

# Update all books with None cover image
books_updated_null = Book.objects.filter(cover_image__isnull=True).update(cover_image='books/default.png')
print(f"Updated {books_updated_null} books with NULL cover image")

# Update all customers without avatar
customers_updated = Customer.objects.filter(avatar='').update(avatar='avatars/default.png')
print(f"Updated {customers_updated} customers with default avatar")

# Update all customers with None avatar
customers_updated_null = Customer.objects.filter(avatar__isnull=True).update(avatar='avatars/default.png')
print(f"Updated {customers_updated_null} customers with NULL avatar")

print("\n✅ Done! All empty images have been set to default.png")
