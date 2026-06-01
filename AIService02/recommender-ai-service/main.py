"""
recommender-ai-service/main.py
FastAPI :8004 — AI Recommendations, DL Prediction, RAG Chat, Neo4j Admin
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import jwt, os, pandas as pd

app = FastAPI(title="Recommender AI Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY  = os.getenv("JWT_SECRET", "shopai-secret-2026")
DATA_PATH   = os.getenv("DATA_PATH",  "../data/data_user500.csv")
MODEL_PATH  = os.getenv("MODEL_PATH", "../models/model_best.keras")

_df = None
def get_df():
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH)
    return _df


# ── Auth helpers ──
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
class PredictRequest(BaseModel):
    device:           str = "mobile"
    category:         str = "electronics"
    session_duration: int = 300
    price:           float = 100.0
    user_id:          str = "U001"
    product_id:       str = "P001"

class ChatRequest(BaseModel):
    question: str

class CypherRequest(BaseModel):
    query: str


# ── Routes ──
@app.get("/health")
def health(): return {"status": "UP", "service": "recommender-ai-service"}

@app.post("/predict")
def predict(req: PredictRequest, user: dict = Depends(get_current_user)):
    try:
        import sys, os; sys.path.insert(0, os.path.dirname(__file__))
        from predict_logic import predict_next_action
        result = predict_next_action(
            device=req.device, category=req.category,
            session_duration=req.session_duration, price=req.price,
            user_id=req.user_id, product_id=req.product_id,
        )
        return result
    except Exception as e:
        return {"predicted_action": "view", "confidence": 0.5, "using_model": False, "error": str(e)}

@app.get("/recommend/{user_id}")
def recommend(user_id: str, top_n: int = 5, user: dict = Depends(get_current_user)):
    try:
        from predict_logic import get_top_products_for_user
        df   = get_df()
        recs = get_top_products_for_user(df, user_id, top_n)
        return {"recommendations": recs.to_dict(orient="records")}
    except Exception as e:
        return {"recommendations": [], "error": str(e)}

@app.get("/popular")
def popular(top_n: int = 10, user: dict = Depends(get_current_user)):
    try:
        from predict_logic import get_popular_products
        df    = get_df()
        items = get_popular_products(df, top_n)
        return {"products": items.to_dict(orient="records")}
    except Exception as e:
        return {"products": [], "error": str(e)}

@app.post("/chat")
def chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    try:
        from rag_logic import ask_ai
        answer = ask_ai(req.question)
        return {"answer": answer, "question": req.question}
    except Exception as e:
        return {"answer": f"Error: {e}", "question": req.question}

@app.get("/neo4j/status")
def neo4j_status(user: dict = Depends(get_current_user)):
    try:
        from rag_logic import get_neo4j_status
        return get_neo4j_status()
    except Exception as e:
        return {"online": False, "error": str(e)}

@app.post("/admin/cypher")
def run_cypher(req: CypherRequest, user: dict = Depends(require_admin)):
    """Admin only: run arbitrary Cypher query on Neo4j"""
    try:
        from rag_logic import _graph, _init_chain
        _init_chain()
        if _graph is None:
            raise HTTPException(status_code=503, detail="Neo4j not connected")
        results = _graph.query(req.query)
        return {"results": results, "count": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/graph-data")
def graph_data(limit: int = 100, user: dict = Depends(require_admin)):
    """Return nodes + edges for graph visualization"""
    try:
        from rag_logic import _graph, _init_chain, _online
        _init_chain()
        if not _online or _graph is None:
            raise HTTPException(status_code=503, detail="Neo4j not connected")

        nodes_raw = _graph.query(f"""
            MATCH (n) RETURN 
            id(n) as id,
            labels(n)[0] as label,
            properties(n) as props
            LIMIT {limit}
        """)
        edges_raw = _graph.query(f"""
            MATCH (a)-[r]->(b)
            RETURN id(a) as source, id(b) as target, type(r) as rel_type
            LIMIT {limit * 2}
        """)
        return {"nodes": nodes_raw, "edges": edges_raw}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def stats(user: dict = Depends(get_current_user)):
    df = get_df()
    return {
        "total_users":    int(df["user_id"].nunique()),
        "total_products": int(df["product_id"].nunique()),
        "total_records":  int(len(df)),
        "actions": df["action"].value_counts().to_dict(),
        "categories": df["category"].value_counts().to_dict(),
        "devices": df["device"].value_counts().to_dict(),
    }
