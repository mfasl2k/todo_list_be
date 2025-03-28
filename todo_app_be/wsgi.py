"""
WSGI config for todo_app_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import pathlib
import dotenv

# Load environment variables from .env file
from django.core.wsgi import get_wsgi_application

# Find .env file
env_path = pathlib.Path('.') / '.env'
if env_path.exists():
    dotenv.load_dotenv(str(env_path))

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_app_be.settings.production')

# Get the WSGI application
application = get_wsgi_application()

# Vercel needs this variable name specifically
app = application