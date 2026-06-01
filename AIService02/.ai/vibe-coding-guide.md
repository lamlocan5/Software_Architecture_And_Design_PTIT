## 2. Nội dung file `vibe-coding-guide.md` (Hướng dẫn tương tác)

```markdown
# 🤖 Hướng dẫn Phát triển Microservices với AI (Vibe Coding)

> ⚠️ AI là "Co-pilot" (Người lái phụ), bạn là "Pilot" (Cơ trưởng). Kiến trúc Microservices rất phức tạp, nếu phó mặc hoàn toàn cho AI, hệ thống của bạn sẽ bị gãy vỡ (broken) ở khâu giao tiếp giữa các service.

---

## AI Coding Tools & Configuration

| Tool           | File cấu hình (auto-loaded)       | Trạng thái dự án                   |
| -------------- | --------------------------------- | ---------------------------------- |
| GitHub Copilot | `.github/copilot-instructions.md` | Hỗ trợ code autocomplete           |
| Cursor         | `.cursorrules`                    | Đọc toàn bộ workspace cực tốt      |
| Windsurf       | `.windsurfrules`                  | Quản lý multi-agents hiệu quả      |
| ChatGPT/Claude | Trực tiếp qua Web                 | Dùng để review kiến trúc/debug lỗi |

Tất cả các rules của IDE phải được tham chiếu từ [`AGENTS.md`](AGENTS.md) — bộ luật tối cao của hệ thống E-commerce này.

---

## Chiến lược "Vibe Coding" cho Microservices

Vì dự án có tới **15+ thư mục services**, AI rất dễ bị "ảo giác" (hallucination) và viết nhầm file. Hãy tuân thủ các quy tắc sau:

### 1. Chỉ định rõ Service

Thay vì prompt: _"Tạo chức năng thêm vào giỏ hàng"_.
Hãy prompt: _"Trong thư mục `cart-service`, tạo endpoint `POST /cart/add` bằng [Ngôn ngữ/Framework]. Sau đó ở thư mục `api-gateway`, cấu hình route để forward request `/api/cart/_`vào`cart-service`."\*

### 2. Quản lý Database Độc Lập

Nếu bạn yêu cầu AI tạo bảng, hãy nhắc AI: _"Nhớ rằng `order-service` dùng DB riêng. Hãy tạo script SQL init trong thư mục `data/order-db-init/`."_

### 3. Gọi chéo (Inter-service Communication)

Khi cần một service gọi service khác, hãy prompt rõ ràng:
_"Trong `order-service`, tôi cần kiểm tra tồn kho. Hãy viết một REST Client gọi sang `catalogue-service` qua url nội bộ của Docker (ví dụ: `http://catalogue-service:8080`)."_

---

## Mẫu Prompt hữu ích cho Dự án này

Copy và điền vào chỗ trống để AI làm việc chính xác nhất:

**1. Tạo Microservice mới (Khung cơ bản):**

> "Dựa theo chuẩn của dự án trong AGENTS.md, hãy khởi tạo cấu trúc cho `[TÊN_SERVICE]`. Service này chịu trách nhiệm `[CHỨC_NĂNG]`. Viết file Dockerfile, requirements/pom.xml, và endpoint `GET /health`. Đảm bảo nó chạy ở port `[PORT_NUMBER]`."

**2. Thêm tính năng xác thực (Auth):**

> "Trong `[TÊN_SERVICE]`, hãy viết một middleware/interceptor để chặn các request không có header Authorization. Parse JWT token, giải mã nó bằng secret key trong `.env`, và kiểm tra xem role có phải là `[ROLE_CẦN_THIẾT]` không."

**3. Tích hợp AI (Cho riêng `recommender-ai-service`):**

> "Trong `recommender-ai-service`, tôi cần viết một endpoint RAG. Hãy dùng Langchain kết nối vào Neo4j (bolt://neo4j-db:7687). Khi user gửi câu hỏi, dịch nó thành Cypher query, lấy kết quả từ Graph và dùng OpenAI trả lời."

---

## Tiêu chí Báo cáo & Trình bày (Nên chuẩn bị trước)

Với một kiến trúc đồ sộ thế này, giảng viên sẽ hỏi xoáy vào cách hệ thống vận hành. Bạn cần nắm chắc:

1. **Khởi chạy (Spin-up)**: `docker-compose up` hoặc chạy script `compile_code.ps1` có lỗi gì không? Các container có health-check "xanh" hết chưa?
2. **Luồng dữ liệu (Data Flow)**: Demo luồng từ Đăng ký -> Đăng nhập -> Tìm hàng -> Mua hàng -> Thanh toán. Chỉ ra log của API Gateway khi request đi qua.
3. **Khả năng chịu lỗi (Resilience)**: Nếu `review-service` chết, hệ thống có vẫn cho phép khách mua hàng được không? (Trả lời: Phải được).
4. **Phần AI Integration**: Mở `recommender-ai-service`, show biểu đồ Deep Learning, show hình ảnh Graph trên Neo4j Browser và demo chat RAG thành công.
```
