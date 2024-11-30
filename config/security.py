from functools import wraps
from flask import session, redirect, url_for
from datetime import datetime

# إعدادات الأمان
SECURITY_CONFIG = {
    'SESSION_TIMEOUT': 3600,  # مدة الجلسة بالثواني (ساعة واحدة)
    'MAX_LOGIN_ATTEMPTS': 5,  # الحد الأقصى لمحاولات تسجيل الدخول
    'PASSWORD_MIN_LENGTH': 8  # الحد الأدنى لطول كلمة المرور
}

def login_required(f):
    """مصادقة المستخدم للوصول إلى الصفحات المحمية"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if not validate_session():
            return redirect(url_for('auth.login'))
        # تحديث وقت آخر نشاط
        session['last_activity'] = datetime.now()
        return f(*args, **kwargs)
    return decorated_function

def validate_session():
    """التحقق من صلاحية الجلسة"""
    if 'last_activity' in session:
        last_activity = session['last_activity']
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        if (datetime.now() - last_activity).total_seconds() > SECURITY_CONFIG['SESSION_TIMEOUT']:
            session.clear()
            return False
    return True
