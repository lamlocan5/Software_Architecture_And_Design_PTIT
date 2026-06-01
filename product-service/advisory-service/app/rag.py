from __future__ import annotations

import hashlib
import logging

import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

logger = logging.getLogger(__name__)

_COLLECTION = None


def _chunks_from_markdown(text: str, max_chars: int = 700) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        extra = len(block) + (2 if buf else 0)
        if size + extra > max_chars and buf:
            parts.append("\n\n".join(buf))
            buf = [block]
            size = len(block)
        else:
            buf.append(block)
            size += extra
    if buf:
        parts.append("\n\n".join(buf))
    return parts


def _load_kb_documents() -> tuple[list[str], list[str], list[dict]]:
    docs: list[str] = []
    ids: list[str] = []
    metas: list[dict] = []
    kb_dir = settings.kb_dir
    if not kb_dir.is_dir():
        logger.warning("Thư mục KB không tồn tại: %s", kb_dir)
        return docs, ids, metas

    for path in sorted(kb_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(_chunks_from_markdown(text)):
            h = hashlib.md5(f"{path.name}:{i}:{chunk[:120]}".encode()).hexdigest()[:16]
            ids.append(f"{path.stem}_{i}_{h}")
            docs.append(chunk)
            metas.append({"source": path.name})
    return docs, ids, metas


def get_collection():
    global _COLLECTION
    if _COLLECTION is not None:
        return _COLLECTION

    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    collection = client.get_or_create_collection(name="advisory_kb", embedding_function=ef)

    if collection.count() == 0:
        docs, ids, metas = _load_kb_documents()
        if docs:
            batch = 80
            for start in range(0, len(docs), batch):
                collection.add(
                    documents=docs[start : start + batch],
                    ids=ids[start : start + batch],
                    metadatas=metas[start : start + batch],
                )
            logger.info("Đã index %s đoạn KB vào Chroma.", len(docs))
        else:
            logger.warning("Không có tài liệu KB để index.")

    _COLLECTION = collection
    return collection


def retrieve(query: str, k: int = 5) -> list[tuple[str, str]]:
    col = get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[query], n_results=min(k, max(1, col.count())))
    out: list[tuple[str, str]] = []
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    for doc, meta in zip(docs, metas):
        src = ""
        if isinstance(meta, dict):
            src = str(meta.get("source", ""))
        out.append((doc, src))
    return out


def reindex() -> int:
    """Xóa collection và index lại (tiện khi đổi file KB)."""
    global _COLLECTION
    _COLLECTION = None
    if settings.chroma_dir.exists():
        import shutil

        shutil.rmtree(settings.chroma_dir, ignore_errors=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    get_collection()
    return get_collection().count()
