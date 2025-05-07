import os, hashlib, mimetypes
from typing import List, Dict

def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def scan(directory: str, recursive: bool = True) -> List[Dict]:
    out: List[Dict] = []
    walker = os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]
    for root, _, files in walker:
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                out.append({
                    "file_hash": _hash_file(fp),
                    "filename": fn,
                    "original_path": fp,
                    "file_type": os.path.splitext(fn)[1].lstrip(".").lower(),
                    "mime_type": mimetypes.guess_type(fp)[0] or "application/octet-stream",
                    "size_bytes": os.path.getsize(fp)
                })
            except Exception:
                continue
    return out