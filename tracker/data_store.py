# ==========================================================================
# File : tracker/data_store.py
# What : Temporary "storage" for candidates while there is no database.
#        Candidates live in one file: data/candidates.json
#        (first run: filled with the demo candidates from dummy_data.py).
# Later : when SQL Server is connected, replace the functions in this file
#         (get_candidates, add_candidate, add_candidates, existing_keys)
#         with database queries. The rest of the portal does not change.
# Note  : a simple lock protects the file when several HR users save at
#         the same time on ONE running server. It is meant for testing,
#         not for heavy multi-user use.
# ==========================================================================

#-------------- Start Code for Imports and file location -----------------
import json
import os
import re
import threading
from datetime import date

from django.conf import settings

from .candidate_rules import OPTION_FIELDS, PLACEHOLDER_VALUES, REFERRAL_SOURCE, clean_text
from .dummy_data import get_candidates as _demo_candidates

_LOCK = threading.RLock()


def _data_file():
    """Full path of data/candidates.json (folder is created when needed)."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return settings.DATA_DIR / "candidates.json"
#-------------- End of the code ------------------------------


#-------------- Start Code for Reading and writing the file -----------------
def _to_file_format(person):
    """Dates become text ('2026-10-25') so they can be saved as JSON."""
    saved = dict(person)
    saved["interview_date"] = person["interview_date"].isoformat()
    saved.pop("month_year", None)            # always calculated again when loading
    return saved


def _from_file_format(saved):
    """Reverse of _to_file_format: text date -> date, and add Month & Year."""
    person = dict(saved)
    person.setdefault("referred_by", "")          # records saved before this field existed
    person["interview_date"] = date.fromisoformat(saved["interview_date"])
    person["month_year"] = person["interview_date"].strftime("%b %Y")
    return person


def _read_all():
    """Return the saved candidates (list of dictionaries). Creates demo data on first use."""
    path = _data_file()
    if not path.exists():
        _write_all([_to_file_format(p) for p in _demo_candidates()])
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["candidates"]


def _write_all(saved_list):
    """Save the whole list safely (write to a temp file first, then swap)."""
    path = _data_file()
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump({"version": 1, "candidates": saved_list}, handle, ensure_ascii=False, indent=1)
    os.replace(temp, path)
#-------------- End of the code ------------------------------


#-------------- Start Code for Public functions used by the pages -----------------
def get_candidates(today=None):
    """All candidates as dictionaries (same keys the pages already use).
    `today` is accepted only to match the older function; it is not needed now."""
    with _LOCK:
        return [_from_file_format(item) for item in _read_all()]


def get_candidate(sr_no):
    """One candidate by Sr. No. (None if there is no such candidate)."""
    for person in get_candidates():
        if person["sr_no"] == sr_no:
            return person
    return None


def contact_digits(contact):
    """'90000 00001' -> '9000000001' (used to compare contact numbers)."""
    return re.sub(r"\D", "", str(contact))


def existing_keys():
    """Set of (contact digits, interview date) used to stop duplicate entries.
    Returns a dictionary {key: sr_no} so messages can name the existing row."""
    with _LOCK:
        return {(contact_digits(i["contact"]), date.fromisoformat(i["interview_date"])): i["sr_no"]
                for i in _read_all()}


def add_candidates(clean_rows):
    """Save one or many new candidates. Sr. No. is given automatically.
    Returns the list of saved candidates (with sr_no)."""
    with _LOCK:
        saved_list = _read_all()
        next_no = max((i["sr_no"] for i in saved_list), default=0) + 1
        added = []
        for row in clean_rows:
            person = dict(row)
            person["sr_no"] = next_no
            next_no += 1
            saved_list.append(_to_file_format(person))
            added.append(person)
        _write_all(saved_list)
        return added


def add_candidate(clean_row):
    """Save a single candidate and return it (with its new sr_no)."""
    return add_candidates([clean_row])[0]


#-------------- End of the code ------------------------------


#-------------- Start Code for Dropdown lists and the (+) button -----------------
# Extra choices added with the (+) button are kept in data/options.json:
#   {"education": ["B.C.A."], "position": [...], ...}
# The dropdown on the Add form shows: values already used by saved candidates
# + values added with (+). (Later: a database table replaces options.json.)
def _options_file():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return settings.DATA_DIR / "options.json"


def _read_options():
    path = _options_file()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def same_text(text):
    """Compare ignoring case, spaces and dots: 'B.C.A.' = 'bca' = 'B C A'."""
    return re.sub(r"[^0-9a-z\u0900-\u097f]", "", text.lower())


def option_lists(selected=None):
    """Dropdown choices for every (+) field: {'education': [...], ...}, sorted A-Z.
    `selected` = {field: value} currently chosen; it is always kept in the list
    (for example after a form error)."""
    people = get_candidates()
    extra = _read_options()
    lists = {}
    for field in OPTION_FIELDS:
        values = {p[field] for p in people if p.get(field)}
        values.update(extra.get(field, []))
        if field == "source":
            values.add(REFERRAL_SOURCE)               # always offered, the Add form needs it
        if selected and selected.get(field):
            values.add(selected[field])
        lists[field] = sorted((v for v in values if v.lower() not in PLACEHOLDER_VALUES), key=str.lower)
    return lists


def add_option(field, value):
    """Add a new choice for a dropdown. Returns (saved_value, already_existed, error_text).
    If the same choice already exists (ignoring case / dots / spaces) the existing one is returned."""
    if field not in OPTION_FIELDS:
        return "", False, "Unknown field."
    label, longest = OPTION_FIELDS[field]
    value = clean_text(value)
    if not value:
        return "", False, f"Type the new {label.lower()} first."
    if len(value) > longest:
        return "", False, f"{label} is too long (maximum {longest} characters)."
    if not re.search(r"[A-Za-z\u0900-\u097F]", value):
        return "", False, f"{label} must contain letters."
    if value.lower() in PLACEHOLDER_VALUES:
        return "", False, "Please type a real name."

    with _LOCK:
        for existing in option_lists()[field]:
            if same_text(existing) == same_text(value):
                return existing, True, ""
        extra = _read_options()
        extra.setdefault(field, []).append(value)
        path = _options_file()
        temp = path.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(extra, handle, ensure_ascii=False, indent=1)
        os.replace(temp, path)
    return value, False, ""
#-------------- End of the code ------------------------------
