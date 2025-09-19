from __future__ import annotations
import tkinter as tk
from .core import brand_text
def splash(title: str|None=None, ms: int=1800):
    root = tk.Tk(); root.title(title or brand_text()); root.geometry("520x260"); root.resizable(False, False)
    lab = tk.Label(root, text=(title or brand_text()), font=("Segoe UI", 14)); lab.pack(expand=True, fill="both", padx=16, pady=16)
    root.after(ms, root.destroy); root.mainloop()
