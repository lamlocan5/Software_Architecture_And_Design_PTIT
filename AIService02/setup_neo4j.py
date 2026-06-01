"""
setup_neo4j.py — Câu 2b: Xây dựng Knowledge Base Graph (KB_Graph) với Neo4j
Tạo các nodes và relationships từ data_user500.csv

Chạy: python setup_neo4j.py
"""
import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import time

load_dotenv()

# ==========================================
# CẤU HÌNH KẾT NỐI NEO4J
# ==========================================
NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER     = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "123456789")

DATA_PATH = "data_user500.csv"

# ==========================================
# LỚP QUẢN LÝ KB_GRAPH
# ==========================================
class KBGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✅ Kết nối Neo4j thành công: {uri}")

    def close(self):
        self.driver.close()

    def clear_database(self):
        """Xóa toàn bộ dữ liệu cũ trước khi import"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("🗑  Đã xóa dữ liệu cũ trong database")

    def create_constraints_and_indexes(self):
        """Tạo constraints và indexes để tăng hiệu suất"""
        with self.driver.session() as session:
            # Constraints (unique)
            constraints = [
                "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
                "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT device_name IF NOT EXISTS FOR (d:Device) REQUIRE d.name IS UNIQUE",
            ]
            for c in constraints:
                try:
                    session.run(c)
                except Exception:
                    pass  # Constraint có thể đã tồn tại

            # Indexes
            indexes = [
                "CREATE INDEX user_idx IF NOT EXISTS FOR (u:User) ON (u.user_id)",
                "CREATE INDEX product_idx IF NOT EXISTS FOR (p:Product) ON (p.product_id)",
            ]
            for idx in indexes:
                try:
                    session.run(idx)
                except Exception:
                    pass
        print("📋 Đã tạo constraints và indexes")

    def create_category_nodes(self, categories):
        """Tạo các Node Category"""
        with self.driver.session() as session:
            for cat in categories:
                session.run("""
                    MERGE (c:Category {name: $name})
                """, name=cat)
        print(f"📦 Đã tạo {len(categories)} Category nodes: {categories}")

    def create_device_nodes(self, devices):
        """Tạo các Node Device"""
        with self.driver.session() as session:
            for dev in devices:
                session.run("""
                    MERGE (d:Device {name: $name})
                """, name=dev)
        print(f"📱 Đã tạo {len(devices)} Device nodes: {devices}")

    def create_user_nodes(self, users_df):
        """Tạo các Node User với thống kê hành vi"""
        with self.driver.session() as session:
            for user_id, group in users_df.groupby("user_id"):
                total_sessions     = len(group)
                view_count         = len(group[group["action"] == "view"])
                click_count        = len(group[group["action"] == "click"])
                add_to_cart_count  = len(group[group["action"] == "add_to_cart"])
                avg_session        = float(group["session_duration"].mean())
                favorite_device    = group["device"].mode()[0]
                favorite_category  = group["category"].mode()[0]

                session.run("""
                    MERGE (u:User {user_id: $user_id})
                    SET u.total_sessions     = $total_sessions,
                        u.view_count         = $view_count,
                        u.click_count        = $click_count,
                        u.add_to_cart_count  = $add_to_cart_count,
                        u.avg_session        = $avg_session,
                        u.favorite_device    = $favorite_device,
                        u.favorite_category  = $favorite_category
                """, user_id=user_id, total_sessions=total_sessions,
                     view_count=view_count, click_count=click_count,
                     add_to_cart_count=add_to_cart_count, avg_session=avg_session,
                     favorite_device=favorite_device, favorite_category=favorite_category)
        print(f"👥 Đã tạo {users_df['user_id'].nunique()} User nodes")

    def create_product_nodes(self, products_df):
        """Tạo các Node Product với thông tin đầy đủ"""
        with self.driver.session() as session:
            for product_id, group in products_df.groupby("product_id"):
                category = group["category"].mode()[0]
                avg_price = float(group["price"].mean())
                view_count = len(group[group["action"] == "view"])
                popularity_score = view_count + len(group[group["action"] == "click"]) * 2 + len(group[group["action"] == "add_to_cart"]) * 5

                session.run("""
                    MERGE (p:Product {product_id: $product_id})
                    SET p.category         = $category,
                        p.avg_price        = $avg_price,
                        p.view_count       = $view_count,
                        p.popularity_score = $popularity_score
                """, product_id=product_id, category=category,
                     avg_price=avg_price, view_count=view_count,
                     popularity_score=popularity_score)
        print(f"🛍️  Đã tạo {products_df['product_id'].nunique()} Product nodes")

    def create_relationships(self, df):
        """Tạo các Relationships giữa nodes"""
        with self.driver.session() as session:
            # 1. User -[BEHAVIOR]-> Product relationships
            for _, row in df.iterrows():
                action_map = {
                    "view":        "VIEWED",
                    "click":       "CLICKED",
                    "add_to_cart": "ADDED_TO_CART"
                }
                rel_type = action_map.get(row["action"], "VIEWED")

                session.run(f"""
                    MATCH (u:User {{user_id: $user_id}})
                    MATCH (p:Product {{product_id: $product_id}})
                    MERGE (u)-[r:{rel_type} {{timestamp: $timestamp}}]->(p)
                    SET r.device           = $device,
                        r.session_duration = $session_duration,
                        r.price            = $price
                """, user_id=row["user_id"], product_id=row["product_id"],
                     timestamp=str(row["timestamp"]), device=row["device"],
                     session_duration=int(row["session_duration"]), price=float(row["price"]))

            # 2. Product -[IN_CATEGORY]-> Category
            product_cats = df[["product_id", "category"]].drop_duplicates()
            for _, row in product_cats.iterrows():
                session.run("""
                    MATCH (p:Product {product_id: $product_id})
                    MATCH (c:Category {name: $category})
                    MERGE (p)-[:IN_CATEGORY]->(c)
                """, product_id=row["product_id"], category=row["category"])

            # 3. User -[USES_DEVICE]-> Device
            user_devices = df[["user_id", "device"]].drop_duplicates()
            for _, row in user_devices.iterrows():
                session.run("""
                    MATCH (u:User {user_id: $user_id})
                    MATCH (d:Device {name: $device})
                    MERGE (u)-[:USES_DEVICE]->(d)
                """, user_id=row["user_id"], device=row["device"])

        print("🔗 Đã tạo tất cả Relationships (VIEWED, CLICKED, ADDED_TO_CART, IN_CATEGORY, USES_DEVICE)")

    def print_statistics(self):
        """In thống kê về graph đã tạo"""
        with self.driver.session() as session:
            stats = {}
            queries = {
                "Users":         "MATCH (u:User) RETURN count(u) as cnt",
                "Products":      "MATCH (p:Product) RETURN count(p) as cnt",
                "Categories":    "MATCH (c:Category) RETURN count(c) as cnt",
                "Devices":       "MATCH (d:Device) RETURN count(d) as cnt",
                "VIEWED":        "MATCH ()-[r:VIEWED]->() RETURN count(r) as cnt",
                "CLICKED":       "MATCH ()-[r:CLICKED]->() RETURN count(r) as cnt",
                "ADDED_TO_CART": "MATCH ()-[r:ADDED_TO_CART]->() RETURN count(r) as cnt",
                "IN_CATEGORY":   "MATCH ()-[r:IN_CATEGORY]->() RETURN count(r) as cnt",
                "USES_DEVICE":   "MATCH ()-[r:USES_DEVICE]->() RETURN count(r) as cnt",
            }
            for name, q in queries.items():
                result = session.run(q).single()
                stats[name] = result["cnt"]

        print("\n" + "="*50)
        print("📊 KB_GRAPH STATISTICS")
        print("="*50)
        print(f"  Nodes:")
        print(f"    👥 Users:      {stats['Users']}")
        print(f"    🛍️  Products:   {stats['Products']}")
        print(f"    📦 Categories: {stats['Categories']}")
        print(f"    📱 Devices:    {stats['Devices']}")
        print(f"  Relationships:")
        print(f"    👁️  VIEWED:         {stats['VIEWED']}")
        print(f"    🖱️  CLICKED:        {stats['CLICKED']}")
        print(f"    🛒 ADDED_TO_CART:  {stats['ADDED_TO_CART']}")
        print(f"    📑 IN_CATEGORY:    {stats['IN_CATEGORY']}")
        print(f"    📱 USES_DEVICE:    {stats['USES_DEVICE']}")
        print("="*50)
        print("\n💡 Mở Neo4j Browser tại: http://localhost:7474")
        print("   Chạy: MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 100")
        print("="*50)


# ==========================================
# MAIN
# ==========================================
def main():
    print("="*50)
    print("🚀 KB_GRAPH BUILDER — Câu 2b")
    print("="*50)

    # Load data
    print(f"\n📂 Loading {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"   ✅ Loaded {len(df)} rows, {df['user_id'].nunique()} users, {df['product_id'].nunique()} products")

    # Kết nối Neo4j
    try:
        builder = KBGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    except Exception as e:
        print(f"\n❌ Không thể kết nối Neo4j: {e}")
        print("   👉 Hãy đảm bảo Neo4j đang chạy trên localhost:7687")
        return

    try:
        print("\n⚙️  Bắt đầu xây dựng KB_Graph...")
        start = time.time()

        # 1. Xóa data cũ
        builder.clear_database()

        # 2. Tạo constraints/indexes
        builder.create_constraints_and_indexes()

        # 3. Tạo Nodes
        categories = df["category"].unique().tolist()
        devices    = df["device"].unique().tolist()
        builder.create_category_nodes(categories)
        builder.create_device_nodes(devices)
        builder.create_user_nodes(df)
        builder.create_product_nodes(df)

        # 4. Tạo Relationships
        print("🔗 Đang tạo relationships (có thể mất vài phút)...")
        builder.create_relationships(df)

        elapsed = time.time() - start
        print(f"\n⏱️  Hoàn thành trong {elapsed:.1f} giây")

        # 5. In thống kê
        builder.print_statistics()

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình xây dựng graph: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close()


if __name__ == "__main__":
    main()
