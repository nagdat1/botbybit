# -*- coding: utf-8 -*-
"""
ملف إعدادات بوت التداول على Bybit
قم بتحديث المعلومات التالية حسب حسابك
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# التحقق من وجود المتغيرات المطلوبة
def get_required_env(key: str) -> str:
    """الحصول على متغير بيئة مطلوب"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

# إعدادات تلغرام
TELEGRAM_TOKEN = get_required_env('TELEGRAM_TOKEN')
ADMIN_USER_ID = int(get_required_env('ADMIN_USER_ID'))

# إعدادات Bybit API
BYBIT_API_KEY = get_required_env('BYBIT_API_KEY')
BYBIT_API_SECRET = get_required_env('BYBIT_API_SECRET')
BYBIT_BASE_URL = "https://api.bybit.com"  # لا حاجة لتغييره عادةً

# إعدادات Webhook للـ Railway
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
RAILWAY_PORT = int(os.getenv('PORT', '8080'))

# إعداد عنوان الويب هوك
def get_webhook_url():
    """تحديد عنوان الويب هوك بناءً على بيئة التشغيل"""
    if RAILWAY_STATIC_URL:
        return f"https://{RAILWAY_STATIC_URL}"
    return os.getenv('WEBHOOK_URL', 'http://localhost:8080')

# إعدادات افتراضية للبوت
DEFAULT_SETTINGS = {
    'account_type': 'demo',          # demo أو real
    'market_type': 'spot',           # spot أو futures
    'trade_amount': 100.0,           # مبلغ التداول الافتراضي
    'leverage': 10,                  # الرافعة المالية للفيوتشر
    'profit_plan': 'trailing',       # trailing أو multi_tp
    'trailing_stop_percent': 0.5,    # نسبة التوقف المتحرك
    'tp1_percent': 1.5,              # هدف الربح الأول
    'tp2_percent': 3.0,              # هدف الربح الثاني
    'tp3_percent': 6.0,              # هدف الربح الثالث
    'stop_loss_percent': 2.0,        # نسبة وقف الخسارة
    'language': 'ar'                 # اللغة
}

# إعدادات الحساب التجريبي الداخلي
DEMO_ACCOUNT_SETTINGS = {
    'initial_balance_spot': 10000.0,     # الرصيد الأولي للسبوت
    'initial_balance_futures': 10000.0,  # الرصيد الأولي للفيوتشر
}

# إعدادات الأمان
SECURITY_SETTINGS = {
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),        # عدد المحاولات القصوى
    'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '10')), # مهلة الطلب بالثواني
    'rate_limit_delay': float(os.getenv('RATE_LIMIT_DELAY', '0.1')), # تأخير بين الطلبات
}

# إعدادات التسجيل
LOGGING_SETTINGS = {
    'log_file': None,  # استخدام stdout في Railway
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# إعدادات Railway
RAILWAY_CONFIG = {
    'environment': os.getenv('RAILWAY_ENVIRONMENT', 'production'),
    'project_id': os.getenv('RAILWAY_PROJECT_ID', ''),
    'service_name': os.getenv('RAILWAY_SERVICE_NAME', ''),
}

# رسائل البوت
MESSAGES = {
    'welcome': """
🤖 مرحباً بك في بوت التداول على Bybit

🔧 الميزات المتاحة:
• التداول الحقيقي والتجريبي الداخلي
• دعم أسواق Spot و Futures
• استقبال إشارات من TradingView
• خطط جني الأرباح المتقدمة
• إدارة المخاطر

استخدم الأزرار أدناه للتنقل في البوت
    """,
    
    'bot_started': "✅ تم تشغيل البوت، سيتم معالجة الإشارات الواردة",
    'bot_stopped': "⏹️ تم إيقاف البوت، لن يتم معالجة الإشارات الجديدة",
    'symbol_not_found': "❌ الرمز {} غير موجود في منصة Bybit",
    'insufficient_balance': "❌ الرصيد غير كافي لفتح الصفقة",
    'trade_success': "✅ تم تنفيذ الصفقة بنجاح",
    'trade_failed': "❌ فشل في تنفيذ الصفقة: {}",
    'no_open_positions': "📭 لا توجد صفقات مفتوحة حالياً",
    'position_closed': "✅ تم إغلاق الصفقة بنجاح",
    'unauthorized': "غير مصرح لك باستخدام هذا البوت"
}

# إعدادات قاعدة البيانات
DATABASE_SETTINGS = {
    'enabled': os.getenv('DB_ENABLED', 'false').lower() == 'true',
    'type': os.getenv('DB_TYPE', 'sqlite'),
    'url': os.getenv('DATABASE_URL', ''),  # Railway يوفر هذا المتغير تلقائياً
    'filename': os.getenv('DB_FILENAME', 'trading_bot.db')  # يستخدم فقط مع sqlite
}