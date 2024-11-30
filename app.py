import warnings
warnings.filterwarnings("ignore", category=Warning)
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, make_response
from config.settings import APP_CONFIG
from services.analysis_service import analysis_service
from database.manager import db_manager
import json
from io import BytesIO
from services.pdf_service import generate_case_pdf
import uuid
from datetime import datetime

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.update(APP_CONFIG)

    # تهيئة قاعدة البيانات عند بدء التطبيق
    with app.app_context():
        db_manager.init_db()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/completed-cases')
    def completed_cases():
        try:
            cases = db_manager.get_all_cases()
            return render_template('cases/completed.html', cases=cases)
        except Exception as e:
            print(f"Error loading completed cases: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/analyze-stage/<int:stage>', methods=['POST'])
    async def analyze_stage(stage):
        try:
            data = request.json
            text = data.get('text')
            case_id = data.get('case_id')
            
            if not text:
                return jsonify({'error': 'لم يتم توفير نص للتحليل'}), 400

            result = await analysis_service.analyze_single_stage(text, stage)
            print(f"Analysis completed for stage {stage}")
            
            return jsonify({
                'status': 'success',
                'result': result,
                'stage': stage,
                'is_last_stage': stage == 8,
                'case_id': case_id
            })

        except Exception as e:
            print(f"Error in analyze_stage {stage}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/save-case', methods=['POST'])
    def save_case():
        try:
            data = request.json
            stages = data.get('stages', {})
            text = data.get('text')
            
            if not text:
                return jsonify({'error': 'بيانات غير مكتملة'}), 400

            # إنشاء معرف جديد للقضية
            case_id = str(uuid.uuid4())
            
            # تحضير بيانات المراحل
            formatted_stages = {}
            for stage_num, stage_data in stages.items():
                formatted_stages[stage_num] = {
                    'content': stage_data,
                    'status': 'completed',
                    'model': 'groq' if int(stage_num) in [1, 3, 5, 7] else 'gemini',
                    'timestamp': datetime.now().isoformat()
                }

            # تحضير بيانات القضية
            case_data = {
                'id': case_id,
                'title': text[:100] + '...' if len(text) > 100 else text,
                'original_text': text,
                'stages': json.dumps(formatted_stages),  # تحويل المراحل إلى JSON
                'status': 'completed',  # إضافة حالة القضية
                'date': datetime.now().isoformat()
            }

            # حفظ القضية في قاعدة البيانات
            db_manager.save_case(case_data)
            
            return jsonify({
                'status': 'success',
                'message': 'تم حفظ القضية بنجاح',
                'case_id': case_id
            })
            
        except Exception as e:
            print(f"Error saving case: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/case/<case_id>')
    def view_case(case_id):
        try:
            case = db_manager.get_case(case_id)
            if not case:
                return jsonify({'error': 'لم يتم العثور على القضية'}), 404
            
            # التأكد من أن case.stages موجود
            if not case.get('stages'):
                case['stages'] = {}
            
            # تحويل المراحل من نص JSON إلى كائن Python إذا كانت نصاً
            if isinstance(case['stages'], str):
                case['stages'] = json.loads(case['stages'])
            
            # استرجاع سجل المحادثة
            chat_history = db_manager.get_chat_history(case_id)
            case['chat_history'] = chat_history
                
            return render_template('cases/view.html', case=case)
            
        except Exception as e:
            print(f"Error viewing case: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/delete-case/<case_id>', methods=['DELETE'])
    def delete_case(case_id):
        try:
            # حذف القضية من قاعدة البيانات
            db_manager.delete_case(case_id)
            
            return jsonify({
                'status': 'success',
                'message': 'تم حذف القضية بنجاح'
            })
            
        except Exception as e:
            print(f"Error deleting case: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Chat routes
    @app.route('/chat/<case_id>')
    def chat_page(case_id):
        case = db_manager.get_case(case_id)
        if not case:
            flash('القضية غير موجودة', 'error')
            return redirect(url_for('index'))
        return render_template('chat/chat.html', case=case)

    @app.route('/api/chat', methods=['POST'])
    async def handle_chat():
        data = request.get_json()
        message = data.get('message')
        case_id = data.get('case_id')
        
        if not message or not case_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            # تحليل نوع السؤال وتوجيهه للنموذج المناسب
            response = await analysis_service.process_chat_message(message, case_id)
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chat/export/<case_id>')
    def api_export_chat(case_id):
        try:
            pdf_data = analysis_service.export_chat_to_pdf(case_id)
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=chat_export_{case_id}.pdf'
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chat/clear/<case_id>', methods=['POST'])
    def clear_chat(case_id):
        try:
            db_manager.clear_chat_history(case_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)