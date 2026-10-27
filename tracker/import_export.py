# ==========================================================================
# File : tracker/import_export.py
# What : The logic behind the Export, Template and Import buttons.
#        - build_export()    candidates -> CSV / XLSX / XLS file
#        - build_template()  empty import file with instructions
#        - check_upload()    read an uploaded file, check every row
#        - save_staged() / load_staged()  keep checked rows until the user confirms
# ==========================================================================

#-------------- Start Code for Imports -----------------
import json
import re
import secrets
import time
from datetime import date

from django.conf import settings

from . import data_store
from .candidate_rules import (
    EXPERIENCE_TYPES, FILE_COLUMNS, IGNORED_KEYS, REQUIRED_KEYS,
    clean_candidate, heading_lookup, heading_of,
)
from .dummy_data import FINAL_STATUSES, INTERVIEW_STATUSES
from .file_io import FORMATS, FileReadError, read_table, write_table

# Positions (0 = first column) of special columns in Export / Template files
_KEYS = [key for key, _ in FILE_COLUMNS]
_DATE_COLS = (_KEYS.index("interview_date"),)
_TEXT_COLS = (_KEYS.index("contact"),)
_NUMBER_COLS = (_KEYS.index("expected_ctc"),)
#-------------- End of the code ------------------------------


#-------------- Start Code for Export and Template files -----------------
def build_export(kind, people):
    """Return the bytes of an export file holding `people` (list of candidate dictionaries)."""
    rows = [[person.get(key) for key in _KEYS] for person in people]
    return write_table(kind, [heading for _, heading in FILE_COLUMNS], rows,
                       date_columns=_DATE_COLS, text_columns=_TEXT_COLS, number_columns=_NUMBER_COLS)


def _instruction_rows():
    """Rows of the 'Instructions' sheet inside Excel templates."""
    required = set(REQUIRED_KEYS)
    notes = [("Column", "Required?", "What to enter", "Example")]
    help_text = {
        "sr_no": ("Leave blank. Numbers are given automatically.", ""),
        "name": ("Full name of the candidate.", "Aarav Kulkarni"),
        "education": ("Highest qualification (optional).", "B.E. (Computer)"),
        "department": ("Department the candidate applied for.", "IT"),
        "position": ("Job position.", "Software Developer"),
        "experience": ("Fresher or Experienced.", "Experienced"),
        "contact": ("10-digit mobile number. +91 and spaces are accepted.", "98765 43210"),
        "interview_date": ("Date of interview. Day first: 25-Oct-2026 or 25/10/2026.", "25-Oct-2026"),
        "interview_status": ("One of: " + ", ".join(INTERVIEW_STATUSES) + ". Blank = Scheduled.", "Scheduled"),
        "interviewer": ("Name of the interviewer. Blank = Not assigned.", "Rahul Deshmukh"),
        "source": ("Naukri, LinkedIn, Walk-in, Employee Referral... Blank = Not specified.", "Naukri"),
        "referred_by": ("Employee who referred the candidate. REQUIRED when Reference / Source is Employee Referral, otherwise leave blank.", "Anil Pawar"),
        "month_year": ("Leave blank. Calculated from the interview date.", ""),
        "remark": ("Any note (optional, up to 300 characters).", "Good communication"),
        "final_status": ("One of: " + ", ".join(FINAL_STATUSES) + ". Blank = Pending.", "Pending"),
        "expected_ctc": ("Expected CTC in lakh per annum (LPA), number only.", "3.5"),
    }
    for key, heading in FILE_COLUMNS:
        text, example = help_text[key]
        notes.append((heading, "Yes" if key in required else "No", text, example))
    notes += [
        ("", "", "", ""),
        ("Rules", "", "Do not rename or delete the column headings in row 1 of the 'Candidates' sheet.", ""),
        ("", "", "A row is skipped (and reported) if a required value is missing or wrong.", ""),
        ("", "", "A row is also skipped if the same contact number already has an interview on the same date.", ""),
        ("", "", "If Reference / Source is Employee Referral, Referred By (Employee) must be filled in.", ""),
        ("", "", "You can import a file exported from this portal. Sr. No. and Month & Year are ignored.", ""),
    ]
    return notes


def build_template(kind):
    """Return the bytes of an empty import file (headings only; Excel files also get an 'Instructions' sheet)."""
    positions = {key: _KEYS.index(key) for key in ("experience", "interview_status", "final_status")}
    return write_table(
        kind, [heading for _, heading in FILE_COLUMNS], [],
        date_columns=_DATE_COLS, text_columns=_TEXT_COLS, number_columns=_NUMBER_COLS,
        notes=_instruction_rows() if kind != "csv" else None,
        dropdowns={
            positions["experience"]: EXPERIENCE_TYPES,
            positions["interview_status"]: INTERVIEW_STATUSES,
            positions["final_status"]: FINAL_STATUSES,
        } if kind == "xlsx" else None,
    )


def file_name(prefix, kind):
    """'Candidates_2026-10-25_1430.xlsx'"""
    return f"{prefix}_{time.strftime('%Y-%m-%d_%H%M')}.{FORMATS[kind]['ext']}"
#-------------- End of the code ------------------------------


#-------------- Start Code for Checking an uploaded file -----------------
def check_upload(content, filename):
    """Read an uploaded file and check every row. Nothing is saved here.

    Returns a dictionary:
      valid        : list of clean candidate records ready to save
      problems     : list of {row, name, messages} for rows that cannot be imported
      total_rows   : number of data rows found in the file
      ignored      : column headings in the file that the portal does not use
      error        : text when the whole file is unusable (otherwise '')
    """
    result = {"valid": [], "problems": [], "total_rows": 0, "ignored": [], "error": ""}

    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        result["error"] = f"The file is larger than {settings.MAX_UPLOAD_MB} MB. Split it into smaller files."
        return result
    try:
        headings, rows = read_table(content, filename)
    except FileReadError as error:
        result["error"] = str(error)
        return result
    if len(rows) > settings.MAX_IMPORT_ROWS:
        result["error"] = f"The file has {len(rows)} rows. At most {settings.MAX_IMPORT_ROWS} rows can be imported at once."
        return result

    # ---- Match file headings to our fields ----
    lookup = heading_lookup()
    column_of = {}                       # record key -> position in the file
    for position, heading in enumerate(headings):
        key = lookup.get(re.sub(r"[^a-z0-9]", "", heading.lower()))
        if key and key not in column_of:
            column_of[key] = position
        elif heading and not key:
            result["ignored"].append(heading)
    missing = [heading_of(key) for key in REQUIRED_KEYS if key not in column_of]
    if missing:
        result["error"] = ("These required columns were not found in row 1: " + ", ".join(missing) +
                           ". Download the template and copy your data into it.")
        return result

    # ---- Check every row ----
    known = data_store.existing_keys()           # already saved candidates
    # Employee names already in use: "anil pawar" in the file becomes "Anil Pawar" (no near-duplicate names)
    names = {data_store.same_text(n): n for n in data_store.option_lists()["referred_by"]}
    seen_in_file = {}                            # same contact + date repeated inside this file
    result["total_rows"] = len(rows)
    for row_number, values in rows:
        raw = {key: (values[pos] if pos < len(values) else None)
               for key, pos in column_of.items() if key not in IGNORED_KEYS}
        clean, errors = clean_candidate(raw)
        # Add the column name in front, unless the message already starts with it.
        messages = [message if message.lower().startswith(heading_of(key).split(" (")[0].lower())
                    else f"{heading_of(key)}: {message}"
                    for key, message in errors.items()]

        if clean.get("referred_by") and "referred_by" not in errors:
            clean["referred_by"] = names.setdefault(data_store.same_text(clean["referred_by"]), clean["referred_by"])

        if not errors:
            key = (data_store.contact_digits(clean["contact"]), clean["interview_date"])
            if key in known:
                messages.append(f"Already saved: this contact number already has an interview on this date (Sr. No. {known[key]}).")
            elif key in seen_in_file:
                messages.append(f"Repeated in this file: same contact number and date as row {seen_in_file[key]}.")
            else:
                seen_in_file[key] = row_number

        if messages:
            result["problems"].append({"row": row_number, "name": str(raw.get("name") or "").strip() or "(no name)", "messages": messages})
        else:
            result["valid"].append(clean)
    return result
#-------------- End of the code ------------------------------


#-------------- Start Code for Keeping checked rows until the user confirms -----------------
_TOKEN = re.compile(r"[0-9a-f]{32}")


def _stage_folder():
    folder = settings.DATA_DIR / "import_staging"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_staged(valid_rows):
    """Keep the checked rows in a temporary file and return its token."""
    folder = _stage_folder()
    for old in folder.glob("*.json"):                       # remove files older than 1 day
        if time.time() - old.stat().st_mtime > 86400:
            old.unlink(missing_ok=True)
    token = secrets.token_hex(16)
    saved = [{**row, "interview_date": row["interview_date"].isoformat()} for row in valid_rows]
    (folder / f"{token}.json").write_text(json.dumps(saved), encoding="utf-8")
    return token


def load_staged(token):
    """Return the kept rows for a token (None if the token is wrong or expired)."""
    if not _TOKEN.fullmatch(token or ""):
        return None
    path = _stage_folder() / f"{token}.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [{**row, "interview_date": date.fromisoformat(row["interview_date"])} for row in rows]


def delete_staged(token):
    if _TOKEN.fullmatch(token or ""):
        (_stage_folder() / f"{token}.json").unlink(missing_ok=True)
#-------------- End of the code ------------------------------
