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
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw")
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', "8169000394"))

# إعدادات Bybit API
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', "osH14PNXCGzrxQLT0T")
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', "kpP2LHqNOc8Z2P1QjKB5Iw874x7Q2QXGfBHX")
BYBIT_BASE_URL = "https://api.bybit.com"

# إعدادات Webhook
# Use Railway's provided URL if available, otherwise use ngrok or localhost
RAILWAY_URL = os.getenv('RAILWAY_STATIC_URL')
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', RAILWAY_URL or RENDER_URL or "https://1557a38f4447.ngrok-free.app")
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', os.getenv('PORT', "5000")))

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

# إعدادات قاعدة البيانات (إذا كنت تريد حفظ البيانات)
DATABASE_SETTINGS = {
    'enabled': False,
    'type': 'sqlite',  # sqlite, mysql, postgresql
    'filename': 'trading_bot.db'
}