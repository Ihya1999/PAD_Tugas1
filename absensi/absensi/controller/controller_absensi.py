from models.model_absensi import Absensi


class AbsensiController:
    """Controller untuk aksi absensi mahasiswa."""

    @staticmethod
    def absen_masuk(user_id, status="hadir"):
        """Return (berhasil: bool, pesan: str)."""
        return Absensi.absen_masuk(user_id, status)

    @staticmethod
    def absen_pulang(user_id):
        """Return (berhasil: bool, pesan: str)."""
        return Absensi.absen_pulang(user_id)

    @staticmethod
    def status_hari_ini(user_id):
        """Data absensi user untuk hari ini (None kalau belum absen)."""
        return Absensi.get_today(user_id)

    @staticmethod
    def riwayat(user_id):
        """Riwayat absensi seorang user."""
        return Absensi.get_by_user(user_id)

    @staticmethod
    def statistik(user_id):
        """Hitung jumlah per status dari riwayat user."""
        data = Absensi.get_by_user(user_id)
        return {
            "total": len(data),
            "hadir": sum(1 for r in data if r["status"] == "hadir"),
            "izin": sum(1 for r in data if r["status"] == "izin"),
            "sakit": sum(1 for r in data if r["status"] == "sakit"),
        }
