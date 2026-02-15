"""
WSGI config for interview_service project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interview_service.settings.prod")

application = get_wsgi_application()
