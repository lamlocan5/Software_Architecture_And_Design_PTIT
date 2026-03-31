from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
import requests

BOOK_SERVICE_URL          = "http://book-service:8000"
CLOTHE_SERVICE_URL        = "http://clothe-service:8000"
ELECTRONIC_SERVICE_URL    = "http://electronic-service:8000"
CATALOGUE_SERVICE_URL     = "http://catalogue-service:8000"
CART_SERVICE_URL          = "http://cart-service:8000"
CUSTOMER_SERVICE_URL      = "http://customer-service:8000"
STAFF_SERVICE_URL         = "http://staff-service:8000"
MANAGER_SERVICE_URL       = "http://manager-service:8000"
ORDER_SERVICE_URL         = "http://order-service:8000"
REVIEW_SERVICE_URL        = "http://review-service:8000"
SHIP_SERVICE_URL          = "http://ship-service:8000"
PAY_SERVICE_URL           = "http://pay-service:8000"
RECOMMENDER_SERVICE_URL   = "http://recommender-ai-service:8000"


# ──────────────────────────────── helpers ────────────────────────────────

def _get(url, default=None):
    try:
        r = requests.get(url, timeout=3)
        return r.json()
    except Exception:
        return default if default is not None else []


def _post(url, data):
    return requests.post(url, json=data, timeout=3)

def _patch(url, data):
    return requests.patch(url, json=data, timeout=3)


def _get_customer_id(user):
    """Lấy customer_id từ profile của user đang đăng nhập."""
    try:
        return user.profile.customer_id
    except Exception:
        return None


def _user_in_group(user, group_name: str) -> bool:
    try:
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


def _is_admin(user) -> bool:
    return bool(getattr(user, "is_superuser", False))


def _is_manager(user) -> bool:
    return _is_admin(user) or _user_in_group(user, "manager")


def _is_staff_user(user) -> bool:
    return _is_admin(user) or _user_in_group(user, "staff")


def _can_manage_books(user) -> bool:
    return _is_admin(user) or _is_staff_user(user) or _is_manager(user)


# ──────────────────────────────── HOME ───────────────────────────────────

@login_required
def home(request):
    # Admin + Staff + Manager → dashboard quản trị
    if _can_manage_books(request.user) or _is_admin(request.user):
        books      = _get(f"{BOOK_SERVICE_URL}/books/", [])
        customers  = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
        orders     = _get(f"{ORDER_SERVICE_URL}/orders/", [])
        reviews    = _get(f"{REVIEW_SERVICE_URL}/reviews/", [])
        publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])

        # AI recommendations (best-effort)
        reco_books = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/", [])
        recommended = []
        if isinstance(reco_books, list) and reco_books:
            try:
                rr = _post(f"{RECOMMENDER_SERVICE_URL}/recommendations/", {"books": reco_books[:50], "limit": 6, "context": "home"})
                if getattr(rr, "status_code", 200) < 400:
                    ids = rr.json().get("recommended_ids", [])
                    id_map = {b.get("id"): b for b in reco_books if isinstance(b, dict)}
                    recommended = [id_map.get(i) for i in ids if i in id_map]
                    recommended = [b for b in recommended if b]
            except Exception:
                recommended = []

        return render(request, "index.html", {
            "book_count":      len(books)      if isinstance(books, list)      else 0,
            "customer_count":  len(customers)  if isinstance(customers, list)  else 0,
            "order_count":     len(orders)     if isinstance(orders, list)     else 0,
            "review_count":    len(reviews)    if isinstance(reviews, list)    else 0,
            "publisher_count": len(publishers) if isinstance(publishers, list) else 0,
            # Tổng số microservice backend (không tính api-gateway):
            # customer, book, cart, order, review, ship, pay, catalogue, staff, manager
            "service_count": 10,
            "recommended_books": recommended,
        })

    # Ngược lại: khách hàng thường → user dashboard
    customer_id = _get_customer_id(request.user)
    books       = _get(f"{BOOK_SERVICE_URL}/books/", [])
    cart_items  = []
    cart_total  = 0
    orders      = []

    if customer_id:
        items    = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
        book_map = {b["id"]: b for b in (books if isinstance(books, list) else [])}
        for item in (items if isinstance(items, list) else []):
            book             = book_map.get(item["book_id"], {})
            item["book"]     = book
            item["subtotal"] = float(book.get("price", 0)) * item["quantity"] if book else 0
            cart_total      += item["subtotal"]
        cart_items = items

        orders = _get(f"{ORDER_SERVICE_URL}/orders/customer/{customer_id}/", [])

    return render(request, "user_home.html", {
        "cart_items":  cart_items if isinstance(cart_items, list) else [],
        "cart_count":  len(cart_items) if isinstance(cart_items, list) else 0,
        "cart_total":  cart_total,
        "orders":      orders if isinstance(orders, list) else [],
        "order_count": len(orders) if isinstance(orders, list) else 0,
        "book_count":  len(books)  if isinstance(books, list)  else 0,
    })


# ──────────────────────────────── BOOKS ──────────────────────────────────

@login_required
def book_list(request):
    message = None

    if request.method == "POST":
        if not _can_manage_books(request.user):
            return redirect("book_list")
        try:
            stock_val = int(request.POST.get("stock") or 0)
            price_val = float(request.POST.get("price") or 0)
        except (ValueError, TypeError):
            message = {"type": "danger", "text": "Số lượng (stock) và giá (price) phải là số hợp lệ!"}
            books = _get(f"{BOOK_SERVICE_URL}/books/", [])
            return render(request, "books.html", {"books": books if isinstance(books, list) else [], "message": message})

        data = {
            "title":     request.POST.get("title"),
            "author":    request.POST.get("author"),
            "price":     price_val,
            "stock":     stock_val,
            "publisher": int(request.POST.get("publisher")) if request.POST.get("publisher") else None,
        }
        try:
            r = _post(f"{BOOK_SERVICE_URL}/books/", data)
            if r.status_code == 201:
                return redirect("book_list")
            message = {"type": "danger", "text": f"Thêm sách thất bại: {r.text}"}
        except Exception as e:
            message = {"type": "danger", "text": f"Lỗi kết nối book-service: {e}"}

    books = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/", [])
    if not isinstance(books, list):
        books = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối catalogue-service!"}

    publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])

    return render(request, "books.html", {"books": books, "publishers": publishers if isinstance(publishers, list) else [], "message": message})


# ──────────────────────────────── CLOTHES ────────────────────────────────

@login_required
def clothes_list(request):
    message = None

    # Chỉ admin/manager/staff mới được sửa dữ liệu
    can_manage = _can_manage_books(request.user)

    if request.method == "POST" and can_manage:
        action = request.POST.get("action") or "create"
        try:
            stock_val = int(request.POST.get("stock") or 0)
            price_val = float(request.POST.get("price") or 0)
        except (ValueError, TypeError):
            message = {"type": "danger", "text": "Số lượng (stock) và giá (price) phải là số hợp lệ!"}
        else:
            payload = {
                "name":   request.POST.get("name"),
                "size":   request.POST.get("size") or "",
                "color":  request.POST.get("color") or "",
                "price":  price_val,
                "stock":  stock_val,
                "category": int(request.POST.get("category")) if request.POST.get("category") else None,
            }
            try:
                if action == "update":
                    cid = request.POST.get("id")
                    r = _patch(f"{CLOTHE_SERVICE_URL}/clothes/{cid}/", payload)
                elif action == "delete":
                    cid = request.POST.get("id")
                    r = requests.delete(f"{CLOTHE_SERVICE_URL}/clothes/{cid}/", timeout=3)
                else:
                    r = _post(f"{CLOTHE_SERVICE_URL}/clothes/", payload)

                if r.status_code in (200, 201, 204):
                    return redirect("clothes_list")
                message = {"type": "danger", "text": f"Thao tác với quần áo thất bại: {getattr(r, 'text', '')}"}
            except Exception as e:
                message = {"type": "danger", "text": f"Lỗi kết nối clothe-service: {e}"}

    clothes = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    if not isinstance(clothes, list):
        clothes = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối clothe-service!"}

    categories = _get(f"{CLOTHE_SERVICE_URL}/clothes/categories/", [])
    if not isinstance(categories, list):
        categories = []

    return render(request, "clothes.html", {
        "clothes": clothes,
        "categories": categories,
        "message": message,
        "is_admin": _is_admin(request.user),
        "is_staff_role": _is_staff_user(request.user),
        "is_manager_role": _is_manager(request.user),
        "can_manage_clothes": can_manage,
    })


@login_required
def clothe_detail(request, clothe_id):
    customer_id = _get_customer_id(request.user)
    message = None

    clothing = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    if isinstance(clothing, list):
        clothing = next((c for c in clothing if isinstance(c, dict) and c.get("id") == clothe_id), None)
    if not isinstance(clothing, dict) or not clothing:
        return redirect("clothes_list")

    # Lấy cart_id hiện tại của customer
    cart_id = None
    if customer_id:
        try:
            cart_info = requests.get(f"{CART_SERVICE_URL}/carts/customer/{customer_id}/", timeout=3).json()
            cart_id   = cart_info.get("id")
        except Exception:
            cart_id = None

    if request.method == "POST":
        if not customer_id:
            return redirect("login")
        if not cart_id:
            message = {"type": "danger", "text": "Không tìm thấy giỏ hàng của bạn!"}
        else:
            try:
                quantity = int(request.POST.get("quantity", 1))
                if quantity < 1:
                    quantity = 1
            except Exception:
                quantity = 1

            try:
                r = _post(f"{CART_SERVICE_URL}/carts/add-item/", {
                    "cart": cart_id,
                    "clothing_id": clothe_id,
                    "quantity": quantity,
                })
                if r.status_code == 200:
                    return redirect("cart_view", customer_id=customer_id)
                message = {"type": "danger", "text": f"Thêm vào giỏ thất bại: {getattr(r, 'text', '')}"}
            except Exception as e:
                message = {"type": "danger", "text": f"Lỗi kết nối cart-service: {e}"}

    return render(request, "clothe_detail.html", {
        "clothe": clothing,
        "message": message,
        "customer_id": customer_id,
    })


# ──────────────────────────────── ELECTRONICS ──────────────────────────────

@login_required
def electronics_list(request):
    message = None
    can_manage = _can_manage_books(request.user)

    # Hiện tại chỉ đọc, nếu muốn CRUD có thể reuse logic như clothes_list
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    if not isinstance(electronics, list):
        electronics = []
        message = {"type": "warning", "text": "Không thể kết nối electronic-service!"}

    return render(request, "electronics.html", {
        "electronics": electronics,
        "message": message,
        "can_manage_electronics": can_manage,
    })


@login_required
def electronic_detail(request, electronic_id):
    customer_id = _get_customer_id(request.user)
    message = None

    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    if isinstance(electronics, list):
        electronic = next((e for e in electronics if isinstance(e, dict) and e.get("id") == electronic_id), None)
    else:
        electronic = None

    if not isinstance(electronic, dict) or not electronic:
        return redirect("electronics_list")

    cart_id = None
    if customer_id:
        try:
            cart_info = requests.get(f"{CART_SERVICE_URL}/carts/customer/{customer_id}/", timeout=3).json()
            cart_id   = cart_info.get("id")
        except Exception:
            cart_id = None

    if request.method == "POST":
        if not customer_id:
            return redirect("login")
        if not cart_id:
            message = {"type": "danger", "text": "Không tìm thấy giỏ hàng của bạn!"}
        else:
            try:
                quantity = int(request.POST.get("quantity", 1))
                if quantity < 1:
                    quantity = 1
            except Exception:
                quantity = 1

            try:
                r = _post(f"{CART_SERVICE_URL}/carts/add-item/", {
                    "cart": cart_id,
                    "electronic_id": electronic_id,
                    "quantity": quantity,
                })
                if r.status_code == 200:
                    return redirect("cart_view", customer_id=customer_id)
                message = {"type": "danger", "text": f"Thêm vào giỏ thất bại: {getattr(r, 'text', '')}"}
            except Exception as e:
                message = {"type": "danger", "text": f"Lỗi kết nối cart-service: {e}"}

    return render(request, "electronic_detail.html", {
        "electronic": electronic,
        "message": message,
        "customer_id": customer_id,
    })

@login_required
def book_detail(request, book_id):
    customer_id = _get_customer_id(request.user)
    message = None

    book = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/{book_id}/", {})
    if not isinstance(book, dict) or not book:
        return redirect("book_list")

    publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])
    if not isinstance(publishers, list):
        publishers = []
    pub_map = {p.get("id"): p for p in publishers}

    if request.method == "POST":
        if not customer_id:
            return redirect("login")
        try:
            quantity = int(request.POST.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except Exception:
            quantity = 1

        try:
            cart_info = requests.get(f"{CART_SERVICE_URL}/carts/customer/{customer_id}/", timeout=3).json()
            cart_id = cart_info.get("id")
            if not cart_id:
                message = {"type": "danger", "text": "Không tìm thấy giỏ hàng của bạn!"}
            else:
                r = _post(f"{CART_SERVICE_URL}/carts/add-item/", {
                    "cart": cart_id,
                    "book_id": book_id,
                    "quantity": quantity,
                })
                if r.status_code == 200:
                    return redirect("cart_view", customer_id=customer_id)
                message = {"type": "danger", "text": f"Thêm vào giỏ thất bại: {r.text}"}
        except Exception as e:
            message = {"type": "danger", "text": f"Lỗi kết nối cart-service: {e}"}

    return render(request, "book_detail.html", {
        "book": book,
        "publisher": pub_map.get(book.get("publisher")),
        "message": message,
        "customer_id": customer_id,
    })


# ──────────────────────────────── CATALOGUE ──────────────────────────────

@login_required
def catalogue_list(request):
    message = None

    q = (request.GET.get("q") or "").strip()
    publisher_filter = (request.GET.get("publisher") or "").strip()
    min_price_raw = (request.GET.get("min_price") or "").strip()
    max_price_raw = (request.GET.get("max_price") or "").strip()

    books = _get(f"{CATALOGUE_SERVICE_URL}/catalog/books/", [])
    if not isinstance(books, list):
        books = []
        message = {"type": "warning", "text": "Không thể kết nối catalogue-service!"}

    publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])
    if not isinstance(publishers, list):
        publishers = []

    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return None

    min_price = _to_float(min_price_raw) if min_price_raw else None
    max_price = _to_float(max_price_raw) if max_price_raw else None

    def _match(book):
        title = str(book.get("title", ""))
        author = str(book.get("author", ""))
        if q:
            q_lower = q.lower()
            if q_lower not in title.lower() and q_lower not in author.lower():
                return False

        if publisher_filter:
            if str(book.get("publisher") or "") != publisher_filter:
                return False

        price = None
        try:
            price = float(book.get("price", 0))
        except Exception:
            price = None

        if min_price is not None and price is not None and price < min_price:
            return False
        if max_price is not None and price is not None and price > max_price:
            return False

        return True

    filtered_books = [b for b in books if _match(b)]

    # recommendations (best-effort) based on filtered list
    recommended = []
    try:
        rr = _post(f"{RECOMMENDER_SERVICE_URL}/recommendations/", {"books": filtered_books[:50], "limit": 6, "context": "catalogue"})
        if getattr(rr, "status_code", 200) < 400:
            ids = rr.json().get("recommended_ids", [])
            id_map = {b.get("id"): b for b in filtered_books if isinstance(b, dict)}
            recommended = [id_map.get(i) for i in ids if i in id_map]
            recommended = [b for b in recommended if b]
    except Exception:
        recommended = []

    filters = {
        "q": q,
        "publisher": publisher_filter,
        "min_price": min_price_raw,
        "max_price": max_price_raw,
    }

    return render(
        request,
        "catalogue.html",
        {
            "books": filtered_books,
            "publishers": publishers,
            "message": message,
            "filters": filters,
            "recommended_books": recommended,
        },
    )


# ──────────────────────────────── CUSTOMERS ──────────────────────────────

@login_required
def customer_list(request):
    # Admin, staff, manager đều có thể quản lý khách hàng
    if not (_is_admin(request.user) or _is_staff_user(request.user) or _is_manager(request.user)):
        return redirect("home")

    message = None

    if request.method == "POST":
        data = {
            "name":  request.POST.get("name"),
            "email": request.POST.get("email"),
        }
        try:
            r = _post(f"{CUSTOMER_SERVICE_URL}/customers/", data)
            if r.status_code == 200:
                return redirect("customer_list")
            message = {"type": "danger", "text": "Thêm thất bại! Email có thể đã tồn tại."}
        except Exception as e:
            message = {"type": "danger", "text": f"Lỗi kết nối customer-service: {e}"}

    customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
    if not isinstance(customers, list):
        customers = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối customer-service!"}

    return render(request, "customers.html", {"customers": customers, "message": message})


# ──────────────────────────────── STAFF ──────────────────────────────────

@login_required
def staff_list(request):
    if not _is_admin(request.user):
        return redirect("home")

    message = None
    if request.method == "POST":
        action = (request.POST.get("action") or "create").strip()

        if action == "toggle_active":
            staff_id = request.POST.get("staff_id")
            active = request.POST.get("active") == "1"
            email = (request.POST.get("email") or "").strip().lower()
            try:
                _patch(f"{STAFF_SERVICE_URL}/staff/{int(staff_id)}/", {"active": active})
            except Exception:
                pass
            if email:
                try:
                    u = User.objects.filter(username=email).first()
                    if u:
                        u.is_active = active
                        u.save(update_fields=["is_active"])
                except Exception:
                    pass
            return redirect("staff_list")

        if action == "delete":
            staff_id = request.POST.get("staff_id")
            email = (request.POST.get("email") or "").strip().lower()
            try:
                # delete record in staff-service
                try:
                    requests.delete(f"{STAFF_SERVICE_URL}/staff/{int(staff_id)}/", timeout=3)
                except Exception:
                    pass

                # delete or deactivate Django user
                u = User.objects.filter(username=email).first()
                if u:
                    u.is_active = False
                    u.save(update_fields=["is_active"])
                return redirect("staff_list")
            except Exception as e:
                message = {"type": "danger", "text": f"Xoá staff thất bại: {e}"}

        if action == "edit":
            staff_id = request.POST.get("staff_id")
            old_email = (request.POST.get("old_email") or "").strip().lower()
            name = (request.POST.get("name") or "").strip()
            email = (request.POST.get("email") or "").strip().lower()
            new_password = request.POST.get("new_password") or ""

            if not staff_id or not old_email or not name or not email:
                message = {"type": "danger", "text": "Thiếu thông tin (id/name/email)."}
            else:
                # First update staff-service record (avoid gateway/user changes if upstream rejects)
                try:
                    r = _patch(f"{STAFF_SERVICE_URL}/staff/{int(staff_id)}/", {"name": name, "email": email})
                    if getattr(r, "status_code", 200) >= 400:
                        message = {"type": "danger", "text": f"Cập nhật staff-service thất bại: {r.text}"}
                    else:
                        # Then update Django user
                        u = User.objects.filter(username=old_email).first()
                        if not u:
                            message = {"type": "danger", "text": "Không tìm thấy user đăng nhập theo email cũ."}
                        elif old_email != email and User.objects.filter(username=email).exists():
                            message = {"type": "danger", "text": "Email mới đã tồn tại trong hệ thống đăng nhập."}
                        else:
                            u.username = email
                            u.email = email
                            u.first_name = name
                            if new_password:
                                if len(new_password) < 6:
                                    raise ValueError("Mật khẩu mới phải >= 6 ký tự.")
                                u.set_password(new_password)
                            u.save()
                            return redirect("staff_list")
                except Exception as e:
                    message = {"type": "danger", "text": f"Cập nhật thất bại: {e}"}

        # create
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        if not name or not email or len(password) < 6:
            message = {"type": "danger", "text": "Vui lòng nhập Name/Email và mật khẩu >= 6 ký tự."}
        elif User.objects.filter(username=email).exists():
            message = {"type": "danger", "text": "Email này đã tồn tại trong hệ thống đăng nhập (api-gateway)."}
        else:
            try:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                staff_group, _ = Group.objects.get_or_create(name="staff")
                user.groups.add(staff_group)
            except Exception as e:
                message = {"type": "danger", "text": f"Tạo user đăng nhập thất bại: {e}"}
            else:
                try:
                    r = _post(f"{STAFF_SERVICE_URL}/staff/", {"name": name, "email": email})
                    if r.status_code == 201:
                        return redirect("staff_list")
                    message = {"type": "danger", "text": f"Tạo staff record thất bại: {r.text}"}
                except Exception as e:
                    message = {"type": "danger", "text": f"Lỗi kết nối staff-service: {e}"}

    staff = _get(f"{STAFF_SERVICE_URL}/staff/", [])
    if not isinstance(staff, list):
        staff = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối staff-service!"}

    # map login status by email
    email_list = [str(s.get("email", "")).lower() for s in staff if isinstance(s, dict)]
    user_map = {u.username.lower(): u for u in User.objects.filter(username__in=email_list)}
    for s in staff:
        u = user_map.get(str(s.get("email", "")).lower())
        if u:
            s["login_active"] = bool(u.is_active)
        else:
            s["login_active"] = False

    return render(request, "staff.html", {"staff": staff, "message": message})


# ──────────────────────────────── MANAGERS ───────────────────────────────

@login_required
def manager_list(request):
    if not _is_admin(request.user):
        return redirect("home")

    message = None
    if request.method == "POST":
        action = (request.POST.get("action") or "create").strip()

        if action == "toggle_active":
            manager_id = request.POST.get("manager_id")
            active = request.POST.get("active") == "1"
            email = (request.POST.get("email") or "").strip().lower()
            try:
                _patch(f"{MANAGER_SERVICE_URL}/managers/{int(manager_id)}/", {"active": active})
            except Exception:
                pass
            if email:
                try:
                    u = User.objects.filter(username=email).first()
                    if u:
                        u.is_active = active
                        u.save(update_fields=["is_active"])
                except Exception:
                    pass
            return redirect("manager_list")

        if action == "delete":
            manager_id = request.POST.get("manager_id")
            email = (request.POST.get("email") or "").strip().lower()
            try:
                try:
                    requests.delete(f"{MANAGER_SERVICE_URL}/managers/{int(manager_id)}/", timeout=3)
                except Exception:
                    pass

                u = User.objects.filter(username=email).first()
                if u:
                    u.is_active = False
                    u.save(update_fields=["is_active"])
                return redirect("manager_list")
            except Exception as e:
                message = {"type": "danger", "text": f"Xoá manager thất bại: {e}"}

        if action == "edit":
            manager_id = request.POST.get("manager_id")
            old_email = (request.POST.get("old_email") or "").strip().lower()
            name = (request.POST.get("name") or "").strip()
            email = (request.POST.get("email") or "").strip().lower()
            new_password = request.POST.get("new_password") or ""

            if not manager_id or not old_email or not name or not email:
                message = {"type": "danger", "text": "Thiếu thông tin (id/name/email)."}
            else:
                try:
                    r = _patch(f"{MANAGER_SERVICE_URL}/managers/{int(manager_id)}/", {"name": name, "email": email})
                    if getattr(r, "status_code", 200) >= 400:
                        message = {"type": "danger", "text": f"Cập nhật manager-service thất bại: {r.text}"}
                    else:
                        u = User.objects.filter(username=old_email).first()
                        if not u:
                            message = {"type": "danger", "text": "Không tìm thấy user đăng nhập theo email cũ."}
                        elif old_email != email and User.objects.filter(username=email).exists():
                            message = {"type": "danger", "text": "Email mới đã tồn tại trong hệ thống đăng nhập."}
                        else:
                            u.username = email
                            u.email = email
                            u.first_name = name
                            if new_password:
                                if len(new_password) < 6:
                                    raise ValueError("Mật khẩu mới phải >= 6 ký tự.")
                                u.set_password(new_password)
                            u.save()
                            return redirect("manager_list")
                except Exception as e:
                    message = {"type": "danger", "text": f"Cập nhật thất bại: {e}"}

        # create
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        if not name or not email or len(password) < 6:
            message = {"type": "danger", "text": "Vui lòng nhập Name/Email và mật khẩu >= 6 ký tự."}
        elif User.objects.filter(username=email).exists():
            message = {"type": "danger", "text": "Email này đã tồn tại trong hệ thống đăng nhập (api-gateway)."}
        else:
            try:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                manager_group, _ = Group.objects.get_or_create(name="manager")
                user.groups.add(manager_group)
            except Exception as e:
                message = {"type": "danger", "text": f"Tạo user đăng nhập thất bại: {e}"}
            else:
                try:
                    r = _post(f"{MANAGER_SERVICE_URL}/managers/", {"name": name, "email": email})
                    if r.status_code == 201:
                        return redirect("manager_list")
                    message = {"type": "danger", "text": f"Tạo manager record thất bại: {r.text}"}
                except Exception as e:
                    message = {"type": "danger", "text": f"Lỗi kết nối manager-service: {e}"}

    managers = _get(f"{MANAGER_SERVICE_URL}/managers/", [])
    if not isinstance(managers, list):
        managers = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối manager-service!"}

    email_list = [str(m.get("email", "")).lower() for m in managers if isinstance(m, dict)]
    user_map = {u.username.lower(): u for u in User.objects.filter(username__in=email_list)}
    for m in managers:
        u = user_map.get(str(m.get("email", "")).lower())
        if u:
            m["login_active"] = bool(u.is_active)
        else:
            m["login_active"] = False

    return render(request, "managers.html", {"managers": managers, "message": message})


# ──────────────────────────────── CART ───────────────────────────────────

@login_required
def cart_view(request, customer_id):
    # User chỉ được xem giỏ của chính mình
    if not request.user.is_staff:
        own_id = _get_customer_id(request.user)
        if own_id and own_id != customer_id:
            return redirect("cart_view", customer_id=own_id)

    message = None
    cart_id = None

    try:
        cart_info = requests.get(f"{CART_SERVICE_URL}/carts/customer/{customer_id}/", timeout=3).json()
        cart_id   = cart_info.get("id")
    except Exception:
        message = {"type": "danger", "text": "Không tìm thấy giỏ hàng của khách hàng này!"}

    if request.method == "POST":
        if cart_id:
            data = {
                "cart":     cart_id,
                "book_id":  int(request.POST.get("book_id")),
                "quantity": int(request.POST.get("quantity", 1)),
            }
            try:
                r = _post(f"{CART_SERVICE_URL}/carts/add-item/", data)
                if r.status_code == 200:
                    return redirect("cart_view", customer_id=customer_id)
                message = {"type": "danger", "text": "Thêm vào giỏ thất bại!"}
            except Exception as e:
                message = {"type": "danger", "text": f"Lỗi kết nối: {e}"}
        else:
            message = {"type": "danger", "text": "Không tìm thấy giỏ hàng!"}

    items      = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
    books      = _get(f"{BOOK_SERVICE_URL}/books/", [])
    clothes    = _get(f"{CLOTHE_SERVICE_URL}/clothes/", [])
    electronics = _get(f"{ELECTRONIC_SERVICE_URL}/electronics/", [])
    book_map      = {b["id"]: b for b in (books if isinstance(books, list) else [])}
    clothe_map    = {c["id"]: c for c in (clothes if isinstance(clothes, list) else [])}
    electronic_map = {e["id"]: e for e in (electronics if isinstance(electronics, list) else [])}
    total    = 0
    for item in (items if isinstance(items, list) else []):
        product = None
        if item.get("book_id"):
            product = book_map.get(item["book_id"])
            item["product_type"] = "book"
        elif item.get("clothing_id"):
            product = clothe_map.get(item["clothing_id"])
            item["product_type"] = "clothing"
        elif item.get("electronic_id"):
            product = electronic_map.get(item["electronic_id"])
            item["product_type"] = "electronic"
        else:
            item["product_type"] = "unknown"

        item["product"] = product or {}
        price = 0.0
        if isinstance(product, dict):
            # cả book và clothing đều dùng field price
            try:
                price = float(product.get("price", 0))
            except Exception:
                price = 0.0
        item["subtotal"] = price * item.get("quantity", 0)
        total           += item["subtotal"]

    return render(request, "cart.html", {
        "items":       items if isinstance(items, list) else [],
        "books":       books if isinstance(books, list) else [],
        "customer_id": customer_id,
        "cart_id":     cart_id,
        "total":       total,
        "message":     message,
    })


# ──────────────────────────────── ORDERS ─────────────────────────────────

@login_required
def order_list(request):
    # Admin / Manager / Staff: xem tất cả đơn
    if _can_manage_books(request.user):
        orders    = _get(f"{ORDER_SERVICE_URL}/orders/", [])
        customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
        cust_map  = {c["id"]: c for c in (customers if isinstance(customers, list) else [])}
        for order in (orders if isinstance(orders, list) else []):
            order["customer"] = cust_map.get(order.get("customer_id"), {})
        return render(request, "orders.html", {
            "orders":   orders if isinstance(orders, list) else [],
            "is_admin": True,
        })

    # Khách hàng: chỉ xem đơn của mình
    customer_id = _get_customer_id(request.user)
    orders = []
    if customer_id:
        orders = _get(f"{ORDER_SERVICE_URL}/orders/customer/{customer_id}/", [])
    return render(request, "orders.html", {
        "orders":   orders if isinstance(orders, list) else [],
        "is_admin": False,
    })


@login_required
def order_checkout(request, customer_id):
    if request.method != "POST":
        return redirect("cart_view", customer_id=customer_id)

    # User chỉ checkout giỏ của chính mình
    if not request.user.is_staff:
        own_id = _get_customer_id(request.user)
        if own_id and own_id != customer_id:
            return redirect("home")

    items    = _get(f"{CART_SERVICE_URL}/carts/{customer_id}/", [])
    books    = _get(f"{BOOK_SERVICE_URL}/books/", [])
    book_map = {b["id"]: b for b in (books if isinstance(books, list) else [])}

    order_items = []
    total       = 0
    for item in (items if isinstance(items, list) else []):
        book = book_map.get(item["book_id"], {})
        if not book:
            continue
        price    = float(book["price"])
        total   += price * item["quantity"]
        order_items.append({
            "book_id":        item["book_id"],
            "quantity":       item["quantity"],
            "price_at_order": price,
        })

    if not order_items:
        return redirect("cart_view", customer_id=customer_id)

    try:
        r = _post(f"{ORDER_SERVICE_URL}/orders/create/", {
            "customer_id":  customer_id,
            "total_amount": round(total, 2),
            "items":        order_items,
        })
        if r.status_code == 201:
            order_id = r.json().get("id")

            # Đọc lựa chọn payment / shipping từ form
            payment_method   = (request.POST.get("payment_method") or "cod").strip() or "cod"
            shipment_carrier = (request.POST.get("shipment_carrier") or "").strip()
            shipment_address = (request.POST.get("shipment_address") or "").strip()
            shipment_phone   = (request.POST.get("shipment_phone") or "").strip()

            # Best-effort: tạo payment dựa trên lựa chọn
            try:
                _post(f"{PAY_SERVICE_URL}/payments/create/", {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "amount": round(total, 2),
                    "method": payment_method,
                })
            except Exception:
                pass

            # Best-effort: tạo shipment với carrier/address/phone đã chọn
            try:
                customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
                cust_map = {c["id"]: c for c in (customers if isinstance(customers, list) else [])}
                cust = cust_map.get(int(customer_id), {})
                _post(f"{SHIP_SERVICE_URL}/shipments/create/", {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "receiver_name": cust.get("name", "") or "",
                    "address": shipment_address,
                    "phone": shipment_phone,
                    "carrier": shipment_carrier,
                })
            except Exception:
                pass

            return redirect("order_detail", order_id=order_id)
    except Exception:
        pass

    return redirect("cart_view", customer_id=customer_id)


@login_required
def order_detail(request, order_id):
    message = None

    order = _get(f"{ORDER_SERVICE_URL}/orders/{order_id}/", {})
    if not isinstance(order, dict) or not order:
        return redirect("order_list")

    # Khách hàng chỉ xem đơn của chính mình; admin/manager/staff xem tất cả
    if not _can_manage_books(request.user):
        own_id = _get_customer_id(request.user)
        if own_id and order.get("customer_id") != own_id:
            return redirect("order_list")

    if request.method == "POST":
        # Admin / Manager / Staff được phép đổi trạng thái
        if not _can_manage_books(request.user):
            return redirect("order_detail", order_id=order_id)
        try:
            action = request.POST.get("action") or "order_status"
            if action == "order_status":
                new_status = request.POST.get("status")
                _patch(f"{ORDER_SERVICE_URL}/orders/{order_id}/status/", {"status": new_status})
            elif action == "payment_status":
                payment_id = request.POST.get("payment_id")
                payment_status = request.POST.get("payment_status")
                _patch(f"{PAY_SERVICE_URL}/payments/{payment_id}/status/", {"status": payment_status})
            elif action == "shipment_status":
                shipment_id = request.POST.get("shipment_id")
                shipment_status = request.POST.get("shipment_status")
                _patch(f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/status/", {"status": shipment_status})
            return redirect("order_detail", order_id=order_id)
        except Exception as e:
            message = {"type": "danger", "text": f"Cập nhật thất bại: {e}"}

    books    = _get(f"{BOOK_SERVICE_URL}/books/", [])
    book_map = {b["id"]: b for b in (books if isinstance(books, list) else [])}
    for item in order.get("items", []):
        item["book"] = book_map.get(item["book_id"], {})

    customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
    cust_map  = {c["id"]: c for c in (customers if isinstance(customers, list) else [])}
    order["customer"] = cust_map.get(order.get("customer_id"), {})

    payments = _get(f"{PAY_SERVICE_URL}/payments/order/{order_id}/", [])
    shipments = _get(f"{SHIP_SERVICE_URL}/shipments/order/{order_id}/", [])

    return render(request, "order_detail.html", {
        "order":          order,
        "status_choices": ['pending', 'confirmed', 'shipping', 'delivered', 'cancelled'],
        "message":        message,
        "payments":       payments if isinstance(payments, list) else [],
        "shipments":      shipments if isinstance(shipments, list) else [],
        "payment_status_choices": ['initiated', 'paid', 'failed', 'refunded', 'cancelled'],
        "shipment_status_choices": ['pending', 'picked', 'shipping', 'delivered', 'failed', 'cancelled'],
    })


# ──────────────────────────────── PAYMENTS ───────────────────────────────

@login_required
def payment_list(request):
    if request.user.is_staff:
        payments = _get(f"{PAY_SERVICE_URL}/payments/", [])
        return render(request, "payments.html", {"payments": payments if isinstance(payments, list) else [], "is_admin": True})

    customer_id = _get_customer_id(request.user)
    payments = []
    if customer_id:
        payments = _get(f"{PAY_SERVICE_URL}/payments/customer/{customer_id}/", [])
    return render(request, "payments.html", {"payments": payments if isinstance(payments, list) else [], "is_admin": False})


# ──────────────────────────────── SHIPMENTS ───────────────────────────────

@login_required
def shipment_list(request):
    if request.user.is_staff:
        shipments = _get(f"{SHIP_SERVICE_URL}/shipments/", [])
        return render(request, "shipments.html", {"shipments": shipments if isinstance(shipments, list) else [], "is_admin": True})

    customer_id = _get_customer_id(request.user)
    shipments = []
    if customer_id:
        shipments = _get(f"{SHIP_SERVICE_URL}/shipments/customer/{customer_id}/", [])
    return render(request, "shipments.html", {"shipments": shipments if isinstance(shipments, list) else [], "is_admin": False})


# ──────────────────────────────── PUBLISHERS ─────────────────────────────

@login_required
def publisher_edit(request, publisher_id):
    if not request.user.is_staff:
        return redirect("home")
    if request.method != "POST":
        return redirect("publisher_list")

    data = {
        "name":    request.POST.get("name", "").strip(),
        "address": request.POST.get("address", "").strip(),
        "mail":    request.POST.get("mail", "").strip(),
    }

    try:
        requests.put(f"{BOOK_SERVICE_URL}/publishers/{publisher_id}/", json=data, timeout=3)
    except Exception:
        pass
    return redirect("publisher_list")


# ──────────────────────────────── REVIEWS ────────────────────────────────

@login_required
def review_list(request):
    message = None

    if request.method == "POST":
        book_id     = request.POST.get("book_id")
        customer_id = request.POST.get("customer_id")
        rating      = request.POST.get("rating")
        comment     = request.POST.get("comment", "")

        # Nếu là user thường, dùng customer_id của chính họ
        if not request.user.is_staff:
            customer_id = str(_get_customer_id(request.user) or "")

        customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])
        cust_map  = {str(c["id"]): c for c in (customers if isinstance(customers, list) else [])}
        books     = _get(f"{BOOK_SERVICE_URL}/books/", [])
        book_map  = {str(b["id"]): b for b in (books if isinstance(books, list) else [])}

        data = {
            "book_id":       int(book_id),
            "customer_id":   int(customer_id),
            "customer_name": cust_map.get(customer_id, {}).get("name", "Khách hàng"),
            "book_title":    book_map.get(book_id, {}).get("title", ""),
            "rating":        int(rating),
            "comment":       comment,
        }
        try:
            r = _post(f"{REVIEW_SERVICE_URL}/reviews/", data)
            if r.status_code == 201:
                return redirect("review_list")
            message = {"type": "danger", "text": "Gửi đánh giá thất bại!"}
        except Exception as e:
            message = {"type": "danger", "text": f"Lỗi kết nối: {e}"}

    reviews   = _get(f"{REVIEW_SERVICE_URL}/reviews/", [])
    books     = _get(f"{BOOK_SERVICE_URL}/books/", [])
    customers = _get(f"{CUSTOMER_SERVICE_URL}/customers/", [])

    return render(request, "reviews.html", {
        "reviews":   reviews   if isinstance(reviews, list)   else [],
        "books":     books     if isinstance(books, list)     else [],
        "customers": customers if isinstance(customers, list) else [],
        "message":   message,
    })


# ──────────────────────────────── PUBLISHERS ─────────────────────────────

@login_required
def publisher_list(request):
    if not request.user.is_staff:
        return redirect("home")

    message = None

    if request.method == "POST":
        data = {
            "name":    request.POST.get("name", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "mail":    request.POST.get("mail", "").strip(),
        }
        try:
            r = _post(f"{BOOK_SERVICE_URL}/publishers/", data)
            if r.status_code == 201:
                return redirect("publisher_list")
            message = {"type": "danger", "text": f"Thêm thất bại: {r.text}"}
        except Exception as e:
            message = {"type": "danger", "text": f"Lỗi kết nối book-service: {e}"}

    publishers = _get(f"{BOOK_SERVICE_URL}/publishers/", [])
    if not isinstance(publishers, list):
        publishers = []
        if message is None:
            message = {"type": "warning", "text": "Không thể kết nối book-service!"}

    return render(request, "publishers.html", {"publishers": publishers, "message": message})


# ──────────────────────────────── BOOK EDIT ──────────────────────────────

@login_required
def book_edit(request, book_id):
    if not request.user.is_staff:
        return redirect("book_list")

    if request.method == "POST":
        try:
            stock_val = int(request.POST.get("stock") or 0)
            price_val = float(request.POST.get("price") or 0)
        except (ValueError, TypeError):
            return redirect("book_list")

        data = {
            "title":     request.POST.get("title", "").strip(),
            "author":    request.POST.get("author", "").strip(),
            "price":     price_val,
            "stock":     stock_val,
            "publisher": int(request.POST.get("publisher")) if request.POST.get("publisher") else None,
        }
        try:
            requests.put(f"{BOOK_SERVICE_URL}/books/{book_id}/", json=data, timeout=3)
        except Exception:
            pass

    return redirect("book_list")

