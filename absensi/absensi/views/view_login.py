import tkinter as tk
from tkinter import messagebox
from controller.controller_auth import AuthController
from views import theme as t


class LoginView:
    """Tampilan halaman login (kartu di tengah, layout grid)."""

    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        # Kartu login di tengah window
        self.frame = tk.Frame(
            root, bg=t.CARD, padx=40, pady=36,
            highlightbackground=t.BORDER, highlightthickness=1,
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Ikon + judul
        tk.Label(self.frame, text="🗓️", font=(t.FONT, 34), bg=t.CARD).grid(
            row=0, column=0, columnspan=2)
        tk.Label(
            self.frame, text="Sistem Absensi", font=(t.FONT_HEAD, 20, "bold"),
            bg=t.CARD, fg=t.PRIMARY,
        ).grid(row=1, column=0, columnspan=2)
        tk.Label(
            self.frame, text="Masuk dengan akun Anda",
            font=(t.FONT, 10), bg=t.CARD, fg=t.MUTED,
        ).grid(row=2, column=0, columnspan=2, pady=(2, 22))

        # Username
        tk.Label(self.frame, text="Username", font=(t.FONT, 10, "bold"),
                 bg=t.CARD, fg=t.TEXT).grid(row=3, column=0, columnspan=2, sticky="w")
        self.entry_username = tk.Entry(
            self.frame, font=(t.FONT, 11), width=30, relief="flat",
            highlightbackground=t.BORDER, highlightcolor=t.PRIMARY,
            highlightthickness=1,
        )
        self.entry_username.grid(row=4, column=0, columnspan=2, ipady=6, pady=(3, 14))

        # Password
        tk.Label(self.frame, text="Password", font=(t.FONT, 10, "bold"),
                 bg=t.CARD, fg=t.TEXT).grid(row=5, column=0, columnspan=2, sticky="w")
        self.entry_password = tk.Entry(
            self.frame, font=(t.FONT, 11), width=30, show="•", relief="flat",
            highlightbackground=t.BORDER, highlightcolor=t.PRIMARY,
            highlightthickness=1,
        )
        self.entry_password.grid(row=6, column=0, columnspan=2, ipady=6, pady=(3, 8))

        # Checkbox lihat password
        self.show_var = tk.BooleanVar()
        tk.Checkbutton(
            self.frame, text="Lihat password", variable=self.show_var,
            command=self.toggle_password, bg=t.CARD, fg=t.MUTED,
            font=(t.FONT, 9), activebackground=t.CARD, cursor="hand2",
            selectcolor=t.CARD,
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Tombol login
        t.make_button(
            self.frame, "Masuk", self.handle_login, color=t.PRIMARY, width=28
        ).grid(row=8, column=0, columnspan=2)

        # Info akun default
        tk.Label(
            self.frame,
            text="Coba: dosen1 / mahasiswa1  •  password: 123456",
            font=(t.FONT, 8), bg=t.CARD, fg=t.MUTED,
        ).grid(row=9, column=0, columnspan=2, pady=(18, 0))

        self.entry_password.bind("<Return>", lambda e: self.handle_login())
        self.entry_username.focus()

    def toggle_password(self):
        self.entry_password.config(show="" if self.show_var.get() else "•")

    def handle_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        user, error = AuthController.login(username, password)
        if error:
            messagebox.showerror("Login Gagal", error)
            return

        self.on_success(user)
