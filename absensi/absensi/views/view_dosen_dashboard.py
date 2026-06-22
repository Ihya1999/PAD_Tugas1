import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from controller.controller_report import ReportController
from views import theme as t


class DosenDashboard:
    """Dashboard dosen: rekap absensi semua mahasiswa + cari + export CSV."""

    def __init__(self, root, user, on_logout):
        self.root = root
        self.user = user
        self.on_logout = on_logout
        self._data = []          # cache data mentah (buat filter & export)
        self._clock_running = True

        self.frame = tk.Frame(root, bg=t.BG)
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_stats()
        self._build_toolbar()
        self._build_table()

        self.refresh()
        self._tick()

    # ---------- Header ----------
    def _build_header(self):
        header = tk.Frame(self.frame, bg=t.PRIMARY)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)

        kiri = tk.Frame(header, bg=t.PRIMARY)
        kiri.grid(row=0, column=0, sticky="w", padx=20, pady=14)
        tk.Label(kiri, text=f"Dashboard Dosen — {self.user['nama']}",
                 font=(t.FONT, 16, "bold"), bg=t.PRIMARY, fg="white").pack(anchor="w")
        tk.Label(kiri, text="Dosen", font=(t.FONT, 9),
                 bg=t.PRIMARY, fg=t.ACCENT_SOFT).pack(anchor="w")

        kanan = tk.Frame(header, bg=t.PRIMARY)
        kanan.grid(row=0, column=1, sticky="e", padx=20)
        self.label_clock = tk.Label(kanan, font=(t.FONT, 11, "bold"),
                                    bg=t.PRIMARY, fg="white")
        self.label_clock.pack(anchor="e")
        t.make_button(kanan, "Logout", self.on_logout, color=t.PRIMARY_DARK,
                      width=10).pack(anchor="e", pady=(4, 0))

    # ---------- Kartu statistik ----------
    def _build_stats(self):
        wrap = tk.Frame(self.frame, bg=t.BG)
        wrap.pack(fill="x", padx=20, pady=(16, 6))
        self.card_mhs, self.lbl_mhs = t.stat_card(wrap, "Total Mahasiswa", 0, t.INFO)
        self.card_abs, self.lbl_abs = t.stat_card(wrap, "Total Catatan Absensi", 0, t.PRIMARY)
        self.card_today, self.lbl_today = t.stat_card(wrap, "Absen Hari Ini", 0, t.SUCCESS)
        for c in (self.card_mhs, self.card_abs, self.card_today):
            c.pack(side="left", expand=True, fill="x", padx=5)

    # ---------- Toolbar: cari + tombol ----------
    def _build_toolbar(self):
        bar = tk.Frame(self.frame, bg=t.BG)
        bar.pack(fill="x", padx=20, pady=6)

        tk.Label(bar, text="🔍", bg=t.BG, font=(t.FONT, 11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(bar, textvariable=self.search_var, font=(t.FONT, 10), width=28,
                 relief="flat", highlightbackground=t.BORDER,
                 highlightcolor=t.PRIMARY, highlightthickness=1
                 ).pack(side="left", ipady=4, padx=(4, 0))
        tk.Label(bar, text="cari nama mahasiswa…", bg=t.BG, fg=t.MUTED,
                 font=(t.FONT, 8)).pack(side="left", padx=8)

        t.make_button(bar, "📥 Export CSV", self.export_csv,
                      color=t.SUCCESS, width=14).pack(side="right")
        t.make_button(bar, "⟳ Refresh", self.refresh,
                      color=t.INFO, width=12).pack(side="right", padx=6)

    # ---------- Tabel ----------
    def _build_table(self):
        wrap = tk.Frame(self.frame, bg=t.BG)
        wrap.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        self.tree = ttk.Treeview(
            wrap, columns=("nama", "tanggal", "masuk", "pulang", "status"),
            show="headings")
        for col, txt, w in [("nama", "Nama", 180), ("tanggal", "Tanggal", 110),
                            ("masuk", "Jam Masuk", 100), ("pulang", "Jam Pulang", 100),
                            ("status", "Status", 90)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("nama", anchor="w")
        self.tree.tag_configure("odd", background=t.STRIPE)
        self.tree.pack(fill="both", expand=True)

    # ---------- Logika ----------
    def refresh(self):
        self._data = ReportController.rekap_semua()
        r = ReportController.ringkasan()
        self.lbl_mhs.config(text=r["jumlah_mahasiswa"])
        self.lbl_abs.config(text=r["total_absensi"])
        self.lbl_today.config(text=r["absen_hari_ini"])
        self._apply_filter()

    def _apply_filter(self):
        kata = self.search_var.get().strip().lower()
        rows = [d for d in self._data if kata in d["nama"].lower()] if kata else self._data
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", tags=(tag,), values=(
                row["nama"], row["tanggal"], row["jam_masuk"] or "-",
                row["jam_pulang"] or "-", row["status"].upper()))

    def export_csv(self):
        if not self._data:
            messagebox.showwarning("Export", "Belum ada data untuk diexport.")
            return
        nama_file = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=f"rekap_absensi_{datetime.now():%Y%m%d}.csv")
        if not nama_file:
            return
        try:
            with open(nama_file, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Nama", "Tanggal", "Jam Masuk", "Jam Pulang", "Status"])
                for d in self._data:
                    w.writerow([d["nama"], d["tanggal"], d["jam_masuk"] or "",
                                d["jam_pulang"] or "", d["status"]])
            messagebox.showinfo("Export", f"Berhasil disimpan ke:\n{nama_file}")
        except OSError as e:
            messagebox.showerror("Export Gagal", str(e))

    # ---------- Jam live ----------
    def _tick(self):
        if not self._clock_running or not self.label_clock.winfo_exists():
            self._clock_running = False
            return
        self.label_clock.config(text=datetime.now().strftime("%d-%m-%Y  %H:%M:%S"))
        self.label_clock.after(1000, self._tick)
