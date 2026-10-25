# ==========================================================================
# File : tracker/context_processors.py
# What : Values added automatically to EVERY page (theme list, app name).
# ==========================================================================

#-------------- Start Code for Theme list (add / rename themes here) -----------------
# key    = the value stored in the browser and used in static/css/themes.css
# label  = name shown as a tooltip on the theme switcher
# swatch = colour of the little circle in the switcher
# To add a new theme: add a line here AND a matching [data-theme="key"]
# block in static/css/themes.css.
THEMES = [
    {"key": "dark",    "label": "Dark",    "swatch": "#1c2128"},
    {"key": "grey",    "label": "Grey",    "swatch": "#3a3d44"},
    {"key": "lite",    "label": "Lite",    "swatch": "#f3f4f7"},
    {"key": "blue",    "label": "Blue",    "swatch": "#1b4b82"},
    {"key": "emerald", "label": "Emerald", "swatch": "#1d4a3c"},
]
#-------------- End of the code ------------------------------


#-------------- Start Code for Context processor function -----------------
def themes(request):
    """Make the theme list and app name available in every template."""
    return {"THEMES": THEMES, "APP_NAME": "Recruitment Tracker"}
#-------------- End of the code ------------------------------
