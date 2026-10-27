# Recruitment Tracker (v1.0)

A Django web portal for the HR team to record and track recruitment: candidates, interviews, statuses and expected CTC.

**Current phase: web pages only. There is no database yet.** The first run creates fake (dummy) candidates; everything you add or import afterwards is kept in the file `data/candidates.json` (temporary storage for testing). SQL Server will be connected in a later phase.

## 1. Prerequisites

| Need | Details |
|---|---|
| Python | 3.10 or newer (3.12 recommended). Download from python.org and tick **"Add python.exe to PATH"** during install. |
| pip | Comes with Python. |
| Web browser | Any modern Chrome / Edge / Firefox. |
| Code editor (optional) | VS Code with the "Python" and "Django" extensions. |

Check Python is ready: open Command Prompt and run `python --version`.

Python packages (installed by `run_server.bat`, or by `pip install -r requirements.txt`): Django, openpyxl (.xlsx), xlrd (read .xls), xlwt (write .xls).

## 2. Setup and run (Windows)

**Easy way:** double-click `run_server.bat`. Then open <http://127.0.0.1:8000>.

**Manual way** (Command Prompt, inside the project folder):

```
cd /d D:\Recruitment_Tracker_v1-0
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Stop the server with `CTRL+C`.

**Open on other HR PCs in the office network (optional):**
1. Start with `python manage.py runserver 0.0.0.0:8000` (or another port, e.g. `8012`).
2. Others open `http://<this-PC-IP>:8000`. Windows Firewall may ask for permission; allow Python / the port.
3. No IP address needs to be edited: `config/settings.py` detects this PC's name and IP addresses automatically at startup.
4. If HR opens the portal through some other name (a DNS alias), add it before starting: `set RT_ALLOWED_HOSTS=hr-portal,192.168.0.50` (Command Prompt).

## 3. Folder structure

```
Recruitment_Tracker_v1-0/
|-- manage.py              Django command tool (run server, checks)
|-- run_server.bat         One-click start for Windows
|-- requirements.txt       Python packages needed
|-- README.md              This file
|-- CLAUDE.md              Project guide: what it is, stack, decisions, status, rules (updated after every change)
|-- CHANGELOG.md           Every add / change / fix / removal with date and time
|-- config/                Project-wide settings
|   |-- settings.py        Main configuration (database block is empty on purpose)
|   |-- urls.py            Top-level address list
|-- tracker/               The Recruitment Tracker app
|   |-- dummy_data.py      FAKE candidate records used to create the first demo data
|   |-- documents.py       Candidate documents: allowed file types, checks, storage
|   |-- notices.py         One-time messages shown after a redirect
|   |-- data_store.py      Temporary storage (data/candidates.json); replaced by SQL Server later
|   |-- candidate_rules.py Field rules + accepted column names (Add form and Import use the same rules)
|   |-- file_io.py         Reads / writes CSV, XLSX and XLS files
|   |-- import_export.py   Export, Template and Import checking logic
|   |-- services.py        Dashboard calculations (counts, %, trends)
|   |-- views.py           One function per page
|   |-- urls.py            Page addresses
|   |-- context_processors.py   Theme list shared by all pages
|-- templates/             HTML pages
|   |-- base.html          Common page frame (menu + top bar)
|   |-- partials/          Reusable pieces (_sidebar, _topbar, _option_field = dropdown with + button, _document_rows = file upload rows)
|   |-- tracker/           One HTML file per page (dashboard, candidates, candidate_form, candidates_import, candidate_detail)
|-- static/
|   |-- css/               themes.css (colours), base.css (shared), dashboard.css, candidates.css, forms.css, detail.css (one per page type)
|   |-- js/                theme.js (theme switcher), candidates.js (auto-apply filters), option_adder.js (+ button), documents.js (document rows)
|-- data/                  Created automatically: candidates.json, options.json (+ choices), documents.json + documents/<Sr. No.>/ (uploaded files). BACK UP THIS FOLDER
|                          (also import_staging/ and notices/ = temporary files)
|-- tools/
    |-- changelog_add.py   Adds a timestamped line to CHANGELOG.md
    |-- reset_demo_data.py Deletes saved candidates and restores fresh demo data
```

## 4. Themes

Five themes, switched with the round buttons at the top right. The choice is remembered in the browser.

| Theme | Look |
|---|---|
| Dark (default) | Ink black with teal accent |
| Grey | Charcoal with amber accent |
| Lite | Light mode with indigo accent |
| Blue | Deep navy with sky-blue accent |
| Emerald | Deep green with mint accent |

To change a colour: edit the matching block in `static/css/themes.css`.
To add a theme: copy a block in `themes.css`, rename it, and add one line in `tracker/context_processors.py`.

Speed: no external fonts, no CDN, no JavaScript chart libraries. Charts are plain CSS, so pages load fast and also work without internet.

## 5. Candidate fields (from the HR Excel sheet)

Sr. No., Candidate Name, Education, Department, Position, Fresher / Experienced, Contact No., Date of Interview, Interview Status, Interviewer Name, Reference/Source, Month & Year, Remark, Final Status, Expected CTC.

**Added field:** **Referred By (Employee)** - shown right after Reference / Source. When Reference / Source is **Employee Referral**, HR must choose the employee who referred the candidate (dropdown with a + button for new names). For every other source it stays blank.

Allowed values used for now (to be confirmed with HR):
- **Interview Status:** Scheduled, Rescheduled, Completed, No Show
- **Final Status:** Pending, On Hold, Selected, Joined, Rejected
- **Expected CTC:** stored as lakh per annum (LPA), for example `3.6`

## 5a. Candidates page

- Shows all 15 Excel columns plus Referred By (employee). Sr. No. and Candidate Name stay in place while you scroll sideways.
- **Search** looks in name, contact, education, position, department, interviewer, source and remark.
- **Filters:** Department, Final status, Interview status, Fresher / Experienced, Reference / Source, Referred by (employee), Interviewer, Month & Year. They can be combined.
- **Sorting:** click a column heading (click again to reverse). **Paging:** 15 candidates per page.
- The web address holds the search / filters, so a filtered list can be bookmarked or shared. Dashboard pipeline numbers link to the matching filtered list.

### Buttons: Add candidate, Import, Export, Template

| Button | What it does |
|---|---|
| **Add candidate** | Form for one candidate. Choosing **Employee Referral** under Reference / Source opens a required "Referred by (employee)" dropdown. Sr. No. and Month & Year are automatic. Wrong values are explained next to the field and nothing is saved until all are correct. |
| **Import** | Upload a **.csv, .xlsx or .xls** file. Step 1: the file is only checked and a preview is shown, with every problem row listed (row number and what to fix). Step 2: you press "Import N candidates" and only the correct rows are saved. |
| **Export** | Downloads **CSV, Excel (.xlsx) or Excel 97-2003 (.xls)**. Contains **all candidates that match the current search / filters / sorting** (not only the visible page). Clear the filters to export everyone. |
| **Template** | Downloads an empty import file in **CSV, .xlsx or .xls**. The Excel versions have an "Instructions" sheet (what to enter in each column); the .xlsx version also has drop-down lists for Fresher / Experienced, Interview Status and Final Status. |

### Plus (+) button on the Add candidate form

**Education, Department, Position, Reference / Source, Interviewer and Referred by (employee)** are dropdowns with a **+** button beside them. If the value you need is not in the list (for example B.C.A. under Education):
1. Press **+** (a small box opens under the dropdown).
2. Type the new value and press **Add** (or Enter).
3. It is saved for everyone, put in the dropdown in A-Z order, and selected. You carry on filling the form; nothing else is lost.

Notes:
- If the value already exists in another spelling (`BCA`, `b.c.a.`), the existing one is selected instead of creating a duplicate.
- Values used by saved or imported candidates always appear in the dropdowns. Values added with + are kept in `data/options.json`.
- Fresher / Experienced, Interview Status and Final Status are fixed lists on purpose, because the Dashboard colours and counts depend on them.
- The list on the Candidates page filters shows a value once at least one candidate uses it.

### Candidate documents (CV, certificates ...)

Each candidate can have **many documents**: CV / Resume, 10th Certificate, 12th Certificate, Graduation Certificate, Post-Graduation Certificate and Other.

- **Allowed formats only:** PDF, images (JPG, PNG, GIF, BMP, WEBP, TIF) and MS Word (DOC, DOCX). Up to **10 MB** per file, 10 files at a time, 30 per candidate (`MAX_DOCUMENT_MB`, `MAX_FILES_PER_UPLOAD`, `MAX_DOCUMENTS_PER_CANDIDATE` in `config/settings.py`).
- **While adding a candidate:** the "Documents" section at the bottom. Choose the type, optionally a name, pick the file; press **+ Add another document** for more rows.
- **Later:** click the candidate's name (or "3 files" in the Documents column) to open the **Candidate details** page. There you can **View** (PDF and images open in the browser), **Download**, **Delete** (asks first) and add more documents.
- Files are checked by their **content**, not only the name: a program renamed to `.pdf`, SVG files, Word files with macros (`.docm`) and Excel files renamed to `.doc` are refused.
- Where they are saved: `data/documents/<Sr. No.>/` (random file names; the original name is kept for download) and the list in `data/documents.json`. **Back up the whole `data` folder.**
- Import and Export do not include documents (only candidate data).
- **Privacy:** documents contain personal data. There is no login yet, so anyone who can open the portal can open the documents. Limit who can reach the PC / port (Windows Firewall) until login is built in the database phase.

Import rules:
- Row 1 must contain the column headings. Required columns: Candidate Name, Department, Position, Fresher / Experienced, Contact No., Date of Interview, Expected CTC. Other columns are optional. Heading spelling is flexible ("Mobile", "Dept", "Designation", "Remarks" also work). Unknown columns are ignored.
- Sr. No. and Month & Year in the file are ignored; the portal calculates them. A file exported from this portal can be imported again.
- Contact: 10-digit mobile number (+91 and spaces accepted). Dates are read day first: 25-Oct-2026 or 25/10/2026. Expected CTC is in lakh per annum (`3.5`, `3.5 LPA` and `2,5` all work).
- Blank Interview Status = Scheduled, blank Final Status = Pending, blank Interviewer = Not assigned, blank Source = Not specified.
- If Reference / Source is **Employee Referral**, the column **Referred By (Employee)** must be filled in; otherwise the row is reported. For other sources the column is ignored. Names are matched to existing employees ("anil  pawar" becomes "Anil Pawar"). Files without this column still work, except for Employee Referral rows.
- A row is skipped (and reported) if the same contact number already has an interview on the same date, or if it is repeated inside the file.
- Limits: 5 MB and 2000 rows per file (change `MAX_UPLOAD_MB` / `MAX_IMPORT_ROWS` in `config/settings.py`).
- Text starting with `=`, `+`, `-` or `@` is written to export files with a leading apostrophe so Excel cannot run it as a formula; Import removes the apostrophe again.

### Where saved data lives (until SQL Server)

`data/candidates.json` is created on first use. To start again with fresh demo data (interview dates recalculated from today), run `python tools/reset_demo_data.py`. This deletes everything added or imported during testing, including the choices added with the + button and all uploaded documents. The file is protected against two people saving at the same moment on one running server, but it is meant for testing, not for heavy multi-user use.

## 6. Build plan (one page at a time)

| Step | Page | Status |
|---|---|---|
| 1 | Dashboard | Confirmed |
| 2 | Candidates list (all 15 fields, search, filters, sorting, paging) | Confirmed |
| 3 | Add candidate, Import, Export, Template (CSV / XLSX / XLS), + button, Referred By, **Candidate documents** (details page) | Built, waiting for confirmation |
| 4 | Edit / delete candidate | Planned |
| 5 | Interviews (schedule view) | Planned |
| 6 | Departments and positions | Planned |
| 7 | Reports | Planned |
| 8 | Settings | Planned |
| 9 | Database phase: SQL Server connection | Later |

After you confirm a page, its link in the left menu is switched on (`templates/partials/_sidebar.html`) and we start the next page.

## 7. How to find and edit code

Every code section is wrapped like this:

```
#-------------- Start Code for <what this code does> -----------------
...code...
#-------------- End of the code ------------------------------
```

(CSS uses `/* ... */`, HTML uses `<!-- ... -->`, JavaScript uses `//`.)
Search the file for **"Start Code for"** to list all sections.

Quick guide for common edits:

| I want to... | Edit this |
|---|---|
| Change the first demo candidates | `tracker/dummy_data.py` -> `_RAW_ROWS` (then run `tools/reset_demo_data.py`) |
| Change a field rule (phone, dates, CTC, allowed values) | `tracker/candidate_rules.py` (Add form and Import both follow it) |
| Change when Referred By is required | `REFERRAL_SOURCE` and the "Referred by" block in `clean_candidate()` in `tracker/candidate_rules.py` |
| Change document types or allowed file types | `DOCUMENT_TYPES` / `ALLOWED_TYPES` in `tracker/documents.py` (and the checks in `_looks_like`) |
| Give another dropdown a + button | `OPTION_FIELDS` in `tracker/candidate_rules.py`, then use `partials/_option_field.html` in the form |
| Rename a column in Export / Template | `FILE_COLUMNS` in `tracker/candidate_rules.py` |
| Change a colour | `static/css/themes.css` |
| Change the Dashboard layout | `templates/tracker/dashboard.html` and `static/css/dashboard.css` |
| Change a number or chart calculation | `tracker/services.py` |
| Add a menu item | `templates/partials/_sidebar.html` |
| Add / hide a Candidates column | `LIST_COLUMNS` in `tracker/services.py` and the matching cell in `templates/tracker/candidates.html` |
| Add a Candidates filter | `FILTER_FIELDS` in `tracker/services.py` (dropdown appears automatically) |
| Change rows per page | `PAGE_SIZE` in `tracker/services.py` |

## 8. Moving to SQL Server later

The `DATABASES` block in `config/settings.py` is empty on purpose. In the database phase we will:
1. Install an SQL Server ODBC driver on the server PC and the packages `mssql-django` and `pyodbc` (check version compatibility with Django at that time).
2. Create models for the candidate fields above and replace the functions in `tracker/data_store.py` (`get_candidates`, `add_candidates`, `existing_keys`) with database queries. The dictionary keys stay the same, so pages, Import and Export keep working. `data/candidates.json` can be imported into SQL Server first (or exported with the Export button).
3. Add login / user roles (HR user, HR manager) if required.

## 9. Keeping the changelog

After any change, run:

```
python tools/changelog_add.py Added "Short description"
```

Types: `Added`, `Changed`, `Fixed`, `Removed`. The date and time are filled in automatically.
