"""Tema & komponen UI bersama (warna, font, tombol, style tabel).

Tema: "Aurora" — Violet / Indigo modern.
"""
import tkinter as tk
from tkinter import ttk

# ---- Palet warna (tema Aurora / Violet) ----
BG = "#f4f2fb"        # latar utama (lavender lembut)
CARD = "#ffffff"      # latar kartu
PRIMARY = "#6d28d9"   # violet (aksen utama)
PRIMARY_DARK = "#5b21b6"
TEXT = "#1f1b2e"      # teks gelap keunguan
MUTED = "#6b6685"     # teks abu-ungu
SUCCESS = "#0ea968"   # hijau emerald
WARNING = "#e08a1e"   # amber
DANGER = "#e11d48"    # merah rose
INFO = "#2563eb"      # biru royal

# warna pendukung
ACCENT_SOFT = "#ddd6fe"   # ungu muda (subtitle di header)
STRIPE = "#f7f5fe"        # baris ganjil tabel (lavender sangat muda)
SELECT = "#e0d9fd"        # baris terpilih
BORDER = "#e3e0f0"        # garis tepi input

FONT = "Segoe UI"
FONT_HEAD = "Segoe UI Semibold"


def setup_styles(root):
    """Atur tema global + style Treeview. Panggil sekali saat app mulai."""
    root.configure(bg=BG)
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        rowheight=34,
        font=(FONT, 11),
        background=CARD,
        fieldbackground=CARD,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        font=(FONT_HEAD, 11, "bold"),
        background=PRIMARY,
        foreground="white",
        relief="flat",
        padding=10,
    )
    style.map("Treeview.Heading", background=[("active", PRIMARY_DARK)])
    style.map("Treeview", background=[("selected", SELECT)],
              foreground=[("selected", TEXT)])

    # Combobox senada tema
    style.configure(
        "TCombobox",
        fieldbackground=CARD,
        background=CARD,
        bordercolor=BORDER,
        arrowcolor=PRIMARY,
        padding=5,
    )
    return style


def make_button(parent, text, command, color=PRIMARY, width=16, fg="white"):
    """Tombol flat modern (pill) + efek hover."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=(FONT, 10, "bold"),
        bg=color,
        fg=fg,
        activebackground=color,
        activeforeground=fg,
        relief="flat",
        cursor="hand2",
        width=width,
        bd=0,
        pady=10,
        padx=8,
    )

    def _on_enter(_):
        btn.configure(bg=_darken(color))

    def _on_leave(_):
        btn.configure(bg=color)

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    return btn


def stat_card(parent, judul, nilai, warna=PRIMARY):
    """Kartu statistik dengan aksen garis samping. Return (frame, label_nilai)."""
    card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    # aksen garis tebal di sisi kiri kartu
    tk.Frame(card, bg=warna, width=5).pack(side="left", fill="y")
    isi = tk.Frame(card, bg=CARD, padx=18, pady=14)
    isi.pack(side="left", fill="both", expand=True)
    tk.Label(isi, text=judul.upper(), font=(FONT, 9, "bold"),
             bg=CARD, fg=MUTED).pack(anchor="w")
    lbl = tk.Label(isi, text=str(nilai), font=(FONT_HEAD, 24, "bold"),
                   bg=CARD, fg=warna)
    lbl.pack(anchor="w")
    return card, lbl


def _darken(hex_color, factor=0.85):
    """Gelapkan warna hex sedikit (buat efek hover)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"
