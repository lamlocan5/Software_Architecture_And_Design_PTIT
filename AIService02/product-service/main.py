"""
product-service/main.py
FastAPI :8002 — Product Catalog & CRUD (Admin only for mutations)
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json, os, jwt
from copy import deepcopy

app = FastAPI(title="Product Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = os.getenv("JWT_SECRET", "shopai-secret-2026")
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "products_catalog.json")

# Load catalog
with open(CATALOG_PATH, encoding="utf-8") as f:
    PRODUCTS: dict = json.load(f)


# ── Auth helpers (duplicated for service independence) ──
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return decode_token(authorization.split(" ", 1)[1])

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ── Schemas ──
class ProductCreate(BaseModel):
    name:        str
    category:    str
    price:       float
    stock:       int = 100
    description: str = ""
    image_emoji: str = "🛍️"

class ProductUpdate(BaseModel):
    name:        Optional[str]
    price:       Optional[float]
    stock:       Optional[int]
    description: Optional[str]


# ── Routes ──
@app.get("/health")
def health(): return {"status": "UP", "service": "product-service"}

@app.get("/products")
def get_products(category: Optional[str] = None, search: Optional[str] = None,
                 sort: str = "popular"):
    items = deepcopy(PRODUCTS)
    if category and category != "all":
        items = {k: v for k, v in items.items() if v["category"] == category}
    if search:
        s = search.lower()
        items = {k: v for k, v in items.items()
                 if s in v["name"].lower() or s in v["category"].lower() or s in k.lower()}
    result = list(items.values())
    for item in result:
        item["product_id"] = [k for k, v in PRODUCTS.items() if v["name"] == item["name"]][0]
    if sort == "price_asc":
        result.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        result.sort(key=lambda x: x["price"], reverse=True)
    return {"products": result, "total": len(result)}

@app.get("/products/{product_id}")
def get_product(product_id: str):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    return {**PRODUCTS[product_id], "product_id": product_id}

@app.post("/products", status_code=201)
def create_product(product: ProductCreate, user: dict = Depends(require_admin)):
    new_id = f"P{len(PRODUCTS)+1:03d}"
    PRODUCTS[new_id] = product.model_dump()
    return {"product_id": new_id, **PRODUCTS[new_id]}

@app.put("/products/{product_id}")
def update_product(product_id: str, update: ProductUpdate, user: dict = Depends(require_admin)):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, val in update.model_dump(exclude_none=True).items():
        PRODUCTS[product_id][field] = val
    return {**PRODUCTS[product_id], "product_id": product_id}

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str, user: dict = Depends(require_admin)):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    del PRODUCTS[product_id]

@app.get("/categories")
def get_categories():
    cats = list(set(v["category"] for v in PRODUCTS.values()))
    return {"categories": sorted(cats)}
