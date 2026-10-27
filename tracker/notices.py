# ==========================================================================
# File : tracker/notices.py
# What : One-time messages shown after a redirect (for example "2 documents
#        saved, 1 could not be saved because ..."). The messages are kept in a
#        small temporary file and only a random token travels in the web
#        address, so nobody can type their own message into a page.
# ==========================================================================

#-------------- Start Code for One-time notices -----------------
import json
import re
import secrets
import time

from django.conf import settings

_TOKEN = re.compile(r"[0-9a-f]{32}")


def _folder():
    folder = settings.DATA_DIR / "notices"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def stash(good=None, bad=None):
    """Keep messages and return a token for the web address.
    good = list of success messages, bad = list of problem messages."""
    folder = _folder()
    for old in folder.glob("*.json"):                       # tidy up files older than 1 day
        if time.time() - old.stat().st_mtime > 86400:
            old.unlink(missing_ok=True)
    token = secrets.token_hex(16)
    (folder / f"{token}.json").write_text(json.dumps({"good": good or [], "bad": bad or []}), encoding="utf-8")
    return token


def take(token):
    """Read the messages for a token ONCE (the file is deleted). Returns (good, bad)."""
    if not _TOKEN.fullmatch(token or ""):
        return [], []
    path = _folder() / f"{token}.json"
    if not path.exists():
        return [], []
    data = json.loads(path.read_text(encoding="utf-8"))
    path.unlink(missing_ok=True)
    return data.get("good", []), data.get("bad", [])
#-------------- End of the code ------------------------------
