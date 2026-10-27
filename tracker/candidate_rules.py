# ==========================================================================
# File : tracker/candidate_rules.py
# What : The rules for ONE candidate record, used by the Add form AND the
#        Import page, so both check data in exactly the same way.
#        Contains: column list (Excel order), accepted column names,
#        and the validation / cleaning function.
# ==========================================================================

#-------------- Start Code for Imports -----------------
import re
from datetime import date, datetime, timedelta

from .dummy_data import FINAL_STATUSES, INTERVIEW_STATUSES
#-------------- End of the code ------------------------------


#-------------- Start Code for Columns used by Export, Template and Import -----------------
# (record key, column heading written in Export / Template files)
# Same order as the HR Excel sheet. Change a heading here to rename it everywhere.
FILE_COLUMNS = [
    ("sr_no",            "Sr. No."),
    ("name",             "Candidate Name"),
    ("education",        "Education"),
    ("department",       "Department"),
    ("position",         "Position"),
    ("experience",       "Fresher / Experienced"),
    ("contact",          "Contact No."),
    ("interview_date",   "Date of Interview"),
    ("interview_status", "Interview Status"),
    ("interviewer",      "Interviewer Name"),
    ("source",           "Reference / Source"),
    ("referred_by",      "Referred By (Employee)"),
    ("month_year",       "Month & Year"),
    ("remark",           "Remark"),
    ("final_status",     "Final Status"),
    ("expected_ctc",     "Expected CTC (LPA)"),
]

# Other headings accepted when importing (letters and numbers only, lower case).
# Example: "Contact No.", "contact no", "CONTACT_NO" all become "contactno".
HEADING_ALIASES = {
    "sr_no": ["srno", "serialno", "sno", "slno"],
    "name": ["candidatename", "name", "candidate"],
    "education": ["education", "qualification"],
    "department": ["department", "dept"],
    "position": ["position", "designation", "post", "role"],
    "experience": ["fresherexperienced", "fresherexperience", "experience", "experiencetype", "type"],
    "contact": ["contactno", "contactnumber", "contact", "mobile", "mobileno", "mobilenumber", "phone", "phoneno"],
    "interview_date": ["dateofinterview", "interviewdate", "date"],
    "interview_status": ["interviewstatus"],
    "interviewer": ["interviewername", "interviewer"],
    "source": ["referencesource", "reference", "source"],
    "referred_by": ["referredbyemployee", "referredby", "referredbyemployeename", "referrer", "referrername", "employeename", "referralname"],
    "month_year": ["monthyear"],
    "remark": ["remark", "remarks", "comment", "comments"],
    "final_status": ["finalstatus", "status"],
    "expected_ctc": ["expectedctclpa", "expectedctc", "ctc"],
}

# Columns that MUST exist in an import file, and must have a value in every row.
REQUIRED_KEYS = ["name", "department", "position", "experience", "contact", "interview_date", "expected_ctc"]

# Columns that are calculated by the portal; values in the file are ignored.
IGNORED_KEYS = ["sr_no", "month_year"]

EXPERIENCE_TYPES = ["Fresher", "Experienced"]


def normalise_heading(text):
    """'Fresher / Experienced' -> 'fresherexperienced'."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def heading_lookup():
    """{'contactno': 'contact', 'mobile': 'contact', ...}"""
    lookup = {}
    for key, heading in FILE_COLUMNS:
        lookup[normalise_heading(heading)] = key
    for key, names in HEADING_ALIASES.items():
        for name in names:
            lookup.setdefault(name, key)
    return lookup


def heading_of(key):
    """Column heading for a record key."""
    return dict(FILE_COLUMNS)[key]
#-------------- End of the code ------------------------------


#-------------- Start Code for Dropdown fields that have a (+) button -----------------
# record key -> (label used in messages, longest text allowed)
# These are the fields whose dropdown list the user can extend with the (+) button.
# Fresher / Experienced, Interview Status and Final Status are NOT here on purpose:
# the Dashboard colours and counts depend on their fixed values.
OPTION_FIELDS = {
    "education":   ("Education", 60),
    "department":  ("Department", 50),
    "position":    ("Position", 80),
    "source":      ("Reference / Source", 60),
    "interviewer": ("Interviewer name", 60),
    "referred_by": ("Referred by (employee name)", 80),
}

# When Reference / Source is this value, "Referred By (Employee)" must be filled in.
REFERRAL_SOURCE = "Employee Referral"

# Values the portal fills in itself when a field is left blank. They are not real choices.
PLACEHOLDER_VALUES = {"not assigned", "not specified"}
#-------------- End of the code ------------------------------


#-------------- Start Code for Small cleaning helpers -----------------
_FORMULA_START = ("=", "+", "-", "@")


def clean_text(value):
    """Any cell value -> tidy single-line text ('' when empty).
    Whole numbers from Excel (9000000001.0) lose the '.0'."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = re.sub(r"\s+", " ", str(value)).strip()
    # Exported files protect text starting with = + - @ with a leading apostrophe; remove it again.
    if len(text) > 1 and text[0] == "'" and text[1] in _FORMULA_START:
        text = text[1:]
    return text


def _pick(text, options, extra=None):
    """Match text to one of `options` ignoring case, spaces and dashes. Returns None if no match."""
    wanted = re.sub(r"[^a-z]", "", text.lower())
    table = {re.sub(r"[^a-z]", "", option.lower()): option for option in options}
    for alias, option in (extra or {}).items():
        table[alias] = option
    return table.get(wanted)


_DATE_FORMATS = [
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d-%b-%Y", "%d %b %Y",
    "%d-%B-%Y", "%d %B %Y", "%d/%m/%y", "%d-%m-%y", "%d-%b-%y", "%d %b, %Y",
    "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
]


def parse_date(value):
    """Cell / form value -> date, or None when it is not a date.
    Written dates are read day-first (25/10/2026 = 25 October), as used in India."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 20000 < value < 80000:                       # Excel date number
            return (datetime(1899, 12, 30) + timedelta(days=float(value))).date()
        return None
    text = clean_text(value)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_contact(value):
    """Return the contact as '98765 43210', or None if it is not a valid 10-digit mobile number."""
    digits = re.sub(r"\D", "", clean_text(value))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        return None
    return f"{digits[:5]} {digits[5:]}"


def parse_ctc(value):
    """'3.5', '3.5 LPA', 'Rs. 4' -> 3.5 / 4.0 (lakh per annum). None when not a valid number."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = re.sub(r"(?i)lpa|lakhs?|lacs?|rs\.?|inr|\u20b9", "", clean_text(value)).strip()
        if re.fullmatch(r"\d+,\d{1,2}", text):      # "2,5" is a decimal comma = 2.5
            text = text.replace(",", ".")
        text = text.replace(",", "")
        try:
            number = float(text)
        except ValueError:
            return None
    return round(number, 2) if 0 < number <= 999 else None
#-------------- End of the code ------------------------------


#-------------- Start Code for Main validation function -----------------
def clean_candidate(raw):
    """Check one candidate and return (clean_record, errors).

    raw    : dictionary with the record keys (name, contact, ...) and raw values
             (text from the form, or mixed values from a file).
    errors : {record key: message}. Empty dictionary = the record is valid.
    """
    errors = {}
    clean = {}

    def text_field(key, label, maximum, required=False, default=""):
        value = clean_text(raw.get(key))
        if not value and required:
            errors[key] = f"{label} is required."
        elif len(value) > maximum:
            errors[key] = f"{label} is too long (maximum {maximum} characters)."
        clean[key] = value or default

    # --- Candidate, education, department, position ---
    text_field("name", "Candidate name", 100, required=True)
    if clean["name"] and not re.search(r"[A-Za-z\u0900-\u097F]", clean["name"]) and "name" not in errors:
        errors["name"] = "Candidate name must contain letters."
    text_field("education", "Education", 60)
    text_field("department", "Department", 50, required=True)
    text_field("position", "Position", 80, required=True)

    # --- Fresher / Experienced ---
    typed = clean_text(raw.get("experience"))
    experience = _pick(typed, EXPERIENCE_TYPES, {"fresh": "Fresher", "exp": "Experienced", "experience": "Experienced"})
    if not typed:
        errors["experience"] = "Select Fresher or Experienced."
    elif not experience:
        errors["experience"] = "Use Fresher or Experienced."
    clean["experience"] = experience or typed

    # --- Contact number ---
    contact = parse_contact(raw.get("contact"))
    if contact is None:
        errors["contact"] = "Enter a 10-digit mobile number starting with 6, 7, 8 or 9."
    clean["contact"] = contact or clean_text(raw.get("contact"))

    # --- Date of interview ---
    typed_date = raw.get("interview_date")
    interview_date = parse_date(typed_date)
    if not clean_text(typed_date) and not isinstance(typed_date, (date, datetime)):
        errors["interview_date"] = "Date of interview is required."
    elif interview_date is None or not (2000 <= interview_date.year <= 2100):
        errors["interview_date"] = "Use a valid date, for example 25-Oct-2026 or 25/10/2026."
        interview_date = None
    clean["interview_date"] = interview_date

    # --- Interview status / final status (blank = default) ---
    typed = clean_text(raw.get("interview_status"))
    status = _pick(typed, INTERVIEW_STATUSES) if typed else "Scheduled"
    if status is None:
        errors["interview_status"] = "Use one of: " + ", ".join(INTERVIEW_STATUSES) + "."
    clean["interview_status"] = status or typed

    typed = clean_text(raw.get("final_status"))
    final = _pick(typed, FINAL_STATUSES) if typed else "Pending"
    if final is None:
        errors["final_status"] = "Use one of: " + ", ".join(FINAL_STATUSES) + "."
    clean["final_status"] = final or typed

    # --- Optional text fields ---
    text_field("interviewer", "Interviewer name", 60, default="Not assigned")
    text_field("source", "Reference / Source", 60, default="Not specified")
    text_field("remark", "Remark", 300)

    # --- Referred by (only for Employee Referral) ---
    # "employee referral", "Employee  Referral" ... are all stored as "Employee Referral".
    is_referral = re.sub(r"[^a-z]", "", clean["source"].lower()) == re.sub(r"[^a-z]", "", REFERRAL_SOURCE.lower())
    referrer = clean_text(raw.get("referred_by"))
    if is_referral:
        clean["source"] = REFERRAL_SOURCE
        if not referrer:
            errors["referred_by"] = "Referred by (employee name) is required when Reference / Source is Employee Referral."
        elif len(referrer) > 80:
            errors["referred_by"] = "Referred by (employee name) is too long (maximum 80 characters)."
        elif not re.search(r"[A-Za-z\u0900-\u097F]", referrer):
            errors["referred_by"] = "Referred by (employee name) must contain letters."
    clean["referred_by"] = referrer if is_referral else ""    # ignored for every other source

    # --- Expected CTC ---
    ctc = parse_ctc(raw.get("expected_ctc"))
    if ctc is None:
        errors["expected_ctc"] = "Enter the expected CTC in lakh per annum, for example 3.5."
    clean["expected_ctc"] = ctc

    if interview_date:
        clean["month_year"] = interview_date.strftime("%b %Y")
    return clean, errors
#-------------- End of the code ------------------------------
