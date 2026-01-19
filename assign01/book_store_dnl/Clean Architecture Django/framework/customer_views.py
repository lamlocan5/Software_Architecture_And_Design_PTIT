"""Django views for customer operations"""
from django.shortcuts import render, redirect
from django.contrib import messages

from usecases.customer.register_customer import RegisterCustomer
from usecases.customer.authenticate_customer import AuthenticateCustomer
from infrastructure.repositories.django_customer_repository import DjangoCustomerRepository


# Initialize repository
customer_repository = DjangoCustomerRepository()


def register_view(request):
    """Customer registration view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Execute use case
        use_case = RegisterCustomer(customer_repository)
        result = use_case.execute(name, email, password)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('login')
        else:
            messages.error(request, result['error'])
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """Customer login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Execute use case
        use_case = AuthenticateCustomer(customer_repository)
        result = use_case.execute(email, password)
        
        if result['success']:
            customer = result['customer']
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name
            messages.success(request, f'Chào mừng {customer.name}!')
            return redirect('book_list')
        else:
            messages.error(request, result['error'])
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Customer logout view"""
    request.session.flush()
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('home')
