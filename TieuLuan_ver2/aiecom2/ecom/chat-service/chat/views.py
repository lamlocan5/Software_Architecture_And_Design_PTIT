"""
chat-service/chat/views.py
POST /api/chat/ → RAG pipeline: Neo4j + Gemini
"""
import os
import re
import requests
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from . import neo4j_client

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://127.0.0.1:8001')

_gemini_model = None


def get_gemini():
    global _gemini_model
    if _gemini_model is None and GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        except Exception as e:
            print(f"[Chat/Gemini] Lỗi: {e}")
    return _gemini_model


def build_product_map() -> dict:
    """Gọi product-service để lấy tên sản phẩm (inter-service call)."""
    try:
        res = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/", timeout=5)
        products = res.json().get('products', [])
        return {p['id']: p['name'] for p in products}
    except Exception:
        return {}


def parse_intent(query: str):
    q = query.lower()
    for p in [r'user\s*(\d+)', r'người dùng\s*(\d+)', r'id\s*(\d+)', r'gợi ý cho.*?(\d+)']:
        m = re.search(p, q)
        if m:
            return 'user_recommend', {'user_id': int(m.group(1))}
    for p in [r'tương tự.*?(\d+)', r'giống.*?sản phẩm.*?(\d+)', r'sản phẩm.*?(\d+).*?tương tự']:
        m = re.search(p, q)
        if m:
            return 'similar', {'product_id': int(m.group(1))}
    for p in [r'phổ biến', r'trending', r'hot', r'bán chạy', r'nhiều người']:
        if re.search(p, q):
            return 'popular', {}
    return 'general', {}


def retrieve_context(intent, params, product_map) -> str:
    lines = []
    if intent == 'user_recommend':
        data = neo4j_client.get_user_top_products(params.get('user_id', 1))
        lines.append(f"Sản phẩm User {params.get('user_id')} hay tương tác:")
        for d in data:
            p_name = product_map.get(d['product_id'], f"#{d['product_id']}")
            lines.append(f"  - {p_name} (score: {d['score']})")
    elif intent == 'similar':
        pid = params.get('product_id', 1)
        data = neo4j_client.get_similar_products(pid)
        lines.append(f"Sản phẩm tương tự #{pid}:")
        for d in data:
            p_name = product_map.get(d['product_id'], f"#{d['product_id']}")
            lines.append(f"  - {p_name} ({d['common_users']} users chung)")
    else:
        data = neo4j_client.get_popular_products()
        lines.append("Top sản phẩm phổ biến:")
        for i, d in enumerate(data, 1):
            p_name = product_map.get(d['product_id'], f"#{d['product_id']}")
            lines.append(f"  {i}. {p_name} - {d['score']} điểm")
    return '\n'.join(lines)


class ChatView(APIView):
    """
    POST /api/chat/
    Body: {"message": "...", "user_id": 1}
    """
    def post(self, request):
        message = request.data.get('message', '').strip()
        user_id = request.data.get('user_id')

        if not message:
            return Response({'error': 'Thiếu message'}, status=400)

        # 1. Parse intent
        intent, params = parse_intent(message)
        if intent == 'user_recommend' and not params.get('user_id'):
            params['user_id'] = user_id or 1

        # 2. Lấy context từ Neo4j
        product_map = build_product_map()
        context = retrieve_context(intent, params, product_map)

        # 3. Gọi Gemini
        prompt = f"""Bạn là trợ lý AI tư vấn mua sắm công nghệ.
Dữ liệu từ Knowledge Graph:
{context}

Câu hỏi: {message}
Trả lời ngắn gọn (3-5 câu), thân thiện, bằng tiếng Việt."""

        gemini = get_gemini()
        if gemini:
            try:
                answer = gemini.generate_content(prompt).text
            except Exception as e:
                print(f"[Gemini Error]: {e}")
                answer = f"⚠️ Không thể gọi AI Gemini. Vui lòng kiểm tra lại API Key trong file .env (thường bắt đầu bằng AIzaSy...)\nChi tiết lỗi: {e}\n\nContext thô:\n{context}"
        else:
            answer = f"Dựa trên Knowledge Graph:\n\n{context}"

        return Response({'question': message, 'answer': answer})
