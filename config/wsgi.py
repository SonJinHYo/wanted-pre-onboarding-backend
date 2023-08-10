"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.conf import settings

from django.core.wsgi import get_wsgi_application

if settings.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
