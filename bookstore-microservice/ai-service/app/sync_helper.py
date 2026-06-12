import os
import time
import requests
from app.models import ProductNode, ProductSimilarity, UserBehavior
from app.graph_engine import Neo4jGraphEngine
from app.lstm_model import train_lstm_model
from app.rag_engine import RAGEngine

def run_bootstrap_sync():
    """
    Perform a one-time bootstrap synchronization of book metadata, similarity relations,
    and user behavior logs on startup.
    """
    # Sleep to allow other microservices and Neo4j container to fully initialize
    print("AI-Service background bootstrap sync will start in 15 seconds...")
    time.sleep(15)
    print("AI-Service background bootstrap sync starting...")

    # Check if we already have books. If so, skip import (one-time sync check)
    if ProductNode.objects.exists():
        print("ProductNode database already contains records. Skipping bootstrap sync.")
        # Trigger index build on current records
        try:
            RAGEngine.get_instance().rebuild_index()
        except Exception as e:
            print(f"Error rebuilding FAISS index: {e}")
        return

    host_catalog = "catalogue-service:8000"
    host_product = "product-service:8000"
    host_review = "review-service:8000"
    
    db_host = os.environ.get('DB_HOST', '')
    if db_host in ('127.0.0.1', 'localhost'):
        host_catalog = "localhost:8008"
        host_product = "localhost:8002"
        host_review = "localhost:8005"

    # 1. Fetch books from catalogue-service
    books = []
    try:
        r = requests.get(f"http://{host_catalog}/catalog/books/", timeout=10)
        if r.status_code == 200:
            books = r.json()
            print(f"Successfully fetched {len(books)} books from catalogue-service.")
    except Exception as e:
        print(f"Failed to fetch from catalogue-service: {e}. Trying product-service...")
        try:
            r = requests.get(f"http://{host_product}/books/", timeout=10)
            if r.status_code == 200:
                books = r.json()
                print(f"Successfully fetched {len(books)} books from product-service.")
        except Exception as ex:
            print(f"Failed to fetch books from product-service: {ex}")

    if not books:
        print("No books could be fetched. Seeding dummy product nodes...")
        # Create a few dummy books to ensure the system is not empty
        books = [
            {"id": 1, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "category_name": "Kỹ năng", "price": 86000.0},
            {"id": 2, "title": "Số Đỏ", "author": "Vũ Trọng Phụng", "category_name": "Văn học", "price": 65000.0},
            {"id": 3, "title": "Chí Phèo", "author": "Nam Cao", "category_name": "Văn học", "price": 45000.0},
            {"id": 4, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài", "category_name": "Thiếu nhi", "price": 55000.0},
        ]

    # Save books to local ProductNode
    for b in books:
        try:
            pid = b.get('id')
            title = b.get('title') or b.get('name') or f"Product {pid}"
            author = b.get('author') or 'Unknown'
            # Parse category
            category = 'General'
            if b.get('category_name'):
                category = b.get('category_name')
            elif isinstance(b.get('category_detail'), dict):
                category = b.get('category_detail', {}).get('name', 'General')
            price = b.get('price') or 0.0

            ProductNode.objects.update_or_create(
                product_id=pid,
                defaults={
                    'title': title,
                    'author': author,
                    'category': category,
                    'price': price
                }
            )
        except Exception as e:
            print(f"Error saving book {b}: {e}")

    print("ProductNode table populated successfully.")

    # 2. Build similarities and sync to Neo4j
    nodes = list(ProductNode.objects.all())
    graph = Neo4jGraphEngine()
    if graph.driver:
        print("Connected to Neo4j. Seeding SIMILAR relationships...")
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                p1 = nodes[i]
                p2 = nodes[j]
                
                # Compute mock similarity based on category and author
                sim = 0.2
                if p1.category == p2.category:
                    sim += 0.4
                if p1.author == p2.author:
                    sim += 0.3
                    
                # Save to PostgreSQL
                ProductSimilarity.objects.update_or_create(
                    product_id_1=p1.product_id,
                    product_id_2=p2.product_id,
                    defaults={'similarity_score': sim}
                )
                ProductSimilarity.objects.update_or_create(
                    product_id_1=p2.product_id,
                    product_id_2=p1.product_id,
                    defaults={'similarity_score': sim}
                )
                # Sync to Neo4j
                graph.sync_similarity(p1.product_id, p2.product_id, sim)
                graph.sync_similarity(p2.product_id, p1.product_id, sim)
    else:
        print("Could not connect to Neo4j. Skipping Neo4j similarity sync.")

    # 3. Fetch reviews from review-service and sync as VIEW behaviors
    reviews = []
    try:
        r = requests.get(f"http://{host_review}/reviews/", timeout=10)
        if r.status_code == 200:
            reviews = r.json()
            print(f"Successfully fetched {len(reviews)} reviews from review-service.")
    except Exception as e:
        print(f"Failed to fetch reviews from review-service: {e}")

    for rev in reviews:
        try:
            uid = rev.get('customer_id') or 1
            pid = rev.get('book_id') or 1
            # Save UserBehavior to DB
            UserBehavior.objects.get_or_create(
                user_id=uid,
                product_id=pid,
                behavior_type='view'
            )
            # Sync to Neo4j
            if graph.driver:
                graph.sync_behavior(uid, pid, 'view')
        except Exception as e:
            print(f"Error syncing review behavior: {e}")

    # Seed some mock behavior logs if still empty
    if not UserBehavior.objects.exists():
        print("No behaviors recorded. Seeding basic interaction sequences...")
        # Simulating sequence 1->2->3->4->5 for user 7
        # Simulating sequence 2->3->4->5->6 for user 8
        mock_behaviors = [
            (7, 1, 'view'), (7, 2, 'view'), (7, 3, 'view'), (7, 4, 'view'), (7, 5, 'buy'),
            (8, 2, 'view'), (8, 3, 'view'), (8, 4, 'view'), (8, 5, 'view'), (8, 6, 'buy'),
        ]
        for uid, pid, btype in mock_behaviors:
            UserBehavior.objects.create(user_id=uid, product_id=pid, behavior_type=btype)
            if graph.driver:
                graph.sync_behavior(uid, pid, btype)

    if graph:
        graph.close()

    print("Auto-training LSTM model with seeded data...")
    try:
        behaviors = list(UserBehavior.objects.all())
        train_lstm_model(behaviors)
    except Exception as e:
        print(f"Error training LSTM: {e}")

    print("Rebuilding FAISS index for RAG chatbot...")
    try:
        RAGEngine.get_instance().rebuild_index()
    except Exception as e:
        print(f"Error building FAISS: {e}")

    print("AI-Service background bootstrap sync completed successfully!")
