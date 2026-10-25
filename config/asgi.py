# File : config/asgi.py - async entry point (not used in Phase 1, kept for completeness).
#-------------- Start Code for ASGI entry point -----------------
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
#-------------- End of the code ------------------------------
