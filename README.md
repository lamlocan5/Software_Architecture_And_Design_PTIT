# 🏛️ Software Architecture and Design — Project Collection
> **Học viện Công nghệ Bưu chính Viễn thông (PTIT)**  
> **Môn học:** Kiến trúc và Thiết kế Phần mềm (Software Architecture & Design)  
> **Sinh viên thực hiện:** Đặng Ngọc Lâm (Mã nhóm/Lớp: `04.03`, Tên tài khoản: `lamdn`)

---

## 🌟 Tổng quan thư mục dự án
Repository này chứa toàn bộ các bài tập thường kỳ, bài kiểm tra tiến trình, và các đồ án/tiểu luận môn học liên quan đến **Kiến trúc và Thiết kế Phần mềm (Software Architecture & Design)**. Nội dung bao gồm việc minh họa từ mô hình nguyên khối (**Monolithic**), kiến trúc đa lớp (**Clean Architecture**), đến các hệ thống hướng dịch vụ lớn (**Microservices**) tích hợp trí tuệ nhân tạo (**AI Service**), cùng các tài liệu phân tích hệ thống chi tiết.

---

## 🗂️ Sơ đồ cấu trúc Workspace

Dưới đây là sơ đồ tóm tắt các thư mục và thành phần chính trong repo:

| Thư mục / Thành phần | Kiến trúc / Loại | Công nghệ chính | Mô tả / Chức năng chính |
| :--- | :--- | :--- | :--- |
| 📚 [bookstore-microservice](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice) | **Microservices (Event-Driven)** | Django, Docker, Redis, Neo4j, Gemini AI, Prometheus, Grafana | Hệ thống nhà sách trực tuyến quy mô lớn với 11+ services, giao tiếp qua Redis Pub/Sub, cơ sở dữ liệu Graph Neo4j và chatbot AI. |
| 🏥 [healthcare](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/healthcare) | **Microservices (Domain-Driven Design)** | Django REST Framework, Nginx API Gateway, PostgreSQL, Redis | Hệ thống quản lý bệnh viện phân tán, tự động trừ kho thuốc & tạo hóa đơn qua REST API. |
| 🚀 [TieuLuan_ver2/aiecom2](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2) | **Microservices & AI Integration** | Django, MySQL, Neo4j, SimpleRNN, Gemini RAG | Dự án Tiểu luận học phần phiên bản 2: Hệ thống E-commerce đề xuất sản phẩm dựa trên mô hình RNN và Chatbot RAG. |
| 📝 [kiemtra01_04.03_lamdn](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/kiemtra01_04.03_lamdn) | **Microservices (Progress Test)** | Django, Nginx Gateway, MySQL | Bài kiểm tra số 1: Quản lý thiết bị công nghệ (Laptop, Mobile), khách hàng và nhân viên hỗ trợ. |
| 📉 [dudoan_diemthi](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/dudoan_diemthi) | **Machine Learning & Web App** | Python, Flask, Jupyter Notebook, Scikit-learn | Dự đoán điểm số sinh viên dựa trên tập dữ liệu học tập, đi kèm giao diện web tương tác trực quan. |
| 📂 [assign01](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/assign01) | **Comparison (Monolith vs. Clean vs. Microservices)** | Django, Python | Bài tập 1: Hiện thực hóa hệ thống Book Store qua 3 mô hình kiến trúc khác nhau để so sánh ưu nhược điểm. |
| 📂 [assign02](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/assign02) | **Analysis & Design Project** | Django | Bài tập 2: Dự án Bookstore phân tích chi tiết quy trình từ bản vẽ thiết kế đến mã nguồn thực nghiệm. |
| 📂 [assign03](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/assign03) | **UML Modeling & Mockups** | Visual Paradigm, UML Diagrams | Bài tập 3: Bản vẽ thiết kế kiến trúc hệ thống Bookstore (`SAD.vpp`) cùng các ảnh chụp luồng UI mockups. |
| 🎓 [TieuLuan_final](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_final) | **Final Report & Thesis Docs** | MS Word, PDF, Visual Paradigm | Báo cáo tiểu luận kết thúc môn học chính thức (`healthcare.vpp` và file thuyết minh chi tiết). |
| 📁 [btapTrenLop](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/btapTrenLop) | **In-class Exercises** | Python | Tổng hợp các bài tập nhỏ, thực hành nhanh trên lớp theo từng tuần học. |

---

## 🛠️ Chi tiết các Dự án Tiêu biểu

### 1. 📚 Bookstore Microservices System
Hệ thống Nhà sách trực tuyến hoàn chỉnh được triển khai với tính chịu lỗi cao (**Resilience**) và theo dõi hiệu năng hệ thống (**Observability**).

- **Kiến trúc dữ liệu:** *Database-per-Service*. Mỗi dịch vụ có database riêng (MySQL cho `user-service`, PostgreSQL cho các service nghiệp vụ khác).
- **Cơ chế giao tiếp:** Kết hợp đồng bộ (HTTP REST qua API Gateway) và bất đồng bộ (Redis Pub/Sub Broker cho các luồng xử lý sau mua hàng như gửi Notification, cập nhật Catalogue).
- **Giám sát & Quản lý Log tập trung:** Sử dụng bộ công cụ **Prometheus** (thu thập metrics), **Grafana** (trực quan hóa chỉ số), **Loki & Promtail** (thu thập log tập trung).
- **Dịch vụ AI:** [ai-service](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice/ai-service) kết nối database đồ thị **Neo4j** biểu diễn mối quan hệ giữa các thực thể và tích hợp **Gemini AI API** làm chatbot tư vấn sản phẩm.
- **Khởi chạy nhanh (Quick Start):**
  1. Mở file [bookstore-microservice/.env](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice/.env) để cấu hình `GEMINI_API_KEY` và mật khẩu Database.
  2. Click đúp chuột vào file [bookstore-microservice/run.bat](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice/run.bat) để tự động khởi tạo database, dựng Docker container, migrate dữ liệu và nạp Mock Data mẫu.
  3. Truy cập dashboard chính tại: **`http://localhost:8000`**

---

### 2. 🏥 Healthcare Management Microservices
Hệ thống quản lý bệnh viện phân tán được thiết kế theo phương pháp **Domain-Driven Design (DDD)**.

- **Các service nghiệp vụ chính:**
  - `patient-service`: Quản lý thông tin bệnh nhân.
  - `doctor-service`: Quản lý chuyên khoa và thông tin bác sĩ.
  - `clinical-service`: Thực hiện các giao dịch khám bệnh, hẹn lịch và kê đơn.
  - `inventory-service`: Quản lý danh mục dược phẩm và xuất/nhập kho.
  - `billing-service`: Tạo hóa đơn và thực hiện các giao dịch thanh toán.
- **Luồng tích hợp:** Khi bác sĩ thực hiện kê đơn thuốc tại `clinical-service`, hệ thống sẽ tự động gọi REST API nội bộ tới `inventory-service` để giảm số lượng tồn kho của loại thuốc đó, đồng thời kích hoạt `billing-service` để tự động lập hóa đơn tương ứng cho bệnh nhân.
- **Khởi chạy nhanh (Quick Start):**
  1. Đảm bảo PostgreSQL chạy trên máy host cổng `5432`.
  2. Click đúp chuột vào file [healthcare/run.bat](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/healthcare/run.bat) (trên Windows) hoặc chạy `./run.sh` trên Linux/macOS.
  3. Giao diện quản lý hiển thị tại: **`http://localhost:8080`**

---

### 3. 🚀 AI E-Commerce Microservices (`aiecom2`)
Nằm trong thư mục [TieuLuan_ver2/aiecom2/ecom](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2/ecom), đây là hệ thống mua sắm tích hợp AI Recommender.

- **Thành phần công nghệ:** Django + MySQL + Neo4j + SimpleRNN + Gemini RAG.
- **Cách thức hoạt động của AI Recommender:**
  1. Khi khách hàng thao tác xem/mua sản phẩm, lịch sử được lưu trữ tại `behavior-service`.
  2. `recommend-service` sử dụng mô hình học sâu **SimpleRNN** (được huấn luyện trong file Jupyter notebook [code train.ipynb](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2/code train.ipynb)) để dự đoán các sản phẩm tiếp theo người dùng có khả năng click nhiều nhất.
  3. Chatbot AI tại `chat-service` truy vấn dữ liệu đồ thị Neo4j kết hợp Gemini API để tư vấn sản phẩm thông minh theo ngữ cảnh RAG.
- **Cách chạy hệ thống:**
  1. Bật MySQL và Neo4j qua Docker compose: `docker compose up -d` tại thư mục `ecom/`.
  2. Migrate dữ liệu và chạy scripts trong thư mục [seeds/](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2/ecom/seeds) để nạp dữ liệu sản phẩm, hành vi người dùng vào MySQL và Neo4j.
  3. Khởi động các microservices bằng cách chạy file [start_all.bat](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2/start_all.bat).
  4. Mở file [frontend/index.html](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/TieuLuan_ver2/aiecom2/ecom/frontend/index.html) để bắt đầu trải nghiệm.

---

### 4. 📝 Bài Kiểm tra Số 1 (`kiemtra01_04.03_lamdn`)
Bài kiểm tra thực hành xây dựng hệ thống quản lý thiết bị công nghệ bao gồm:
- **Dịch vụ nghiệp vụ:** `laptop_service`, `moblie_service`, `customer_service`, `staff_service`, `advisor_service` (dịch vụ tư vấn khách hàng).
- Toàn bộ các yêu cầu được định tuyến qua `gateway_service` bảo mật và được cấu hình khởi chạy dễ dàng qua `docker-compose.yml`.

---

### 5. 📉 Dự đoán Điểm thi (`dudoan_diemthi`)
Dự án phân tích dữ liệu học tập và dự báo kết quả của sinh viên:
- **Phần phân tích:** File Jupyter notebook [student_score_prediction.ipynb](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/dudoan_diemthi/student_score_prediction.ipynb) thực hiện tiền xử lý dữ liệu từ file [student_scores_dataset.csv](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/dudoan_diemthi/student_scores_dataset.csv), huấn luyện mô hình dự đoán.
- **Phần Web App:** Ứng dụng Flask [app.py](file:///C:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/dudoan_diemthi/app.py) cung cấp giao diện nhập các chỉ số học tập để đưa ra dự đoán điểm thi trực quan kèm biểu đồ phân tích.

---

## 🔒 Ghi chú Bảo mật & Quản lý Credentials
- Khi làm việc với các dịch vụ AI (như Gemini), hãy đảm bảo **không commit trực tiếp** mã khóa API (`GEMINI_API_KEY`) lên hệ thống quản lý phiên bản Git.
- Sử dụng file cấu hình môi trường `.env` và thêm nó vào `.gitignore` để tránh rò rỉ thông tin cá nhân.

---
*Tài liệu này được biên soạn nhằm hướng dẫn nhanh cấu trúc toàn bộ kho lưu trữ phục vụ cho quá trình đánh giá và thực hành môn học.*
