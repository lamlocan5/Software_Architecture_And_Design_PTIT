from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem
from books.models import Book
from accounts.models import Customer

def add_to_cart(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if user is logged in
        customer_id = request.session.get('customer_id')
        if not customer_id:
            messages.error(request, 'Vui lòng đăng nhập để thêm vào giỏ hàng!')
            return redirect('/login/')
        
        try:
            customer = Customer.objects.get(id=customer_id)
            book = Book.objects.get(id=book_id)
            
            # Check stock
            if book.stock < quantity:
                messages.error(request, 'Không đủ hàng trong kho!')
                return redirect('/books/')
            
            # Get or create cart
            cart, _ = Cart.objects.get_or_create(customer=customer)
            
            # Check if item already exists in cart
            try:
                cart_item = CartItem.objects.get(cart=cart, book=book)
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f'Đã cập nhật số lượng "{book.title}" trong giỏ hàng!')
            except CartItem.DoesNotExist:
                CartItem.objects.create(
                    cart=cart,
                    book=book,
                    quantity=quantity
                )
                messages.success(request, f'Đã thêm "{book.title}" vào giỏ hàng!')
            
            return redirect('/cart/')
        except (Customer.DoesNotExist, Book.DoesNotExist):
            messages.error(request, 'Có lỗi xảy ra!')
            return redirect('/books/')
    
    return redirect('/books/')

def view_cart(request):
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        messages.warning(request, 'Vui lòng đăng nhập để xem giỏ hàng!')
        return redirect('/login/')
    
    try:
        customer = Customer.objects.get(id=customer_id)
        cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(cart=cart).select_related('book')
        
        # Calculate subtotal for each item
        for item in cart_items:
            item.subtotal = item.book.price * item.quantity
        
        # Calculate total
        total = sum(item.subtotal for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'total': total
        }
        return render(request, 'cart/cart.html', context)
    except (Customer.DoesNotExist, Cart.DoesNotExist):
        return render(request, 'cart/cart.html', {'cart_items': []})

def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id)
            book_title = cart_item.book.title
            cart_item.delete()
            messages.success(request, f'Đã xóa "{book_title}" khỏi giỏ hàng!')
        except CartItem.DoesNotExist:
            messages.error(request, 'Mục không tồn tại!')
        
        return redirect('/cart/')
    
    return redirect('/cart/')
