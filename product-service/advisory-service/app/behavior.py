from __future__ import annotations

import logging
import pickle
from typing import Any

import numpy as np

from app.config import settings
from app.features import FEATURE_ORDER

_MODEL = None
_SCALER: Any = None
_ENCODER: Any = None
_WARNED = False
# Đã thử load model nhưng lỗi (vd. .h5 không tương thích Keras) — không thử lại mỗi request
_BEHAVIOR_LOAD_FAILED = False

logger = logging.getLogger(__name__)


def artifacts_present() -> bool:
    d = settings.artifacts_dir
    return all(
        (d / name).is_file() for name in ("model_behavior.h5", "scaler.pkl", "label_encoder.pkl")
    )


def _load() -> None:
    global _MODEL, _SCALER, _ENCODER, _WARNED, _BEHAVIOR_LOAD_FAILED
    if _BEHAVIOR_LOAD_FAILED:
        return
    if _MODEL is not None:
        return
    if not artifacts_present():
        if not _WARNED:
            logger.warning(
                "Thiếu artifacts mô hình hành vi. Sao chép model_behavior.h5, scaler.pkl, "
                "label_encoder.pkl vào advisory-service/artifacts/ sau khi chạy notebook."
            )
            _WARNED = True
        return
    import tensorflow as tf  # noqa: WPS433 — tải lazy để khởi động nhanh hơn khi không dùng

    # Keras 3 mặc định chặt; file H5 cũ dùng batch_shape trong InputLayer cần bật deserialize "legacy"
    try:
        import keras

        _enable = getattr(keras.config, "enable_unsafe_deserialization", None)
        if callable(_enable):
            _enable()
    except Exception:
        pass

    def _abort_load(reason: BaseException) -> None:
        global _BEHAVIOR_LOAD_FAILED
        logger.error("Không load được model hành vi (.h5): %s", reason)
        _BEHAVIOR_LOAD_FAILED = True

    d = settings.artifacts_dir
    path = d / "model_behavior.h5"
    _model = None
    try:
        # Keras 3 (TF 2.15): H5 cũ có InputLayer(batch_shape=...) — cần safe_mode=False
        _model = tf.keras.models.load_model(path, compile=False, safe_mode=False)
    except TypeError as e:
        msg = str(e).lower()
        # Chỉ fallback khi lỗi là *không có* tham số safe_mode; không fallback khi lỗi deserialize (batch_shape)
        if "safe_mode" in msg or "unexpected keyword" in msg:
            try:
                _model = tf.keras.models.load_model(path, compile=False)
            except Exception as e2:
                _abort_load(e2)
                _MODEL = None
                _SCALER = None
                _ENCODER = None
                return
        else:
            _abort_load(e)
            _MODEL = None
            _SCALER = None
            _ENCODER = None
            return
    except Exception as e:
        _abort_load(e)
        _MODEL = None
        _SCALER = None
        _ENCODER = None
        return

    try:
        with open(d / "scaler.pkl", "rb") as f:
            _scaler = pickle.load(f)
        with open(d / "label_encoder.pkl", "rb") as f:
            _encoder = pickle.load(f)
    except Exception as e:
        logger.error("Không load scaler/encoder: %s", e)
        _BEHAVIOR_LOAD_FAILED = True
        _MODEL = None
        _SCALER = None
        _ENCODER = None
        return

    _MODEL = _model
    _SCALER = _scaler
    _ENCODER = _encoder


def predict_label(feature_row: dict[str, int]) -> str | None:
    try:
        _load()
        if _MODEL is None or _SCALER is None or _ENCODER is None:
            return None
        X = np.array([[feature_row[k] for k in FEATURE_ORDER]], dtype=np.float32)
        Xs = _SCALER.transform(X)
        probs = _MODEL.predict(Xs, verbose=0)
        idx = int(np.argmax(probs, axis=1)[0])
        return str(_ENCODER.inverse_transform([idx])[0])
    except Exception as e:
        logger.warning("predict_label lỗi, bỏ qua cá nhân hóa hành vi: %s", e)
        return None
