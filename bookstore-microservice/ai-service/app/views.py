import os
import re
from typing import Any
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.models import UserBehavior
from app.graph_engine import Neo4jGraphEngine
from app.hybrid_scorer import get_hybrid_recommendations
from app.rag_engine import RAGEngine


# ──────────────────────────────── NEW API VIEWS ────────────────────────────────

class BehaviorLogView(APIView):
    """
    POST /behavior/
    Body: { "user_id": 7, "product_id": 1, "behavior_type": "view"|"buy"|"cart" }
    """
    def post(self, request):
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        behavior_type = request.data.get("behavior_type")

        if user_id is None or product_id is None or not behavior_type:
            return Response(
                {"error": "user_id, product_id, and behavior_type are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = int(user_id)
            product_id = int(product_id)
            behavior_type = str(behavior_type).strip().lower()
        except ValueError:
            return Response(
                {"error": "user_id and product_id must be integers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Save to PostgreSQL database
        try:
            behavior = UserBehavior.objects.create(
                user_id=user_id,
                product_id=product_id,
                behavior_type=behavior_type
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to save behavior to database: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 2. Synchronize behavior to Neo4j graph
        graph = None
        try:
            graph = Neo4jGraphEngine()
            graph.sync_behavior(user_id, product_id, behavior_type)
        except Exception as e:
            print(f"Non-blocking error syncing to Neo4j: {e}")
        finally:
            if graph:
                graph.close()

        return Response(
            {"status": "success", "message": "Behavior logged successfully", "id": behavior.id},
            status=status.HTTP_201_CREATED
        )


class RecommendView(APIView):
    """
    GET /recommend/?user_id=...&limit=6
    """
    def get(self, request):
        user_id_raw = request.query_params.get("user_id")
        limit_raw = request.query_params.get("limit", "6")

        if not user_id_raw:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = int(user_id_raw)
            limit = int(limit_raw)
        except ValueError:
            return Response(
                {"error": "user_id and limit must be valid integers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recommended_ids = get_hybrid_recommendations(user_id, limit)
            return Response({
                "user_id": user_id,
                "recommended_ids": recommended_ids,
                "source": "hybrid"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to compute hybrid recommendations: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatbotView(APIView):
    """
    POST /chatbot/
    Body: { "query": "Your message here..." }
    """
    def post(self, request):
        query = request.data.get("query")
        if not query or not str(query).strip():
            return Response(
                {"error": "query field is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rag = RAGEngine.get_instance()
            response_text = rag.generate_chatbot_answer(query)
            return Response({
                "response": response_text
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Chatbot generation error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ────────────────────────────── LEGACY COMPATIBILITY VIEW ──────────────────────────────

def _fallback_recommendations(books: list[dict[str, Any]], limit: int) -> list[int]:
    def score(b: dict[str, Any]) -> tuple:
        stock = int(b.get("stock") or 0)
        avg = float(b.get("avg_rating") or 0)
        cnt = int(b.get("total_reviews") or 0)
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

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    r = requests.post(
        url,
        params={"key": api_key},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
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


class GraphDataView(APIView):
    """
    GET /graph/
    Retrieve Neo4j graph nodes, relationships, and stats.
    """
    def get(self, request):
        graph = None
        try:
            graph = Neo4jGraphEngine()
            if not graph.driver:
                return Response(
                    {"error": "Failed to connect to Neo4j database"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            node_stats = []
            rel_stats = []
            nodes = []
            relationships = []

            with graph.driver.session() as session:
                # 1. Fetch node stats
                node_stats_result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
                for row in node_stats_result:
                    node_stats.append({
                        "label": row["label"] or "Unknown",
                        "count": row["count"]
                    })

                # 2. Fetch relationship stats
                rel_stats_result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
                for row in rel_stats_result:
                    rel_stats.append({
                        "type": row["type"],
                        "count": row["count"]
                    })

                # 3. Fetch nodes (limit to 150)
                nodes_result = session.run("MATCH (n) RETURN labels(n)[0] AS label, n.id AS id, properties(n) AS properties LIMIT 150")
                for row in nodes_result:
                    nodes.append({
                        "label": row["label"] or "Unknown",
                        "id": row["id"],
                        "properties": row["properties"]
                    })

                # 4. Fetch relationships (limit to 150)
                rels_result = session.run("MATCH (n)-[r]->(m) RETURN type(r) AS type, n.id AS source, m.id AS target, properties(r) AS properties LIMIT 150")
                for row in rels_result:
                    relationships.append({
                        "type": row["type"],
                        "source": row["source"],
                        "target": row["target"],
                        "properties": row["properties"]
                    })

            return Response({
                "node_stats": node_stats,
                "relationship_stats": rel_stats,
                "nodes": nodes,
                "relationships": relationships
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Error querying Neo4j: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if graph:
                graph.close()

