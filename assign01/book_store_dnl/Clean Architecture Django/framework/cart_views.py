"""Django views for cart operations"""
from django.shortcuts import render, redirect
from django.contrib import messages

from usecases.cart.add_to_cart import AddToCart
from usecases.cart.view_cart import ViewCart
from usecases.cart.remove_from_cart import RemoveFromCart
from infrastructure.repositories.django_cart_repository import DjangoCartRepository
from infrastructure.repositories.django_book_repository import DjangoBookRepository


# Initialize repositories
cart_repository = DjangoCartRepository()
book_repository = DjangoBookRepository()


def add_to_cart_view(request):
    """Add item to cart view"""
    if request.method == 'POST':
        # Check if user is logged in
        customer_id = request.session.get('customer_id')
        if not customer_id:
            messages.error(request, 'Vui lòng đăng nhập để thêm vào giỏ hàng!')
            return redirect('login')
        
        book_id = int(request.POST.get('book_id'))
        quantity = int(request.POST.get('quantity', 1))
        
        # Execute use case
        use_case = AddToCart(cart_repository, book_repository)
        result = use_case.execute(customer_id, book_id, quantity)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('view_cart')
        else:
            messages.error(request, result['error'])
            return redirect('book_list')
    
    return redirect('book_list')


def view_cart_view(request):
    """View cart view"""
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        messages.warning(request, 'Vui lòng đăng nhập để xem giỏ hàng!')
        return redirect('login')
    
    # Execute use case
    use_case = ViewCart(cart_repository)
    result = use_case.execute(customer_id)
    
    context = {
        'cart': result['cart'],
        'total': result['total'],
        'item_count': result['item_count']
    }
    
    return render(request, 'cart/cart.html', context)


def remove_from_cart_view(request):
    """Remove item from cart view"""
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('login')
        
        book_id = int(request.POST.get('book_id'))
        
        # Execute use case
        use_case = RemoveFromCart(cart_repository)
        result = use_case.execute(customer_id, book_id)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['error'])
    
    return redirect('view_cart')
