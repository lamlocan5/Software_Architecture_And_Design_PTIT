"""
RAG Pipeline — Retrieval-Augmented Generation với Gemini + ChromaDB
"""
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False

from django.conf import settings
from .chroma_client import get_laptop_collection, get_mobile_collection, get_advisory_collection
from .behaviour import get_profile_summary

# Khởi tạo Gemini (lazy — chỉ khi thực sự dùng)
_model = None


def _get_model():
    global _model
    if not _GENAI_AVAILABLE:
        raise RuntimeError("google-generativeai không được cài đặt")
    if _model is None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model


def _detect_intent(query: str) -> dict:
    """Phát hiện ý định tìm kiếm từ câu hỏi"""
    q = query.lower()
    intents = {
        'want_laptop':  any(w in q for w in ['laptop', 'máy tính', 'notebook', 'macbook']),
        'want_mobile':  any(w in q for w in ['điện thoại', 'phone', 'iphone', 'samsung', 'xiaomi', 'oppo', 'vivo', 'di động']),
        'want_gaming':  any(w in q for w in ['game', 'gaming', 'chơi game', 'rtx', 'fps']),
        'want_budget':  any(w in q for w in ['rẻ', 'giá rẻ', 'tiết kiệm', 'ngân sách', 'sinh viên', 'dưới']),
        'want_premium': any(w in q for w in ['cao cấp', 'xịn', 'tốt nhất', 'flagship', 'pro max']),
        'want_camera':  any(w in q for w in ['camera', 'chụp', 'ảnh', 'selfie', 'zoom']),
        'want_compare': any(w in q for w in ['vs', 'so sánh', 'hay là', 'khác gì', 'tốt hơn']),
    }
    return intents


def _retrieve_context(query: str, intents: dict, n_results: int = 4) -> str:
    """Truy xuất tài liệu liên quan từ ChromaDB"""
    contexts = []

    # Luôn tìm trong advisory KB
    try:
        adv_col = get_advisory_collection()
        adv_results = adv_col.query(query_texts=[query], n_results=3)
        for i, doc in enumerate(adv_results['documents'][0]):
            meta = adv_results['metadatas'][0][i]
            contexts.append(f"[Tư vấn: {meta.get('title', '')}]\n{doc}")
    except Exception:
        pass

    # Tìm laptop nếu query liên quan
    if intents.get('want_laptop') or (not intents.get('want_mobile')):
        try:
            lap_col = get_laptop_collection()
            lap_results = lap_col.query(query_texts=[query], n_results=n_results)
            for doc in lap_results['documents'][0]:
                contexts.append(f"[Sản phẩm laptop]\n{doc}")
        except Exception:
            pass

    # Tìm điện thoại nếu query liên quan
    if intents.get('want_mobile') or (not intents.get('want_laptop')):
        try:
            mob_col = get_mobile_collection()
            mob_results = mob_col.query(query_texts=[query], n_results=n_results)
            for doc in mob_results['documents'][0]:
                contexts.append(f"[Sản phẩm điện thoại]\n{doc}")
        except Exception:
            pass

    return '\n\n---\n\n'.join(contexts[:10])  # Limit context size


def _build_prompt(query: str, context: str, user_profile: str, history: list) -> str:
    """Tạo prompt đầy đủ cho Gemini"""
    system = """Bạn là trợ lý tư vấn mua sắm điện tử chuyên nghiệp của một cửa hàng bán laptop và điện thoại tại Việt Nam.

Nhiệm vụ của bạn:
- Tư vấn sản phẩm phù hợp dựa trên nhu cầu, ngân sách và hành vi mua sắm của khách hàng
- Trả lời bằng tiếng Việt, thân thiện, rõ ràng và có cấu trúc
- Chỉ gợi ý sản phẩm CÓ TRONG dữ liệu được cung cấp
- Nêu rõ giá (tính theo triệu đồng), điểm mạnh, điểm yếu
- Nếu khách hỏi so sánh, hãy so sánh trực tiếp và đưa ra khuyến nghị cụ thể
- Kết thúc bằng câu hỏi để hiểu thêm nhu cầu (nếu chưa rõ)

Phong cách: Chuyên nghiệp, nhiệt tình, trung thực - không nói quá về sản phẩm."""

    profile_section = f"\n[Hồ sơ khách hàng]\n{user_profile}\n" if user_profile else ""

    history_section = ""
    if history:
        history_section = "\n[Lịch sử hội thoại]\n"
        for h in history[-6:]:  # 3 lượt cuối
            role = "Khách" if h['role'] == 'user' else "Tư vấn viên"
            history_section += f"{role}: {h['content']}\n"

    return f"""{system}
{profile_section}
[Thông tin sản phẩm và tư vấn trong cửa hàng]
{context}
{history_section}
[Câu hỏi của khách hàng]
{query}

[Câu trả lời của Tư vấn viên]"""


def chat(query: str, customer_id: int = None, history: list = None) -> dict:
    """
    Hàm chat chính — RAG pipeline hoàn chỉnh
    Returns: {'response': str, 'sources': list}
    """
    history = history or []

    # 1. Phát hiện intent
    intents = _detect_intent(query)

    # 2. Lấy user profile từ behaviour engine
    user_profile = ""
    if customer_id:
        try:
            user_profile = get_profile_summary(customer_id)
        except Exception:
            pass

    # 3. Truy xuất context từ KB
    context = _retrieve_context(query, intents)

    if not context:
        context = "Không tìm thấy thông tin sản phẩm phù hợp trong hệ thống."

    # 4. Build prompt
    prompt = _build_prompt(query, context, user_profile, history)

    # 5. Gọi Gemini
    try:
        model = _get_model()
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 1024,
            }
        )
        answer = response.text
    except Exception as e:
        answer = f"Xin lỗi, hệ thống tư vấn tạm thời gặp sự cố: {str(e)}. Vui lòng thử lại sau."

    return {
        'response': answer,
        'intent': intents,
        'has_profile': bool(user_profile),
    }
