Sau khi chạy train/model_behavior.ipynb và lưu file, sao chép vào thư mục này:

  model_behavior.h5
  scaler.pkl
  label_encoder.pkl

Khi thiếu file, dịch vụ tư vấn vẫn chạy RAG nhưng không có dự đoán hành vi (behavior_label).

Nếu dữ liệu train dùng đơn vị tiền khác (ví dụ VND), đặt biến môi trường BEHAVIOR_AMOUNT_SCALE trong docker-compose
(ví dụ 24000) để quy đổi subtotal từ giỏ/đơn cho sát thang lúc huấn luyện.
