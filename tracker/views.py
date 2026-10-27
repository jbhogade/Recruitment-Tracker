# ==========================================================================
# File : tracker/views.py
# What : One function per page. Each function prepares data and chooses
#        the HTML template to show (or the file to download).
# ==========================================================================

#-------------- Start Code for Imports -----------------
import re

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import data_store, documents, import_export, notices
from .candidate_rules import REFERRAL_SOURCE, clean_candidate
from .dummy_data import FINAL_STATUSES, INTERVIEW_STATUSES
from .candidate_rules import EXPERIENCE_TYPES
from .file_io import FORMATS
from .services import _ctc_text, build_candidate_detail, build_candidates_context, build_dashboard_context, select_candidates
#-------------- End of the code ------------------------------


#-------------- Start Code for Dashboard page view -----------------
def dashboard(request):
    """Dashboard page: summary numbers, pipeline, charts and recent candidates."""
    context = build_dashboard_context()   # all calculations live in services.py
    context["page_title"] = "Dashboard"
    context["active_nav"] = "dashboard"
    return render(request, "tracker/dashboard.html", context)
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidates page view -----------------
def _whole_number(text):
    """'12' -> 12, anything else -> None (safe reading of numbers from the web address)."""
    return int(text) if text and text.isdigit() and len(text) < 7 else None


def _notice(request):
    """Green message shown after Add / Import (?added=35 or ?imported=12&skipped=2)."""
    added = _whole_number(request.GET.get("added"))
    if added:
        match = [p for p in data_store.get_candidates() if p["sr_no"] == added]
        if match:
            return f"Candidate added: {match[0]['name']} (Sr. No. {added})."
    imported = _whole_number(request.GET.get("imported"))
    if imported is not None:
        skipped = _whole_number(request.GET.get("skipped")) or 0
        text = f"Import finished: {imported} candidate{'s' if imported != 1 else ''} added"
        return text + (f", {skipped} skipped because they were already saved." if skipped else ".")
    return ""


def _file_links(route_name, query=""):
    """One download link per file type (CSV, XLSX, XLS) for the Export / Template menus."""
    base = reverse(route_name)
    return [{"label": info["label"], "url": f"{base}?{query + '&' if query else ''}format={key}"}
            for key, info in FORMATS.items()]


def candidates(request):
    """Candidates page: full list with search, filters, sorting and paging."""
    context = build_candidates_context(request.GET)   # request.GET = options in the web address
    context["page_title"] = "Candidates"
    context["active_nav"] = "candidates"
    context["notice"] = _notice(request)
    context["export_links"] = _file_links("tracker:candidates_export", context["export_query"])
    context["template_links"] = _file_links("tracker:candidates_template")
    return render(request, "tracker/candidates.html", context)
#-------------- End of the code ------------------------------


#-------------- Start Code for Export button (download file) -----------------
def _download(content, kind, name):
    """Send bytes to the browser as a downloadable file."""
    response = HttpResponse(content, content_type=FORMATS[kind]["type"])
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    return response


def _requested_format(request):
    kind = request.GET.get("format", "xlsx")
    if kind not in FORMATS:
        raise Http404("Unknown file type")
    return kind


def candidates_export(request):
    """Download ALL candidates matching the current search / filters / sorting (not only the visible page)."""
    kind = _requested_format(request)
    _, matched, query, active, _, _ = select_candidates(request.GET)
    prefix = "Candidates_filtered" if (query or active) else "Candidates"
    return _download(import_export.build_export(kind, matched), kind, import_export.file_name(prefix, kind))
#-------------- End of the code ------------------------------


#-------------- Start Code for Template button (download empty import file) -----------------
def candidates_template(request):
    """Download an empty import file (headings + instructions)."""
    kind = _requested_format(request)
    return _download(import_export.build_template(kind), kind, import_export.file_name("Candidates_Import_Template", kind))
#-------------- End of the code ------------------------------


#-------------- Start Code for Add Candidate page view -----------------
_FORM_KEYS = ["name", "education", "department", "position", "experience", "contact", "interview_date",
              "interview_status", "interviewer", "source", "referred_by", "remark", "final_status", "expected_ctc"]


def candidate_add(request):
    """Add Candidate form. Checks every field with the same rules as Import."""
    values = {"interview_status": "Scheduled", "final_status": "Pending"}
    errors = {}

    if request.method == "POST":
        values = {key: request.POST.get(key, "").strip() for key in _FORM_KEYS}
        clean, errors = clean_candidate(values)
        if not errors:
            known = data_store.existing_keys()
            key = (data_store.contact_digits(clean["contact"]), clean["interview_date"])
            if key in known:
                errors["contact"] = f"This contact number already has an interview on this date (Sr. No. {known[key]})."
        if not errors:
            saved = data_store.add_candidate(clean)
            if _has_document_rows(request):          # documents were attached: show the details page
                good, bad = _save_documents(request, saved["sr_no"])
                good.insert(0, f"Candidate added: {saved['name']} (Sr. No. {saved['sr_no']}).")
                token = notices.stash(good, bad)
                return redirect(f"{reverse('tracker:candidate_detail', args=[saved['sr_no']])}?n={token}")
            return redirect(f"{reverse('tracker:candidates')}?added={saved['sr_no']}")

    return render(request, "tracker/candidate_form.html", {
        "page_title": "Add candidate",
        "active_nav": "candidates",
        "values": values,
        "errors": errors,
        "error_count": len(errors),
        "experience_types": EXPERIENCE_TYPES,
        "referral_source": REFERRAL_SOURCE,
        "interview_statuses": INTERVIEW_STATUSES,
        "final_statuses": FINAL_STATUSES,
        "option_lists": data_store.option_lists(values),   # dropdown choices (values typed before an error are kept)
        **_document_context(),
    })
#-------------- End of the code ------------------------------


#-------------- Start Code for Import page views -----------------
def _import_context(**extra):
    return {
        "page_title": "Import candidates",
        "active_nav": "candidates",
        "template_links": _file_links("tracker:candidates_template"),
        **extra,
    }


def candidates_import(request):
    """Import page. GET = upload form. POST = check the file and show a preview (nothing is saved yet)."""
    if request.method != "POST":
        return render(request, "tracker/candidates_import.html", _import_context())

    upload = request.FILES.get("file")
    if not upload:
        return render(request, "tracker/candidates_import.html",
                      _import_context(error="Choose a .csv, .xlsx or .xls file first."))

    result = import_export.check_upload(upload.read(), upload.name)
    token = import_export.save_staged(result["valid"]) if result["valid"] else ""
    return render(request, "tracker/candidates_import.html", _import_context(
        result=result, token=token, filename=upload.name,
        error=result["error"],
        preview=[{**row, "ctc": _ctc_text(row["expected_ctc"])} for row in result["valid"][:10]],
        problem_count=len(result["problems"]), valid_count=len(result["valid"]),
    ))


@require_POST
def candidates_import_confirm(request):
    """Second step: really save the rows that passed the check."""
    token = request.POST.get("token", "")
    rows = import_export.load_staged(token)
    if rows is None:
        return render(request, "tracker/candidates_import.html", _import_context(
            error="This import has expired or was already completed. Please upload the file again."))

    known = data_store.existing_keys()       # check again: someone may have added the same person meanwhile
    to_save, skipped = [], 0
    for row in rows:
        key = (data_store.contact_digits(row["contact"]), row["interview_date"])
        if key in known:
            skipped += 1
        else:
            known[key] = 0
            to_save.append(row)
    if to_save:
        data_store.add_candidates(to_save)
    import_export.delete_staged(token)
    return redirect(f"{reverse('tracker:candidates')}?imported={len(to_save)}&skipped={skipped}")
#-------------- End of the code ------------------------------


#-------------- Start Code for (+) button: add a new dropdown choice -----------------
@require_POST
def option_add(request):
    """Called by the (+) button on the Add form. Saves a new choice (for example a new
    Education) and answers with JSON so the page can add it to the dropdown without reloading."""
    saved, existed, error = data_store.add_option(request.POST.get("field", ""), request.POST.get("value", ""))
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)
    return JsonResponse({"ok": True, "value": saved, "existing": existed})
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidate documents: helpers -----------------
def _document_context():
    """Values the document upload rows need (Add form and Candidate details page)."""
    return {
        "doc_types": documents.DOCUMENT_TYPES,
        "doc_accept": documents.ACCEPT_ATTRIBUTE,
        "doc_allowed_text": documents.ALLOWED_TEXT,
        "doc_max_mb": settings.MAX_DOCUMENT_MB,
        "doc_max_files": settings.MAX_FILES_PER_UPLOAD,
    }


def _document_rows(request):
    """Row numbers of the files sent in this request (inputs are named doc_file_0, doc_file_1 ...)."""
    found = (re.fullmatch(r"doc_file_(\d+)", key) for key in request.FILES)
    return sorted(int(match.group(1)) for match in found if match)


def _has_document_rows(request):
    return bool(_document_rows(request))


def _save_documents(request, sr_no):
    """Check and save every file sent with the form. Returns (good messages, problem messages)."""
    good, bad = [], []
    rows = _document_rows(request)
    if len(rows) > settings.MAX_FILES_PER_UPLOAD:
        bad.append(f"Only {settings.MAX_FILES_PER_UPLOAD} documents can be added at once. The extra ones were not saved.")
        rows = rows[:settings.MAX_FILES_PER_UPLOAD]
    for number in rows:
        uploaded = request.FILES[f"doc_file_{number}"]
        _, error = documents.check_file(uploaded)
        if error:
            bad.append(error)
            continue
        try:
            record = documents.add_document(sr_no, request.POST.get(f"doc_type_{number}", ""),
                                            request.POST.get(f"doc_title_{number}", ""), uploaded)
        except ValueError as problem:
            bad.append(str(problem))
            break
        good.append(f"Document saved: {record['doc_type']} - {record['title']}.")
    return good, bad
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidate details page (documents) -----------------
def _candidate_or_404(sr_no):
    person = data_store.get_candidate(sr_no)
    if person is None:
        raise Http404("No such candidate")
    return person


def candidate_detail(request, sr_no):
    """All details of one candidate plus the documents panel (view, download, add, delete)."""
    person = _candidate_or_404(sr_no)
    good, bad = notices.take(request.GET.get("n", ""))
    return render(request, "tracker/candidate_detail.html", {
        "page_title": person["name"],
        "active_nav": "candidates",
        "person": person,
        "fields": build_candidate_detail(person),
        "docs": documents.list_documents(sr_no),
        "notices_good": good,
        "notices_bad": bad,
        **_document_context(),
    })


@require_POST
def document_upload(request, sr_no):
    """Add documents to an existing candidate."""
    _candidate_or_404(sr_no)
    if not _has_document_rows(request):
        token = notices.stash(bad=["Choose at least one file to upload."])
    else:
        good, bad = _save_documents(request, sr_no)
        token = notices.stash(good, bad)
    return redirect(f"{reverse('tracker:candidate_detail', args=[sr_no])}?n={token}#documents")


def document_file(request, sr_no, doc_id):
    """Open (PDF / images) or download (all types) one document. Only for the candidate it belongs to."""
    record = documents.get_document(sr_no, doc_id)
    path = documents.file_path(record) if record else None
    if record is None or not path.exists():
        raise Http404("No such document")
    _, content_type, can_view = documents.ALLOWED_TYPES[record["ext"]]
    show_inside_browser = can_view and not request.GET.get("download")
    response = FileResponse(open(path, "rb"), content_type=content_type,
                            as_attachment=not show_inside_browser, filename=record["original_name"])
    response["X-Content-Type-Options"] = "nosniff"
    return response


@require_POST
def document_delete(request, sr_no, doc_id):
    """Delete one document (the file and its entry)."""
    removed = documents.delete_document(sr_no, doc_id)
    if removed:
        token = notices.stash([f"Document deleted: {removed['doc_type']} - {removed['title']}."])
    else:
        token = notices.stash(bad=["That document was not found. It may already have been deleted."])
    return redirect(f"{reverse('tracker:candidate_detail', args=[sr_no])}?n={token}#documents")
#-------------- End of the code ------------------------------
