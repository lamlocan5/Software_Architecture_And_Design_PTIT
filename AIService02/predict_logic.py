"""
predict_logic.py — Câu 2a (integration): Dùng model_best.keras để dự đoán hành vi user
Feature pipeline khớp đúng với train.ipynb:
  X = [user_id_enc, product_id_enc, device_enc, category_enc, session_duration, price]
  -> StandardScaler -> reshape (1,1,6) -> model.predict()
"""
import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ==========================================
# ACTION CLASSES (khớp với LabelEncoder trong train.ipynb)
# Thứ tự alphabetical theo sklearn LabelEncoder
# ==========================================
ACTION_CLASSES = ["add_to_cart", "click", "view"]   # sorted alphabetically
ACTION_LABELS  = {i: a for i, a in enumerate(ACTION_CLASSES)}
ACTION_SCORE   = {"view": 1, "click": 2, "add_to_cart": 5}

# ==========================================
# FIT ENCODER & SCALER từ dữ liệu gốc (một lần, cached)
# ==========================================
_encoder_dict  = None   # {col: LabelEncoder}
_scaler        = None   # StandardScaler
_df_ref        = None   # reference dataframe

def _build_preprocessors():
    """Tái tạo encoder + scaler y hệt như trong train.ipynb"""
    global _encoder_dict, _scaler, _df_ref

    if _encoder_dict is not None:
        return

    from sklearn.preprocessing import LabelEncoder, StandardScaler

    df = pd.read_csv("data_user500.csv")
    _df_ref = df.copy()

    cat_cols = ["user_id", "product_id", "device", "category"]
    _encoder_dict = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        _encoder_dict[col] = le

    # X = drop action, action_encoded (nếu có), timestamp
    X = df.drop(columns=[c for c in ["action", "action_encoded", "timestamp"] if c in df.columns])

    _scaler = StandardScaler()
    _scaler.fit(X)


def _encode_row(user_id: str, product_id: str,
                device: str, category: str,
                session_duration: int, price: float) -> np.ndarray:
    """
    Encode 1 sample thành vector 6 features chuẩn hóa.
    Nếu user/product chưa biết → dùng mode của training set.
    """
    _build_preprocessors()

    def safe_encode(le, val):
        classes = list(le.classes_)
        if val in classes:
            return le.transform([val])[0]
        # Unknown → dùng phần tử ở giữa
        return len(classes) // 2

    uid_enc  = safe_encode(_encoder_dict["user_id"],   user_id)
    pid_enc  = safe_encode(_encoder_dict["product_id"], product_id)
    dev_enc  = safe_encode(_encoder_dict["device"],     device.lower())
    cat_enc  = safe_encode(_encoder_dict["category"],   category.lower())

    raw = np.array([[uid_enc, pid_enc, dev_enc, cat_enc,
                     session_duration, price]], dtype=np.float64)
    scaled = _scaler.transform(raw)
    return scaled.reshape(1, 1, 6).astype(np.float32)


# ==========================================
# LAZY LOAD MODEL
# ==========================================
_model        = None
_model_loaded = False
_load_error   = None


def _load_model():
    global _model, _model_loaded, _load_error
    if _model_loaded:
        return _model

    model_path = "model_best.keras"
    if not os.path.exists(model_path):
        _load_error = f"Model file not found: {model_path}"
        _model_loaded = True
        return None

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(model_path)
        _model_loaded = True
        return _model
    except Exception as e:
        _load_error = str(e)
        _model_loaded = True
        return None


# ==========================================
# PREDICTION FUNCTIONS
# ==========================================
def predict_next_action(device: str = "mobile",
                        category: str = "electronics",
                        session_duration: int = 300,
                        price: float = 100.0,
                        user_id: str = "U001",
                        product_id: str = "P001") -> dict:
    """
    Dự đoán hành vi tiếp theo của user.
    Returns: {predicted_action, probabilities, confidence, using_model}
    """
    model = _load_model()
    if model is None:
        return _rule_based_prediction(device, category, session_duration, price)

    try:
        X = _encode_row(user_id, product_id, device, category,
                        session_duration, price)
        probs    = model.predict(X, verbose=0)[0]
        pred_idx = int(np.argmax(probs))

        return {
            "predicted_action": ACTION_LABELS[pred_idx],
            "probabilities":    {ACTION_CLASSES[i]: float(probs[i]) for i in range(3)},
            "confidence":       float(probs[pred_idx]),
            "using_model":      True,
        }
    except Exception as e:
        return _rule_based_prediction(device, category, session_duration, price)


def _rule_based_prediction(device, category, session_duration, price):
    """Fallback heuristic khi model không khả dụng"""
    score = 0
    if session_duration > 400: score += 2
    if price < 200:             score += 1
    if device == "mobile":      score += 1
    if category == "electronics": score -= 1

    if score >= 3:
        action, probs = "add_to_cart", [0.5, 0.3, 0.2]
    elif score >= 1:
        action, probs = "click",       [0.2, 0.5, 0.3]
    else:
        action, probs = "view",        [0.1, 0.3, 0.6]

    return {
        "predicted_action": action,
        "probabilities":    {ACTION_CLASSES[i]: probs[i] for i in range(3)},
        "confidence":       max(probs),
        "using_model":      False,
    }


# ==========================================
# RECOMMENDATION FUNCTIONS
# ==========================================
def get_top_products_for_user(df: pd.DataFrame,
                               user_id: str,
                               top_n: int = 5) -> pd.DataFrame:
    """
    Gợi ý sản phẩm cho user dựa trên interaction history.
    Ưu tiên sản phẩm được nhiều user khác add_to_cart trong cùng category yêu thích.
    """
    user_data = df[df["user_id"] == user_id]
    if user_data.empty:
        return get_popular_products(df, top_n)

    # Category yêu thích của user
    fav_cat = user_data["category"].mode()[0]

    # Sản phẩm user đã mua
    bought = user_data[user_data["action"] == "add_to_cart"]["product_id"].unique()

    # Tính điểm cho từng sản phẩm
    scored = (
        df.groupby("product_id")
        .apply(lambda g: sum(ACTION_SCORE.get(a, 0) for a in g["action"]))
        .reset_index()
        .rename(columns={0: "popularity_score"})
    )

    # Bonus nếu cùng category yêu thích
    product_info = (
        df.groupby("product_id")
        .agg(category=("category", "first"), avg_price=("price", "mean"))
        .reset_index()
    )
    result = pd.merge(scored, product_info, on="product_id")
    result["total_score"] = result["popularity_score"] + result["category"].apply(
        lambda c: 20 if c == fav_cat else 0
    )

    # User score (chính sản phẩm user đã click/view)
    user_sc = (
        user_data.groupby("product_id")
        .apply(lambda g: sum(ACTION_SCORE.get(a, 0) for a in g["action"]) * 2)
        .reset_index()
        .rename(columns={0: "user_score"})
    )
    result = pd.merge(result, user_sc, on="product_id", how="left")
    result["user_score"]   = result["user_score"].fillna(0)
    result["total_score"] += result["user_score"]

    # Bỏ sản phẩm đã mua
    result = result[~result["product_id"].isin(bought)]
    result["avg_price"] = result["avg_price"].round(2)

    return result.nlargest(top_n, "total_score").reset_index(drop=True)


def get_popular_products(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top sản phẩm phổ biến (toàn hệ thống)"""
    scored = (
        df.groupby("product_id")
        .apply(lambda g: sum(ACTION_SCORE.get(a, 0) for a in g["action"]))
        .reset_index()
        .rename(columns={0: "popularity_score"})
    )
    info = (
        df.groupby("product_id")
        .agg(category=("category", "first"), avg_price=("price", "mean"))
        .reset_index()
    )
    result = pd.merge(scored, info, on="product_id")
    result["avg_price"] = result["avg_price"].round(2)
    return result.nlargest(top_n, "popularity_score").reset_index(drop=True)
