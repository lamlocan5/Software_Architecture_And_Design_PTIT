"""
recommend-service/recommend/ml_model.py

Microservice pattern: Service này KHÔNG truy cập DB trực tiếp.
Thay vào đó gọi behavior-service để lấy sequence và product-service để lấy chi tiết.

Flow:
  1. Gọi behavior-service:8003 → lấy 7 product_id gần nhất
  2. Load model_best.h5 → predict → top N indices
  3. Gọi product-service:8001 → lấy thông tin sản phẩm
"""
import os
import numpy as np
import requests

# ---- Cấu hình ----
MAX_PRODUCT_ID = 30
SEQ_LEN = 7
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model_best.h5')

BEHAVIOR_SERVICE_URL = os.getenv('BEHAVIOR_SERVICE_URL', 'http://127.0.0.1:8003')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://127.0.0.1:8001')

_model = None


def load_model():
    global _model
    if _model is None:
        try:
            import tensorflow as tf
            _model = tf.keras.models.load_model(MODEL_PATH)
            print(f"[Recommend] Model loaded: input={_model.input_shape}, output={_model.output_shape}")
        except Exception as e:
            print(f"[Recommend] WARNING: {e}")
            _model = None
    return _model


def get_user_sequence(user_id: int) -> list:
    """
    Gọi behavior-service qua HTTP để lấy sequence.
    Đây là inter-service communication trong microservice.
    """
    try:
        url = f"{BEHAVIOR_SERVICE_URL}/api/behaviors/sequence/{user_id}/"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get('sequence', [0] * SEQ_LEN)
    except requests.RequestException as e:
        print(f"[Recommend] Lỗi gọi behavior-service: {e}")
    return [0] * SEQ_LEN


def get_products_by_ids(product_ids: list) -> list:
    """
    Gọi product-service qua HTTP để lấy thông tin sản phẩm.
    Đây là inter-service communication trong microservice.
    """
    if not product_ids:
        return []
    try:
        ids_str = ','.join(map(str, product_ids))
        url = f"{PRODUCT_SERVICE_URL}/api/products/by-ids/?ids={ids_str}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get('products', [])
    except requests.RequestException as e:
        print(f"[Recommend] Lỗi gọi product-service: {e}")
    return []


def predict_next_products(user_id: int, top_n: int = 5) -> list:
    """
    Pipeline dự đoán:
      1. Lấy sequence từ behavior-service
      2. Predict bằng model_best.h5
      3. Trả về danh sách product_id (chưa có metadata)
    """
    model = load_model()

    # Lấy sequence từ behavior-service
    seq = get_user_sequence(user_id)
    print(f"[Recommend] User {user_id} sequence: {seq}")

    if model is None:
        return _fallback(user_id, top_n)

    # Normalize và reshape cho SimpleRNN
    seq_normalized = np.array(seq, dtype=np.float32) / MAX_PRODUCT_ID
    seq_input = seq_normalized.reshape(1, SEQ_LEN, 1)

    try:
        predictions = model.predict(seq_input, verbose=0)[0]
    except Exception as e:
        print(f"[Recommend] Predict error: {e}")
        return _fallback(user_id, top_n)

    top_indices = np.argsort(predictions)[::-1]
    result = []
    output_size = len(predictions)

    for idx in top_indices:
        pid = int(idx) + 1 if output_size == MAX_PRODUCT_ID else int(idx)
        if 1 <= pid <= MAX_PRODUCT_ID:
            result.append(pid)
        if len(result) >= top_n:
            break

    return result


def _fallback(user_id: int, top_n: int) -> list:
    """Fallback: trả về product_id phổ biến (đơn giản)."""
    return list(range(1, top_n + 1))
