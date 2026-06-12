import os
from neo4j import GraphDatabase

class Neo4jGraphEngine:
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        username = os.environ.get("NEO4J_USERNAME", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password123")
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
        except Exception as e:
            print(f"Error initializing Neo4j driver: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def sync_behavior(self, user_id, product_id, behavior_type):
        """
        Merge User and Product nodes, and create a VIEW or BUY relationship between them.
        """
        if not self.driver:
            return False

        btype = behavior_type.lower()
        if btype == 'buy':
            query = """
            MERGE (u:User {id: $uid})
            MERGE (p:Product {id: $pid})
            MERGE (u)-[r:BUY]->(p)
            ON CREATE SET r.timestamp = timestamp()
            RETURN r
            """
        else:
            query = """
            MERGE (u:User {id: $uid})
            MERGE (p:Product {id: $pid})
            MERGE (u)-[r:VIEW]->(p)
            ON CREATE SET r.timestamp = timestamp()
            RETURN r
            """

        try:
            with self.driver.session() as session:
                session.run(query, uid=int(user_id), pid=int(product_id))
            return True
        except Exception as e:
            print(f"Error syncing behavior to Neo4j: {e}")
            return False

    def sync_similarity(self, product_id_1, product_id_2, score):
        """
        Create a SIMILAR relationship between two products.
        """
        if not self.driver:
            return False

        query = """
        MERGE (p1:Product {id: $pid1})
        MERGE (p2:Product {id: $pid2})
        MERGE (p1)-[r:SIMILAR]->(p2)
        SET r.score = $score
        RETURN r
        """
        try:
            with self.driver.session() as session:
                session.run(query, pid1=int(product_id_1), pid2=int(product_id_2), score=float(score))
            return True
        except Exception as e:
            print(f"Error syncing similarity to Neo4j: {e}")
            return False

    def get_collaborative_recommendations(self, user_id, limit=10):
        """
        Find products bought by other users who also bought the same items.
        """
        if not self.driver:
            return []

        query = """
        MATCH (u1:User {id: $uid})-[:BUY]->(p:Product)<-[:BUY]-(u2:User)-[:BUY]->(rec:Product)
        WHERE NOT (u1)-[:BUY|VIEW]->(rec) AND rec.id <> p.id
        RETURN rec.id AS product_id, count(u2) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, uid=int(user_id), limit=int(limit))
                return [(row["product_id"], float(row["score"])) for row in result]
        except Exception as e:
            print(f"Error fetching collab recommendations: {e}")
            return []

    def get_similar_recommendations(self, user_id, limit=10):
        """
        Find products similar to products the user has already bought or viewed.
        """
        if not self.driver:
            return []

        query = """
        MATCH (u:User {id: $uid})-[:VIEW|BUY]->(p:Product)-[r:SIMILAR]->(rec:Product)
        WHERE NOT (u)-[:VIEW|BUY]->(rec)
        RETURN rec.id AS product_id, sum(r.score) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, uid=int(user_id), limit=int(limit))
                return [(row["product_id"], float(row["score"])) for row in result]
        except Exception as e:
            print(f"Error fetching similarity recommendations: {e}")
            return []
