import requests
import threading
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

SERVICE_BASE_URLS = {
    "staff": "http://staff_service:8000",
    "customer": "http://customer_service:8000",
    "laptop": "http://laptop_service:8000",
    "moblie": "http://moblie_service:8000",
    "advisor": "http://advisor_service:8000",
}

ADVISOR_TRACK_URL = "http://advisor_service:8000/track/"


def gateway_health(_request):
    return JsonResponse({"gateway": "ok"})


def _build_forward_headers(request):
    headers = {}
    for header_name in ["Authorization", "Content-Type", "Accept"]:
        header_value = request.headers.get(header_name)
        if header_value:
            headers[header_name] = header_value
    headers["Host"] = "localhost"
    return headers


def _send_behaviour_event(event_data: dict):
    """Gửi behaviour event đến advisor_service (non-blocking)"""
    def _fire():
        try:
            requests.post(ADVISOR_TRACK_URL, json=event_data, timeout=3)
        except Exception:
            pass  # Silent fail — tracking is best-effort
    threading.Thread(target=_fire, daemon=True).start()


def _extract_customer_id(request) -> int | None:
    """Lấy customer_id từ Authorization JWT header"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        import base64, json as _json
        token = auth.split(" ")[1]
        payload_b64 = token.split(".")[1]
        # Pad base64
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = _json.loads(base64.b64decode(payload_b64))
        return payload.get("user_id") or payload.get("id")
    except Exception:
        return None


def _proxy_request(request, service_name, upstream_path):
    base_url = SERVICE_BASE_URLS[service_name]
    upstream_url = f"{base_url}/{upstream_path}"
    if request.META.get("QUERY_STRING"):
        upstream_url = f"{upstream_url}?{request.META['QUERY_STRING']}"

    try:
        upstream_response = requests.request(
            method=request.method,
            url=upstream_url,
            headers=_build_forward_headers(request),
            data=request.body if request.body else None,
            timeout=20,
        )
    except requests.RequestException:
        return JsonResponse({"error": f"{service_name}_service unavailable"}, status=503)

    response = HttpResponse(
        content=upstream_response.content,
        status=upstream_response.status_code,
        content_type=upstream_response.headers.get("Content-Type", "application/json"),
    )
    return response


@csrf_exempt
def proxy_to_staff(request, upstream_path):
    return _proxy_request(request, "staff", upstream_path)


@csrf_exempt
def proxy_to_customer(request, upstream_path):
    return _proxy_request(request, "customer", upstream_path)


@csrf_exempt
def proxy_to_laptop(request, upstream_path):
    response = _proxy_request(request, "laptop", upstream_path)

    # Auto-track: view product details (GET /products/<id>/)
    if request.method == "GET" and upstream_path.startswith("products/") and upstream_path.count("/") >= 2:
        try:
            import json as _json
            data = _json.loads(response.content)
            customer_id = _extract_customer_id(request)
            if customer_id and data.get("id"):
                _send_behaviour_event({
                    "customer_id":  customer_id,
                    "product_id":   data["id"],
                    "product_type": "laptop",
                    "product_name": data.get("name", ""),
                    "action":       "view_product",
                    "price":        data.get("price") or data.get("price_vnd"),
                })
        except Exception:
            pass

    # Auto-track: add to cart (POST to cart endpoint conveyed through laptop service)
    if request.method == "POST" and "cart" in upstream_path:
        try:
            import json as _json
            body = _json.loads(request.body)
            customer_id = _extract_customer_id(request)
            if customer_id and body.get("product_id"):
                _send_behaviour_event({
                    "customer_id":  customer_id,
                    "product_id":   body["product_id"],
                    "product_type": "laptop",
                    "product_name": body.get("product_name", ""),
                    "action":       "add_to_cart",
                    "price":        body.get("price"),
                })
        except Exception:
            pass

    return response


@csrf_exempt
def proxy_to_moblie(request, upstream_path):
    response = _proxy_request(request, "moblie", upstream_path)

    # Auto-track: view product details
    if request.method == "GET" and upstream_path.startswith("products/") and upstream_path.count("/") >= 2:
        try:
            import json as _json
            data = _json.loads(response.content)
            customer_id = _extract_customer_id(request)
            if customer_id and data.get("id"):
                _send_behaviour_event({
                    "customer_id":  customer_id,
                    "product_id":   data["id"],
                    "product_type": "mobile",
                    "product_name": data.get("name", ""),
                    "action":       "view_product",
                    "price":        data.get("price") or data.get("price_vnd"),
                })
        except Exception:
            pass

    return response


@csrf_exempt
def proxy_to_advisor(request, upstream_path):
    return _proxy_request(request, "advisor", upstream_path)
