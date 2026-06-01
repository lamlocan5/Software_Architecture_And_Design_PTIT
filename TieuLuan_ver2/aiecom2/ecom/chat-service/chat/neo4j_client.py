"""
chat-service/chat/neo4j_client.py
Truy vấn Neo4j Knowledge Graph.
"""
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            _driver.verify_connectivity()
        except Exception as e:
            print(f"[Chat/Neo4j] Lỗi kết nối: {e}")
    return _driver


def get_user_top_products(user_id, limit=5):
    driver = get_driver()
    if not driver:
        return []
    query = """
    MATCH (u:User {id: $user_id})-[r]->(p:Product)
    WITH p, SUM(CASE type(r) WHEN 'ADD_TO_CART' THEN 3 WHEN 'CLICK' THEN 2 ELSE 1 END) AS score
    RETURN p.id AS product_id, p.name AS name, score
    ORDER BY score DESC LIMIT $limit
    """
    try:
        with driver.session() as s:
            return [dict(r) for r in s.run(query, user_id=user_id, limit=limit)]
    except Exception as e:
        print(f"[Chat/Neo4j] Lỗi: {e}")
        return []


def get_popular_products(limit=8):
    driver = get_driver()
    if not driver:
        return []
    query = """
    MATCH (u:User)-[r]->(p:Product)
    WITH p, SUM(CASE type(r) WHEN 'ADD_TO_CART' THEN 3 WHEN 'CLICK' THEN 2 ELSE 1 END) AS score,
         COUNT(DISTINCT u) AS unique_users
    RETURN p.id AS product_id, p.name AS name, score, unique_users
    ORDER BY score DESC LIMIT $limit
    """
    try:
        with driver.session() as s:
            return [dict(r) for r in s.run(query, limit=limit)]
    except Exception as e:
        print(f"[Chat/Neo4j] Lỗi: {e}")
        return []


def get_similar_products(product_id, limit=5):
    driver = get_driver()
    if not driver:
        return []
    query = """
    MATCH (u:User)-[]->(p:Product {id: $product_id})
    MATCH (u)-[]->(other:Product)
    WHERE other.id <> $product_id
    WITH other, COUNT(DISTINCT u) AS common_users
    RETURN other.id AS product_id, other.name AS name, common_users
    ORDER BY common_users DESC LIMIT $limit
    """
    try:
        with driver.session() as s:
            return [dict(r) for r in s.run(query, product_id=product_id, limit=limit)]
    except Exception as e:
        print(f"[Chat/Neo4j] Lỗi: {e}")
        return []
