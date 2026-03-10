## Tổng quan API các microservice

Tài liệu này tóm tắt nhanh các endpoint chính (REST) của từng service. Chi tiết schema tham khảo trong các file OpenAPI tại `docs/api/openapi/*.yaml`.

---

## Book Service (`book-service:8000`)

- `GET /books/`  
  - Mô tả: Lấy danh sách tất cả sách.  
  - Response: `200 OK` – mảng `Book`.

- `POST /books/`  
  - Mô tả: Tạo sách mới.  
  - Body (JSON, ví dụ):
    ```json
    {
      "title": "Python Cơ Bản",
      "author": "Nguyễn Văn A",
      "price": 149000,
      "stock": 10,
      "publisher": 2
    }
    ```

- `GET /publishers/` – danh sách NXB.  
- `POST /publishers/` – tạo NXB.  
- `GET /publishers/{id}/` – chi tiết NXB.  
- `PUT /publishers/{id}/` – cập nhật.  
- `DELETE /publishers/{id}/` – xoá.

---

## Customer Service (`customer-service:8000`)

- `GET /customers/`  
  - Lấy danh sách khách hàng.

- `POST /customers/`  
  - Tạo khách hàng mới **và tự động tạo giỏ hàng** bên `cart-service`.
  - Body ví dụ:
    ```json
    { "name": "Nguyễn Văn B", "email": "user@example.com" }
    ```

---

## Cart Service (`cart-service:8000`)

- `POST /carts/`  
  - Tạo giỏ hàng cho `customer_id`.
  - Body: `{ "customer_id": 1 }`.

- `POST /carts/add-item/`  
  - Thêm sách vào giỏ.
  - Body:
    ```json
    { "cart": 1, "book_id": 5, "quantity": 2 }
    ```

- `GET /carts/{customer_id}/`  
  - Xem chi tiết items trong giỏ của `customer_id`.

- `GET /carts/customer/{customer_id}/`  
  - Lấy thông tin giỏ (bao gồm `id`) từ customer.

---

## Order Service (`order-service:8000`)

- `GET /orders/`  
  - Lấy danh sách tất cả đơn hàng.

- `POST /orders/create/`  
  - Tạo đơn hàng mới từ giỏ.
  - Body ví dụ:
    ```json
    {
      "customer_id": 1,
      "total_amount": 500000,
      "items": [
        { "book_id": 5, "quantity": 2, "price_at_order": 150000 },
        { "book_id": 7, "quantity": 1, "price_at_order": 200000 }
      ]
    }
    ```

- `GET /orders/{order_id}/` – chi tiết đơn.  
- `PATCH /orders/{order_id}/status/` – cập nhật trạng thái đơn (pending/confirmed/shipping/delivered/cancelled).  
- `GET /orders/customer/{customer_id}/` – danh sách đơn của 1 khách.

---

## Review Service (`review-service:8000`)

- `GET /reviews/` – danh sách đánh giá.  
- `POST /reviews/` – tạo đánh giá mới:
  ```json
  {
    "book_id": 5,
    "customer_id": 1,
    "customer_name": "Nguyễn Văn B",
    "book_title": "Python Cơ Bản",
    "rating": 5,
    "comment": "Rất hay!"
  }
  ```

- `GET /reviews/book/{book_id}/` – tất cả review cho 1 sách.  
- `GET /reviews/stats/{book_id}/` – thống kê `avg_rating`, `total_reviews` cho sách.

---

## Pay Service (`pay-service:8000`)

- `GET /payments/` – danh sách payment.  
- `POST /payments/create/` – tạo payment:
  ```json
  {
    "order_id": 10,
    "customer_id": 1,
    "amount": 500000,
    "method": "cod"
  }
  ```

- `GET /payments/{payment_id}/` – chi tiết payment.  
- `PATCH /payments/{payment_id}/status/` – cập nhật trạng thái (initiated/paid/failed/refunded/cancelled).  
- `GET /payments/order/{order_id}/` – payments theo đơn.  
- `GET /payments/customer/{customer_id}/` – payments theo khách.

---

## Ship Service (`ship-service:8000`)

- `GET /shipments/` – danh sách shipment.  
- `POST /shipments/create/` – tạo shipment:
  ```json
  {
    "order_id": 10,
    "customer_id": 1,
    "receiver_name": "Nguyễn Văn B",
    "phone": "0901234567",
    "address": "Số 1, Q.1, TP.HCM",
    "carrier": "ghn"
  }
  ```

- `GET /shipments/{shipment_id}/` – chi tiết shipment.  
- `PATCH /shipments/{shipment_id}/status/` – cập nhật trạng thái (pending/picked/shipping/delivered/failed/cancelled).  
- `GET /shipments/order/{order_id}/` – shipment theo order.  
- `GET /shipments/customer/{customer_id}/` – shipment theo customer.

---

## Catalogue Service (`catalogue-service:8000`)

- `GET /catalog/books/`  
  - Lấy danh sách sách đã ghép `avg_rating` và `total_reviews`.

- `GET /catalog/books/{id}/`  
  - Chi tiết 1 sách (có cả rating).

---

## Staff Service (`staff-service:8000`)

- `GET /staff/` – danh sách staff.  
- `POST /staff/` – tạo staff mới:
  ```json
  { "name": "Nguyễn Văn Staff", "email": "staff@example.com" }
  ```

- `PATCH /staff/{id}/` – cập nhật một phần (name, email, active).  
- `DELETE /staff/{id}/` – xoá staff.

---

## Manager Service (`manager-service:8000`)

- `GET /managers/` – danh sách manager.  
- `POST /managers/` – tạo manager mới:
  ```json
  { "name": "Nguyễn Văn Manager", "email": "manager@example.com" }
  ```

- `PATCH /managers/{id}/` – cập nhật name/email/active.  
- `DELETE /managers/{id}/` – xoá manager.

---

## Recommender-AI Service (`recommender-ai-service:8000`)

- `POST /recommendations/`  
  - Mô tả: Dựa trên danh sách sách (từ `catalogue-service`), chọn ra một số ID sách gợi ý.  
  - Body ví dụ:
    ```json
    {
      "context": "home",
      "limit": 6,
      "books": [
        {
          "id": 5,
          "title": "Python Cơ Bản",
          "author": "Nguyễn Văn A",
          "price": 149000,
          "stock": 10,
          "publisher": "NXB Trẻ",
          "avg_rating": 4.5,
          "total_reviews": 12
        }
      ]
    }
    ```
  - Response:
    ```json
    {
      "recommended_ids": [5, 7, 3],
      "source": "gemini"
    }
    ```

