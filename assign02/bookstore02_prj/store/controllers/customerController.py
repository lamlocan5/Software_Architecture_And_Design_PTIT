"""
Customer Controller (Views)
Handles customer registration, login, profile management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from store.models.customer import Customer, Address


def register(request):
    """Customer registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone', '')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'customer/register.html')
        
        if Customer.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'customer/register.html')
        
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'customer/register.html')
        
        # Create customer
        customer = Customer(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone
        )
        customer.set_password(password)
        customer.save()
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('customer_login')
    
    return render(request, 'customer/register.html')


def login(request):
    """Customer login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(username=username)
            if customer.check_password(password):
                # Store customer ID in session
                request.session['customer_id'] = customer.customer_id
                request.session['customer_username'] = customer.username
                messages.success(request, f'Welcome back, {customer.full_name}!')
                return redirect('book_list')
            else:
                messages.error(request, 'Invalid password')
        except Customer.DoesNotExist:
            messages.error(request, 'User not found')
    
    return render(request, 'customer/login.html')


def logout(request):
    """Customer logout"""
    if 'customer_id' in request.session:
        del request.session['customer_id']
        del request.session['customer_username']
    messages.success(request, 'Logged out successfully')
    return redirect('book_list')


def profile(request):
    """Customer profile view and edit"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login first')
        return redirect('customer_login')
    
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    if request.method == 'POST':
        customer.full_name = request.POST.get('full_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            customer.avatar = request.FILES['avatar']
        
        customer.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('customer_profile')
    
    context = {
        'customer': customer,
        'addresses': customer.addresses.all()
    }
    return render(request, 'customer/profile.html', context)


def add_address(request):
    """Add new address"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if request.method == 'POST':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        address = Address(
            customer=customer,
            street=request.POST.get('street'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            postal_code=request.POST.get('postal_code')
        )
        address.save()
        messages.success(request, 'Address added successfully')
        return redirect('customer_profile')
    
    return render(request, 'customer/add_address.html')


def delete_address(request, address_id):
    """Delete address"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    address = get_object_or_404(Address, address_id=address_id, customer_id=customer_id)
    address.delete()
    messages.success(request, 'Address deleted successfully')
    return redirect('customer_profile')
