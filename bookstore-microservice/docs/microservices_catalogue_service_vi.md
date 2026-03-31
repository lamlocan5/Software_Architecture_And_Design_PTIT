## Tổng quan microservices trong dự án bookstore

- **Microservices**: hệ thống được tách thành nhiều service nhỏ, mỗi service chạy độc lập (mỗi thư mục `*-service` là một service).
- **Giao tiếp giữa các service**: qua HTTP REST API (ví dụ `catalogue-service` gọi `book-service`, `review-service`).
- **Triển khai**: dùng `docker-compose.yml` để chạy nhiều service cùng lúc, mỗi service có `Dockerfile` riêng, port riêng, volume riêng.
- **Ưu điểm**:
  - Dễ scale độc lập từng service.
  - Dễ deploy từng phần, giảm ảnh hưởng toàn hệ thống.
  - Mã nguồn mỗi service nhỏ, tập trung một nghiệp vụ.
- **Nhược điểm**:
  - Phức tạp hơn về networking, monitoring, logging.
  - Cần thiết kế rõ ràng boundary giữa các service.

Trong tài liệu này, ta sẽ phân tích chi tiết **`catalogue-service`** như một ví dụ microservice cụ thể.

---

## 1. Vai trò và kiến trúc tổng thể của `catalogue-service`

- **Mục đích**: tổng hợp dữ liệu từ:
  - **`book-service`**: trả về danh sách sách, thông tin sách.
  - **`review-service`**: trả về thống kê review (điểm trung bình, số lượng review).
- **Kết quả**: `catalogue-service` cung cấp API:
  - `GET /catalog/books/`: danh sách sách + thống kê review.
  - `GET /catalog/books/<id>/`: chi tiết 1 sách + thống kê review.
- **Kiểu service**: đây là một **composition/aggregation service** (service tổng hợp) – nó **không lưu dữ liệu** riêng mà **gọi sang service khác** rồi ghép kết quả.

Liên hệ với `docker-compose.yml`:

```yaml
services:
  catalogue-service:
    build: ./catalogue-service
    ports:
      - "8008:8000"
    volumes:
      - ./data/catalogue:/app/data
```

- **`build: ./catalogue-service`**: Docker build image cho service này từ thư mục `catalogue-service`.
- **`ports: "8008:8000"`**:
  - Port `8000` là port container Django run.
  - Port `8008` là port trên máy host, map tới `8000` trong container.
- **`volumes: ./data/catalogue:/app/data`**:
  - Map thư mục dữ liệu (VD: DB sqlite, file log) từ host vào container.

---

## 2. File `manage.py` – entrypoint cho Django của service

```12:21:catalogue-service/manage.py
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalogue_service.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        ...
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

- **`DJANGO_SETTINGS_MODULE`**:
  - Chỉ định Django dùng file settings: `catalogue_service.settings`.
  - Đây là nơi cấu hình DB, installed apps, middleware, v.v.
- **`execute_from_command_line(sys.argv)`**:
  - Cho phép chạy các lệnh Django: `python manage.py runserver`, `migrate`, `makemigrations`, v.v.
- Trong môi trường Docker, lệnh trong `Dockerfile` sẽ gọi `manage.py` nhiều lần:
  - `python manage.py makemigrations app`
  - `python manage.py migrate`
  - `python manage.py runserver 0.0.0.0:8000`

---

## 3. File `catalogue_service/settings.py` – cấu hình microservice

```1:21:catalogue-service/catalogue_service/settings.py
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-catalogue-service-secret-key-bookstore-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'rest_framework',
    'app',
]
```

- **`BASE_DIR`**: thư mục gốc của project Django (dùng để build path khác, như DB file).
- **`SECRET_KEY`**: khoá bí mật cho:
  - Ký session, CSRF token, password reset token.
  - Trong production phải để trong biến môi trường, không commit lên git.
- **`DEBUG = True`**:
  - Bật mode debug: log chi tiết lỗi.
  - Production nên `DEBUG = False`.
- **`ALLOWED_HOSTS = ['*']`**:
  - Cho phép tất cả host truy cập.
  - Production nên giới hạn domain cụ thể.
- **`INSTALLED_APPS`**:
  - Liệt kê app Django được load.
  - `rest_framework`: Django REST Framework – để tạo API.
  - `app`: ứng dụng business logic của `catalogue-service` (chứa `views.py`, `models.py`, `serializers.py`).

```23:31:catalogue-service/catalogue_service/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

- **Middleware** là các lớp xử lý request/response chung:
  - Bảo mật, session, CSRF, auth, message, clickjacking.

```33:50:catalogue-service/catalogue_service/settings.py
ROOT_URLCONF = 'catalogue_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'catalogue_service.wsgi.application'
```

- **`ROOT_URLCONF`**: trỏ tới file `catalogue_service/urls.py` để định nghĩa route.
- **`TEMPLATES`**: cấu hình engine template (mặc định Django, dù service này chủ yếu trả JSON).
- **`WSGI_APPLICATION`**: entrypoint WSGI nếu deploy bằng gunicorn/uWSGI.

```52:56:catalogue-service/catalogue_service/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}
```

- **Database**:
  - Dùng SQLite file nằm trong `BASE_DIR / 'data' / 'db.sqlite3'`.
  - Thư mục `data` map ra ngoài container bằng volume trong `docker-compose`.
  - Với `catalogue-service` hiện tại, DB chủ yếu là placeholder (ít dùng vì service chỉ aggregate từ service khác).

```59:66:catalogue-service/catalogue_service/settings.py
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

- Cấu hình ngôn ngữ, timezone, static url, default auto field.

---

## 4. File `catalogue_service/urls.py` – định nghĩa API endpoint của service

```1:10:catalogue-service/catalogue_service/urls.py
from django.contrib import admin
from django.urls import path
from app.views import CatalogueBookList, CatalogueBookDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('catalog/books/', CatalogueBookList.as_view()),
    path('catalog/books/<int:pk>/', CatalogueBookDetail.as_view()),
]
```

- **`urlpatterns`**: danh sách route.
- **`path('catalog/books/', CatalogueBookList.as_view())`**:
  - Khi có request `GET /catalog/books/`, Django gọi view `CatalogueBookList`.
- **`path('catalog/books/<int:pk>/', CatalogueBookDetail.as_view())`**:
  - `<int:pk>`: bắt tham số `pk` kiểu số nguyên (id sách).
  - URL ví dụ: `/catalog/books/1/`.

Trong microservices, mỗi service có **namespace URL riêng** (ở đây là `/catalog/...`) để tránh conflict.

---

## 5. File `app/views.py` – business logic tổng hợp dữ liệu

```1:9:catalogue-service/app/views.py
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


BOOK_SERVICE_URL = "http://book-service:8000"
REVIEW_SERVICE_URL = "http://review-service:8000"
```

- **`requests`**: thư viện HTTP client dùng để gọi sang microservice khác.
- **`BOOK_SERVICE_URL` / `REVIEW_SERVICE_URL`**:
  - Dùng hostname Docker service (`book-service`, `review-service`) và port `8000`.
  - Trong mạng internal của Docker Compose, `book-service` được Docker DNS resolve ra container tương ứng.

```11:19:catalogue-service/app/views.py
def _get(url, default=None):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code >= 400:
            return default if default is not None else []
        return r.json()
    except Exception:
        return default if default is not None else []
```

- **Hàm helper `_get`**:
  - Gửi `GET` với `timeout=3` giây.
  - Nếu status code >= 400 (lỗi client/server) → trả về `default` (hoặc `[]` nếu không truyền).
  - Nếu có exception (timeout, connection error, JSON parse lỗi, v.v.) → cũng trả về `default`.
- Đây là **pattern chống lỗi giữa các microservices**:
  - Không cho exception “văng” ra ngoài, mà xử lý thành default value.
  - Giúp `catalogue-service` vẫn trả về được response (dù thiếu dữ liệu).

### 5.1. View `CatalogueBookList` – danh sách sách + thống kê review

```21:44:catalogue-service/app/views.py
class CatalogueBookList(APIView):
    """
    GET /catalog/books/
    Trả về danh sách sách đã ghép thêm thống kê review (avg_rating, total_reviews).
    """

    def get(self, request):
        books = _get(f"{BOOK_SERVICE_URL}/books/", [])
        if not isinstance(books, list):
            return Response(
                {"detail": "Upstream book-service error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        for book in books:
            book_id = book.get("id")
            if not book_id:
                continue
            stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{book_id}/", {})
            if isinstance(stats, dict):
                book["avg_rating"] = stats.get("avg_rating", 0)
                book["total_reviews"] = stats.get("total_reviews", 0)

        return Response(books)
```

- **`class CatalogueBookList(APIView)`**:
  - Kế thừa `APIView` của DRF → hỗ trợ các method HTTP (`get`, `post`, …).
- **`books = _get(f"{BOOK_SERVICE_URL}/books/", [])`**:
  - Gửi HTTP GET tới `http://book-service:8000/books/`.
  - Nếu có lỗi, trả về `[]`.
- **`if not isinstance(books, list)`**:
  - Đảm bảo dữ liệu từ `book-service` là list.
  - Nếu không phải list → coi là lỗi upstream → trả về:
    - body `{"detail": "Upstream book-service error"}`.
    - HTTP status `502 BAD GATEWAY` (lỗi từ service phía sau).
- **Vòng lặp `for book in books:`**:
  - Lấy `book_id = book.get("id")`: nếu không có id thì `continue`.
  - Gọi tiếp sang `review-service`:

    ```python
    stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{book_id}/", {})
    ```

    - URL ví dụ: `http://review-service:8000/reviews/stats/1/`.
    - Nếu lỗi, trả về `{}`.

  - Nếu `stats` là dict:
    - `book["avg_rating"] = stats.get("avg_rating", 0)`
    - `book["total_reviews"] = stats.get("total_reviews", 0)`

  → Mỗi phần tử sách được enrich thêm 2 field thống kê review.

- **`return Response(books)`**:
  - DRF tự serialize list Python thành JSON.
  - Status mặc định `200 OK`.

**Ý nghĩa microservices**:
- `catalogue-service` **không tự lưu sách hay review**, chỉ:
  - Gọi `book-service` để lấy danh sách sách.
  - Gọi `review-service` để lấy thống kê.
  - Ghép dữ liệu lại và trả cho client.

### 5.2. View `CatalogueBookDetail` – chi tiết 1 sách + thống kê review

```47:73:catalogue-service/app/views.py
class CatalogueBookDetail(APIView):
    """
    GET /catalog/books/<id>/
    Trả về chi tiết 1 sách + thống kê review.
    """

    def get(self, request, pk):
        books = _get(f"{BOOK_SERVICE_URL}/books/", [])
        if not isinstance(books, list):
            return Response(
                {"detail": "Upstream book-service error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        book = next((b for b in books if b.get("id") == pk), None)
        if not book:
            return Response(
                {"detail": "Book not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{pk}/", {})
        if isinstance(stats, dict):
            book["avg_rating"] = stats.get("avg_rating", 0)
            book["total_reviews"] = stats.get("total_reviews", 0)

        return Response(book)
```

- **Route**: `GET /catalog/books/<id>/`.
- Logic:
  1. Gọi `book-service` để lấy **toàn bộ danh sách sách**.
  2. Tìm sách có `id == pk`:
     - Dùng `next((b for b in books if b.get("id") == pk), None)`.
  3. Nếu không tìm thấy → trả `404 Book not found`.
  4. Nếu tìm thấy:
     - Gọi `review-service` lấy stats:

       ```python
       stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{pk}/", {})
       ```

     - Ghép `avg_rating` và `total_reviews` vào `book`.
  5. Trả JSON của 1 sách.

**Lưu ý thiết kế**:
- Độ phức tạp: mỗi lần lấy detail 1 sách, service vẫn đang gọi `/books/` rồi lọc. Nếu dữ liệu lớn, có thể tối ưu:
  - `book-service` hỗ trợ endpoint `/books/<id>/`.
  - `catalogue-service` gọi thẳng endpoint detail thay vì lấy cả danh sách.

---

## 6. File `app/models.py` và `app/serializers.py` – placeholder cho domain riêng

```1:10:catalogue-service/app/models.py
class Placeholder(models.Model):
    """Placeholder model to keep app migrations simple; can be removed when real models are added."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
```

- **`Placeholder`**:
  - `abstract = True`: Django không tạo bảng DB cho model này.
  - Dùng như một base class chung sau này (nếu cần).
  - Ở trạng thái hiện tại, `catalogue-service` **không yêu cầu DB riêng** → chỉ dùng model placeholder cho dễ migrate.

```1:6:catalogue-service/app/serializers.py
class EmptySerializer(serializers.Serializer):
    """Serializer placeholder; real serializers can be added later if needed."""
    pass
```

- **`EmptySerializer`**:
  - Placeholder cho serializer, hiện chưa dùng.
  - Vì view hiện tại trả thẳng JSON từ các service khác, chưa cần mapping sang serializer.

---

## 7. File `Dockerfile` – cách đóng gói và chạy microservice

```1:12:catalogue-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "mkdir -p data && python manage.py makemigrations app && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

- **`FROM python:3.11-slim`**:
  - Image base: Python 3.11 nhẹ (slim).
- **`WORKDIR /app`**:
  - Đặt thư mục làm việc mặc định trong container.
- **`COPY requirements.txt .` + `RUN pip install ...`**:
  - Copy file requirements.
  - Cài thư viện Python (Django, DRF, requests, v.v.).
- **`COPY . .`**:
  - Copy toàn bộ code `catalogue-service` vào `/app` trong container.
- **`EXPOSE 8000`**:
  - Thông báo container sẽ lắng nghe port 8000.
- **`CMD`**:

  ```sh
  mkdir -p data \
  && python manage.py makemigrations app \
  && python manage.py migrate \
  && python manage.py runserver 0.0.0.0:8000
  ```

  - Tạo thư mục `data` (chứa DB SQLite).
  - Tạo migration cho app `app`.
  - Áp dụng migration.
  - Chạy server Django, lắng nghe `0.0.0.0:8000`.

Khi dùng `docker-compose up --build`, Docker sẽ:
- Build image từ `Dockerfile`.
- Chạy container, map port và volume như cấu hình trong `docker-compose.yml`.

---

## 8. Tóm tắt cách triển khai microservices từ ví dụ này

- **Cấu trúc mỗi microservice (ở mức cơ bản)**:
  - `manage.py`: entrypoint Django.
  - `<service_name>/settings.py`: cấu hình, DB, app.
  - `<service_name>/urls.py`: định nghĩa route API của service.
  - `app/views.py`: business logic, ở đây là **tổng hợp dữ liệu các service khác**.
  - `app/models.py`: model/domain riêng (hoặc placeholder nếu không cần).
  - `app/serializers.py`: mapping dữ liệu Python ↔ JSON (hoặc placeholder).
  - `Dockerfile`: cách build & chạy service.
- **Giao tiếp giữa các service**:
  - Dùng HTTP REST (`requests.get(...)`).
  - URL dùng hostname = tên service trong `docker-compose`.
  - Có xử lý lỗi cẩn thận (timeout, code >= 400).
- **Triển khai**:
  - Dùng `docker-compose.yml` để:
    - Khởi động nhiều service song song.
    - Cấu hình port, volumes, dependency (`depends_on`).

---

## 9. Gợi ý cho bạn khi học và mở rộng

- **Bước 1**: Dùng `docker-compose up --build` để chạy toàn bộ hệ thống, thử gọi:
  - `http://localhost:8008/catalog/books/`
  - `http://localhost:8008/catalog/books/1/`
- **Bước 2**: Mở thêm các service khác (`book-service`, `review-service`) để xem chúng định nghĩa models, views, serializers thế nào.
- **Bước 3**: Thử:
  - Thêm field mới ở `review-service` (ví dụ `five_star_count`) và ghép thêm ở `catalogue-service`.
  - Thêm một endpoint mới trong `catalogue_service/urls.py` và xử lý trong `app/views.py`.

Nếu bạn muốn, mình có thể tiếp tục viết thêm một file tương tự cho `book-service` hoặc `order-service` để bạn so sánh cách tổ chức giữa các microservice khác nhau.

