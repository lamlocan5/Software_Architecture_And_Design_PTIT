# 🧠 AI Service - Bookstore Microservice

Dịch vụ AI cung cấp các tính năng gợi ý sản phẩm thông minh và trợ lý ảo (Chatbot) tư vấn bán hàng tự động. Dịch vụ này tích hợp mô hình học sâu **PyTorch LSTM** cho gợi ý theo chuỗi hành vi, cơ sở dữ liệu đồ thị **Neo4j** cho gợi ý cộng tác, và hệ thống **RAG (Retrieval-Augmented Generation)** kết hợp **FAISS** cùng **Gemini 3.5 Flash** để vận hành Chatbot tư vấn cho cả 3 danh mục: **Sách, Thời trang (Quần áo) và Đồ điện tử**.

---

## 🏗️ Kiến trúc các thành phần AI

AI Service kết hợp 3 phương pháp tiếp cận chính để đưa ra kết quả gợi ý tối ưu nhất (Hybrid Scoring):

```
                       +---------------------------------------+
                       |           User Behavior Log           |
                       +---------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
                    v                      v                      v
        +-----------------------+ +-----------------+ +-----------------------+
        |   PyTorch LSTM (5L)   | |   Neo4j Graph   | |  Content Similarity   |
        |  Sequence Predictor   | |  Collaborative  | |    Vector Search      |
        +-----------------------+ +-----------------+ +-----------------------+
                    |                      |                      |
                    +----------------------+----------------------+
                                           |
                                           v
                            +-----------------------------+
                            |   Hybrid Scorer (Weighted)  |
                            +-----------------------------+
                                           |
                                           v
                            +-----------------------------+
                            |    Top-K Recommendations    |
                            +-----------------------------+
```

### 1. Học sâu Gợi ý Chuỗi (PyTorch LSTM Model)
* Mô hình mạng hồi quy tuần hoàn (RNN) gồm 5 lớp:
  1. `nn.Embedding` (Lớp nhúng sản phẩm)
  2. `nn.LSTM` (Lớp tuần hoàn cấp 1)
  3. `nn.LSTM` (Lớp tuần hoàn cấp 2)
  4. `nn.LSTM` (Lớp tuần hoàn cấp 3)
  5. `nn.Linear` (Lớp Dense ánh xạ xác suất đoán sản phẩm tiếp theo)
* Huấn luyện trực tiếp trên chuỗi lịch sử tương tác (views, cart, buys) của người dùng để đoán sản phẩm họ muốn xem tiếp theo.

### 2. Gợi ý Đồ thị (Neo4j Graph Database)
* Biểu diễn thực thể `(User)` và `(Product)` dưới dạng các nút (Nodes).
* Ánh xạ các hành vi thành các mối quan hệ (Relationships) `:VIEW` và `:BUY` đi kèm nhãn thời gian.
* Sử dụng ngôn ngữ truy vấn Cypher để thực hiện giải thuật gợi ý lân cận (Neighborhood-based Collaborative Filtering) và phân tích các tuyến liên kết đồ thị (Path-based Recommendation).

### 3. Trợ lý tư vấn RAG (FAISS + Sentence Transformers + Gemini AI)
* **Mã hóa ngữ nghĩa:** Sử dụng mô hình `all-MiniLM-L6-v2` để chuyển đổi mô tả của toàn bộ đầu sách, quần áo (màu sắc/kích cỡ) và đồ điện tử (hãng/model) thành các vector đặc trưng 384 chiều.
* **Chỉ mục tìm kiếm:** Lưu trữ các vector vào cơ sở dữ liệu vector cực nhanh **FAISS** (IndexFlatL2).
* **Sinh câu trả lời:** Tìm kiếm top-K sản phẩm phù hợp nhất, tiêm vào Prompt ngữ cảnh và gửi đến **Gemini 3.5 Flash API** để tạo ra câu trả lời tư vấn bằng tiếng Việt tự nhiên, chuyên nghiệp.

---

## 📡 Chi tiết các API Endpoints

Mặc định dịch vụ chạy trên cổng **`8011`** (nội bộ container chạy cổng `8000`).

### 1. Ghi nhận hành vi người dùng
* **Endpoint:** `POST /behavior/`
* **Request Body (JSON):**
  ```json
  {
    "user_id": 7,
    "product_id": 1,
    "behavior_type": "view"  // Hoặc "buy", "cart"
  }
  ```
* **Mô tả:** Lưu log hành vi vào cơ sở dữ liệu quan hệ PostgreSQL và đồng bộ sang Graph Database Neo4j trong thời gian thực.

### 2. Lấy gợi ý sản phẩm Hybrid
* **Endpoint:** `GET /recommend/?user_id=<user_id>&limit=<limit>`
* **Mô tả:** Tính toán điểm tổng hợp từ LSTM, các đường đi đồ thị trên Neo4j, và tương đồng nội dung để trả về danh sách ID sản phẩm gợi ý tốt nhất cho người dùng (hỗ trợ cả Sách, Thời trang, Đồ điện tử).
* **Response (JSON):**
  ```json
  {
    "user_id": 7,
    "recommended_ids": [15, 14, 6, 8, 13, 23],
    "source": "hybrid"
  }
  ```

### 3. Trợ lý ảo tư vấn sản phẩm (Chatbot RAG)
* **Endpoint:** `POST /chatbot/`
* **Request Body (JSON):**
  ```json
  {
    "query": "Tôi muốn mua một chiếc laptop Asus tầm 20 triệu để làm văn phòng"
  }
  ```
* **Response (JSON):**
  ```json
  {
    "response": "Chào bạn! Bookstore xin gợi ý mẫu **Laptop Asus Zenbook 14 OLED (ID: 21)** với giá bán 21.990.000 VND. Dòng Zenbook nổi tiếng với thiết kế sang trọng, mỏng nhẹ, màn hình OLED cực kỳ sắc nét rất thích hợp cho công việc văn phòng..."
  }
  ```

### 4. Gợi ý thông minh Legacy (Tương thích ngược)
* **Endpoint:** `POST /recommendations/`
* **Mô tả:** Chọn lọc gợi ý trực tiếp từ danh sách sản phẩm đầu vào sử dụng Gemini prompt hoặc giải thuật fallback.

---

## ⚙️ Cấu hình Biến môi trường

Khai báo các biến sau trong file `.env` ở thư mục gốc:

```env
# API key để gọi mô hình ngôn ngữ Gemini 3.5 Flash
GEMINI_API_KEY=AIzaSy...

# Kết nối cơ sở dữ liệu đồ thị Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123

# Kết nối cơ sở dữ liệu quan hệ PostgreSQL của AI service
DB_HOST=host.docker.internal
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=1234
DB_NAME=bookstore_ai
```

---

## 📓 Thư mục Jupyter Notebooks (`notebooks/`)

Cung cấp hai tài liệu tương tác trực quan để phát triển và kiểm tra thuật toán:

1. **[train_lstm.ipynb](file:///c:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice/ai-service/notebooks/train_lstm.ipynb):**
   * Tổng hợp chuỗi hành vi của người dùng từ Django ORM.
   * Huấn luyện thử nghiệm mô hình PyTorch LSTM và vẽ biểu đồ suy giảm hàm mất mát (loss curve).
   * Kiểm thử dự đoán Top-K xác suất.

2. **[visualize_rag.ipynb](file:///c:/Users/Admin/Desktop/PTIT/Y4_T2/SoftwareArchitectureAndDesign/bookstore-microservice/ai-service/notebooks/visualize_rag.ipynb):**
   * Mã hóa ngữ nghĩa toàn bộ danh mục sách hiện có.
   * Sử dụng PCA / t-SNE để chiếu vector 384 chiều xuống không gian 2D và trực quan hóa phân bố sách bằng biểu đồ phân tán Scatter Plot.
   * Thử nghiệm chất lượng tìm kiếm vector FAISS và sinh văn bản chatbot RAG.
