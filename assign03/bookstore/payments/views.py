from django.shortcuts import render, redirect, get_object_or_404
from .models import Payment, PaymentMethod
from orders.models import Order

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Simulate payment processing
        method_name = request.POST.get('method', 'COD')
        method = PaymentMethod.objects.filter(name=method_name).first()
        if not method:
            method = PaymentMethod.objects.create(name=method_name)

        payment = Payment.objects.create(
            order=order,
            method=method,
            amount=order.total_amount,
            status="SUCCESS" # Auto success for demo
        )

        return redirect("order_success", order_id=order.id)
        
    return render(request, 'payments/payment.html', {'order': order})
