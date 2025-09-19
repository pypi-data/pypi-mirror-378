from __future__ import annotations
import sys, os
from typing import Iterable, Set
IS_WINDOWS = (os.name == "nt")
def is_debugger_present() -> bool:
    if not IS_WINDOWS: return False
    import ctypes; return bool(ctypes.windll.kernel32.IsDebuggerPresent())
def get_loaded_modules_windows() -> Set[str]:
    if not IS_WINDOWS: return set()
    import ctypes, ctypes.wintypes as wt, os
    psapi = ctypes.WinDLL("Psapi.dll"); kernel32 = ctypes.WinDLL("kernel32.dll")
    h = kernel32.GetCurrentProcess(); arr = (wt.HMODULE * 1024)(); needed = wt.DWORD()
    if not psapi.EnumProcessModules(h, ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(needed)): return set()
    count = int(needed.value // ctypes.sizeof(wt.HMODULE)); names = set(); buf = ctypes.create_unicode_buffer(260)
    for i in range(count): psapi.GetModuleFileNameExW(h, arr[i], buf, 260); names.add(os.path.basename(buf.value).lower())
    return names
def enforce_allowlist(allowed: Iterable[str], *, fail_fast: bool=True) -> None:
    allowed_set = {a.lower() for a in allowed}; loaded = get_loaded_modules_windows()
    unknown = {m for m in loaded if m not in allowed_set}
    if unknown:
        sys.stderr.write(f"[Erton] Unknown modules: {sorted(unknown)}\n"); sys.stderr.flush()
        if fail_fast: raise SystemExit(23)
def guard_start(allowed_modules: Iterable[str], *, forbid_debugger: bool=True) -> None:
    if forbid_debugger and is_debugger_present(): raise SystemExit(22)
    enforce_allowlist(allowed_modules, fail_fast=True)
