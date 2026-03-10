"""
URL configuration for bookstore project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Store app URLs
    path('', include('store.urls.book_urls')),  # Book browsing at root
    path('customer/', include('store.urls.customer_urls')),
    path('cart/', include('store.urls.order_urls')),
    path('staff/', include('store.urls.staff_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
