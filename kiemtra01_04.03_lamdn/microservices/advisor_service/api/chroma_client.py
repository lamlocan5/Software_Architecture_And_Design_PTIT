"""
ChromaDB client singleton — tương thích với chromadb==0.6.3
"""
import time
from django.conf import settings


_client = None
_laptop_col = None
_mobile_col = None
_advisory_col = None


def get_client():
    global _client
    if _client is None:
        import chromadb
        # Retry để đợi ChromaDB server khởi động hoàn toàn
        for attempt in range(5):
            try:
                _client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
                _client.heartbeat()  # Kiểm tra kết nối
                break
            except Exception as e:
                if attempt < 4:
                    time.sleep(3)
                else:
                    raise RuntimeError(f"Không thể kết nối ChromaDB sau 5 lần thử: {e}")
    return _client


def _get_or_create(name: str):
    """Tạo hoặc lấy collection với cosine similarity"""
    return get_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def get_laptop_collection():
    global _laptop_col
    if _laptop_col is None:
        _laptop_col = _get_or_create("laptops_kb")
    return _laptop_col


def get_mobile_collection():
    global _mobile_col
    if _mobile_col is None:
        _mobile_col = _get_or_create("mobiles_kb")
    return _mobile_col


def get_advisory_collection():
    global _advisory_col
    if _advisory_col is None:
        _advisory_col = _get_or_create("advisory_kb")
    return _advisory_col
