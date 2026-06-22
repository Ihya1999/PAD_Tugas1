import sqlite3
import os
from datetime import datetime

DB_NAME = "absensi.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            nama TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Absensi table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS absensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tanggal DATE NOT NULL,
            jam_masuk TIME,
            jam_pulang TIME,
            status TEXT DEFAULT 'hadir',
            keterangan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, tanggal)
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_default_data():
    """Insert default users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (?, ?, ?, ?)
            ''', ('dosen1', '123456', 'dosen', 'Dr. Saeful'))
            
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (?, ?, ?, ?)
            ''', ('mahasiswa1', '123456', 'mahasiswa', 'Andi Pratama'))
            
            cursor.execute('''
                INSERT INTO users (username, password, role, nama)
                VALUES (?, ?, ?, ?)
            ''', ('mahasiswa2', '123456', 'mahasiswa', 'Siti Nurhaliza'))
            
            conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
    insert_default_data()
    print("Database initialized successfully!")