#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أزرار البوت الكاملة - Button Definitions
يحتوي على جميع الأزرار مع callback_data والوظائف المقابلة لها
"""

from telegram import InlineKeyboardButton
from typing import Dict, List

# ===========================================
# 🏠 الأزرار الرئيسية - Main Menu Buttons
# ===========================================

def get_main_menu_buttons():
    """القائمة الرئيسية للبوت"""
    return [
        [InlineKeyboardButton("🏦 اختيار المنصة (Bybit)", callback_data="select_exchange")],
        [InlineKeyboardButton("💰 مبلغ التداول", callback_data="set_amount")],
        [InlineKeyboardButton("🏪 نوع السوق", callback_data="set_market")],
        [InlineKeyboardButton("👤 نوع الحساب", callback_data="set_account")],
        [InlineKeyboardButton("🤖 تطبيق تلقائي TP/SL", callback_data="auto_apply_menu")],
        [InlineKeyboardButton("🛡️ إدارة المخاطر", callback_data="risk_management_menu")],
        [InlineKeyboardButton("🔗 رابط الإشارات", callback_data="webhook_url")],
        [InlineKeyboardButton("▶️/⏹️ تشغيل/إيقاف البوت", callback_data="toggle_bot")]
    ]

# ===========================================
# 🏦 قسم اختيار المنصة - Exchange Selection
# ===========================================

EXCHANGE_BUTTONS = {
    "select_exchange": {
        "description": "اختيار المنصة للربط",
        "callback_data": "select_exchange",
        "text": "🏦 اختيار المنصة (Bybit)"
    },
    "link_bybit_api": {
        "description": "ربط مفاتيح Bybit API",
        "callback_data": "link_bybit_api",
        "text": "🔗 ربط Bybit API"
    },
    "bybit_test_connection": {
        "description": "اختبار اتصال Bybit",
        "callback_data": "bybit_test_connection",
        "text": "🔍 اختبار الاتصال"
    }
}

# ===========================================
# 💰 إعدادات التداول - Trading Settings
# ===========================================

TRADING_SETTINGS_BUTTONS = {
    "set_amount": {
        "description": "تعيين مبلغ التداول",
        "callback_data": "set_amount",
        "text": "💰 مبلغ التداول"
    },
    "set_market": {
        "description": "تعيين نوع السوق (Spot/Futures)",
        "callback_data": "set_market",
        "text": "🏪 نوع السوق"
    },
    "set_account": {
        "description": "تعيين نوع الحساب (Demo/Real)",
        "callback_data": "set_account",
        "text": "👤 نوع الحساب"
    },
    "set_leverage": {
        "description": "تعيين الرافعة المالية (Futures فقط)",
        "callback_data": "set_leverage",
        "text": "⚡ الرافعة المالية"
    },
    "set_demo_balance": {
        "description": "تعيين رصيد الحساب التجريبي",
        "callback_data": "set_demo_balance",
        "text": "💳 رصيد الحساب التجريبي"
    },
    "confirm_spot": {
        "description": "تأكيد اختيار Spot",
        "callback_data": "confirm_spot",
        "text": "✅ Spot"
    },
    "confirm_futures": {
        "description": "تأكيد اختيار Futures",
        "callback_data": "confirm_futures",
        "text": "✅ Futures"
    },
    "confirm_demo": {
        "description": "تأكيد اختيار الحساب التجريبي",
        "callback_data": "confirm_demo",
        "text": "✅ حساب تجريبي"
    },
    "confirm_real": {
        "description": "تأكيد اختيار الحساب الحقيقي",
        "callback_data": "confirm_real",
        "text": "✅ حساب حقيقي"
    }
}

# ===========================================
# 🤖 التطبيق التلقائي - Auto Apply Settings
# ===========================================

AUTO_APPLY_BUTTONS = {
    "auto_apply_menu": {
        "description": "قائمة التطبيق التلقائي TP/SL",
        "callback_data": "auto_apply_menu",
        "text": "🤖 تطبيق تلقائي TP/SL"
    },
    "toggle_auto_apply": {
        "description": "تفعيل/تعطيل التطبيق التلقائي",
        "callback_data": "toggle_auto_apply",
        "text": "✅/⏸️ التطبيق التلقائي"
    },
    "edit_auto_settings": {
        "description": "تعديل إعدادات التطبيق التلقائي",
        "callback_data": "edit_auto_settings",
        "text": "⚙️ تعديل الإعدادات"
    },
    "quick_auto_setup": {
        "description": "إعداد سريع للتطبيق التلقائي",
        "callback_data": "quick_auto_setup",
        "text": "🎲 إعداد سريع"
    },
    "clear_auto_settings": {
        "description": "حذف إعدادات التطبيق التلقائي",
        "callback_data": "clear_auto_settings",
        "text": "🗑️ حذف الإعدادات"
    }
}

# ===========================================
# 🎯 أهداف الربح التلقائية - Auto Take Profit
# ===========================================

AUTO_TP_BUTTONS = {
    "edit_auto_tp": {
        "description": "تعديل أهداف الربح التلقائية",
        "callback_data": "edit_auto_tp",
        "text": "🎯 تعديل أهداف الربح"
    },
    "auto_tp_targets_1": {
        "description": "إعداد هدف واحد",
        "callback_data": "auto_tp_targets_1",
        "text": "1️⃣"
    },
    "auto_tp_targets_2": {
        "description": "إعداد هدفين",
        "callback_data": "auto_tp_targets_2",
        "text": "2️⃣"
    },
    "auto_tp_targets_3": {
        "description": "إعداد ثلاثة أهداف",
        "callback_data": "auto_tp_targets_3",
        "text": "3️⃣"
    },
    "auto_tp_targets_4": {
        "description": "إعداد أربعة أهداف",
        "callback_data": "auto_tp_targets_4",
        "text": "4️⃣"
    },
    "auto_tp_targets_5": {
        "description": "إعداد خمسة أهداف",
        "callback_data": "auto_tp_targets_5",
        "text": "5️⃣"
    },
    # أزرار النسبة السريعة
    "quick_tp_1": {
        "description": "TP بنسبة 1%",
        "callback_data": "quick_tp_1",
        "text": "💰 1%"
    },
    "quick_tp_1.5": {
        "description": "TP بنسبة 1.5%",
        "callback_data": "quick_tp_1.5",
        "text": "💰 1.5%"
    },
    "quick_tp_2": {
        "description": "TP بنسبة 2%",
        "callback_data": "quick_tp_2",
        "text": "💎 2%"
    },
    "quick_tp_3": {
        "description": "TP بنسبة 3%",
        "callback_data": "quick_tp_3",
        "text": "🎯 3%"
    },
    "quick_tp_5": {
        "description": "TP بنسبة 5%",
        "callback_data": "quick_tp_5",
        "text": "🚀 5%"
    },
    "quick_tp_10": {
        "description": "TP بنسبة 10%",
        "callback_data": "quick_tp_10",
        "text": "💎 10%"
    },
    "custom_tp_percent_input": {
        "description": "إدخال نسبة مخصصة",
        "callback_data": "custom_tp_percent_input",
        "text": "✏️ إدخال رقم مخصص"
    },
    # أزرار نسبة الإغلاق
    "quick_close_25": {
        "description": "إغلاق 25%",
        "callback_data": "quick_close_25",
        "text": "📊 25%"
    },
    "quick_close_33": {
        "description": "إغلاق 33%",
        "callback_data": "quick_close_33",
        "text": "📊 33%"
    },
    "quick_close_50": {
        "description": "إغلاق 50%",
        "callback_data": "quick_close_50",
        "text": "📊 50%"
    },
    "quick_close_75": {
        "description": "إغلاق 75%",
        "callback_data": "quick_close_75",
        "text": "📊 75%"
    },
    "quick_close_100": {
        "description": "إغلاق 100%",
        "callback_data": "quick_close_100",
        "text": "✅ 100%"
    },
    "custom_close_percent_input": {
        "description": "إدخال نسبة إغلاق مخصصة",
        "callback_data": "custom_close_percent_input",
        "text": "✏️ إدخال رقم مخصص"
    }
}

# ===========================================
# 🛑 وقف الخسارة التلقائي - Auto Stop Loss
# ===========================================

AUTO_SL_BUTTONS = {
    "edit_auto_sl": {
        "description": "تعديل Stop Loss التلقائي",
        "callback_data": "edit_auto_sl",
        "text": "🛑 تعديل Stop Loss"
    },
    "quick_sl_1": {
        "description": "SL بنسبة 1%",
        "callback_data": "quick_sl_1",
        "text": "🛡️ 1%"
    },
    "quick_sl_1.5": {
        "description": "SL بنسبة 1.5%",
        "callback_data": "quick_sl_1.5",
        "text": "🛡️ 1.5%"
    },
    "quick_sl_2": {
        "description": "SL بنسبة 2%",
        "callback_data": "quick_sl_2",
        "text": "🔒 2%"
    },
    "quick_sl_2.5": {
        "description": "SL بنسبة 2.5%",
        "callback_data": "quick_sl_2.5",
        "text": "🔒 2.5%"
    },
    "quick_sl_3": {
        "description": "SL بنسبة 3%",
        "callback_data": "quick_sl_3",
        "text": "⚠️ 3%"
    },
    "quick_sl_5": {
        "description": "SL بنسبة 5%",
        "callback_data": "quick_sl_5",
        "text": "⚠️ 5%"
    },
    "custom_sl_input": {
        "description": "إدخال SL مخصص",
        "callback_data": "custom_sl_input",
        "text": "✏️ إدخال مخصص"
    }
}

# ===========================================
# ⚡ Trailing Stop - الإيقاف المتحرك
# ===========================================

TRAILING_BUTTONS = {
    "toggle_auto_trailing": {
        "description": "تفعيل/تعطيل Trailing Stop",
        "callback_data": "toggle_auto_trailing",
        "text": "⚡ تفعيل/تعطيل Trailing"
    }
}

# ===========================================
# 🛡️ إدارة المخاطر - Risk Management
# ===========================================

RISK_MANAGEMENT_BUTTONS = {
    "risk_management_menu": {
        "description": "قائمة إدارة المخاطر",
        "callback_data": "risk_management_menu",
        "text": "🛡️ إدارة المخاطر"
    },
    "toggle_risk_management": {
        "description": "تفعيل/إلغاء إدارة المخاطر",
        "callback_data": "toggle_risk_management",
        "text": "🛡️ تفعيل/إلغاء إدارة المخاطر"
    },
    "set_max_loss_percent": {
        "description": "تعديل حد الخسارة المئوي",
        "callback_data": "set_max_loss_percent",
        "text": "📉 تعديل حد الخسارة المئوي"
    },
    "set_max_loss_amount": {
        "description": "تعديل حد الخسارة بالمبلغ",
        "callback_data": "set_max_loss_amount",
        "text": "💸 تعديل حد الخسارة بالمبلغ"
    },
    "set_daily_loss_limit": {
        "description": "تعديل الحد اليومي للخسارة",
        "callback_data": "set_daily_loss_limit",
        "text": "📅 تعديل الحد اليومي"
    },
    "set_weekly_loss_limit": {
        "description": "تعديل الحد الأسبوعي للخسارة",
        "callback_data": "set_weekly_loss_limit",
        "text": "📆 تعديل الحد الأسبوعي"
    },
    "toggle_stop_trading": {
        "description": "إيقاف التداول عند الخسارة",
        "callback_data": "toggle_stop_trading",
        "text": "⏹️ إيقاف التداول عند الخسارة"
    },
    "show_risk_stats": {
        "description": "عرض إحصائيات المخاطر",
        "callback_data": "show_risk_stats",
        "text": "📊 عرض إحصائيات المخاطر"
    },
    "reset_risk_stats": {
        "description": "إعادة تعيين الإحصائيات",
        "callback_data": "reset_risk_stats",
        "text": "🔄 إعادة تعيين الإحصائيات"
    },
    "risk_management_guide": {
        "description": "شرح مفصل للخيارات",
        "callback_data": "risk_management_guide",
        "text": "📖 شرح مفصل للخيارات"
    }
}

# ===========================================
# 📊 الصفقات المفتوحة - Open Positions
# ===========================================

POSITIONS_BUTTONS = {
    "show_positions": {
        "description": "عرض الصفقات المفتوحة",
        "callback_data": "show_positions",
        "text": "📊 الصفقات المفتوحة"
    },
    "refresh_positions": {
        "description": "تحديث الصفقات المفتوحة",
        "callback_data": "refresh_positions",
        "text": "🔄 تحديث"
    },
    "manage_position": {
        "description": "إدارة صفقة محددة",
        "callback_data": "manage_{position_id}",
        "text": "⚙️ إدارة {symbol}"
    },
    "close_position": {
        "description": "إغلاق صفقة محددة",
        "callback_data": "close_{position_id}",
        "text": "❌ إغلاق"
    }
}

# ===========================================
# 🎯 إدارة الصفقات - Position Management
# ===========================================

POSITION_MANAGEMENT_BUTTONS = {
    "setTP_menu": {
        "description": "قائمة أهداف الربح",
        "callback_data": "setTP_menu_{position_id}",
        "text": "🎯 أهداف الربح"
    },
    "setSL_menu": {
        "description": "قائمة وقف الخسارة",
        "callback_data": "setSL_menu_{position_id}",
        "text": "🛑 وقف الخسارة"
    },
    "partial_custom": {
        "description": "إغلاق جزئي مخصص",
        "callback_data": "partial_custom_{position_id}",
        "text": "📊 إغلاق جزئي مخصص"
    },
    "moveBE": {
        "description": "نقل للتعادل",
        "callback_data": "moveBE_{position_id}",
        "text": "🔁 نقل للتعادل"
    },
    "trailing_menu": {
        "description": "قائمة Trailing Stop",
        "callback_data": "trailing_menu_{position_id}",
        "text": "⚡ Trailing Stop"
    },
    "quick_setup": {
        "description": "إعداد سريع ذكي",
        "callback_data": "quick_setup_{position_id}",
        "text": "🎲 إعداد سريع (ذكي)"
    },
    "tools_guide": {
        "description": "دليل الأدوات",
        "callback_data": "tools_guide_{position_id}",
        "text": "ℹ️ دليل الأدوات"
    },
    "close_full": {
        "description": "إغلاق كامل",
        "callback_data": "close_{position_id}",
        "text": "❌ إغلاق كامل"
    }
}

# ===========================================
# 🎯 أهداف الربح المخصصة (في الصفقة)
# ===========================================

CUSTOM_TP_BUTTONS = {
    "autoTP": {
        "description": "أهداف تلقائية ذكية",
        "callback_data": "autoTP_{position_id}",
        "text": "🎲 تلقائي (ذكي)"
    },
    "customTP": {
        "description": "إدخال مخصص",
        "callback_data": "customTP_{position_id}",
        "text": "✏️ إدخال مخصص"
    },
    "clearTP": {
        "description": "حذف جميع الأهداف",
        "callback_data": "clearTP_{position_id}",
        "text": "🗑️ حذف جميع الأهداف"
    }
}

# ===========================================
# 🛑 وقف الخسارة المخصص (في الصفقة)
# ===========================================

CUSTOM_SL_BUTTONS = {
    "autoSL": {
        "description": "SL تلقائي ذكي",
        "callback_data": "autoSL_{position_id}",
        "text": "🛡️ تلقائي (ذكي)"
    },
    "customSL": {
        "description": "إدخال مخصص",
        "callback_data": "customSL_{position_id}",
        "text": "✏️ إدخال مخصص"
    },
    "clearSL": {
        "description": "إلغاء SL",
        "callback_data": "clearSL_{position_id}",
        "text": "🗑️ إلغاء SL"
    }
}

# ===========================================
# 🔁 Trailing Stop (في الصفقة)
# ===========================================

CUSTOM_TRAILING_BUTTONS = {
    "enable_trailing": {
        "description": "تفعيل Trailing Stop",
        "callback_data": "enable_trailing_{position_id}",
        "text": "⚡ تفعيل Trailing"
    },
    "disable_trailing": {
        "description": "تعطيل Trailing Stop",
        "callback_data": "disable_trailing_{position_id}",
        "text": "⏸️ تعطيل Trailing"
    },
    "set_trailing_distance": {
        "description": "تعيين المسافة",
        "callback_data": "set_trailing_distance_{position_id}",
        "text": "📏 تعيين المسافة"
    }
}

# ===========================================
# 🔙 أزرار التنقل - Navigation Buttons
# ===========================================

NAVIGATION_BUTTONS = {
    "back_to_main": {
        "description": "الرجوع للقائمة الرئيسية",
        "callback_data": "back_to_main",
        "text": "🏠 الرئيسية"
    },
    "back_to_settings": {
        "description": "الرجوع للإعدادات",
        "callback_data": "back_to_settings",
        "text": "🔙 رجوع"
    },
    "back_to_auto_apply": {
        "description": "الرجوع للتطبيق التلقائي",
        "callback_data": "auto_apply_menu",
        "text": "🔙 رجوع"
    },
    "back_to_risk": {
        "description": "الرجوع لإدارة المخاطر",
        "callback_data": "risk_management_menu",
        "text": "🔙 رجوع"
    },
    "back_to_position": {
        "description": "الرجوع لإدارة الصفقة",
        "callback_data": "manage_{position_id}",
        "text": "🔙 رجوع"
    }
}

# ===========================================
# ❌ أزرار الإلغاء والحذف
# ===========================================

ACTION_BUTTONS = {
    "cancel": {
        "description": "إلغاء العملية",
        "callback_data": "cancel",
        "text": "❌ إلغاء"
    },
    "confirm": {
        "description": "تأكيد العملية",
        "callback_data": "confirm",
        "text": "✅ تأكيد"
    },
    "delete": {
        "description": "حذف",
        "callback_data": "delete",
        "text": "🗑️ حذف"
    },
    "toggle_bot": {
        "description": "تشغيل/إيقاف البوت",
        "callback_data": "toggle_bot",
        "text": "▶️/⏹️ تشغيل/إيقاف"
    }
}

# ===========================================
# 🔗 نظام المطورين - Developers System
# ===========================================

DEVELOPER_BUTTONS = {
    "developer_panel": {
        "description": "لوحة المطور",
        "callback_data": "developer_panel",
        "text": "👨‍💻 لوحة المطور"
    },
    "dev_show_followers": {
        "description": "عرض المتابعين",
        "callback_data": "dev_show_followers",
        "text": "👥 المتابعون"
    },
    "dev_stats": {
        "description": "إحصائيات المطور",
        "callback_data": "dev_stats",
        "text": "📊 الإحصائيات"
    },
    "dev_remove_follower": {
        "description": "إزالة متابع",
        "callback_data": "dev_remove_follower_{follower_id}",
        "text": "❌ إزالة"
    }
}

# ===========================================
# 🔗 رابط الإشارات
# ===========================================

WEBHOOK_BUTTONS = {
    "webhook_url": {
        "description": "عرض رابط الإشارات",
        "callback_data": "webhook_url",
        "text": "🔗 رابط الإشارات"
    },
    "info": {
        "description": "معلومات",
        "callback_data": "info",
        "text": "ℹ️ معلومات"
    },
    "link_api": {
        "description": "ربط API",
        "callback_data": "link_api",
        "text": "🔗 ربط API"
    }
}

# ===========================================
# 📋 ملخص جميع الأزرار
# ===========================================

ALL_BUTTONS = {
    **EXCHANGE_BUTTONS,
    **TRADING_SETTINGS_BUTTONS,
    **AUTO_APPLY_BUTTONS,
    **AUTO_TP_BUTTONS,
    **AUTO_SL_BUTTONS,
    **TRAILING_BUTTONS,
    **RISK_MANAGEMENT_BUTTONS,
    **POSITIONS_BUTTONS,
    **POSITION_MANAGEMENT_BUTTONS,
    **CUSTOM_TP_BUTTONS,
    **CUSTOM_SL_BUTTONS,
    **CUSTOM_TRAILING_BUTTONS,
    **NAVIGATION_BUTTONS,
    **ACTION_BUTTONS,
    **DEVELOPER_BUTTONS,
    **WEBHOOK_BUTTONS
}

# ===========================================
# 🔍 وظائف البحث والمساعدة
# ===========================================

def find_button_by_callback(callback_data: str) -> Dict:
    """البحث عن زر بواسطة callback_data"""
    for button_id, button_info in ALL_BUTTONS.items():
        if callback_data == button_info["callback_data"] or callback_data in button_info["callback_data"]:
            return button_info
    return None

def get_all_callbacks() -> List[str]:
    """الحصول على قائمة بجميع callback_data"""
    callbacks = []
    for button_info in ALL_BUTTONS.values():
        if button_info["callback_data"] not in callbacks:
            callbacks.append(button_info["callback_data"])
    return sorted(callbacks)

def get_buttons_by_category(category: str) -> Dict:
    """الحصول على أزرار حسب الفئة"""
    categories = {
        "exchange": EXCHANGE_BUTTONS,
        "trading": TRADING_SETTINGS_BUTTONS,
        "auto_apply": AUTO_APPLY_BUTTONS,
        "risk": RISK_MANAGEMENT_BUTTONS,
        "positions": POSITIONS_BUTTONS,
        "navigation": NAVIGATION_BUTTONS,
        "developers": DEVELOPER_BUTTONS
    }
    return categories.get(category.lower(), {})

