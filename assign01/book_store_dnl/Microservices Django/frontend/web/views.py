from django.shortcuts import render, redirect
from django.contrib import messages
from .services import BookService, CustomerService, CartService

# Initialize services
book_service = BookService()
customer_service = CustomerService()
cart_service = CartService()

def home(request):
    return render(request, 'home.html')

def book_list(request):
    print(f"DEBUG BOOK_LIST SESSION: {dict(request.session)}")
    data = book_service.list_books()
    return render(request, 'books/book_list.html', {
        'books': data.get('books', []),
        'count': data.get('count', 0)
    })

def book_detail(request, book_id):
    data = book_service.get_book(book_id)
    if data and data.get('success'):
        return render(request, 'books/book_detail.html', {'book': data.get('book')})
    return redirect('book_list')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        data, status = customer_service.login(email, password)
        
        if status == 200 and data.get('success'):
            customer = data.get('customer')
            print(f"DEBUG LOGIN DATA: {data}")
            print(f"DEBUG CUSTOMER: {customer}")
            request.session['customer_id'] = customer['id']
            request.session['customer_name'] = customer['name']
            print(f"DEBUG SESSION NAME SET: {request.session.get('customer_name')}")
            messages.success(request, f"Welcome back, {customer['name']}!")
            return redirect('book_list')
        else:
            messages.error(request, data.get('error', 'Login failed'))
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        data, status = customer_service.register(name, email, password)
        
        if status == 201 and data.get('success'):
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, data.get('error', 'Registration failed'))
            
    return render(request, 'accounts/register.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

def view_cart(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.warning(request, 'Please login to view cart')
        return redirect('login')
        
    data = cart_service.get_cart(customer_id)
    cart_data = data.get('cart', {}) if data else {}
    
    return render(request, 'cart/cart.html', {
        'cart': cart_data,
        'total': cart_data.get('total', 0),
        'item_count': cart_data.get('item_count', 0)
    })

def add_to_cart(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('login')
            
        book_id = int(request.POST.get('book_id'))
        quantity = int(request.POST.get('quantity', 1))
        
        data, status = cart_service.add_to_cart(customer_id, book_id, quantity)
        
        if status == 201:
            messages.success(request, data.get('message', 'Added to cart'))
            return redirect('view_cart')
        else:
            messages.error(request, data.get('error', 'Failed to add to cart'))
            
    return redirect('book_list')

def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('book_id') # Note: In existing cart.html form, input name is "book_id" but for removal we might need item_id or delete by book_id.
        # However, CartService.remove_from_cart expects item_id (pk of CartItem).
        # Version B implementation used item id logic or book id logic. 
        # Let's check Cart Service API implementation: DELETE /api/cart/items/<id>/
        # The template sends `book_id` as value for `book_id`. Wait, let's check Version B template.
        
        # Version B template: <input type="hidden" name="book_id" value="{{ item.book_id }}">
        # Version B View: RemoveFromCart use case takes (customer_id, book_id).
        # BUT Version C API: path('api/cart/items/<int:item_id>/', views.remove_from_cart)
        # We need to adjust either the template or the view logic.
        # Since we are reusing Version B templates, we receive `book_id`.
        # Version C Cart Service doesn't seem to expose "remove by book_id", only "remove item by ID".
        # We might need to find the item ID first or just assume we can change the template or API.
        # Let's check the verify tools output for Version C Cart Service again? 
        pass 
        # Actually in Version C, we don't store `item_id` in the template explicitly if we copy exactly. 
        # Wait, the `cart` object from API returns `items` list. If that list has `id`, we can use it.
        # Let's check CartItemSerializer in Version C: fields = ['id', 'book_id', ...]
        # So `item.id` exists. 
        # The Version B template uses: <input type="hidden" name="book_id" value="{{ item.book_id }}">
        # This is a mismatch. Version B removes by (customer, book). Version C removes by Item ID.
        # I should simply update the View here to handle this, OR update template.
        # Updating template is better but shared template?
        # I will assume I can update the template in Version C (copy then modify).
        
        # New Logic:
        # In Version C, I'll modify the `cart.html` after copying to use `item.id` and name `item_id`.
        
        item_id = request.POST.get('item_id')
        if item_id:
             cart_service.remove_from_cart(item_id)
             messages.success(request, 'Item removed')
        
    return redirect('view_cart')
