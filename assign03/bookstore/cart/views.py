from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from catalog.models import Book

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.compute_total()
    return render(request, 'cart/view_cart.html', {'cart': cart})

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book, defaults={'quantity': 0, 'price': book.price})
    
    if not item_created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
        
    cart_item.save()
    cart.compute_total()
    
    messages.success(request, f'Added {book.title} to your cart.')
    return redirect('book_list')
