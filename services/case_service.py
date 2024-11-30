from datetime import datetime
import json
import os
import uuid
from sqlite3 import DatabaseError
from database.manager import db_manager

def load_cases():
    """تحميل جميع القضايا"""
    try:
        # تحقق من وجود المجلد
        cases_dir = os.path.join('cases', 'json')
        if not os.path.exists(cases_dir):
            os.makedirs(cases_dir)
            return []

        cases = []
        # قراءة جميع ملفات JSON في المجلد
        for filename in os.listdir(cases_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(cases_dir, filename), 'r', encoding='utf-8') as f:
                        case_data = json.load(f)
                        if not isinstance(case_data, dict):
                            print(f"Invalid case data format in {filename}")
                            continue
                            
                        # تأكد من وجود جميع المفاتيح المطلوبة وتعيين قيم افتراضية
                        case = {
                            'case_id': case_data.get('case_id', filename.replace('.json', '')),
                            'title': case_data.get('title', 'بدون عنوان'),
                            'date': case_data.get('date', datetime.now().isoformat()),
                            'model_name': case_data.get('model_name', 'غير محدد'),
                            'stages': case_data.get('stages', {}),
                            'status': case_data.get('status', 'in_progress'),
                            'original_text': case_data.get('original_text', '')
                        }
                        
                        # تأكد من أن stages هو قاموس
                        if not isinstance(case['stages'], dict):
                            case['stages'] = {}
                        
                        cases.append(case)
                        print(f"Loaded case: {case['case_id']} with {len(case['stages'])} stages")
                except Exception as e:
                    print(f"Error loading case file {filename}: {str(e)}")
                    continue
        
        # فلترة القضايا المكتملة فقط عند الحاجة
        completed = [case for case in cases if case.get('status') == 'completed']
        return completed
    except Exception as e:
        print(f"Error in load_cases: {str(e)}")
        return []

def load_case(case_id):
    """تحميل بيانات القضية"""
    try:
        json_path = f'cases/json/{case_id}.json'
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading case: {str(e)}")
        return None

def delete_case(case_id):
    """حذف القضية وجميع ملفاتها"""
    try:
        # حذف ملف JSON
        json_path = os.path.join('cases', 'json', f'{case_id}.json')
        if os.path.exists(json_path):
            os.remove(json_path)
            print(f"Deleted JSON file: {json_path}")

        # حذف ملف PDF إذا كان موجوداً
        pdf_path = os.path.join('cases', 'pdf', f'{case_id}.pdf')
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Deleted PDF file: {pdf_path}")

        # حذف من قاعدة البيانات
        db_manager.execute_query(
            'DELETE FROM case_updates WHERE case_id = ?', 
            (case_id,), 
            fetch=False
        )
        db_manager.execute_query(
            'DELETE FROM cases WHERE id = ?', 
            (case_id,), 
            fetch=False
        )
        
        print(f"Successfully deleted case: {case_id}")
        return True
        
    except Exception as e:
        print(f"Error deleting case {case_id}: {str(e)}")
        return False

def get_case_updates(case_id):
    try:
        query = 'SELECT * FROM case_updates WHERE case_id = ? ORDER BY date DESC'
        cursor = db_manager.execute_query(query, (case_id,))
        updates = []
        for row in cursor.fetchall():
            update = {
                'id': row['id'],
                'case_id': row['case_id'],
                'date': row['date'],
                'update_type': row['update_type'],
                'content': row['content'],
                'analysis': row['analysis'],
                'attachments': json.loads(row['attachments']) if row['attachments'] else [],
                'status': row['status']
            }
            updates.append(update)
        return updates
    except Exception as e:
        print(f"خطأ في جلب المستجدات: {str(e)}")
        return []

def save_case_update(update_data):
    try:
        update_id = str(uuid.uuid4())
        query = '''
            INSERT INTO case_updates 
            (id, case_id, date, update_type, content, analysis, attachments, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        db_manager.execute_insert(query, (
            update_id,
            update_data['case_id'],
            datetime.now().isoformat(),
            update_data['update_type'],
            update_data['content'],
            update_data.get('analysis', ''),
            json.dumps(update_data.get('attachments', [])),
            'new'
        ))
        
        return True
        
    except Exception as e:
        print(f"Error saving case update: {str(e)}")
        return False

def save_case(case_data):
    """حفظ القضية في ملف JSON"""
    try:
        case_id = case_data.get('case_id')
        if not case_id:
            case_id = str(uuid.uuid4())
            case_data['case_id'] = case_id

        # تنظيم بيانات القضية
        formatted_case = {
            'case_id': case_id,
            'title': case_data.get('title', 'بدون عنوان'),
            'date': case_data.get('date', datetime.now().isoformat()),
            'model_name': case_data.get('model_name', 'غير محدد'),
            'status': case_data.get('status', 'in_progress'),
            'original_text': case_data.get('original_text', ''),
            'stages': {}
        }

        # إضافة المراحل
        if 'stages' in case_data:
            for stage_num, stage_data in case_data['stages'].items():
                formatted_case['stages'][str(stage_num)] = {
                    'content': stage_data.get('content', ''),
                    'model': stage_data.get('model', ''),
                    'timestamp': stage_data.get('timestamp', datetime.now().isoformat())
                }

        # إنشاء المجلد إذا لم يكن موجوداً
        cases_dir = os.path.join('cases', 'json')
        os.makedirs(cases_dir, exist_ok=True)

        # حفظ الملف
        json_path = os.path.join(cases_dir, f'{case_id}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_case, f, ensure_ascii=False, indent=2)
            print(f"Saved case: {case_id} with {len(formatted_case['stages'])} stages")

        return case_id
    except Exception as e:
        print(f"Error saving case: {str(e)}")
        raise