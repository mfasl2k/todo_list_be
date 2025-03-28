#!/bin/bash
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --settings=todo_app_be.settings.production

echo "Running migrations..."
python3 manage.py migrate --settings=todo_app_be.settings.production

echo "Build completed"