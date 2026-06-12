from django.shortcuts import render, redirect
import requests

USER_SERVICE_URL = "http://user-service:8000"


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            r = requests.post(
                f"{USER_SERVICE_URL}/api/token/",
                json={"username": username, "password": password},
                timeout=3,
            )
            if r.status_code == 200:
                tokens = r.json()
                request.session['access_token'] = tokens['access']
                request.session['refresh_token'] = tokens['refresh']
                response = redirect(request.GET.get('next', '/'))
                response.set_cookie('access_token', tokens['access'], httponly=True)
                return response
            error = "Email hoặc mật khẩu không đúng!"
        except Exception as e:
            error = f"Lỗi kết nối tới dịch vụ xác thực: {e}"

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    response = redirect('login')
    response.delete_cookie('access_token')
    return response


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
        else:
            try:
                # Call user-service to create user & customer
                r = requests.post(
                    f"{USER_SERVICE_URL}/customers/",
                    json={"name": name, "email": email, "password": password1},
                    timeout=3,
                )
                if r.status_code in (200, 201):
                    # Direct login after registration
                    login_r = requests.post(
                        f"{USER_SERVICE_URL}/api/token/",
                        json={"username": email, "password": password1},
                        timeout=3
                    )
                    if login_r.status_code == 200:
                        tokens = login_r.json()
                        request.session['access_token'] = tokens['access']
                        request.session['refresh_token'] = tokens['refresh']
                        response = redirect('home')
                        response.set_cookie('access_token', tokens['access'], httponly=True)
                        return response
                else:
                    error = "Đăng ký thất bại! Email có thể đã tồn tại."
            except Exception as e:
                error = f"Lỗi kết nối tới user-service: {e}"

    return render(request, 'register.html', {'error': error})

