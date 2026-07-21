FROM python:3.12-slim

WORKDIR /app

# Ensure every process in this image (gunicorn, entrypoint.sh's management
# commands) uses prod settings; manage.py otherwise falls back to dev.
ENV DJANGO_SETTINGS_MODULE=interview_service.settings.prod

# 1. Install system deps (including libpq-dev for psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# This installs your dependencies from pyproject.toml
RUN pip install --no-cache-dir . 

# 3. Copy the rest of your code

# 4. Django setup
RUN python manage.py collectstatic --noinput --settings=interview_service.settings.prod

# 5. Security & Runtime
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "interview_service.wsgi:application", "--bind", "0.0.0.0:8000"]
