from django.shortcuts import render

def index(request):
    return render(request, 'frontend/index.html')

def login_view(request):
    return render(request, 'frontend/login.html')

def cart_view(request):
    return render(request, 'frontend/cart.html')

def staff_login_view(request):
    return render(request, 'frontend/staff_login.html')

def products_view(request):
    return render(request, 'frontend/products.html')

def product_detail_view(request, id):
    return render(request, 'frontend/product_detail.html', {'id': id})

def profile_view(request):
    return render(request, 'frontend/profile.html')

def staff_dashboard_view(request):
    return render(request, 'frontend/staff_dashboard.html')

def manage_products_view(request):
    return render(request, 'frontend/manage_products.html')

def manage_orders_view(request):
    return render(request, 'frontend/manage_orders.html')
