from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
import os
import arabic_reshaper
from bidi.algorithm import get_display

def generate_case_pdf(case_data):
    """إنشاء ملف PDF للقضية"""
    buffer = BytesIO()
    
    # تسجيل الخط العربي
    font_path = os.path.join(os.path.dirname(__file__), '../static/fonts/NotoNaskhArabic-Regular.ttf')
    pdfmetrics.registerFont(TTFont('Arabic', font_path))
    
    # تعريف الأنماط
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Arabic',
        fontName='Arabic',
        fontSize=12,
        leading=16,
        alignment=1,  # right alignment
        rightIndent=0,
        leftIndent=0,
        firstLineIndent=0,
        textColor=colors.black
    ))
    
    # إنشاء المستند
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # تجهيز المحتوى
    story = []
    
    # إضافة العنوان
    title = format_arabic("تحليل القضية القانونية")
    story.append(Paragraph(title, styles['Arabic']))
    story.append(Spacer(1, 20))
    
    # إضافة النص الأصلي
    story.append(Paragraph(format_arabic("النص الأصلي:"), styles['Arabic']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(format_arabic(case_data['original_text']), styles['Arabic']))
    story.append(Spacer(1, 20))
    
    # إضافة نتائج التحليل
    stage_names = ['تحليل أولي', 'تحديد الأطراف', 'تحليل الوقائع', 'التحليل القانوني', 'التوصيات']
    
    for stage_num in range(1, 6):
        stage_data = case_data['stages'].get(str(stage_num))
        if stage_data:
            # عنوان المرحلة
            stage_title = f"المرحلة {stage_num}: {stage_names[stage_num-1]}"
            story.append(Paragraph(format_arabic(stage_title), styles['Arabic']))
            story.append(Spacer(1, 10))
            
            # معلومات النموذج
            model_info = f"تم التحليل باستخدام: {stage_data['model']}"
            story.append(Paragraph(format_arabic(model_info), styles['Arabic']))
            story.append(Spacer(1, 10))
            
            # محتوى التحليل
            story.append(Paragraph(format_arabic(stage_data['content']), styles['Arabic']))
            story.append(Spacer(1, 20))
    
    # بناء المستند
    doc.build(story)
    buffer.seek(0)
    return buffer

def format_arabic(text):
    """تنسيق النص العربي للعرض الصحيح"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text 