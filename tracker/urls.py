# ==========================================================================
# File : tracker/urls.py
# What : Page addresses of the Recruitment Tracker app.
# Add each new page here as we build it (Candidates, Interviews, ...).
# ==========================================================================

#-------------- Start Code for Page URL list -----------------
from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    # Home page = Dashboard
    path("", views.dashboard, name="dashboard"),
    # (next pages will be added here, one by one)
]
#-------------- End of the code ------------------------------
