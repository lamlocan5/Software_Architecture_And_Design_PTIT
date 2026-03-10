from .models import Order, OrderItem, OrderStatus

class OrderService:
    @staticmethod
    def create_order(user, cart_items):
        status_new = OrderStatus.objects.filter(name="NEW").first()
        if not status_new:
            status_new = OrderStatus.objects.create(name="NEW")
        order = Order.objects.create(user=user, status=status_new, total_amount=0)

        total = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.price
            )
            total += item.price * item.quantity

        order.total_amount = total
        order.save()
        return order
