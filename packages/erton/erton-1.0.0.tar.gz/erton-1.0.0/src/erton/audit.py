from __future__ import annotations
import json, time, sys

def log(event, **fields):
    sys.stdout.write(json.dumps({'ts':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'event':event,'fields':fields}, ensure_ascii=False)+'\n');sys.stdout.flush()
