import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Laptop
@require_GET
def info(_request):
    return JsonResponse({"service":"laptop","count":Laptop.objects.count()})
@require_GET
def list_products(_request):
    return JsonResponse({"items":[{"id":x.id,"model_name":x.model_name,"cpu":x.cpu,"ram_gb":x.ram_gb,"price":str(x.price)} for x in Laptop.objects.all()[:100]]})
@csrf_exempt
@require_POST
def create_product(request):
    p = json.loads(request.body.decode("utf-8"))
    obj = Laptop.objects.create(model_name=p["model_name"], cpu=p["cpu"], ram_gb=int(p["ram_gb"]), price=Decimal(str(p["price"])))
    return JsonResponse({"id":obj.id,"model_name":obj.model_name}, status=201)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product(_request, id):
    try:
        Laptop.objects.get(id=id).delete()
        return JsonResponse({"success":True})
    except Laptop.DoesNotExist:
        return JsonResponse({"error":"not found"}, status=404)

@csrf_exempt
@require_http_methods(["PUT", "POST"])
def update_product(request, id):
    try:
        obj = Laptop.objects.get(id=id)
        p = json.loads(request.body.decode("utf-8"))
        if "model_name" in p: obj.model_name = p["model_name"]
        if "cpu" in p: obj.cpu = p["cpu"]
        if "ram_gb" in p: obj.ram_gb = int(p["ram_gb"])
        if "price" in p: obj.price = Decimal(str(p["price"]))
        obj.save()
        return JsonResponse({"success":True})
    except Laptop.DoesNotExist:
        return JsonResponse({"error":"not found"}, status=404)

