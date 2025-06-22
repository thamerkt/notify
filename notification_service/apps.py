# notification_service/apps.py

from django.apps import AppConfig
import threading
import os

class NotificationServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification_service'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .consumers import start_notification_service

            def run_safe_consumer():
                import django
                from django.db import close_old_connections

                close_old_connections()  # ✅ Ensure DB connection works in thread

                print("✅ Starting Notification Service consumer thread...")
                start_notification_service()

            thread = threading.Thread(target=run_safe_consumer, daemon=True)
            thread.start()
