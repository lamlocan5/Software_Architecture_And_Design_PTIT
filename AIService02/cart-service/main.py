"""
cart-service/main.py
FastAPI :8003 — Shopping Cart & Checkout
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import jwt, os
from datetime import datetime

app = FastAPI(title="Cart Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = os.getenv("JWT_SECRET", "shopai-secret-2026")

# In-memory carts: {username: {product_id: {name, qty, price, category}}}
CARTS:  Dict[str, Dict] = {}
ORDERS: Dict[str, list] = {}   # order history


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return decode_token(authorization.split(" ", 1)[1])


class AddItemRequest(BaseModel):
    product_id: str
    name:       str
    price:      float
    category:   str
    qty:        int = 1

class CheckoutRequest(BaseModel):
    note: str = ""


@app.get("/health")
def health(): return {"status": "UP", "service": "cart-service"}

@app.get("/cart")
def get_cart(user: dict = Depends(get_current_user)):
    cart = CARTS.get(user["username"], {})
    items = list(cart.values())
    total = sum(i["qty"] * i["price"] for i in items)
    discount = total * 0.05 if total > 500 else 0
    return {
        "items":    items,
        "subtotal": round(total, 2),
        "discount": round(discount, 2),
        "total":    round(total - discount, 2),
        "count":    sum(i["qty"] for i in items),
    }

@app.post("/cart/add")
def add_to_cart(req: AddItemRequest, user: dict = Depends(get_current_user)):
    username = user["username"]
    if username not in CARTS:
        CARTS[username] = {}
    cart = CARTS[username]
    if req.product_id in cart:
        cart[req.product_id]["qty"] += req.qty
    else:
        cart[req.product_id] = req.model_dump()
    return {"message": "Added to cart", "cart_count": sum(i["qty"] for i in cart.values())}

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    cart = CARTS.get(user["username"], {})
    cart.pop(product_id, None)
    return {"message": "Removed"}

@app.patch("/cart/{product_id}")
def update_qty(product_id: str, qty: int, user: dict = Depends(get_current_user)):
    cart = CARTS.get(user["username"], {})
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")
    if qty <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id]["qty"] = qty
    return {"message": "Updated"}

@app.delete("/cart")
def clear_cart(user: dict = Depends(get_current_user)):
    CARTS[user["username"]] = {}
    return {"message": "Cart cleared"}

@app.post("/cart/checkout")
def checkout(req: CheckoutRequest, user: dict = Depends(get_current_user)):
    username = user["username"]
    cart = CARTS.get(username, {})
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    items  = list(cart.values())
    total  = sum(i["qty"] * i["price"] for i in items)
    disc   = total * 0.05 if total > 500 else 0
    order  = {
        "order_id":   f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "username":   username,
        "items":      items,
        "subtotal":   round(total, 2),
        "discount":   round(disc, 2),
        "total":      round(total - disc, 2),
        "status":     "confirmed",
        "created_at": datetime.utcnow().isoformat(),
        "note":       req.note,
    }
    ORDERS.setdefault(username, []).append(order)
    CARTS[username] = {}
    return order

@app.get("/orders")
def get_orders(user: dict = Depends(get_current_user)):
    return {"orders": ORDERS.get(user["username"], [])}
