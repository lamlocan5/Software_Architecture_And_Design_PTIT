from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import os

BOOK_SERVICE_URL          = "http://product-service:8000"
CLOTHE_SERVICE_URL        = "http://product-service:8000"
ELECTRONIC_SERVICE_URL    = "http://product-service:8000"
CATALOGUE_SERVICE_URL     = "http://catalogue-service:8000"
CART_SERVICE_URL          = "http://cart-service:8000"
CUSTOMER_SERVICE_URL      = "http://user-service:8000"
STAFF_SERVICE_URL         = "http://user-service:8000"
MANAGER_SERVICE_URL       = "http://user-service:8000"
ORDER_SERVICE_URL         = "http://order-service:8000"
REVIEW_SERVICE_URL        = "http://review-service:8000"
SHIP_SERVICE_URL          = "http://shipping-service:8000"
PAY_SERVICE_URL           = "http://payment-service:8000"
RECOMMENDER_SERVICE_URL   = "http://ai-service:8000"
NOTIFICATION_SERVICE_URL  = "http://notification-service:8000"

from .resilience import get_breaker, resilience_session

def _get(url, default=None):
    breaker = get_breaker(url)
    try:
        r = breaker.call(resilience_session.get, url, timeout=3)
        return r.json()
    except Exception:
        return default if default is not None else []

def _post(url, data):
    breaker = get_breaker(url)
    return breaker.call(resilience_session.post, url, json=data, timeout=3)

def _patch(url, data):
    breaker = get_breaker(url)
    return breaker.call(resilience_session.patch, url, json=data, timeout=3)

def _get_customer_id(user):
    try:
        return user.profile.customer_id
    except Exception:
        return None

def _is_admin(user) -> bool:
    return bool(getattr(user, "is_superuser", False))

def _is_manager(user) -> bool:
    return _is_admin(user) or (hasattr(user, 'role') and user.role == 'manager')

def _is_staff_user(user) -> bool:
    return _is_admin(user) or (hasattr(user, 'role') and user.role in ['staff', 'manager'])

def _can_manage_books(user) -> bool:
    return _is_admin(user) or _is_staff_user(user) or _is_manager(user)

# JSON Views for API Gateway / BFF
def home(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if _can_manage_books(request.user) or _is_admin(request.user):
        books      = _get(f"{BOOK_SERVICE_URL}/books/", [])
        customers  = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
        orders     = _get(f"{ORDER_SERVICE_URL}/orders/", [])
        reviews    = _get(f"{REVIEW_SERVICE_URL}/reviews/", [])
        publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])

        reco_books = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/", [])
        recommended = []
        if isinstance(reco_books, list) and reco_books:
            try:
                rr = _post(f"{RECOMMENDER_SERVICE_URL}/recommendations/", {"books": reco_books[:50], "limit": 6, "context": "home"})
                if getattr(rr, "status_code", 200) < 400:
                    ids = rr.json().get("recommended_ids", [])
                    id_map = {b.get("id"): b for b in reco_books if isinstance(b, dict)}
                    recommended = [id_map.get(i) for i in ids if i in id_map]
                    recommended = [b for b in recommended if b]
            except Exception:
                recommended = []

        return JsonResponse({
            "is_admin": True,
            "book_count": len(books) if isinstance(books, list) else 0,
            "customer_count": len(customers) if isinstance(customers, list) else 0,
            "order_count": len(orders) if isinstance(orders, list) else 0,
            "review_count": len(reviews) if isinstance(reviews, list) else 0,
            "publisher_count": len(publishers) if isinstance(publishers, list) else 0,
            "service_count": 11,
            "recommended_books": recommended,
        })

    customer_id = _get_customer_id(request.user)
    books       = _get(f"{BOOK_SERVICE_URL}/books/", [])
    clothes     = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    cart_items  = []
    cart_total  = 0
    orders      = []

    if customer_id:
        items    = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
        product_map = {}
        for b in (books if isinstance(books, list) else []):
            if isinstance(b, dict) and "id" in b:
                b["title"] = b.get("title") or b.get("name")
                product_map[b["id"]] = b
        for c in (clothes if isinstance(clothes, list) else []):
            if isinstance(c, dict) and "id" in c:
                c["title"] = c.get("name")
                product_map[c["id"]] = c
        for e in (electronics if isinstance(electronics, list) else []):
            if isinstance(e, dict) and "id" in e:
                e["title"] = e.get("name")
                product_map[e["id"]] = e

        for item in (items if isinstance(items, list) else []):
            prod_id = item.get("book_id") or item.get("clothing_id") or item.get("electronic_id")
            product = product_map.get(prod_id, {}) if prod_id else {}
            if product:
                product["title"] = product.get("title") or product.get("name")
                product["author"] = product.get("author") or "—"
            
            item["book"]     = product
            item["subtotal"] = float(product.get("price", 0)) * item["quantity"] if product else 0
            cart_total      += item["subtotal"]
        cart_items = items
        orders = _get(f"{ORDER_SERVICE_URL}/orders/customer/{customer_id}/", [])

    return JsonResponse({
        "is_admin": False,
        "customer_id": customer_id,
        "cart_items": cart_items,
        "cart_total": cart_total,
        "orders": orders,
        "book_count": len(books) if isinstance(books, list) else 0,
    })

def catalogue_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    books = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/", [])
    publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])

    # Recommendations best-effort
    recommended = []
    try:
        rr = _post(f"{RECOMMENDER_SERVICE_URL}/recommendations/", {"books": books[:50], "limit": 6, "context": "catalogue"})
        if getattr(rr, "status_code", 200) < 400:
            ids = rr.json().get("recommended_ids", [])
            id_map = {b.get("id"): b for b in books if isinstance(b, dict)}
            recommended = [id_map.get(i) for i in ids if i in id_map]
            recommended = [b for b in recommended if b]
    except Exception:
        recommended = []

    return JsonResponse({
        "books": books,
        "publishers": publishers,
        "recommended_books": recommended,
    })

def cart_view(request, customer_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    items      = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
    books      = _get(f"{BOOK_SERVICE_URL}/books/", [])
    clothes    = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    
    book_map      = {b["id"]: b for b in (books if isinstance(books, list) else [])}
    clothe_map    = {c["id"]: c for c in (clothes if isinstance(clothes, list) else [])}
    electronic_map = {e["id"]: e for e in (electronics if isinstance(electronics, list) else [])}
    
    total = 0
    for item in (items if isinstance(items, list) else []):
        product = None
        if item.get("book_id") and item.get("book_id") != 0:
            product = book_map.get(item["book_id"])
            item["product_type"] = "book"
        elif item.get("clothing_id"):
            product = clothe_map.get(item["clothing_id"])
            item["product_type"] = "clothing"
        elif item.get("electronic_id"):
            product = electronic_map.get(item["electronic_id"])
            item["product_type"] = "electronic"

        if product:
            product["title"] = product.get("title") or product.get("name")
            product["author"] = product.get("author") or "—"

        item["product"] = product or {}
        price = float(product.get("price", 0)) if product else 0.0
        item["subtotal"] = price * item.get("quantity", 0)
        total += item["subtotal"]

    return JsonResponse({
        "items": items,
        "total": total,
        "customer_id": customer_id
    })

@csrf_exempt
def order_checkout(request, customer_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        body = json.loads(request.body)
    except Exception:
        body = request.POST

    payment_method = body.get("payment_method", "cod")
    shipment_carrier = body.get("shipment_carrier", "")
    shipment_address = body.get("shipment_address", "")
    shipment_phone = body.get("shipment_phone", "")

    items       = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
    books       = _get(f"{BOOK_SERVICE_URL}/books/", [])
    clothes     = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])

    product_map = {}
    for b in (books if isinstance(books, list) else []):
        if isinstance(b, dict) and "id" in b:
            product_map[b["id"]] = b
    for c in (clothes if isinstance(clothes, list) else []):
        if isinstance(c, dict) and "id" in c:
            product_map[c["id"]] = c
    for e in (electronics if isinstance(electronics, list) else []):
        if isinstance(e, dict) and "id" in e:
            product_map[e["id"]] = e

    order_items = []
    total       = 0
    for item in (items if isinstance(items, list) else []):
        prod_id = item.get("book_id") or item.get("clothing_id") or item.get("electronic_id")
        if not prod_id:
            continue
        product = product_map.get(prod_id)
        if not product:
            continue
        price    = float(product["price"])
        total   += price * item["quantity"]
        order_items.append({
            "book_id":        prod_id,
            "quantity":       item["quantity"],
            "price_at_order": price,
        })

    if not order_items:
        return JsonResponse({"error": "Cart is empty"}, status=400)

    try:
        r = _post(f"{ORDER_SERVICE_URL}/orders/create/", {
            "customer_id":  customer_id,
            "total_amount": round(total, 2),
            "items":        order_items,
        })
        if r.status_code == 201:
            order_id = r.json().get("id")

            # Clear cart
            try:
                requests.delete(f"{CART_SERVICE_URL}/carts/{customer_id}/", timeout=3)
            except Exception:
                pass

            # Create payment
            try:
                _post(f"{PAY_SERVICE_URL}/payments/create/", {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "amount": round(total, 2),
                    "method": payment_method,
                })
            except Exception:
                pass

            # Create shipment
            try:
                customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
                cust_map = {c["id"]: c for c in (customers if isinstance(customers, list) else [])}
                cust = cust_map.get(int(customer_id), {})
                _post(f"{SHIP_SERVICE_URL}/shipments/create/", {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "receiver_name": cust.get("name", "") or "",
                    "address": shipment_address,
                    "phone": shipment_phone,
                    "carrier": shipment_carrier,
                })
            except Exception:
                pass

            return JsonResponse({"status": "success", "order_id": order_id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Checkout failed"}, status=400)

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    order = _get(f"{ORDER_SERVICE_URL}/orders/{order_id}/", {})
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)

    books       = _get(f"{BOOK_SERVICE_URL}/books/", [])
    clothes     = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    product_map = {}
    for b in (books if isinstance(books, list) else []):
        if isinstance(b, dict) and "id" in b:
            b["title"] = b.get("title") or b.get("name")
            product_map[b["id"]] = b
    for c in (clothes if isinstance(clothes, list) else []):
        if isinstance(c, dict) and "id" in c:
            c["title"] = c.get("name")
            product_map[c["id"]] = c
    for e in (electronics if isinstance(electronics, list) else []):
        if isinstance(e, dict) and "id" in e:
            e["title"] = e.get("name")
            product_map[e["id"]] = e

    for item in order.get("items", []):
        item["book"] = product_map.get(item["book_id"], {})

    customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
    cust_map  = {c["id"]: c for c in (customers if isinstance(customers, list) else [])}
    order["customer"] = cust_map.get(order.get("customer_id"), {})

    payments = _get(f"{PAY_SERVICE_URL}/payments/order/{order_id}/", [])
    shipments = _get(f"{SHIP_SERVICE_URL}/shipments/order/{order_id}/", [])

    return JsonResponse({
        "order": order,
        "payments": payments,
        "shipments": shipments
    })

def notifications_api(request, customer_id=None):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    is_admin = _is_admin(request.user) or _is_staff_user(request.user)
    if is_admin and not customer_id:
        url = f"{NOTIFICATION_SERVICE_URL}/notifications/"
    else:
        cid = customer_id or _get_customer_id(request.user)
        url = f"{NOTIFICATION_SERVICE_URL}/notifications/customer/{cid}/"

    try:
        r = requests.get(url, timeout=3)
        return JsonResponse(r.json(), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
