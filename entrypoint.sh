#!/bin/sh

echo "Migrating database..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn HelpDeskProject.wsgi:application --bind 0.0.0.0:8000
