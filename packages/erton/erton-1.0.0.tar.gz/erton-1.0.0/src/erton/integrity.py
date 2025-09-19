from __future__ import annotations
import hashlib
from pathlib import Path
def file_sha256(path: str|Path)->str:
    p=Path(path); h=hashlib.sha256()
    with p.open('rb') as f:
        for ch in iter(lambda:f.read(8192), b''):
            h.update(ch)
    return h.hexdigest()
