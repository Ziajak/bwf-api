#!/bin/sh

echo "Waiting for Postgres..."

while ! nc -z db 5432; do
  sleep 0.5
done

echo "Postgres started"

python manage.py migrate

python manage.py create_admin

gunicorn bwf.wsgi:application --bind 0.0.0.0:8000