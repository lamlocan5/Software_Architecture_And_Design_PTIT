"""
recommend-service/recommend/views.py
POST /api/recommend/ → predict từ model + lấy info từ product-service
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from .ml_model import predict_next_products, get_products_by_ids


class RecommendView(APIView):
    """
    POST /api/recommend/
    Body: { "user_id": 1, "top_n": 5 }

    Flow (microservice):
      1. predict_next_products() → gọi behavior-service:8003
      2. Nhận model predictions (list product_id)
      3. get_products_by_ids() → gọi product-service:8001
      4. Trả về kết quả đầy đủ
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        top_n = int(request.data.get('top_n', 5))

        if not user_id:
            return Response({'error': 'Thiếu user_id'}, status=400)

        # Bước 1: Predict product_ids
        product_ids = predict_next_products(int(user_id), top_n=top_n)

        # Bước 2: Lấy thông tin sản phẩm từ product-service
        products = get_products_by_ids(product_ids)

        return Response({
            'user_id': user_id,
            'top_n': top_n,
            'source': 'model_best.h5 (SimpleRNN) via behavior-service + product-service',
            'product_ids': product_ids,
            'recommendations': products
        })
