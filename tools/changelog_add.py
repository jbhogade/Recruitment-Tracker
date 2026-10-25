# ==========================================================================
# File : tools/changelog_add.py
# What : Adds a new entry (with today's date and current time) at the top
#        of CHANGELOG.md, so you never have to type the timestamp.
# Use  : python tools/changelog_add.py Added "Candidates page created"
#        Type must be one of: Added, Changed, Fixed, Removed
# ==========================================================================

#-------------- Start Code for Changelog helper -----------------
import sys
from datetime import datetime
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
MARKER = "<!-- NEW ENTRIES GO BELOW THIS LINE (newest first) -->"
TYPES = ("Added", "Changed", "Fixed", "Removed")


def main():
    # Expect exactly: <Type> "<description>"
    if len(sys.argv) < 3 or sys.argv[1].capitalize() not in TYPES:
        print('Usage: python tools/changelog_add.py <Added|Changed|Fixed|Removed> "what happened"')
        sys.exit(1)

    entry_type = sys.argv[1].capitalize()
    text = " ".join(sys.argv[2:])
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")   # local PC date and time

    content = CHANGELOG.read_text(encoding="utf-8")
    if MARKER not in content:
        print("Marker line not found in CHANGELOG.md - entry not added.")
        sys.exit(1)

    new_line = f"- **{stamp}** | **{entry_type}** | {text}"
    CHANGELOG.write_text(content.replace(MARKER, MARKER + "\n" + new_line, 1), encoding="utf-8")
    print("Added to CHANGELOG.md:", new_line)


if __name__ == "__main__":
    main()
#-------------- End of the code ------------------------------
