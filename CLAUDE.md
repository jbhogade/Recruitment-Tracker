# CLAUDE.md - Recruitment Tracker

Project guide for Claude (and any developer). Read this first.
**Keep this file up to date after EVERY update** (see "Rules for working on this project" at the bottom).

**Last updated:** 2026-10-26 (after: recorded the planned document folder layout for the SQL Server phase; no code changed)

---

## 1. What this project is

A **local web portal for the company HR team** to record and track recruitment: candidates, interviews, statuses and expected CTC. It replaces the Excel sheet the HR team uses today.

- Owner / developer: Jai (IT administration / development).
- Users: HR team, opening the portal in a browser on the office network.
- Base folder: `D:\Recruitment_Tracker_v1-0` (may change later; nothing in the code depends on the folder path).
- Language of the UI: English. Dates are day-first (India). Money is Expected CTC in **lakh per annum (LPA)**.

## 2. Stack

| Part | Choice |
|---|---|
| Language | Python 3.12 (3.10 or newer works) |
| Framework | Django 5.2 LTS (`Django>=5.2,<6.0`) |
| Database | **None yet.** `DATABASES = {}`. Candidates are kept in `data/candidates.json`, extra dropdown choices in `data/options.json` (temporary storage) |
| Future database | **SQL Server** (planned: `mssql-django` + `pyodbc`, ODBC Driver 18) |
| Files | `openpyxl` (.xlsx read/write), `xlrd` (.xls read), `xlwt` (.xls write), `csv` (standard library) |
| Front end | Plain HTML templates + hand-written CSS + small vanilla JavaScript. **No CDN, no external fonts, no chart or UI libraries** (fast, works offline) |
| Platform | Windows PCs; started with `run_server.bat` or `python manage.py runserver 0.0.0.0:<port>` (user tests with port 8012) |

## 3. Status: is it complete?

**No. Phase 1 (web pages only, no database) is in progress.** Pages are built one at a time; the next page starts only after the user confirms the previous one.

| Step | Page / feature | Status |
|---|---|---|
| 1 | Dashboard | Confirmed by user |
| 2 | Candidates list (15 Excel columns + Referred By, search, 8 filters, sorting, paging) | Confirmed by user |
| 3 | Add candidate form, Import, Export, Template (CSV / XLSX / XLS), (+) button for dropdown choices, Referred By (Employee) for Employee Referral, **candidate documents** (PDF / images / Word) with a Candidate details page | **Built and tested by Claude, waiting for user confirmation** |
| 4 | Edit / delete candidate | Planned (next) |
| 5 | Interviews (schedule view) | Planned |
| 6 | Departments and positions | Planned |
| 7 | Reports | Planned |
| 8 | Settings | Planned |
| 9 | Database phase: SQL Server, login / user roles | Later |

Sidebar menu: Dashboard and Candidates are live. Interviews, Departments, Reports, Settings show as "Planned" (switched on in `templates/partials/_sidebar.html` after the page is confirmed).

**Known limits / not done yet**
- **No login, and documents hold personal data** (CVs, certificates). Anyone who can open the portal can open every document. Tell the user to restrict network access until login exists. Documents are plain files in `data/documents/` (not encrypted); the user must back up the `data` folder.
- The Candidate details page is read-only (no edit yet). When **delete candidate** is built it MUST also delete that candidate's documents (`documents.py` has no cascade yet).
- Import / Export do not carry documents.
- TIFF images can be stored and downloaded but browsers cannot display them (no View button). HEIC (iPhone photos) is not allowed.
- No edit or delete of a candidate (step 4). Until it exists, demo "Employee Referral" candidates saved before the Referred By field existed show "-" as the employee; `python tools/reset_demo_data.py` recreates demo data with employee names (and deletes test data).
- No login or user roles. Anyone who can open the address can change data.
- Storage is a JSON file: fine for testing and a few users, not for heavy multi-user use or multiple server processes.
- Only the Windows development setup was considered; the code was tested on Linux with Django's test client and a headless browser, not yet reported back from the user's PC for steps after 2.
- Office / location (Solapur, Pune, Mumbai HO, Virar) is not a field. It may be worth adding later (not requested yet).

## 4. Decisions made (and why)

**Scope and process**
- Build **page by page**; confirm each page before the next (avoids duplicates and rework). After confirmation, link the page in the sidebar and update Dashboard links.
- **Phase 1 = no database connection.** Dummy data first, SQL Server later.
- Start from the HR team's current **Excel fields**: Sr. No., Candidate Name, Education, Department, Position, Fresher / Experienced, Contact No., Date of Interview, Interview Status, Interviewer Name, Reference/Source, Month & Year, Remark, Final Status, Expected CTC. New fields only after discussion.
- **Added field (user request): `referred_by` = "Referred By (Employee)"**, placed right after Reference / Source in the table, Export, Template and Import.

**Design**
- Dark / grey look to reduce load and eye strain, with good visuals. **5 themes:** Dark (default), Grey, Lite (light), Blue, Emerald. Chosen theme is remembered in the browser (`localStorage`). Colours live only in `static/css/themes.css`.
- Speed first: system font stack, no CDN, charts are plain CSS.
- Sidebar navigation, pipeline bar as the Dashboard's main element, status colours consistent everywhere (chips use the status colour variables).

**Data and rules** (all in `tracker/candidate_rules.py`; the Add form and Import use the same function `clean_candidate`)
- Interview Status: `Scheduled, Rescheduled, Completed, No Show` (blank = Scheduled).
- Final Status: `Pending, On Hold, Selected, Joined, Rejected` (blank = Pending).
- Fresher / Experienced: `Fresher, Experienced`.
- Contact: 10-digit Indian mobile starting 6-9, stored as `98765 43210`; `+91`, spaces, dashes accepted.
- Dates read **day-first** (25-Oct-2026, 25/10/2026, also 2026-10-25). Expected CTC: number in LPA (`3.5`, `3.5 LPA`, `2,5` accepted).
- Blank Interviewer = "Not assigned", blank Source = "Not specified".
- **Referral rule:** when Source = `Employee Referral` (any spelling of it is stored as exactly that), `referred_by` is **required** (dropdown with (+) on the Add form, shown only for that source; required column value in Import). For any other source it is cleared / ignored. Chosen so HR always knows which employee referred the candidate; the "required" part is easy to relax in `clean_candidate()` if HR wants it optional.
- **Duplicate rule:** same contact number + same interview date = duplicate (blocked on Add, skipped on Import). Same person on a different date is allowed (re-interview).
- Sr. No. is automatic (highest + 1). Month & Year is calculated from the interview date. Both are ignored in import files.

**Import / Export / Template**
- Every one of these supports **CSV, .xlsx and .xls** (user requirement). File type is detected from the file's first bytes, not only the extension.
- Import is **two steps**: check + preview (nothing saved), then confirm. Problem rows are listed with row number and reason; valid rows can still be imported. Checked rows wait in `data/import_staging/` (deleted after 24 h).
- Export contains **all rows matching the current search / filters / sorting** (not only the visible page).
- Template: headings only; Excel versions add an "Instructions" sheet; .xlsx also has drop-downs.
- Cells starting with `= + - @` are exported with a leading apostrophe (prevents Excel formula injection); Import removes it.
- Limits: 5 MB, 2000 rows per import (`config/settings.py`).

**Dropdown (+) button** (user requirement)
- Education, Department, Position, Reference / Source, Interviewer and Referred by (employee) are dropdowns with a (+) button that adds a missing value on the spot (saved, selected, no page change). Duplicates in another spelling (BCA / B.C.A.) reuse the existing value.
- Fresher/Experienced, Interview Status and Final Status are deliberately **fixed** (Dashboard colours and counts depend on them). Adding a status needs Dashboard work too.

**Candidate documents** (user requirement: multiple documents per candidate; only PDF, images, MS Word)
- Types: CV / Resume, 10th, 12th, Graduation, Post-Graduation, Other (list in `tracker/documents.py` -> `DOCUMENT_TYPES`). Several documents of the same type are allowed.
- Allowed: `.pdf .jpg .jpeg .png .gif .bmp .webp .tif .tiff .doc .docx`. The **content** is checked (magic bytes; `.docx` must contain `word/document.xml` and no macros; `.doc` must be a real Word file or RTF), not just the extension. SVG, `.docm`, executables and everything else are refused.
- Limits: 10 MB per file, 10 files per upload, 30 per candidate (`config/settings.py`).
- Storage: `data/documents/<6-digit Sr. No.>/<random id>.<ext>` + list in `data/documents.json`; document ids are random hex and a document is only served through its own candidate's URL (wrong candidate / bad id = 404). PDFs and images open in the browser (`inline`), Word and TIFF are downloads; `X-Content-Type-Options: nosniff`.
- Where: optional "Documents" section on the Add form (rows named `doc_type_<n>`, `doc_title_<n>`, `doc_file_<n>`; candidate data is saved first, so a rejected file never loses typed data), and the **Candidate details** page (`/candidates/<Sr. No.>/`) to view, download, delete and add more. Candidate names in the list link to it; the list has a Documents column (count).
- Messages after redirects (saved / refused files) are one-time notices kept in `data/notices/` (token in the address), not text typed in the address.
- Delete asks for confirmation in the browser and needs POST + CSRF token.

**Network**
- `ALLOWED_HOSTS` is detected automatically at start-up (localhost, PC name, all IPv4 addresses of the PC) so the portal opens on any PC without editing; extra names via the `RT_ALLOWED_HOSTS` environment variable. `"*"` is only for quick tests with dummy data.

**Decided for the SQL Server phase (user instruction - NOT built yet, do not build in Phase 1)**
- When candidates move to SQL Server, documents must be stored in **folders named with the candidate's name**, inside the project, in this layout (user's wording: `Project -> Candidate Documents -> [dd-mmmm-yyyy_hh-mm-ss]`):
  - Base folder: `<project>/Candidate Documents/`
  - Candidate folder: named with the **Candidate Name**.
  - Timestamp folder: named **`dd-mmmm-yyyy_hh-mm-ss`** (day, full month name, year, 24-hour time), for example `26-October-2026_14-35-20`.
  - Claude's reading of the layout (use this unless the user corrects it): `Candidate Documents/<Candidate Name>/<dd-mmmm-yyyy_hh-mm-ss>/<document files>`.
- **Confirm with the user before building** (not asked yet, the user said only to note it): (1) what the timestamp is: when the candidate was created, or each upload batch; (2) whether the timestamp folder sits inside the candidate-name folder (as read above) or the other way round; (3) how to handle two candidates with the same name (the Sr. No. / database id may need to be added to the folder name); (4) moving the existing files from the Phase 1 layout `data/documents/<Sr. No.>/` (and updating `data/documents.json` entries or the new SQL table); (5) invalid Windows folder characters and long names must be cleaned (`\ / : * ? " < > |`), and the base path may change later like the project folder.
- Today (Phase 1) the temporary layout is `data/documents/<6-digit Sr. No.>/<random id>.<ext>`; the file list is in `data/documents.json`. Only `tracker/documents.py` knows these paths, so the new layout should be a change in that file plus the SQL table.

## 5. Project map

```
Recruitment_Tracker_v1-0/
|-- CLAUDE.md, README.md, CHANGELOG.md   documentation (keep all three current)
|-- manage.py, requirements.txt, run_server.bat
|-- config/        settings.py (DATA_DIR, import limits, ALLOWED_HOSTS auto-detect), urls.py
|-- tracker/       the app
|   |-- views.py            one function per page / download / (+) endpoint
|   |-- urls.py             page addresses
|   |-- services.py         Dashboard maths; Candidates page search / filter / sort / paging
|   |-- candidate_rules.py  FILE_COLUMNS (Excel order + Referred By), heading aliases, OPTION_FIELDS, REFERRAL_SOURCE, clean_candidate()
|   |-- data_store.py       temporary storage (JSON) + dropdown options  <-- replaced by SQL Server later
|   |-- dummy_data.py       fake candidates that create the first demo data
|   |-- file_io.py          read / write CSV, XLSX, XLS (no candidate knowledge)
|   |-- import_export.py    export, template, import checking, staging
|   |-- documents.py        candidate documents: types, allowed files, content checks, storage
|   |-- notices.py          one-time messages after redirects
|   |-- context_processors.py   theme list for every page
|-- templates/     base.html, partials/ (_sidebar, _topbar, _option_field, _document_rows, _document_row), tracker/ (dashboard, candidates, candidate_form, candidates_import, candidate_detail)
|-- static/css/    themes.css (colours), base.css (shared), dashboard.css, candidates.css, forms.css, detail.css
|-- static/js/     theme.js, candidates.js (filters + menus), option_adder.js (+ button, Referred By), documents.js (document rows, delete confirm)
|-- tools/         changelog_add.py (timestamped changelog line), reset_demo_data.py
|-- data/          created at run time (candidates.json, options.json, documents.json, documents/<Sr. No.>/, import_staging/, notices/); never shipped in zips
```

**When SQL Server is added:** replace the functions in `tracker/data_store.py` (`get_candidates`, `add_candidates`, `add_candidate`, `existing_keys`, `option_lists`, `add_option`) with database code. Keep the dictionary keys (`sr_no, name, education, department, position, experience, contact, interview_date, interview_status, interviewer, source, month_year, remark, final_status, expected_ctc`) so pages, Import and Export keep working. Add models, migrations, login / roles then.

## 6. Coding conventions (user requirement)

- **Comments everywhere.** Every code section is wrapped in start / end blocks so the user can find and edit it:
  - Python: `#-------------- Start Code for <what it does> -----------------` ... `#-------------- End of the code ------------------------------`
  - CSS: `/*-------------- Start Code for ... -----------------*/` ... `/*-------------- End of the code ------------------------------*/`
  - HTML: `<!-- ------------- Start Code for ... ----------------- -->` ... `<!-- ------------- End of the code ------------------------------ -->`
  - JavaScript: `//-------------- Start Code for ... -----------------` ... `//-------------- End of the code ------------------------------`
  - Each file also starts with a header comment: file name, what it is for.
- Wide tables must scroll inside their panel: keep `.content > * { min-width: 0; }` in `base.css` (removing it makes the page scroll sideways).
- Pages with file inputs need `enctype="multipart/form-data"`; check uploaded files by content in `documents.check_file`, never trust the extension alone.
- Never write Django template tags (`{% ... %}`, `{{ ... }}`) inside HTML comments; Django still runs them.
- Accessible, responsive pages (labels, focus styles, keyboard use, small-screen layout).
- Colours only through the CSS variables in `themes.css`; every theme must stay readable.

## 7. How to run and test

```
cd /d D:\Recruitment_Tracker_v1-0
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8012
```
(or double-click `run_server.bat`). Open `http://<this-PC-IP>:8012`.
Checks used so far: `python manage.py check`, Django test client scripts covering all pages, filters, sort, paging, export / template / import in all 3 formats, duplicates, validation and the (+) endpoint, plus headless-browser runs of the UI. Reset test data with `python tools/reset_demo_data.py`.

## 8. Rules for working on this project

1. **After every update, update this file** (status table, decisions, project map, limits, "Last updated"), **and** `CHANGELOG.md` (use `python tools/changelog_add.py <Added|Changed|Fixed|Removed> "text"`, it adds date and time) **and** `README.md` if usage changed.
2. Work one page / feature at a time; do not start the next until the user confirms.
3. Test before delivering (run the app, exercise the new feature, check screenshots). Say plainly what was tested and what was not, and say so up front if something is not ready.
4. Deliver all download links together at the end: an **update zip** (only changed files, same folder structure) and the **full project zip**, plus README / CHANGELOG (and this file when it changed). Mention any new `pip install` step.
5. Keep answers short; the user prefers concise communication.
6. Keep the comment-block convention in section 6 for all new code, including pages and CSS.
7. Do not add things the user did not ask for without saying so (for example new fields or statuses); ask first.
