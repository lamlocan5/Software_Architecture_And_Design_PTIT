from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile
import requests

CUSTOMER_SERVICE_URL = "http://customer-service:8000"


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        error = "Email hoặc mật khẩu không đúng!"

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        email     = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not name or not email:
            error = "Vui lòng điền đầy đủ họ tên và email!"
        elif password1 != password2:
            error = "Mật khẩu xác nhận không khớp!"
        elif len(password1) < 6:
            error = "Mật khẩu phải có ít nhất 6 ký tự!"
        elif User.objects.filter(username=email).exists():
            error = "Email này đã được đăng ký!"
        else:
            # Tạo Django User
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=name,
            )

            # Tạo Customer trong customer-service
            customer_id = None
            try:
                r = requests.post(
                    f"{CUSTOMER_SERVICE_URL}/customers/",
                    json={"name": name, "email": email},
                    timeout=3,
                )
                if r.status_code == 200:
                    customer_id = r.json().get('id')
            except Exception:
                pass

            UserProfile.objects.create(user=user, customer_id=customer_id)
            login(request, user)
            return redirect('home')

    return render(request, 'register.html', {'error': error})
