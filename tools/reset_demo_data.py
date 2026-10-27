# ==========================================================================
# File : tools/reset_demo_data.py
# What : Deletes everything saved while testing, so the portal creates fresh
#        demo data (interview dates re-calculated from today) on the next page load:
#          data/candidates.json, data/options.json (choices added with +),
#          data/documents.json and the uploaded files in data/documents/
#        WARNING: all candidates, dropdown choices and DOCUMENTS added or
#        imported during testing are lost.
# Use  : python tools/reset_demo_data.py
# ==========================================================================

#-------------- Start Code for Reset demo data -----------------
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FILES = [DATA_DIR / "candidates.json", DATA_DIR / "options.json", DATA_DIR / "documents.json"]
FOLDERS = [DATA_DIR / "documents", DATA_DIR / "import_staging", DATA_DIR / "notices"]

existing = [p for p in FILES + FOLDERS if p.exists()]
if existing:
    answer = input("This deletes ALL saved candidates, dropdown choices and uploaded documents "
                   "and restores demo data. Type YES to continue: ")
    if answer.strip() == "YES":
        for path in existing:
            shutil.rmtree(path) if path.is_dir() else path.unlink()
        print("Done. Demo data will be created again when you open the portal.")
    else:
        print("Cancelled. Nothing was changed.")
else:
    print("No saved data found. Nothing to reset.")
#-------------- End of the code ------------------------------
