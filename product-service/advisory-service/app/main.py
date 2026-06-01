from __future__ import annotations

import logging
import time

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import behavior, features, rag
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TechStore Advisory", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    token: str | None = Field(None, description="Token khách (tùy chọn) để cá nhân hóa mô hình hành vi")


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    behavior_label: str | None = None
    behavior_features: dict | None = None


class PredictRequest(BaseModel):
    token: str


def _behavior_hint_text(label: str | None) -> str:
    if not label:
        return ""
    m = {
        "laptop": "bạn có xu hướng quan tâm nhiều tới laptop / máy tính xách tay",
        "mobile": "bạn có xu hướng quan tâm nhiều tới điện thoại di động",
        "both": "bạn có xu hướng quan tâm tới cả laptop và điện thoại",
    }
    return m.get(label.lower(), f"xu hướng nhóm «{label}»")


def _compose_answer_without_llm(question: str, contexts: list[tuple[str, str]], behavior_label: str | None) -> str:
    lines: list[str] = [
        "### Trả lời tư vấn (RAG)",
        "",
        "Dưới đây là nội dung trích từ knowledge base của cửa hàng, bạn có thể tham khảo:",
        "",
    ]
    for i, (doc, src) in enumerate(contexts, 1):
        ref = f" ({src})" if src else ""
        lines.append(f"**{i}.**{ref}\n{doc}\n")

    if behavior_label:
        lines.extend(
            [
                "---",
                "**Gợi ý cá nhân hóa (mô hình hành vi):**",
                _behavior_hint_text(behavior_label),
                "",
            ]
        )
    lines.append(
        "*Đặt **GEMINI_API_KEY** (Google AI Studio) hoặc **OPENAI_API_KEY** để có câu trả lời diễn đạt tự nhiên hơn.*"
    )
    return "\n".join(lines)


def _gemini_parse_response(data: dict) -> str | None:
    cands = data.get("candidates") or []
    if not cands:
        logger.warning("Gemini không trả candidate: %s", data)
        return None
    parts = (cands[0].get("content") or {}).get("parts") or []
    texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
    text = "".join(texts).strip()
    return text or None


def _gemini_post(model_name: str, key: str, payload: dict) -> requests.Response:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    last: requests.Response | None = None
    for attempt in range(2):
        r = requests.post(url, params={"key": key}, json=payload, timeout=90)
        last = r
        if r.status_code == 429 and attempt == 0:
            logger.warning("Gemini model=%s: 429 — chờ rồi thử lại (quota).", model_name)
            time.sleep(5)
            continue
        return r
    assert last is not None
    return last


def _gemini_answer(question: str, contexts: list[tuple[str, str]], behavior_label: str | None) -> str | None:
    key = (settings.gemini_api_key or "").strip()
    if not key:
        return None

    ctx = "\n\n".join(f"[{src or 'KB'}]\n{doc}" for doc, src in contexts[:6])
    hint = ""
    if behavior_label:
        hint = (
            f"\nGợi ý phân nhóm hành vi khách (chỉ gợi ý, không bắt buộc nhắc nếu không liên quan): "
            f"{_behavior_hint_text(behavior_label)}.\n"
        )

    system = (
        "Bạn là tư vấn viên TechStore (laptop & điện thoại). Trả lời tiếng Việt, ngắn gọn, chính xác. "
        "Chỉ dựa vào ngữ cảnh được cung cấp; nếu không đủ thông tin, nói rõ và gợi ý liên hệ nhân viên. "
        "Không bịa thông số không có trong ngữ cảnh."
    )
    user = f"Câu hỏi khách: {question}\n\nNgữ cảnh từ KB:\n{ctx}\n{hint}"

    gen_cfg = {"temperature": 0.4, "maxOutputTokens": 1024}
    primary = (settings.gemini_model or "gemini-2.5-flash").strip()
    fallback_model = (settings.gemini_model_fallback or "gemini-flash-latest").strip()
    # Thêm model thường còn quota khi 2.0-flash hết free tier hoặc 1.5-* 404 trên API mới
    extra_try = ("gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite")
    models_order: list[str] = []
    for m in (primary, fallback_model, *extra_try):
        if m and m not in models_order:
            models_order.append(m)

    try:
        for model_name in models_order:
            # 1) API chuẩn: systemInstruction
            payload_sys = {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": gen_cfg,
            }
            r = _gemini_post(model_name, key, payload_sys)
            if r.status_code == 200:
                return _gemini_parse_response(r.json())
            logger.warning(
                "Gemini model=%s (systemInstruction) HTTP %s — %s",
                model_name,
                r.status_code,
                (r.text or "")[:500],
            )

            # 2) Fallback: gộp system + user (một số key/model lỗi format 400)
            merged = f"{system}\n\n{user}"
            payload_plain = {
                "contents": [{"role": "user", "parts": [{"text": merged}]}],
                "generationConfig": gen_cfg,
            }
            r2 = _gemini_post(model_name, key, payload_plain)
            if r2.status_code == 200:
                return _gemini_parse_response(r2.json())
            logger.warning(
                "Gemini model=%s (merged prompt) HTTP %s — %s",
                model_name,
                r2.status_code,
                (r2.text or "")[:500],
            )

        return None
    except Exception as exc:
        msg = str(exc).split("?key=")[0] if "?key=" in str(exc) else str(exc)
        logger.warning("Gemini lỗi: %s", msg[:200])
        return None


def _openai_answer(question: str, contexts: list[tuple[str, str]], behavior_label: str | None) -> str | None:
    key = (settings.openai_api_key or "").strip()
    if not key:
        return None

    ctx = "\n\n".join(f"[{src or 'KB'}]\n{doc}" for doc, src in contexts[:6])
    hint = ""
    if behavior_label:
        hint = f"\nGợi ý phân nhóm hành vi khách (chỉ là gợi ý, không bắt buộc nhắc nếu không liên quan): {_behavior_hint_text(behavior_label)}.\n"

    system = (
        "Bạn là tư vấn viên TechStore (laptop & điện thoại). Trả lời tiếng Việt, ngắn gọn, chính xác. "
        "Chỉ dựa vào ngữ cảnh được cung cấp; nếu không đủ thông tin, nói rõ và gợi ý liên hệ nhân viên. "
        "Không bịa thông số không có trong ngữ cảnh."
    )
    user = f"Câu hỏi khách: {question}\n\nNgữ cảnh từ KB:\n{ctx}\n{hint}"

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.4,
                "max_tokens": 900,
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning("OpenAI lỗi: %s", exc)
        return None


def _llm_answer(question: str, contexts: list[tuple[str, str]], behavior_label: str | None) -> str | None:
    """Ưu tiên Gemini (AI Studio), sau đó OpenAI."""
    out = _gemini_answer(question, contexts, behavior_label)
    if out:
        return out
    return _openai_answer(question, contexts, behavior_label)


@app.on_event("startup")
def startup():
    rag.get_collection()
    if not (settings.gemini_api_key or "").strip() and not (settings.openai_api_key or "").strip():
        logger.warning(
            "Chưa có GEMINI_API_KEY / OPENAI_API_KEY trong biến môi trường — chỉ trả trích dẫn KB (kiểm tra docker-compose + file .env ở host)."
        )


@app.get("/health")
def health():
    gk = bool((settings.gemini_api_key or "").strip())
    ok = bool((settings.openai_api_key or "").strip())
    return {
        "status": "ok",
        "kb_chunks": rag.get_collection().count(),
        "behavior_model": behavior.artifacts_present(),
        "gemini_configured": gk,
        "gemini_model": settings.gemini_model,
        "gemini_model_fallback": settings.gemini_model_fallback,
        "openai_configured": ok,
    }


@app.post("/reindex-kb")
def reindex_kb():
    n = rag.reindex()
    return {"indexed_chunks": n}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    q = req.message.strip()
    hits = rag.retrieve(q, k=5)
    sources = [{"text": t[:280] + ("…" if len(t) > 280 else ""), "source": s} for t, s in hits]

    feat_row = None
    bh = None
    if req.token:
        feat_row = features.build_feature_row(req.token)
        if feat_row is not None:
            bh = behavior.predict_label(feat_row)

    llm = _llm_answer(q, hits, bh)
    answer = llm if llm else _compose_answer_without_llm(q, hits, bh)
    return ChatResponse(
        answer=answer,
        sources=sources,
        behavior_label=bh,
        behavior_features=feat_row,
    )


@app.post("/predict-behavior")
def predict_behavior(req: PredictRequest):
    row = features.build_feature_row(req.token)
    if row is None:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")
    label = behavior.predict_label(row)
    return {"label": label, "features": row}
