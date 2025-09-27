# -*- coding: utf-8 -*-
"""
ملف إعدادات بوت التداول على Bybit
قم بتحديث المعلومات التالية حسب حسابك
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعدادات تلغرام
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))

# إعدادات Bybit API
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')
BYBIT_BASE_URL = os.getenv('BYBIT_BASE_URL')

# إعدادات Webhook
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
# استخدام منفذ Railway إذا كان متاحاً، وإلا استخدام 5000 كافتراضي
WEBHOOK_PORT = int(os.environ.get('PORT', os.getenv('WEBHOOK_PORT', "5000")))

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
    'max_retries': 3,                    # عدد المحاولات القصوى
    'request_timeout': 10,               # مهلة الطلب بالثواني
    'rate_limit_delay': 0.1,            # تأخير بين الطلبات
}

# إعدادات التسجيل
LOGGING_SETTINGS = {
    'log_file': 'trading_bot.log',
    'log_level': 'INFO',
    'max_log_size': 10 * 1024 * 1024,   # 10 MB
    'backup_count': 5
}

// ... existing code ...
