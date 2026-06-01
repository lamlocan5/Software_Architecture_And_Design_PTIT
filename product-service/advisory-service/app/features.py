"""
Tổng hợp vector đặc trưng hành vi khách từ Customer Service (giỏ) và Order Service.
Thứ tự cột khớp behavior_train_150_rows.csv (trừ nhãn).
"""
from __future__ import annotations

import datetime as dt
from typing import Any

import requests

from app.config import settings

FEATURE_ORDER = [
    "qty_laptop_cart",
    "qty_mobile_cart",
    "spent_laptop_cart",
    "spent_mobile_cart",
    "orders_with_laptop",
    "orders_with_mobile",
    "spent_laptop_orders",
    "spent_mobile_orders",
    "has_both_in_cart",
    "has_mixed_order",
    "days_since_customer_created",
    "recency_laptop",
    "recency_mobile",
]


def _scale_amount(x: float) -> int:
    return int(round(float(x) * settings.behavior_amount_scale))


def _parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        v = value.replace("Z", "+00:00")
        return dt.datetime.fromisoformat(v)
    except ValueError:
        return None


def fetch_cart(token: str) -> dict[str, Any] | None:
    url = f"{settings.customer_service_url}/customer/cart/"
    try:
        r = requests.get(url, params={"token": token}, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def fetch_orders(token: str) -> list[dict[str, Any]]:
    url = f"{settings.order_service_url}/orders/"
    try:
        r = requests.get(url, params={"token": token}, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("orders") or []
    except requests.RequestException:
        return []


def fetch_customer_meta(token: str) -> dict[str, Any] | None:
    url = f"{settings.customer_service_url}/customer/verify/"
    try:
        r = requests.get(url, params={"token": token}, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def build_feature_row(token: str) -> dict[str, int] | None:
    meta = fetch_customer_meta(token)
    if not meta or meta.get("customer_id") is None:
        return None

    cart = fetch_cart(token) or {}
    items = cart.get("items") or []

    today = dt.date.today()
    created_raw = _parse_dt(meta.get("created_at"))
    created_date = created_raw.date() if created_raw else None
    days_since_customer = (today - created_date).days if created_date else 0

    qty_laptop = sum(int(i.get("quantity", 0)) for i in items if i.get("product_type") == "laptop")
    qty_mobile = sum(int(i.get("quantity", 0)) for i in items if i.get("product_type") == "mobile")
    spent_laptop_cart = sum(
        _scale_amount(float(i.get("subtotal", 0))) for i in items if i.get("product_type") == "laptop"
    )
    spent_mobile_cart = sum(
        _scale_amount(float(i.get("subtotal", 0))) for i in items if i.get("product_type") == "mobile"
    )
    has_laptop_ci = any(i.get("product_type") == "laptop" for i in items)
    has_mobile_ci = any(i.get("product_type") == "mobile" for i in items)
    has_both_in_cart = 1 if has_laptop_ci and has_mobile_ci else 0

    cart_upd = _parse_dt(cart.get("updated_at"))

    orders = fetch_orders(token)
    orders_with_laptop = 0
    orders_with_mobile = 0
    spent_laptop_orders = 0
    spent_mobile_orders = 0
    has_mixed_order = 0

    last_laptop: dt.datetime | None = None
    last_mobile: dt.datetime | None = None

    if cart_upd:
        if has_laptop_ci:
            last_laptop = cart_upd
        if has_mobile_ci:
            last_mobile = cart_upd

    for order in orders:
        if order.get("status") == "cancelled":
            continue
        oitems = order.get("items") or []
        types_in_order = {it.get("product_type") for it in oitems}
        if "laptop" in types_in_order and "mobile" in types_in_order:
            has_mixed_order = 1
        oc = _parse_dt(order.get("created_at"))
        has_l = "laptop" in types_in_order
        has_m = "mobile" in types_in_order
        if has_l:
            orders_with_laptop += 1
        if has_m:
            orders_with_mobile += 1
        for it in oitems:
            pt = it.get("product_type")
            sub = float(it.get("price", 0)) * int(it.get("quantity", 0))
            amt = _scale_amount(sub)
            if pt == "laptop":
                spent_laptop_orders += amt
                if oc and (last_laptop is None or oc > last_laptop):
                    last_laptop = oc
            elif pt == "mobile":
                spent_mobile_orders += amt
                if oc and (last_mobile is None or oc > last_mobile):
                    last_mobile = oc

    def days_since(ts: dt.datetime | None) -> int:
        if not ts:
            return 999
        d = ts.date() if isinstance(ts, dt.datetime) else ts
        return max(0, (today - d).days)

    recency_laptop = days_since(last_laptop)
    recency_mobile = days_since(last_mobile)

    return {
        "qty_laptop_cart": int(qty_laptop),
        "qty_mobile_cart": int(qty_mobile),
        "spent_laptop_cart": int(spent_laptop_cart),
        "spent_mobile_cart": int(spent_mobile_cart),
        "orders_with_laptop": int(orders_with_laptop),
        "orders_with_mobile": int(orders_with_mobile),
        "spent_laptop_orders": int(spent_laptop_orders),
        "spent_mobile_orders": int(spent_mobile_orders),
        "has_both_in_cart": int(has_both_in_cart),
        "has_mixed_order": int(has_mixed_order),
        "days_since_customer_created": int(days_since_customer),
        "recency_laptop": int(recency_laptop),
        "recency_mobile": int(recency_mobile),
    }


def row_to_vector(row: dict[str, int]) -> list[float]:
    return [float(row[k]) for k in FEATURE_ORDER]
