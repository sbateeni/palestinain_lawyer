from contextlib import contextmanager
import sqlite3
import os
from config.settings import APP_CONFIG

class DatabaseService:
    def __init__(self):
        self.db_path = APP_CONFIG['DATABASE_PATH']
        self._ensure_db_directory()
        self._init_db()
    
    def _ensure_db_directory(self):
        """التأكد من وجود مجلد قاعدة البيانات"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"خطأ في قاعدة البيانات: {str(e)}")
        finally:
            conn.close()
    
    def _init_db(self):
        """تهيئة قاعدة البيانات"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_case(self, title, content, analysis=None):
        """حفظ قضية جديدة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cases (title, content, analysis) VALUES (?, ?, ?)",
                (title, content, analysis)
            )
            return cursor.lastrowid
    
    def get_case(self, case_id):
        """استرجاع قضية محددة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
            return dict(cursor.fetchone() or {})
    
    def update_analysis(self, case_id, analysis):
        """تحديث تحليل قضية"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE cases SET analysis = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (analysis, case_id)
            )
    
    def get_recent_cases(self, limit=10):
        """استرجاع آخر القضايا"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM cases ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
