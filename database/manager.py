import sqlite3
import json
from datetime import datetime
from config.settings import APP_CONFIG

class DatabaseManager:
    def __init__(self):
        self.db_path = APP_CONFIG['DATABASE_PATH']
        print(f"Database path: {self.db_path}")  # للتتبع

    def init_db(self):
        """تهيئة قاعدة البيانات"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cases (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        original_text TEXT NOT NULL,
                        status TEXT NOT NULL,
                        date TEXT NOT NULL,
                        stages TEXT NOT NULL
                    )
                ''')
                
                # إنشاء جدول رسائل الدردشة
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT NOT NULL,
                        model_used TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (case_id) REFERENCES cases(id)
                    )
                ''')
                conn.commit()
                print("Database initialized successfully")  # للتتبع
        except Exception as e:
            print(f"Error initializing database: {str(e)}")  # للتتبع
            raise

    def get_all_cases(self):
        """استرجاع جميع القضايا"""
        try:
            print("Fetching all cases from database")  # للتتبع
            query = 'SELECT * FROM cases ORDER BY date DESC'
            results = self.execute_query(query)
            cases = []
            for row in results:
                case = dict(row)
                case['stages'] = json.loads(case['stages'])
                cases.append(case)
            print(f"Found {len(cases)} cases")  # للتتبع
            return cases
        except Exception as e:
            print(f"Error fetching cases: {str(e)}")  # للتتبع
            raise

    def save_case(self, case_data):
        """حفظ قضية جديدة"""
        try:
            print(f"Saving case: {case_data['id']}")  # للتتبع
            query = '''
                INSERT OR REPLACE INTO cases (id, title, original_text, status, date, stages)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (
                case_data['id'],
                case_data['title'],
                case_data['original_text'],
                case_data['status'],
                case_data['date'],
                case_data['stages']
            )
            self.execute_query(query, params, fetch=False)
            print("Case saved successfully")  # للتتبع
        except Exception as e:
            print(f"Error saving case: {str(e)}")  # للتتبع
            raise

    def execute_query(self, query, params=(), fetch=True):
        """تنفيذ استعلام SQL"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error executing query: {str(e)}")  # للتتبع
            raise

    def get_case(self, case_id):
        """استرجاع قضية محددة"""
        try:
            print(f"Getting case from database: {case_id}")  # للتتبع
            query = 'SELECT * FROM cases WHERE id = ?'
            result = self.execute_query(query, (case_id,))
            if result:
                case = dict(result[0])
                case['stages'] = json.loads(case['stages'])
                print(f"Case found: {case['id']}")  # للتتبع
                return case
            print("Case not found")  # للتتبع
            return None
        except Exception as e:
            print(f"Error in get_case: {str(e)}")  # للتتبع
            raise

    def save_chat_message(self, case_id, message, response, model_used):
        """حفظ رسالة دردشة جديدة"""
        try:
            query = '''
                INSERT INTO chat_messages (case_id, message, response, model_used, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            '''
            params = (case_id, message, response, model_used)
            self.execute_query(query, params, fetch=False)
            print(f"Chat message saved for case: {case_id}")
        except Exception as e:
            print(f"Error saving chat message: {str(e)}")
            raise

    def get_chat_history(self, case_id):
        """استرجاع سجل الدردشة لقضية محددة"""
        try:
            query = 'SELECT * FROM chat_messages WHERE case_id = ? ORDER BY timestamp ASC'
            results = self.execute_query(query, (case_id,))
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error fetching chat history: {str(e)}")
            raise

    def delete_case(self, case_id):
        """حذف قضية من قاعدة البيانات"""
        try:
            # حذف القضية
            query = 'DELETE FROM cases WHERE id = ?'
            self.execute_query(query, (case_id,), fetch=False)
            
            # حذف سجل المحادثة المرتبط بالقضية
            query = 'DELETE FROM chat_messages WHERE case_id = ?'
            self.execute_query(query, (case_id,), fetch=False)
            
            print(f"Case {case_id} deleted successfully")
        except Exception as e:
            print(f"Error deleting case: {str(e)}")
            raise

    def add_chat_message(self, case_id, message, response, model):
        """إضافة رسالة جديدة إلى سجل المحادثة"""
        try:
            query = '''
                INSERT INTO chat_messages (case_id, message, response, model_used, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            '''
            self.execute_query(query, (case_id, message, response, model), fetch=False)
            print(f"Chat message saved for case: {case_id}")
            return True
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return False

    def get_chat_history(self, case_id):
        """استرجاع سجل المحادثة لقضية معينة"""
        try:
            query = '''
                SELECT message, response, model_used as model, timestamp
                FROM chat_messages
                WHERE case_id = ?
                ORDER BY timestamp ASC
            '''
            results = self.execute_query(query, (case_id,))
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    def clear_chat_history(self, case_id):
        """مسح سجل المحادثة لقضية معينة"""
        try:
            query = 'DELETE FROM chat_messages WHERE case_id = ?'
            self.execute_query(query, (case_id,), fetch=False)
            print(f"Chat history cleared for case: {case_id}")
            return True
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False

# إنشاء نسخة واحدة للاستخدام
db_manager = DatabaseManager() 