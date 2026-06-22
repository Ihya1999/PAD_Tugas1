from models.model_users import User


class AuthController:
    """Controller untuk autentikasi (login)."""

    @staticmethod
    def login(username, password):
        """Validasi input lalu cek ke Model.
        Return (user_dict, None) kalau sukses, atau (None, pesan_error)."""
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return None, "Username dan password wajib diisi."

        user = User.login(username, password)
        if not user:
            return None, "Username atau password salah."

        return user, None
