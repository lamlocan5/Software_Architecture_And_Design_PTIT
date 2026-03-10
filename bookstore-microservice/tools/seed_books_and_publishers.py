import random
import sys
from dataclasses import dataclass

import requests


BOOK_SERVICE_BASE = "http://localhost:8002"


@dataclass(frozen=True)
class PublisherSeed:
    name: str
    mail: str
    address: str


@dataclass(frozen=True)
class BookSeed:
    title: str
    author: str
    price: float
    stock: int
    publisher_idx: int | None  # index into publishers list


def _post(path: str, payload: dict):
    url = f"{BOOK_SERVICE_BASE}{path}"
    r = requests.post(url, json=payload, timeout=10)
    try:
        data = r.json()
    except Exception:
        data = r.text
    return r.status_code, data


def _get(path: str):
    url = f"{BOOK_SERVICE_BASE}{path}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    # Avoid Windows console encoding issues by forcing UTF-8 stdout
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    publishers = [
        PublisherSeed("NXB Trẻ", "contact@nxbtre.example", "161B Lý Chính Thắng, Q.3, TP.HCM"),
        PublisherSeed("NXB Kim Đồng", "contact@nxbkimdong.example", "55 Quang Trung, Hà Nội"),
        PublisherSeed("NXB Tổng Hợp TP.HCM", "contact@nxbth.example", "62 Nguyễn Thị Minh Khai, Q.1, TP.HCM"),
        PublisherSeed("NXB Lao Động", "contact@nxblodong.example", "175 Giảng Võ, Hà Nội"),
        PublisherSeed("NXB Giáo Dục", "contact@nxbgd.example", "81 Trần Hưng Đạo, Hà Nội"),
    ]

    books = [
        BookSeed("Python Cơ Bản", "Nguyễn Văn A", 149000, 12, 0),
        BookSeed("Python Nâng Cao", "Nguyễn Văn A", 199000, 8, 0),
        BookSeed("Clean Code (Bản Việt)", "Robert C. Martin", 259000, 6, 1),
        BookSeed("Design Patterns", "Erich Gamma", 299000, 5, 1),
        BookSeed("Django Thực Chiến", "Lê Minh", 219000, 10, 2),
        BookSeed("REST API với DRF", "Trần Huy", 189000, 9, 2),
        BookSeed("Cấu Trúc Dữ Liệu", "Phạm Quang", 179000, 15, 4),
        BookSeed("Giải Thuật Cơ Bản", "Phạm Quang", 189000, 14, 4),
        BookSeed("Microservices 101", "Sam Newman", 279000, 7, 3),
        BookSeed("System Design Interview", "Alex Xu", 289000, 4, 3),
        BookSeed("SQL Từ A-Z", "Hoàng Anh", 159000, 20, 4),
        BookSeed("PostgreSQL Thực Hành", "Hoàng Anh", 209000, 11, 4),
        BookSeed("Kỹ Năng Làm Việc Nhóm", "Ngọc Hà", 99000, 25, 0),
        BookSeed("Tư Duy Phản Biện", "Ngọc Hà", 119000, 18, 0),
        BookSeed("Kinh Tế Vĩ Mô", "Đặng Minh", 189000, 6, 3),
        BookSeed("Quản Trị Dự Án", "Đặng Minh", 219000, 5, 3),
        BookSeed("UI/UX Căn Bản", "Thu Trang", 169000, 13, 2),
        BookSeed("Product Thinking", "Thu Trang", 199000, 9, 2),
        BookSeed("Tâm Lý Học Hành Vi", "Lan Anh", 179000, 0, 1),
        BookSeed("Kỹ Năng Đọc Sách", "Lan Anh", 99000, 30, 1),
    ]

    # sanity check service is reachable
    try:
        _get("/publishers/")
    except Exception as e:
        print(f"[ERR] Cannot reach book-service at {BOOK_SERVICE_BASE}: {e}")
        return 1

    created_publishers = []
    for p in publishers:
        status, data = _post(
            "/publishers/",
            {"name": p.name, "mail": p.mail, "address": p.address},
        )
        if status == 201:
            created_publishers.append(data)
            print(f"[OK] Publisher created: id={data.get('id')} mail={p.mail}")
        elif status == 400 and isinstance(data, dict) and "mail" in data:
            # already exists -> fetch existing by listing
            existing = _get("/publishers/")
            match = next((x for x in existing if str(x.get("mail", "")).lower() == p.mail.lower()), None)
            if match:
                created_publishers.append(match)
                print(f"[SKIP] Publisher exists: id={match.get('id')} mail={p.mail}")
            else:
                print(f"[ERR] Publisher error: mail={p.mail} -> {data}")
                return 1
        else:
            print(f"[ERR] Publisher create failed: mail={p.mail} status={status} data={data}")
            return 1

    # create books
    random.shuffle(books)
    for b in books:
        publisher_id = None
        if b.publisher_idx is not None:
            publisher_id = created_publishers[b.publisher_idx].get("id")
        payload = {
            "title": b.title,
            "author": b.author,
            "price": float(b.price),
            "stock": int(b.stock),
            "publisher": publisher_id,
        }
        status, data = _post("/books/", payload)
        if status == 201:
            print(f"[OK] Book created: id={data.get('id')} title={b.title}")
        else:
            print(f"[ERR] Book create failed: {b.title} status={status} data={data}")
            return 1

    # verify counts
    pubs = _get("/publishers/")
    bs = _get("/books/")
    print(f"[DONE] publishers={len(pubs)} books={len(bs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

