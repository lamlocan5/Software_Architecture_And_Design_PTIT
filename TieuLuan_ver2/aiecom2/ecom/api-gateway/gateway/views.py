"""
api-gateway/gateway/views.py

Single Entry Point cho toàn bộ hệ thống.
Frontend chỉ cần gọi gateway:8000, gateway tự route sang đúng service.

Route map:
  /api/products/*   → product-service:8001
  /api/recommend/   → recommend-service:8002
  /api/behaviors/   → behavior-service:8003
  /api/chat/        → chat-service:8004
"""
import os
import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

SERVICES = {
    'products':  os.getenv('PRODUCT_SERVICE_URL',   'http://127.0.0.1:8001'),
    'recommend': os.getenv('RECOMMEND_SERVICE_URL',  'http://127.0.0.1:8002'),
    'behaviors': os.getenv('BEHAVIOR_SERVICE_URL',   'http://127.0.0.1:8003'),
    'chat':      os.getenv('CHAT_SERVICE_URL',       'http://127.0.0.1:8004'),
}


def _proxy(request, service_key, path):
    """Forward request sang service tương ứng."""
    base = SERVICES.get(service_key)
    if not base:
        return JsonResponse({'error': f'Service {service_key} không tồn tại'}, status=404)

    url = f"{base}/api/{path}"

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            params=request.GET.dict(),
            json=request.data if request.method in ('POST', 'PUT', 'PATCH') else None,
            timeout=30,
            headers={'Content-Type': 'application/json'},
        )
        try:
            data = resp.json()
        except Exception:
            data = {'raw': resp.text}
        return JsonResponse(data, status=resp.status_code, safe=False)

    except requests.Timeout:
        return JsonResponse({'error': f'Service {service_key} timeout'}, status=504)
    except requests.ConnectionError:
        return JsonResponse(
            {'error': f'Không kết nối được {service_key} ({base}). Hãy đảm bảo service đang chạy.'},
            status=503
        )


class ProductsProxy(APIView):
    """Proxy → product-service:8001"""
    def get(self, request, path='products/'):
        return _proxy(request, 'products', path)


class ProductDetailProxy(APIView):
    """Proxy → product-service:8001/products/<pk>/"""
    def get(self, request, pk):
        return _proxy(request, 'products', f'products/{pk}/')


class ProductsByIdsProxy(APIView):
    """Proxy → product-service:8001/products/by-ids/"""
    def get(self, request):
        return _proxy(request, 'products', 'products/by-ids/')


class RecommendProxy(APIView):
    """Proxy → recommend-service:8002"""
    def post(self, request):
        return _proxy(request, 'recommend', 'recommend/')


class BehaviorProxy(APIView):
    """Proxy → behavior-service:8003"""
    def post(self, request):
        return _proxy(request, 'behaviors', 'behaviors/')


class ChatProxy(APIView):
    """Proxy → chat-service:8004"""
    def post(self, request):
        return _proxy(request, 'chat', 'chat/')


class HealthCheckView(APIView):
    """GET /api/health/ → kiểm tra trạng thái tất cả services"""
    def get(self, request):
        health = {}
        for name, base in SERVICES.items():
            try:
                requests.get(f"{base}/api/", timeout=2)
                health[name] = {'status': 'up', 'url': base}
            except Exception:
                health[name] = {'status': 'down', 'url': base}
        return Response({'gateway': 'up', 'services': health})
