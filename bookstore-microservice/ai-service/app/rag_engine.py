import os
import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models import ProductNode

class RAGEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Load lightweight and fast model suitable for CPU execution
        print("Initializing SentenceTransformer encoder...")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.product_ids = []
        self.rebuild_index()

    def rebuild_index(self):
        """
        Pull all products from ProductNode model, encode descriptions, and populate FAISS.
        """
        products = ProductNode.objects.all()
        if not products.exists():
            print("No products in ProductNode database. FAISS index will be empty.")
            self.index = None
            self.product_ids = []
            return

        texts = []
        pids = []
        for p in products:
            # Combine attributes into text block for embedding based on product_type
            if p.product_type == 'clothing':
                desc = f"Sản phẩm thời trang quần áo: {p.title}. Chi tiết: {p.author}. Thể loại: {p.category or 'Thời trang'}. Giá: {p.price} VND."
            elif p.product_type == 'electronic':
                desc = f"Thiết bị đồ điện tử máy móc: {p.title}. Chi tiết: {p.author}. Thể loại: {p.category or 'Đồ điện tử'}. Giá: {p.price} VND."
            else:
                desc = f"Sách đọc: {p.title}. Tác giả: {p.author or 'Chưa rõ'}. Thể loại: {p.category or 'Sách'}. Giá: {p.price} VND."
            texts.append(desc)
            pids.append(p.product_id)

        try:
            embeddings = self.encoder.encode(texts)
            embeddings = np.array(embeddings).astype('float32')
            dimension = embeddings.shape[1]
            
            # Setup L2 distance Flat index
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            self.index = index
            self.product_ids = pids
            print(f"FAISS index successfully rebuilt with {len(pids)} items!")
        except Exception as e:
            print(f"Error rebuilding FAISS index: {e}")
            self.index = None
            self.product_ids = []

    def sync_from_remote(self):
        """
        Fetch latest products (books, clothes, electronics) from remote services and update local ProductNode table.
        """
        import requests
        
        host_catalog = "catalogue-service:8000"
        host_product = "product-service:8000"
        
        db_host = os.environ.get('DB_HOST', '')
        if db_host in ('127.0.0.1', 'localhost'):
            host_catalog = "localhost:8008"
            host_product = "localhost:8002"

        # 1. Fetch Books
        books = []
        try:
            r = requests.get(f"http://{host_catalog}/catalog/books/", timeout=2)
            if r.status_code == 200:
                books = r.json()
        except Exception:
            try:
                r = requests.get(f"http://{host_product}/books/", timeout=2)
                if r.status_code == 200:
                    books = r.json()
            except Exception:
                pass

        # 2. Fetch Clothes
        clothes = []
        try:
            r = requests.get(f"http://{host_product}/clothes/", timeout=2)
            if r.status_code == 200:
                clothes = r.json()
        except Exception:
            pass

        # 3. Fetch Electronics
        electronics = []
        try:
            r = requests.get(f"http://{host_product}/electronics/", timeout=2)
            if r.status_code == 200:
                electronics = r.json()
        except Exception:
            pass

        all_products = []
        for b in (books if isinstance(books, list) else []):
            if not isinstance(b, dict) or not b.get("id"):
                continue
            all_products.append({
                "product_id": b["id"],
                "title": b.get("title") or b.get("name") or f"Book #{b['id']}",
                "author": b.get("author") or "Unknown",
                "category": b.get("category_name") or "General",
                "price": float(b.get("price") or 0.0),
                "product_type": "book"
            })

        for c in (clothes if isinstance(clothes, list) else []):
            if not isinstance(c, dict) or not c.get("id"):
                continue
            cat_name = c.get("category_detail", {}).get("name") if isinstance(c.get("category_detail"), dict) else "Thời trang"
            size = c.get("size") or "—"
            color = c.get("color") or "—"
            all_products.append({
                "product_id": c["id"],
                "title": c.get("name") or f"Clothing #{c['id']}",
                "author": f"Size: {size}, Màu: {color}",
                "category": cat_name,
                "price": float(c.get("price") or 0.0),
                "product_type": "clothing"
            })

        for e in (electronics if isinstance(electronics, list) else []):
            if not isinstance(e, dict) or not e.get("id"):
                continue
            cat_name = e.get("category_detail", {}).get("name") if isinstance(e.get("category_detail"), dict) else "Điện tử"
            brand = e.get("brand") or "—"
            model = e.get("model") or "—"
            all_products.append({
                "product_id": e["id"],
                "title": e.get("name") or f"Electronic #{e['id']}",
                "author": f"Hãng: {brand}, Model: {model}",
                "category": cat_name,
                "price": float(e.get("price") or 0.0),
                "product_type": "electronic"
            })

        # Compare keys
        current_pids = set(self.product_ids) if self.product_ids else set()
        remote_pids = {p["product_id"] for p in all_products}

        if not current_pids or current_pids != remote_pids:
            print(f"Syncing {len(all_products)} products from catalog...")
            for p in all_products:
                ProductNode.objects.update_or_create(
                    product_id=p["product_id"],
                    defaults={
                        'title': p["title"],
                        'author': p["author"],
                        'category': p["category"],
                        'price': p["price"],
                        'product_type': p["product_type"]
                    }
                )
            # Delete any local nodes that were removed remotely
            ProductNode.objects.exclude(product_id__in=remote_pids).delete()
            self.rebuild_index()

    def search(self, query, k=3):
        """
        Query vector search in FAISS.
        """
        self.sync_from_remote()
        if self.index is None or not self.product_ids:
            self.rebuild_index()
            if self.index is None:
                return []

        try:
            query_vector = self.encoder.encode([query])
            query_vector = np.array(query_vector).astype('float32')
            distances, indices = self.index.search(query_vector, k)
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.product_ids):
                    continue
                pid = self.product_ids[idx]
                try:
                    product = ProductNode.objects.get(product_id=pid)
                    results.append((product, float(dist)))
                except ProductNode.DoesNotExist:
                    continue
            return results
        except Exception as e:
            print(f"Error during FAISS search: {e}")
            return []

    def generate_chatbot_answer(self, query):
        """
        Retrieves top books context and constructs a Gemini model prompt.
        """
        # Retrieve top 4 relevant matches
        matches = self.search(query, k=4)
        
        context_parts = []
        for p, dist in matches:
            if p.product_type == 'clothing':
                context_parts.append(
                    f"- [Thời trang - ID: {p.product_id}] \"{p.title}\" ({p.author}, Thể loại: {p.category or 'Thời trang'}, Giá: {p.price} VND)"
                )
            elif p.product_type == 'electronic':
                context_parts.append(
                    f"- [Đồ điện tử - ID: {p.product_id}] \"{p.title}\" ({p.author}, Thể loại: {p.category or 'Điện tử'}, Giá: {p.price} VND)"
                )
            else:
                context_parts.append(
                    f"- [Sách - ID: {p.product_id}] \"{p.title}\" của tác giả {p.author or 'chưa rõ'} (Thể loại: {p.category or 'Sách'}, Giá: {p.price} VND)"
                )
        context_text = "\n".join(context_parts) if context_parts else "Không tìm thấy sản phẩm nào cụ thể liên quan trong cơ sở dữ liệu."

        prompt = (
            "Bạn là trợ lý AI (Chatbot) thông minh, thân thiện tư vấn và bán các sản phẩm (Sách, Quần áo thời trang, Thiết bị điện tử) của Bookstore.\n"
            "Dưới đây là một số sản phẩm từ hệ thống của cửa hàng chúng tôi phù hợp với truy vấn của người dùng:\n"
            f"{context_text}\n\n"
            "Hãy trả lời người dùng bằng tiếng Việt tự nhiên, nhiệt tình và chuyên nghiệp. "
            "Gợi ý trực tiếp các sản phẩm phù hợp trên khi trả lời, nêu rõ ID sản phẩm, tên, giá cả và thuộc tính để khách dễ chọn mua. "
            "Nếu câu hỏi không liên quan trực tiếp đến sản phẩm của cửa hàng, vẫn trả lời lịch sự và khéo léo liên hệ tới các sản phẩm tương ứng.\n"
            "QUAN TRỌNG: Chỉ trả lời trực tiếp nội dung trò chuyện với khách hàng. Tuyệt đối không thêm bất kỳ bước phân tích, quy tắc ẩn, ghi chú kỹ thuật hay checklist nào khác ở cuối câu trả lời.\n\n"
            f"Câu hỏi của khách hàng: {query}\n"
            "Câu trả lời:"
        )

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            return (
                f"Chào bạn! Rất tiếc hiện tại khóa kết nối AI (GEMINI_API_KEY) chưa được thiết lập. "
                f"Tuy nhiên, dựa vào kho sách của chúng tôi, tôi tìm thấy một số gợi ý cho bạn:\n{context_text}"
            )

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
        try:
            r = requests.post(
                url,
                params={"key": api_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.6, "maxOutputTokens": 4096},
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
            return text or "Cảm ơn bạn đã liên hệ! Tôi có thể giúp gì thêm cho bạn?"
        except Exception as e:
            print(f"Gemini API generation error: {e}")
            import traceback
            traceback.print_exc()
            return (
                f"Chào bạn! Có một lỗi nhỏ khi kết nối tới AI. "
                f"Đây là một số gợi ý sách phù hợp nhất từ hệ thống của chúng tôi:\n{context_text}"
            )
