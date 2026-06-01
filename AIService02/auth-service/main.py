"""
auth-service/main.py
FastAPI :8001 — Authentication & User Management
Routes: POST /login, POST /register, GET /me, GET /users (admin)
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import hashlib, jwt, os, json
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="Auth Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = os.getenv("JWT_SECRET", "shopai-secret-2026")
ALGORITHM  = "HS256"
EXP_HOURS  = 24

# ── In-memory user store (demo) ──
USERS_DB: dict = {
    "admin": {
        "username":      "admin",
        "password_hash": hashlib.sha256(b"admin123").hexdigest(),
        "display_name":  "Administrator",
        "email":         "admin@shopai.vn",
        "role":          "admin",
        "created_at":    "2026-01-01T00:00:00",
    },
    "demo": {
        "username":      "demo",
        "password_hash": hashlib.sha256(b"demo123").hexdigest(),
        "display_name":  "Demo User",
        "email":         "demo@shopai.vn",
        "role":          "user",
        "created_at":    "2026-01-01T00:00:00",
    },
}


# ── Schemas ──
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username:     str
    password:     str
    display_name: str
    email:        str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         dict


# ── Helpers ──
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def create_token(data: dict) -> str:
    payload = {**data, "exp": datetime.utcnow() + timedelta(hours=EXP_HOURS)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return decode_token(authorization.split(" ", 1)[1])

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ── Routes ──
@app.get("/health")
def health(): return {"status": "UP", "service": "auth-service"}

@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    u = USERS_DB.get(req.username)
    if not u or u["password_hash"] != hash_pw(req.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    token = create_token({"username": u["username"], "role": u["role"], "display_name": u["display_name"], "email": u["email"]})
    safe = {k: v for k, v in u.items() if k != "password_hash"}
    return TokenResponse(access_token=token, user=safe)

@app.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    if req.username in USERS_DB:
        raise HTTPException(status_code=409, detail="Username already exists")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if "@" not in req.email:
        raise HTTPException(status_code=400, detail="Invalid email")

    new_user = {
        "username":      req.username,
        "password_hash": hash_pw(req.password),
        "display_name":  req.display_name,
        "email":         req.email,
        "role":          "user",
        "created_at":    datetime.utcnow().isoformat(),
    }
    USERS_DB[req.username] = new_user
    token = create_token({"username": req.username, "role": "user", "display_name": req.display_name, "email": req.email})
    safe  = {k: v for k, v in new_user.items() if k != "password_hash"}
    return TokenResponse(access_token=token, user=safe)

@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user

@app.get("/users")
def list_users(user: dict = Depends(require_admin)):
    return [
        {k: v for k, v in u.items() if k != "password_hash"}
        for u in USERS_DB.values()
    ]
