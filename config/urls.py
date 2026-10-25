# ==========================================================================
# File : config/urls.py
# What : Top-level address book. Sends every web address to the right app.
# ==========================================================================

#-------------- Start Code for Main URL list -----------------
from django.urls import include, path

urlpatterns = [
    # Everything is handled by the "tracker" app (see tracker/urls.py).
    path("", include("tracker.urls")),
]
#-------------- End of the code ------------------------------
