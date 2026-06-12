import time
import threading
from django.http import HttpResponse

_lock = threading.Lock()
# Metrics counters
_request_count = {}
_request_latency = {}
_request_latency_count = {}

class PrometheusMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/metrics' or request.path == '/metrics/':
            return self.get_response(request)

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        method = request.method
        path = request.path
        status = str(response.status_code)

        # Standardize path to avoid high-cardinality values (like ID paths)
        # Replacing digits with :id
        path_parts = [part if not part.isdigit() else ':id' for part in path.split('/')]
        clean_path = '/'.join(path_parts)

        key = (method, clean_path, status)
        latency_key = (method, clean_path)

        with _lock:
            _request_count[key] = _request_count.get(key, 0) + 1
            _request_latency[latency_key] = _request_latency.get(latency_key, 0.0) + duration
            _request_latency_count[latency_key] = _request_latency_count.get(latency_key, 0) + 1

        return response

def metrics_view(request):
    lines = []
    lines.append("# HELP django_http_requests_total Total HTTP Requests")
    lines.append("# TYPE django_http_requests_total counter")
    
    with _lock:
        for (method, path, status), count in _request_count.items():
            lines.append(f'django_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        lines.append("# HELP django_http_request_duration_seconds_sum Total request latency sum")
        lines.append("# TYPE django_http_request_duration_seconds_sum counter")
        for (method, path), latency_sum in _request_latency.items():
            lines.append(f'django_http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {latency_sum:.6f}')

        lines.append("# HELP django_http_request_duration_seconds_count Total request latency count")
        lines.append("# TYPE django_http_request_duration_seconds_count counter")
        for (method, path), count in _request_latency_count.items():
            lines.append(f'django_http_request_duration_seconds_count{{method="{method}",path="{path}"}} {count}')

    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')
