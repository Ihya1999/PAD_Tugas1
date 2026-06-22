import sqlite3
from datetime import datetime
from database import get_connection


class Absensi:
    """Model untuk Absensi"""

    @staticmethod
    def _today():
        """Tanggal hari ini (format YYYY-MM-DD)"""
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _now_time():
        """Jam sekarang (format HH:MM:SS)"""
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_today(user_id):
        """Ambil data absensi user untuk hari ini (None kalau belum ada)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM absensi WHERE user_id = ? AND tanggal = ?",
            (user_id, Absensi._today()),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def absen_masuk(user_id, status="hadir", keterangan=""):
        """Catat jam masuk untuk hari ini dengan status (hadir/izin/sakit).
        Return (True, pesan) kalau berhasil, (False, pesan) kalau gagal."""
        if Absensi.get_today(user_id):
            return False, "Kamu sudah absen hari ini."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO absensi (user_id, tanggal, jam_masuk, status, keterangan)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, Absensi._today(), Absensi._now_time(), status, keterangan),
        )
        conn.commit()
        conn.close()
        return True, f"Absen berhasil dicatat (status: {status})."

    @staticmethod
    def absen_pulang(user_id):
        """Catat jam pulang untuk hari ini.
        Return (True, pesan) atau (False, pesan)."""
        today = Absensi.get_today(user_id)
        if not today:
            return False, "Kamu belum absen masuk hari ini."
        if today["jam_pulang"]:
            return False, "Kamu sudah absen pulang hari ini."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE absensi SET jam_pulang = ? WHERE user_id = ? AND tanggal = ?",
            (Absensi._now_time(), user_id, Absensi._today()),
        )
        conn.commit()
        conn.close()
        return True, "Absen pulang berhasil dicatat."

    @staticmethod
    def get_by_user(user_id):
        """Riwayat absensi seorang user (terbaru di atas)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM absensi WHERE user_id = ? ORDER BY tanggal DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def count_today():
        """Jumlah mahasiswa yang sudah absen hari ini."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM absensi WHERE tanggal = ?", (Absensi._today(),)
        )
        n = cursor.fetchone()[0]
        conn.close()
        return n

    @staticmethod
    def get_all():
        """Rekap semua absensi + nama user (untuk dosen)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.tanggal, a.jam_masuk, a.jam_pulang, a.status,
                   u.nama, u.username
            FROM absensi a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.tanggal DESC, u.nama ASC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
