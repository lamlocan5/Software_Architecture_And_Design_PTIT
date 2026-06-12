# Báo cáo kỹ thuật hệ thống Bookstore Microservices

## 1. Giới thiệu

### 1.1 Mục tiêu hệ thống

Hệ thống Bookstore Microservices được xây dựng nhằm mô phỏng một cửa hàng sách trực tuyến phân tán với các miền nghiệp vụ được cô lập rõ ràng:

- Quản lý catalogue sản phẩm đa dạng (Sách, Quần áo, Thiết bị điện tử).
- Đăng ký tài khoản khách hàng, quản lý giỏ hàng, đặt hàng và quản lý vòng đời đơn hàng.
- Xử lý giao dịch thanh toán và giao vận đơn hàng.
- Đánh giá sản phẩm (review, rating).
- Gửi thông báo tự động (email, SMS, hệ thống) qua cơ chế hướng sự kiện (Event-Driven).
- Đưa ra đề xuất gợi ý sản phẩm thông minh sử dụng trí tuệ nhân tạo (Gemini AI + CSDL Đồ thị Neo4j).
- Phân vai **Admin / Manager / Staff / Customer** với các giao diện quản trị và sử dụng riêng biệt.

Kiến trúc được thiết kế theo mô hình Microservices thực thụ để đảm bảo khả năng mở rộng độc lập, tối ưu hóa cơ sở dữ liệu cho từng nghiệp vụ (Database-per-Service) và nâng cao tính chịu lỗi của hệ thống.

### 1.2 Công nghệ sử dụng

- **Backend Framework**: Django 5.1 + Django REST Framework (DRF) làm nền tảng phát triển API.
- **Cơ sở dữ liệu**: MySQL cho `user-service` (quản lý phân quyền và thông tin người dùng), PostgreSQL cho tất cả các dịch vụ nghiệp vụ khác, và Neo4j cho lưu trữ hành vi người dùng trong `ai-service`.
- **API Gateway Layer (Nginx)**: Nginx hoạt động như một reverse proxy cổng vào duy nhất (Single Entrypoint) xử lý bảo mật, điều phối requests và rate limiting.
- **BFF (Backend For Frontend)**: Django app (`api-gateway`) đóng vai trò là API Gateway logic trả về JSON, thực hiện xác thực JWT và tổng hợp dữ liệu từ các service (API Composition/Orchestration).
- **Frontend UI**: Django app (`frontend`) độc lập thực hiện render giao diện HTML động bằng Bootstrap, lưu trữ JWT trong Signed Session Cookies bảo mật.
- **Message Broker**: Sử dụng **Redis** làm kênh truyền tin nhắn hướng sự kiện bất đồng bộ (Asynchronous Event Broker) giữa các microservices.
- **AI Integration**: Gemini 3.5 Flash API kết hợp cơ sở dữ liệu đồ thị Neo4j và FAISS Vector Index thực hiện RAG Chatbot và gợi ý sản phẩm (Sách, Quần áo, Đồ điện tử).
- **Containerization**: Docker & Docker Compose để quản lý vòng đời phát triển và deploy các containers.

---

## 2. Kiến trúc tổng thể

### 2.1 Các service chính

Hệ thống bao gồm 13 services chạy song song trong các Docker container độc lập:

1. `nginx-gateway` (Port `8000:80`): Cổng vào reverse proxy định tuyến requests.
2. `frontend` (Port nội bộ): Giao diện người dùng Web HTML.
3. `api-gateway` (Port nội bộ): BFF JSON API Orchestrator.
4. `user-service` (Port `8001`): Quản lý người dùng, phân quyền (MySQL).
5. `product-service` (Port `8002`): Quản lý sản phẩm sách, quần áo, đồ điện tử (PostgreSQL).
6. `cart-service` (Port `8003`): Quản lý giỏ hàng của khách hàng (PostgreSQL).
7. `order-service` (Port `8004`): Quản lý đơn đặt hàng (PostgreSQL).
8. `review-service` (Port `8005`): Quản lý đánh giá sản phẩm (PostgreSQL).
9. `shipping-service` (Port `8006`): Quản lý vận chuyển đơn hàng (PostgreSQL).
10. `payment-service` (Port `8007`): Quản lý giao dịch thanh toán (PostgreSQL).
11. `catalogue-service` (Port `8008`): Tổng hợp thông tin sách và thống kê rating (PostgreSQL).
12. `notification-service` (Port `8009`): Lắng nghe Redis events và tạo log thông báo (PostgreSQL).
13. `ai-service` (Port `8011`): Gợi ý sản phẩm Hybrid (Sách, Quần áo, Đồ điện tử) và RAG Chatbot (PostgreSQL + Neo4j).
14. `redis` (Port `6379`): Message Broker trung gian.
15. `neo4j` (Port `7474`, `7687`): Cơ sở dữ liệu đồ thị cho AI.

### 2.2 Luồng giao tiếp hệ thống

Hệ thống áp dụng chiến lược giao tiếp hỗn hợp (Hybrid Communication):

1. **Giao tiếp đồng bộ (Synchronous)**: Sử dụng các yêu cầu REST API qua HTTP đối với các nghiệp vụ cần phản hồi tức thời như:
   - Client đăng nhập, tải trang chủ.
   - Thêm sản phẩm vào giỏ hàng.
   - Catalogue service truy vấn danh sách sản phẩm và thống kê rating.
   - AI Service gọi API Gemini.

2. **Giao tiếp bất đồng bộ (Asynchronous)**: Sử dụng cơ chế Pub/Sub qua Redis Message Broker cho các sự kiện kích hoạt nghiệp vụ chéo nhằm giảm thiểu sự phụ thuộc trực tiếp giữa các service:
   - **Tạo người dùng**: `user-service` phát event `customer_created` -> `cart-service` tạo giỏ hàng trống mới và `notification-service` tạo thông báo chào mừng.
   - **Tạo đơn hàng**: `order-service` phát event `order_created` -> `notification-service` tạo thông báo xác nhận đơn.
   - **Xử lý thanh toán**: `payment-service` phát event `payment_processed` -> `order-service` tự động cập nhật đơn hàng thành `confirmed`/`cancelled` và `notification-service` tạo thông báo billing.
   - **Trạng thái giao hàng**: `shipping-service` phát event `shipment_updated` -> `notification-service` tạo thông báo hành trình vận đơn.

---

## 3. Mô tả chi tiết các service

### 3.1 api-gateway (BFF JSON Orchestrator)
- Cung cấp các endpoint điều phối dạng JSON sạch cho Frontend UI.
- Xác thực người dùng thông qua mã JWT (JSON Web Tokens).
- Phân phối quyền hạn dựa trên payload của token:
  - **Admin**: Quản lý toàn bộ hệ thống và tài khoản nhân viên.
  - **Manager / Staff**: Dashboard vận hành quản lý sản phẩm, đơn hàng.
  - **Customer**: Truy cập các thông tin cá nhân.
- Tự động gom nhóm dữ liệu (API Aggregation): khi tải trang Checkout hoặc Home, BFF gọi song song nhiều microservices và tổng hợp dữ liệu trả về trong một response duy nhất.

### 3.2 user-service
- Quản lý thông tin tài khoản Khách hàng (Customer), Nhân viên (Staff), Quản lý (Manager).
- Cơ sở dữ liệu sử dụng MySQL (`bookstore_user`) chứa bảng thông tin và phân quyền Django Auth.
- Phát sự kiện `customer_created` lên Redis khi có khách hàng đăng ký mới.

### 3.3 product-service
- Quản lý sản phẩm thuộc 3 loại chính: `book`, `clothing`, `electronic`.
- Lưu trữ thông tin động trong `attributes` dạng JSONField (ví dụ: tác giả đối với sách, size/color đối với quần áo, brand/model đối với đồ điện tử).
- Quản lý thông tin Nhà xuất bản (Publisher) và Danh mục (Category).

### 3.4 cart-service
- Quản lý giỏ hàng của từng khách hàng.
- Chứa logic thêm/xóa/sửa số lượng sản phẩm trong giỏ hàng.
- Lắng nghe sự kiện `customer_created` từ Redis để khởi tạo giỏ hàng trống ngay lập tức mà không cần gọi HTTP chéo.

### 3.5 order-service
- Tiếp nhận yêu cầu tạo đơn hàng từ giỏ hàng.
- Quản lý chi tiết đơn hàng (`OrderItem`) và trạng thái đơn hàng.
- Khi tạo đơn hàng thành công, phát đi sự kiện `order_created`.
- Lắng nghe sự kiện `payment_processed` để tự động đổi trạng thái đơn hàng thành `confirmed` (khi thanh toán thành công) hoặc `cancelled` (khi thanh toán thất bại).

### 3.6 payment-service
- Khởi tạo giao dịch thanh toán khi nhận được yêu cầu.
- Hỗ trợ các phương thức thanh toán: `cod`, `bank`, `card`, `wallet`.
- Khi trạng thái thanh toán chuyển đổi (ví dụ từ `initiated` sang `paid` hoặc `failed`), phát đi sự kiện `payment_processed`.

### 3.7 shipping-service
- Quản lý thông tin giao vận đơn hàng, địa chỉ, đơn vị vận chuyển (`carrier`) và mã vận đơn (`tracking_number`).
- Phát đi sự kiện `shipment_updated` khi cập nhật trạng thái vận đơn.

### 3.8 catalogue-service
- Service tổng hợp dữ liệu (Read Model Composer) không sở hữu DB nghiệp vụ riêng.
- Truy vấn REST API tới `product-service` và `review-service` để ghép điểm đánh giá trung bình cùng tổng số lượt review vào danh sách sản phẩm.

### 3.9 notification-service
- Service quản lý nhật ký thông báo.
- Chạy một background consumer thread lắng nghe toàn bộ các sự kiện Pub/Sub trên Redis (`customer_created`, `order_created`, `payment_processed`, `shipment_updated`).
- Tự động tạo và lưu trữ bản ghi thông báo tương ứng cho khách hàng phục vụ hiển thị trên hộp thư thông báo (inbox).

### 3.10 ai-service
- Service tích hợp AI, sử dụng mô hình học sâu **PyTorch LSTM** cho gợi ý theo chuỗi hành vi, kết hợp cơ sở dữ liệu đồ thị **Neo4j** và **Content Similarity (FAISS)** để chấm điểm hỗn hợp (Hybrid Scoring) đưa ra gợi ý sản phẩm tốt nhất (Sách, Quần áo, Đồ điện tử).
- Sử dụng **Gemini 3.5 Flash** cùng với **FAISS** (mã hóa vector ngữ nghĩa bằng `all-MiniLM-L6-v2`) để xây dựng chatbot RAG hỗ trợ tư vấn sản phẩm thông minh và phản hồi tự nhiên bằng tiếng Việt.
- Tích hợp **Real-time User Behavior Tracking**: frontend tự động gửi sự kiện (view, add to cart) về `POST /api/behavior/` của `ai-service` để cập nhật lập tức sang PostgreSQL và Neo4j, từ đó làm mới gợi ý Hybrid trên trang chủ.

---

## 4. Bảo mật và phân quyền

### 4.1 Xác thực JWT và Centralized Gateway Authentication
- **Quy trình Đăng nhập**: Người dùng đăng nhập qua `/login/` trên `frontend`. Frontend gửi thông tin đăng nhập tới `user-service/api/token/` qua BFF. Sau khi xác thực thành công, access token nhận được sẽ được lưu trữ đồng thời ở cả Django session và cookie `access_token` dưới dạng HttpOnly để bảo mật và cho phép Nginx trích xuất trực tiếp.
- **Xác thực Tập trung ở Gateway (Nginx auth_request)**:
  - Mọi yêu cầu tới API được bảo vệ (`/api/gateway/` và `/api/notifications/`) đều được Nginx Gateway đánh chặn bằng module `auth_request` trước khi gửi tới backend.
  - Nginx gửi subrequest xác thực nội bộ tới `/api/auth/verify/` thuộc `user-service`, truyền token lấy từ header `Authorization` hoặc cookie `access_token`.
  - Nếu token hợp lệ, `user-service` phản hồi `200 OK` kèm theo thông tin định danh của user trong response headers. Nginx trích xuất các header này và inject ngược lại dưới dạng các header `X-User-Id`, `X-User-Email`, `X-User-Role`, `X-User-Profile-Id`, `X-User-Superuser`, `X-User-Username` chuyển tiếp cho các backend microservices.
  - Để chống giả mạo thông tin người dùng từ client (Header Spoofing), Nginx Gateway sẽ xóa sạch mọi header `X-User-*` do client tự gửi trước khi thực hiện xác thực và chuyển tiếp.
  - Nếu token không hợp lệ, Nginx sẽ trực tiếp trả về lỗi `401 Unauthorized` chặn đứng request từ gateway.
- **Tích hợp phía Backend**: Middleware `JWTAuthenticationMiddleware` tại `api-gateway` và `frontend` chỉ cần đọc các header `X-User-*` đáng tin cậy đã được Gateway xác thực để dựng đối tượng `request.user` một cách cực kỳ nhanh chóng mà không cần giải mã lại chữ ký JWT. Middleware vẫn hỗ trợ giải mã trực tiếp cookie/session token làm phương án dự phòng (fallback) khi chạy phát triển local độc lập không qua gateway.

### 4.2 Phân quyền chức năng
- **Customer**: Chỉ có quyền thao tác trên giỏ hàng của chính mình, xem và đặt đơn hàng của mình, viết đánh giá cho sản phẩm đã mua, xem thông báo inbox cá nhân.
- **Staff/Manager**: Có quyền quản lý sản phẩm, danh mục, kiểm tra đơn hàng, cập nhật trạng thái giao vận/thanh toán.
- **Admin**: Quyền quản trị tối cao, quản lý tài khoản nhân viên/quản lý, giám sát toàn bộ log thông báo hệ thống.

### 4.3 Khả năng chịu lỗi và tự phục hồi (Fault Tolerance & Resilience)
Để đảm bảo hệ thống hoạt động ổn định khi xảy ra sự cố mạng chập chờn hoặc microservice phía sau bị sập, hệ thống triển khai các cơ chế:
- **Timeout**: Áp dụng thời gian chờ kết nối tối đa tại Nginx Gateway (`proxy_read_timeout 5s;`) và thời gian chờ gọi API tối đa tại BFF/Frontend (`timeout=3`) để tránh việc tắc nghẽn luồng xử lý và rò rỉ kết nối socket.
- **Retry (Thử lại)**: Tự động thử lại tối đa 2 lần đối với các yêu cầu đọc dữ liệu đồng bộ (HTTP GET - các thao tác có tính chất idempotent) khi gặp sự cố mạng tạm thời hoặc nhận mã lỗi 502/503/504 từ phía downstream.
- **Circuit Breaker (Cầu dao tự ngắt)**: Triển khai class `CircuitBreaker` tự thiết kế (không phụ thuộc thư viện ngoài) theo mô hình máy trạng thái (`CLOSED`, `OPEN`, `HALF_OPEN`) độc lập cho từng dịch vụ đích. Nếu một microservice gặp 5 lỗi liên tiếp, mạch điện chuyển sang `OPEN`, chặn đứng toàn bộ yêu cầu gọi tới dịch vụ đó trong vòng 15 giây và trả về dữ liệu dự phòng ngay lập tức (Fallback - ví dụ: giỏ hàng trống hoặc danh sách sách trống) giúp hệ thống không bị sập dây chuyền. Sau 15 giây, mạch chuyển sang `HALF_OPEN` để cho phép một yêu cầu đi qua chạy thử nghiệm; nếu thành công, mạch đóng lại (`CLOSED`) và phục hồi bình thường.

### 4.4 Giám sát & Quản lý Log tập trung (Prometheus + Loki + Grafana)
Để theo dõi sức khỏe hệ thống và xử lý sự cố nhanh chóng, hệ thống đã tích hợp giải pháp PLG Stack (Prometheus + Loki + Promtail + Grafana) dung lượng nhẹ:
- **Core metrics**: Custom Python metrics middleware đếm request (`django_http_requests_total`) và đo độ trễ của API trên `api-gateway`, `frontend`, và `user-service`, xuất dữ liệu theo chuẩn Prometheus qua endpoint `/metrics/`.
- **Logs tập trung**: Promtail thu thập log file Django và Nginx lưu trữ trong shared Docker volumes và ingest trực tiếp vào Loki.
- **Trực quan hóa**: Grafana kết nối tự động tới Prometheus & Loki làm data source mặc định, hỗ trợ truy vấn LogQL và PromQL trực tiếp qua giao diện Explore.

---

## 5. Kết luận & Hướng phát triển

Hệ thống Bookstore Microservices đã được chuẩn hóa kiến trúc hoàn chỉnh:

- Độc lập cơ sở dữ liệu (MySQL cho user, PostgreSQL cho các service khác).
- Tách biệt hoàn toàn Frontend UI phục vụ HTML tĩnh/động khỏi BFF API Gateway phục vụ JSON.
- Tích hợp cơ chế truyền tin hướng sự kiện bất đồng bộ qua Redis giúp tăng tính linh hoạt và khả năng chịu lỗi.
- Triển khai cơ chế xác thực tập trung tại API Gateway (Nginx `auth_request`) kết hợp các cơ chế chịu lỗi tự động (Timeout, Retry, Circuit Breaker) giúp tăng cường bảo mật và độ ổn định của hệ thống.
- Đầy đủ tài liệu OpenAPI, tài liệu kiến trúc Mermaid, và báo cáo phân tích thiết kế DDD.
