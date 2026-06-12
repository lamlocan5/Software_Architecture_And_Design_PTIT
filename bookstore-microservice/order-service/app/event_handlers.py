from app.models import Order

def handle_payment_processed(data):
    order_id = data.get('order_id')
    status = data.get('status')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if status == 'paid':
                order.status = 'confirmed'
                order.save()
                print(f"[Order Service] Asynchronously updated order {order_id} status to 'confirmed' due to successful payment")
            elif status in ('failed', 'cancelled'):
                order.status = 'cancelled'
                order.save()
                print(f"[Order Service] Asynchronously updated order {order_id} status to 'cancelled' due to payment failure")
        except Order.DoesNotExist:
            print(f"[Order Service] Order {order_id} not found for payment status update")
        except Exception as e:
            print(f"[Order Service] Error handling payment_processed: {e}")
