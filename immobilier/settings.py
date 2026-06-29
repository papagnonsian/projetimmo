"""
Django settings for immobilier project.
"""

from pathlib import Path
import os
import ssl
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Fix certificats SSL sur Windows : Python n'utilise pas le store Windows par défaut.
# certifi fournit un bundle de certificats CA reconnus.
try:
    import certifi
    _orig_create_default_context = ssl.create_default_context
    def _certifi_ssl_context(*args, **kwargs):
        ctx = _orig_create_default_context(*args, **kwargs)
        ctx.load_verify_locations(certifi.where())
        return ctx
    ssl.create_default_context = _certifi_ssl_context
except ImportError:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-ta-cle-secrete-change-en-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'annonces',  # Notre application principale
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'immobilier.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← TRÈS IMPORTANT : ajoute cette ligne
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

WSGI_APPLICATION = 'immobilier.wsgi.application'

# Database
# En local (sans variables d'environnement) : SQLite.
# En production (cPanel) : MySQL, configure via les variables d'environnement
# DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
if os.environ.get('DB_ENGINE'):
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
   
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# Affiche les montants/nombres avec séparateur de milliers (ex: 25 000 000)
# dans tous les templates, selon le format du fr-fr (espace fine).
USE_THOUSAND_SEPARATOR = True
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Chemin où Django collecte les fichiers statiques en production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Dossiers supplémentaires contenant des fichiers statiques
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise sert les fichiers statiques compresses directement par l'app
# (utile sur cPanel/Passenger ou il n'y a pas de configuration Nginx/Apache dediee)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email (notifications : nouvelle demande de visite, demande traitée)
# En local (sans variables d'environnement) : les emails s'affichent dans la console.
# En production : configure via EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@agenceimmoci.com')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirection après connexion
LOGIN_URL = 'connexion'
LOGIN_REDIRECT_URL = 'accueil'
LOGOUT_REDIRECT_URL = 'accueil'

# Sécurité en production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True