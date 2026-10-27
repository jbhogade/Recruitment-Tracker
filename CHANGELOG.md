# CHANGELOG - Recruitment Tracker

Every add / change / fix / removal in this project is recorded here with date and time (newest first).
Types: **Added**, **Changed**, **Fixed**, **Removed**.

Tip: add a line automatically (time is filled in for you):

```
python tools/changelog_add.py Added "Candidates page created"
```

## Entries

| Format | `- **YYYY-MM-DD HH:MM** \| **Type** \| What happened` |
|---|---|

<!-- NEW ENTRIES GO BELOW THIS LINE (newest first) -->
- **2026-10-26 16:30** | **Changed** | tools/reset_demo_data.py also deletes documents.json, uploaded documents, staging and notice files; README, CLAUDE.md updated (privacy note: no login yet)
- **2026-10-26 16:30** | **Changed** | Candidates list: candidate names link to the details page; new Documents column (count, sortable) (candidates.html, services.py)
- **2026-10-26 16:30** | **Added** | tracker/notices.py: one-time messages after uploads (kept in data/notices/, only a token in the address)
- **2026-10-26 16:30** | **Added** | Candidate details page /candidates/<Sr. No.>/ : all fields, documents table with View (PDF / images), Download and Delete (asks first), and Add documents (templates/tracker/candidate_detail.html, static/css/detail.css, tracker/views.py)
- **2026-10-26 16:30** | **Added** | Add candidate form: optional Documents section with several rows (type, name, file) and '+ Add another document' (partials/_document_rows.html, static/js/documents.js); a rejected file never loses the typed candidate data
- **2026-10-26 16:30** | **Added** | Candidate documents: several documents per candidate (CV / Resume, 10th, 12th, Graduation, Post-Graduation, Other); only PDF, images (JPG, PNG, GIF, BMP, WEBP, TIF) and Word (DOC, DOCX); files are checked by content, max 10 MB each (tracker/documents.py, config/settings.py)
- **2026-10-26 10:46** | **Changed** | CLAUDE.md, README.md updated for the Referred By field
- **2026-10-26 10:46** | **Fixed** | Candidates table stretched the whole page sideways instead of scrolling inside its panel (caused by an earlier menu fix); added .content > * { min-width: 0 } in static/css/base.css
- **2026-10-26 10:46** | **Changed** | Demo data: 'Employee Referral' candidates get fake employee names (dummy_data.py); records saved earlier without the field load as blank; Employee Referral is always offered in the Source dropdown (data_store.py)
- **2026-10-26 10:46** | **Added** | Referred By (Employee) column in the Candidates table, search and a new filter, and in Export, Template (with instructions) and Import; Import maps typed names to existing employees and reports Employee Referral rows without a name (services.py, import_export.py, candidates.html)
- **2026-10-26 10:46** | **Added** | Referred By (Employee) field: when Reference / Source = Employee Referral the Add form shows a required 'Referred by (employee)' dropdown with a + button for new names; for other sources it is hidden and saved blank (candidate_form.html, option_adder.js, candidate_rules.py)
- **2026-10-26 10:34** | **Changed** | README.md folder structure now lists CLAUDE.md
- **2026-10-26 10:34** | **Added** | CLAUDE.md project guide: what the project is, stack, status of every step, decisions made, project map, coding conventions and the rule to update it (with CHANGELOG and README) after every change
- **2026-10-26 10:10** | **Changed** | tools/reset_demo_data.py now also removes data/options.json
- **2026-10-26 10:10** | **Changed** | Add candidate form: Education, Department, Position, Source and Interviewer changed from type-in boxes with suggestions to dropdowns; Fresher / Experienced and both Status fields stay fixed lists
- **2026-10-26 10:10** | **Added** | New choices are kept in data/options.json; duplicates in another spelling (BCA / B.C.A.) reuse the existing choice (tracker/data_store.py add_option / option_lists, tracker/candidate_rules.py OPTION_FIELDS)
- **2026-10-26 10:10** | **Added** | Plus (+) button beside Education, Department, Position, Reference / Source and Interviewer on the Add candidate form: type the missing value, press Add, it is saved, added to the dropdown and selected without leaving the page (templates/partials/_option_field.html, static/js/option_adder.js, static/css/forms.css, tracker/views.py option_add, tracker/urls.py)
- **2026-10-25 20:06** | **Fixed** | Duplicate check (same contact + same interview date) compared a text date with a real date and never matched; corrected in tracker/data_store.py before release
- **2026-10-25 20:06** | **Changed** | requirements.txt: added openpyxl, xlrd, xlwt (run pip install -r requirements.txt again); config/settings.py: DATA_DIR, MAX_UPLOAD_MB, MAX_IMPORT_ROWS; sidebar note reworded; README updated
- **2026-10-25 20:06** | **Changed** | Candidates page: 'Add candidate' button enabled; Import, Export and Template buttons added; green message after Add / Import; shared button and message styles moved to base.css
- **2026-10-25 20:06** | **Changed** | Dashboard and Candidates page now read from data_store (saved candidates) instead of the fixed dummy list; Expected CTC shows up to 2 decimals (tracker/services.py)
- **2026-10-25 20:06** | **Added** | tracker/data_store.py: candidates added or imported are saved in data/candidates.json (temporary, until SQL Server); tools/reset_demo_data.py restores fresh demo data; tracker/candidate_rules.py holds the field rules used by Add and Import
- **2026-10-25 20:06** | **Added** | Template button: empty import file in CSV / XLSX / XLS; Excel versions include an Instructions sheet, .xlsx also has drop-down lists
- **2026-10-25 20:06** | **Added** | Export button: CSV / XLSX / XLS download of all candidates matching the current search, filters and sorting; Excel formula protection for text cells (tracker/import_export.py, file_io.py)
- **2026-10-25 20:06** | **Added** | Import button and page: upload CSV / XLSX / XLS, file is checked first (preview + list of problem rows with row numbers), rows are saved only after pressing Import; duplicates and repeated rows skipped (tracker/import_export.py, candidates_import.html)
- **2026-10-25 20:06** | **Added** | Add candidate form (templates/tracker/candidate_form.html, static/css/forms.css): all Excel fields, type-ahead lists from saved data, errors shown beside each field, duplicate contact + date blocked
- **2026-10-25 14:27** | **Changed** | Candidates page shows the 'Add candidate' button disabled; Add / Edit form is planned as the next step
- **2026-10-25 14:27** | **Changed** | Dashboard: pipeline legend items now open the Candidates page filtered by that Final Status; 'View all candidates' link added to Recent candidates (dashboard.html, dashboard.css, base.css)
- **2026-10-25 14:27** | **Changed** | Left menu: Candidates link switched on (templates/partials/_sidebar.html)
- **2026-10-25 14:27** | **Added** | Candidates page (Build plan step 2): all 15 Excel columns, search, 7 dropdown filters, click-to-sort headers, 15 rows per page, fixed Sr. No. and Name columns while scrolling (templates/tracker/candidates.html, static/css/candidates.css, static/js/candidates.js, tracker/services.py, views.py, urls.py)
- **2026-10-25 14:27** | **Changed** | ALLOWED_HOSTS now auto-detects this PC's name and IP addresses, so the portal opens on any system without editing an IP (config/settings.py); extra hosts via RT_ALLOWED_HOSTS
- **2026-10-25 14:27** | **Changed** | Dashboard page confirmed after testing; Build plan step 1 closed
- **2026-10-25 12:58** | **Fixed** | Dashboard: "Employee Referral" label was cut off in the "By reference / source" list; label column widened (static/css/dashboard.css)
- **2026-10-25 12:58** | **Fixed** | Sidebar: a help comment contained a Django template tag, which crashed the page; comment reworded (templates/partials/_sidebar.html)
- **2026-10-25 12:58** | **Added** | v1.0 Step 1: Dashboard page (hiring pipeline, key numbers, upcoming interviews, interviews per month, department / source / fresher-experienced breakdown, recent candidates)
- **2026-10-25 12:58** | **Added** | 5 colour themes: Dark (default), Grey, Lite, Blue, Emerald; choice is remembered in the browser (static/css/themes.css, static/js/theme.js)
- **2026-10-25 12:58** | **Added** | 34 dummy candidate records based on the HR Excel fields (tracker/dummy_data.py); no database connected
- **2026-10-25 12:58** | **Added** | Project created: Django 5.2 project skeleton (config/ and tracker/ folders), README.md, CHANGELOG.md, requirements.txt, run_server.bat, tools/changelog_add.py
