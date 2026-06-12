from app.models import Cart

def handle_customer_created(data):
    customer_id = data.get('customer_id')
    if customer_id:
        try:
            cart, created = Cart.objects.get_or_create(customer_id=customer_id)
            if created:
                print(f"[Cart Service] Asynchronously created cart for customer {customer_id}")
            else:
                print(f"[Cart Service] Cart already exists for customer {customer_id}")
        except Exception as e:
            print(f"[Cart Service] Error handling customer_created: {e}")
