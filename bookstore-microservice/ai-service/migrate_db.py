import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommender_ai_service.settings')
django.setup()

from django.db import connection

print("Starting custom migration script...")
with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE app_productnode ADD COLUMN product_type varchar(50) NOT NULL DEFAULT 'book';")
        print("Success: added product_type column to app_productnode table!")
    except Exception as e:
        print("Error/Notice:", e)
