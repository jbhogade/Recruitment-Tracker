# ==========================================================================
# File : tracker/services.py
# What : All calculations behind the Dashboard (counts, percentages,
#        monthly trend...). Views stay small; this file does the maths.
# Later : when SQL Server is added, only the data source changes
#         (get_candidates), these calculations can stay as they are.
# ==========================================================================

#-------------- Start Code for Imports and helpers -----------------
from collections import Counter
from datetime import date

from .dummy_data import FINAL_STATUSES, get_candidates


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
            "ctc": f"{p['expected_ctc']:.1f}",
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
