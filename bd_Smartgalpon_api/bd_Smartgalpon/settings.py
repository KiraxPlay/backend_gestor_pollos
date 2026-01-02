from pathlib import Path
import os
import dj_database_url  # Importación para Supabase

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# SECURITY CONFIGURATION
# -----------------------------------------------------------------------------

# SECRET KEY - Modificado para producción segura
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Solo en desarrollo permitir clave insegura
        SECRET_KEY = 'django-insecure--*s9)0j@^jbirajc*m=qa92s=o5j+s817@x@drg+!c-80u%(mp'
    else:
        raise ValueError("SECRET_KEY must be set in production environment")

# DEBUG - Configuración mejorada
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED HOSTS - Configuración para Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
ALLOWED_HOSTS = []

# Hosts permitidos desde variables de entorno
env_hosts = os.environ.get('ALLOWED_HOSTS', '')
if env_hosts:
    ALLOWED_HOSTS.extend(env_hosts.split(','))

# Agregar hostname de Render automáticamente
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Hosts por defecto para desarrollo
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0'])
elif not ALLOWED_HOSTS:  # Si no hay hosts en producción
    ALLOWED_HOSTS.append('.onrender.com')  # Permite cualquier subdominio de Render

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
    'whitenoise.runserver_nostatic',  # Para desarrollo con whitenoise

    'api',
]

# -----------------------------------------------------------------------------
# MIDDLEWARE - IMPORTANTE: Orden correcto
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- AGREGAR ESTO (después de SecurityMiddleware)
    'corsheaders.middleware.CorsMiddleware',       # <-- CORS después de WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------------------------------------------------------
# CORS / CSRF - Configuración para producción
# -----------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo permitir todos en desarrollo

# Orígenes permitidos desde variables de entorno
CORS_ALLOWED_ORIGINS = []
cors_env = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_env:
    CORS_ALLOWED_ORIGINS.extend(cors_env.split(','))

# En desarrollo, agregar localhost
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://10.0.2.2:8000",
    ])

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = []
csrf_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_env:
    CSRF_TRUSTED_ORIGINS.extend(csrf_env.split(','))

# Agregar Render URL automáticamente
if RENDER_EXTERNAL_HOSTNAME:
    render_url = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    CSRF_TRUSTED_ORIGINS.append(render_url)
    if render_url not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(render_url)

# En desarrollo, agregar localhost
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8000",
    ])

# Configuración adicional de CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
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
# DATABASE - CAMBIADO A SUPABASE (POSTGRESQL)
# -----------------------------------------------------------------------------
# Obtener DATABASE_URL de variables de entorno
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Conexión a Supabase (PostgreSQL en producción)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True  # SSL obligatorio para Supabase
        )
    }
    
    # Configuración adicional para Supabase
    if 'supabase' in DATABASE_URL:
        # Asegurar que use SSL
        if 'sslmode' not in DATABASE_URL:
            # Si no está en la URL, forzar en configuración
            DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
            
            # También puedes agregar otros parámetros
            DATABASES['default']['OPTIONS'].update({
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
            })
else:
    # Fallback a SQLite para desarrollo local
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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

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
# SUPABASE CONFIGURATION
# -----------------------------------------------------------------------------
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_KEY', '')

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