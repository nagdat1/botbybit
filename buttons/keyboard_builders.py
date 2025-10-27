#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyboard Builders - مولدات لوحات المفاتيح
دوال لإنشاء جميع keyboards في البوت
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .buttons_definition import *

# ===========================================
# 🏠 القوائم الرئيسية
# ===========================================

def build_settings_menu(market_type: str = 'spot', account_type: str = 'demo', auto_status: str = "⏸️"):
    """بناء قائمة الإعدادات"""
    keyboard = [
        [InlineKeyboardButton("🏦 اختيار المنصة (Bybit)", callback_data="select_exchange")],
        [InlineKeyboardButton("💰 مبلغ التداول", callback_data="set_amount")],
        [InlineKeyboardButton("🏪 نوع السوق", callback_data="set_market")],
        [InlineKeyboardButton("👤 نوع الحساب", callback_data="set_account")]
    ]
    
    # إضافة زر الرافعة المالية فقط إذا كان السوق Futures
    if market_type == 'futures':
        keyboard.append([InlineKeyboardButton("⚡ الرافعة المالية", callback_data="set_leverage")])
    
    # إضافة زر رصيد الحساب التجريبي فقط إذا كان نوع الحساب تجريبي
    if account_type == 'demo':
        keyboard.append([InlineKeyboardButton("💳 رصيد الحساب التجريبي", callback_data="set_demo_balance")])
    
    # إضافة باقي الأزرار
    keyboard.extend([
        [InlineKeyboardButton(f"🤖 تطبيق تلقائي TP/SL {auto_status}", callback_data="auto_apply_menu")],
        [InlineKeyboardButton("🛡️ إدارة المخاطر", callback_data="risk_management_menu")],
        [InlineKeyboardButton("🔗 رابط الإشارات", callback_data="webhook_url")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_main_navigation():
    """بناء أزرار التنقل الرئيسية"""
    return [
        InlineKeyboardButton("🏠 الرئيسية", callback_data="settings"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")
    ]

# ===========================================
# 🏦 أزرار اختيار المنصة
# ===========================================

def build_exchange_menu(bybit_linked: bool = False, current_exchange: str = ''):
    """بناء قائمة اختيار المنصة"""
    bybit_icon = "✅" if (current_exchange == 'bybit' and bybit_linked) else ("🔗" if bybit_linked else "⚪")
    
    keyboard = [
        [InlineKeyboardButton(f"{bybit_icon} Bybit", callback_data="exchange_select_bybit")],
        [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_bybit_options(has_keys: bool):
    """بناء خيارات Bybit"""
    keyboard = [
        [InlineKeyboardButton("🔑 ربط/تحديث Bybit API Keys", callback_data="exchange_setup_bybit")]
    ]
    
    if has_keys:
        keyboard.extend([
            [InlineKeyboardButton("✅ استخدام Bybit", callback_data="exchange_activate_bybit")],
            [InlineKeyboardButton("📊 اختبار الاتصال بـ Bybit", callback_data="exchange_test_bybit")]
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="exchange_menu")])
    
    return InlineKeyboardMarkup(keyboard)

# ===========================================
# 🤖 أزرار التطبيق التلقائي
# ===========================================

def build_auto_apply_menu(auto_enabled: bool):
    """بناء قائمة التطبيق التلقائي"""
    status_button = "⏸️ تعطيل" if auto_enabled else "✅ تفعيل"
    
    keyboard = [
        [InlineKeyboardButton(f"{status_button} التطبيق التلقائي", callback_data="toggle_auto_apply")],
        [InlineKeyboardButton("⚙️ تعديل الإعدادات", callback_data="edit_auto_settings")],
        [InlineKeyboardButton("🎲 إعداد سريع", callback_data="quick_auto_setup")],
        [InlineKeyboardButton("🗑️ حذف الإعدادات", callback_data="clear_auto_settings")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_auto_tp_menu():
    """بناء قائمة أهداف الربح التلقائية"""
    keyboard = [
        [InlineKeyboardButton("🎯 تعديل أهداف الربح", callback_data="edit_auto_tp")],
        [InlineKeyboardButton("🛑 تعديل Stop Loss", callback_data="edit_auto_sl")],
        [InlineKeyboardButton("⚡ تفعيل/تعطيل Trailing", callback_data="toggle_auto_trailing")],
        [InlineKeyboardButton("🎲 إعداد سريع", callback_data="quick_auto_setup")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_tp_targets_selection():
    """بناء قائمة اختيار عدد أهداف الربح"""
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data="auto_tp_targets_1"),
            InlineKeyboardButton("2️⃣", callback_data="auto_tp_targets_2"),
            InlineKeyboardButton("3️⃣", callback_data="auto_tp_targets_3")
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data="auto_tp_targets_4"),
            InlineKeyboardButton("5️⃣", callback_data="auto_tp_targets_5")
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_quick_tp_percentages():
    """بناء قائمة نسبة TP السريعة"""
    keyboard = [
        [
            InlineKeyboardButton("💰 1%", callback_data="quick_tp_1"),
            InlineKeyboardButton("💰 1.5%", callback_data="quick_tp_1.5"),
            InlineKeyboardButton("💎 2%", callback_data="quick_tp_2")
        ],
        [
            InlineKeyboardButton("🎯 3%", callback_data="quick_tp_3"),
            InlineKeyboardButton("🚀 5%", callback_data="quick_tp_5"),
            InlineKeyboardButton("💎 10%", callback_data="quick_tp_10")
        ],
        [InlineKeyboardButton("✏️ إدخال رقم مخصص", callback_data="custom_tp_percent_input")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_quick_close_percentages():
    """بناء قائمة نسبة الإغلاق السريعة"""
    keyboard = [
        [
            InlineKeyboardButton("📊 25%", callback_data="quick_close_25"),
            InlineKeyboardButton("📊 33%", callback_data="quick_close_33"),
            InlineKeyboardButton("📊 50%", callback_data="quick_close_50")
        ],
        [
            InlineKeyboardButton("📊 75%", callback_data="quick_close_75"),
            InlineKeyboardButton("✅ 100%", callback_data="quick_close_100")
        ],
        [InlineKeyboardButton("✏️ إدخال رقم مخصص", callback_data="custom_close_percent_input")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_quick_sl_percentages():
    """بناء قائمة نسبة SL السريعة"""
    keyboard = [
        [
            InlineKeyboardButton("🛡️ 1%", callback_data="quick_sl_1"),
            InlineKeyboardButton("🛡️ 1.5%", callback_data="quick_sl_1.5"),
            InlineKeyboardButton("🔒 2%", callback_data="quick_sl_2")
        ],
        [
            InlineKeyboardButton("🔒 2.5%", callback_data="quick_sl_2.5"),
            InlineKeyboardButton("⚠️ 3%", callback_data="quick_sl_3"),
            InlineKeyboardButton("⚠️ 5%", callback_data="quick_sl_5")
        ],
        [InlineKeyboardButton("✏️ إدخال مخصص", callback_data="custom_sl_input")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

# ===========================================
# 🛡️ أزرار إدارة المخاطر
# ===========================================

def build_risk_management_menu():
    """بناء قائمة إدارة المخاطر"""
    keyboard = [
        [InlineKeyboardButton("🛡️ تفعيل/إلغاء إدارة المخاطر", callback_data="toggle_risk_management")],
        [InlineKeyboardButton("📉 تعديل حد الخسارة المئوي", callback_data="set_max_loss_percent")],
        [InlineKeyboardButton("💸 تعديل حد الخسارة بالمبلغ", callback_data="set_max_loss_amount")],
        [InlineKeyboardButton("📅 تعديل الحد اليومي", callback_data="set_daily_loss_limit")],
        [InlineKeyboardButton("📆 تعديل الحد الأسبوعي", callback_data="set_weekly_loss_limit")],
        [InlineKeyboardButton("⏹️ إيقاف التداول عند الخسارة", callback_data="toggle_stop_trading")],
        [InlineKeyboardButton("📊 عرض إحصائيات المخاطر", callback_data="show_risk_stats")],
        [InlineKeyboardButton("🔄 إعادة تعيين الإحصائيات", callback_data="reset_risk_stats")],
        [InlineKeyboardButton("📖 شرح مفصل للخيارات", callback_data="risk_management_guide")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_risk_stats_refresh():
    """بناء أزرار تحديث إحصائيات المخاطر"""
    keyboard = [
        [InlineKeyboardButton("🔄 تحديث", callback_data="show_risk_stats")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="risk_management_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

# ===========================================
# 📊 أزرار الصفقات المفتوحة
# ===========================================

def build_positions_keyboard(has_positions: bool = True):
    """بناء أزرار الصفقات"""
    keyboard = []
    
    if has_positions:
        keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="settings")])
    
    return InlineKeyboardMarkup(keyboard)

# ===========================================
# 🎯 أزرار إدارة الصفقات
# ===========================================

def build_position_management_menu(position_id: str, has_tp: bool, has_sl: bool, is_trailing: bool, is_breakeven: bool):
    """بناء قائمة إدارة الصفقة"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"🎯 أهداف الربح {'✅' if has_tp else '➕'}", 
                callback_data=f"setTP_menu_{position_id}"
            ),
            InlineKeyboardButton(
                f"🛑 وقف الخسارة {'✅' if has_sl else '➕'}", 
                callback_data=f"setSL_menu_{position_id}"
            )
        ],
        [
            InlineKeyboardButton("📊 إغلاق جزئي مخصص", callback_data=f"partial_custom_{position_id}")
        ],
        [
            InlineKeyboardButton(
                f"🔁 نقل للتعادل {'🔒' if is_breakeven else '⏸️'}", 
                callback_data=f"moveBE_{position_id}"
            ),
            InlineKeyboardButton(
                f"⚡ Trailing Stop {'✅' if is_trailing else '⏸️'}", 
                callback_data=f"trailing_menu_{position_id}"
            )
        ],
        [
            InlineKeyboardButton("🎲 إعداد سريع (ذكي)", callback_data=f"quick_setup_{position_id}"),
            InlineKeyboardButton("ℹ️ دليل الأدوات", callback_data=f"tools_guide_{position_id}")
        ],
        [
            InlineKeyboardButton("❌ إغلاق كامل", callback_data=f"close_{position_id}"),
            InlineKeyboardButton("🔙 رجوع", callback_data="show_positions")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_tp_menu(position_id: str):
    """بناء قائمة أهداف الربح في الصفقة"""
    keyboard = [
        [InlineKeyboardButton("🎲 تلقائي (ذكي)", callback_data=f"autoTP_{position_id}")],
        [InlineKeyboardButton("✏️ إدخال مخصص", callback_data=f"customTP_{position_id}")],
        [InlineKeyboardButton("🗑️ حذف جميع الأهداف", callback_data=f"clearTP_{position_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_sl_menu(position_id: str):
    """بناء قائمة Stop Loss في الصفقة"""
    keyboard = [
        [InlineKeyboardButton("🎲 تلقائي (ذكي)", callback_data=f"autoSL_{position_id}")],
        [InlineKeyboardButton("✏️ إدخال مخصص", callback_data=f"customSL_{position_id}")],
        [InlineKeyboardButton("🗑️ إلغاء SL", callback_data=f"clearSL_{position_id}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_trailing_menu(position_id: str, is_trailing: bool):
    """بناء قائمة Trailing Stop"""
    keyboard = []
    
    if not is_trailing:
        keyboard.append([InlineKeyboardButton("✅ تفعيل Trailing Stop", callback_data=f"enable_trailing_{position_id}")])
    else:
        keyboard.append([InlineKeyboardButton("⚙️ تعديل المسافة", callback_data=f"set_trailing_distance_{position_id}")])
        keyboard.append([InlineKeyboardButton("❌ تعطيل Trailing Stop", callback_data=f"disable_trailing_{position_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")])
    
    return InlineKeyboardMarkup(keyboard)

# ===========================================
# 🔙 أزرار التنقل والمساعدة
# ===========================================

def build_back_button(callback_data: str = "back_to_settings"):
    """بناء زر الرجوع"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data=callback_data)]
    ])

def build_cancel_button(callback_data: str = "cancel"):
    """بناء زر الإلغاء"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ إلغاء", callback_data=callback_data)]
    ])

def build_confirm_button():
    """بناء زر التأكيد"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
    ])

