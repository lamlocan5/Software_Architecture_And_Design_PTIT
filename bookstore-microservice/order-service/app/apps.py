from django.apps import AppConfig
import sys
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Avoid running consumer during database migrations or administrative commands
        ignore_commands = {'migrate', 'makemigrations', 'createsuperuser', 'shell', 'collectstatic', 'check'}
        if not any(cmd in sys.argv for cmd in ignore_commands):
            # Also check if we are in reload phase of Django runserver
            if os.environ.get('RUN_MAIN') == 'true' or 'runserver' not in sys.argv:
                try:
                    from .event_broker import start_consumer
                    from .event_handlers import handle_payment_processed
                    
                    handlers = {
                        'payment_processed': handle_payment_processed
                    }
                    start_consumer(handlers)
                except Exception as e:
                    print(f"[Order Service] Error starting consumer: {e}")
