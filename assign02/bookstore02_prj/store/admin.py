from django.contrib import admin
from store.models.customer import Customer, Address
from store.models.book import Book, Author, Publisher, Category, BookAuthor, BookCategory, Review
from store.models.order import Order, OrderItem, Cart, Wishlist, Shipping
from store.models.staff import Staff


# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'username', 'email', 'full_name', 'phone')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('username',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_id', 'customer', 'street', 'city', 'country', 'postal_code')
    search_fields = ('customer__username', 'city', 'country')
    list_filter = ('country', 'city')


# Book Admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'isbn', 'price', 'stock', 'publisher', 'published_date')
    search_fields = ('title', 'isbn')
    list_filter = ('publisher', 'published_date')
    # Cannot use filter_horizontal with through models
    # filter_horizontal = ('authors', 'categories')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'name')
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('publisher_id', 'name', 'email', 'phone')
    search_fields = ('name', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name')
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'book', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'customer__username')


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'total_amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'order_date')
    search_fields = ('customer__username', 'order_id')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'book', 'quantity', 'price')
    search_fields = ('order__order_id', 'book__title')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'customer', 'book', 'quantity', 'added_at')
    search_fields = ('customer__username', 'book__title')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('wishlist_id', 'customer', 'book', 'added_at')
    search_fields = ('customer__username', 'book__title')


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('shipping_id', 'order', 'shipping_method', 'tracking_number', 'estimated_delivery')
    search_fields = ('order__order_id', 'tracking_number')
    list_filter = ('shipping_method', 'estimated_delivery')


# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'username', 'email', 'full_name', 'role', 'hire_date')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('role', 'hire_date')
