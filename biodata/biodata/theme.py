"""Tema & komponen UI bersama (tema Aurora / Violet)."""
import tkinter as tk
from tkinter import ttk

BG = "#f4f2fb"
CARD = "#ffffff"
PRIMARY = "#6d28d9"
PRIMARY_DARK = "#5b21b6"
TEXT = "#1f1b2e"
MUTED = "#6b6685"
SUCCESS = "#0ea968"
WARNING = "#e08a1e"
DANGER = "#e11d48"
INFO = "#2563eb"

ACCENT_SOFT = "#ddd6fe"
STRIPE = "#f7f5fe"
SELECT = "#e0d9fd"
BORDER = "#e3e0f0"

FONT = "Segoe UI"
FONT_HEAD = "Segoe UI Semibold"


def setup_styles(root):
    root.configure(bg=BG)
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Treeview", rowheight=30, font=(FONT, 10),
                    background=CARD, fieldbackground=CARD, borderwidth=0)
    style.configure("Treeview.Heading", font=(FONT_HEAD, 10, "bold"),
                    background=PRIMARY, foreground="white", relief="flat", padding=8)
    style.map("Treeview.Heading", background=[("active", PRIMARY_DARK)])
    style.map("Treeview", background=[("selected", SELECT)],
              foreground=[("selected", TEXT)])
    style.configure("TCombobox", fieldbackground=CARD, background=CARD,
                    bordercolor=BORDER, arrowcolor=PRIMARY, padding=4)
    return style


def make_button(parent, text, command, color=PRIMARY, width=14, fg="white"):
    btn = tk.Button(parent, text=text, command=command, font=(FONT, 10, "bold"),
                    bg=color, fg=fg, activebackground=color, activeforeground=fg,
                    relief="flat", cursor="hand2", width=width, bd=0, pady=8, padx=6)
    btn.bind("<Enter>", lambda _: btn.configure(bg=_darken(color)))
    btn.bind("<Leave>", lambda _: btn.configure(bg=color))
    return btn


def entry(parent, textvariable=None, show=None, width=28):
    return tk.Entry(parent, textvariable=textvariable, show=show or "",
                    font=(FONT, 11), width=width, relief="flat",
                    highlightbackground=BORDER, highlightcolor=PRIMARY,
                    highlightthickness=1)


def _darken(hex_color, factor=0.85):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"
