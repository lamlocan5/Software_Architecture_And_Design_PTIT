# Báo cáo kỹ thuật hệ thống Bookstore Microservice

## 1. Giới thiệu

### 1.1 Mục tiêu hệ thống

Hệ thống Bookstore Microservice được xây dựng nhằm mô phỏng một cửa hàng sách trực tuyến với các chức năng chính:

- Quản lý sách và nhà xuất bản.
- Đăng ký khách hàng, quản lý giỏ hàng, đặt đơn hàng.
- Thanh toán, vận chuyển và theo dõi trạng thái đơn.
- Khách hàng đánh giá sách (review, rating).
- Phân vai **Admin / Manager / Staff / Customer** với giao diện quản trị riêng.
- Tích hợp **AI recommender** (dùng Gemini) để gợi ý sách cho người dùng.

Kiến trúc được thiết kế dạng **microservices** để:

- Tách biệt rõ các miền nghiệp vụ (books, orders, payments, shipments, reviews, catalogue, staff/manager, recommender).
- Dễ mở rộng, scale độc lập từng service.
- Thuận tiện cho việc học tập, demo kiến trúc microservice với Django + DRF + Docker.

### 1.2 Công nghệ sử dụng

- **Backend framework**: Django 5.x + Django REST Framework (DRF).
- **Cơ sở dữ liệu**: SQLite (mỗi service 1 file DB riêng trong volume `./data/...`).
- **API Gateway**: Một ứng dụng Django (`api-gateway`) cung cấp:
  - UI HTML (Bootstrap).
  - Auth đăng nhập (Django auth).
  - Orchestration gọi tới các backend services.
- **Containerization**: Docker + docker-compose.
- **AI Recommender**: Service riêng (`recommender-ai-service`) gọi **Gemini API** qua HTTP.

---

## 2. Kiến trúc tổng thể

### 2.1 Các service chính

Hệ thống gồm các service sau:

- `api-gateway`: cổng vào duy nhất từ browser, xử lý:
  - Đăng nhập / đăng ký.
  - Phân quyền (admin/manager/staff/customer).
  - Render UI cho tất cả use case.
  - Gọi các microservice backend bằng HTTP (REST).
- `book-service`: quản lý sách (`Book`) và nhà xuất bản (`Publisher`).
- `customer-service`: quản lý khách hàng business.
  - Khi tạo customer mới sẽ **tự động tạo giỏ hàng** bên `cart-service`.
- `cart-service`: quản lý giỏ hàng (`Cart`, `CartItem`).
- `order-service`: quản lý đơn hàng (`Order`, `OrderItem`) và trạng thái đơn.
- `review-service`: quản lý đánh giá sách (`Review`) và thống kê rating.
- `pay-service`: quản lý payment cho đơn hàng (`Payment`).
- `ship-service`: quản lý shipment/giao hàng (`Shipment`).
- `catalogue-service`: aggregation sách + rating để phục vụ trang catalogue.
- `staff-service`: hồ sơ nhân viên vận hành (staff).
- `manager-service`: hồ sơ quản lý (manager).
- `recommender-ai-service`: service AI gợi ý sách dùng Gemini.

### 2.2 Luồng tổng thể (tóm tắt)

Luồng tổng thể có thể hình dung như sau:

- Browser → `api-gateway` (đăng nhập, UI).
- Gateway theo chức năng sẽ gọi sang:
  - `customer-service` khi quản lý khách hàng.
  - `book-service` khi thêm/xem/sửa sách/nxb.
  - `cart-service` khi thao tác giỏ hàng.
  - `order-service` khi tạo / xem / cập nhật đơn.
  - `pay-service` và `ship-service` để xem/cập nhật payment/shipment.
  - `review-service` khi đọc và ghi đánh giá.
  - `catalogue-service` để lấy danh sách sách kèm rating.
  - `recommender-ai-service` để sinh danh sách gợi ý sách.

Chi tiết schema và sơ đồ từng service đã được trình bày trong `docs/architecture/architecture.md` (Mermaid) và các file PNG tương ứng.

---

## 3. Mô tả từng service

### 3.1 api-gateway

- Công nghệ: Django (UI, templates).
- Nhiệm vụ:
  - Xử lý auth người dùng (login, logout, register).
  - Phân vai:
    - **Admin**: toàn quyền, xem dashboard kiến trúc, quản lý staff/manager/customers/books/orders/payments/shipments.
    - **Manager / Staff**: dashboard vận hành, quản lý sách, khách hàng, đơn hàng.
    - **Customer**: dashboard cá nhân (giỏ hàng, đơn hàng của chính mình).
  - Orchestrator:
    - Ví dụ khi checkout:
      - Gọi `order-service` tạo đơn.
      - Gọi `pay-service` tạo payment theo **phương thức thanh toán** mà customer chọn.
      - Gọi `ship-service` tạo shipment với **địa chỉ / carrier / phone** mà customer nhập.
  - UI:
    - Trang home (`/`) – dashboard.
    - Trang quản lý sách, khách hàng, đơn hàng, reviews, payments, shipments, staff, manager.
    - Trang catalogue (`/catalogue/`).
    - Widget gợi ý AI (home + catalogue).

### 3.2 book-service

- Model chính:
  - `Publisher(name, address, mail)`.
  - `Book(title, author, price, stock, publisher)`.
- Cung cấp API cho:
  - `GET/POST /books/`
  - `GET/POST /publishers/`
  - `GET/PUT/DELETE /publishers/{id}/`
- Được gateway và catalogue-service sử dụng.

### 3.3 customer-service

- Model:
  - `Customer(name, email)`.
- API:
  - `GET /customers/`
  - `POST /customers/`
- Khi `POST /customers/` thành công:
  - Service chủ động gọi `cart-service` (`POST /carts/`) để tạo giỏ cho `customer_id` mới.

### 3.4 cart-service

- Model:
  - `Cart(customer_id)`
  - `CartItem(cart, book_id, quantity)`
- API:
  - `POST /carts/` – tạo giỏ.
  - `POST /carts/add-item/` – thêm sách vào giỏ.
  - `GET /carts/{customer_id}/` – xem items trong giỏ.
  - `GET /carts/customer/{customer_id}/` – lấy `cart_id` từ customer.
- Được gateway dùng trên:
  - Trang giỏ hàng (`/cart/{customer_id}/`).
  - Trang chi tiết sách khi khách bấm “Thêm vào giỏ”.

### 3.5 order-service

- Model:
  - `Order(customer_id, status, total_amount, created_at)`
  - `OrderItem(order, book_id, quantity, price_at_order)`
- API:
  - `GET /orders/` – danh sách tất cả đơn.
  - `POST /orders/create/` – tạo đơn từ giỏ.
  - `GET /orders/{id}/` – chi tiết đơn.
  - `PATCH /orders/{id}/status/` – cập nhật trạng thái.
  - `GET /orders/customer/{customer_id}/` – đơn theo khách.
- Trạng thái đơn:
  - `pending → confirmed → shipping → delivered` hoặc `cancelled`.

### 3.6 review-service

- Model:
  - `Review(book_id, customer_id, customer_name, book_title, rating, comment, created_at)`.
- API:
  - `GET/POST /reviews/`
  - `GET /reviews/book/{book_id}/`
  - `GET /reviews/stats/{book_id}/`
- Được sử dụng bởi:
  - Gateway để hiển thị danh sách review.
  - Catalogue-service để ghép rating vào danh sách sách.

### 3.7 pay-service

- Model:
  - `Payment(order_id, customer_id, amount, method, provider, transaction_id, status, created_at, updated_at)`.
- API:
  - `GET /payments/`
  - `POST /payments/create/`
  - `GET /payments/{id}/`
  - `PATCH /payments/{id}/status/`
  - `GET /payments/order/{order_id}/`
  - `GET /payments/customer/{customer_id}/`
- Trạng thái:
  - `initiated`, `paid`, `failed`, `refunded`, `cancelled`.

### 3.8 ship-service

- Model:
  - `Shipment(order_id, customer_id, receiver_name, phone, address, carrier, tracking_number, status, created_at, updated_at)`.
- API:
  - `GET /shipments/`
  - `POST /shipments/create/`
  - `GET /shipments/{id}/`
  - `PATCH /shipments/{id}/status/`
  - `GET /shipments/order/{order_id}/`
  - `GET /shipments/customer/{customer_id}/`
- Trạng thái:
  - `pending`, `picked`, `shipping`, `delivered`, `failed`, `cancelled`.

### 3.9 catalogue-service

- Không sở hữu dữ liệu riêng (Phase 1), chủ yếu gọi:
  - `book-service` (`GET /books/`)
  - `review-service` (`GET /reviews/stats/{book_id}/`)
- API:
  - `GET /catalog/books/`
  - `GET /catalog/books/{id}/`
- Trả về:
  - Thông tin sách gốc (book-service) + `avg_rating` và `total_reviews`.

### 3.10 staff-service & manager-service

- `staff-service`:
  - Model: `Staff(name, email, active, created_at)`.
  - API:
    - `GET/POST /staff/`
    - `PATCH/DELETE /staff/{id}/`

- `manager-service`:
  - Model: `Manager(name, email, active, created_at)`.
  - API:
    - `GET/POST /managers/`
    - `PATCH/DELETE /managers/{id}/`

Gateway mapping:

- Khi admin tạo staff/manager:
  - Tạo user đăng nhập trong Django auth (gán Group `staff` hoặc `manager`).
  - Gửi request tạo staff/manager bên service tương ứng.
- Cho phép:
  - Cập nhật name/email/password.
  - Bật/tắt active và xoá bản ghi staff/manager.

### 3.11 recommender-ai-service

- Không có model business phức tạp (chỉ SQLite tối thiểu cho log nếu cần).
- API:
  - `POST /recommendations/`
    - Input: danh sách sách (từ catalogue-service), `limit`, `context`.
    - Output: `recommended_ids` + `source` (`gemini` hoặc `fallback`).
- Bên trong:
  - Build prompt từ danh sách sách (giá, rating, review count, stock).
  - Gọi Gemini (Gemini 1.5 Flash) với `GEMINI_API_KEY`.
  - Parse danh sách ID trả về.
  - Nếu lỗi / quota / không parse được:
    - Fallback: sort theo `stock>0`, `avg_rating`, `total_reviews`.

---

## 4. Luồng nghiệp vụ chính

### 4.1 Đăng ký khách hàng → tạo cart

1. User (chưa đăng nhập) vào `/register/` trên gateway.
2. Gateway:
   - Tạo `User` trong Django auth.
   - Gửi `POST /customers/` tới `customer-service`:
     - Body: `{ "name": ..., "email": ... }`.
3. `customer-service`:
   - Lưu `Customer`.
   - Gọi `cart-service` `POST /carts/` với `customer_id` mới.
4. `UserProfile` trong gateway lưu `customer_id`.

### 4.2 Customer thêm sách vào giỏ, cập nhật giỏ

1. Customer đăng nhập → dashboard user.
2. Xem danh sách sách tại `/books/` hoặc `/catalogue/`.
3. Khi bấm “Thêm vào giỏ”:
   - Gateway gọi `GET /carts/customer/{customer_id}/` để lấy `cart_id`.
   - Sau đó `POST /carts/add-item/` với `{ cart, book_id, quantity }`.
4. Trang `/cart/{customer_id}/` hiển thị:
   - Items trong giỏ (`GET /carts/{customer_id}/`).
   - Tổng tiền.
   - Form thêm item.

### 4.3 Đặt đơn, chọn phương thức thanh toán và giao hàng

1. Trong `/cart/{customer_id}/`, khi có items:
   - UI hiển thị:
     - Dropdown **phương thức thanh toán** (`payment_method`: `cod`, `bank_transfer`, `card`…).
     - Form thông tin giao hàng: `shipment_carrier`, `shipment_address`, `shipment_phone`.
2. Khi bấm “Đặt hàng ngay”:
   - Gateway `POST /orders/checkout/{customer_id}/`:
     - Tính tổng từ items trong giỏ.
     - Gọi `order-service` `POST /orders/create/` để tạo đơn.
   - Nếu tạo đơn thành công:
     - Gọi `pay-service` `POST /payments/create/` với `method` đúng theo form.
     - Gọi `ship-service` `POST /shipments/create/` với thông tin:
       - `receiver_name` (từ `Customer`).
       - `address`, `phone`, `carrier` (từ form của user).
3. UI `order_detail` hiển thị:
   - Đơn hàng, items, customer.
   - Payment(s) và Shipment(s) liên quan.
   - Admin/Manager/Staff có thể cập nhật trạng thái đơn/payment/shipment.

### 4.4 Đánh giá sách

1. User vào `/reviews/` hoặc trang chi tiết sách.
2. Gửi `POST /reviews/` với:
   - `book_id`, `customer_id`, `customer_name`, `book_title`, `rating`, `comment`.
3. `review-service` lưu review.
4. Khi hiển thị danh sách sách:
   - `api-gateway` (trước đây) hoặc `catalogue-service` gọi `GET /reviews/stats/{book_id}/` để lấy:
     - `avg_rating`, `total_reviews`.

### 4.5 Gợi ý sách (Recommender AI)

1. Trên Home hoặc Catalogue:
   - Gateway gọi `catalogue-service` để lấy `books` đã kèm rating.
   - Gọi `POST /recommendations/` tới `recommender-ai-service` với:
     - `books` (subset, tối đa 50).
     - `context` (`home` hoặc `catalogue`).
     - `limit` (số sách cần gợi ý).
2. `recommender-ai-service`:
   - Nếu Gemini hoạt động:
     - Trả về `recommended_ids` do Gemini đề xuất.
   - Nếu lỗi:
     - Trả về danh sách theo thuật toán fallback (sorting).
3. Gateway map `recommended_ids` sang object sách và render widget “Gợi ý cho bạn”.

---

## 5. Triển khai Docker

### 5.1 docker-compose

- File: `docker-compose.yml`.
- Mỗi service có:
  - `build: ./<service>` – Dockerfile riêng.
  - `ports: "<host_port>:8000"` – map ra ngoài (chủ yếu để debug).
  - `volumes: ./data/<service>:/app/data` – SQLite DB volume.
- `api-gateway`:
  - Phụ thuộc (`depends_on`) tất cả service backend, bao gồm `recommender-ai-service`.
- `recommender-ai-service`:
  - Nhận env `GEMINI_API_KEY` (cần export từ môi trường shell trước khi chạy `docker compose up`).

### 5.2 Chạy hệ thống

```bash
cd bookstore-microservice
docker compose up --build
```

- Truy cập gateway: `http://localhost:8000`.
- Các service khác:
  - `book-service`: `http://localhost:8002`
  - `customer-service`: `http://localhost:8001`
  - `cart-service`: `http://localhost:8003`
  - `order-service`: `http://localhost:8004`
  - `review-service`: `http://localhost:8005`
  - `ship-service`: `http://localhost:8006`
  - `pay-service`: `http://localhost:8007`
  - `catalogue-service`: `http://localhost:8008`
  - `staff-service`: `http://localhost:8009`
  - `manager-service`: `http://localhost:8010`
  - `recommender-ai-service`: `http://localhost:8011`

---

## 6. Bảo mật và phân quyền

### 6.1 Auth và role

- Auth:
  - Được xử lý hoàn toàn ở `api-gateway` (Django auth).
- Role:
  - `is_superuser`: Admin.
  - Group `manager`: Manager.
  - Group `staff`: Staff.
- Phân quyền:
  - Admin:
    - Toàn quyền vào mọi màn hình và hành động.
    - Quản lý staff/manager accounts.
  - Manager/Staff:
    - Dashboard vận hành (không xem sơ đồ kiến trúc).
    - Quản lý sách, khách hàng, đơn hàng.
  - Customer:
    - Dashboard cá nhân.
    - Chỉ xem giỏ hàng, đơn, payment, shipment của chính mình.

### 6.2 Gemini API

- Key đặt trong biến môi trường `GEMINI_API_KEY`.
- Không commit key vào repo.
- Recommender chỉ gửi **dữ liệu sách công khai** (title, author, giá, rating, reviews); **không gửi dữ liệu cá nhân** của user.

---

## 7. Hạn chế & hướng phát triển

### 7.1 Hạn chế

- Sử dụng SQLite cho tất cả service:
  - Đủ cho demo, nhưng không phù hợp cho load lớn / HA.
- Chưa có:
  - Pagination chuẩn (limit/offset) cho list endpoints.
  - Logging, metrics, tracing (observability).
  - Cơ chế retry/bulkhead/circuit breaker giữa các service.
- Recommender AI:
  - Mới chỉ dùng thông tin sách cơ bản + rating.
  - Chưa cá nhân hoá theo lịch sử từng customer (purchase history, clicks, v.v.).

### 7.2 Hướng phát triển

- Thay SQLite bằng PostgreSQL hoặc MySQL; tách DB riêng cho mỗi service.
- Thêm:
  - Pagination, filtering, sorting server-side.
  - Logging chuẩn (structed logs) và metrics (Prometheus + Grafana).
  - API Gateway “thật” (Kong, Traefik, v.v.) nếu cần.
- Recommender:
  - Mở rộng input với lịch sử cart/order/review của từng customer (nếu muốn cá nhân hoá).
  - Thử các mô hình hoặc API khác.
  - Thêm caching (VD: cache kết quả recommendations cho 1 khoảng thời gian).

---

## 8. Kết luận

Hệ thống Bookstore Microservice hiện tại đáp ứng khá đầy đủ các yêu cầu:

- Quản lý sách, khách hàng, giỏ hàng, đơn hàng, thanh toán, giao hàng, đánh giá.
- Phân rã thành nhiều microservice độc lập, được điều phối bởi `api-gateway`.
- Có phân quyền rõ giữa **Admin / Manager / Staff / Customer**.
- Bổ sung `catalogue-service` để tối ưu việc duyệt sách + rating.
- Tích hợp `recommender-ai-service` sử dụng Gemini để gợi ý sách, kèm fallback khi AI lỗi.

Bộ tài liệu đi kèm (architecture diagrams, OpenAPI, API reference, báo cáo kỹ thuật) giúp:

- Dễ hiểu luồng nghiệp vụ.
- Dễ mở rộng / bảo trì.
- Thuận tiện cho việc học tập, demo kiến trúc microservice và tích hợp AI trong bối cảnh e-commerce nhỏ gọn.

