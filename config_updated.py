#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف إعدادات شامل ومحدث للبوت
يحتوي على جميع الإعدادات المطلوبة للتشغيل الصحيح
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# ========================================
# إعدادات تلغرام
# ========================================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw")
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', "8169000394"))

# ========================================
# إعدادات Bybit API - المفاتيح الجديدة المختبرة
# ========================================
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', "RKk6fTapgDqys6vt5S")
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp")
BYBIT_BASE_URL = "https://api.bybit.com"

# ========================================
# إعدادات MEXC API
# ========================================
MEXC_API_KEY = os.getenv('MEXC_API_KEY', "")
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', "")
MEXC_BASE_URL = "https://api.mexc.com"

# ========================================
# إعدادات Webhook
# ========================================
RAILWAY_URL = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL')
PORT = int(os.getenv('PORT', '5000'))

if RAILWAY_URL:
    if not RAILWAY_URL.startswith('http'):
        RAILWAY_URL = f"https://{RAILWAY_URL}"
    WEBHOOK_URL = f"{RAILWAY_URL}/webhook"
elif RENDER_URL:
    WEBHOOK_URL = f"{RENDER_URL}/webhook"
else:
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', f"http://localhost:{PORT}/webhook")

WEBHOOK_PORT = PORT

# ========================================
# إعدادات افتراضية للبوت - محدثة ومحسنة
# ========================================
DEFAULT_SETTINGS = {
    'account_type': 'real',          # demo أو real - تم تغييره إلى real
    'market_type': 'futures',        # spot أو futures - تم تغييره إلى futures
    'exchange': 'bybit',             # bybit أو mexc
    'trade_amount': 50.0,            # مبلغ التداول الافتراضي - تم تقليله
    'leverage': 2,                   # الرافعة المالية للفيوتشر - تم تقليلها
    'profit_plan': 'trailing',       # trailing أو multi_tp
    'trailing_stop_percent': 0.5,    # نسبة التوقف المتحرك
    'tp1_percent': 1.5,              # هدف الربح الأول
    'tp2_percent': 3.0,              # هدف الربح الثاني
    'tp3_percent': 6.0,              # هدف الربح الثالث
    'stop_loss_percent': 2.0,        # نسبة وقف الخسارة
    'language': 'ar',                # اللغة
    'min_quantity': 0.001,           # الكمية الدنيا للصفقات (BTC)
    'auto_trade': True,              # التداول التلقائي
    'notifications': True            # الإشعارات
}

# ========================================
# إعدادات الحساب التجريبي الداخلي
# ========================================
DEMO_ACCOUNT_SETTINGS = {
    'initial_balance_spot': 10000.0,     # الرصيد الأولي للسبوت
    'initial_balance_futures': 10000.0,  # الرصيد الأولي للفيوتشر
}

# ========================================
# إعدادات الأمان والأداء
# ========================================
SECURITY_SETTINGS = {
    'max_retries': 3,                    # عدد المحاولات القصوى
    'request_timeout': 10,               # مهلة الطلب بالثواني
    'rate_limit_delay': 0.1,            # تأخير بين الطلبات
    'max_daily_trades': 50,              # الحد الأقصى للصفقات اليومية
    'max_position_size': 1000.0,         # الحد الأقصى لحجم الصفقة
}

# ========================================
# إعدادات التسجيل
# ========================================
LOGGING_SETTINGS = {
    'log_file': 'trading_bot.log',
    'log_level': 'INFO',
    'max_log_size': 10 * 1024 * 1024,   # 10 MB
    'backup_count': 5,
    'console_output': True               # إخراج السجلات في الكونسول
}

# ========================================
# رسائل البوت المحدثة
# ========================================
MESSAGES = {
    'welcome': """
🤖 مرحباً بك في بوت التداول على Bybit

الميزات المتاحة:
• التداول الحقيقي والتجريبي الداخلي
• دعم أسواق Spot و Futures
• استقبال إشارات من TradingView
• خطط جني الأرباح المتقدمة
• إدارة المخاطر الذكية
• ربط API Keys من الإعدادات

استخدم الأزرار أدناه للتنقل في البوت
    """,
    
    'bot_started': "✅ تم تشغيل البوت، سيتم معالجة الإشارات الواردة",
    'bot_stopped': "⏹️ تم إيقاف البوت، لن يتم معالجة الإشارات الجديدة",
    'symbol_not_found': "❌ الرمز {} غير موجود في منصة Bybit",
    'insufficient_balance': "💰 الرصيد غير كافي لفتح الصفقة",
    'trade_success': "✅ تم تنفيذ الصفقة بنجاح",
    'trade_failed': "❌ فشل في تنفيذ الصفقة: {}",
    'no_open_positions': "📭 لا توجد صفقات مفتوحة حالياً",
    'position_closed': "✅ تم إغلاق الصفقة بنجاح",
    'unauthorized': "🚫 غير مصرح لك باستخدام هذا البوت",
    'api_linked': "🔗 تم ربط API بنجاح",
    'api_unlinked': "🔓 تم إلغاء ربط API",
    'settings_updated': "⚙️ تم تحديث الإعدادات بنجاح"
}

# ========================================
# إعدادات قاعدة البيانات
# ========================================
DATABASE_SETTINGS = {
    'enabled': True,
    'type': 'sqlite',
    'filename': 'trading_bot.db',
    'backup_enabled': True,
    'backup_interval': 24  # ساعات
}

# ========================================
# إعدادات التداول المتقدمة
# ========================================
TRADING_SETTINGS = {
    'supported_symbols': [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
        'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT'
    ],
    'min_trade_amount': 10.0,           # الحد الأدنى لمبلغ التداول
    'max_trade_amount': 10000.0,         # الحد الأقصى لمبلغ التداول
    'default_leverage': 2,               # الرافعة الافتراضية
    'max_leverage': 10,                  # الحد الأقصى للرافعة
    'slippage_tolerance': 0.5,          # تحمل الانزلاق (%)
}

# ========================================
# إعدادات الإشعارات
# ========================================
NOTIFICATION_SETTINGS = {
    'trade_notifications': True,         # إشعارات الصفقات
    'error_notifications': True,         # إشعارات الأخطاء
    'balance_notifications': True,      # إشعارات الرصيد
    'daily_summary': True,              # ملخص يومي
    'weekly_summary': True              # ملخص أسبوعي
}

# ========================================
# إعدادات التطوير
# ========================================
DEVELOPMENT_SETTINGS = {
    'debug_mode': False,                # وضع التطوير
    'test_mode': False,                 # وضع الاختبار
    'mock_trades': False,               # محاكاة الصفقات
    'verbose_logging': False            # تسجيل مفصل
}

# ========================================
# معلومات الإصدار
# ========================================
VERSION_INFO = {
    'version': '2.0.0',
    'build_date': '2025-01-25',
    'author': 'Trading Bot Team',
    'description': 'Bybit Trading Bot with Enhanced Features'
}

print(f"تم تحميل إعدادات البوت - الإصدار {VERSION_INFO['version']}")
print(f"Bybit API Key: {BYBIT_API_KEY[:10]}...")
print(f"Telegram Token: {TELEGRAM_TOKEN[:10]}...")
print(f"الإعدادات الافتراضية: {DEFAULT_SETTINGS['account_type']} - {DEFAULT_SETTINGS['market_type']}")
