"""
Rule-based Behaviour Scoring Engine
Phân tích hành vi khách hàng và xây dựng UserProfile
"""
from django.conf import settings
from .models import BehaviourLog, UserProfile
from collections import defaultdict
from decimal import Decimal


WEIGHTS = {
    'view_product':     0.3,
    'search':           0.2,
    'add_to_cart':      1.0,
    'remove_from_cart': -0.3,
    'checkout':         2.0,
}

BRAND_KEYWORDS = {
    'apple':    ['apple', 'macbook', 'iphone', 'ipad', 'mac'],
    'dell':     ['dell', 'inspiron', 'xps', 'latitude', 'alienware'],
    'hp':       ['hp', 'pavilion', 'spectre', 'envy', 'omen', 'elitebook'],
    'lenovo':   ['lenovo', 'thinkpad', 'ideapad', 'yoga', 'legion'],
    'asus':     ['asus', 'vivobook', 'zenbook', 'rog', 'tuf'],
    'acer':     ['acer', 'aspire', 'swift', 'predator', 'nitro'],
    'samsung':  ['samsung', 'galaxy'],
    'xiaomi':   ['xiaomi', 'redmi', 'mi ', 'poco'],
    'oppo':     ['oppo', 'reno', 'find'],
    'vivo':     ['vivo', 'v-series', 'x-series'],
    'realme':   ['realme'],
    'nokia':    ['nokia'],
    'sony':     ['sony', 'xperia'],
    'lg':       ['lg'],
    'huawei':   ['huawei', 'mate', 'p-series'],
}

USECASE_KEYWORDS = {
    'gaming':    ['gaming', 'game', 'rtx', 'gtx', 'rog', 'tuf', 'predator', 'nitro', 'legion', 'alienware', 'omen'],
    'student':   ['student', 'sinh viên', 'học sinh', 'học', 'nhẹ', 'pin tốt', 'giá rẻ'],
    'office':    ['văn phòng', 'office', 'thinkpad', 'latitude', 'elitebook', 'business'],
    'creative':  ['đồ họa', 'design', 'creative', 'macbook', 'colorful', 'sRGB', 'video editing'],
    'developer': ['lập trình', 'developer', 'code', 'ram cao', 'thinkpad', 'xps'],
    'budget':    ['giá rẻ', 'tiết kiệm', 'budget', 'phổ thông', 'dưới 10', 'dưới 15'],
    'premium':   ['cao cấp', 'premium', 'flagship', 'macbook pro', 'xps', 'spectre', 'ultrabook'],
    'photography': ['camera', 'chụp ảnh', 'photography', 'hasselblad', 'zeiss', 'ois'],
}


def compute_profile(customer_id: int) -> UserProfile:
    """Tính lại UserProfile từ toàn bộ BehaviourLog của customer"""
    logs = BehaviourLog.objects.filter(customer_id=customer_id)

    type_scores   = defaultdict(float)
    brand_scores  = defaultdict(float)
    usecase_scores = defaultdict(float)
    product_scores = defaultdict(lambda: {'score': 0.0, 'type': '', 'name': ''})
    prices = []

    for log in logs:
        w = WEIGHTS.get(log.action, 0.1)
        ptype = log.product_type.lower()

        # Score theo loại sản phẩm
        type_scores[ptype] += w

        # Score theo sản phẩm cụ thể
        key = f"{log.product_type}_{log.product_id}"
        product_scores[key]['score'] += w
        product_scores[key]['type']   = log.product_type
        product_scores[key]['name']   = log.product_name
        product_scores[key]['id']     = log.product_id

        # Trích xuất brand từ tên sản phẩm
        name_lower = (log.product_name + ' ' + log.search_query).lower()
        for brand, kws in BRAND_KEYWORDS.items():
            if any(kw in name_lower for kw in kws):
                brand_scores[brand] += w

        # Trích xuất use-case từ search query + tên sản phẩm
        for uc, kws in USECASE_KEYWORDS.items():
            if any(kw in name_lower for kw in kws):
                usecase_scores[uc] += w

        if log.price and log.price > 0:
            prices.append(float(log.price))

    # Top brands (≥1 điểm)
    top_brands = sorted(
        [b for b, s in brand_scores.items() if s >= 0.5],
        key=lambda b: brand_scores[b], reverse=True
    )[:5]

    # Top use-cases
    top_usecases = sorted(
        [u for u, s in usecase_scores.items() if s >= 0.3],
        key=lambda u: usecase_scores[u], reverse=True
    )[:4]

    # Top sản phẩm quan tâm
    top_products = sorted(
        product_scores.values(), key=lambda x: x['score'], reverse=True
    )[:10]

    avg_price = Decimal(str(round(sum(prices) / len(prices), 0))) if prices else Decimal('0')

    profile, _ = UserProfile.objects.update_or_create(
        customer_id=customer_id,
        defaults={
            'laptop_score':       type_scores.get('laptop', 0.0),
            'mobile_score':       type_scores.get('mobile', 0.0),
            'budget_avg':         avg_price,
            'preferred_brands':   top_brands,
            'preferred_usecases': top_usecases,
            'top_products':       list(top_products),
            'total_events':       logs.count(),
        }
    )
    return profile


def get_profile_summary(customer_id: int) -> str:
    """Trả về mô tả ngắn hồ sơ user để đưa vào RAG prompt"""
    try:
        p = UserProfile.objects.get(customer_id=customer_id)
    except UserProfile.DoesNotExist:
        return "Khách hàng mới, chưa có lịch sử mua sắm."

    parts = []

    # Sở thích loại sản phẩm
    if p.laptop_score > p.mobile_score and p.laptop_score > 0:
        parts.append(f"Khách hàng có xu hướng quan tâm đến laptop (điểm {p.laptop_score:.1f})")
    elif p.mobile_score > p.laptop_score and p.mobile_score > 0:
        parts.append(f"Khách hàng có xu hướng quan tâm đến điện thoại (điểm {p.mobile_score:.1f})")
    elif p.laptop_score > 0 and p.mobile_score > 0:
        parts.append("Khách hàng quan tâm cả laptop lẫn điện thoại")

    # Ngân sách
    if p.budget_avg > 0:
        budget_m = float(p.budget_avg) / 1_000_000
        parts.append(f"Mức giá thường xem khoảng {budget_m:.0f} triệu đồng")

    # Thương hiệu
    if p.preferred_brands:
        parts.append(f"Ưa thích thương hiệu: {', '.join(p.preferred_brands)}")

    # Use-case
    if p.preferred_usecases:
        parts.append(f"Nhu cầu sử dụng: {', '.join(p.preferred_usecases)}")

    return '. '.join(parts) + '.' if parts else "Khách hàng chưa có đủ thông tin hành vi."
