#!/usr/bin/env python
# ==========================================================================
# File : manage.py
# What : Django's command-line helper (run server, check project, etc.).
#        You normally never need to edit this file.
# ==========================================================================

#-------------- Start Code for Django command-line entry point -----------------
import os
import sys


def main():
    """Point Django at our settings module and run the command typed by the user."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Activate the virtual environment and run: "
            "pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
#-------------- End of the code ------------------------------
