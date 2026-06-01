"""
behavior-service/behaviors/views.py
Endpoints:
  POST /api/behaviors/           → Ghi hành vi mới
  GET  /api/behaviors/sequence/<user_id>/  → Lấy 7 product_id gần nhất (gọi bởi recommend-service)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import UserBehavior


class BehaviorView(APIView):
    """POST /api/behaviors/ - Ghi hành vi user"""
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        action = request.data.get('action', 'view')

        if not user_id or not product_id:
            return Response({'error': 'Thiếu user_id hoặc product_id'}, status=400)

        if action not in ('view', 'click', 'add_to_cart'):
            return Response({'error': 'action không hợp lệ'}, status=400)

        UserBehavior.objects.create(
            user_id=int(user_id),
            product_id=int(product_id),
            action=action,
            timestamp=timezone.now()
        )
        return Response({'status': 'ok'})


class UserSequenceView(APIView):
    """
    GET /api/behaviors/sequence/<user_id>/
    Trả về 7 product_id gần nhất của user (dùng cho recommend-service).
    Nếu user có < 7 hành vi, pad 0 ở đầu.
    """
    SEQ_LEN = 7

    def get(self, request, user_id):
        behaviors = (
            UserBehavior.objects
            .filter(user_id=user_id)
            .order_by('timestamp')
            .values_list('product_id', flat=True)
        )
        seq = list(behaviors)[-self.SEQ_LEN:]      # Lấy 7 cuối
        while len(seq) < self.SEQ_LEN:             # Pad 0 nếu thiếu
            seq.insert(0, 0)

        return Response({
            'user_id': user_id,
            'sequence': seq,
            'length': len(seq)
        })
