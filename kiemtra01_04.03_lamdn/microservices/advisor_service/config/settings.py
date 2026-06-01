import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'advisor-service-secret-key-2024')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'api',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'advisor_db'),
        'USER': os.environ.get('DB_USER', 'app_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '1234'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ChromaDB
CHROMA_HOST = os.environ.get('CHROMA_HOST', 'chromadb')
CHROMA_PORT = int(os.environ.get('CHROMA_PORT', '8000'))

# Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Behaviour scoring weights
BEHAVIOUR_WEIGHTS = {
    'view_product':     0.3,
    'search':           0.2,
    'add_to_cart':      1.0,
    'remove_from_cart': -0.5,
    'checkout':         2.0,
}

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_TZ = True
