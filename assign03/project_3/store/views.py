"""
Views: Auth, Staff (book entry), Product list/detail (search, related books),
Cart, Checkout & Shipping.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from .models import Book, Order, OrderItem, Shipment
from .forms import LoginForm, RegisterForm, BookForm, ShippingAddressForm
from .cart import CartService


# ----- Authentication -----

def login_view(request):
    if request.user.is_authenticated:
        return redirect_next(request)
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_next(request)
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'store/auth/login.html', {'form': form})


def redirect_next(request):
    """After login: use ?next= if safe; else Staff -> /staff/dashboard/, Customer -> /."""
    from django.utils.http import url_has_allowed_host_and_scheme
    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=[request.get_host()]):
        return redirect(next_url)
    if request.user.is_staff:
        return redirect('staff:dashboard')
    return redirect('/')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created. Welcome!')
            return redirect_next(request)
        for field, errors in form.errors.items():
            for e in errors:
                messages.error(request, e)
    else:
        form = RegisterForm()
    return render(request, 'store/auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('/')


# ----- Product list (search + HTMX) -----

class ProductListView(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'store/product_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.select_related('category', 'author').filter(stock__gt=0)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(author__name__icontains=q)
            )
        return qs

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['store/partials/product_list_results.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


# ----- Product detail (related books) -----

class ProductDetailView(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'store/product_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = self.object
        related = Book.objects.filter(
            category=book.category
        ).exclude(pk=book.pk).order_by('?')[:4]
        ctx['related_books'] = related
        return ctx


# ----- Staff: Book entry -----

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    login_url = '/accounts/login/'


class StaffBookCreateView(StaffRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'store/staff/book_form.html'
    success_url = reverse_lazy('staff:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Book added successfully.')
        return super().form_valid(form)


def staff_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('auth:login')
    return render(request, 'store/staff/dashboard.html')


# ----- Cart -----

def cart_add(request, product_id):
    book = get_object_or_404(Book, pk=product_id)
    if request.method != 'POST':
        return redirect('store:product_list')
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    cart = CartService(request)
    if book.stock < quantity:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<span class="text-red-600">Not enough stock.</span>',
                status=400,
            )
        messages.error(request, 'Not enough stock.')
        return redirect('store:product_detail', pk=product_id)
    cart.add(book, quantity)
    if request.headers.get('HX-Request'):
        return render(request, 'store/partials/cart_badge.html', {'cart_item_count': cart.get_item_count()})
    messages.success(request, f'Added {book.title} to cart.')
    return redirect(request.POST.get('next', reverse('store:product_list')))


def cart_detail(request):
    cart = CartService(request)
    return render(request, 'store/cart/detail.html', {'cart': cart})


def cart_update_quantity(request, product_id):
    if request.method != 'POST':
        return redirect('store:cart_detail')
    book = get_object_or_404(Book, pk=product_id)
    quantity = int(request.POST.get('quantity', 0))
    cart = CartService(request)
    if quantity <= 0:
        cart.remove(book)
    else:
        if book.stock < quantity:
            messages.error(request, f'Only {book.stock} in stock for {book.title}.')
        else:
            cart.set_quantity(book, quantity)
    return redirect('store:cart_detail')


def cart_remove(request, product_id):
    if request.method != 'POST':
        return redirect('store:cart_detail')
    book = get_object_or_404(Book, pk=product_id)
    CartService(request).remove(book)
    messages.info(request, 'Item removed from cart.')
    return redirect('store:cart_detail')


# ----- Checkout & Shipping -----

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CheckoutView(FormView):
    form_class = ShippingAddressForm
    template_name = 'store/checkout/checkout.html'
    success_url = reverse_lazy('store:order_success')

    def get(self, request, *args, **kwargs):
        cart = CartService(request)
        if not cart.get_items():
            messages.warning(request, 'Your cart is empty.')
            return redirect('store:cart_detail')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        cart = CartService(self.request)
        items = cart.get_items()
        if not items:
            messages.warning(self.request, 'Cart is empty.')
            return redirect('store:cart_detail')

        try:
            with transaction.atomic():
                total = cart.get_total_price()
                order = Order.objects.create(
                    user=self.request.user,
                    status='Pending',
                    payment_method=form.cleaned_data['payment_method'],
                    total_amount=total,
                )
                for book, qty in items:
                    if book.stock < qty:
                        raise ValueError(f'Not enough stock for "{book.title}". Available: {book.stock}')
                    OrderItem.objects.create(
                        order=order,
                        book=book,
                        quantity=qty,
                        price=book.price,
                    )
                    book.stock -= qty
                    book.save(update_fields=['stock'])
                Shipment.objects.create(
                    order=order,
                    status='Processing',
                    street=form.cleaned_data['street'],
                    city=form.cleaned_data['city'],
                    country=form.cleaned_data['country'],
                    postal_code=form.cleaned_data['postal_code'],
                )
                cart.clear()
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Order placed successfully.')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cart'] = CartService(self.request)
        return ctx


def order_success(request):
    return render(request, 'store/checkout/success.html')
