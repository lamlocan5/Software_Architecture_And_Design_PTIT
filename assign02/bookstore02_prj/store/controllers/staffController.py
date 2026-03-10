"""
Staff Controller (Views)
Handles staff dashboard, order management, inventory management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from store.models.staff import Staff
from store.models.order import Order, OrderItem
from store.models.book import Book
from store.models.customer import Customer


def staff_login(request):
    """Staff login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            staff = Staff.objects.get(username=username)
            if staff.check_password(password):
                request.session['staff_id'] = staff.staff_id
                request.session['staff_username'] = staff.username
                request.session['staff_role'] = staff.role
                messages.success(request, f'Welcome, {staff.full_name}!')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Staff.DoesNotExist:
            messages.error(request, 'Staff not found')
    
    return render(request, 'staff/login.html')


def staff_logout(request):
    """Staff logout"""
    if 'staff_id' in request.session:
        del request.session['staff_id']
        del request.session['staff_username']
        del request.session['staff_role']
    messages.success(request, 'Logged out successfully')
    return redirect('staff_login')


def staff_dashboard(request):
    """Staff dashboard with statistics"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, 'Please login first')
        return redirect('staff_login')
    
    # Calculate statistics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_customers = Customer.objects.count()
    total_books = Book.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-order_date')[:10]
    
    # Monthly revenue
    monthly_revenue = Order.objects.filter(
        order_date__gte=last_30_days,
        status__in=['Processing', 'Shipped', 'Delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Low stock books
    low_stock_books = Book.objects.filter(stock__lt=10).order_by('stock')[:5]
    
    # Top selling books
    top_books = Book.objects.annotate(
        total_sold=Sum('order_items__quantity')
    ).order_by('-total_sold')[:5]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_books': total_books,
        'recent_orders': recent_orders,
        'monthly_revenue': monthly_revenue,
        'low_stock_books': low_stock_books,
        'top_books': top_books,
    }
    return render(request, 'staff/dashboard.html', context)


def manage_orders(request):
    """Manage all orders"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, 'Please login first')
        return redirect('staff_login')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = Order.objects.filter(status=status_filter)
    else:
        orders = Order.objects.all()
    
    orders = orders.order_by('-order_date')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'staff/orders.html', context)


def update_order_status(request, order_id):
    """Update order status"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return redirect('staff_login')
    
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order #{order_id} status updated to {new_status}')
    
    return redirect('manage_orders')


def manage_inventory(request):
    """Manage book inventory"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, 'Please login first')
        return redirect('staff_login')
    
    # Search and filter
    search_query = request.GET.get('search', '')
    if search_query:
        books = Book.objects.filter(title__icontains=search_query)
    else:
        books = Book.objects.all()
    
    books = books.order_by('title')
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'staff/inventory.html', context)


def update_stock(request, book_id):
    """Update book stock"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return redirect('staff_login')
    
    book = get_object_or_404(Book, book_id=book_id)
    
    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', 0))
        book.stock = new_stock
        book.save()
        messages.success(request, f'Stock updated for {book.title}')
    
    return redirect('manage_inventory')


def manage_customers(request):
    """View and manage customers"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, 'Please login first')
        return redirect('staff_login')
    
    search_query = request.GET.get('search', '')
    if search_query:
        customers = Customer.objects.filter(username__icontains=search_query)
    else:
        customers = Customer.objects.all()
    
    # Annotate with order count
    customers = customers.annotate(
        order_count=Count('orders')
    ).order_by('-order_count')
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'staff/customers.html', context)


def sales_report(request):
    """Generate sales report"""
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, 'Please login first')
        return redirect('staff_login')
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    orders = Order.objects.filter(status__in=['Processing', 'Shipped', 'Delivered'])
    
    if start_date:
        orders = orders.filter(order_date__gte=start_date)
    if end_date:
        orders = orders.filter(order_date__lte=end_date)
    
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()
    avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'orders': orders.order_by('-order_date'),
    }
    return render(request, 'staff/sales_report.html', context)
