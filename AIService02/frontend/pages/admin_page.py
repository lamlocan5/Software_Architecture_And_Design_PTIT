"""
frontend/pages/admin_page.py
Admin Dashboard: Stats, Product CRUD, Neo4j Graph Visualization, Cypher Console
Uses Neo4j native driver for accurate relationship type retrieval.
"""
import streamlit as st
import pandas as pd
import os, sys
from dotenv import load_dotenv
load_dotenv()

# Path setup for local imports
_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_dir, ".."))       # frontend/
sys.path.insert(0, os.path.join(_dir, "..", "..")) # project root

CAT_CSS  = {"clothing":"cat-clothing","electronics":"cat-electronics","beauty":"cat-beauty","home":"cat-home"}
CAT_ICON = {"clothing":"👔","electronics":"💻","beauty":"💄","home":"🏠"}
NODE_COLORS = {
    "User":     "#8B5CF6",
    "Product":  "#F59E0B",
    "Category": "#10B981",
    "Device":   "#3B82F6",
}
EDGE_COLORS = {
    "VIEWED":        "#94A3B8",
    "CLICKED":       "#FBBF24",
    "ADDED_TO_CART": "#34D399",
    "IN_CATEGORY":   "#10B981",
    "USES_DEVICE":   "#60A5FA",
}


# ═══════════════════════════════════════════
# Load graph data DIRECTLY via Neo4j driver
# ═══════════════════════════════════════════
def _load_graph_direct(node_limit: int) -> dict:
    """Query Neo4j directly (no LangChain wrapper) for accurate rel types."""
    from neo4j import GraphDatabase

    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD", "123456789")

    driver = GraphDatabase.driver(uri, auth=(user, pw))
    nodes, edges = [], []

    with driver.session() as s:
        # Nodes
        result = s.run(f"""
            MATCH (n)
            RETURN elementId(n) AS id,
                   labels(n)[0] AS label,
                   properties(n) AS props
            LIMIT {node_limit}
        """)
        for rec in result:
            nodes.append({
                "id":    rec["id"],
                "label": rec["label"],
                "props": dict(rec["props"]),
            })

        # Collect node IDs for edge query
        node_ids = [n["id"] for n in nodes]

        # Edges — type(r) gives relationship type; also get action property as fallback
        result2 = s.run(f"""
            MATCH (a)-[r]->(b)
            WHERE elementId(a) IN $ids OR elementId(b) IN $ids
            RETURN elementId(a)          AS source,
                   elementId(b)          AS target,
                   type(r)               AS rel_type,
                   r.action              AS action_prop,
                   properties(r)         AS props
            LIMIT {node_limit * 3}
        """, ids=node_ids)

        # Map action values → canonical relationship type labels
        ACTION_MAP = {
            "view":        "VIEWED",
            "click":       "CLICKED",
            "add_to_cart": "ADDED_TO_CART",
        }

        for rec in result2:
            rt = rec["rel_type"]
            # If DB has generic "ACTION" type, use the action property for the label
            if rt == "ACTION" and rec.get("action_prop"):
                rt = ACTION_MAP.get(rec["action_prop"], rec["action_prop"].upper())
            edges.append({
                "source":   rec["source"],
                "target":   rec["target"],
                "rel_type": rt,
                "props":    dict(rec["props"]) if rec["props"] else {},
            })

    driver.close()
    return {"nodes": nodes, "edges": edges}


def _neo4j_stats_direct() -> dict:
    """Get graph statistics directly from Neo4j."""
    from neo4j import GraphDatabase

    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD", "123456789")

    driver = GraphDatabase.driver(uri, auth=(user, pw))
    stats  = {}

    with driver.session() as s:
        queries = {
            "Users":         "MATCH (u:User)          RETURN count(u)  AS cnt",
            "Products":      "MATCH (p:Product)        RETURN count(p)  AS cnt",
            "Categories":    "MATCH (c:Category)       RETURN count(c)  AS cnt",
            "Devices":       "MATCH (d:Device)         RETURN count(d)  AS cnt",
            "VIEWED":        "MATCH ()-[r:VIEWED]->()        RETURN count(r) AS cnt",
            "CLICKED":       "MATCH ()-[r:CLICKED]->()       RETURN count(r) AS cnt",
            "ADDED_TO_CART": "MATCH ()-[r:ADDED_TO_CART]->() RETURN count(r) AS cnt",
            "IN_CATEGORY":   "MATCH ()-[r:IN_CATEGORY]->()   RETURN count(r) AS cnt",
            "USES_DEVICE":   "MATCH ()-[r:USES_DEVICE]->()   RETURN count(r) AS cnt",
        }
        for name, q in queries.items():
            try:
                result = s.run(q).single()
                stats[name] = result["cnt"]
            except Exception:
                stats[name] = 0

    driver.close()
    return stats


def _cypher_direct(query: str) -> list:
    """Run arbitrary Cypher and return list of dicts."""
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD", "123456789")
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    rows = []
    with driver.session() as s:
        result = s.run(query)
        rows = [dict(r) for r in result]
    driver.close()
    return rows


# ═══════════════════════════════════════════
# Pyvis graph builder
# ═══════════════════════════════════════════
def _make_node_id(raw) -> str:
    """Normalize Neo4j elementId (4:uuid:N) or int to a short unique string."""
    s = str(raw)
    # Neo4j 5 elementId format: "4:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:123"
    if ":" in s:
        return s.rsplit(":", 1)[-1]   # take the trailing number
    return s


def build_pyvis_graph(nodes_raw: list, edges_raw: list) -> str:
    try:
        from pyvis.network import Network

        net = Network(
            height="560px", width="100%",
            bgcolor="#0d0d1a", font_color="#e2e8f0",
            notebook=False, directed=True,
        )
        net.set_options("""{
          "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {"gravitationalConstant": -80, "springLength": 140, "springConstant": 0.05},
            "stabilization": {"iterations": 200}
          },
          "edges": {
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
            "smooth": {"type": "curvedCW", "roundness": 0.15},
            "font": {"size": 9, "color": "#e2e8f0"},
            "width": 1.4
          },
          "nodes": {"borderWidth": 2, "shadow": {"enabled": true}},
          "interaction": {"hover": true, "tooltipDelay": 100, "navigationButtons": true}
        }""")

        # Build: raw_id → short_id mapping
        raw_to_short = {}
        added_nodes  = set()

        for n in nodes_raw:
            raw_id = n["id"]
            nid    = _make_node_id(raw_id)
            raw_to_short[str(raw_id)] = nid

            label  = n.get("label", "Node")
            props  = n.get("props", {})
            color  = NODE_COLORS.get(label, "#8B5CF6")

            if label == "User":
                display = props.get("user_id", f"U{nid}")
                size    = 16 + min(int(props.get("total_sessions", 0)) // 8, 22)
            elif label == "Product":
                display = props.get("product_id", f"P{nid}")
                size    = 12 + min(int(props.get("popularity_score", 0)) // 25, 20)
            elif label == "Category":
                display = props.get("name", "Cat")
                size    = 32
            else:
                display = props.get("name", "Dev")
                size    = 20

            tooltip = f"[{label}]\n" + "\n".join(f"{k}: {v}" for k, v in props.items())

            if nid not in added_nodes:
                net.add_node(
                    nid, label=display,
                    color={"background": color, "border": color},
                    size=size, title=tooltip, shape="dot",
                    borderWidthSelected=4,
                    font={"color": "#f1f5f9", "size": 10, "bold": True},
                )
                added_nodes.add(nid)

        for e in edges_raw:
            src_raw = str(e.get("source", ""))
            dst_raw = str(e.get("target", ""))
            src = raw_to_short.get(src_raw, _make_node_id(src_raw))
            dst = raw_to_short.get(dst_raw, _make_node_id(dst_raw))
            rel = e.get("rel_type", "REL")
            color = EDGE_COLORS.get(rel, "#64748b")
            ep = e.get("props", {})
            tip = rel + ("\n" + "\n".join(f"{k}: {v}" for k, v in ep.items() if v) if ep else "")
            if src in added_nodes and dst in added_nodes:
                try:
                    net.add_edge(src, dst, label=rel,
                                 color={"color": color, "highlight": "#ffffff"},
                                 title=tip)
                except Exception:
                    pass

        return net.generate_html()

    except ImportError:
        return """<div style="text-align:center;padding:3rem;background:rgba(255,0,0,0.1);border-radius:12px;">
  <div style="font-size:2rem;">⚠️</div>
  <div style="color:#F87171;">pyvis not installed — Run: pip install pyvis</div>
</div>"""


# ═══════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════
def render_admin(token: str, catalog: dict):
    # Try API client (services running), fallback to direct
    def _try_api(fn_name, *args, **kwargs):
        try:
            from services.api_client import (
                run_cypher, get_graph_data, ai_stats, neo4j_status,
                create_product, update_product, delete_product, list_users,
            )
            fns = {
                "cypher": run_cypher, "graph": get_graph_data, "stats": ai_stats,
                "neo4j_status": neo4j_status, "create_product": create_product,
                "update_product": update_product, "delete_product": delete_product,
                "list_users": list_users,
            }
            return fns[fn_name](token, *args, **kwargs), True
        except Exception:
            return None, False

    st.markdown("""
<div class="fade-in">
  <div class="page-title">⚙️ Admin Dashboard</div>
  <div class="page-subtitle">Quan tri he thong — chi danh cho Administrator</div>
</div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Thong ke", "🛍️ Quan ly san pham",
        "🕸️ Graph DB Viewer", "👥 Quan ly Users",
    ])

    # ═══ TAB 1: STATS ════════════════════════
    with tab1:
        st.markdown("### 📊 Thong ke he thong")

        # Try AI service → fallback to CSV data → fallback to Neo4j
        stats_ok = False
        try:
            stats, ok = _try_api("stats")
            if ok and stats:
                c1, c2, c3 = st.columns(3)
                c1.metric("Users",    stats.get("total_users","—"))
                c1.metric("Products", stats.get("total_products","—"))
                c2.metric("Records",  f"{stats.get('total_records',0):,}")
                actions = stats.get("actions",{})
                c2.metric("Add to Cart", actions.get("add_to_cart","—"))
                devs = stats.get("devices",{})
                c3.metric("Mobile", devs.get("mobile","—"))
                c3.metric("Desktop", devs.get("desktop","—"))
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Hanh vi:**")
                    if actions: st.bar_chart(pd.DataFrame(actions.items(), columns=["Action","Count"]).set_index("Action"))
                with col_b:
                    st.markdown("**Category:**")
                    cats = stats.get("categories",{})
                    if cats: st.bar_chart(pd.DataFrame(cats.items(), columns=["Category","Count"]).set_index("Category"))
                stats_ok = True
        except Exception:
            pass

        if not stats_ok:
            # Fallback: read CSV directly
            try:
                data_path = os.path.join(_dir, "..", "..", "data", "data_user500.csv")
                if not os.path.exists(data_path):
                    data_path = os.path.join(_dir, "..", "..", "data_user500.csv")
                df = pd.read_csv(data_path)

                c1, c2, c3 = st.columns(3)
                c1.metric("Users",    int(df["user_id"].nunique()))
                c1.metric("Products", int(df["product_id"].nunique()))
                c2.metric("Records",  f"{len(df):,}")
                c2.metric("San pham catalog", len(catalog))
                devs = df["device"].value_counts()
                c3.metric("Mobile",  int(devs.get("mobile",0)))
                c3.metric("Desktop", int(devs.get("desktop",0)))

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Phan bo hanh vi:**")
                    acts = df["action"].value_counts()
                    st.bar_chart(pd.DataFrame({"Action":acts.index,"Count":acts.values}).set_index("Action"))
                with col_b:
                    st.markdown("**Phan bo Category:**")
                    cats = df["category"].value_counts()
                    st.bar_chart(pd.DataFrame({"Category":cats.index,"Count":cats.values}).set_index("Category"))
            except Exception as e:
                st.warning(f"Khong doc duoc du lieu: {e}")
                st.metric("Tong san pham catalog", len(catalog))

        # Neo4j Graph Stats
        st.markdown("---")
        st.markdown("**Thong ke Neo4j Knowledge Graph:**")
        try:
            ns = _neo4j_stats_direct()
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Users",    ns.get("Users",0))
            col2.metric("Products", ns.get("Products",0))
            col3.metric("VIEWED",        ns.get("VIEWED",0))
            col4.metric("CLICKED",       ns.get("CLICKED",0))
            col5.metric("ADD_TO_CART",   ns.get("ADDED_TO_CART",0))
        except Exception:
            st.info("Neo4j offline hoac chua import du lieu.")

    # ═══ TAB 2: PRODUCT CRUD ══════════════════
    with tab2:
        st.markdown("### 🛍️ Quan ly san pham")
        action_mode = st.radio("Chon thao tac:", ["Them san pham moi","Chinh sua san pham","Xoa san pham"],
                               horizontal=True, key="prod_action")

        if action_mode == "Them san pham moi":
            st.markdown("#### Them san pham moi")
            with st.form("add_product_form"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    p_name  = st.text_input("Ten san pham", placeholder="iPhone 16 Pro Max")
                    p_cat   = st.selectbox("Category", ["electronics","clothing","beauty","home"])
                    icons   = {"electronics":"💻","clothing":"👔","beauty":"💄","home":"🏠"}
                    p_emoji = icons.get(p_cat,"🛍️")
                with fc2:
                    p_price = st.number_input("Gia ($)", min_value=1.0, value=99.99, step=0.01)
                    p_stock = st.number_input("Ton kho", min_value=0, value=100, step=10)
                p_desc = st.text_area("Mo ta", placeholder="Mo ta ngan gon ve san pham...")

                if st.form_submit_button("Them san pham", use_container_width=True):
                    if not p_name:
                        st.error("Vui long nhap ten san pham.")
                    else:
                        new_data = {"name":p_name,"category":p_cat,"price":p_price,
                                    "stock":p_stock,"description":p_desc,"image_emoji":p_emoji}
                        result, ok = _try_api("create_product", new_data)
                        if ok:
                            st.success(f"Da them qua API: {result.get('product_id')} — {p_name}")
                        else:
                            new_id = f"P{len(catalog)+1:03d}"
                            catalog[new_id] = new_data
                            st.success(f"Da them (local): {new_id} — {p_name}")

        elif action_mode == "Chinh sua san pham":
            pid_list = list(catalog.keys())
            sel = st.selectbox("Chon san pham:", pid_list,
                               format_func=lambda x: f"{x} — {catalog[x]['name']}")
            prod = catalog.get(sel, {})
            with st.form("edit_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input("Ten", value=prod.get("name",""))
                    cats   = ["electronics","clothing","beauty","home"]
                    e_cat  = st.selectbox("Cat", cats, index=cats.index(prod.get("category","electronics")))
                with ec2:
                    e_price = st.number_input("Gia", value=float(prod.get("price",99.99)), step=0.01)
                    e_stock = st.number_input("Ton kho", value=int(prod.get("stock",100)), step=10)
                e_desc = st.text_area("Mo ta", value=prod.get("description",""))

                if st.form_submit_button("Luu thay doi", use_container_width=True):
                    upd = {"name":e_name,"price":e_price,"stock":e_stock,"description":e_desc}
                    _, ok = _try_api("update_product", sel, upd)
                    if not ok:
                        catalog[sel].update(upd)
                    st.success(f"Da cap nhat: {sel} — {e_name}")
                    st.rerun()

        else:
            pid_list = list(catalog.keys())
            del_pid = st.selectbox("Chon san pham can xoa:", pid_list,
                                   format_func=lambda x: f"{x} — {catalog[x]['name']}")
            if del_pid:
                info = catalog.get(del_pid,{})
                st.warning(f"Sap xoa: **{info.get('name')}** ({del_pid}) — ${info.get('price',0):.2f}")
                if st.button("Xac nhan xoa", key="confirm_del"):
                    _try_api("delete_product", del_pid)
                    catalog.pop(del_pid, None)
                    st.success(f"Da xoa: {del_pid}")
                    st.rerun()

        st.divider()
        st.markdown(f"**Tong san pham: {len(catalog)}**")
        rows = [{"ID":k,"Ten":v["name"],"Cat":v["category"],
                 "Gia":f"${v['price']:.2f}","Stock":v.get("stock","-")}
                for k,v in list(catalog.items())[:25]]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ═══ TAB 3: GRAPH DB VIEWER ═══════════════
    with tab3:
        st.markdown("### Neo4j Knowledge Base Graph")

        # Check connectivity
        is_online = False
        neo4j_uri = ""
        try:
            from neo4j import GraphDatabase
            uri  = os.getenv("NEO4J_URI","bolt://127.0.0.1:7687")
            user = os.getenv("NEO4J_USERNAME","neo4j")
            pw   = os.getenv("NEO4J_PASSWORD","123456789")
            drv  = GraphDatabase.driver(uri, auth=(user, pw))
            drv.verify_connectivity()
            drv.close()
            is_online = True
            neo4j_uri = uri
        except Exception:
            is_online = False

        dot_col = "#34D399" if is_online else "#F87171"
        label   = f"Neo4j Connected — {neo4j_uri}" if is_online else "Neo4j Offline"
        st.markdown(
            f'<div style="margin-bottom:1rem;">'
            f'<span style="color:{dot_col};font-size:1.1rem;">●</span> '
            f'<span style="color:#e2e8f0;">{label}</span></div>',
            unsafe_allow_html=True,
        )

        if is_online:
            gc1, gc2 = st.columns([3,1])
            with gc1:
                node_limit = st.slider("So nodes hien thi:", 20, 200, 80, step=20)
            with gc2:
                st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
                refresh = st.button("Tai lai Graph", use_container_width=True)

            st.markdown("""
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:0.8rem;font-size:0.78rem;
background:rgba(0,0,0,0.25);padding:0.6rem 1rem;border-radius:10px;">
  <span>🟣 <b>User</b></span>
  <span>🟡 <b>Product</b></span>
  <span>🟢 <b>Category</b></span>
  <span>🔵 <b>Device</b></span>
  &nbsp;|&nbsp;
  <span style="color:#94A3B8">─ VIEWED</span>
  <span style="color:#FBBF24">─ CLICKED</span>
  <span style="color:#34D399">─ ADDED_TO_CART</span>
  <span style="color:#10B981">─ IN_CATEGORY</span>
  <span style="color:#60A5FA">─ USES_DEVICE</span>
</div>""", unsafe_allow_html=True)

            if "graph_html" not in st.session_state or refresh:
                with st.spinner("Tai du lieu tu Neo4j..."):
                    try:
                        data = _load_graph_direct(node_limit)
                        st.session_state.graph_html   = build_pyvis_graph(data["nodes"], data["edges"])
                        st.session_state.graph_n_cnt  = len(data["nodes"])
                        st.session_state.graph_e_cnt  = len(data["edges"])
                    except Exception as ex:
                        st.error(f"Loi tai graph: {ex}")
                        st.session_state.graph_html  = ""
                        st.session_state.graph_n_cnt = 0
                        st.session_state.graph_e_cnt = 0

            m1, m2 = st.columns(2)
            m1.metric("Nodes", st.session_state.get("graph_n_cnt","—"))
            m2.metric("Edges", st.session_state.get("graph_e_cnt","—"))

            if st.session_state.get("graph_html"):
                st.components.v1.html(st.session_state.graph_html, height=580, scrolling=False)

            # ─ Cypher Console ─
            st.divider()
            st.markdown("#### Cypher Query Console")
            examples = [
                "MATCH (u:User)-[r:ADDED_TO_CART]->(p:Product) RETURN u.user_id, p.product_id, p.category LIMIT 10",
                "MATCH (p:Product)-[:IN_CATEGORY]->(c:Category) RETURN c.name, count(p) as total ORDER BY total DESC",
                "MATCH (u:User) WHERE u.add_to_cart_count > 3 RETURN u.user_id, u.add_to_cart_count ORDER BY u.add_to_cart_count DESC LIMIT 10",
                "MATCH (p:Product) RETURN p.product_id, p.popularity_score ORDER BY p.popularity_score DESC LIMIT 10",
                "CALL db.schema.visualization()",
                "MATCH (n) RETURN labels(n)[0] as type, count(*) as cnt ORDER BY cnt DESC",
            ]
            sel_ex = st.selectbox("Query mau:", ["-- tu nhap --"] + examples, label_visibility="collapsed")
            q_input = st.text_area(
                "Cypher:", value=sel_ex if sel_ex != "-- tu nhap --" else "",
                height=90, placeholder="MATCH (n) RETURN n LIMIT 10",
            )
            if st.button("Chay Query", key="run_cypher"):
                if q_input.strip():
                    with st.spinner("Dang query..."):
                        try:
                            rows = _cypher_direct(q_input.strip())
                            st.success(f"Ket qua: {len(rows)} dong")
                            if rows:
                                # Convert complex values to strings
                                flat = []
                                for r in rows:
                                    flat.append({k: str(v) if not isinstance(v,(str,int,float,bool,type(None))) else v
                                                 for k,v in r.items()})
                                st.dataframe(pd.DataFrame(flat), use_container_width=True)
                        except Exception as e2:
                            st.error(f"Query loi: {e2}")
        else:
            st.info("Khoi dong Neo4j truoc, sau do chay `python setup_neo4j.py` de import du lieu Graph.")
            st.code('docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/123456789 neo4j:5', language="bash")

    # ═══ TAB 4: USER MANAGEMENT ════════════════
    with tab4:
        st.markdown("### Quan ly Users")
        result, ok = _try_api("list_users")
        if ok and result:
            df_u = pd.DataFrame(result)
            if "password_hash" in df_u.columns:
                df_u = df_u.drop(columns=["password_hash"])
            st.dataframe(df_u, hide_index=True, use_container_width=True)
            st.metric("Tong tai khoan", len(result))
        else:
            # Show demo users
            st.info("Auth Service chua chay (Docker). Hien thi tai khoan demo.")
            demo = pd.DataFrame([
                {"Username":"admin","Ho ten":"Administrator","Email":"admin@shopai.vn","Quyen":"admin"},
                {"Username":"demo","Ho ten":"Demo User","Email":"demo@shopai.vn","Quyen":"user"},
            ])
            st.dataframe(demo, hide_index=True, use_container_width=True)
            st.markdown("""
> **Chay day du voi Docker:**
> ```
> docker-compose up
> ```
> Khi do Auth Service bat len co the quan ly users tu day du.
""")
