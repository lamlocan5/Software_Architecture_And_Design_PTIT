"""
frontend/app.py — ShopAI Main Application
Microservices frontend: calls auth/product/cart/recommender-ai APIs
LOCAL_MODE: direct import when services are offline (dev mode)
"""
import streamlit as st
import pandas as pd
import sys, os, json, time, random
from datetime import datetime

# Add services path
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="ShopAI — Intelligent E-Commerce",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════
# GLOBAL CSS (same premium theme)
# ════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─── Base ─────────────────────────────────── */
*, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: #f8f9fa !important;
    color: #1a1a2e !important;
}
.block-container { padding: 1.5rem 2rem !important; max-width: 1400px; }
#MainMenu, footer, header { visibility: hidden; }

/* ─── Sidebar ───────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #fff5f5 100%) !important;
    border-right: 2px solid #fee2e2 !important;
    box-shadow: 4px 0 20px rgba(220,38,38,0.06) !important;
}

/* ─── Buttons ───────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 2px 8px rgba(220,38,38,0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(220,38,38,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ─── Inputs ─────────────────────────────────── */
.stTextInput input, .stPasswordInput input,
.stTextArea textarea, .stSelectbox > div > div {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #1f2937 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stPasswordInput input:focus,
.stTextArea textarea:focus {
    border-color: #dc2626 !important;
    box-shadow: 0 0 0 3px rgba(220,38,38,0.1) !important;
}

/* ─── Typography ─────────────────────────────── */
.page-title {
    font-size: 2rem; font-weight: 800; color: #1a1a2e;
    letter-spacing: -0.5px; margin-bottom: 0.2rem;
}
.page-title span.red { color: #dc2626; }
.page-subtitle { color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem; }
h1, h2, h3 { color: #1a1a2e !important; }

/* ─── Cards ──────────────────────────────────── */
.glass-card {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: all 0.25s ease;
}
.glass-card:hover {
    border-color: #fecaca;
    box-shadow: 0 8px 28px rgba(220,38,38,0.12);
    transform: translateY(-1px);
}

.product-card {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.2rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.product-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #dc2626, #f87171);
    opacity: 0;
    transition: opacity 0.25s;
}
.product-card:hover {
    border-color: #fecaca;
    transform: translateY(-2px);
    box-shadow: 0 10px 32px rgba(220,38,38,0.14);
}
.product-card:hover::before { opacity: 1; }

.cart-item {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ─── Product text ───────────────────────────── */
.prod-id    { font-size: 1rem; font-weight: 700; color: #111827; }
.prod-price { font-size: 1.2rem; font-weight: 800; color: #dc2626; }

/* ─── Category badges ───────────────────────── */
.prod-cat {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 0.7rem;
    font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; margin: 4px 0;
}
.cat-clothing    { background: #fff0f6; color: #be185d; border: 1px solid #fbcfe8; }
.cat-electronics { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.cat-beauty      { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.cat-home        { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }

/* ─── AI Prediction badges ───────────────────── */
.badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 6px; font-size: 0.68rem; font-weight: 700;
}
.badge-green  { background: #dcfce7; color: #16a34a; }
.badge-yellow { background: #fef9c3; color: #b45309; }
.badge-gray   { background: #f3f4f6; color: #6b7280; }
.badge-purple { background: #f5f3ff; color: #7c3aed; }
.badge-admin  { background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }

/* ─── Mini stats ─────────────────────────────── */
.mini-stat {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.2s;
}
.mini-stat:hover { border-color: #fecaca; box-shadow: 0 4px 16px rgba(220,38,38,0.1); }
.mini-stat-val { font-size: 1.6rem; font-weight: 800; color: #dc2626; }
.mini-stat-lbl { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; }

/* ─── Dividers ───────────────────────────────── */
.neon-hr {
    height: 1px;
    background: linear-gradient(90deg, transparent, #fee2e2, transparent);
    margin: 1rem 0; border: none;
}

/* ─── Chat ───────────────────────────────────── */
.chat-wrap {
    height: 440px; overflow-y: auto;
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 20px; padding: 1rem;
    display: flex; flex-direction: column; gap: 10px;
    scrollbar-width: thin; scrollbar-color: #fca5a5 transparent;
}
.msg-row-user { display: flex; justify-content: flex-end; }
.msg-row-ai   { display: flex; justify-content: flex-start; align-items: flex-end; gap: 8px; }

.bubble-user {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: #fff; border-radius: 18px 18px 4px 18px;
    padding: 10px 14px; max-width: 75%;
    font-size: 0.88rem; line-height: 1.5;
    box-shadow: 0 2px 10px rgba(220,38,38,0.3);
}
.bubble-ai {
    background: #ffffff; border: 1px solid #f3f4f6;
    color: #1f2937; border-radius: 18px 18px 18px 4px;
    padding: 10px 14px; max-width: 75%;
    font-size: 0.88rem; line-height: 1.6;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.ai-ava {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, #dc2626, #f87171);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; color: white; font-weight: 700; flex-shrink: 0;
}
.chat-time { font-size: 0.62rem; color: #9ca3af; margin-top: 2px; }

/* ─── Status dots ───────────────────────────── */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.dot-green { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.dot-red   { background: #ef4444; }

/* ─── Admin badge ───────────────────────────── */
.admin-badge {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white; border-radius: 6px;
    padding: 2px 8px; font-size: 0.7rem; font-weight: 700;
}

/* ─── Popularity bar ─────────────────────────── */
.pop-bar {
    height: 3px; border-radius: 2px;
    background: linear-gradient(90deg, #dc2626, #f87171);
    margin-top: 8px;
}

/* ─── Streamlit overrides ───────────────────── */
[data-testid="stMetricValue"]  { color: #dc2626 !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"]  { color: #6b7280 !important; }
[data-testid="stTab"]          { color: #6b7280 !important; }
[data-testid="stTab"][aria-selected="true"] { color: #dc2626 !important; border-bottom-color: #dc2626 !important; }
[data-testid="stDataFrameContainer"] { border-radius: 12px !important; border: 1px solid #f3f4f6 !important; }
div[data-testid="stExpander"]  { border: 1px solid #f3f4f6 !important; border-radius: 12px !important; }

/* ─── Alerts ─────────────────────────────────── */
.stAlert  { border-radius: 12px !important; border-left: 4px solid #dc2626 !important; }

/* ─── Animation ──────────────────────────────── */
@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.fade-in { animation: fadeIn 0.35s ease; }

/* ─── Scrollbar ──────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #fca5a5; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════
DEFAULTS = {
    "page": "login", "logged_in": False, "token": None,
    "current_user": None, "auth_tab": "login",
    "chat_msgs": [], "chat_typing": False, "quick_q": None,
    "local_cart": {},      # fallback cart when cart-service offline
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════
# DATA & CATALOG
# ════════════════════════════════════════════════
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "product-service", "products_catalog.json")
DATA_PATH    = os.path.join(os.path.dirname(__file__), "..", "data", "data_user500.csv")

@st.cache_data
def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_df():
    return pd.read_csv(DATA_PATH)

@st.cache_data
def build_product_stats(df):
    p = df.groupby("product_id").agg(
        views=("action", lambda x:(x=="view").sum()),
        clicks=("action", lambda x:(x=="click").sum()),
        carts=("action", lambda x:(x=="add_to_cart").sum()),
    ).reset_index()
    p["score"] = p["views"] + p["clicks"]*2 + p["carts"]*5
    p["score_norm"] = (p["score"]-p["score"].min())/(p["score"].max()-p["score"].min()+1)
    return p

try:
    catalog    = load_catalog()
    df_data    = load_df()
    prod_stats = build_product_stats(df_data)
except Exception as e:
    catalog    = {}
    df_data    = pd.DataFrame()
    prod_stats = pd.DataFrame()

# ════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════
CAT_CSS  = {"clothing":"cat-clothing","electronics":"cat-electronics","beauty":"cat-beauty","home":"cat-home"}
CAT_ICON = {"clothing":"👔","electronics":"💻","beauty":"💄","home":"🏠"}
PRED_CLS = {"add_to_cart":"badge-green","click":"badge-yellow","view":"badge-gray"}
PRED_ICO = {"add_to_cart":"🛒","click":"👆","view":"👁️"}

def cat_badge(cat):
    return f'<span class="prod-cat {CAT_CSS.get(cat,"")}">{CAT_ICON.get(cat,"📦")} {cat.capitalize()}</span>'

def now_str(): return datetime.now().strftime("%H:%M")
def go(page): st.session_state.page = page; st.rerun()
def is_admin(): return st.session_state.current_user and st.session_state.current_user.get("role") == "admin"
def token(): return st.session_state.token or ""

def get_cart_summary():
    """Try cart-service, fallback to local"""
    try:
        from services.api_client import get_cart
        return get_cart(token())
    except Exception:
        items = list(st.session_state.local_cart.values())
        total = sum(i["qty"]*i["price"] for i in items)
        return {"items": items, "total": total, "count": sum(i["qty"] for i in items)}

def cart_count():
    try:
        from services.api_client import get_cart
        return get_cart(token()).get("count", 0)
    except Exception:
        return sum(i["qty"] for i in st.session_state.local_cart.values())

def local_add_cart(product_id, name, price, category, qty=1):
    cart = st.session_state.local_cart
    if product_id in cart:
        cart[product_id]["qty"] += qty
    else:
        cart[product_id] = {"product_id":product_id,"name":name,"price":price,"category":category,"qty":qty}

def local_remove_cart(pid):
    st.session_state.local_cart.pop(pid, None)

def get_prediction_local(device, category, session_duration, price, user_id, product_id):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from predict_logic import predict_next_action
        return predict_next_action(device, category, session_duration, price, user_id, product_id)
    except Exception:
        return {"predicted_action":"view","confidence":0.5,"using_model":False}

def call_ai_local(question):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from rag_logic import ask_ai
        return ask_ai(question)
    except Exception as e:
        return f"Loi: {e}"

def get_recs_local(user_id, top_n=4):
    try:
        from predict_logic import get_top_products_for_user
        return get_top_products_for_user(df_data, user_id, top_n).to_dict(orient="records")
    except Exception:
        return []

def neo4j_online_status():
    try:
        from rag_logic import get_neo4j_status
        return get_neo4j_status().get("online", False)
    except Exception:
        return False

# ════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════
def render_sidebar():
    if not st.session_state.logged_in:
        return
    user = st.session_state.current_user
    cnt  = cart_count()

    with st.sidebar:
        # Avatar + profile
        init = (user.get("display_name") or "U")[0].upper()
        role_badge = '<span class="admin-badge">ADMIN</span>' if is_admin() else ""
        avatar_bg  = "linear-gradient(135deg,#dc2626,#b91c1c)" if is_admin() else "linear-gradient(135deg,#ef4444,#fca5a5)"
        st.markdown(f"""
<div style="text-align:center;padding:1rem 0 0.5rem;">
  <div style="width:64px;height:64px;border-radius:50%;
    background:{avatar_bg};
    margin:0 auto;display:flex;align-items:center;justify-content:center;
    font-size:26px;font-weight:700;color:white;
    box-shadow:0 4px 16px rgba(220,38,38,0.35);">
    {init}
  </div>
  <div style="margin-top:0.6rem;font-weight:700;color:#1a1a2e;">{user['display_name']} {role_badge}</div>
  <div style="font-size:0.72rem;color:#9ca3af;">{user.get('email','')}</div>
</div>
<hr style="border:1px solid #fee2e2;margin:0.5rem 0;"/>
""", unsafe_allow_html=True)

        # Nav
        nav_items = [
            ("🛒", "Shop",          "shop"),
            ("🛍️", f"Gio hang ({cnt})", "cart"),
            ("🤖", "AI Chat",       "chat"),
        ]
        if is_admin():
            nav_items.append(("⚙️", "Admin Dashboard", "admin"))

        for icon, label, page_key in nav_items:
            active = st.session_state.page == page_key
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                go(page_key)

        st.markdown('<hr style="border:1px solid #fee2e2;margin:0.5rem 0;"/>', unsafe_allow_html=True)

        # Service health indicators (compact)
        neo4j = neo4j_online_status()
        neo4j_color = "#15803d" if neo4j else "#9ca3af"
        st.markdown(f"""
<div style="font-size:0.72rem;color:#6b7280;padding:0 0.5rem;">
  <div><span class="status-dot {'dot-green' if neo4j else 'dot-red'}" style="margin-right:4px;"></span>
  <span style="color:{neo4j_color};font-weight:600;">Neo4j {'Connected' if neo4j else 'Offline'}</span></div>
  <div style="margin-top:3px;color:#9ca3af;">Gemini 2.5 Flash + RNN</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<hr style="border:1px solid #fee2e2;margin:0.5rem 0;"/>', unsafe_allow_html=True)
        if st.button("🚪 Dang xuat", use_container_width=True, key="logout_btn"):
            for k in ["logged_in","token","current_user","chat_msgs","local_cart"]:
                st.session_state[k] = DEFAULTS.get(k)
            go("login")

# ════════════════════════════════════════════════
# PAGE: LOGIN / REGISTER
# ════════════════════════════════════════════════
def page_auth():
    st.markdown("""
<div style="position:fixed;top:-10%;left:-10%;width:40%;height:40%;
background:radial-gradient(circle,rgba(139,92,246,0.15) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
<div style="position:fixed;bottom:-10%;right:-10%;width:40%;height:40%;
background:radial-gradient(circle,rgba(236,72,153,0.12) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
<div class="fade-in" style="text-align:center;margin-bottom:1.5rem;">
  <div style="width:72px;height:72px;border-radius:20px;
    background:linear-gradient(135deg,#dc2626,#b91c1c);
    margin:0 auto 0.8rem;display:flex;align-items:center;
    justify-content:center;font-size:2rem;
    box-shadow:0 8px 24px rgba(220,38,38,0.3);">🛒</div>
  <div style="font-size:2.5rem;font-weight:900;color:#1a1a2e;letter-spacing:-1px;">Shop<span style="color:#dc2626;">AI</span></div>
  <div style="color:#9ca3af;font-size:0.85rem;margin-top:4px;">Microservices · Neo4j · Gemini 2.5 Flash</div>
</div>""", unsafe_allow_html=True)

        t1, t2 = st.columns(2)
        with t1:
            if st.button("Dang nhap", key="tab_login", use_container_width=True):
                st.session_state.auth_tab = "login"; st.rerun()
        with t2:
            if st.button("Dang ky", key="tab_register", use_container_width=True):
                st.session_state.auth_tab = "register"; st.rerun()

        st.markdown('<hr style="border:1px solid #fee2e2;margin:0.8rem 0;"/>', unsafe_allow_html=True)

        # ── LOGIN ──
        if st.session_state.auth_tab == "login":
            st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#1a1a2e;text-align:center;margin-bottom:1rem;">Chao mung tro lai 👋</div>', unsafe_allow_html=True)
            username = st.text_input("Ten dang nhap", key="li_user", placeholder="username...")
            password = st.text_input("Mat khau", type="password", key="li_pass", placeholder="password...")

            if st.button("🚀 Dang nhap", key="do_login", use_container_width=True):
                if not username or not password:
                    st.error("Vui long nhap day du thong tin.")
                else:
                    try:
                        from services.api_client import login as api_login
                        result = api_login(username, password)
                        st.session_state.token = result["access_token"]
                        st.session_state.current_user = result["user"]
                        st.session_state.logged_in = True
                        go("shop")
                    except Exception:
                        # Local fallback auth
                        import hashlib
                        local_users = {
                            "admin": {"password_hash": hashlib.sha256(b"admin123").hexdigest(), "display_name":"Administrator","email":"admin@shopai.vn","role":"admin"},
                            "demo":  {"password_hash": hashlib.sha256(b"demo123").hexdigest(),  "display_name":"Demo User","email":"demo@shopai.vn","role":"user"},
                        }
                        u = local_users.get(username)
                        if u and u["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
                            st.session_state.token = "local_token"
                            st.session_state.current_user = {**u, "username": username}
                            st.session_state.logged_in = True
                            go("shop")
                        else:
                            st.error("Sai ten dang nhap hoac mat khau.")

            st.markdown("""
<div style="text-align:center;margin-top:0.8rem;font-size:0.78rem;color:#9ca3af;
  background:#fff5f5;padding:0.5rem;border-radius:8px;border:1px solid #fee2e2;">
  Demo: <code style="background:#fee2e2;color:#dc2626;padding:1px 4px;border-radius:4px;">admin</code>
  / <code style="background:#fee2e2;color:#dc2626;padding:1px 4px;border-radius:4px;">admin123</code> (Admin)
  &nbsp;·&nbsp;
  <code style="background:#f3f4f6;color:#6b7280;padding:1px 4px;border-radius:4px;">demo</code>
  / <code style="background:#f3f4f6;color:#6b7280;padding:1px 4px;border-radius:4px;">demo123</code> (User)
</div>""", unsafe_allow_html=True)

        # ── REGISTER ──
        else:
            st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#1a1a2e;text-align:center;margin-bottom:1rem;">Tao tai khoan moi ✨</div>', unsafe_allow_html=True)
            r_name  = st.text_input("Ho va ten",       key="rg_name",  placeholder="Nguyen Van A")
            r_email = st.text_input("Email",           key="rg_email", placeholder="email@example.com")
            r_user  = st.text_input("Ten dang nhap",   key="rg_user",  placeholder="username (min 3 ky tu)")
            r_pass  = st.text_input("Mat khau",        type="password", key="rg_pass",  placeholder="min 6 ky tu")
            r_conf  = st.text_input("Xac nhan mat khau", type="password", key="rg_conf", placeholder="nhap lai mat khau")

            if st.button("🎉 Dang ky ngay", key="do_register", use_container_width=True):
                if not all([r_name, r_email, r_user, r_pass, r_conf]):
                    st.error("Vui long dien day du tat ca cac truong.")
                elif r_pass != r_conf:
                    st.error("Mat khau xac nhan khong khop.")
                elif len(r_pass) < 6:
                    st.error("Mat khau phai co it nhat 6 ky tu.")
                elif len(r_user) < 3:
                    st.error("Ten dang nhap phai co it nhat 3 ky tu.")
                elif "@" not in r_email:
                    st.error("Email khong hop le.")
                else:
                    try:
                        from services.api_client import register as api_register
                        result = api_register(r_user, r_pass, r_name, r_email)
                        st.session_state.token = result["access_token"]
                        st.session_state.current_user = result["user"]
                        st.session_state.logged_in = True
                        st.success(f"Dang ky thanh cong! Chao mung {r_name}!")
                        time.sleep(0.5); go("shop")
                    except Exception as e:
                        st.error(f"Dang ky that bai: {e}")

# ════════════════════════════════════════════════
# PAGE: SHOP
# ════════════════════════════════════════════════
def page_shop():
    user   = st.session_state.current_user
    uid    = f"U{random.randint(1,500):03d}"

    st.markdown(f"""
<div class="fade-in">
  <div class="page-title">🛒 E-Commerce <span class="red">Shop</span></div>
  <div class="page-subtitle">Xin chao, <b style="color:#dc2626">{user['display_name']}</b>
  {'<span class="admin-badge" style="margin-left:6px;">ADMIN</span>' if is_admin() else ''}
  — Kham pha san pham voi AI goi y ca nhan hoa.</div>
</div>""", unsafe_allow_html=True)

    # Stats
    cc = cart_count()
    s1,s2,s3,s4 = st.columns(4)
    with s1: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{len(catalog)}</div><div class="mini-stat-lbl">Tong san pham</div></div>', unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{len(df_data["user_id"].unique()) if not df_data.empty else 500}</div><div class="mini-stat-lbl">Users</div></div>', unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{len(df_data):,}</div><div class="mini-stat-lbl">Interactions</div></div>', unsafe_allow_html=True)
    with s4: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{cc}</div><div class="mini-stat-lbl">Gio hang</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

    # Search + Filter
    fc1, fc2, fc3 = st.columns([3,1.2,1])
    with fc1:
        search = st.text_input("", placeholder="Tim san pham theo ten hoac category...", key="shop_search", label_visibility="collapsed")
    with fc2:
        cat_opts = ["Tat ca"] + sorted(set(v["category"] for v in catalog.values()))
        filter_cat = st.selectbox("", cat_opts, label_visibility="collapsed", key="shop_cat")
    with fc3:
        sort_by = st.selectbox("", ["Pho bien nhat","Gia tang dan","Gia giam dan"], label_visibility="collapsed", key="shop_sort")

    # AI Recommendations banner
    recs = get_recs_local(uid, 4)
    if recs:
        st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#dc2626;margin:0.8rem 0 0.5rem;">✨ AI Goi y rieng cho ban</div>', unsafe_allow_html=True)
        rc = st.columns(4)
        for i, r in enumerate(recs[:4]):
            pid  = r.get("product_id","")
            info = catalog.get(pid, {"name":pid,"category":r.get("category","home"),"price":r.get("avg_price",99),"image_emoji":"🛍️"})
            pred = get_prediction_local("mobile", info["category"], 350, float(info["price"]), uid, pid)
            pa   = pred["predicted_action"]
            with rc[i]:
                st.markdown(f"""
<div class="glass-card" style="padding:0.8rem;text-align:center;">
  <div style="font-size:1.5rem;">{info.get('image_emoji','📦')}</div>
  <div style="font-weight:700;color:#111827;font-size:0.85rem;margin-top:3px;">{info['name'][:22]}</div>
  {cat_badge(info['category'])}
  <div style="color:#dc2626;font-weight:800;">${info['price']:.2f}</div>
  <span class="badge {PRED_CLS.get(pa,'badge-gray')}">{PRED_ICO.get(pa,'')} {pa}</span>
</div>""", unsafe_allow_html=True)
                if st.button(f"+ Them", key=f"rec_{pid}", use_container_width=True):
                    try:
                        from services.api_client import add_to_cart as api_add
                        api_add(token(), pid, info["name"], float(info["price"]), info["category"])
                    except Exception:
                        local_add_cart(pid, info["name"], float(info["price"]), info["category"])
                    st.toast(f"Da them {info['name']} vao gio!")
                    st.rerun()

    st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

    # Filter & sort catalog
    items = {
        k: v for k, v in catalog.items()
        if (filter_cat == "Tat ca" or v["category"] == filter_cat)
        and (not search or search.lower() in v["name"].lower() or search.lower() in v["category"].lower() or search.lower() in k.lower())
    }
    if not prod_stats.empty:
        score_map = prod_stats.set_index("product_id")["score"].to_dict()
        norm_map  = prod_stats.set_index("product_id")["score_norm"].to_dict()
    else:
        score_map = {}; norm_map = {}

    if sort_by == "Gia tang dan":
        items = dict(sorted(items.items(), key=lambda x: x[1]["price"]))
    elif sort_by == "Gia giam dan":
        items = dict(sorted(items.items(), key=lambda x: x[1]["price"], reverse=True))
    else:
        items = dict(sorted(items.items(), key=lambda x: score_map.get(x[0],0), reverse=True))

    shown = list(items.items())[:12]
    st.caption(f"Hien thi {len(shown)} / {len(items)} san pham")

    cart_items = st.session_state.local_cart
    for row_start in range(0, len(shown), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = row_start + j
            if idx >= len(shown): break
            pid, info = shown[idx]
            pred = get_prediction_local("mobile", info["category"],
                                        random.randint(150,550), float(info["price"]), uid, pid)
            pa      = pred["predicted_action"]
            conf    = int(pred["confidence"]*100)
            pop_w   = int(norm_map.get(pid,0)*100)
            in_cart = pid in cart_items
            qty_in  = cart_items.get(pid,{}).get("qty",0)
            emoji   = info.get("image_emoji","📦")

            with cols[j]:
                st.markdown(f"""
<div class="product-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <span style="font-size:1.6rem;">{emoji}</span>
      <div class="prod-id" style="margin-top:2px;">{info['name'][:28]}</div>
      <div style="font-size:0.7rem;color:#475569;">{pid}</div>
    </div>
    <span class="prod-price">${info['price']:.2f}</span>
  </div>
  {cat_badge(info['category'])}
  <div style="font-size:0.72rem;color:#475569;margin:4px 0;">
    Ton kho: {info.get('stock','-')} sp
  </div>
  <div>
    <span class="badge {PRED_CLS.get(pa,'badge-gray')}">{PRED_ICO.get(pa,'')} {pa} {conf}%</span>
    {'<span style="color:#34D399;font-size:0.7rem;margin-left:6px;">+'+str(qty_in)+'</span>' if in_cart else ''}
  </div>
  <div class="pop-bar" style="width:{pop_w}%;"></div>
</div>""", unsafe_allow_html=True)

                btn = f"Da co x{qty_in} | Them" if in_cart else "Them vao gio"
                if st.button(btn, key=f"add_{pid}", use_container_width=True):
                    try:
                        from services.api_client import add_to_cart as api_add
                        api_add(token(), pid, info["name"], float(info["price"]), info["category"])
                    except Exception:
                        local_add_cart(pid, info["name"], float(info["price"]), info["category"])
                    st.toast(f"Da them {info['name']} vao gio!")
                    st.rerun()

# ════════════════════════════════════════════════
# PAGE: CART
# ════════════════════════════════════════════════
def page_cart():
    st.markdown('<div class="fade-in"><div class="page-title">Gio hang</div><div class="page-subtitle">Quan ly san pham va thanh toan</div></div>', unsafe_allow_html=True)

    # Get cart data
    try:
        from services.api_client import get_cart as api_cart, remove_from_cart as api_remove, update_cart_qty, checkout as api_checkout
        cart_data = api_cart(token())
        items     = cart_data.get("items", [])
        use_api   = True
    except Exception:
        items     = list(st.session_state.local_cart.values())
        total_raw = sum(i["qty"]*i["price"] for i in items)
        discount  = total_raw * 0.05 if total_raw > 500 else 0
        cart_data = {"items":items,"subtotal":total_raw,"discount":discount,"total":total_raw-discount,"count":sum(i["qty"] for i in items)}
        use_api   = False

    if not items:
        st.markdown('<div style="text-align:center;padding:4rem 2rem;"><div style="font-size:4rem;">🛒</div><div style="font-size:1.3rem;font-weight:600;color:#e2e8f0;margin-top:1rem;">Gio hang trong</div><div style="color:#64748b;margin-top:0.5rem;">Kham pha shop va them san pham yeu thich!</div></div>', unsafe_allow_html=True)
        if st.button("Di den Shop", key="empty_cart_shop"): go("shop")
        return

    col_items, col_summary = st.columns([1.8, 1])

    with col_items:
        st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#dc2626;margin-bottom:0.8rem;">🛍️ San pham da chon</div>', unsafe_allow_html=True)
        for item in items:
            pid   = item["product_id"]
            qty   = item["qty"]
            price = item["price"]
            name  = item.get("name", pid)
            cat   = item.get("category","home")
            info  = catalog.get(pid, {})
            emoji = info.get("image_emoji","📦")

            st.markdown(f"""
<div class="cart-item">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div style="display:flex;gap:0.8rem;align-items:center;">
      <span style="font-size:2rem;">{emoji}</span>
      <div>
        <div style="font-weight:700;color:#111827;">{name}</div>
        <div style="font-size:0.75rem;color:#9ca3af;">{pid}</div>
        {cat_badge(cat)}
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:1.2rem;font-weight:800;color:#dc2626;">${qty*price:.2f}</div>
      <div style="font-size:0.75rem;color:#9ca3af;">${price:.2f} × {qty}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            qa, qb, qc = st.columns([1,1,1])
            with qa:
                if st.button("Giam", key=f"dec_{pid}", use_container_width=True):
                    if use_api:
                        try: update_cart_qty(token(), pid, qty-1)
                        except Exception: pass
                    else:
                        if qty > 1: st.session_state.local_cart[pid]["qty"] -= 1
                        else: local_remove_cart(pid)
                    st.rerun()
            with qb:
                if st.button("Tang", key=f"inc_{pid}", use_container_width=True):
                    if use_api:
                        try: update_cart_qty(token(), pid, qty+1)
                        except Exception: pass
                    else:
                        st.session_state.local_cart[pid]["qty"] += 1
                    st.rerun()
            with qc:
                if st.button("Xoa", key=f"rem_{pid}", use_container_width=True):
                    if use_api:
                        try: api_remove(token(), pid)
                        except Exception: pass
                    local_remove_cart(pid)
                    st.rerun()

    with col_summary:
        total    = cart_data.get("total", 0)
        subtotal = cart_data.get("subtotal", total)
        discount = cart_data.get("discount", 0)

        st.markdown(f"""
<div class="glass-card">
  <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#dc2626;margin-bottom:1rem;">Tong don hang</div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
    <span style="color:#6b7280;">Tam tinh ({len(items)} sp)</span>
    <span style="color:#111827;font-weight:600;">${subtotal:.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
    <span style="color:#6b7280;">Phi van chuyen</span>
    <span style="color:#16a34a;font-weight:600;">Mien phi ✓</span>
  </div>
  {'<div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;"><span style="color:#6b7280;">Giam gia 5% (>$500)</span><span style="color:#dc2626;font-weight:600;">-$'+f"{discount:.2f}"+'</span></div>' if discount>0 else ''}
  <hr style="border:1px solid #f3f4f6;margin:0.8rem 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:1rem;">
    <span style="color:#111827;font-weight:700;font-size:1rem;">Tong cong</span>
    <span style="color:#dc2626;font-weight:800;font-size:1.3rem;">${total:.2f}</span>
  </div>
  {'<div style="background:#fff5f5;border:1px dashed #fca5a5;border-radius:10px;padding:0.6rem;margin-bottom:1rem;font-size:0.78rem;color:#6b7280;">Them $' + f"{max(0,500-subtotal):.2f}" + ' de duoc giam 5%!</div>' if subtotal < 500 else ''}
</div>""", unsafe_allow_html=True)


        if st.button("Thanh toan ngay", key="checkout_btn", use_container_width=True):
            try:
                if use_api:
                    order = api_checkout(token())
                    st.balloons()
                    st.success(f"Dat hang thanh cong! Ma don: {order.get('order_id','#ORD-' + str(int(time.time())))}")
                else:
                    st.balloons()
                    st.success("Dat hang thanh cong! Cam on ban da mua hang tai ShopAI.")
                    st.session_state.local_cart = {}
                time.sleep(1.5); go("shop")
            except Exception as e:
                st.error(f"Loi thanh toan: {e}")

        if st.button("Tiep tuc mua sam", key="continue_shop", use_container_width=True): go("shop")
        if st.button("Xoa gio hang", key="clear_all", use_container_width=True):
            st.session_state.local_cart = {}
            st.rerun()

# ════════════════════════════════════════════════
# PAGE: CHAT
# ════════════════════════════════════════════════
def page_chat():
    neo4j = neo4j_online_status()
    _, mid, _ = st.columns([0.1, 0.8, 0.1])
    with mid:
        st.markdown(f"""
<div class="fade-in" style="text-align:center;margin-bottom:1rem;">
  <div class="page-title">AI Shopping Assistant</div>
  <div class="page-subtitle">
    <span class="status-dot {'dot-green' if neo4j else 'dot-red'}" style="margin-right:4px;"></span>
    {'Neo4j RAG Online' if neo4j else 'LLM Fallback Mode'} &nbsp;·&nbsp;
    Gemini 2.5 Flash + KB_Graph
  </div>
</div>""", unsafe_allow_html=True)

        user = st.session_state.current_user
        if not st.session_state.chat_msgs:
            st.session_state.chat_msgs.append({
                "role": "assistant",
                "content": f"Xin chao <b>{user['display_name']}</b>! Toi la <b>ShopAI Assistant</b>. Toi co the giup ban tim san pham, tu van mua hang, va phan tich xu huong. Hay hoi toi bat cu dieu gi!",
                "time": now_str(),
            })

        chat_html = '<div class="chat-wrap">'
        for m in st.session_state.chat_msgs:
            t = m.get("time","")
            if m["role"] == "user":
                chat_html += f'<div class="msg-row-user"><div><div class="bubble-user">{m["content"]}</div><div class="chat-time" style="text-align:right">{t}</div></div></div>'
            else:
                chat_html += f'<div class="msg-row-ai"><div class="ai-ava">AI</div><div><div class="bubble-ai">{m["content"]}</div><div class="chat-time">{t}</div></div></div>'
        if st.session_state.chat_typing:
            chat_html += '<div class="msg-row-ai"><div class="ai-ava">AI</div><div class="bubble-ai">...</div></div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        st.markdown('<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;color:#64748b;margin:0.7rem 0 0.4rem">Cau hoi nhanh</div>', unsafe_allow_html=True)
        quick_qs = ["San pham pho bien nhat?","Category ban chay nhat?","Goi y 5 san pham hot","Xu huong mua sam?","Top san pham gia tot?","Review san pham electronics?"]
        qcols = st.columns(3)
        for i, q in enumerate(quick_qs):
            with qcols[i%3]:
                if st.button(q, key=f"qq_{i}", use_container_width=True):
                    st.session_state.quick_q = q; st.rerun()

        st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)
        ic, bc, cc = st.columns([5,1,1])
        with ic:
            user_input = st.text_input("", key="chat_in", label_visibility="collapsed",
                                       placeholder="Hoi AI ve san pham, goi y, xu huong...",
                                       value=st.session_state.quick_q or "")
        with bc:
            send = st.button("Gui", key="send_btn", use_container_width=True)
        with cc:
            if st.button("Xoa", key="clr_btn", use_container_width=True):
                st.session_state.chat_msgs = []; st.rerun()

        if st.session_state.quick_q:
            st.session_state.quick_q = None

        final_q = user_input.strip()
        if (send or final_q) and final_q:
            last = next((m["content"] for m in reversed(st.session_state.chat_msgs) if m["role"]=="user"), None)
            if final_q != last:
                st.session_state.chat_msgs.append({"role":"user","content":final_q,"time":now_str()})
                st.session_state.chat_typing = True
                st.rerun()

        if st.session_state.chat_typing:
            last_q = next((m["content"] for m in reversed(st.session_state.chat_msgs) if m["role"]=="user"), None)
            if last_q:
                with st.spinner(""):
                    try:
                        from services.api_client import chat_with_ai
                        answer = chat_with_ai(token(), last_q)
                    except Exception:
                        answer = call_ai_local(last_q)
                st.session_state.chat_msgs.append({"role":"assistant","content":answer.replace("\n","<br>"),"time":now_str()})
            st.session_state.chat_typing = False
            st.rerun()

# ════════════════════════════════════════════════
# MAIN ROUTER
# ════════════════════════════════════════════════
render_sidebar()

if not st.session_state.logged_in:
    page_auth()
else:
    pg = st.session_state.page
    if pg == "shop":
        page_shop()
    elif pg == "cart":
        page_cart()
    elif pg == "chat":
        page_chat()
    elif pg == "admin":
        if is_admin():
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from frontend.pages.admin_page import render_admin
            render_admin(token(), catalog)
        else:
            st.error("Khong co quyen truy cap.")
            go("shop")
    else:
        page_shop()
