import os
from groq import Groq
import google.generativeai as genai
from config.settings import APP_CONFIG, MODEL_CONFIG
from datetime import datetime
import json
from database.manager import db_manager

class AnalysisService:
    def __init__(self):
        # تهيئة النماذج
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # تحديد المراحل لكل نموذج
        self.model_stages = MODEL_CONFIG

    async def analyze_single_stage(self, text, stage):
        """تحليل مرحلة واحدة"""
        try:
            print(f"Starting analysis for stage {stage}")
            
            # تحديد النموذج المناسب للمرحلة
            if stage in self.model_stages['GROQ_STAGES']:
                result = await self.analyze_stage_groq(text, stage)
                print(f"Using Groq for stage {stage}")
            else:
                result = await self.analyze_stage_gemini(text, stage)
                print(f"Using Gemini for stage {stage}")
            
            print(f"Completed analysis for stage {stage}")
            return result

        except Exception as e:
            print(f"Error in analyze_single_stage: {str(e)}")
            raise

    async def analyze_stage_groq(self, text, stage):
        """تحليل باستخدام نموذج Groq للمراحل 1,3,5"""
        try:
            prompt = self._get_stage_prompt(text, stage)
            completion = self.groq_client.chat.completions.create(
                model='llama3-groq-70b-8192-tool-use-preview',
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
                top_p=1,
                stream=False
            )
            
            content = completion.choices[0].message.content
            return {
                'content': content,
                'model': 'Groq-Llama3',
                'stage': stage,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error in analyze_stage_groq: {str(e)}")
            raise

    async def analyze_stage_gemini(self, text, stage):
        """تحليل باستخدام نموذج Gemini للمراحل 2,4"""
        try:
            prompt = self._get_stage_prompt(text, stage)
            response = self.gemini_model.generate_content(prompt)
            
            return {
                'content': response.text,
                'model': 'Gemini-Pro',
                'stage': stage,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error in analyze_stage_gemini: {str(e)}")
            raise

    def _get_stage_prompt(self, text, stage):
        """تحضير النص للتحليل حسب المرحلة مع التركيز على القانون الفلسطيني"""
        prompts = {
            1: f"""قم بتحليل أولي للقضية التالية وفقاً للقانون الفلسطيني:
{text}

قم بتحديد:
1. نوع القضية وتصنيفها القانوني
2. المحكمة المختصة (صلح، بداية، استئناف)
3. القيمة المالية للدعوى إن وجدت
4. الإطار القانوني العام للقضية في القانون الفلسطيني""",

            2: f"""حدد الأطراف المشاركة في القضية التالية:
{text}

لكل طرف حدد:
1. صفته القانونية في الدعوى
2. أهليته القانونية وفقاً للقانون الفلسطيني
3. حقوقه والتزاماته القانونية
4. مصلحته في الدعوى حسب قانون أصول المحاكمات المدنية والتجارية الفلسطيني""",

            3: f"""قم بتحليل وقائع القضية التالية وفقاً للقانون الفلسطيني:
{text}

قم بتحديد:
1. الوقائع المادية المؤثرة قانوناً
2. التسلسل الزمني للأحداث
3. الأدلة والمستندات المتوفرة ومدى حجيتها وفقاً لقانون البينات الفلسطيني
4. الإجراءات القانونية السابقة إن وجدت""",

            4: f"""قم بالتحليل القانوني للقضية وفقاً للقوانين الفلسطينية:
{text}

حدد:
1. النصوص القانونية المنطبقة من القوانين الفلسطينية
2. مواد مجلة الأحكام العدلية ذات الصلة
3. القرارات والمراسيم الرئاسية المتعلقة
4. الاجتهادات القضائية لمحكمة النقض الفلسطينية""",

            5: f"""قدم توصيات وحلول للقضية وفقاً للقانون الفلسطيني:
{text}

اقترح:
1. الإجراءات القانونية الواجب اتباعها حسب قانون أصول المحاكمات
2. الطلبات التي يجب تضمينها في لائحة الدعوى
3. الأدلة المطلوب تقديمها وفقاً لقانون البينات
4. الإجراءات التحفظية الممكنة""",

            6: f"""ابحث عن السوابق القضائية الفلسطينية المشابهة للقضية التالية:
{text}

حدد:
1. قرارات محكمة النقض الفلسطينية المشابهة
2. المبادئ القانونية المستقرة في القضاء الفلسطيني
3. التوجهات القضائية في المحاكم الفلسطينية
4. التطبيقات العملية للنصوص القانونية""",

            7: f"""قم بتحليل المخاطر القانونية للقضية وفقاً للقانون الفلسطيني:
{text}

حدد:
1. احتمالات نجاح الدعوى في المحاكم الفلسطينية
2. المدة المتوقعة للتقاضي في المحاكم الفلسطينية
3. التكاليف المتوقعة (رسوم، أتعاب، مصاريف)
4. العقبات الإجرائية المحتملة""",

            8: f"""اقترح بدائل وحلول للنزاع وفقاً للقانون الفلسطيني:
{text}

اقترح:
1. إمكانية الصلح والتسوية الودية
2. الوساطة القضائية وفقاً للقانون الفلسطيني
3. التحكيم وفقاً لقانون التحكيم الفلسطيني
4. الحلول البديلة المتاحة قانوناً"""
        }
        return prompts.get(stage, "")

    async def process_chat_message(self, message, case_id):
        """معالجة رسالة الدردشة وتوجيهها للنموذج المناسب"""
        try:
            # استرجاع بيانات القضية
            case = db_manager.get_case(case_id)
            if not case:
                raise Exception("لم يتم العثور على القضية")

            # تحليل نوع السؤال
            question_type = self._analyze_question_type(message)
            
            # اختيار النموذج المناسب وإنشاء الإجابة
            if question_type in ['تحليل', 'تفسير', 'شرح']:
                response = await self._process_with_groq(message, case)
                model = 'groq'
            else:
                response = await self._process_with_gemini(message, case)
                model = 'gemini'

            return {
                'response': response,
                'model': model
            }

        except Exception as e:
            print(f"Error processing chat message: {str(e)}")
            raise

    def _analyze_question_type(self, message):
        """تحليل نوع السؤال"""
        analysis_keywords = ['تحليل', 'تفسير', 'شرح', 'توضيح', 'لماذا', 'كيف']
        factual_keywords = ['متى', 'أين', 'من', 'ما هو', 'هل', 'كم']
        
        message_lower = message.lower()
        
        for keyword in analysis_keywords:
            if keyword in message_lower:
                return 'تحليل'
                
        for keyword in factual_keywords:
            if keyword in message_lower:
                return 'واقعي'
                
        return 'عام'

    async def _process_with_groq(self, message, case):
        """معالجة السؤال باستخدام نموذج Groq"""
        try:
            prompt = f"""
            بناءً على القضية التالية:
            {case['original_text']}

            والتحليل السابق:
            {json.dumps(case['stages'], ensure_ascii=False)}

            الرجاء الإجابة على السؤال التالي:
            {message}

            قدم إجابة مفصلة ومدعمة بالأسباب والتحليل القانوني.
            """

            completion = self.groq_client.chat.completions.create(
                model='llama3-groq-70b-8192-tool-use-preview',
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            return completion.choices[0].message.content

        except Exception as e:
            print(f"Error in _process_with_groq: {str(e)}")
            raise

    async def _process_with_gemini(self, message, case):
        """معالجة السؤال باستخدام نموذج Gemini"""
        try:
            prompt = f"""
            بناءً على القضية التالية:
            {case['original_text']}

            والتحليل السابق:
            {json.dumps(case['stages'], ensure_ascii=False)}

            الرجاء الإجابة على السؤال التالي:
            {message}

            قدم إجابة موجزة وواضحة تركز على الحقائق والمعلومات المباشرة.
            """

            response = self.gemini_model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Error in _process_with_gemini: {str(e)}")
            raise

    def export_chat_to_pdf(self, case_id):
        """تصدير سجل المحادثة إلى ملف PDF"""
        try:
            # استرجاع بيانات القضية والمحادثة
            case = db_manager.get_case(case_id)
            chat_history = db_manager.get_chat_history(case_id)
            
            if not case or not chat_history:
                raise Exception("لم يتم العثور على القضية أو سجل المحادثة")

            # إنشاء محتوى PDF
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from io import BytesIO
            
            # إنشاء buffer للـ PDF
            buffer = BytesIO()
            
            # إنشاء المستند
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            story = []
            
            # تعريف الأنماط
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # center
            )
            
            # إضافة العنوان
            story.append(Paragraph(f"سجل المحادثة - {case['title']}", title_style))
            story.append(Spacer(1, 12))
            
            # إضافة المحادثة
            for msg in chat_history:
                # رسالة المستخدم
                story.append(Paragraph(f"السؤال: {msg['message']}", styles['Normal']))
                story.append(Spacer(1, 6))
                
                # رسالة النظام
                story.append(Paragraph(f"الإجابة ({msg['model']}): {msg['response']}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # إنشاء PDF
            doc.build(story)
            
            # إرجاع البيانات
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data

        except Exception as e:
            print(f"Error exporting chat to PDF: {str(e)}")
            raise

# إنشاء نسخة واحدة للاستخدام
analysis_service = AnalysisService() 