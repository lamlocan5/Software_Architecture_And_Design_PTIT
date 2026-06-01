"""
frontend/services/api_client.py
HTTP client that calls all backend microservices.
Falls back to direct Python imports when running locally (LOCAL_MODE=True).
"""
import os, requests
from typing import Optional

# ── Service URLs (from env or defaults for local dev) ──
AUTH_URL    = os.getenv("AUTH_SERVICE_URL",    "http://localhost:8001")
PRODUCT_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
CART_URL    = os.getenv("CART_SERVICE_URL",    "http://localhost:8003")
AI_URL      = os.getenv("AI_SERVICE_URL",      "http://localhost:8004")

TIMEOUT = 10


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _check_service(url: str) -> bool:
    try:
        r = requests.get(f"{url}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ═════════════════════════════════
# SERVICE AVAILABILITY
# ═════════════════════════════════
def services_available() -> dict:
    return {
        "auth":    _check_service(AUTH_URL),
        "product": _check_service(PRODUCT_URL),
        "cart":    _check_service(CART_URL),
        "ai":      _check_service(AI_URL),
    }


# ═════════════════════════════════
# AUTH SERVICE
# ═════════════════════════════════
def login(username: str, password: str) -> dict:
    """Returns {access_token, user} or raises exception"""
    r = requests.post(f"{AUTH_URL}/login",
                      json={"username": username, "password": password},
                      timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Login failed"))
    return r.json()


def register(username: str, password: str, display_name: str, email: str) -> dict:
    r = requests.post(f"{AUTH_URL}/register",
                      json={"username": username, "password": password,
                            "display_name": display_name, "email": email},
                      timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Register failed"))
    return r.json()


def list_users(token: str) -> list:
    r = requests.get(f"{AUTH_URL}/users", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ═════════════════════════════════
# PRODUCT SERVICE
# ═════════════════════════════════
def get_products(token: str, category: str = None, search: str = None, sort: str = "popular") -> dict:
    params = {"sort": sort}
    if category and category != "Tat ca":
        params["category"] = category
    if search:
        params["search"] = search
    r = requests.get(f"{PRODUCT_URL}/products", headers=_headers(token),
                     params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_categories(token: str) -> list:
    r = requests.get(f"{PRODUCT_URL}/categories", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("categories", [])


def create_product(token: str, data: dict) -> dict:
    r = requests.post(f"{PRODUCT_URL}/products", headers=_headers(token),
                      json=data, timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Create product failed"))
    return r.json()


def update_product(token: str, product_id: str, data: dict) -> dict:
    r = requests.put(f"{PRODUCT_URL}/products/{product_id}", headers=_headers(token),
                     json=data, timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Update failed"))
    return r.json()


def delete_product(token: str, product_id: str):
    r = requests.delete(f"{PRODUCT_URL}/products/{product_id}",
                        headers=_headers(token), timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Delete failed"))


# ═════════════════════════════════
# CART SERVICE
# ═════════════════════════════════
def get_cart(token: str) -> dict:
    r = requests.get(f"{CART_URL}/cart", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def add_to_cart(token: str, product_id: str, name: str, price: float, category: str, qty: int = 1) -> dict:
    r = requests.post(f"{CART_URL}/cart/add", headers=_headers(token),
                      json={"product_id": product_id, "name": name,
                            "price": price, "category": category, "qty": qty},
                      timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def remove_from_cart(token: str, product_id: str):
    r = requests.delete(f"{CART_URL}/cart/{product_id}",
                        headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()


def update_cart_qty(token: str, product_id: str, qty: int):
    r = requests.patch(f"{CART_URL}/cart/{product_id}",
                       headers=_headers(token), params={"qty": qty}, timeout=TIMEOUT)
    r.raise_for_status()


def checkout(token: str, note: str = "") -> dict:
    r = requests.post(f"{CART_URL}/cart/checkout", headers=_headers(token),
                      json={"note": note}, timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Checkout failed"))
    return r.json()


def get_orders(token: str) -> list:
    r = requests.get(f"{CART_URL}/orders", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("orders", [])


# ═════════════════════════════════
# AI SERVICE
# ═════════════════════════════════
def get_recommendations(token: str, user_id: str, top_n: int = 5) -> list:
    r = requests.get(f"{AI_URL}/recommend/{user_id}",
                     headers=_headers(token), params={"top_n": top_n}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("recommendations", [])


def get_popular(token: str, top_n: int = 10) -> list:
    r = requests.get(f"{AI_URL}/popular", headers=_headers(token),
                     params={"top_n": top_n}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("products", [])


def chat_with_ai(token: str, question: str) -> str:
    r = requests.post(f"{AI_URL}/chat", headers=_headers(token),
                      json={"question": question}, timeout=30)
    r.raise_for_status()
    return r.json().get("answer", "No answer")


def ai_stats(token: str) -> dict:
    r = requests.get(f"{AI_URL}/stats", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def neo4j_status(token: str) -> dict:
    r = requests.get(f"{AI_URL}/neo4j/status", headers=_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def run_cypher(token: str, query: str) -> dict:
    r = requests.post(f"{AI_URL}/admin/cypher", headers=_headers(token),
                      json={"query": query}, timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Cypher query failed"))
    return r.json()


def get_graph_data(token: str, limit: int = 80) -> dict:
    r = requests.get(f"{AI_URL}/admin/graph-data", headers=_headers(token),
                     params={"limit": limit}, timeout=TIMEOUT)
    if not r.ok:
        raise ValueError(r.json().get("detail", "Graph data unavailable"))
    return r.json()
