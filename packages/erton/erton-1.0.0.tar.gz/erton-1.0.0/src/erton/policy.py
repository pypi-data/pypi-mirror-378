from __future__ import annotations
import json, base64
from .crypto import hmac_verify
def load_signed_policy(path_json: str, path_sig: str, key: bytes) -> dict:
    data = open(path_json, 'rb').read()
    sig = base64.b64decode(open(path_sig, 'rb').read())
    if not hmac_verify(data, sig, key): raise SystemError('policy signature invalid')
    return json.loads(data.decode('utf-8'))
