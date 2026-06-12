## Tổng quan API các microservices

Tài liệu này tóm tắt danh sách các endpoint chính (REST) của từng service phục vụ trong hệ thống Bookstore Microservices.

---

## 🚪 API Entrypoints (Qua Nginx Gateway — Host Port `8000`)

Mọi yêu cầu từ ngoài hệ thống cần được gửi qua Nginx Gateway trên cổng `8000`.

- **`/`**: Chuyển tiếp tới giao diện HTML (`frontend`).
- **`/api/gateway/`**: Chuyển tiếp tới BFF API gateway (`api-gateway`).
  - `/api/gateway/home/` - Lấy thông tin trang chủ/dashboard tổng hợp.
  - `/api/gateway/catalogue/` - Lấy danh mục sản phẩm tổng hợp.
  - `/api/gateway/cart/<customer_id>/` - Xem giỏ hàng.
  - `/api/gateway/checkout/<customer_id>/` - Đặt hàng từ giỏ.
  - `/api/gateway/orders/<order_id>/` - Xem chi tiết đơn hàng.
  - `/api/gateway/notifications/` - Nhật ký thông báo của admin.
  - `/api/gateway/notifications/<customer_id>/` - Nhật ký thông báo của khách hàng.
- **`/api/notifications/`**: Chuyển tiếp tới `notification-service`.

---

## 👤 User Service (`user-service:8001`)

Quản lý thông tin tài khoản Khách hàng (Customer), Nhân viên (Staff), Quản lý (Manager).

### Customers
- `GET /customers/` — Lấy danh sách khách hàng.
- `POST /customers/` — Đăng ký khách hàng mới (phát event `customer_created`).
  - Body: `{"name": "Nguyễn Văn A", "email": "nguyenvana@email.com", "password": "customer123"}`
- `GET /customers/{id}/` — Chi tiết khách hàng.

### Staff
- `GET /staff/` — Danh sách nhân viên.
- `POST /staff/` — Tạo nhân viên mới.
- `PATCH /staff/{id}/` — Cập nhật nhân viên.
- `DELETE /staff/{id}/` — Xóa nhân viên.

### Managers
- `GET /managers/` — Danh sách quản lý.
- `POST /managers/` — Tạo quản lý mới.
- `PATCH /managers/{id}/` — Cập nhật quản lý.
- `DELETE /managers/{id}/` — Xóa quản lý.

---

## 📦 Product Service (`product-service:8002`)

Quản lý sản phẩm thuộc các dòng khác nhau (Sách, Quần áo, Đồ điện tử).

### Products
- `GET /products/` — Lấy toàn bộ danh sách sản phẩm.
- `POST /products/` — Thêm sản phẩm mới.
  - Body: `{"name": "Áo khoác gió", "product_type": "clothing", "price": 450000, "stock": 20, "attributes": {"size": "XL", "color": "Đen"}}`
- `GET /products/{id}/` — Chi tiết sản phẩm.

### Publishers
- `GET /publishers/` — Danh sách NXB.
- `POST /publishers/` — Tạo NXB.
- `GET /publishers/{id}/` — Chi tiết NXB.
- `PUT /publishers/{id}/` — Cập nhật NXB.
- `DELETE /publishers/{id}/` — Xóa NXB.

### Categories
- `GET /categories/` — Danh sách các danh mục.

---

## 🛒 Cart Service (`cart-service:8003`)

Quản lý giỏ hàng của khách hàng.

- `POST /carts/` — Khởi tạo giỏ hàng cho `customer_id`.
  - Body: `{"customer_id": 1}`
- `GET /carts/{customer_id}/` — Xem chi tiết items trong giỏ hàng.
- `GET /carts/customer/{customer_id}/` — Lấy thông tin giỏ hàng tổng thể.
- `POST /carts/add-item/` — Thêm sản phẩm vào giỏ hàng.
  - Body: `{"cart": 1, "book_id": 2, "quantity": 1}`

---

## 📋 Order Service (`order-service:8004`)

Quản lý đơn hàng và dòng đơn hàng.

- `GET /orders/` — Danh sách đơn hàng toàn hệ thống.
- `POST /orders/create/` — Tạo đơn hàng mới từ giỏ hàng (phát event `order_created`).
  - Body:
    ```json
    {
      "customer_id": 6,
      "total_amount": 86000,
      "items": [{"book_id": 1, "quantity": 1, "price_at_order": 86000}]
    }
    ```
- `GET /orders/{order_id}/` — Chi tiết đơn hàng.
- `PATCH /orders/{order_id}/status/` — Cập nhật trạng thái đơn hàng (`pending`, `confirmed`, `shipping`, `delivered`, `cancelled`).
- `GET /orders/customer/{customer_id}/` — Đơn hàng theo khách hàng.

---

## ⭐ Review Service (`review-service:8005`)

Quản lý đánh giá sản phẩm.

- `GET /reviews/` — Danh sách đánh giá.
- `POST /reviews/` — Tạo đánh giá mới.
- `GET /reviews/book/{book_id}/` — Đánh giá theo sản phẩm.
- `GET /reviews/stats/{book_id}/` — Thống kê rating trung bình và tổng số đánh giá.

---

## 🚚 Shipping Service (`shipping-service:8006`)

Quản lý quá trình giao vận đơn hàng.

- `GET /shipments/` — Danh sách vận đơn.
- `POST /shipments/` — Tạo vận đơn mới.
- `GET /shipments/{id}/` — Chi tiết vận đơn.
- `PATCH /shipments/{id}/status/` — Cập nhật trạng thái vận chuyển (phát event `shipment_updated`).
  - Trạng thái: `pending`, `picked`, `shipping`, `delivered`, `failed`, `cancelled`

---

## 💳 Payment Service (`payment-service:8007`)

Quản lý các giao dịch thanh toán hóa đơn.

- `GET /payments/` — Danh sách giao dịch.
- `POST /payments/` — Khởi tạo thanh toán mới.
- `GET /payments/{id}/` — Chi tiết giao dịch thanh toán.
- `PATCH /payments/{payment_id}/status/` — Cập nhật trạng thái thanh toán (phát event `payment_processed`).
  - Body: `{"status": "paid"}`

---

## 🗂️ Catalogue Service (`catalogue-service:8008`)

Service tổng hợp dữ liệu sản phẩm cùng với điểm đánh giá rating tương ứng.

- `GET /catalog/books/` — Danh sách sách có kèm thống kê đánh giá.
- `GET /catalog/books/{id}/` — Chi tiết một sách có kèm thống kê đánh giá.

---

## 🔔 Notification Service (`notification-service:8009`)

Ghi nhật ký thông báo tự động cho khách hàng.

- `GET /notifications/` — Danh sách toàn bộ thông báo hệ thống (Dành cho Admin).
- `GET /notifications/customer/{customer_id}/` — Danh sách thông báo theo khách hàng.
- `POST /notifications/` — Tạo thông báo thủ công.

---

## 🤖 AI Service (`ai-service:8011`)

Gợi ý sản phẩm thông minh và chatbot tư vấn bán hàng.

- `GET /recommend/` — Gợi ý sản phẩm Hybrid (PyTorch LSTM + Neo4j Graph Path + FAISS Similarity).
- `POST /behavior/` — Ghi nhận hành vi người dùng (view, cart, buy) theo thời gian thực để đồng bộ vào PostgreSQL và Neo4j.
- `POST /chatbot/` — Chatbot RAG hỗ trợ tư vấn sản phẩm thông minh (Sách, Quần áo, Điện tử) sử dụng FAISS + Gemini 3.5 Flash.
- `POST /recommendations/` — Gợi ý sản phẩm thông minh legacy qua Gemini API hoặc thuật toán fallback.
