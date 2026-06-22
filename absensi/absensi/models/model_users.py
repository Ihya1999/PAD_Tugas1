import sqlite3
from database import get_connection

class User:
    """Model untuk User"""
    
    @staticmethod
    def login(username, password):
        """Login pengguna"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password = ?
        ''', (username, password))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_all_mahasiswa():
        """Get all mahasiswa"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE role = "mahasiswa" ORDER BY nama')
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY nama')
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]