from __future__ import annotations
import argparse, socket, json, threading, base64, time
from .analyzers.aim import features, score_and_reasons
from .runtime_guard import guard_start
from .audit import log
from .watch import WATCH
from .crypto import hmac_sign, check_token

def handle(conn, addr, policy, shared_key: bytes):
    with conn:
        f = conn.makefile("rwb")
        chal = base64.b64encode(hmac_sign(str(time.time()).encode(), shared_key)).decode()
        f.write((json.dumps({"hello":"erton","challenge":chal})+"\n").encode()); f.flush()
        for line in f:
            try:
                msg = json.loads(line.decode("utf-8", errors="ignore"))
                token = msg.get("token","")
                if not check_token(token, shared_key):
                    out = {"ok": False, "error":"auth token invalid"}
                else:
                    typ = msg.get("type"); pid = msg.get("player_id","")
                    if typ == "watch.approve":
                        WATCH.approve(pid); out = {"ok": True, "approved": pid}
                    elif typ == "watch.revoke":
                        WATCH.revoke(pid); out = {"ok": True, "revoked": pid}
                    elif typ == "aim_tick":
                        if not WATCH.is_approved(pid): out={"ok":True,"skip":True}
                        else:
                            p = msg; feats = features(p.get("dt",0.016), p.get("delta_yaw",0.0), p.get("delta_pitch",0.0),
                                                     p.get("mouse_dx",0.0), p.get("mouse_dy",0.0), p.get("sens",1.0), p.get("fov",90.0))
                            score, reasons = score_and_reasons(feats)
                            warn = policy.get("thresh_warn",0.7); act = policy.get("thresh_action",0.9)
                            if score >= act: rec = policy.get("action_high","ban")
                            elif score >= warn: rec = policy.get("action_mid","kick")
                            else: rec = "none"
                            out = {"ok": True, "score": round(score,3), "reasons": reasons, "recommendation": rec, "feats": feats}
                    else:
                        out = {"ok": False, "error":"unknown type"}
            except Exception as e:
                out = {"ok": False, "error": str(e)}
            f.write((json.dumps(out, ensure_ascii=False)+"\n").encode()); f.flush()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--policy", type=str, default="config/policy.json")
    ap.add_argument("--guard", action="store_true")
    ap.add_argument("--shared-key", type=str, default="")
    args = ap.parse_args()
    import pathlib, json as j, base64
    policy = {"thresh_warn":0.7,"thresh_action":0.9,"action_mid":"kick","action_high":"ban",
              "allow_dlls":["python.exe","kernel32.dll","user32.dll","psapi.dll","ntdll.dll"]}
    pj = pathlib.Path(args.policy)
    if pj.is_file(): policy = j.loads(pj.read_text(encoding="utf-8"))
    if args.guard: guard_start(policy.get("allow_dlls", []), forbid_debugger=True)
    SHARED_KEY = base64.b64decode(args.shared_key.encode()) if args.shared_key else b"default_dev_key____________________"[:32]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((args.host, args.port)); s.listen(16)
    log("service.start", host=args.host, port=args.port, policy=policy)
    try:
        while True:
            c, a = s.accept()
            threading.Thread(target=handle, args=(c, a, policy, SHARED_KEY), daemon=True).start()
    finally:
        s.close()
if __name__ == "__main__": main()
