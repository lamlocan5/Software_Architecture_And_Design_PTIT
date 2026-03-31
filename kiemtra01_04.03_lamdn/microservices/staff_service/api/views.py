import json
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.http import JsonResponse
from django.core import signing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Staff, StaffAccount
@require_GET
def info(_request):
    return JsonResponse({"service":"staff","count":Staff.objects.count()})
def _body(request):
    return json.loads(request.body.decode("utf-8")) if request.body else {}
@csrf_exempt
@require_POST
def register_staff(request):
    p = _body(request)
    s = Staff.objects.create(full_name=p["full_name"], position=p["position"], email=p["email"])
    a = StaffAccount.objects.create(username=p["username"], password_hash=make_password(p["password"]), staff=s)
    return JsonResponse({"staff_id":s.id,"account_id":a.id}, status=201)
@csrf_exempt
@require_POST
def login_staff(request):
    p = _body(request)
    a = StaffAccount.objects.filter(username=p.get("username")).first()
    if not a or not check_password(p.get("password",""), a.password_hash):
        return JsonResponse({"error":"Invalid credentials"}, status=401)
    return JsonResponse({"access_token": signing.TimestampSigner().sign(a.username)})

def _auth(request):
    h = request.headers.get("Authorization","")
    if not h.startswith("Bearer "):
        return None
    t = h.replace("Bearer ","",1)
    try:
        u = signing.TimestampSigner().unsign(t, max_age=28800)
    except signing.BadSignature:
        return None
    return StaffAccount.objects.filter(username=u).first()

@csrf_exempt
@require_GET
def get_profile(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    return JsonResponse({"username":a.username, "full_name":a.staff.full_name, "email":a.staff.email, "position":a.staff.position})

@csrf_exempt
@require_http_methods(["PUT", "POST"])
def update_profile(request):
    a = _auth(request)
    if not a:
        return JsonResponse({"error":"Unauthorized"}, status=401)
    p = _body(request)
    s = a.staff
    if "full_name" in p: s.full_name = p["full_name"]
    if "email" in p: s.email = p["email"]
    if "position" in p: s.position = p["position"]
    s.save()
    return JsonResponse({"success":True})
