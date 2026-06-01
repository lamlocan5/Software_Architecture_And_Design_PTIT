import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json


def _proxy(request, service_url, path):
    """Generic HTTP proxy to forward requests to downstream services."""
    url = f"{service_url}/{path}"
    params = request.GET.dict()
    headers = {'Content-Type': 'application/json'}

    try:
        if request.method == 'GET':
            resp = requests.get(url, params=params, headers=headers, timeout=10)
        elif request.method == 'POST':
            try:
                body = json.loads(request.body)
            except Exception:
                body = {}
            resp = requests.post(url, json=body, params=params, headers=headers, timeout=10)
        elif request.method == 'PUT':
            try:
                body = json.loads(request.body)
            except Exception:
                body = {}
            resp = requests.put(url, json=body, params=params, headers=headers, timeout=10)
        elif request.method == 'DELETE':
            resp = requests.delete(url, params=params, headers=headers, timeout=10)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

        try:
            data = resp.json()
        except Exception:
            data = {'response': resp.text}

        return JsonResponse(data, status=resp.status_code, safe=False)

    except requests.RequestException as e:
        return JsonResponse({'error': f'Service unavailable: {str(e)}'}, status=503)


# ─── Customer Service Proxy ───────────────────────────────────────────────────

@csrf_exempt
def customer_proxy(request, path=''):
    return _proxy(request, settings.CUSTOMER_SERVICE_URL, f"customer/{path}")


# ─── Staff Service Proxy ──────────────────────────────────────────────────────

@csrf_exempt
def staff_proxy(request, path=''):
    return _proxy(request, settings.STAFF_SERVICE_URL, f"staff/{path}")


# ─── Laptop Service Proxy ─────────────────────────────────────────────────────

@csrf_exempt
def laptop_proxy(request, path=''):
    return _proxy(request, settings.LAPTOP_SERVICE_URL, f"laptops/{path}")


# ─── Mobile Service Proxy ─────────────────────────────────────────────────────

@csrf_exempt
def mobile_proxy(request, path=''):
    return _proxy(request, settings.MOBILE_SERVICE_URL, f"mobiles/{path}")


# ─── Order Service Proxy ──────────────────────────────────────────────────────

@csrf_exempt
def order_proxy(request, path=''):
    return _proxy(request, settings.ORDER_SERVICE_URL, f"orders/{path}")


# ─── Advisory (RAG + hành vi) ─────────────────────────────────────────────────

@csrf_exempt
def advisory_proxy(request, path=''):
    """Proxy tới FastAPI advisory-service (vd. chat, health, predict-behavior)."""
    adv = settings.ADVISORY_SERVICE_URL.rstrip('/')
    base = f"{adv}/{path}" if path else adv
    params = request.GET.dict()
    headers = {'Content-Type': 'application/json'}
    try:
        if request.method == 'GET':
            resp = requests.get(base, params=params, headers=headers, timeout=120)
        elif request.method == 'POST':
            try:
                body = json.loads(request.body)
            except Exception:
                body = {}
            resp = requests.post(base, json=body, params=params, headers=headers, timeout=120)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        try:
            data = resp.json()
        except Exception:
            data = {'response': resp.text}
        return JsonResponse(data, status=resp.status_code, safe=False)
    except requests.RequestException as e:
        return JsonResponse({'error': f'Advisory service unavailable: {str(e)}'}, status=503)


# ─── UI Views ─────────────────────────────────────────────────────────────────

def staff_ui(request):
    """Render giao diện Staff"""
    return render(request, 'staff_ui.html', {
        'staff_service_url': '/api/staff',
        'laptop_service_url': '/api/laptop',
        'mobile_service_url': '/api/mobile',
    })


def customer_ui(request):
    """Render giao diện Customer"""
    return render(request, 'customer_ui.html', {
        'customer_service_url': '/api/customer',
        'laptop_service_url': '/api/laptop',
        'mobile_service_url': '/api/mobile',
    })


def home(request):
    """Trang chủ - điều hướng đến 2 UI"""
    return render(request, 'home.html')
