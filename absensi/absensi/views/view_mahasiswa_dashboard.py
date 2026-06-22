import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from controller.controller_absensi import AbsensiController
from views import theme as t


class MahasiswaDashboard:
    """Dashboard mahasiswa: absen (hadir/izin/sakit), statistik, riwayat."""

    def __init__(self, root, user, on_logout):
        self.root = root
        self.user = user
        self.on_logout = on_logout
        self._clock_running = True

        self.frame = tk.Frame(root, bg=t.BG)
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_stats()
        self._build_absen()
        self._build_table()

        self.refresh()
        self._tick()

    # ---------- Header berwarna ----------
    def _build_header(self):
        header = tk.Frame(self.frame, bg=t.PRIMARY)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)

        kiri = tk.Frame(header, bg=t.PRIMARY)
        kiri.grid(row=0, column=0, sticky="w", padx=20, pady=14)
        tk.Label(kiri, text=f"{self._greeting()}, {self.user['nama']} 👋",
                 font=(t.FONT, 16, "bold"), bg=t.PRIMARY, fg="white").pack(anchor="w")
        tk.Label(kiri, text="Mahasiswa", font=(t.FONT, 9),
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
        self.card_total, self.lbl_total = t.stat_card(wrap, "Total Absen", 0, t.PRIMARY)
        self.card_hadir, self.lbl_hadir = t.stat_card(wrap, "Hadir", 0, t.SUCCESS)
        self.card_izin, self.lbl_izin = t.stat_card(wrap, "Izin", 0, t.WARNING)
        self.card_sakit, self.lbl_sakit = t.stat_card(wrap, "Sakit", 0, t.DANGER)
        for c in (self.card_total, self.card_hadir, self.card_izin, self.card_sakit):
            c.pack(side="left", expand=True, fill="x", padx=5)

    # ---------- Panel absen ----------
    def _build_absen(self):
        panel = tk.Frame(self.frame, bg=t.CARD, padx=16, pady=14)
        panel.pack(fill="x", padx=20, pady=8)

        self.label_status = tk.Label(panel, font=(t.FONT, 11), bg=t.CARD)
        self.label_status.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        tk.Label(panel, text="Status:", font=(t.FONT, 10, "bold"),
                 bg=t.CARD, fg=t.TEXT).grid(row=1, column=0, padx=(0, 8))
        self.status_var = tk.StringVar(value="hadir")
        ttk.Combobox(panel, textvariable=self.status_var, state="readonly", width=10,
                     values=["hadir", "izin", "sakit"]).grid(row=1, column=1, padx=(0, 12))

        t.make_button(panel, "✔ Absen Masuk", self.absen_masuk,
                      color=t.SUCCESS, width=16).grid(row=1, column=2, padx=5)
        t.make_button(panel, "← Absen Pulang", self.absen_pulang,
                      color=t.WARNING, width=16).grid(row=1, column=3, padx=5)

    # ---------- Tabel riwayat ----------
    def _build_table(self):
        wrap = tk.Frame(self.frame, bg=t.BG)
        wrap.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        tk.Label(wrap, text="Riwayat Absensi", font=(t.FONT, 12, "bold"),
                 bg=t.BG, fg=t.TEXT).pack(anchor="w", pady=(0, 6))

        self.tree = ttk.Treeview(
            wrap, columns=("tanggal", "masuk", "pulang", "status"),
            show="headings",
        )
        for col, txt in [("tanggal", "Tanggal"), ("masuk", "Jam Masuk"),
                         ("pulang", "Jam Pulang"), ("status", "Status")]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=160, anchor="center")
        self.tree.tag_configure("odd", background=t.STRIPE)
        self.tree.pack(fill="both", expand=True)

    # ---------- Logika ----------
    def refresh(self):
        today = AbsensiController.status_hari_ini(self.user["id"])
        if today:
            self.label_status.config(
                text=f"✅ Hari ini: {today['status'].upper()}  •  "
                     f"masuk {today['jam_masuk'] or '-'}  •  "
                     f"pulang {today['jam_pulang'] or '-'}",
                fg=t.SUCCESS)
        else:
            self.label_status.config(text="⚠ Hari ini: belum absen.", fg=t.DANGER)

        s = AbsensiController.statistik(self.user["id"])
        self.lbl_total.config(text=s["total"])
        self.lbl_hadir.config(text=s["hadir"])
        self.lbl_izin.config(text=s["izin"])
        self.lbl_sakit.config(text=s["sakit"])

        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(AbsensiController.riwayat(self.user["id"])):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", tags=(tag,), values=(
                row["tanggal"], row["jam_masuk"] or "-",
                row["jam_pulang"] or "-", row["status"].upper()))

    def absen_masuk(self):
        ok, msg = AbsensiController.absen_masuk(self.user["id"], self.status_var.get())
        (messagebox.showinfo if ok else messagebox.showwarning)("Absen Masuk", msg)
        self.refresh()

    def absen_pulang(self):
        ok, msg = AbsensiController.absen_pulang(self.user["id"])
        (messagebox.showinfo if ok else messagebox.showwarning)("Absen Pulang", msg)
        self.refresh()

    # ---------- Jam live & sapaan ----------
    def _tick(self):
        if not self._clock_running or not self.label_clock.winfo_exists():
            self._clock_running = False
            return
        now = datetime.now()
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        self.label_clock.config(
            text=f"{hari[now.weekday()]}, {now.strftime('%d-%m-%Y  %H:%M:%S')}")
        self.label_clock.after(1000, self._tick)

    @staticmethod
    def _greeting():
        h = datetime.now().hour
        if h < 11:
            return "Selamat pagi"
        if h < 15:
            return "Selamat siang"
        if h < 19:
            return "Selamat sore"
        return "Selamat malam"
