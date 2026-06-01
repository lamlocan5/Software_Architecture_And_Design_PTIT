import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobile_service.settings')
django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute("""
        CREATE TABLE IF NOT EXISTS app_mobile (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            cpu VARCHAR(100) DEFAULT '',
            ram VARCHAR(50) DEFAULT '',
            storage VARCHAR(100) DEFAULT '',
            camera VARCHAR(100) DEFAULT '',
            battery VARCHAR(50) DEFAULT '',
            display VARCHAR(100) DEFAULT '',
            os VARCHAR(50) DEFAULT '',
            description TEXT DEFAULT '',
            stock INT DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    print("app_mobile table ensured.")
