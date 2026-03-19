from pathlib import Path
import os
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# ENV HELPERS (evita problemas de encoding con .env en Windows)
# -----------------------------------------------------------------------------
def _env_str(key: str, default: str = "") -> str:
    value = os.environ.get(key)
    return default if value is None else value


def _env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


# SECRET KEY
SECRET_KEY = _env_str('SECRET_KEY', 'django-insecure-default-key-for-dev-only')

# DEBUG - En producción debe ser False
DEBUG = _env_bool('DEBUG', False)

# ALLOWED HOSTS - SIN https://
ALLOWED_HOSTS = [
    'backend-gestor-pollos.onrender.com',  # SIN https://
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]


# -----------------------------------------------------------------------------
# CONFIGURANDO SIMPLEJWT
# -----------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,       # genera nuevo refresh en cada uso
    'BLACKLIST_AFTER_ROTATION': False,   # no requiere app extra
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -----------------------------------------------------------------------------
# REST FRAMEWORK CONFIG
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    # Ojo: mantenemos AllowAny por compatibilidad y protegemos por-view.
    # Si quieres "todo privado por defecto", cambia a IsAuthenticated.
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
CORS_ALLOW_ALL_ORIGINS = True  # Para desarrollo, en producción especifica orígenes

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://backend-gestor-pollos.onrender.com",
    # Agrega aquí tu frontend cuando lo despliegues
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "https://backend-gestor-pollos.onrender.com",
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
# DATABASE - CAMBIADO A Render base de datos (POSTGRESQL)
# -----------------------------------------------------------------------------
# Obtener DATABASE_URL de variables de entorno
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# -----------------------------------------------------------------------------
# PASSWORD VALIDATION
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# -----------------------------------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'  # Cambia según tu zona horaria
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# STATIC FILES - CONFIGURACIÓN PARA RENDER
# -----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Directorios adicionales de static files
# Reemplaza la línea STATICFILES_DIRS actual por:
static_dir = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [static_dir] if os.path.isdir(static_dir) else []
# -----------------------------------------------------------------------------
# MEDIA FILES (si necesitas subir archivos)
# -----------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------------------------------------------------------
# DEFAULT AUTO FIELD
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -----------------------------------------------------------------------------
# SECURITY SETTINGS PARA PRODUCCIÓN
# -----------------------------------------------------------------------------
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Otros ajustes de seguridad
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')