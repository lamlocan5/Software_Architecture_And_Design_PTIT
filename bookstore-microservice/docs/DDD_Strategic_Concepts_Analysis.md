# Phân tích Strategic DDD trong codebase Bookstore Microservice

Tài liệu này trả lời câu hỏi: **Code của bạn có phần nào về Strategic DDD (Ubiquitous Language, Bounded Context, Context Mapping, Aggregate) không?** — và **chỉ rõ vị trí trong code**.

---

## 1. Khái niệm ngắn gọn

| Khái niệm | Ý nghĩa (Strategic DDD) |
|-----------|-------------------------|
| **Ubiquitous Language** | Ngôn ngữ thống nhất giữa domain và code: tên nghiệp vụ (Customer, Order, Cart, Product...) dùng nhất quán trong tên service, API, model, field. |
| **Bounded Context** | Ranh giới rõ ràng của một “ngữ cảnh” nghiệp vụ; mỗi context có model và ngôn ngữ riêng. Trong kiến trúc microservice, **mỗi service thường = 1 Bounded Context**. |
| **Context Mapping** | Mối quan hệ giữa các Bounded Context: ai phụ thuộc ai, giao tiếp thế nào (Customer-Supplier, Conformist, ACL, v.v.). Thể hiện trong code qua **REST HTTP API** hoặc **Asynchronous Message Pub/Sub**. |
| **Aggregate** | Nhóm entity/value object được bảo toàn cùng nhau; có **Aggregate Root** — mọi thay đổi đi qua root. Trong code thường là **model cha + model con (ForeignKey)** trong cùng một service. |

---

## 2. Ubiquitous Language (Ngôn ngữ phổ quát)

### Kết luận: **Có** — ngôn ngữ nghiệp vụ được dùng nhất quán trong tên service, API, model và field.

### 2.1 Tên service = tên Bounded Context / domain

- `user-service` → **User** (quản lý Customer, Staff, Manager)
- `product-service` → **Product** (quản lý Book, Clothing, Electronic, Publisher, Category)
- `cart-service` → **Cart**
- `order-service` → **Order**
- `review-service` → **Review**
- `payment-service` → **Payment**
- `shipping-service` → **Shipment / Shipping**
- `catalogue-service` → **Catalogue** (tổng hợp danh mục sản phẩm + review)
- `notification-service` → **Notification** (nhật ký thông báo bất đồng bộ)
- `ai-service` → **AI Service / Recommendation** (gợi ý sản phẩm thông minh)
- `frontend` → **Frontend / UI Layer**

**Vị trí:** Tên thư mục dự án và tên service trong `docker-compose.yml`.

### 2.2 URL/API paths — từ vựng domain

| Từ vựng | Nơi xuất hiện trong code |
|---------|---------------------------|
| `customers/`, `staff/`, `managers/` | `user-service/app/urls.py` |
| `products/`, `publishers/`, `categories/` | `product-service/product_service/urls.py` |
| `carts/`, `carts/add-item/` | `cart-service/cart_service/urls.py` |
| `orders/`, `orders/<order_id>/` | `order-service/order_service/urls.py` |
| `reviews/`, `reviews/stats/<product_id>/` | `review-service/review_service/urls.py` |
| `payments/` | `payment-service/pay_service/urls.py` |
| `shipments/` | `shipping-service/ship_service/urls.py` |
| `catalog/books/` | `catalogue-service/catalogue_service/urls.py` |
| `notifications/` | `notification-service/app/urls.py` |
| `api/gateway/home/`, `api/gateway/checkout/` | `api-gateway/api_gateway/urls.py` |

**Vị trí:** Toàn bộ file `*/urls.py` của từng service.

### 2.3 Model và field — ngôn ngữ nghiệp vụ trong dữ liệu

- **User/Customer/Staff/Manager:** `user-service/app/models.py` — `Customer`, `Staff`, `Manager`.
- **Product/Publisher/Category:** `product-service/app/models.py` — `Product` (với `product_type`), `Publisher`, `Category`.
- **Cart/CartItem:** `cart-service/app/models.py` — `Cart`, `CartItem`.
- **Order/OrderItem:** `order-service/app/models.py` — `Order`, `OrderItem`.
- **Review:** `review-service/app/models.py` — `Review`.
- **Payment:** `payment-service/app/models.py` — `Payment`.
- **Shipment:** `shipping-service/app/models.py` — `Shipment`.
- **Notification:** `notification-service/app/models.py` — `Notification` (loại `email`, `sms`, `system`).

**Trạng thái nghiệp vụ (status) dùng từ domain:**

- **Order** (`order-service/app/models.py`): `pending`, `confirmed`, `shipping`, `delivered`, `cancelled`.
- **Payment** (`payment-service/app/models.py`): `initiated`, `paid`, `failed`, `refunded`, `cancelled`.
- **Shipment** (`shipping-service/app/models.py`): `pending`, `picked`, `shipping`, `delivered`, `failed`, `cancelled`.

---

## 3. Bounded Context (Bối cảnh giới hạn)

### Kết luận: **Có** — mỗi microservice đóng vai trò một Bounded Context riêng biệt.

Trong DDD, Bounded Context định nghĩa ranh giới logic rõ ràng. Trong kiến trúc hệ thống của bạn, **mỗi service độc lập = một Bounded Context** sở hữu schema DB riêng và giao tiếp qua API hoặc Event.

| Bounded Context | Service (thư mục) | Cơ sở dữ liệu | Nội dung chính |
|-----------------|-------------------|---------------|----------------|
| **User/Identity** | `user-service/` | MySQL (`bookstore_user`) | Quản lý thông tin tài khoản Khách hàng, Nhân viên, Quản lý. |
| **Product** | `product-service/` | PostgreSQL (`bookstore_product`) | Quản lý catalogue sản phẩm đa dạng (sách, quần áo, đồ điện tử). |
| **Cart** | `cart-service/` | PostgreSQL (`bookstore_cart`) | Quản lý giỏ hàng của từng khách hàng. |
| **Order** | `order-service/` | PostgreSQL (`bookstore_order`) | Quản lý quy trình đặt hàng và vòng đời đơn hàng. |
| **Review** | `review-service/` | PostgreSQL (`bookstore_review`) | Quản lý đánh giá và bình luận sản phẩm. |
| **Payment** | `payment-service/` | PostgreSQL (`bookstore_payment`) | Quản lý giao dịch thanh toán đơn hàng. |
| **Shipping** | `shipping-service/` | PostgreSQL (`bookstore_shipping`) | Quản lý vận chuyển và theo dõi giao hàng. |
| **Catalogue (Read Model)** | `catalogue-service/` | PostgreSQL (`bookstore_catalogue`) | Tổng hợp sản phẩm và rating trung bình (Composition). |
| **Notification** | `notification-service/` | PostgreSQL (`bookstore_notification`) | Ghi nhật ký và gửi thông báo hệ thống/SMS/Email. |
| **AI Recommendation** | `ai-service/` | PostgreSQL (`bookstore_ai`) & Neo4j | Gợi ý sản phẩm thông minh và chatbot hỗ trợ khách hàng. |
| **API Gateway (BFF)** | `api-gateway/` | PostgreSQL (`bookstore_gateway`) | API gateway dạng BFF, xác thực và điều phối dữ liệu JSON. |
| **Frontend UI** | `frontend/` | PostgreSQL (`bookstore_frontend`) | Render giao diện HTML động cho khách hàng và admin. |

**Vị trí trong code:**
- **Cấu trúc thư mục:** Mỗi thư mục con `*-service/`, `frontend/`, `api-gateway/` tương ứng với một context.
- **Docker Compose:** File `docker-compose.yml` định nghĩa tách biệt các containers độc lập về network, volume và database.

---

## 4. Context Mapping (Bản đồ quan hệ giữa các Bounded Context)

### Kết luận: **Có** — mối quan hệ giữa các Bounded Context được phân chia rõ ràng thành giao tiếp đồng bộ (HTTP REST) và bất đồng bộ (Redis Pub/Sub).

### 4.1 Giao tiếp bất đồng bộ qua Redis Broker (Event-Driven)

Khi một sự kiện xảy ra ở một Context Upstream, nó phát đi event lên Redis. Các Context Downstream đăng ký lắng nghe (consume) sự kiện này để cập nhật trạng thái tương ứng mà không tạo coupling trực tiếp.

1. **User Context → Cart & Notification Contexts**:
   - Khi tạo Customer mới, `user-service` publishes event `customer_created`.
   - `cart-service` lắng nghe và tự động tạo giỏ hàng trống.
   - `notification-service` lắng nghe và tự động log thông báo chào mừng.
   - **Vị trí code:** `user-service/app/views.py` (class `CustomerListCreate`) gọi `publish_event('customer_created', ...)`. `cart-service/app/apps.py` đăng ký `handle_customer_created` cho handler.

2. **Order Context → Notification Context**:
   - Khi đơn hàng được tạo, `order-service` phát event `order_created`.
   - `notification-service` tạo thông báo xác nhận đơn hàng thành công.

3. **Payment Context → Order & Notification Contexts**:
   - Khi giao dịch thanh toán thay đổi (ví dụ: sang `paid`), `payment-service` phát event `payment_processed`.
   - `order-service` lắng nghe để tự động chuyển trạng thái đơn hàng sang `confirmed`.
   - `notification-service` tạo thông báo kết quả thanh toán.
   - **Vị trí code:** `payment-service/app/views.py` (class `PaymentStatusUpdate`) gọi `publish_event('payment_processed', ...)`. `order-service/app/event_handlers.py` lắng nghe và cập nhật đơn hàng.

4. **Shipping Context → Notification Context**:
   - Khi trạng thái vận chuyển cập nhật, `shipping-service` phát event `shipment_updated` để `notification-service` log thông tin.

### 4.2 Giao tiếp đồng bộ (HTTP REST API)

Được sử dụng cho các luồng dữ liệu thời gian thực (real-time read) hoặc điều phối đồng bộ (BFF API aggregation).

- **Catalogue Context → Product & Review Contexts**:
  `catalogue-service/app/views.py` thực hiện các cuộc gọi REST HTTP đồng bộ đến `product-service` (lấy danh sách sản phẩm) và `review-service` (lấy thống kê rating) để tổng hợp read model.
- **API Gateway (BFF) → Các Context**:
  `api-gateway/api_gateway/views.py` đóng vai trò là API Composer, thực hiện gọi đồng bộ đến các microservices nghiệp vụ để đóng gói dữ liệu JSON trả về cho Frontend UI.

### 4.3 Tóm tắt Context Mapping (trong code)

| Nguồn (caller) | Đích (callee) | Vị trí code / Kênh | Cơ chế giao tiếp |
|----------------|---------------|-------------------|------------------|
| user-service | cart-service | Redis: `customer_created` | Asynchronous Event (Pub/Sub) |
| user-service | notification-service | Redis: `customer_created` | Asynchronous Event (Pub/Sub) |
| order-service | notification-service | Redis: `order_created` | Asynchronous Event (Pub/Sub) |
| payment-service | order-service | Redis: `payment_processed` | Asynchronous Event (Pub/Sub) |
| payment-service | notification-service | Redis: `payment_processed` | Asynchronous Event (Pub/Sub) |
| shipping-service | notification-service | Redis: `shipment_updated` | Asynchronous Event (Pub/Sub) |
| catalogue-service | product-service | HTTP REST (`_get`) | Synchronous API Call |
| catalogue-service | review-service | HTTP REST (`_get`) | Synchronous API Call |
| frontend | api-gateway | HTTP REST | Synchronous UI Data Request |
| api-gateway | mọi backend | HTTP REST | Synchronous Orchestration (BFF) |

---

## 5. Aggregate (Tổng thể nhất quán)

### Kết luận: **Có** — cấu trúc dữ liệu trong các service được gom nhóm thành các Aggregate với một Aggregate Root chịu trách nhiệm bảo toàn tính hợp lệ của dữ liệu.

### 5.1 Order Aggregate (`order-service`)
- **Aggregate Root:** `Order`
- **Internal Entities:** `OrderItem` (xóa theo cơ chế cascade cùng với `Order`).
- **Vị trí code:** `order-service/app/models.py` (`OrderItem` tham chiếu đến `Order` qua `ForeignKey` với `on_delete=models.CASCADE`). Mọi thay đổi về đơn hàng phải đi qua thực thể root `Order`.

### 5.2 Cart Aggregate (`cart-service`)
- **Aggregate Root:** `Cart`
- **Internal Entities:** `CartItem`
- **Vị trí code:** `cart-service/app/models.py` (`CartItem` tham chiếu đến `Cart`).

### 5.3 Product Aggregate (`product-service`)
- **Aggregate Root:** `Product`
- **Internal Entities:** `Publisher`, `Category`
- **Vị trí code:** `product-service/app/models.py` (`Product` lưu trữ `attributes` dưới dạng JSONField linh hoạt cho các thuộc tính đặc thù và liên kết với `Publisher` qua `ForeignKey`).

### 5.4 Các Aggregate đơn (Single Entity)
Các context sau đây chứa các Aggregate chỉ gồm một entity duy nhất (chính nó là root):
- **Customer / Staff / Manager** (`user-service/app/models.py`)
- **Review** (`review-service/app/models.py`)
- **Payment** (`payment-service/app/models.py`)
- **Shipment** (`shipping-service/app/models.py`)
- **Notification** (`notification-service/app/models.py`)

---

## 6. Tổng kết

| Strategic DDD Concept | Có trong code? | Nơi thể hiện chính |
|-----------------------|----------------|--------------------|
| **Ubiquitous Language** | Có | Tên service, API paths (`urls.py`), tên models và fields (`models.py`), trạng thái nghiệp vụ. |
| **Bounded Context** | Có | Mỗi microservice = 1 context: cấu trúc thư mục `*-service/`, database độc lập và cấu hình `docker-compose.yml`. |
| **Context Mapping** | Có | Giao tiếp bất đồng bộ qua Redis Broker (`customer_created`, `payment_processed`, etc.) và đồng bộ qua REST HTTP. |
| **Aggregate** | Có | Cấu trúc root + internal entities như Order + OrderItem, Cart + CartItem, Product + Publisher. |
