import json
from decimal import Decimal
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .models import Cart, CartItem, Customer, CustomerAccount
def _body(request):
    return json.loads(request.body.decode("utf-8")) if request.body else {}
def _auth(request):
    h = request.headers.get("Authorization","")
    if not h.startswith("Bearer "):
        return None
    t = h.replace("Bearer ","",1)
    try:
        u = signing.TimestampSigner().unsign(t, max_age=28800)
    except signing.BadSignature:
        return None
    return CustomerAccount.objects.filter(username=u).first()
@require_GET
def info(_request):
    return JsonResponse({"service":"customer","count":Customer.objects.count()})
@csrf_exempt
@require_POST
def register(request):
    p = _body(request)
    c = Customer.objects.create(full_name=p["full_name"], phone=p["phone"], email=p["email"])
    a = CustomerAccount.objects.create(username=p["username"], password_hash=make_password(p["password"]), customer=c)
    return JsonResponse({"customer_id":c.id,"account_id":a.id}, status=201)
@csrf_exempt
@require_POST
def login(request):
    p = _body(request)
    a = CustomerAccount.objects.filter(username=p.get("username")).first()
    if not a or not check_password(p.get("password",""), a.password_hash):
        return JsonResponse({"error":"Invalid credentials"}, status=401)
    return JsonResponse({"access_token": signing.TimestampSigner().sign(a.username)})
@require_GET
def search(request):
    q = request.GET.get("q","").strip()
    qs = Customer.objects.filter(Q(full_name__icontains=q)|Q(email__icontains=q)) if q else Customer.objects.all()
    return JsonResponse({"items":[{"id":x.id,"full_name":x.full_name,"phone":x.phone,"email":x.email} for x in qs[:50]]})
@csrf_exempt
@require_http_methods(["GET", "POST"])
def create_cart(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    if request.method == "POST":
        p = _body(request)
        c = Cart.objects.create(account=a, name=p.get("name","default"), is_active=True)
        return JsonResponse({"cart_id":c.id}, status=201)
    else:
        c = _active(a)
        if not c:
            return JsonResponse({"items":[], "total_price": 0})
        items = CartItem.objects.filter(cart=c)
        item_list = [{"id": i.id, "product_id": i.product_id, "product_type": i.product_type, "product_name": i.product_name, "price": float(i.unit_price), "quantity": i.quantity} for i in items]
        total = sum((i.unit_price * i.quantity for i in items), Decimal("0.0"))
        return JsonResponse({"items": item_list, "total_price": float(total)})
def _active(account):
    return Cart.objects.filter(account=account, is_active=True).order_by("-id").first()
@csrf_exempt
@require_POST
def add_item(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    p = _body(request)
    c = _active(a) or Cart.objects.create(account=a, name="default", is_active=True)
    i = CartItem.objects.create(cart=c, product_type=p["product_type"], product_id=int(p["product_id"]), product_name=p["product_name"], unit_price=Decimal(str(p["unit_price"])), quantity=int(p["quantity"]))
    return JsonResponse({"item_id":i.id}, status=201)
@csrf_exempt
@require_http_methods(["PATCH"])
def update_item(request, item_id):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    p = _body(request)
    i = CartItem.objects.filter(id=item_id, cart__account=a, cart__is_active=True).first()
    if not i:
        return JsonResponse({"error":"Not found"}, status=404)
    i.quantity = int(p["quantity"])
    i.save(update_fields=["quantity"])
    return JsonResponse({"ok":True})
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_item(request, item_id):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    i = CartItem.objects.filter(id=item_id, cart__account=a, cart__is_active=True).first()
    if not i:
        return JsonResponse({"error":"Not found"}, status=404)
    i.delete()
    return JsonResponse({"ok":True})
@csrf_exempt
@require_POST
def checkout(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    c = _active(a)
    if not c:
        return JsonResponse({"error":"No active cart"}, status=404)
    c.is_active = False
    c.save(update_fields=["is_active"])
    return JsonResponse({"ok":True,"cart_id":c.id})

@csrf_exempt
@require_GET
def get_profile(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    return JsonResponse({"username":a.username, "full_name":a.customer.full_name, "email":a.customer.email, "phone":a.customer.phone})

@csrf_exempt
@require_http_methods(["PUT", "POST"])
def update_profile(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    p = _body(request)
    c = a.customer
    if "full_name" in p: c.full_name = p["full_name"]
    if "email" in p: c.email = p["email"]
    if "phone" in p: c.phone = p["phone"]
    c.save()
    return JsonResponse({"success":True})
