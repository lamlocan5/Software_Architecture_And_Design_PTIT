from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    customer_service_url: str = "http://customer-service:8001"
    order_service_url: str = "http://order-service:8005"
    kb_dir: Path = Path(__file__).resolve().parent.parent / "kb"
    chroma_dir: Path = Path(__file__).resolve().parent.parent / "chroma_data"
    artifacts_dir: Path = Path(__file__).resolve().parent.parent / "artifacts"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    # Google AI Studio / Gemini (ưu tiên dùng để sinh câu trả lời nếu được set)
    gemini_api_key: str = ""
    # Tên model REST v1beta (vd. gemini-2.5-flash). Tránh gemini-2.0-flash nếu free tier báo quota 0.
    gemini_model: str = "gemini-2.5-flash"
    # Dự phòng khi 429/404; gemini-1.5-flash không còn hợp lệ trên nhiều project → dùng alias mới
    gemini_model_fallback: str = "gemini-flash-latest"
    # Nhân giá (subtotal) để khớp thang đo lúc train (vd. VND); để 1 nếu train trên USD
    behavior_amount_scale: float = 1.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
