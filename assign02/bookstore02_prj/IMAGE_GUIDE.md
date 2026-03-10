# 🖼️ Hướng dẫn sử dụng ảnh mặc định

## Cấu trúc thư mục

```
media/
├── books/
│   └── default.png       # Ảnh mặc định cho cover sách
└── avatars/
    └── default.png       # Ảnh mặc định cho avatar khách hàng
```

## Đã thực hiện

✅ Tạo thư mục `media/books/` và `media/avatars/`  
✅ Copy `anh1.png` vào cả 2 thư mục như `default.png`  
✅ Tạo script Python để update database  
✅ Tạo script SQL để update database

## Cách sử dụng

### Option 1: Dùng Python Script (Sau khi migrate)

```bash
python manage.py shell < set_default_images.py
```

Script này sẽ:
- Update tất cả Book có `cover_image` NULL hoặc rỗng → `books/default.png`
- Update tất cả Customer có `avatar` NULL hoặc rỗng → `avatars/default.png`

### Option 2: Dùng SQL Script (Trực tiếp vào database)

```bash
mysql -u root -p123456789 bookstore_db < update_default_images.sql
```

### Option 3: Thêm ảnh khi tạo dữ liệu mới

Khi thêm sách mới trong admin panel hoặc shell:

```python
from store.models import Book, Publisher

publisher = Publisher.objects.first()

book = Book.objects.create(
    title="Sách mới",
    isbn="978-123-456-789-0",
    description="Mô tả sách",
    price=100000,
    stock=50,
    cover_image='books/default.png',  # <-- Chỉ định ảnh mặc định
    publisher=publisher
)
```

## Thay đổi ảnh mặc định

Để thay ảnh mặc định khác:

```bash
# Copy ảnh mới vào
copy "C:\path\to\your\image.png" media\books\default.png
copy "C:\path\to\your\image.png" media\avatars\default.png

# Sau đó chạy lại script update
python manage.py shell < set_default_images.py
```

## Upload ảnh mới qua Admin Panel

1. Truy cập `http://localhost:8000/admin/`
2. Chọn Books hoặc Customers
3. Click vào item muốn edit
4. Upload ảnh mới tại field "Cover image" hoặc "Avatar"
5. Save

Ảnh sẽ được lưu vào:
- `media/books/tên_file.png` cho cover
- `media/avatars/tên_file.png` cho avatar

## Hiển thị ảnh trong template

Template đã được cấu hình sẵn để hiển thị ảnh:

```html
<!-- Book cover -->
{% if book.cover_image %}
    <img src="{{ book.cover_image.url }}" alt="{{ book.title }}">
{% else %}
    <div>No Image</div>
{% endif %}

<!-- Customer avatar -->
{% if customer.avatar %}
    <img src="{{ customer.avatar.url }}" alt="{{ customer.username }}">
{% endif %}
```

## Lưu ý

- Đảm bảo `MEDIA_URL` và `MEDIA_ROOT` đã được cấu hình trong `settings.py` ✅
- Trong development, Django tự động serve media files ✅
- Trong production, cần cấu hình web server (nginx/apache) để serve `media/`
