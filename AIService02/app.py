"""
app.py — AI E-Commerce Intelligence Platform
Multi-page app with: Login/Register, Shop, Cart, AI Chat
Premium dark UI with glassmorphism design
"""
import streamlit as st
import pandas as pd
import hashlib
import time
import random
from datetime import datetime

st.set_page_config(
    page_title="ShopAI — Intelligent E-Commerce",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════
# GLOBAL CSS
# ════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, body, html, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ─── Dark Gradient Background ─── */
.stApp {
    background: radial-gradient(ellipse at top left, #1a0533 0%, #0d0d1a 40%, #000d1a 100%) !important;
    min-height: 100vh;
}
.block-container { padding: 1.5rem 2rem !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ─── Sidebar Styling ─── */
[data-testid="stSidebar"] {
    background: rgba(15, 5, 30, 0.95) !important;
    border-right: 1px solid rgba(139,92,246,0.2) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1rem !important; }

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.25s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #A78BFA, #8B5CF6) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(139,92,246,0.4) !important;
}

/* ─── Inputs ─── */
.stTextInput input, .stSelectbox select, .stPasswordInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(139,92,246,0.35) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 0.6rem 1rem !important;
}
.stTextInput input:focus, .stPasswordInput input:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.2) !important;
}

/* ─── Metric Cards ─── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.15) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* ─── Dataframes/Tables ─── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ─── Custom Components ─── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 20px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(139,92,246,0.5);
    background: rgba(139,92,246,0.08);
    box-shadow: 0 8px 32px rgba(139,92,246,0.2);
}

/* ─── Auth Card ─── */
.auth-container {
    max-width: 440px;
    margin: 0 auto;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 24px;
    padding: 2.5rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}

/* ─── Page Title ─── */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #A78BFA 0%, #EC4899 50%, #F59E0B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* ─── Product Card ─── */
.product-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 18px;
    padding: 1.2rem;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.product-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #8B5CF6, #EC4899);
    opacity: 0;
    transition: opacity 0.3s;
}
.product-card:hover { 
    border-color: rgba(139,92,246,0.5);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(139,92,246,0.25);
}
.product-card:hover::before { opacity: 1; }

.prod-id    { font-size:1.1rem; font-weight:700; color:#e2e8f0; }
.prod-price { font-size:1.3rem; font-weight:800; color:#A78BFA; }
.prod-cat   { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin:4px 0; }
.cat-clothing    { background:rgba(236,72,153,0.15);  color:#EC4899; border:1px solid rgba(236,72,153,0.3); }
.cat-electronics { background:rgba(59,130,246,0.15);  color:#60A5FA; border:1px solid rgba(59,130,246,0.3); }
.cat-beauty      { background:rgba(245,158,11,0.15);  color:#FBBF24; border:1px solid rgba(245,158,11,0.3); }
.cat-home        { background:rgba(52,211,153,0.15);  color:#34D399; border:1px solid rgba(52,211,153,0.3); }

/* ─── Badge ─── */
.badge {
    display:inline-block; padding:2px 8px; border-radius:6px;
    font-size:0.68rem; font-weight:700;
}
.badge-green  { background:rgba(52,211,153,0.2); color:#34D399; }
.badge-yellow { background:rgba(245,158,11,0.2); color:#FBBF24; }
.badge-gray   { background:rgba(100,116,139,0.2); color:#94a3b8; }

/* ─── Popularity Bar ─── */
.pop-bar { height:3px; border-radius:2px; background:linear-gradient(90deg,#8B5CF6,#EC4899); margin-top:8px; }

/* ─── Chat Bubbles ─── */
.chat-wrap {
    height:440px; overflow-y:auto;
    background:rgba(0,0,0,0.25);
    border:1px solid rgba(139,92,246,0.15);
    border-radius:20px;
    padding:1rem;
    display:flex; flex-direction:column; gap:10px;
    scrollbar-width:thin; scrollbar-color:rgba(139,92,246,0.3) transparent;
}
.msg-row-user { display:flex; justify-content:flex-end; }
.msg-row-ai   { display:flex; justify-content:flex-start; align-items:flex-end; gap:8px; }
.bubble-user  { 
    background:linear-gradient(135deg,#8B5CF6,#EC4899);
    color:#fff; border-radius:18px 18px 4px 18px;
    padding:10px 14px; max-width:72%;
    font-size:0.88rem; line-height:1.5;
    box-shadow:0 4px 15px rgba(139,92,246,0.35);
}
.bubble-ai {
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.1);
    color:#e2e8f0; border-radius:18px 18px 18px 4px;
    padding:10px 14px; max-width:72%;
    font-size:0.88rem; line-height:1.6;
}
.ai-ava {
    width:30px; height:30px; border-radius:50%;
    background:linear-gradient(135deg,#06b6d4,#6366f1);
    display:flex; align-items:center; justify-content:center;
    font-size:14px; flex-shrink:0;
}
.chat-time { font-size:0.62rem; color:#475569; margin-top:2px; }

/* ─── Cart Item ─── */
.cart-item {
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(139,92,246,0.15);
    border-radius:14px; padding:1rem;
    display:flex; align-items:center; gap:1rem;
    margin-bottom:0.7rem;
}

/* ─── Nav Pills ─── */
.nav-pill {
    display:block; padding:0.65rem 1rem;
    border-radius:12px; color:#94a3b8;
    font-size:0.9rem; font-weight:500;
    margin-bottom:0.3rem; cursor:pointer;
    transition:all 0.2s;
    text-decoration:none;
}
.nav-pill:hover, .nav-pill.active {
    background:rgba(139,92,246,0.2);
    color:#A78BFA;
}

/* ─── Divider ─── */
.neon-hr { height:1px; background:linear-gradient(90deg,transparent,rgba(139,92,246,0.4),transparent); margin:1rem 0; border:none; }

/* ─── Login tabs ─── */
.tab-btn {
    background:transparent; border:none;
    padding:0.5rem 1rem; border-radius:10px;
    color:#64748b; font-weight:600; cursor:pointer;
    transition:all 0.2s; font-size:0.9rem;
}
.tab-btn.active { background:rgba(139,92,246,0.2); color:#A78BFA; }

/* ─── Stat mini card ─── */
.mini-stat { 
    background:rgba(255,255,255,0.04); 
    border:1px solid rgba(139,92,246,0.15); 
    border-radius:12px; padding:0.8rem; text-align:center; 
}
.mini-stat-val { font-size:1.5rem; font-weight:800; color:#A78BFA; }
.mini-stat-lbl { font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; }

/* ─── Animations ─── */
@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes ping { 0%,100%{opacity:1} 50%{opacity:0.4} }
.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; }
.dot-green { background:#34D399; box-shadow:0 0 6px #34D399; animation:ping 2s infinite; }
.dot-red   { background:#F87171; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# SESSION STATE INIT
# ════════════════════════════════════════════════
DEFAULTS = {
    "page":          "login",      # login | shop | cart | chat
    "logged_in":     False,
    "current_user":  None,         # {"username", "display_name", "email"}
    "users_db":      {},           # {username: {password_hash, display_name, email}}
    "cart":          {},           # {product_id: {"qty": n, "price": p, "category": c}}
    "chat_msgs":     [],           # [{role, content, time}]
    "chat_typing":   False,
    "quick_q":       None,
    "auth_tab":      "login",      # login | register
    "last_search":   "",
    "filter_cat":    "Tất cả",
    "neo4j_checked": False,
    "neo4j_online":  False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════
# DATA & CACHE
# ════════════════════════════════════════════════
@st.cache_data
def load_data():
    return pd.read_csv("data_user500.csv")

@st.cache_data
def build_product_catalog(df):
    p = (df.groupby("product_id").agg(
        category=("category","first"),
        avg_price=("price","mean"),
        views=("action", lambda x:(x=="view").sum()),
        clicks=("action", lambda x:(x=="click").sum()),
        carts=("action", lambda x:(x=="add_to_cart").sum()),
    ).reset_index())
    p["score"] = p["views"]*1 + p["clicks"]*2 + p["carts"]*5
    p["score_norm"] = (p["score"]-p["score"].min())/(p["score"].max()-p["score"].min()+1e-9)
    p["avg_price"] = p["avg_price"].round(2)
    return p

df = load_data()
products = build_product_catalog(df)

from predict_logic import predict_next_action, get_top_products_for_user, get_popular_products

# ════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════
CATEGORY_ICON = {"clothing":"👔","electronics":"💻","beauty":"💄","home":"🏠"}
PRED_ICON     = {"add_to_cart":"🛒","click":"👆","view":"👁️"}
PRED_CLS      = {"add_to_cart":"badge-green","click":"badge-yellow","view":"badge-gray"}
CAT_CSS       = {"clothing":"cat-clothing","electronics":"cat-electronics","beauty":"cat-beauty","home":"cat-home"}

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def now_str():   return datetime.now().strftime("%H:%M")
def cat_badge(cat): return f'<span class="prod-cat {CAT_CSS.get(cat,"")}">{CATEGORY_ICON.get(cat,"📦")} {cat.capitalize()}</span>'

def cart_count():  return sum(v["qty"] for v in st.session_state.cart.values())
def cart_total():  return sum(v["qty"]*v["price"] for v in st.session_state.cart.values())

def add_to_cart(pid, price, category):
    if pid in st.session_state.cart:
        st.session_state.cart[pid]["qty"] += 1
    else:
        st.session_state.cart[pid] = {"qty":1,"price":price,"category":category}

def remove_from_cart(pid):
    st.session_state.cart.pop(pid, None)

def go(page): st.session_state.page = page; st.rerun()

# ════════════════════════════════════════════════
# NEO4J + RAG (lazy, once)
# ════════════════════════════════════════════════
def get_rag_status():
    if not st.session_state.neo4j_checked:
        try:
            from rag_logic import get_neo4j_status
            s = get_neo4j_status()
            st.session_state.neo4j_online = s["online"]
        except Exception:
            st.session_state.neo4j_online = False
        st.session_state.neo4j_checked = True
    return st.session_state.neo4j_online

def call_ai(question):
    try:
        from rag_logic import ask_ai
        return ask_ai(question)
    except Exception as e:
        return f"Loi he thong AI: {e}"

# ════════════════════════════════════════════════
# SIDEBAR NAVIGATION (only when logged in)
# ════════════════════════════════════════════════
def render_sidebar():
    if not st.session_state.logged_in:
        return
    with st.sidebar:
        user = st.session_state.current_user
        # Avatar
        st.markdown(f"""
<div style="text-align:center; padding:1rem 0 0.5rem;">
  <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#8B5CF6,#EC4899);
              margin:0 auto;display:flex;align-items:center;justify-content:center;
              font-size:24px;font-weight:700;color:white;box-shadow:0 4px 15px rgba(139,92,246,0.4);">
    {user['display_name'][0].upper()}
  </div>
  <div style="margin-top:0.5rem;font-weight:600;color:#e2e8f0;">{user['display_name']}</div>
  <div style="font-size:0.75rem;color:#64748b;">{user['email']}</div>
</div>
<hr class="neon-hr"/>
""", unsafe_allow_html=True)

        # Navigation
        pages = [
            ("🛒", "Shop",    "shop"),
            ("🛍️", f"Giỏ hàng ({cart_count()})", "cart"),
            ("🤖", "AI Chat", "chat"),
        ]
        for icon, label, page_key in pages:
            active_cls = "active" if st.session_state.page == page_key else ""
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                go(page_key)

        st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

        # Neo4j status
        online = get_rag_status()
        dot = "dot-green" if online else "dot-red"
        label = "Neo4j Connected" if online else "Neo4j Offline"
        st.markdown(f'<div style="font-size:0.75rem;color:#64748b;text-align:center;"><span class="status-dot {dot}"></span> {label}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="neon-hr" style="margin-top:1rem"/>', unsafe_allow_html=True)
        # Logout
        if st.button("🚪 Đăng xuất", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.cart = {}
            st.session_state.chat_msgs = []
            st.session_state.neo4j_checked = False
            go("login")

# ════════════════════════════════════════════════
# PAGE: LOGIN / REGISTER
# ════════════════════════════════════════════════
def page_auth():
    # Background glow
    st.markdown("""
<div style="position:fixed;top:-10%;left:-10%;width:40%;height:40%;
background:radial-gradient(circle,rgba(139,92,246,0.15) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
<div style="position:fixed;bottom:-10%;right:-10%;width:40%;height:40%;
background:radial-gradient(circle,rgba(236,72,153,0.12) 0%,transparent 70%);pointer-events:none;z-index:0;"></div>
""", unsafe_allow_html=True)

    # Center content
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        # Logo
        st.markdown("""
<div class="fade-in" style="text-align:center; margin-bottom:2rem;">
  <div style="font-size:3rem; margin-bottom:0.5rem;">⚡</div>
  <div class="page-title" style="font-size:2.2rem;">ShopAI</div>
  <div style="color:#64748b; font-size:0.9rem;">Intelligent E-Commerce Platform</div>
</div>
""", unsafe_allow_html=True)

        # Tab selector
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("🔑 Đăng nhập", key="tab_login", use_container_width=True):
                st.session_state.auth_tab = "login"
                st.rerun()
        with tab_col2:
            if st.button("✨ Đăng ký", key="tab_register", use_container_width=True):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

        # ─── LOGIN FORM ───
        if st.session_state.auth_tab == "login":
            st.markdown('<div style="text-align:center;font-size:1.2rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">Chào mừng trở lại 👋</div>', unsafe_allow_html=True)

            username = st.text_input("Tên đăng nhập", key="login_user", placeholder="Nhập username...")
            password = st.text_input("Mật khẩu", type="password", key="login_pass", placeholder="Nhập mật khẩu...")

            if st.button("🚀 Đăng nhập", key="do_login", use_container_width=True):
                # Demo accounts
                demo_users = {
                    "admin": {"password_hash": hash_pw("admin123"), "display_name": "Administrator", "email": "admin@shopai.vn"},
                    "demo":  {"password_hash": hash_pw("demo123"),  "display_name": "Demo User",     "email": "demo@shopai.vn"},
                }
                all_users = {**demo_users, **st.session_state.users_db}

                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ thông tin.")
                elif username in all_users and all_users[username]["password_hash"] == hash_pw(password):
                    u = all_users[username]
                    st.session_state.logged_in = True
                    st.session_state.current_user = {
                        "username":     username,
                        "display_name": u["display_name"],
                        "email":        u["email"],
                    }
                    st.session_state.page = "shop"
                    st.success(f"Chào mừng {u['display_name']}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu.")

            st.markdown("""
<div style="text-align:center;margin-top:1rem;font-size:0.8rem;color:#64748b;">
  Demo: <code>admin</code> / <code>admin123</code> &nbsp;·&nbsp; <code>demo</code> / <code>demo123</code>
</div>""", unsafe_allow_html=True)

        # ─── REGISTER FORM ───
        else:
            st.markdown('<div style="text-align:center;font-size:1.2rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">Tạo tài khoản mới ✨</div>', unsafe_allow_html=True)

            display_name = st.text_input("Họ và tên", key="reg_name", placeholder="Nguyễn Văn A")
            email        = st.text_input("Email",     key="reg_email", placeholder="email@example.com")
            new_user     = st.text_input("Tên đăng nhập", key="reg_user", placeholder="Chọn username...")
            new_pass     = st.text_input("Mật khẩu",    type="password", key="reg_pass",  placeholder="Ít nhất 6 ký tự")
            confirm_pass = st.text_input("Xác nhận mật khẩu", type="password", key="reg_confirm", placeholder="Nhập lại mật khẩu")

            if st.button("🎉 Đăng ký ngay", key="do_register", use_container_width=True):
                demo_reserved = {"admin", "demo"}
                if not all([display_name, email, new_user, new_pass, confirm_pass]):
                    st.error("Vui lòng điền đầy đủ tất cả các trường.")
                elif new_user in demo_reserved or new_user in st.session_state.users_db:
                    st.error("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.")
                elif len(new_pass) < 6:
                    st.error("Mật khẩu phải có ít nhất 6 ký tự.")
                elif new_pass != confirm_pass:
                    st.error("Mật khẩu xác nhận không khớp.")
                elif "@" not in email:
                    st.error("Email không hợp lệ.")
                else:
                    st.session_state.users_db[new_user] = {
                        "password_hash": hash_pw(new_pass),
                        "display_name":  display_name,
                        "email":         email,
                    }
                    st.success(f"Đăng ký thành công! Chào mừng {display_name}!")
                    st.session_state.logged_in = True
                    st.session_state.current_user = {
                        "username":     new_user,
                        "display_name": display_name,
                        "email":        email,
                    }
                    st.session_state.page = "shop"
                    time.sleep(0.5)
                    st.rerun()

# ════════════════════════════════════════════════
# PAGE: SHOP
# ════════════════════════════════════════════════
def page_shop():
    user = st.session_state.current_user
    uid  = f"U{random.randint(1,500):03d}"  # Map to dataset user for recommendations

    st.markdown(f"""
<div class="fade-in">
  <div class="page-title">🛒 E-Commerce Shop</div>
  <div class="page-subtitle">Xin chào, <b style="color:#A78BFA">{user['display_name']}</b>! Khám phá sản phẩm với AI gợi ý cá nhân hóa.</div>
</div>
""", unsafe_allow_html=True)

    # ── Stats row ──
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{df["user_id"].nunique()}</div><div class="mini-stat-lbl">👥 Users</div></div>', unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{df["product_id"].nunique()}</div><div class="mini-stat-lbl">🛍️ Products</div></div>', unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{len(df):,}</div><div class="mini-stat-lbl">📊 Interactions</div></div>', unsafe_allow_html=True)
    with s4: st.markdown(f'<div class="mini-stat"><div class="mini-stat-val">{cart_count()}</div><div class="mini-stat-lbl">🛒 Giỏ hàng</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

    # ── Search & Filter ──
    fc1, fc2, fc3 = st.columns([3,1.2,1])
    with fc1:
        search = st.text_input("", placeholder="🔍 Tìm sản phẩm theo ID hoặc category...", key="shop_search", label_visibility="collapsed")
    with fc2:
        cat_opts = ["Tất cả"] + sorted(df["category"].unique().tolist())
        filter_cat = st.selectbox("", cat_opts, label_visibility="collapsed", key="shop_cat")
    with fc3:
        sort_by = st.selectbox("", ["Phổ biến nhất", "Giá tăng dần", "Giá giảm dần"], label_visibility="collapsed", key="shop_sort")

    # ── AI Recommendation strip ──
    recs = get_top_products_for_user(df, uid, top_n=4)
    if not recs.empty:
        st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#8B5CF6;margin:0.8rem 0 0.5rem;">✨ AI gợi ý riêng cho bạn</div>', unsafe_allow_html=True)
        rc = st.columns(4)
        for i, (_, r) in enumerate(recs.iterrows()):
            pred = predict_next_action("mobile", r["category"], 350, float(r["avg_price"]), uid, r["product_id"])
            pa   = pred["predicted_action"]
            with rc[i]:
                st.markdown(f"""
<div class="glass-card" style="padding:0.8rem;text-align:center;">
  <div style="font-weight:700;color:#e2e8f0;font-size:0.95rem;">{r['product_id']}</div>
  {cat_badge(r['category'])}
  <div style="color:#A78BFA;font-weight:800;margin:4px 0;">${r['avg_price']:.2f}</div>
  <span class="badge {PRED_CLS.get(pa,'badge-gray')}">{PRED_ICON.get(pa,'')} {pa}</span>
</div>""", unsafe_allow_html=True)
                if st.button("+ Thêm vào giỏ", key=f"rec_add_{r['product_id']}", use_container_width=True):
                    add_to_cart(r["product_id"], float(r["avg_price"]), r["category"])
                    st.toast(f"Đã thêm {r['product_id']} vào giỏ! 🛒")
                    st.rerun()

    st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

    # ── Filter products ──
    filtered = products.copy()
    if search:
        filtered = filtered[filtered["product_id"].str.contains(search, case=False) |
                            filtered["category"].str.contains(search, case=False)]
    if filter_cat != "Tất cả":
        filtered = filtered[filtered["category"] == filter_cat]
    if sort_by == "Phổ biến nhất":
        filtered = filtered.sort_values("score", ascending=False)
    elif sort_by == "Giá tăng dần":
        filtered = filtered.sort_values("avg_price", ascending=True)
    else:
        filtered = filtered.sort_values("avg_price", ascending=False)
    filtered = filtered.reset_index(drop=True)

    total_shown = min(len(filtered), 12)
    st.caption(f"📦 Hiển thị **{total_shown}** / {len(filtered)} sản phẩm")

    # ── Product Grid (3 columns) ──
    for row_start in range(0, total_shown, 3):
        cols = st.columns(3)
        for j in range(3):
            idx = row_start + j
            if idx >= total_shown:
                break
            p = filtered.iloc[idx]
            pred = predict_next_action(
                "mobile", p["category"],
                random.randint(150, 550),
                float(p["avg_price"]),
                uid, p["product_id"]
            )
            pa       = pred["predicted_action"]
            conf_pct = int(pred["confidence"]*100)
            model_lbl = "🤖" if pred["using_model"] else "📐"
            pop_w    = int(p["score_norm"]*100)
            in_cart  = p["product_id"] in st.session_state.cart
            qty_in   = st.session_state.cart.get(p["product_id"], {}).get("qty", 0)

            with cols[j]:
                st.markdown(f"""
<div class="product-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <span class="prod-id">🏷️ {p['product_id']}</span>
    <span class="prod-price">${p['avg_price']:.2f}</span>
  </div>
  {cat_badge(p['category'])}
  <div style="font-size:0.72rem;color:#475569;margin:4px 0;">
    👁️ {p['views']} views &nbsp;·&nbsp; 🖱️ {p['clicks']} clicks &nbsp;·&nbsp; 🛒 {p['carts']} carts
  </div>
  <div style="margin-top:6px;">
    <span class="badge {PRED_CLS.get(pa,'badge-gray')}">{model_lbl} {PRED_ICON.get(pa,'')} {pa} {conf_pct}%</span>
    {'<span style="color:#34D399;font-size:0.72rem;margin-left:8px;">✓ Trong giỏ ×'+str(qty_in)+'</span>' if in_cart else ''}
  </div>
  <div class="pop-bar" style="width:{pop_w}%;"></div>
</div>""", unsafe_allow_html=True)

                btn_label = f"✅ Đã có ×{qty_in} | Thêm" if in_cart else "🛒 Thêm vào giỏ"
                if st.button(btn_label, key=f"add_{p['product_id']}", use_container_width=True):
                    add_to_cart(p["product_id"], float(p["avg_price"]), p["category"])
                    st.toast(f"Đã thêm {p['product_id']} vào giỏ hàng!")
                    st.rerun()

# ════════════════════════════════════════════════
# PAGE: CART
# ════════════════════════════════════════════════
def page_cart():
    st.markdown('<div class="fade-in"><div class="page-title">🛍️ Giỏ hàng</div><div class="page-subtitle">Quản lý sản phẩm và thanh toán</div></div>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("""
<div style="text-align:center;padding:4rem 2rem;">
  <div style="font-size:4rem;margin-bottom:1rem;">🛒</div>
  <div style="font-size:1.3rem;font-weight:600;color:#e2e8f0;margin-bottom:0.5rem;">Giỏ hàng trống</div>
  <div style="color:#64748b;">Hãy khám phá shop và thêm sản phẩm yêu thích!</div>
</div>""", unsafe_allow_html=True)
        if st.button("🛒 Đi đến Shop", use_container_width=False):
            go("shop")
        return

    col_items, col_summary = st.columns([1.8, 1])

    with col_items:
        st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#8B5CF6;margin-bottom:0.8rem;">SẢN PHẨM ĐÃ CHỌN</div>', unsafe_allow_html=True)

        for pid, info in list(st.session_state.cart.items()):
            cat  = info["category"]
            qty  = info["qty"]
            price = info["price"]
            subtotal = qty * price

            with st.container():
                st.markdown(f"""
<div class="glass-card" style="margin-bottom:0.7rem;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-weight:700;color:#e2e8f0;font-size:1rem;">🏷️ {pid}</div>
      {cat_badge(cat)}
      <div style="color:#A78BFA;font-weight:700;margin-top:4px;">${price:.2f} / sản phẩm</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:1.2rem;font-weight:800;color:#34D399;">${subtotal:.2f}</div>
      <div style="font-size:0.78rem;color:#64748b;">Số lượng: {qty}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

                qa, qb, qc = st.columns([1,1,1])
                with qa:
                    if st.button("➖", key=f"minus_{pid}", use_container_width=True):
                        if st.session_state.cart[pid]["qty"] > 1:
                            st.session_state.cart[pid]["qty"] -= 1
                        else:
                            remove_from_cart(pid)
                        st.rerun()
                with qb:
                    if st.button("➕", key=f"plus_{pid}", use_container_width=True):
                        st.session_state.cart[pid]["qty"] += 1
                        st.rerun()
                with qc:
                    if st.button("🗑️ Xóa", key=f"del_{pid}", use_container_width=True):
                        remove_from_cart(pid)
                        st.rerun()

    with col_summary:
        total = cart_total()
        item_count = cart_count()
        discount = total * 0.05 if total > 500 else 0
        final = total - discount

        st.markdown(f"""
<div class="glass-card" style="position:sticky;top:1rem;">
  <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#8B5CF6;margin-bottom:1rem;">
    TỔNG ĐƠN HÀNG
  </div>

  <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
    <span style="color:#94a3b8;">Tạm tính ({item_count} sản phẩm)</span>
    <span style="color:#e2e8f0;font-weight:600;">${total:.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
    <span style="color:#94a3b8;">Phí vận chuyển</span>
    <span style="color:#34D399;font-weight:600;">Miễn phí</span>
  </div>
  {'<div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;"><span style="color:#94a3b8;">Giảm giá 5% (>$500)</span><span style="color:#EC4899;font-weight:600;">-$'+f"{discount:.2f}"+'</span></div>' if discount > 0 else ""}

  <hr style="border:1px solid rgba(139,92,246,0.2);margin:0.8rem 0;">

  <div style="display:flex;justify-content:space-between;margin-bottom:1rem;">
    <span style="color:#e2e8f0;font-weight:700;font-size:1rem;">Tổng cộng</span>
    <span style="color:#A78BFA;font-weight:800;font-size:1.3rem;">${final:.2f}</span>
  </div>

  <div style="background:rgba(139,92,246,0.1);border:1px dashed rgba(139,92,246,0.3);border-radius:10px;padding:0.6rem;margin-bottom:1rem;font-size:0.78rem;color:#94a3b8;">
    🎁 Mua thêm ${max(0,500-total):.2f} để được giảm 5%!
  </div>
</div>""", unsafe_allow_html=True)

        if st.button("💳 Thanh toán ngay", key="checkout_btn", use_container_width=True):
            st.balloons()
            st.success("🎉 Đặt hàng thành công! Cảm ơn bạn đã mua hàng tại ShopAI.")
            st.session_state.cart = {}
            time.sleep(2)
            go("shop")

        if st.button("🛒 Tiếp tục mua sắm", key="continue_shop", use_container_width=True):
            go("shop")

        st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Xóa tất cả", key="clear_cart", use_container_width=True):
            st.session_state.cart = {}
            st.rerun()

# ════════════════════════════════════════════════
# PAGE: AI CHAT
# ════════════════════════════════════════════════
def page_chat():
    online = get_rag_status()
    dot    = "dot-green" if online else "dot-red"
    status = "Neo4j RAG Online" if online else "LLM Fallback Mode"

    _, mid, _ = st.columns([0.1, 0.8, 0.1])
    with mid:
        st.markdown(f"""
<div class="fade-in" style="text-align:center;margin-bottom:1rem;">
  <div class="page-title">🤖 AI Shopping Assistant</div>
  <div class="page-subtitle">
    <span class="status-dot {dot}" style="margin-right:4px;"></span>{status}&nbsp;·&nbsp;
    Powered by <b style="color:#A78BFA">Gemini 2.5 Flash</b> + <b style="color:#34D399">Neo4j KB_Graph</b>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Welcome message ──
        if not st.session_state.chat_msgs:
            user = st.session_state.current_user
            st.session_state.chat_msgs.append({
                "role":    "assistant",
                "content": f"Xin chào <b>{user['display_name']}</b>! Tôi là <b>AI Shopping Assistant</b> của ShopAI. "
                           f"Tôi được kết nối với Knowledge Base Graph chứa dữ liệu của <b>500 users</b> và <b>100 sản phẩm</b>.<br><br>"
                           f"Hãy hỏi tôi về sản phẩm, xu hướng mua sắm, hoặc gợi ý cá nhân hóa!",
                "time": now_str(),
            })

        # ── Chat messages ──
        chat_html = '<div class="chat-wrap" id="chatbox">'
        for m in st.session_state.chat_msgs:
            t = m.get("time","")
            if m["role"] == "user":
                chat_html += f'<div class="msg-row-user"><div><div class="bubble-user">{m["content"]}</div><div class="chat-time" style="text-align:right">{t}</div></div></div>'
            else:
                chat_html += f'<div class="msg-row-ai"><div class="ai-ava">🤖</div><div><div class="bubble-ai">{m["content"]}</div><div class="chat-time">{t}</div></div></div>'

        if st.session_state.chat_typing:
            chat_html += '<div class="msg-row-ai"><div class="ai-ava">🤖</div><div class="bubble-ai" style="padding:12px 16px"><span style="display:inline-flex;gap:5px"><span style="width:7px;height:7px;border-radius:50%;background:#8B5CF6;animation:ping 1s infinite"></span><span style="width:7px;height:7px;border-radius:50%;background:#8B5CF6;animation:ping 1s 0.2s infinite"></span><span style="width:7px;height:7px;border-radius:50%;background:#8B5CF6;animation:ping 1s 0.4s infinite"></span></span></div></div>'

        chat_html += '</div><script>var b=document.getElementById("chatbox");if(b)b.scrollTop=b.scrollHeight;</script>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # ── Quick actions ──
        st.markdown('<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;color:#64748b;margin:0.7rem 0 0.4rem">⚡ Câu hỏi nhanh</div>', unsafe_allow_html=True)
        qa1, qa2, qa3 = st.columns(3)
        quick_qs = [
            "San pham pho bien nhat?",
            "Category nao ban chay nhat?",
            "Goi y 5 san pham tot nhat",
            "Hanh vi mua hang tren mobile?",
            "Top users mua nhieu nhat?",
            "Gia trung binh theo category?",
        ]
        qs_cols = st.columns(3)
        for i, q in enumerate(quick_qs):
            with qs_cols[i % 3]:
                if st.button(q, key=f"qq_{i}", use_container_width=True):
                    st.session_state.quick_q = q
                    st.rerun()

        st.markdown('<hr class="neon-hr"/>', unsafe_allow_html=True)

        # ── Input row ──
        ic, bc, cc = st.columns([5, 1, 1])
        with ic:
            user_input = st.text_input("", key="chat_in", label_visibility="collapsed",
                                       placeholder="💬 Hỏi AI về sản phẩm, xu hướng, gợi ý...",
                                       value=st.session_state.quick_q or "")
        with bc:
            send = st.button("▶ Gửi", key="send_btn", use_container_width=True)
        with cc:
            if st.button("🗑️", key="clr_btn", use_container_width=True):
                st.session_state.chat_msgs = []
                st.rerun()

        if st.session_state.quick_q:
            st.session_state.quick_q = None

        # ── Send logic ──
        final_q = user_input.strip()
        if (send or final_q) and final_q:
            last_user = next((m["content"] for m in reversed(st.session_state.chat_msgs) if m["role"]=="user"), None)
            if final_q != last_user:
                st.session_state.chat_msgs.append({"role":"user","content":final_q,"time":now_str()})
                st.session_state.chat_typing = True
                st.rerun()

        if st.session_state.chat_typing:
            last_q = next((m["content"] for m in reversed(st.session_state.chat_msgs) if m["role"]=="user"), None)
            if last_q:
                with st.spinner(""):
                    answer = call_ai(last_q)
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
    else:
        page_shop()