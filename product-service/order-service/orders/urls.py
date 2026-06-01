from django.urls import path
from . import views

urlpatterns = [
    # Tạo đơn hàng mới
    path('create/', views.create_order, name='order-create'),

    # Lịch sử đơn hàng
    path('', views.list_orders, name='order-list'),

    # Chi tiết đơn hàng
    path('<int:order_id>/', views.order_detail, name='order-detail'),

    # Cập nhật trạng thái (nội bộ / admin)
    path('<int:order_id>/status/', views.update_order_status, name='order-status'),
]
