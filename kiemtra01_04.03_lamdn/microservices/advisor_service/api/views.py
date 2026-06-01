import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import BehaviourLog, ChatHistory, UserProfile
from .behaviour import compute_profile, get_profile_summary
from .rag import chat as rag_chat


def _body(req):
    return json.loads(req.body.decode()) if req.body else {}


# ─── INFO ──────────────────────────────────────────────────────────────────────
@require_GET
def info(_req):
    from api.chroma_client import get_laptop_collection, get_mobile_collection, get_advisory_collection
    try:
        lap_count = get_laptop_collection().count()
        mob_count = get_mobile_collection().count()
        adv_count = get_advisory_collection().count()
        kb_status = {"laptops": lap_count, "mobiles": mob_count, "advisory": adv_count}
    except Exception as e:
        kb_status = {"error": str(e)}
    return JsonResponse({
        "service": "advisor",
        "kb": kb_status,
        "logs": BehaviourLog.objects.count(),
        "profiles": UserProfile.objects.count(),
    })


# ─── BEHAVIOUR TRACKING ────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def track(request):
    """Ghi nhận hành vi khách hàng"""
    p = _body(request)
    required = ['customer_id', 'product_id', 'product_type', 'action']
    for f in required:
        if f not in p:
            return JsonResponse({'error': f'Missing field: {f}'}, status=400)
    if p['action'] not in dict(BehaviourLog.ACTION_CHOICES):
        return JsonResponse({'error': 'Invalid action'}, status=400)

    log = BehaviourLog.objects.create(
        customer_id  = p['customer_id'],
        product_id   = p['product_id'],
        product_type = p['product_type'],
        product_name = p.get('product_name', ''),
        action       = p['action'],
        search_query = p.get('search_query', ''),
        price        = p.get('price'),
    )

    # Tính lại profile sau mỗi event
    try:
        compute_profile(p['customer_id'])
    except Exception:
        pass

    return JsonResponse({'ok': True, 'log_id': log.id}, status=201)


# ─── RECOMMENDATIONS ───────────────────────────────────────────────────────────
@require_GET
def recommendations(request):
    """Trả về top sản phẩm gợi ý dựa trên profile"""
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'customer_id required'}, status=400)
    try:
        profile = UserProfile.objects.get(customer_id=int(customer_id))
        return JsonResponse({
            'customer_id':        int(customer_id),
            'laptop_score':       profile.laptop_score,
            'mobile_score':       profile.mobile_score,
            'budget_avg':         float(profile.budget_avg),
            'preferred_brands':   profile.preferred_brands,
            'preferred_usecases': profile.preferred_usecases,
            'top_products':       profile.top_products,
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'No profile found', 'customer_id': int(customer_id)}, status=404)


# ─── CHAT ──────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def chat(request):
    """Chat tư vấn — RAG pipeline"""
    p = _body(request)
    query = p.get('query', '').strip()
    if not query:
        return JsonResponse({'error': 'query is required'}, status=400)

    customer_id = p.get('customer_id')
    session_id  = p.get('session_id') or str(uuid.uuid4())

    # Lấy lịch sử chat của session
    history = []
    if session_id:
        history = list(
            ChatHistory.objects.filter(session_id=session_id)
            .values('role', 'content')
            .order_by('created_at')[:12]
        )

    # Gọi RAG pipeline
    result = rag_chat(query=query, customer_id=int(customer_id) if customer_id else None, history=history)

    # Lưu lịch sử
    if session_id:
        ChatHistory.objects.create(session_id=session_id, customer_id=customer_id or 0, role='user', content=query)
        ChatHistory.objects.create(session_id=session_id, customer_id=customer_id or 0, role='assistant', content=result['response'])

    return JsonResponse({
        'session_id': session_id,
        'response':   result['response'],
        'intent':     result.get('intent', {}),
    })


# ─── CHAT HISTORY ──────────────────────────────────────────────────────────────
@require_GET
def chat_history(request):
    session_id = request.GET.get('session_id')
    customer_id = request.GET.get('customer_id')
    if not session_id and not customer_id:
        return JsonResponse({'error': 'session_id or customer_id required'}, status=400)

    qs = ChatHistory.objects.all()
    if session_id:
        qs = qs.filter(session_id=session_id)
    if customer_id:
        qs = qs.filter(customer_id=int(customer_id))

    messages = list(qs.values('role', 'content', 'created_at', 'session_id').order_by('created_at')[:50])
    return JsonResponse({'messages': messages})


# ─── KB REBUILD ────────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def kb_rebuild(request):
    """Rebuild Knowledge Base — seed lại ChromaDB"""
    try:
        from api.seed_kb import seed_all
        seed_all()
        return JsonResponse({'ok': True, 'message': 'KB rebuilt successfully'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
