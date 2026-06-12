from app.models import Notification

def handle_customer_created(data):
    customer_id = data.get('customer_id')
    name = data.get('name', 'Khách hàng')
    email = data.get('email')
    
    title = "Đăng ký tài khoản thành công! 🎉"
    content = f"Chào mừng {name} ({email}) đến với Nhà sách trực tuyến! Tài khoản của bạn đã được đăng ký và kích hoạt thành công."
    
    try:
        Notification.objects.create(
            customer_id=customer_id,
            title=title,
            content=content,
            type='email'
        )
        print(f"[Notification Service] Created customer_created notification for customer {customer_id}")
    except Exception as e:
        print(f"[Notification Service] Error creating notification: {e}")

def handle_order_created(data):
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')
    total_amount = data.get('total_amount', 0)
    
    title = f"Đơn hàng #{order_id} đã được tạo! 🛒"
    content = f"Cảm ơn bạn đã mua sắm! Đơn hàng #{order_id} đã được tạo thành công với tổng số tiền {total_amount:,.0f}đ. Trạng thái hiện tại: Đang xử lý."
    
    try:
        Notification.objects.create(
            customer_id=customer_id,
            title=title,
            content=content,
            type='system'
        )
        print(f"[Notification Service] Created order_created notification for customer {customer_id}")
    except Exception as e:
        print(f"[Notification Service] Error creating notification: {e}")

def handle_payment_processed(data):
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')
    amount = data.get('amount', 0)
    status = data.get('status', 'initiated')
    
    status_map = {
        'paid': 'Đã thanh toán thành công',
        'failed': 'Thanh toán thất bại',
        'refunded': 'Đã hoàn tiền',
        'cancelled': 'Đã hủy thanh toán'
    }
    status_str = status_map.get(status, status)
    
    title = f"Cập nhật thanh toán đơn hàng #{order_id} 💳"
    content = f"Giao dịch thanh toán trị giá {amount:,.0f}đ cho đơn hàng #{order_id} có trạng thái: {status_str}."
    
    try:
        Notification.objects.create(
            customer_id=customer_id,
            title=title,
            content=content,
            type='system'
        )
        print(f"[Notification Service] Created payment_processed notification for customer {customer_id}")
    except Exception as e:
        print(f"[Notification Service] Error creating notification: {e}")

def handle_shipment_updated(data):
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')
    carrier = data.get('carrier', 'Đối tác vận chuyển')
    tracking_number = data.get('tracking_number', 'N/A')
    status = data.get('status', 'pending')
    
    status_map = {
        'pending': 'Đang chuẩn bị hàng',
        'picked': 'Đã lấy hàng',
        'shipping': 'Đang giao hàng',
        'delivered': 'Đã giao hàng thành công',
        'failed': 'Giao hàng thất bại',
        'cancelled': 'Đã hủy giao hàng'
    }
    status_str = status_map.get(status, status)
    
    title = f"Cập nhật vận chuyển đơn hàng #{order_id} 🚚"
    content = f"Vận đơn của bạn được vận chuyển bởi {carrier} (Mã: {tracking_number}) hiện tại có trạng thái: {status_str}."
    
    try:
        Notification.objects.create(
            customer_id=customer_id,
            title=title,
            content=content,
            type='sms'
        )
        print(f"[Notification Service] Created shipment_updated notification for customer {customer_id}")
    except Exception as e:
        print(f"[Notification Service] Error creating notification: {e}")
