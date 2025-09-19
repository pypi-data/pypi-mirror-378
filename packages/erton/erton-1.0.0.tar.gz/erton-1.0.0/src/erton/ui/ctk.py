from __future__ import annotations
try:
    import customtkinter as ctk
except Exception as e:
    raise RuntimeError("customtkinter not installed. Install with `pip install '.[gui]'`.") from e
from .core import brand_text
def splash(title: str|None=None, ms: int=1800):
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    root = ctk.CTk(); root.title(title or brand_text()); root.geometry("560x300"); root.resizable(False, False)
    lbl = ctk.CTkLabel(root, text=(title or brand_text()), font=ctk.CTkFont("Segoe UI", 18))
    lbl.pack(expand=True, fill="both", padx=16, pady=16)
    root.after(ms, root.destroy); root.mainloop()
