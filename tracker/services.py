# ==========================================================================
# File : tracker/services.py
# What : All calculations behind the Dashboard (counts, percentages,
#        monthly trend...). Views stay small; this file does the maths.
# Later : when SQL Server is added, only the data source changes
#         (tracker/data_store.py), these calculations can stay as they are.
# ==========================================================================

#-------------- Start Code for Imports and helpers -----------------
from collections import Counter
from datetime import date

from . import documents
from .data_store import get_candidates
from .dummy_data import FINAL_STATUSES


def _slug(text):
    """'On Hold' -> 'on-hold' (used for CSS class names)."""
    return text.lower().replace(" ", "-")


def _pct(part, whole):
    """Percentage as a plain-dot string such as '12.5' (safe inside CSS style)."""
    return f"{(part / whole * 100) if whole else 0:.1f}"


def _bars(counter, limit=None):
    """Turn a Counter into a sorted list for horizontal bar charts."""
    items = counter.most_common(limit)
    top = items[0][1] if items else 1
    return [{"label": label, "count": count, "width": _pct(count, top)} for label, count in items]


def _ctc_text(value):
    """3.5 -> '3.5', 4 -> '4.0', 3.75 -> '3.75' (lakh per annum)."""
    text = f"{value:.2f}"
    return text[:-1] if text.endswith("0") else text


def _when_label(interview_date, today):
    """'Today', 'Tomorrow' or 'in 5 days' for the upcoming interviews list."""
    days = (interview_date - today).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    return f"in {days} days"
#-------------- End of the code ------------------------------


#-------------- Start Code for Dashboard data builder -----------------
def build_dashboard_context(today=None):
    """Prepare everything the Dashboard template needs."""
    today = today or date.today()
    people = get_candidates(today)
    total = len(people)

    # ---- 1. Pipeline (Final Status counts, fixed order) ----
    status_counts = Counter(p["final_status"] for p in people)
    pipeline = [
        {
            "label": status,
            "slug": _slug(status),
            "count": status_counts.get(status, 0),
            "width": _pct(status_counts.get(status, 0), total),
            "percent": round(status_counts.get(status, 0) / total * 100) if total else 0,
        }
        for status in FINAL_STATUSES
    ]

    # ---- 2. Key numbers ----
    this_month = [p for p in people
                  if p["interview_date"].year == today.year and p["interview_date"].month == today.month]
    upcoming_all = sorted(
        (p for p in people
         if p["interview_date"] >= today and p["interview_status"] in ("Scheduled", "Rescheduled")),
        key=lambda p: p["interview_date"],
    )
    next_7_days = [p for p in upcoming_all if (p["interview_date"] - today).days <= 7]
    positive = status_counts.get("Selected", 0) + status_counts.get("Joined", 0)
    decided = positive + status_counts.get("Rejected", 0)
    average_ctc = sum(p["expected_ctc"] for p in people) / total if total else 0

    stats = [
        {"value": len(this_month), "label": "Interviews this month"},
        {"value": len(next_7_days), "label": "Interviews in the next 7 days"},
        {"value": f"{round(positive / decided * 100) if decided else 0}%", "label": "Selection rate (decided cases)"},
        {"value": f"\u20b9 {average_ctc:.1f} LPA", "label": "Average expected CTC"},
    ]

    # ---- 3. Upcoming interviews (next 5) ----
    upcoming = [
        {
            "name": p["name"],
            "position": p["position"],
            "department": p["department"],
            "date": p["interview_date"].strftime("%a, %d %b"),
            "when": _when_label(p["interview_date"], today),
            "interviewer": p["interviewer"],
            "status": p["interview_status"],
            "status_slug": _slug(p["interview_status"]),
        }
        for p in upcoming_all[:5]
    ]

    # ---- 4. Interviews per month (last 6 months, oldest first) ----
    months = []
    year, month = today.year, today.month
    for _ in range(6):
        months.append((year, month))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    months.reverse()
    per_month = Counter((p["interview_date"].year, p["interview_date"].month) for p in people)
    highest = max([per_month.get(m, 0) for m in months] + [1])
    trend = [
        {
            "label": date(y, m, 1).strftime("%b"),
            "count": per_month.get((y, m), 0),
            "height": _pct(per_month.get((y, m), 0), highest),
            "is_current": (y, m) == (today.year, today.month),
        }
        for (y, m) in months
    ]

    # ---- 5. Breakdown bars ----
    by_department = _bars(Counter(p["department"] for p in people))
    by_source = _bars(Counter(p["source"] for p in people))
    experience_counts = Counter(p["experience"] for p in people)
    experience = [
        {"label": label, "count": experience_counts.get(label, 0), "width": _pct(experience_counts.get(label, 0), total)}
        for label in ("Fresher", "Experienced")
    ]

    # ---- 6. Recent candidates (latest 8 interviews up to today) ----
    recent = sorted((p for p in people if p["interview_date"] <= today),
                    key=lambda p: p["interview_date"], reverse=True)[:8]
    recent_rows = [
        {
            "name": p["name"],
            "position": p["position"],
            "department": p["department"],
            "date": p["interview_date"].strftime("%d %b %Y"),
            "experience": p["experience"],
            "ctc": _ctc_text(p["expected_ctc"]),
            "final_status": p["final_status"],
            "final_slug": _slug(p["final_status"]),
        }
        for p in recent
    ]

    return {
        "today_label": today.strftime("%A, %d %B %Y"),
        "total": total,
        "department_count": len({p["department"] for p in people}),
        "pipeline": pipeline,
        "stats": stats,
        "upcoming": upcoming,
        "trend": trend,
        "by_department": by_department,
        "by_source": by_source,
        "experience": experience,
        "recent_rows": recent_rows,
    }
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidates page: settings, columns and filter fields -----------------
# Everything below is used ONLY by the Candidates page.
from urllib.parse import urlencode

from .dummy_data import INTERVIEW_STATUSES

PAGE_SIZE = 15   # rows shown per page on the Candidates page

# (key used in the web address ?sort=..., column heading, record key used for sorting)
# Order = order of the HR Excel sheet. To hide / reorder a column, edit this list
# AND the matching cell in templates/tracker/candidates.html.
LIST_COLUMNS = [
    ("sr_no",            "Sr. No.",               "sr_no"),
    ("name",             "Candidate Name",        "name"),
    ("education",        "Education",             "education"),
    ("department",       "Department",            "department"),
    ("position",         "Position",              "position"),
    ("experience",       "Fresher / Experienced", "experience"),
    ("contact",          "Contact No.",           "contact"),
    ("interview_date",   "Date of Interview",     "interview_date"),
    ("interview_status", "Interview Status",      "interview_status"),
    ("interviewer",      "Interviewer Name",      "interviewer"),
    ("source",           "Reference / Source",    "source"),
    ("referred_by",      "Referred By",           "referred_by"),
    ("month_year",       "Month & Year",          "interview_date"),   # sorts by real date
    ("remark",           "Remark",                "remark"),
    ("final_status",     "Final Status",          "final_status"),
    ("expected_ctc",     "Expected CTC (LPA)",    "expected_ctc"),
    ("documents",        "Documents",             "doc_count"),       # number of uploaded files
]

# Dropdown filters: (record key = also the ?name= in the address, label shown to the user)
FILTER_FIELDS = [
    ("department",       "Department"),
    ("final_status",     "Final status"),
    ("interview_status", "Interview status"),
    ("experience",       "Fresher / Experienced"),
    ("source",           "Reference / Source"),
    ("referred_by",      "Referred by (employee)"),
    ("interviewer",      "Interviewer"),
    ("month_year",       "Month & Year"),
]

# Fields searched by the search box
SEARCH_FIELDS = ["name", "contact", "education", "position", "department",
                 "interviewer", "source", "referred_by", "remark"]
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidates page: helper functions -----------------
def _filter_options(people, key):
    """Distinct values for one dropdown, in a sensible order."""
    if key == "final_status":
        return list(FINAL_STATUSES)
    if key == "interview_status":
        return list(INTERVIEW_STATUSES)
    if key == "month_year":   # chronological, not alphabetical
        ordered = sorted(people, key=lambda p: p["interview_date"])
        seen = []
        for p in ordered:
            if p["month_year"] not in seen:
                seen.append(p["month_year"])
        return seen
    return sorted({p[key] for p in people if p[key]})      # blank values are not offered as a choice


def _sort_value(person, record_key):
    """Value used for sorting (text ignores upper / lower case)."""
    value = person[record_key]
    return value.lower() if isinstance(value, str) else value


def _page_numbers(current, last):
    """Page numbers to show: first, last and 2 on each side of current ('...' = None)."""
    wanted = sorted({1, last} | set(range(max(1, current - 2), min(last, current + 2) + 1)))
    result, previous = [], 0
    for number in wanted:
        if number - previous > 1:
            result.append(None)
        result.append(number)
        previous = number
    return result
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidates page: search, filter and sort -----------------
def select_candidates(params, today=None):
    """Apply the search text, filters and sorting from the web address.
    Used by the Candidates page AND by Export (so the file matches what you see).
    Returns (all people, matching people sorted, search text, active filters, sort, direction)."""
    today = today or date.today()
    people = get_candidates(today)
    counts = documents.counts_by_candidate()          # how many documents each candidate has
    for person in people:
        person["doc_count"] = counts.get(person["sr_no"], 0)

    # ---- 1. Read search text and filters from the address ----
    query = params.get("q", "").strip()
    active = {key: params.get(key, "").strip() for key, _ in FILTER_FIELDS if params.get(key, "").strip()}

    # ---- 2. Apply search and filters ----
    needle = query.lower()
    matched = [
        p for p in people
        if all(str(p[key]) == value for key, value in active.items())
        and (not needle or any(needle in str(p[f]).lower() for f in SEARCH_FIELDS))
    ]

    # ---- 3. Sort (default: Sr. No. ascending, same as the Excel sheet) ----
    sort_keys = {key: record_key for key, _, record_key in LIST_COLUMNS}
    sort = params.get("sort", "sr_no")
    if sort not in sort_keys:
        sort = "sr_no"
    direction = "desc" if params.get("dir") == "desc" else "asc"
    matched.sort(key=lambda p: _sort_value(p, sort_keys[sort]), reverse=(direction == "desc"))
    return people, matched, query, active, sort, direction
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidates page: main data builder -----------------
def build_candidates_context(params, today=None):
    """Prepare the Candidates page. `params` = the web address options (request.GET)."""
    today = today or date.today()
    people, matched, query, active, sort, direction = select_candidates(params, today)
    total_count = len(people)

    # ---- 4. Paging ----
    result_count = len(matched)
    last_page = max(1, -(-result_count // PAGE_SIZE))          # round up
    try:
        page = min(max(int(params.get("page", 1)), 1), last_page)
    except ValueError:
        page = 1
    first = (page - 1) * PAGE_SIZE
    page_rows = matched[first:first + PAGE_SIZE]

    # ---- 5. Web-address helpers (keep search / filters / sort when clicking links) ----
    base = {"q": query, **active}
    base = {k: v for k, v in base.items() if v}

    def link(**extra):
        data = {**base, "sort": sort, "dir": direction, **extra}
        return "?" + urlencode(data)

    export_query = urlencode({**base, "sort": sort, "dir": direction})   # no page number: export ALL matching rows

    columns = []
    for key, label, _ in LIST_COLUMNS:
        is_sorted = key == sort
        columns.append({
            "key": key,
            "label": label,
            "url": link(sort=key, dir=("desc" if is_sorted and direction == "asc" else "asc"), page=1),
            "is_sorted": is_sorted,
            "arrow": ("\u25b2" if direction == "asc" else "\u25bc") if is_sorted else "",
            "aria": ("ascending" if direction == "asc" else "descending") if is_sorted else "none",
        })

    filters = [
        {
            "name": key,
            "label": label,
            "selected": active.get(key, ""),
            "options": _filter_options(people, key),
        }
        for key, label in FILTER_FIELDS
    ]

    pages = [
        {"number": n, "url": link(page=n), "is_current": n == page} if n else None
        for n in _page_numbers(page, last_page)
    ]

    # ---- 6. Rows ready for display ----
    rows = [
        {
            **p,
            "date": p["interview_date"].strftime("%d %b %Y"),
            "ctc": _ctc_text(p["expected_ctc"]),
            "interview_slug": _slug(p["interview_status"]),
            "final_slug": _slug(p["final_status"]),
        }
        for p in page_rows
    ]

    return {
        "today_label": today.strftime("%A, %d %B %Y"),
        "rows": rows,
        "columns": columns,
        "filters": filters,
        "q": query,
        "sort": sort,
        "dir": direction,
        "total_count": total_count,
        "result_count": result_count,
        "showing_from": first + 1 if result_count else 0,
        "showing_to": first + len(rows),
        "pages": pages,
        "prev_url": link(page=page - 1) if page > 1 else "",
        "next_url": link(page=page + 1) if page < last_page else "",
        "export_query": export_query,
        "has_filters": bool(query or active),
        "filter_count": len(active) + (1 if query else 0),
    }
#-------------- End of the code ------------------------------


#-------------- Start Code for Candidate details page -----------------
def build_candidate_detail(person):
    """Field list for the Candidate details page: [{label, value, chip}] in Excel order.
    chip = CSS class of a status chip, or '' for plain text."""
    rows = [
        ("Sr. No.", person["sr_no"], ""),
        ("Candidate Name", person["name"], ""),
        ("Education", person["education"] or "-", ""),
        ("Department", person["department"], ""),
        ("Position", person["position"], ""),
        ("Fresher / Experienced", person["experience"], ""),
        ("Contact No.", person["contact"], ""),
        ("Date of Interview", person["interview_date"].strftime("%d %b %Y"), ""),
        ("Interview Status", person["interview_status"], "chip--" + _slug(person["interview_status"])),
        ("Interviewer Name", person["interviewer"], ""),
        ("Reference / Source", person["source"], ""),
    ]
    if person.get("referred_by"):
        rows.append(("Referred By (Employee)", person["referred_by"], ""))
    rows += [
        ("Month & Year", person["month_year"], ""),
        ("Final Status", person["final_status"], "chip--" + _slug(person["final_status"])),
        ("Expected CTC (LPA)", _ctc_text(person["expected_ctc"]), ""),
        ("Remark", person["remark"] or "-", ""),
    ]
    return [{"label": a, "value": b, "chip": c} for a, b, c in rows]
#-------------- End of the code ------------------------------
