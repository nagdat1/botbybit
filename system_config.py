#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات تهيئة النظام المتكامل
"""

# إعدادات عامة
SYSTEM_NAME = "Bybit Trading Bot"
VERSION = "2.0.0"
DEBUG = False

# إعدادات السيرفر
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
WEBHOOK_PATH = "/webhook"

# إعدادات التلجرام
TELEGRAM_POLLING = True  # True للتشغيل المحلي، False للويب هوك
TELEGRAM_WEBHOOK_URL = None  # سيتم تعيينه تلقائياً

# إعدادات قاعدة البيانات
DATABASE_URL = "sqlite:///trading_bot.db"
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10

# إعدادات التداول
DEFAULT_TRADE_AMOUNT = 100  # بالدولار
DEFAULT_LEVERAGE = 1
DEFAULT_MARKET_TYPE = "spot"  # spot أو futures
ALLOWED_MARKET_TYPES = ["spot", "futures"]
MAX_LEVERAGE = 100
MIN_TRADE_AMOUNT = 10

# إعدادات الأمان
MAX_LOGIN_ATTEMPTS = 3
LOGIN_TIMEOUT = 300  # بالثواني
API_RATE_LIMIT = 60  # طلب في الدقيقة
ALLOWED_IPS = []  # فارغة = السماح لجميع العناوين

# إعدادات المراقبة
MONITORING_INTERVAL = 60  # بالثواني
PRICE_UPDATE_INTERVAL = 5  # بالثواني
BALANCE_UPDATE_INTERVAL = 30  # بالثواني

# إعدادات التسجيل
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "trading_bot.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 ميجابايت
BACKUP_COUNT = 5

# إعدادات التنبيهات
ALERT_ENABLED = True
PRICE_ALERT_THRESHOLD = 0.02  # 2%
BALANCE_ALERT_THRESHOLD = 0.1  # 10%

# إعدادات الأداء
THREAD_POOL_SIZE = 4
ASYNC_WORKERS = 2
REQUEST_TIMEOUT = 30  # بالثواني

# إعدادات النسخ الاحتياطي
BACKUP_ENABLED = True
BACKUP_INTERVAL = 24 * 60 * 60  # مرة كل يوم
BACKUP_PATH = "backups"
MAX_BACKUPS = 7

# تكوينات TradingView
TRADINGVIEW = {
    "enabled": True,
    "required_fields": ["symbol", "action", "price"],
    "allowed_actions": ["buy", "sell", "close"],
    "allowed_symbols": []  # فارغة = السماح لجميع الرموز
}

# تكوينات إدارة المخاطر
RISK_MANAGEMENT = {
    "max_open_trades": 10,
    "max_daily_trades": 50,
    "max_position_size": 1000,  # بالدولار
    "stop_loss_required": True,
    "take_profit_required": False,
    "max_drawdown": 0.2,  # 20%
    "leverage_tiers": {
        "tier1": {"max_leverage": 100, "min_equity": 0},
        "tier2": {"max_leverage": 50, "min_equity": 1000},
        "tier3": {"max_leverage": 20, "min_equity": 5000}
    }
}

# تكوينات المستخدمين
USER_MANAGEMENT = {
    "require_verification": True,
    "session_timeout": 24 * 60 * 60,  # يوم واحد
    "max_accounts": 3,
    "demo_balance": 10000
}

# تكوينات النظام القديم
LEGACY_SYSTEM = {
    "enabled": True,
    "api_version": "v1",
    "compatibility_mode": True
}

# تكوينات النظام الجديد
NEW_SYSTEM = {
    "enabled": True,
    "api_version": "v2",
    "features": {
        "smart_trading": True,
        "risk_analysis": True,
        "portfolio_management": True
    }
}

# تكوينات واجهة المستخدم
UI_CONFIG = {
    "theme": "dark",
    "language": "ar",
    "timezone": "Asia/Riyadh",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "charts_enabled": True,
    "notifications_enabled": True
}

def get_system_config():
    """الحصول على تكوين النظام الكامل"""
    return {
        "system_name": SYSTEM_NAME,
        "version": VERSION,
        "debug": DEBUG,
        "server": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "webhook_path": WEBHOOK_PATH
        },
        "telegram": {
            "polling": TELEGRAM_POLLING,
            "webhook_url": TELEGRAM_WEBHOOK_URL
        },
        "database": {
            "url": DATABASE_URL,
            "pool_size": DATABASE_POOL_SIZE,
            "max_overflow": DATABASE_MAX_OVERFLOW
        },
        "trading": {
            "default_amount": DEFAULT_TRADE_AMOUNT,
            "default_leverage": DEFAULT_LEVERAGE,
            "default_market_type": DEFAULT_MARKET_TYPE,
            "allowed_market_types": ALLOWED_MARKET_TYPES,
            "max_leverage": MAX_LEVERAGE,
            "min_trade_amount": MIN_TRADE_AMOUNT
        },
        "security": {
            "max_login_attempts": MAX_LOGIN_ATTEMPTS,
            "login_timeout": LOGIN_TIMEOUT,
            "api_rate_limit": API_RATE_LIMIT,
            "allowed_ips": ALLOWED_IPS
        },
        "monitoring": {
            "interval": MONITORING_INTERVAL,
            "price_update_interval": PRICE_UPDATE_INTERVAL,
            "balance_update_interval": BALANCE_UPDATE_INTERVAL
        },
        "logging": {
            "level": LOG_LEVEL,
            "format": LOG_FORMAT,
            "file": LOG_FILE,
            "max_size": MAX_LOG_SIZE,
            "backup_count": BACKUP_COUNT
        },
        "alerts": {
            "enabled": ALERT_ENABLED,
            "price_threshold": PRICE_ALERT_THRESHOLD,
            "balance_threshold": BALANCE_ALERT_THRESHOLD
        },
        "performance": {
            "thread_pool_size": THREAD_POOL_SIZE,
            "async_workers": ASYNC_WORKERS,
            "request_timeout": REQUEST_TIMEOUT
        },
        "backup": {
            "enabled": BACKUP_ENABLED,
            "interval": BACKUP_INTERVAL,
            "path": BACKUP_PATH,
            "max_backups": MAX_BACKUPS
        },
        "tradingview": TRADINGVIEW,
        "risk_management": RISK_MANAGEMENT,
        "user_management": USER_MANAGEMENT,
        "legacy_system": LEGACY_SYSTEM,
        "new_system": NEW_SYSTEM,
        "ui": UI_CONFIG
    }