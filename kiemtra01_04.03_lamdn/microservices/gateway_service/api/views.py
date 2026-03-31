import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

SERVICE_BASE_URLS = {
    "staff": "http://staff_service:8000",
    "customer": "http://customer_service:8000",
    "laptop": "http://laptop_service:8000",
    "moblie": "http://moblie_service:8000",
}


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
    return _proxy_request(request, "laptop", upstream_path)


@csrf_exempt
def proxy_to_moblie(request, upstream_path):
    return _proxy_request(request, "moblie", upstream_path)
