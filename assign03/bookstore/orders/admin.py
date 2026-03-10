from django.contrib import admin
from .models import Order, OrderItem, OrderStatus

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'order_date')
    list_filter = ('status', 'order_date')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_completed']

    def mark_as_processing(self, request, queryset):
        # Assumes a status with name 'Processing' exists. 
        # In a real app, use IDs or constants to be safer.
        try:
            status = OrderStatus.objects.get(name='Processing')
            updated = queryset.update(status=status)
            self.message_user(request, f"{updated} orders marked as Processing.")
        except OrderStatus.DoesNotExist:
            self.message_user(request, "Status 'Processing' not found.", level='error')
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_completed(self, request, queryset):
        try:
            status = OrderStatus.objects.get(name='Completed')
            updated = queryset.update(status=status)
            self.message_user(request, f"{updated} orders marked as Completed.")
        except OrderStatus.DoesNotExist:
            self.message_user(request, "Status 'Completed' not found.", level='error')
    mark_as_completed.short_description = "Mark selected orders as Completed"

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
