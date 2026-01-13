from pathlib import Path
import os
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-for-dev-only')

# DEBUG
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    'https://backend-gestor-pollos.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# -----------------------------------------------------------------------------
# REST FRAMEWORK CONFIG
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

# -----------------------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'api',
]

# -----------------------------------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # CRÍTICO PARA RENDER
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://10.0.2.2:8000",
    "https://backend-gestor-pollos.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "https://backend-gestor-pollos.onrender.com,
]

# -----------------------------------------------------------------------------
# URLS & WSGI
# -----------------------------------------------------------------------------
ROOT_URLCONF = 'bd_Smartgalpon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bd_Smartgalpon.wsgi.application'

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION (RENDER + LOCAL)
# -----------------------------------------------------------------------------
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Configuración para Render (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Configuración para desarrollo local (MySQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQLDATABASE', 'bd_smartgalpon'),
            'USER': os.environ.get('MYSQLUSER', 'root'),
            'PASSWORD': os.environ.get('MYSQLPASSWORD', ''),
            'HOST': os.environ.get('MYSQLHOST', 'localhost'),
            'PORT': os.environ.get('MYSQLPORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'connect_timeout': 10,
            }
        }
    }

# -----------------------------------------------------------------------------
# STATIC FILES FOR RENDER
# -----------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
