import os
import dj_database_url
from pathlib import Path

# Import all settings from base settings
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*.vercel.app', '.now.sh', 'localhost', '127.0.0.1']

# Configure database for Neon
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Middleware configuration for handling static files on Vercel
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings - if you need them
CORS_ALLOW_ALL_ORIGINS = True

ALLOWED_HOSTS = ['.vercel.app', '.now.sh', 'localhost', '127.0.0.1', 'https://todo-list-be-three.vercel.app', 'https://todo-list-fe-six.vercel.app',  # Add your frontend URL
    'localhost:5173', ]

CSRF_TRUSTED_ORIGINS = [
    'https://todo-list-be-three.vercel.app',
    'https://todo-list-fe-six.vercel.app',  # Add your frontend URL
    'https://*.vercel.app',
    'http://localhost:5173',
]
# Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}