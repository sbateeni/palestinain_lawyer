from pathlib import Path
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# المسارات الأساسية
BASE_DIR = Path(__file__).parent.parent
CASES_DIR = BASE_DIR / 'cases'

# إنشاء المجلدات المطلوبة
CASES_DIR.mkdir(exist_ok=True)
(CASES_DIR / 'attachments').mkdir(exist_ok=True)
(CASES_DIR / 'json').mkdir(exist_ok=True)
(CASES_DIR / 'pdf').mkdir(exist_ok=True)

# إعدادات التطبيق
APP_CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'your-secret-key'),
    'DATABASE_PATH': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'cases.db'),
    'CASES_PATH': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cases'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB max-limit
}

# إعدادات النماذج والمراحل
MODEL_CONFIG = {
    'GROQ_STAGES': [1, 3, 5, 7],    # المراحل التي يحللها Groq
    'GEMINI_STAGES': [2, 4, 6, 8]   # المراحل التي يحللها Gemini
}

# أسماء المراحل
STAGE_NAMES = [
    'التحليل الأولي وفق القانون الفلسطيني',
    'تحديد الأطراف والصفة القانونية',
    'تحليل الوقائع والأدلة',
    'التحليل وفق التشريعات الفلسطينية',
    'التوصيات والإجراءات القانونية',
    'السوابق القضائية الفلسطينية',
    'تحليل المخاطر والتكاليف',
    'الحلول البديلة المتاحة قانوناً'
]

# وصف المراحل
STAGE_DESCRIPTIONS = {
    1: 'تحليل القضية وفقاً للقانون الفلسطيني وتحديد المحكمة المختصة',
    2: 'تحديد الأطراف وصفاتهم القانونية وفقاً للقانون الفلسطيني',
    3: 'تحليل الوقائع والأدلة وفقاً لقانون البينات الفلسطيني',
    4: 'التحليل وفقاً للتشريعات والقوانين الفلسطينية',
    5: 'التوصيات والإجراءات وفقاً لقانون أصول المحاكمات',
    6: 'تحليل السوابق القضائية من المحاكم الفلسطينية',
    7: 'تحليل المخاطر والتكاليف في النظام القضائي الفلسطيني',
    8: 'الحلول البديلة المتاحة وفقاً للقانون الفلسطيني'
}

# أيقونات المراحل
STAGE_ICONS = [
    'search',           # تحليل أولي
    'users',           # تحديد الأطراف
    'file-alt',        # تحليل الوقائع
    'balance-scale',   # التحليل القانوني
    'check',           # التوصيات
    'gavel',           # السوابق القضائية
    'chart-line',      # تحليل المخاطر
    'lightbulb'        # البدائل والحلول
]

# إعدادات التحليل
ANALYSIS_CONFIG = {
    'DELAY_BETWEEN_STAGES': 2000,  # التأخير بين المراحل (بالميلي ثانية)
    'MAX_TOKENS': 4000,
    'TEMPERATURE': 0.7
}

# التحقق من المتغيرات المطلوبة
def validate_config():
    required_vars = ['GROQ_API_KEY']
    missing_vars = [var for var in required_vars if not MODEL_CONFIG.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 