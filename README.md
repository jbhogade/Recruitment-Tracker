# Recruitment Tracker (v1.0)

A Django web portal for the HR team to record and track recruitment: candidates, interviews, statuses and expected CTC.

**Current phase: web pages only. There is no database yet.** All data comes from fake (dummy) records in `tracker/dummy_data.py`. SQL Server will be connected in a later phase.

## 1. Prerequisites

| Need | Details |
|---|---|
| Python | 3.10 or newer (3.12 recommended). Download from python.org and tick **"Add python.exe to PATH"** during install. |
| pip | Comes with Python. |
| Web browser | Any modern Chrome / Edge / Firefox. |
| Code editor (optional) | VS Code with the "Python" and "Django" extensions. |

Check Python is ready: open Command Prompt and run `python --version`.

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
1. Add this PC's IP address to `ALLOWED_HOSTS` in `config/settings.py`.
2. Start with `python manage.py runserver 0.0.0.0:8000`.
3. Others open `http://<this-PC-IP>:8000`. (Windows Firewall may ask for permission.)

## 3. Folder structure

```
Recruitment_Tracker_v1-0/
|-- manage.py              Django command tool (run server, checks)
|-- run_server.bat         One-click start for Windows
|-- requirements.txt       Python packages needed
|-- README.md              This file
|-- CHANGELOG.md           Every add / change / fix / removal with date and time
|-- config/                Project-wide settings
|   |-- settings.py        Main configuration (database block is empty on purpose)
|   |-- urls.py            Top-level address list
|-- tracker/               The Recruitment Tracker app
|   |-- dummy_data.py      FAKE candidate records (HR Excel fields)
|   |-- services.py        Dashboard calculations (counts, %, trends)
|   |-- views.py           One function per page
|   |-- urls.py            Page addresses
|   |-- context_processors.py   Theme list shared by all pages
|-- templates/             HTML pages
|   |-- base.html          Common page frame (menu + top bar)
|   |-- partials/          Reusable pieces (_sidebar.html, _topbar.html)
|   |-- tracker/           One HTML file per page (dashboard.html ...)
|-- static/
|   |-- css/               themes.css (colours), base.css (shared), dashboard.css (page)
|   |-- js/                theme.js (theme switcher)
|-- tools/
    |-- changelog_add.py   Adds a timestamped line to CHANGELOG.md
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

Allowed values used for now (to be confirmed with HR):
- **Interview Status:** Scheduled, Rescheduled, Completed, No Show
- **Final Status:** Pending, On Hold, Selected, Joined, Rejected
- **Expected CTC:** stored as lakh per annum (LPA), for example `3.6`

## 6. Build plan (one page at a time)

| Step | Page | Status |
|---|---|---|
| 1 | Dashboard | Built, waiting for confirmation |
| 2 | Candidates list (all 15 fields, search, filters) | Planned |
| 3 | Add / Edit candidate form | Planned |
| 4 | Interviews (schedule view) | Planned |
| 5 | Departments and positions | Planned |
| 6 | Reports / export | Planned |
| 7 | Settings | Planned |
| 8 | Database phase: SQL Server connection | Later |

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
| Change dummy candidates | `tracker/dummy_data.py` -> `_RAW_ROWS` |
| Change a colour | `static/css/themes.css` |
| Change the Dashboard layout | `templates/tracker/dashboard.html` and `static/css/dashboard.css` |
| Change a number or chart calculation | `tracker/services.py` |
| Add a menu item | `templates/partials/_sidebar.html` |

## 8. Moving to SQL Server later

The `DATABASES` block in `config/settings.py` is empty on purpose. In the database phase we will:
1. Install an SQL Server ODBC driver on the server PC and the packages `mssql-django` and `pyodbc` (check version compatibility with Django at that time).
2. Create models for the candidate fields above and replace `get_candidates()` in `tracker/dummy_data.py` with database queries. The dictionary keys stay the same, so pages keep working.
3. Add login / user roles (HR user, HR manager) if required.

## 9. Keeping the changelog

After any change, run:

```
python tools/changelog_add.py Added "Short description"
```

Types: `Added`, `Changed`, `Fixed`, `Removed`. The date and time are filled in automatically.
