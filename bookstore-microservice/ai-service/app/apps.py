import os
import sys
import threading
from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Prevent running twice when using Django development server (reloader process)
        if os.environ.get('RUN_MAIN') == 'true' or not sys.argv or 'runserver' not in sys.argv:
            from app.sync_helper import run_bootstrap_sync
            t = threading.Thread(target=run_bootstrap_sync)
            t.daemon = True
            t.start()

