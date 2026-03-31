# Phân tích Strategic DDD trong codebase Bookstore Microservice

Tài liệu này trả lời câu hỏi: **Code của bạn có phần nào về Strategic DDD (Ubiquitous Language, Bounded Context, Context Mapping, Aggregate) không?** — và **chỉ rõ vị trí trong code**.

---

## 1. Khái niệm ngắn gọn

| Khái niệm | Ý nghĩa (Strategic DDD) |
|-----------|-------------------------|
| **Ubiquitous Language** | Ngôn ngữ thống nhất giữa domain và code: tên nghiệp vụ (Customer, Order, Cart, Book...) dùng nhất quán trong tên service, API, model, field. |
| **Bounded Context** | Ranh giới rõ ràng của một “ngữ cảnh” nghiệp vụ; mỗi context có model và ngôn ngữ riêng. Trong kiến trúc microservice, **mỗi service thường = 1 Bounded Context**. |
| **Context Mapping** | Mối quan hệ giữa các Bounded Context: ai gọi ai, phụ thuộc thế nào (Customer-Supplier, Conformist, ACL, v.v.). Thể hiện trong code qua **service gọi service** (HTTP, URL). |
| **Aggregate** | Nhóm entity/value object được bảo toàn cùng nhau; có **Aggregate Root** — mọi thay đổi đi qua root. Trong code thường là **model cha + model con (ForeignKey)** trong cùng một service. |

---

## 2. Ubiquitous Language (Ngôn ngữ phổ quát)

### Kết luận: **Có** — ngôn ngữ nghiệp vụ được dùng nhất quán trong tên service, API, model và field.

### 2.1 Tên service = tên Bounded Context / domain

- `customer-service` → **Customer**
- `book-service` → **Book** (và **Publisher**)
- `cart-service` → **Cart**
- `order-service` → **Order**
- `review-service` → **Review**
- `pay-service` → **Payment**
- `ship-service` → **Shipment**
- `catalogue-service` → **Catalogue** (danh mục sách + review)
- `staff-service` → **Staff**
- `manager-service` → **Manager**

**Vị trí:** tên thư mục và tên service trong `docker-compose.yml`:

- `docker-compose.yml` — các khối `customer-service`, `book-service`, `cart-service`, `order-service`, `review-service`, `pay-service`, `ship-service`, `catalogue-service`, `staff-service`, `manager-service`.

### 2.2 URL/API paths — từ vựng domain

| Từ vựng | Nơi xuất hiện trong code |
|---------|---------------------------|
| `customers/` | `customer-service/app/urls.py`: `path('customers/', ...)` |
| `books/`, `publishers/` | `book-service/book_service/urls.py`: `path('books/', ...)`, `path('publishers/', ...)` |
| `carts/`, `carts/<customer_id>/` | `cart-service/cart_service/urls.py`: `path('carts/', ...)`, `path('carts/<int:customer_id>/', ...)` |
| `orders/`, `orders/<order_id>/` | `order-service/order_service/urls.py`: `path('orders/', ...)`, `path('orders/<order_id>/', ...)` |
| `reviews/`, `reviews/stats/<book_id>/` | `review-service/review_service/urls.py`: `path('reviews/', ...)`, `path('reviews/stats/<int:book_id>/', ...)` |
| `payments/`, `shipments/` | `pay-service/pay_service/urls.py`, `ship-service/ship_service/urls.py` |
| `catalog/books/` | `catalogue-service/catalogue_service/urls.py`: `path('catalog/books/', ...)` |
| `staff/`, `managers/` | `staff-service/.../urls.py`, `manager-service/.../urls.py` |

**Vị trí:** toàn bộ file `*/urls.py` của từng service (đường dẫn ở bảng trên).

### 2.3 Model và field — ngôn ngữ nghiệp vụ trong dữ liệu

- **Customer:** `customer-service/app/models.py` — `Customer`: `name`, `email`.
- **Book, Publisher:** `book-service/app/models.py` — `Book`: `title`, `author`, `price`, `stock`, `publisher` (FK); `Publisher`: `name`, `address`, `mail`.
- **Cart, CartItem:** `cart-service/app/models.py` — `Cart`: `customer_id`; `CartItem`: `cart`, `book_id`, `quantity`.
- **Order, OrderItem:** `order-service/app/models.py` — `Order`: `customer_id`, `status`, `total_amount`, `created_at`; `OrderItem`: `order`, `book_id`, `quantity`, `price_at_order`.
- **Review:** `review-service/app/models.py` — `Review`: `book_id`, `customer_id`, `rating`, `comment`, `book_title`, `customer_name`.
- **Payment:** `pay-service/app/models.py` — `Payment`: `order_id`, `customer_id`, `amount`, `method`, `status`, `transaction_id`.
- **Shipment:** `ship-service/app/models.py` — `Shipment`: `order_id`, `receiver_name`, `address`, `carrier`, `tracking_number`, `status`.
- **Staff, Manager:** `staff-service/app/models.py`, `manager-service/app/models.py` — `name`, `email`, `active`.

**Trạng thái nghiệp vụ (status) dùng từ domain:**

- **Order** (`order-service/app/models.py`): `pending`, `confirmed`, `shipping`, `delivered`, `cancelled` (kèm nhãn tiếng Việt).
- **Payment** (`pay-service/app/models.py`): `initiated`, `paid`, `failed`, `refunded`, `cancelled`.
- **Shipment** (`ship-service/app/models.py`): `pending`, `picked`, `shipping`, `delivered`, `failed`, `cancelled`.

**Tóm tắt:** Ubiquitous Language thể hiện ở **tên service, đường dẫn API, tên model và tên field** — đều dùng từ vựng nghiệp vụ (customer, order, cart, book, review, payment, shipment, publisher, staff, manager) nhất quán.

---

## 3. Bounded Context (Bối cảnh giới hạn)

### Kết luận: **Có** — mỗi microservice đóng vai trò một Bounded Context riêng.

Trong DDD, Bounded Context là ranh giới trong đó một model và ngôn ngữ có ý nghĩa rõ ràng. Trong kiến trúc của bạn, **mỗi service = một context** với DB và API riêng.

| Bounded Context | Service (thư mục) | Nội dung chính |
|-----------------|-------------------|----------------|
| **Customer** | `customer-service/` | Khách hàng (đăng ký, thông tin). |
| **Book / Catalog** | `book-service/` | Sách, nhà xuất bản. |
| **Cart** | `cart-service/` | Giỏ hàng, dòng giỏ (CartItem). |
| **Order** | `order-service/` | Đơn hàng, dòng đơn (OrderItem). |
| **Review** | `review-service/` | Đánh giá sách (rating, comment). |
| **Payment** | `pay-service/` | Thanh toán (payment, method, status). |
| **Shipping** | `ship-service/` | Vận chuyển (shipment, carrier, tracking). |
| **Catalogue (read model)** | `catalogue-service/` | Danh mục “sách + thống kê review” — tổng hợp từ Book + Review. |
| **Staff** | `staff-service/` | Nhân viên. |
| **Manager** | `manager-service/` | Quản lý. |

**Vị trí trong code:**

- **Cấu trúc thư mục:** mỗi thư mục `*-service/` là một context (ví dụ: `book-service/`, `order-service/`, `cart-service/`, ...).
- **Cấu hình triển khai:** `docker-compose.yml` — mỗi service có `build`, `ports`, `volumes` riêng → tách biệt runtime và dữ liệu.
- **Tài liệu kiến trúc:** `docs/architecture/architecture.md` — từng sơ đồ theo từng service, tương ứng từng context.

**Lưu ý:** `catalogue-service` là context “tổng hợp” (composition): không sở hữu dữ liệu gốc mà đọc từ Book và Review — trong DDD có thể xem là **read model / Bounded Context phụ thuộc** vào hai context kia.

---

## 4. Context Mapping (Bản đồ quan hệ giữa các context)

### Kết luận: **Có** — quan hệ giữa các Bounded Context được thể hiện rõ qua **service gọi service** (HTTP).

Context mapping mô tả **ai phụ thuộc ai** và **giao tiếp thế nào**. Trong code của bạn, điều này thể hiện qua:

- Biến URL của service khác (ví dụ `CART_SERVICE_URL`, `BOOK_SERVICE_URL`).
- Gọi HTTP (GET/POST/PATCH) từ service này sang service kia.

### 4.1 Customer Context → Cart Context (tạo giỏ khi tạo khách hàng)

**Quan hệ:** Khi tạo **Customer**, hệ thống tự tạo **Cart** — Customer là “khách hàng” của Cart (theo nghĩa DDD: Customer context điều phối với Cart context).

**Vị trí trong code:**

- `customer-service/app/views.py` (class `CustomerListCreate`, method `post`):

```python
CART_SERVICE_URL = "http://cart-service:8000"
# ...
customer = serializer.save()
# call cart service
requests.post(
    f"{CART_SERVICE_URL}/carts/",
    json={"customer_id": customer.id}
)
```

- **URL được gọi:** `POST http://cart-service:8000/carts/` với `{"customer_id": customer.id}`.

Đây là **Context Mapping** dạng “một context gọi API của context kia” (có thể mô tả là **Customer-Supplier** hoặc **Conformist** tùy cách bạn đặt tên: Customer “đặt hàng” Cart context tạo giỏ).

### 4.2 Catalogue Context → Book Context và Review Context

**Quan hệ:** Catalogue là context tổng hợp; nó **đọc** từ Book và Review.

**Vị trí trong code:**

- `catalogue-service/app/views.py`:

```python
BOOK_SERVICE_URL = "http://book-service:8000"
REVIEW_SERVICE_URL = "http://review-service:8000"
# ...
# Trong CatalogueBookList.get():
books = _get(f"{BOOK_SERVICE_URL}/books/", [])
# ...
stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{book_id}/", {})
```

- **Mapping:** Catalogue → Book (GET `/books/`), Catalogue → Review (GET `/reviews/stats/<book_id>/`).

Có thể xem Catalogue là **Downstream**, Book và Review là **Upstream** (Catalogue phụ thuộc vào hai context đó).

### 4.3 API Gateway → tất cả các context

**Quan hệ:** Gateway là điểm vào; nó **gọi tất cả** các service (các Bounded Context).

**Vị trí trong code:**

- `api-gateway/api_gateway/views.py` — đầu file:

```python
BOOK_SERVICE_URL      = "http://book-service:8000"
CATALOGUE_SERVICE_URL = "http://catalogue-service:8000"
CART_SERVICE_URL      = "http://cart-service:8000"
CUSTOMER_SERVICE_URL  = "http://customer-service:8000"
ORDER_SERVICE_URL     = "http://order-service:8000"
REVIEW_SERVICE_URL    = "http://review-service:8000"
SHIP_SERVICE_URL      = "http://ship-service:8000"
PAY_SERVICE_URL       = "http://pay-service:8000"
STAFF_SERVICE_URL     = "http://staff-service:8000"
MANAGER_SERVICE_URL   = "http://manager-service:8000"
RECOMMENDER_SERVICE_URL = "http://recommender-ai-service:8000"
```

- Các view trong cùng file gọi `_get(..., url)`, `_post(...)` tới các URL trên → đây chính là **bản đồ phụ thuộc** Gateway → từng context.

### 4.4 Tóm tắt Context Mapping (trong code)

| Nguồn (caller) | Đích (callee) | Vị trí code | Hành động |
|----------------|---------------|-------------|-----------|
| customer-service | cart-service | `customer-service/app/views.py` (POST customer → POST /carts/) | Tạo cart khi tạo customer |
| catalogue-service | book-service | `catalogue-service/app/views.py` (`BOOK_SERVICE_URL`, _get) | GET /books/ |
| catalogue-service | review-service | `catalogue-service/app/views.py` (`REVIEW_SERVICE_URL`, _get) | GET /reviews/stats/<id>/ |
| api-gateway | mọi service | `api-gateway/api_gateway/views.py` (các *_SERVICE_URL và _get/_post) | Điều hướng request tới từng context |

Tài liệu kiến trúc tổng thể: `docs/architecture/architecture.md` — các sơ đồ mô tả luồng giữa gateway và từng service, tương ứng với mapping trên.

---

## 5. Aggregate (Tổng thể nhất quán)

### Kết luận: **Có** — một số service có cấu trúc **một root entity + entity con** (ForeignKey), tương ứng với khái niệm Aggregate (root + thành phần trong cùng boundary).

Trong DDD, Aggregate là nhóm entity được cập nhật cùng nhau, với **một Aggregate Root**; bên ngoài chỉ tham chiếu tới root. Trong code của bạn, điều này thể hiện qua **model cha (root) + model con (FK tới cha)** trong **cùng một service**.

### 5.1 Order Aggregate (order-service)

- **Root:** `Order`
- **Thành phần trong aggregate:** `OrderItem` — thuộc một Order, xóa theo Order (`on_delete=models.CASCADE`).

**Vị trí:**

- `order-service/app/models.py`:

```python
class Order(models.Model):
    customer_id  = models.IntegerField()
    status       = models.CharField(...)
    total_amount = models.DecimalField(...)
    created_at   = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_id        = models.IntegerField()
    quantity       = models.IntegerField()
    price_at_order = models.DecimalField(...)
```

- Mọi thay đổi “đơn hàng” (thêm/sửa/xóa dòng) đều thông qua Order và các OrderItem của nó trong cùng service → **Order là Aggregate Root**, OrderItem nằm trong boundary của Order.

### 5.2 Cart Aggregate (cart-service)

- **Root:** `Cart`
- **Thành phần:** `CartItem` — thuộc một Cart, xóa theo Cart.

**Vị trí:**

- `cart-service/app/models.py`:

```python
class Cart(models.Model):
    customer_id = models.IntegerField()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book_id = models.IntegerField()
    quantity = models.IntegerField()
```

- Tương tự: Cart là root, CartItem là phần tử trong aggregate; chỉ thao tác qua Cart (và các item của nó) trong cart-service.

### 5.3 Book và Publisher (book-service)

- **Publisher** và **Book** cùng nằm trong book-service; **Book** có `ForeignKey` tới **Publisher**.
- Có thể xem **Book** là root của một aggregate “Sách” (với tham chiếu tới Publisher), hoặc xem **Publisher** là root với tập **books** (related_name='books'). Tùy nghiệp vụ: nếu mọi thao tác chính đi qua “sách” thì Book là root; nếu có thao tác “theo nhà xuất bản” rõ ràng thì có thể có thêm aggregate Publisher. Trong code hiện tại, **Book** có quan hệ rõ ràng với Publisher → có cấu trúc **aggregate-like** trong cùng Bounded Context.

**Vị trí:**

- `book-service/app/models.py`:

```python
class Publisher(models.Model):
    name    = models.CharField(max_length=255)
    address = models.TextField(...)
    mail    = models.EmailField(unique=True)

class Book(models.Model):
    title     = models.CharField(max_length=255)
    author    = models.CharField(max_length=255)
    price     = models.DecimalField(...)
    stock     = models.IntegerField()
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
```

### 5.4 Các entity đơn (không có “con” trong cùng service)

- **Customer** (`customer-service/app/models.py`): một model, không có entity con → có thể xem là aggregate một thành phần (root = Customer).
- **Review** (`review-service/app/models.py`): một model → aggregate đơn.
- **Payment** (`pay-service/app/models.py`): một model, tham chiếu `order_id` (ID từ context khác) → không phải aggregate con của Order trong cùng service; Payment là aggregate root trong Pay context.
- **Shipment** (`ship-service/app/models.py`): tương tự, `order_id` là tham chiếu sang context Order → Shipment là aggregate root trong Ship context.
- **Staff**, **Manager**: mỗi service một model đơn → aggregate đơn.

**Tóm tắt Aggregate trong code:**

| Bounded Context (service) | Aggregate Root | Thành phần (trong cùng service) | File |
|--------------------------|----------------|----------------------------------|------|
| order-service | Order | OrderItem | `order-service/app/models.py` |
| cart-service | Cart | CartItem | `cart-service/app/models.py` |
| book-service | Book (và/hoặc Publisher) | Book ↔ Publisher | `book-service/app/models.py` |
| customer-service | Customer | — | `customer-service/app/models.py` |
| review-service | Review | — | `review-service/app/models.py` |
| pay-service | Payment | — | `pay-service/app/models.py` |
| ship-service | Shipment | — | `ship-service/app/models.py` |
| staff-service | Staff | — | `staff-service/app/models.py` |
| manager-service | Manager | — | `manager-service/app/models.py` |

---

## 6. Tổng kết

| Strategic DDD Concept | Có trong code? | Nơi thể hiện chính |
|-----------------------|----------------|--------------------|
| **Ubiquitous Language** | Có | Tên service (docker-compose, thư mục), URL (các file `urls.py`), tên model và field (các file `models.py`), status và từ vựng nghiệp vụ. |
| **Bounded Context** | Có | Mỗi microservice = 1 context: cấu trúc thư mục `*-service/`, `docker-compose.yml`, `docs/architecture/architecture.md`. |
| **Context Mapping** | Có | `customer-service/app/views.py` → cart-service; `catalogue-service/app/views.py` → book-service, review-service; `api-gateway/api_gateway/views.py` → mọi service. |
| **Aggregate** | Có | Order + OrderItem (`order-service/app/models.py`), Cart + CartItem (`cart-service/app/models.py`), Book + Publisher (`book-service/app/models.py`); các entity đơn còn lại là aggregate một thành phần. |

Code của bạn **có** các yếu tố Strategic DDD: ngôn ngữ thống nhất, tách theo từng context (microservice), quan hệ giữa context qua HTTP, và cấu trúc aggregate (root + con) trong từng service. Tài liệu này chỉ rõ từng khái niệm và **vị trí file/đoạn code** tương ứng để bạn đối chiếu khi học hoặc báo cáo.
