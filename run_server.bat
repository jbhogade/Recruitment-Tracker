@echo off
REM ==========================================================================
REM File : run_server.bat
REM What : One-click start for Recruitment Tracker on Windows.
REM        First run creates the virtual environment and installs Django.
REM ==========================================================================

REM -------------- Start Code for Starting the portal -----------------
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo.
echo Portal is starting. Open  http://127.0.0.1:8000  in your browser.
echo Press CTRL+C in this window to stop it.
echo.
python manage.py runserver
REM -------------- End of the code ------------------------------
