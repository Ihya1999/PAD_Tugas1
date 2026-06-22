"""Aplikasi Desktop Biodata (Tkinter + SQLite + foto).

Fitur:
- Tambah / ubah / hapus biodata
- Pilih & tampilkan foto (disalin ke folder photos/)
- Cari berdasarkan nama, daftar dalam tabel
"""
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

import database as db
import theme as t

PHOTO_DIR = "photos"
PHOTO_W, PHOTO_H = 170, 210


class BiodataApp:
    def __init__(self):
        os.makedirs(PHOTO_DIR, exist_ok=True)
        db.init_database()

        self.root = tk.Tk()
        self.root.title("Aplikasi Biodata")
        self.root.geometry("980x640")
        self.root.minsize(940, 600)
        t.setup_styles(self.root)

        self.current_id = None        # id biodata yang sedang diedit (None = baru)
        self.foto_path = None         # path foto terpilih
        self._photo_img = None        # simpan referensi agar tidak di-GC

        self._build_header()
        body = tk.Frame(self.root, bg=t.BG)
        body.pack(fill="both", expand=True, padx=18, pady=(8, 16))
        self._build_form(body)
        self._build_list(body)

        self.refresh_list()
        self.reset_form()

    # ---------------- Header ----------------
    def _build_header(self):
        h = tk.Frame(self.root, bg=t.PRIMARY)
        h.pack(fill="x")
        tk.Label(h, text="📇  Aplikasi Biodata", font=(t.FONT_HEAD, 18, "bold"),
                 bg=t.PRIMARY, fg="white").pack(side="left", padx=20, pady=14)
        tk.Label(h, text="Kelola data diri lengkap dengan foto",
                 font=(t.FONT, 9), bg=t.PRIMARY, fg=t.ACCENT_SOFT).pack(
                     side="left", pady=(20, 14))

    # ---------------- Form + foto (kiri) ----------------
    def _build_form(self, parent):
        panel = tk.Frame(parent, bg=t.CARD, highlightbackground=t.BORDER,
                         highlightthickness=1, width=300)
        panel.pack(side="left", fill="y", padx=(0, 14))
        panel.pack_propagate(False)

        # --- Footer tetap (selalu terlihat): tombol Simpan & Baru ---
        footer = tk.Frame(panel, bg=t.CARD)
        footer.pack(side="bottom", fill="x", padx=14, pady=12)
        t.make_button(footer, "💾 Simpan", self.simpan,
                      color=t.SUCCESS, width=11).pack(side="left", padx=3)
        t.make_button(footer, "🆕 Baru", self.reset_form,
                      color=t.WARNING, width=9).pack(side="left", padx=3)

        # --- Area form yang bisa di-scroll ---
        canvas = tk.Canvas(panel, bg=t.CARD, highlightthickness=0)
        sb = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=t.CARD, padx=18, pady=16)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # scroll dengan roda mouse saat kursor di area form
        canvas.bind("<Enter>", lambda _: canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-e.delta / 120), "units")))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))

        # --- Foto ---
        self.foto_label = tk.Label(inner, bg=t.STRIPE, width=PHOTO_W, height=PHOTO_H,
                                   bd=1, relief="solid")
        self.foto_label.grid(row=0, column=0, columnspan=2, pady=(0, 8))

        fbtn = tk.Frame(inner, bg=t.CARD)
        fbtn.grid(row=1, column=0, columnspan=2, pady=(0, 12))
        t.make_button(fbtn, "🖼 Pilih Foto", self.pilih_foto,
                      color=t.INFO, width=12).pack(side="left", padx=3)
        t.make_button(fbtn, "✖ Hapus Foto", self.hapus_foto,
                      color=t.MUTED, width=12).pack(side="left", padx=3)

        # --- Field input ---
        self.vars = {}
        fields = [
            ("nama", "Nama Lengkap", "entry"),
            ("tempat_lahir", "Tempat Lahir", "entry"),
            ("tanggal_lahir", "Tanggal Lahir (dd-mm-yyyy)", "entry"),
            ("jenis_kelamin", "Jenis Kelamin", "combo:Laki-laki,Perempuan"),
            ("agama", "Agama", "combo:Islam,Kristen,Katolik,Hindu,Buddha,Konghucu"),
            ("telepon", "No. Telepon", "entry"),
            ("email", "Email", "entry"),
            ("hobi", "Hobi", "entry"),
        ]
        r = 2
        for key, label, kind in fields:
            tk.Label(inner, text=label, font=(t.FONT, 9, "bold"),
                     bg=t.CARD, fg=t.TEXT).grid(row=r, column=0, columnspan=2,
                                                sticky="w", pady=(4, 1))
            r += 1
            var = tk.StringVar()
            self.vars[key] = var
            if kind.startswith("combo:"):
                opts = kind.split(":", 1)[1].split(",")
                ttk.Combobox(inner, textvariable=var, values=opts, state="readonly",
                             width=26).grid(row=r, column=0, columnspan=2,
                                            sticky="we", pady=(0, 2))
            else:
                t.entry(inner, textvariable=var).grid(
                    row=r, column=0, columnspan=2, sticky="we", ipady=3, pady=(0, 2))
            r += 1

        # Alamat (multiline)
        tk.Label(inner, text="Alamat", font=(t.FONT, 9, "bold"),
                 bg=t.CARD, fg=t.TEXT).grid(row=r, column=0, columnspan=2,
                                            sticky="w", pady=(4, 1))
        r += 1
        self.txt_alamat = tk.Text(inner, height=3, width=28, font=(t.FONT, 10),
                                  relief="flat", highlightbackground=t.BORDER,
                                  highlightcolor=t.PRIMARY, highlightthickness=1)
        self.txt_alamat.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 10))

    # ---------------- Daftar (kanan) ----------------
    def _build_list(self, parent):
        right = tk.Frame(parent, bg=t.BG)
        right.pack(side="left", fill="both", expand=True)

        bar = tk.Frame(right, bg=t.BG)
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="🔍", bg=t.BG, font=(t.FONT, 11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        t.entry(bar, textvariable=self.search_var, width=24).pack(
            side="left", ipady=3, padx=(4, 0))
        tk.Label(bar, text="cari nama…", bg=t.BG, fg=t.MUTED,
                 font=(t.FONT, 8)).pack(side="left", padx=8)
        t.make_button(bar, "🗑 Hapus", self.hapus_data,
                      color=t.DANGER, width=10).pack(side="right")

        wrap = tk.Frame(right, bg=t.BG)
        wrap.pack(fill="both", expand=True)
        cols = ("id", "nama", "jk", "telepon")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        for c, txt, w, anc in [("id", "ID", 40, "center"), ("nama", "Nama", 200, "w"),
                               ("jk", "L/P", 90, "center"),
                               ("telepon", "Telepon", 130, "center")]:
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor=anc)
        self.tree.tag_configure("odd", background=t.STRIPE)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ---------------- Foto ----------------
    def pilih_foto(self):
        path = filedialog.askopenfilename(
            title="Pilih Foto",
            filetypes=[("Gambar", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Semua", "*.*")])
        if not path:
            return
        self.foto_path = path
        self.tampilkan_foto(path)

    def hapus_foto(self):
        self.foto_path = None
        self.tampilkan_foto(None)

    def tampilkan_foto(self, path):
        """Render foto (atau placeholder) ke label, sudah di-resize proporsional."""
        try:
            if path and os.path.exists(path):
                img = Image.open(path)
                img = ImageOps.exif_transpose(img)  # koreksi rotasi EXIF (foto HP)
                img = img.convert("RGB")
                img = self._fit(img, PHOTO_W, PHOTO_H)
            else:
                img = self._placeholder()
        except Exception:
            img = self._placeholder()
        self._photo_img = ImageTk.PhotoImage(img)
        self.foto_label.configure(image=self._photo_img, width=PHOTO_W, height=PHOTO_H)

    @staticmethod
    def _fit(img, w, h):
        """Resize agar pas dalam kotak w×h, sisanya diberi latar putih (kotak rapi)."""
        img.thumbnail((w, h), Image.LANCZOS)
        bg = Image.new("RGB", (w, h), "#f7f5fe")
        bg.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
        return bg

    @staticmethod
    def _placeholder():
        img = Image.new("RGB", (PHOTO_W, PHOTO_H), "#ede9fc")
        d = ImageDraw.Draw(img)
        d.ellipse((55, 45, 115, 105), fill="#c4b5fd")
        d.ellipse((40, 120, 130, 210), fill="#c4b5fd")
        try:
            font = ImageFont.truetype("segoeui.ttf", 13)
        except Exception:
            font = ImageFont.load_default()
        d.text((PHOTO_W // 2, 160), "Tanpa Foto", fill="#7c6fb0",
               anchor="mm", font=font)
        return img

    # ---------------- CRUD ----------------
    def _kumpulkan(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        data["alamat"] = self.txt_alamat.get("1.0", "end").strip()
        data["foto_path"] = self.foto_path
        return data

    def _simpan_foto(self, src):
        """Salin foto ke folder photos/ dan kembalikan path relatif."""
        if not src or not os.path.exists(src):
            return None
        # kalau sudah berada di dalam folder photos, pakai apa adanya
        if os.path.normpath(os.path.dirname(os.path.abspath(src))) == \
                os.path.normpath(os.path.abspath(PHOTO_DIR)):
            return os.path.join(PHOTO_DIR, os.path.basename(src))
        ext = os.path.splitext(src)[1].lower() or ".png"
        nama = datetime.now().strftime("%Y%m%d%H%M%S%f") + ext
        dst = os.path.join(PHOTO_DIR, nama)
        shutil.copy2(src, dst)
        return dst

    def simpan(self):
        data = self._kumpulkan()
        if not data["nama"]:
            messagebox.showwarning("Validasi", "Nama wajib diisi.")
            return
        data["foto_path"] = self._simpan_foto(self.foto_path)

        if self.current_id is None:
            db.tambah(data)
            messagebox.showinfo("Sukses", "Biodata baru tersimpan.")
        else:
            db.ubah(self.current_id, data)
            messagebox.showinfo("Sukses", "Biodata diperbarui.")
        self.refresh_list()
        self.reset_form()

    def hapus_data(self):
        if self.current_id is None:
            messagebox.showwarning("Hapus", "Pilih biodata dari daftar dulu.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus biodata terpilih?"):
            return
        db.hapus(self.current_id)
        self.refresh_list()
        self.reset_form()

    def reset_form(self):
        self.current_id = None
        self.foto_path = None
        for v in self.vars.values():
            v.set("")
        self.txt_alamat.delete("1.0", "end")
        self.tampilkan_foto(None)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    # ---------------- List ----------------
    def refresh_list(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        for i, row in enumerate(db.get_all(self.search_var.get().strip())):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(row["id"]), tags=(tag,),
                             values=(row["id"], row["nama"],
                                     row["jenis_kelamin"] or "-",
                                     row["telepon"] or "-"))

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        row = db.get(int(sel[0]))
        if not row:
            return
        self.current_id = row["id"]
        for k, v in self.vars.items():
            v.set(row.get(k) or "")
        self.txt_alamat.delete("1.0", "end")
        self.txt_alamat.insert("1.0", row.get("alamat") or "")
        self.foto_path = row.get("foto_path")
        self.tampilkan_foto(self.foto_path)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    BiodataApp().run()
