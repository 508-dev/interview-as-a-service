#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Applying migrations..."
python manage.py migrate --noinput --settings=interview_service.settings.prod

echo "Creating superuser..."
# This uses environment variables defined in Coolify
# Ensure DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD are set
python manage.py createsuperuser --noinput --settings=interview_service.settings.prod || echo "Superuser already exists or creation failed."

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=interview_service.settings.prod

# This executes the CMD from your Dockerfile (e.g., gunicorn or nginx)
exec "$@"
