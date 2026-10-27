# ==========================================================================
# File : tracker/documents.py
# What : Candidate documents (CV, 10th / 12th / graduation certificates ...).
#        - which file types are allowed and how they are checked
#        - where the files and their list are stored
# Allowed : PDF, images (JPG, PNG, GIF, BMP, WEBP, TIF) and MS Word (DOC, DOCX).
# Storage : files  -> data/documents/<Sr. No.>/<random name>.<ext>
#           list   -> data/documents.json
#           (Later: SQL Server table for the list; files can stay on disk or
#            move to a network share.)
# ==========================================================================

#-------------- Start Code for Imports -----------------
import json
import os
import re
import secrets
import threading
import zipfile
from datetime import datetime

from django.conf import settings

_LOCK = threading.RLock()
#-------------- End of the code ------------------------------


#-------------- Start Code for Document types and allowed file types -----------------
# Choices shown in the "Document type" dropdown. Change / add names here.
DOCUMENT_TYPES = [
    "CV / Resume",
    "10th Certificate",
    "12th Certificate",
    "Graduation Certificate",
    "Post-Graduation Certificate",
    "Other",
]

# extension -> (group, content type sent to the browser, can be shown inside the browser?)
ALLOWED_TYPES = {
    ".pdf":  ("PDF",   "application/pdf", True),
    ".jpg":  ("Image", "image/jpeg", True),
    ".jpeg": ("Image", "image/jpeg", True),
    ".png":  ("Image", "image/png", True),
    ".gif":  ("Image", "image/gif", True),
    ".bmp":  ("Image", "image/bmp", True),
    ".webp": ("Image", "image/webp", True),
    ".tif":  ("Image", "image/tiff", False),     # browsers cannot show TIFF: download only
    ".tiff": ("Image", "image/tiff", False),
    ".doc":  ("Word",  "application/msword", False),
    ".docx": ("Word",  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False),
}
ACCEPT_ATTRIBUTE = ",".join(ALLOWED_TYPES)                    # for <input type="file" accept="...">
ALLOWED_TEXT = "PDF, images (JPG, PNG, GIF, BMP, WEBP, TIF) and Word (DOC, DOCX)"

_OLE_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"             # old Office files (.doc)
_WORD_STREAM = "WordDocument".encode("utf-16-le")             # present inside real .doc files
#-------------- End of the code ------------------------------


#-------------- Start Code for Checking an uploaded file -----------------
def _looks_like(ext, uploaded):
    """True when the CONTENT of the file really is what its extension says.
    (A program renamed to .pdf is refused.)"""
    uploaded.seek(0)
    head = uploaded.read(2048)
    if ext == ".pdf":
        return b"%PDF-" in head[:1024]
    if ext in (".jpg", ".jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == ".gif":
        return head[:6] in (b"GIF87a", b"GIF89a")
    if ext == ".bmp":
        return head[:2] == b"BM"
    if ext == ".webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext in (".tif", ".tiff"):
        return head[:4] in (b"II*\x00", b"MM\x00*")
    if ext == ".docx":
        uploaded.seek(0)
        try:
            names = zipfile.ZipFile(uploaded).namelist()
        except zipfile.BadZipFile:
            return False
        # a real Word file; files with macros (vbaProject.bin) are refused
        return "word/document.xml" in names and "word/vbaProject.bin" not in names
    if ext == ".doc":
        if head.startswith(b"{\\rtf"):                         # Word saved as RTF
            return True
        if not head.startswith(_OLE_HEADER):
            return False
        uploaded.seek(0)
        return _WORD_STREAM in uploaded.read()                 # excludes Excel / PowerPoint files
    return False


def check_file(uploaded):
    """Check one uploaded file. Returns (extension, error text). error text is '' when the file is fine."""
    name = os.path.basename(uploaded.name or "")
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_TYPES:
        return ext, f"\u201c{name}\u201d is not allowed. Only {ALLOWED_TEXT} files can be added."
    if uploaded.size == 0:
        return ext, f"\u201c{name}\u201d is empty."
    if uploaded.size > settings.MAX_DOCUMENT_MB * 1024 * 1024:
        return ext, f"\u201c{name}\u201d is larger than {settings.MAX_DOCUMENT_MB} MB."
    if not _looks_like(ext, uploaded):
        return ext, f"\u201c{name}\u201d is not a real {ext[1:].upper()} file (the content does not match its name)."
    uploaded.seek(0)
    return ext, ""
#-------------- End of the code ------------------------------


#-------------- Start Code for Reading and writing the document list -----------------
def _list_file():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return settings.DATA_DIR / "documents.json"


def _read_all():
    path = _list_file()
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return []


def _write_all(items):
    path = _list_file()
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(items, handle, ensure_ascii=False, indent=1)
    os.replace(temp, path)


def _folder(sr_no):
    folder = settings.DATA_DIR / "documents" / f"{int(sr_no):06d}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _clean_name(name):
    """File name for display / download: no folders, no odd characters, not too long."""
    name = os.path.basename(str(name).replace("\\", "/"))
    name = re.sub(r"[\x00-\x1f<>:\"|?*]", "", name).strip() or "document"
    stem, ext = os.path.splitext(name)
    return stem[:100] + ext
#-------------- End of the code ------------------------------


#-------------- Start Code for Public functions used by the pages -----------------
def human_size(size):
    """123456 -> '120.6 KB'"""
    if size < 1024:
        return f"{size} bytes"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def list_documents(sr_no):
    """Documents of one candidate, ordered by type (as in DOCUMENT_TYPES) then by upload time."""
    with _LOCK:
        items = [i for i in _read_all() if i["sr_no"] == int(sr_no)]
    order = {name: n for n, name in enumerate(DOCUMENT_TYPES)}
    items.sort(key=lambda i: (order.get(i["doc_type"], 99), i["uploaded_at"]))
    for item in items:
        group, _, inline = ALLOWED_TYPES.get(item["ext"], ("File", "application/octet-stream", False))
        item.update({"group": group, "can_view": inline, "size_text": human_size(item["size"]),
                     "uploaded_text": datetime.fromisoformat(item["uploaded_at"]).strftime("%d %b %Y, %H:%M")})
    return items


def counts_by_candidate():
    """{sr_no: number of documents} for the Candidates list."""
    counts = {}
    with _LOCK:
        for item in _read_all():
            counts[item["sr_no"]] = counts.get(item["sr_no"], 0) + 1
    return counts


def add_document(sr_no, doc_type, title, uploaded):
    """Save one checked file for a candidate and return its record.
    Call check_file() first. Raises ValueError when the candidate already has too many documents."""
    ext = os.path.splitext(uploaded.name or "")[1].lower()
    original = _clean_name(uploaded.name)
    title = re.sub(r"\s+", " ", title or "").strip()[:80] or os.path.splitext(original)[0]
    if doc_type not in DOCUMENT_TYPES:
        doc_type = "Other"

    with _LOCK:
        items = _read_all()
        if sum(1 for i in items if i["sr_no"] == int(sr_no)) >= settings.MAX_DOCUMENTS_PER_CANDIDATE:
            raise ValueError(f"A candidate can have at most {settings.MAX_DOCUMENTS_PER_CANDIDATE} documents.")
        doc_id = secrets.token_hex(8)
        stored = f"{doc_id}{ext}"
        with open(_folder(sr_no) / stored, "wb") as out:
            uploaded.seek(0)
            for chunk in uploaded.chunks():
                out.write(chunk)
        record = {
            "id": doc_id, "sr_no": int(sr_no), "doc_type": doc_type, "title": title,
            "original_name": original, "stored_name": stored, "ext": ext,
            "size": uploaded.size, "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        }
        items.append(record)
        _write_all(items)
    return record


_ID = re.compile(r"[0-9a-f]{16}")


def get_document(sr_no, doc_id):
    """One document record of this candidate (None if it does not exist or belongs to someone else)."""
    if not _ID.fullmatch(doc_id or ""):
        return None
    with _LOCK:
        for item in _read_all():
            if item["id"] == doc_id and item["sr_no"] == int(sr_no):
                return item
    return None


def file_path(record):
    """Full path of the stored file on disk."""
    return settings.DATA_DIR / "documents" / f"{record['sr_no']:06d}" / record["stored_name"]


def delete_document(sr_no, doc_id):
    """Remove a document (list entry and file). Returns the removed record or None."""
    with _LOCK:
        record = get_document(sr_no, doc_id)
        if not record:
            return None
        _write_all([i for i in _read_all() if i["id"] != doc_id])
        file_path(record).unlink(missing_ok=True)
    return record
#-------------- End of the code ------------------------------
