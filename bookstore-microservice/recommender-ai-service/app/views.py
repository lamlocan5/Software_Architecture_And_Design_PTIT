import os
import re
from typing import Any

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def _fallback_recommendations(books: list[dict[str, Any]], limit: int) -> list[int]:
    def score(b: dict[str, Any]) -> tuple:
        stock = int(b.get("stock") or 0)
        avg = float(b.get("avg_rating") or 0)
        cnt = int(b.get("total_reviews") or 0)
        # prefer in-stock, then avg rating, then review count
        return (stock > 0, avg, cnt)

    ordered = sorted(books, key=score, reverse=True)
    ids: list[int] = []
    for b in ordered:
        try:
            ids.append(int(b.get("id")))
        except Exception:
            continue
        if len(ids) >= limit:
            break
    return ids


def _call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    r = requests.post(
        url,
        params={"key": api_key},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512},
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )
    return text or ""


def _extract_ids(text: str) -> list[int]:
    # Accept either JSON list, or text containing ids.
    # Extract up to 20 integers.
    ids = []
    for m in re.finditer(r"\b\d+\b", text):
        ids.append(int(m.group(0)))
        if len(ids) >= 20:
            break
    return ids


class Recommendations(APIView):
    """
    POST /recommendations/
    Body: { books: [...], limit: 6, context: "home"|"catalogue" }
    Returns: { recommended_ids: [...], source: "gemini"|"fallback", raw?: "..." }
    """

    def post(self, request):
        books = request.data.get("books") or []
        limit = request.data.get("limit") or 6
        context = (request.data.get("context") or "home").strip()

        try:
            limit = int(limit)
        except Exception:
            limit = 6
        limit = max(1, min(limit, 12))

        if not isinstance(books, list) or not books:
            return Response({"error": "books list is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Reduce payload to keep prompt small
        compact = []
        for b in books[:50]:
            if not isinstance(b, dict):
                continue
            compact.append(
                {
                    "id": b.get("id"),
                    "title": b.get("title"),
                    "author": b.get("author"),
                    "price": b.get("price"),
                    "stock": b.get("stock"),
                    "publisher": (b.get("publisher_detail") or {}).get("name") if isinstance(b.get("publisher_detail"), dict) else None,
                    "avg_rating": b.get("avg_rating", 0),
                    "total_reviews": b.get("total_reviews", 0),
                }
            )

        prompt = (
            "Bạn là hệ thống gợi ý sách cho bookstore. "
            "Chỉ trả về danh sách ID sách dạng JSON array, ví dụ: [12,5,9]. "
            f"Bối cảnh: {context}. "
            "Ưu tiên sách còn hàng (stock>0), rating cao, nhiều review, giá hợp lý, đa dạng tác giả/NXB. "
            f"Chọn đúng {limit} ID từ danh sách dưới đây, không bịa.\n\n"
            f"Danh sách sách (JSON): {compact}"
        )

        try:
            raw = _call_gemini(prompt)
            ids = _extract_ids(raw)
            allowed = {int(b.get("id")) for b in compact if str(b.get("id")).isdigit()}
            ids = [i for i in ids if i in allowed]
            # de-dup preserving order
            seen = set()
            filtered = []
            for i in ids:
                if i in seen:
                    continue
                seen.add(i)
                filtered.append(i)
                if len(filtered) >= limit:
                    break
            if len(filtered) >= 1:
                return Response({"recommended_ids": filtered, "source": "gemini"})
        except Exception:
            pass

        fallback = _fallback_recommendations(compact, limit)
        return Response({"recommended_ids": fallback, "source": "fallback"})

