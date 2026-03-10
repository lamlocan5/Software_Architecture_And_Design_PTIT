from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from .services import OrderService
from .models import Order
from shipping.models import Shipment

@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('book_list')

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        
        full_address = f"{full_name}, {address}, {city}. Phone: {phone}"

        cart_items = cart.items.all()
        if not cart_items:
            return redirect('book_list')

        # Create Order
        order = OrderService.create_order(request.user, cart_items)
        
        # Create Shipment
        Shipment.objects.create(
            order=order,
            address=full_address,
            status="PENDING"
        )
        
        # Clear Cart
        cart_items.delete()
        cart.total_price = 0
        cart.save()
        
        return redirect("process_payment", order_id=order.id)

    # Compute total for display (if not already up to date)
    cart.compute_total()
    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/order_list.html', {'orders': orders})
