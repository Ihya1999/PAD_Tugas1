from models.model_absensi import Absensi
from models.model_users import User


class ReportController:
    """Controller untuk laporan/rekap (dipakai dosen)."""

    @staticmethod
    def rekap_semua():
        """Rekap absensi seluruh mahasiswa (sudah ada nama user)."""
        return Absensi.get_all()

    @staticmethod
    def ringkasan():
        """Angka ringkasan: jumlah mahasiswa, total catatan, & hadir hari ini."""
        return {
            "jumlah_mahasiswa": len(User.get_all_mahasiswa()),
            "total_absensi": len(Absensi.get_all()),
            "absen_hari_ini": Absensi.count_today(),
        }
