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
    # Candidates page (full list with search, filters, sorting)
    path("candidates/", views.candidates, name="candidates"),
    # Add candidate form
    path("candidates/add/", views.candidate_add, name="candidate_add"),
    # Candidate details + documents (CV, certificates ...)
    path("candidates/<int:sr_no>/", views.candidate_detail, name="candidate_detail"),
    path("candidates/<int:sr_no>/documents/upload/", views.document_upload, name="document_upload"),
    path("candidates/<int:sr_no>/documents/<str:doc_id>/", views.document_file, name="document_file"),
    path("candidates/<int:sr_no>/documents/<str:doc_id>/delete/", views.document_delete, name="document_delete"),
    # (+) button on the Add form: save a new dropdown choice
    path("candidates/options/add/", views.option_add, name="option_add"),
    # Export / Template downloads (CSV, XLSX, XLS chosen with ?format=)
    path("candidates/export/", views.candidates_export, name="candidates_export"),
    path("candidates/template/", views.candidates_template, name="candidates_template"),
    # Import: step 1 upload + check, step 2 confirm
    path("candidates/import/", views.candidates_import, name="candidates_import"),
    path("candidates/import/confirm/", views.candidates_import_confirm, name="candidates_import_confirm"),
    # (next pages will be added here, one by one)
]
#-------------- End of the code ------------------------------
