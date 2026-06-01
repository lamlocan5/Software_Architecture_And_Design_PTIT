"""
rag_logic.py - Cau 2c: RAG Chatbot dua tren KB_Graph Neo4j
Dung Gemini 2.5 Flash + LangChain + Neo4j GraphCypherQAChain
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER     = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "123456789")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================
# LAZY LOAD - khoi tao chain khi can
# ==========================================
_chain  = None
_graph  = None
_online = False   # True neu Neo4j ket noi duoc
_df     = None    # Fallback dataframe


def _load_dataframe():
    global _df
    if _df is None:
        try:
            _df = pd.read_csv("data_user500.csv")
        except Exception:
            _df = pd.DataFrame()
    return _df


def _init_chain():
    """Khoi tao RAG chain. Neu Neo4j offline -> dung fallback LLM-only."""
    global _chain, _graph, _online

    if _chain is not None:
        return

    # 1. Khoi tao Gemini LLM
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.2,
        )
    except Exception as e:
        print(f"[ERROR] Cannot initialize Gemini LLM: {e}")
        _chain = None
        return

    # 2. Thu ket noi Neo4j
    try:
        from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
        _graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD,
        )
        # Test ket noi
        _graph.query("RETURN 1 LIMIT 1")

        # 3. Tao chain voi system prompt tuy chinh
        _chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=_graph,
            verbose=True,
            allow_dangerous_requests=True,
            cypher_prompt=_build_cypher_prompt(),
        )
        _online = True
        print("[OK] RAG Chain initialized with Neo4j")

    except Exception as e:
        print(f"[WARN] Neo4j offline: {e}. Switching to LLM-only fallback.")
        # Fallback: chi dung LLM + context tu CSV
        _chain = llm
        _online = False


def _build_cypher_prompt():
    """System prompt giup LLM viet Cypher query chinh xac hon"""
    from langchain_core.prompts import PromptTemplate

    CYPHER_GENERATION_TEMPLATE = """You are an expert in E-commerce systems and Neo4j Cypher queries.
Answer in Vietnamese.

Graph Schema:
- Nodes: (:User {user_id, total_sessions, view_count, click_count, add_to_cart_count, avg_session, favorite_device, favorite_category})
- Nodes: (:Product {product_id, category, avg_price, view_count, popularity_score})
- Nodes: (:Category {name}) - values: clothing, home, beauty, electronics
- Nodes: (:Device {name}) - values: mobile, tablet, desktop
- Relationships: (User)-[:VIEWED {timestamp, device, session_duration, price}]->(Product)
- Relationships: (User)-[:CLICKED {timestamp, device, session_duration, price}]->(Product)
- Relationships: (User)-[:ADDED_TO_CART {timestamp, device, session_duration, price}]->(Product)
- Relationships: (Product)-[:IN_CATEGORY]->(Category)
- Relationships: (User)-[:USES_DEVICE]->(Device)

Example questions and Cypher:
1. "San pham pho bien nhat?"
   -> MATCH (p:Product) RETURN p.product_id, p.popularity_score ORDER BY p.popularity_score DESC LIMIT 5

2. "User U001 da xem nhung san pham nao?"
   -> MATCH (u:User {{user_id: 'U001'}})-[:VIEWED]->(p:Product) RETURN p.product_id, p.category LIMIT 10

3. "Goi y san pham cho U001"
   -> MATCH (u:User {{user_id: 'U001'}})-[:CLICKED|VIEWED]->(p:Product) RETURN p.product_id, p.category, p.avg_price ORDER BY p.popularity_score DESC LIMIT 5

4. "Category nao duoc mua nhieu nhat?"
   -> MATCH ()-[r:ADDED_TO_CART]->(p:Product)-[:IN_CATEGORY]->(c:Category) RETURN c.name, count(r) as mua ORDER BY mua DESC

Write a valid Cypher query for the following question. Return only the Cypher query, no explanation.

Question: {question}
Cypher query:"""

    return PromptTemplate(
        input_variables=["question"],
        template=CYPHER_GENERATION_TEMPLATE,
    )


# ==========================================
# FALLBACK - LLM-ONLY (khi Neo4j offline)
# ==========================================
def _ask_llm_only(question: str) -> str:
    """Tra loi dung LLM + du lieu CSV (khong can Neo4j)"""
    df = _load_dataframe()

    if df.empty:
        context = "No data available."
    else:
        total_users    = df["user_id"].nunique()
        total_products = df["product_id"].nunique()
        categories     = df["category"].unique().tolist()
        top_products   = (
            df.groupby("product_id").size()
            .nlargest(5)
            .reset_index(name="count")
            .to_string(index=False)
        )
        context = (
            f"E-Commerce AI system data:\n"
            f"- {total_users} users, {total_products} products\n"
            f"- Categories: {categories}\n"
            f"- Top 5 most interacted products:\n{top_products}"
        )

    try:
        prompt = (
            "Ban la AI assistant cho he thong E-commerce Viet Nam.\n"
            "Hay tra loi bang tieng Viet, ngan gon va huu ich.\n\n"
            f"Du lieu context:\n{context}\n\n"
            f"Cau hoi: {question}\n\nTra loi:"
        )
        response = _chain.invoke(prompt)
        if hasattr(response, "content"):
            return response.content
        return str(response)
    except Exception as e:
        return f"Xin loi, co loi khi xu ly cau hoi: {e}"


# ==========================================
# PUBLIC API
# ==========================================
def ask_ai(question: str) -> str:
    """
    Hoi AI ve du lieu e-commerce.
    - Neu Neo4j online: dung GraphCypherQAChain (RAG thuc su)
    - Neu Neo4j offline: dung LLM + context tu CSV (fallback)
    Returns: string tra loi cua AI
    """
    _init_chain()

    if _chain is None:
        return "He thong AI chua san sang. Vui long kiem tra GEMINI_API_KEY trong file .env"

    if not _online:
        return _ask_llm_only(question)

    try:
        result = _chain.invoke({"query": question})
        answer = result.get("result", "Khong tim thay cau tra loi phu hop.")
        return answer if answer else "Toi khong tim thay thong tin phu hop trong co so du lieu."
    except Exception as e:
        print(f"[WARN] RAG query error: {e}. Falling back to LLM-only.")
        return _ask_llm_only(question)


def get_neo4j_status() -> dict:
    """Kiem tra trang thai ket noi Neo4j"""
    _init_chain()
    return {
        "online":       _online,
        "uri":          NEO4J_URI,
        "has_api_key":  bool(GEMINI_API_KEY),
    }


def get_graph_recommendations(user_id: str, top_n: int = 5) -> list:
    """
    Lay recommendations tu KB_Graph cho user cu the.
    Returns: list of dict [{"product_id": ..., "category": ..., "score": ...}]
    """
    _init_chain()

    if not _online or _graph is None:
        return []

    try:
        query = f"""
        MATCH (u:User {{user_id: '{user_id}'}})-[r:CLICKED|VIEWED]->(p:Product)
        WITH p, count(r) as interactions
        ORDER BY interactions DESC
        RETURN p.product_id as product_id, p.category as category,
               p.avg_price as avg_price, p.popularity_score as score
        LIMIT {top_n}
        """
        results = _graph.query(query)
        return results
    except Exception as e:
        print(f"[WARN] Graph query error: {e}")
        return []
