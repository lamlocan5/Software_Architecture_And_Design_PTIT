from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng!')
            return render(request, 'accounts/register.html')
        
        customer = Customer.objects.create(
            name=name,
            email=email,
            password=password  # Note: In production, hash this!
        )
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('/login/')
    
    return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(email=email, password=password)
            request.session['customer_id'] = customer.id
            request.session['customer_name'] = customer.name
            messages.success(request, f'Chào mừng {customer.name}!')
            return redirect('/books/')
        except Customer.DoesNotExist:
            messages.error(request, 'Email hoặc mật khẩu không đúng!')
            return render(request, 'accounts/login.html')
    
    
    return render(request, 'accounts/login.html')

def logout(request):
    request.session.flush()
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('/')
