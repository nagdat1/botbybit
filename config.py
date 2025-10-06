"""
⚙️ إعدادات البوت - Bybit Trading Bot Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 🔐 معلومات Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw")
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', "8169000394"))

# 👨‍💻 معلومات المطور Nagdat
DEVELOPER_INFO = {
    "developer_name": "Nagdat",
    "developer_id": ADMIN_USER_ID,
    "developer_secret_key": os.getenv('DEVELOPER_SECRET_KEY', "NAGDAT-KEY-2024"),
    "developer_signal_webhook": os.getenv('DEVELOPER_WEBHOOK', "https://railway.app/nagdat/signal"),
    "enable_broadcast_signals": True
}

# 🌐 إعدادات Webhook Server
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('PORT', os.getenv('WEBHOOK_PORT', '5000')))  # Railway uses PORT
BASE_WEBHOOK_URL = os.getenv('BASE_WEBHOOK_URL', os.getenv('RAILWAY_STATIC_URL', 'https://your-railway-app.railway.app'))

# 💰 إعدادات الحساب التجريبي
DEMO_INITIAL_BALANCE = 10000  # رصيد ابتدائي
DEMO_CURRENCY = "USDT"

# 📊 إعدادات التداول
TRADING_CONFIG = {
    "min_leverage": 1,
    "max_leverage": 20,
    "default_leverage": 10,
    "min_order_size": 10,  # الحد الأدنى للصفقة بالدولار
    "max_order_size": 100000,
    "default_stop_loss_percent": 2,  # 2%
    "default_take_profit_percent": 5,  # 5%
    "trailing_stop_percent": 1,  # 1%
    "partial_close_options": [25, 50, 75],  # نسب الإغلاق الجزئي
}

# 🔄 إعدادات تحديث الأسعار
PRICE_UPDATE_INTERVAL = 3  # ثواني
CACHE_DURATION = 60  # ثانية للـ Cache

# 🎨 الألوان والرموز
COLORS = {
    "green": "🟢",
    "red": "🔴",
    "yellow": "🟡",
    "blue": "🔵",
    "white": "⚪"
}

EMOJIS = {
    "rocket": "🚀",
    "chart_up": "📈",
    "chart_down": "📉",
    "money": "💰",
    "wallet": "👛",
    "signal": "⚡",
    "warning": "⚠️",
    "success": "✅",
    "error": "❌",
    "info": "ℹ️",
    "settings": "⚙️",
    "star": "⭐",
    "fire": "🔥",
    "lock": "🔒",
    "unlock": "🔓",
    "bell": "🔔",
    "muted": "🔕",
    "target": "🎯",
    "shield": "🛡️"
}

# 📁 قاعدة البيانات
DATABASE_PATH = "botbybit.db"

# 🔐 Bybit API Configuration
BYBIT_TESTNET = {
    "base_url": "https://api-testnet.bybit.com",
    "websocket": "wss://stream-testnet.bybit.com"
}

BYBIT_MAINNET = {
    "base_url": "https://api.bybit.com",
    "websocket": "wss://stream.bybit.com"
}

# 📝 الرسائل
MESSAGES = {
    "welcome": """
{rocket} مرحباً بك في بوت Bybit Trading Bot {rocket}

{star} منصة تداول احترافية متكاملة
{chart_up} دعم Spot & Futures
{shield} أدوات إدارة المخاطر المتقدمة
{signal} إشارات احترافية من Nagdat

اختر نوع الحساب للبدء:
    """,
    
    "help": """
📖 دليل الاستخدام:

1️⃣ اختر نوع الحساب (تجريبي/حقيقي)
2️⃣ ابدأ التداول مع أدوات احترافية
3️⃣ اشترك في إشارات Nagdat للحصول على توصيات
4️⃣ راقب صفقاتك المفتوحة
5️⃣ استخدم أدوات إدارة المخاطر

{warning} الحساب التجريبي: محاكاة كاملة للسوق
{fire} الحساب الحقيقي: تداول فعلي عبر Bybit API
    """,
    
    "developer_panel": """
{star} لوحة المطور - Nagdat Panel {star}

{info} عدد المشتركين: {subscribers}
{chart_up} إشارات مرسلة: {signals_sent}
{fire} البوت نشط

اختر العملية:
    """
}
