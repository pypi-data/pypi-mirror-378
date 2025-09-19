from __future__ import annotations
import argparse
from .runtime_guard import guard_start
from .crypto import generate_key, encrypt, decrypt
from .sdk import ErtonClient
def main() -> None:
    p = argparse.ArgumentParser(prog="erton")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("guard"); g.add_argument("--allow", nargs="*", default=["python.exe","kernel32.dll","user32.dll","psapi.dll","ntdll.dll"])
    k = sub.add_parser("key"); k.add_argument("--out", default="shared.key")
    a = sub.add_parser("approve"); a.add_argument("player"); a.add_argument("--key", default="shared.key")
    t = sub.add_parser("tick"); t.add_argument("player"); t.add_argument("--key", default="shared.key"); t.add_argument("--yaw", type=float, default=35); t.add_argument("--pitch", type=float, default=1.1)
    args = p.parse_args()
    if args.cmd == "guard": guard_start(args.allow, forbid_debugger=True); print("guard ok")
    elif args.cmd == "key": k = generate_key(); open(args.out,"wb").write(k); print("key saved:", args.out)
    elif args.cmd == "approve":
        key = open(args.key,"rb").read(); cli = ErtonClient(shared_key=key); print(cli.approve(args.player))
    elif args.cmd == "tick":
        key = open(args.key,"rb").read(); cli = ErtonClient(shared_key=key)
        print(cli.aim_tick(args.player, dt=0.016, delta_yaw=args.yaw, delta_pitch=args.pitch, mouse_dx=50, mouse_dy=2, sens=0.6, fov=90))
