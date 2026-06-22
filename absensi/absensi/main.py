import tkinter as tk
from database import init_database, insert_default_data
from views import theme
from views.view_login import LoginView
from views.view_mahasiswa_dashboard import MahasiswaDashboard
from views.view_dosen_dashboard import DosenDashboard


class AbsensiApp:
    """Main Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistem Absensi")
        self.root.geometry("860x620")
        self.root.minsize(820, 600)

        # Tema global (warna + style tabel)
        theme.setup_styles(self.root)

        # Initialize database
        init_database()
        insert_default_data()

        # Start with login
        self.show_login()

    def show_login(self):
        """Show login view"""
        self.clear_window()
        LoginView(self.root, self.on_login_success)

    def on_login_success(self, user):
        """Called when login is successful"""
        self.clear_window()

        if user["role"] == "mahasiswa":
            MahasiswaDashboard(self.root, user, self.show_login)
        elif user["role"] == "dosen":
            DosenDashboard(self.root, user, self.show_login)

    def clear_window(self):
        """Clear window widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = AbsensiApp()
    app.run()
