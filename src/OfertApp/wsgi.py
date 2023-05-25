"""
WSGI config for OfertApp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OfertApp.settings')
application = get_wsgi_application()

# Vercel config little detail over here :)
app = application

print("STARTING SCHEDULER")
# Init scheduler
# IMPORTANT: Seems like you'll have to comment this code, run
# django_scheduler migrations (normal migrate command) and then
# uncomment this code again and run the server
from scheduler import scheduler
scheduler.start()