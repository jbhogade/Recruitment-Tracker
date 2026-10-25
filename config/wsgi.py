# File : config/wsgi.py - entry point used by production web servers (IIS, gunicorn...).
#-------------- Start Code for WSGI entry point -----------------
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
#-------------- End of the code ------------------------------
