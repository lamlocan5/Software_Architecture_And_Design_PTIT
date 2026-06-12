from django.apps import AppConfig
import sys
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Avoid running consumer during migrations or admin commands
        ignore_commands = {'migrate', 'makemigrations', 'createsuperuser', 'shell', 'collectstatic', 'check'}
        if not any(cmd in sys.argv for cmd in ignore_commands):
            if os.environ.get('RUN_MAIN') == 'true' or 'runserver' not in sys.argv:
                try:
                    from .event_broker import start_consumer
                    from .event_handlers import (
                        handle_customer_created,
                        handle_order_created,
                        handle_payment_processed,
                        handle_shipment_updated
                    )
                    
                    handlers = {
                        'customer_created': handle_customer_created,
                        'order_created': handle_order_created,
                        'payment_processed': handle_payment_processed,
                        'shipment_updated': handle_shipment_updated,
                    }
                    start_consumer(handlers)
                except Exception as e:
                    print(f"[Notification Service] Error starting consumer: {e}")
