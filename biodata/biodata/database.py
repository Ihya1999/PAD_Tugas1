"""Lapisan database SQLite untuk aplikasi Biodata."""
import sqlite3
from datetime import datetime

DB_NAME = "biodata.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Buat tabel biodata bila belum ada."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS biodata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            tempat_lahir TEXT,
            tanggal_lahir TEXT,
            jenis_kelamin TEXT,
            agama TEXT,
            telepon TEXT,
            email TEXT,
            alamat TEXT,
            hobi TEXT,
            foto_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def tambah(data):
    """Tambah satu biodata. `data` berupa dict. Return id baru."""
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO biodata
            (nama, tempat_lahir, tanggal_lahir, jenis_kelamin, agama,
             telepon, email, alamat, hobi, foto_path)
        VALUES (:nama, :tempat_lahir, :tanggal_lahir, :jenis_kelamin, :agama,
                :telepon, :email, :alamat, :hobi, :foto_path)
        """,
        data,
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def ubah(bio_id, data):
    """Update biodata berdasarkan id."""
    data = dict(data, id=bio_id)
    conn = get_connection()
    conn.execute(
        """
        UPDATE biodata SET
            nama=:nama, tempat_lahir=:tempat_lahir, tanggal_lahir=:tanggal_lahir,
            jenis_kelamin=:jenis_kelamin, agama=:agama, telepon=:telepon,
            email=:email, alamat=:alamat, hobi=:hobi, foto_path=:foto_path
        WHERE id=:id
        """,
        data,
    )
    conn.commit()
    conn.close()


def hapus(bio_id):
    conn = get_connection()
    conn.execute("DELETE FROM biodata WHERE id=?", (bio_id,))
    conn.commit()
    conn.close()


def get_all(keyword=""):
    """Ambil semua biodata, opsi filter berdasarkan nama."""
    conn = get_connection()
    if keyword:
        rows = conn.execute(
            "SELECT * FROM biodata WHERE nama LIKE ? ORDER BY nama",
            (f"%{keyword}%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM biodata ORDER BY nama").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get(bio_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM biodata WHERE id=?", (bio_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    init_database()
    print("Database biodata siap.")
