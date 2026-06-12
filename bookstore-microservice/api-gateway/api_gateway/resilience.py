import time
import requests
import threading
from urllib.parse import urlparse
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, name, failure_threshold=5, recovery_timeout=15):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_state_change = time.time()
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            current_time = time.time()
            if self.state == "OPEN":
                if current_time - self.last_state_change >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    self.last_state_change = current_time
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker for '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            with self.lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    self.last_state_change = time.time()
                elif self.state == "CLOSED":
                    self.failure_count = 0
            return result
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                if self.state in ("CLOSED", "HALF_OPEN"):
                    if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
                        self.state = "OPEN"
                        self.last_state_change = time.time()
            raise e

# Registry of circuit breakers by service hostname
_breakers = {}
_lock = threading.Lock()

def get_breaker(url) -> CircuitBreaker:
    try:
        hostname = urlparse(url).netloc or "default"
    except Exception:
        hostname = "default"
    
    with _lock:
        if hostname not in _breakers:
            _breakers[hostname] = CircuitBreaker(name=hostname, failure_threshold=5, recovery_timeout=15)
        return _breakers[hostname]

# Pre-configured Session with automatic retries for HTTP GET
resilience_session = requests.Session()
retries = Retry(
    total=2,
    backoff_factor=0.2,
    status_forcelist=[502, 503, 504],
    raise_on_status=True
)
resilience_session.mount('http://', HTTPAdapter(max_retries=retries))
