#!/bin/sh

set -e

echo "Applying database migrations..."
python manage.py makemigrations --noinput
python manage.py makemigrations home --noinput
python manage.py makemigrations products --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."

exec gunicorn ecommerce.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -