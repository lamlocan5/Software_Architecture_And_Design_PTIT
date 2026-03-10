"""
Order Controller (Views)
Handles cart, wishlist, checkout, and order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from store.models.order import Cart, Wishlist, Order, OrderItem, Shipping
from store.models.customer import Customer, Address
from store.models.book import Book


def view_cart(request):
    """View shopping cart"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to view cart')
        return redirect('customer_login')
    
    cart_items = Cart.objects.filter(customer_id=customer_id).select_related('book')
    
    # Calculate totals
    subtotal = sum(item.subtotal for item in cart_items)
    shipping_cost = 30000  # Fixed shipping cost (30,000 VND)
    total = subtotal + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    return render(request, 'cart/view.html', context)


def add_to_cart(request, book_id):
    """Add book to cart"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to add items to cart')
        return redirect('customer_login')
    
    book = get_object_or_404(Book, book_id=book_id)
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Check stock
    if book.stock <= 0:
        messages.error(request, 'Book is out of stock')
        return redirect('book_detail', book_id=book_id)
    
    # Check if already in cart
    cart_item, created = Cart.objects.get_or_create(
        customer=customer,
        book=book,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Update quantity if already in cart
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Cart updated')
        else:
            messages.error(request, 'Cannot add more than available stock')
    else:
        messages.success(request, 'Book added to cart')
    
    return redirect('view_cart')


def update_cart(request, cart_id):
    """Update cart item quantity"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    cart_item = get_object_or_404(Cart, cart_id=cart_id, customer_id=customer_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')
        elif quantity <= cart_item.book.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated')
        else:
            messages.error(request, 'Quantity exceeds available stock')
    
    return redirect('view_cart')


def remove_from_cart(request, cart_id):
    """Remove item from cart"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    cart_item = get_object_or_404(Cart, cart_id=cart_id, customer_id=customer_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('view_cart')


def checkout(request):
    """Checkout process"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to checkout')
        return redirect('customer_login')
    
    customer = get_object_or_404(Customer, customer_id=customer_id)
    cart_items = Cart.objects.filter(customer=customer).select_related('book')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('view_cart')
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        shipping_method = request.POST.get('shipping_method', 'Standard')
        
        address = get_object_or_404(Address, address_id=address_id, customer=customer)
        
        # Calculate total
        subtotal = sum(item.subtotal for item in cart_items)
        shipping_cost = 30000 if shipping_method == 'Standard' else 50000
        total = subtotal + shipping_cost
        
        # Create order with transaction
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total,
                    status='Pending',
                    payment_method=payment_method
                )
                
                # Create order items
                for cart_item in cart_items:
                    # Check stock again
                    if cart_item.book.stock < cart_item.quantity:
                        raise Exception(f'Insufficient stock for {cart_item.book.title}')
                    
                    OrderItem.objects.create(
                        order=order,
                        book=cart_item.book,
                        quantity=cart_item.quantity,
                        price=cart_item.book.price
                    )
                    
                    # Update stock
                    cart_item.book.stock -= cart_item.quantity
                    cart_item.book.save()
                
                # Create shipping
                estimated_delivery = timezone.now().date() + timedelta(days=3 if shipping_method == 'Standard' else 1)
                Shipping.objects.create(
                    order=order,
                    address=address,
                    shipping_method=shipping_method,
                    estimated_delivery=estimated_delivery
                )
                
                # Clear cart
                cart_items.delete()
                
                messages.success(request, f'Order #{order.order_id} placed successfully!')
                return redirect('order_detail', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return redirect('checkout')
    
    addresses = customer.addresses.all()
    subtotal = sum(item.subtotal for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
    }
    return render(request, 'cart/checkout.html', context)


def order_history(request):
    """View order history"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login first')
        return redirect('customer_login')
    
    orders = Order.objects.filter(customer_id=customer_id).order_by('-order_date')
    
    context = {'orders': orders}
    return render(request, 'cart/order_history.html', context)


def order_detail(request, order_id):
    """View order details"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login first')
        return redirect('customer_login')
    
    order = get_object_or_404(Order, order_id=order_id, customer_id=customer_id)
    order_items = order.items.all().select_related('book')
    
    context = {
        'order': order,
        'order_items': order_items,
        'shipping': order.shipping,
    }
    return render(request, 'cart/order_detail.html', context)


# Wishlist functions
def view_wishlist(request):
    """View wishlist"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to view wishlist')
        return redirect('customer_login')
    
    wishlist_items = Wishlist.objects.filter(customer_id=customer_id).select_related('book')
    
    context = {'wishlist_items': wishlist_items}
    return render(request, 'cart/wishlist.html', context)


def add_to_wishlist(request, book_id):
    """Add book to wishlist"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to add to wishlist')
        return redirect('customer_login')
    
    book = get_object_or_404(Book, book_id=book_id)
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        customer=customer,
        book=book
    )
    
    if created:
        messages.success(request, 'Added to wishlist')
    else:
        messages.info(request, 'Already in wishlist')
    
    return redirect('book_detail', book_id=book_id)


def remove_from_wishlist(request, wishlist_id):
    """Remove from wishlist"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    wishlist_item = get_object_or_404(Wishlist, wishlist_id=wishlist_id, customer_id=customer_id)
    wishlist_item.delete()
    messages.success(request, 'Removed from wishlist')
    return redirect('view_wishlist')
