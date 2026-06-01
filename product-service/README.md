# Microservices E-Commerce Project

Dự án này là hệ thống thương mại điện tử đơn giản được xây dựng theo kiến trúc **Microservices** dùng Python/Django REST Framework, giao tiếp qua API Gateway để phục vụ UI.

## 🏗 Kiến trúc Hệ Thống

Dự án bao gồm 4 services chính độc lập và 1 cổng trung tâm (API Gateway), chạy trên Docker với các cơ sở dữ liệu riêng:

| Component | Port | Database | Nhiệm vụ chính |
| :--- | :--- | :--- | :--- |
| **API Gateway** | `8000` | SQLite (Internal) | Nhận requests, serve HTML Web UI, điều hướng API xuống các nhánh dưới |
| **Staff Service** | `8002` | MySQL | Đảm nhận chức năng cho Admin/Nhân viên, phân quyền đơn giản, nhập kho |
| **Customer Service** | `8001` | MySQL | Đăng ký & Đăng nhập cho khách, quản lý túi đồ (Giỏ hàng/Cart) |
| **Laptop Service** | `8003` | PostgreSQL | Chứa dữ liệu logic, model của thiết bị Laptop (CRUD, tồn kho, search) |
| **Mobile Service** | `8004` | PostgreSQL | Chứa dữ liệu logic, model của Điện thoại Mobile (CRUD, tồn kho, search) |

---

## 🚀 Hướng Dẫn Vận Hành Hệ Thống

Dự án đã được cấu hình tất cả qua **Docker**.
Chỉ cần bạn có `Docker Desktop` chạy trên máy, mọi cài đặt sẽ diễn ra tự động.

### 1. Build và Chạy Background
Mở Terminal / Command Prompt trong thư mục của dự án (`product-service`) và chạy:
```bash
docker-compose --env-file .env up --build
```
*Lưu ý: Quá trình pull images (MySQL, Postgres, Python) ban đầu có thể mất một lúc.*

### 2. Truy cập Giao Diện Người Dùng (UI)
Bạn có thể thao tác hoàn toàn qua Web thay vì dùng Postman:
* **Trang chủ:** [http://localhost:8000/](http://localhost:8000/) - Tại đây có 2 Options giao diện
  * **[Staff UI]** - Phía dành cho quản lý nhập sản phẩm mới và tồn kho.
  * **[Customer UI]** - Phía bán hàng, tìm kiếm và tạo giỏ hàng.

### 3. Cách Sử Dụng Lần Đầu

#### A. Khách Hàng (Customer UI)
1. Mở Customer UI từ Trang Chủ.
2. Form Đăng nhập & Đăng ký sẽ hiện. **Hãy tạo một user ở form "Register"** bên phải.
3. Sau khi tạo, hãy dùng nó để **Login**.
4. Lúc này bạn có thể gõ "macbook" hay thẻ CPU nào đó vào ô **Search**, xem danh sách, và ấn **Add to Cart**.
5. Chọn tab **Cart** ở Menu để xem chi phí tính toán.

#### B. Nhân viên Quản lý (Staff UI)
Việc tạo Staff Manager chưa có form đăng ký ở giao diện vì tính bảo mật. Bạn cần tạo SuperUser hoặc lưu ý dùng api gọi `register` thủ công. Tuy nhiên, dễ nhất là đăng nhập vào container:
```bash
# Vào container Django staff:
docker exec -it product-service-staff-service-1 bash

# Sau đó gõ lệnh tạo 1 admin user:
python manage.py createsuperuser
# Điền Username, Email, Password tùy ý.
# Thoát container: exit
```
1. Giờ hãy vào **Staff UI** và Login bằng user vừa tạo.
2. Trên Menu, đổi phân loại "Laptop" hoặc "Mobile Phone", điền tên, CPU, RAM... và bấm **Add Product**.
3. Bên dưới bảng Inventory, nhấn chữ **Refresh** cạnh tên sản phẩm để thấy được sản phẩm cập nhật từ Postgres.

---

## 🛠 Commands Tiện Ích khác (Dành cho Dev)

**Theo dõi logs:** (biết Service có bị lỗi Error 500 hay gánh DB không)
```bash
docker-compose logs -f
# hoặc cụ thể cho 1 service
docker-compose logs -f api-gateway
```

**Khởi động lại / Dập Container đi:**
```bash
docker-compose restart
docker-compose down
```

**Dập và xoá hết DB sạch sẽ (Reset Volume data):**
```bash
docker-compose down -v
```
