import os
import google.generativeai as genai
from config.settings import APP_CONFIG

class BotService:
    def __init__(self):
        genai.configure(api_key=APP_CONFIG['GOOGLE_API_KEY'])
        self.model = genai.GenerativeModel('gemini-pro')
        
    def analyze_text(self, text, model='gemini', model_version=None):
        """تحليل النص باستخدام نموذج الذكاء الاصطناعي"""
        try:
            prompt = f"""
            قم بتحليل النص التالي من منظور قانوني:
            
            {text}
            
            قم بتقديم:
            1. ملخص للقضية
            2. النقاط القانونية الرئيسية
            3. التوصيات والإجراءات المقترحة
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error in analyze_text: {str(e)}")
            raise e