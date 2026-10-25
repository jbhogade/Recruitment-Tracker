# ==========================================================================
# File : tracker/views.py
# What : One function per page. Each function prepares data and chooses
#        the HTML template to show.
# ==========================================================================

#-------------- Start Code for Dashboard page view -----------------
from django.shortcuts import render

from .services import build_dashboard_context


def dashboard(request):
    """Dashboard page: summary numbers, pipeline, charts and recent candidates."""
    context = build_dashboard_context()   # all calculations live in services.py
    context["page_title"] = "Dashboard"
    context["active_nav"] = "dashboard"
    return render(request, "tracker/dashboard.html", context)
#-------------- End of the code ------------------------------
