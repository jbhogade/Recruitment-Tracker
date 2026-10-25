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
- **2026-10-25 12:58** | **Fixed** | Dashboard: "Employee Referral" label was cut off in the "By reference / source" list; label column widened (static/css/dashboard.css)
- **2026-10-25 12:58** | **Fixed** | Sidebar: a help comment contained a Django template tag, which crashed the page; comment reworded (templates/partials/_sidebar.html)
- **2026-10-25 12:58** | **Added** | v1.0 Step 1: Dashboard page (hiring pipeline, key numbers, upcoming interviews, interviews per month, department / source / fresher-experienced breakdown, recent candidates)
- **2026-10-25 12:58** | **Added** | 5 colour themes: Dark (default), Grey, Lite, Blue, Emerald; choice is remembered in the browser (static/css/themes.css, static/js/theme.js)
- **2026-10-25 12:58** | **Added** | 34 dummy candidate records based on the HR Excel fields (tracker/dummy_data.py); no database connected
- **2026-10-25 12:58** | **Added** | Project created: Django 5.2 project skeleton (config/ and tracker/ folders), README.md, CHANGELOG.md, requirements.txt, run_server.bat, tools/changelog_add.py
