# ==========================================================================
# File : config/settings.py
# What : Central configuration of the Recruitment Tracker project.
# Note : Phase 1 = web pages only, NO database. See the DATABASES block.
# ==========================================================================

#-------------- Start Code for Imports and base folder -----------------
from pathlib import Path

# BASE_DIR = the project root folder (the folder that contains manage.py).
# Because it is calculated automatically, you can move the project folder
# (e.g. from D:\ to another drive) without changing anything here.
BASE_DIR = Path(__file__).resolve().parent.parent
#-------------- End of the code ------------------------------


#-------------- Start Code for Security / run mode settings -----------------
import os
import socket

# Development-only key. Change it before sharing the portal outside the office.
SECRET_KEY = "dev-only-change-me-before-real-use"

# DEBUG = True shows detailed error pages. Set to False when going live.
DEBUG = True


def _detect_allowed_hosts():
    """Build ALLOWED_HOSTS automatically for whichever PC runs the portal.

    Includes: localhost, this PC's name, and every IPv4 address of this PC,
    so the portal opens on any system without editing an IP address.
    """
    hosts = {"localhost", "127.0.0.1", "[::1]"}
    try:
        # PC name and all IPv4 addresses registered for it
        name = socket.gethostname()
        hosts.update({name, socket.getfqdn()})
        for info in socket.getaddrinfo(name, None, socket.AF_INET):
            hosts.add(info[4][0])
        # IP of the active network card (no data is actually sent)
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("10.255.255.255", 1))
        hosts.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass  # no network: localhost still works

    # Optional extra hosts, e.g. a DNS name HR uses:  set RT_ALLOWED_HOSTS=hr-portal,192.168.0.50
    extra = os.environ.get("RT_ALLOWED_HOSTS", "")
    hosts.update(h.strip() for h in extra.split(",") if h.strip())
    return sorted(hosts)


ALLOWED_HOSTS = _detect_allowed_hosts()

# Quick test option (any address accepted). Use only on a trusted office network
# with dummy data, never with real candidate data:
# ALLOWED_HOSTS = ["*"]
#-------------- End of the code ------------------------------


#-------------- Start Code for Installed apps -----------------
INSTALLED_APPS = [
    "django.contrib.staticfiles",  # serves our CSS / JS files
    "tracker",                     # our own app: all Recruitment Tracker pages
]
#-------------- End of the code ------------------------------


#-------------- Start Code for Middleware -----------------
# Only the middleware that does not need a database is enabled.
# (Sessions / login will be added together with the database phase.)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
#-------------- End of the code ------------------------------


#-------------- Start Code for URL / WSGI entry points -----------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
#-------------- End of the code ------------------------------


#-------------- Start Code for Templates (HTML pages) -----------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # All HTML files live in the top-level "templates" folder.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                # Our own helper: makes the theme list available on every page.
                "tracker.context_processors.themes",
            ],
        },
    },
]
#-------------- End of the code ------------------------------


#-------------- Start Code for Database (DISABLED in Phase 1) -----------------
# An empty dictionary means "no database". All data currently comes from
# tracker/dummy_data.py.
DATABASES = {}

# FUTURE (SQL Server) - example only, do not enable yet:
# DATABASES = {
#     "default": {
#         "ENGINE": "mssql",
#         "NAME": "RecruitmentTracker",
#         "HOST": "YOUR-SERVER-NAME",
#         "OPTIONS": {"driver": "ODBC Driver 18 for SQL Server"},
#     }
# }
#-------------- End of the code ------------------------------


#-------------- Start Code for Language, time zone and number format -----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = False
USE_TZ = True
USE_THOUSAND_SEPARATOR = False
#-------------- End of the code ------------------------------


#-------------- Start Code for Static files (CSS / JS) -----------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
#-------------- End of the code ------------------------------
