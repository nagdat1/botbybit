"""
⌨️ Telegram Keyboards - الأزرار التفاعلية
جميع أزرار البوت بتصميم احترافي
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List
from config import EMOJIS, COLORS


# ==================== القائمة الرئيسية ====================

def main_menu_keyboard(is_admin: bool = False):
    """القائمة الرئيسية"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['chart_up']} التداول", callback_data="menu_trading"),
            InlineKeyboardButton(f"{EMOJIS['wallet']} المحفظة", callback_data="menu_wallet")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['signal']} إشارات Nagdat", callback_data="menu_signals"),
            InlineKeyboardButton(f"{EMOJIS['info']} صفقاتي", callback_data="menu_my_trades")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['settings']} الإعدادات", callback_data="menu_settings"),
            InlineKeyboardButton(f"ℹ️ المساعدة", callback_data="menu_help")
        ]
    ]
    
    if is_admin:
        keyboard.append([
            InlineKeyboardButton(f"{EMOJIS['star']} لوحة المطور", callback_data="admin_panel")
        ])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== اختيار نوع الحساب ====================

def account_type_keyboard():
    """اختيار نوع الحساب"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"🎮 حساب تجريبي (Demo)", 
                callback_data="account_demo"
            )
        ],
        [
            InlineKeyboardButton(
                f"{EMOJIS['fire']} حساب حقيقي (Real)", 
                callback_data="account_real"
            )
        ],
        [
            InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== قائمة التداول ====================

def trading_menu_keyboard():
    """قائمة التداول"""
    keyboard = [
        [
            InlineKeyboardButton(f"{COLORS['green']} شراء (BUY)", callback_data="trade_buy"),
            InlineKeyboardButton(f"{COLORS['red']} بيع (SELL)", callback_data="trade_sell")
        ],
        [
            InlineKeyboardButton(f"📊 Spot", callback_data="trade_type_spot"),
            InlineKeyboardButton(f"🚀 Futures", callback_data="trade_type_futures")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['target']} إدارة الصفقات", callback_data="manage_trades")
        ],
        [
            InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== اختيار الزوج ====================

def symbol_search_keyboard(symbols: List[str], page: int = 0, per_page: int = 8):
    """عرض الأزواج المتاحة"""
    start = page * per_page
    end = start + per_page
    page_symbols = symbols[start:end]
    
    keyboard = []
    
    # عرض الأزواج في صفوف (2 في كل صف)
    for i in range(0, len(page_symbols), 2):
        row = []
        for symbol in page_symbols[i:i+2]:
            row.append(InlineKeyboardButton(symbol, callback_data=f"select_symbol_{symbol}"))
        keyboard.append(row)
    
    # أزرار التنقل
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ السابق", callback_data=f"symbols_page_{page-1}"))
    if end < len(symbols):
        nav_row.append(InlineKeyboardButton("▶️ التالي", callback_data=f"symbols_page_{page+1}"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🔍 بحث مخصص", callback_data="symbol_custom_search")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trading")])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== الأزواج الشائعة ====================

def popular_symbols_keyboard():
    """الأزواج الشائعة"""
    popular = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
        "XRP/USDT", "ADA/USDT", "DOGE/USDT", "MATIC/USDT"
    ]
    
    keyboard = []
    for i in range(0, len(popular), 2):
        row = []
        for symbol in popular[i:i+2]:
            row.append(InlineKeyboardButton(symbol, callback_data=f"select_symbol_{symbol}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("📋 كل الأزواج", callback_data="show_all_symbols")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trading")])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== الرافعة المالية ====================

def leverage_keyboard():
    """اختيار الرافعة المالية"""
    leverages = [1, 2, 3, 5, 10, 15, 20]
    
    keyboard = []
    row = []
    for lev in leverages:
        row.append(InlineKeyboardButton(f"{lev}x", callback_data=f"leverage_{lev}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trading")])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== إدارة المخاطر ====================

def risk_management_keyboard(trade_id: str):
    """أدوات إدارة المخاطر"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['shield']} Stop Loss", callback_data=f"set_sl_{trade_id}"),
            InlineKeyboardButton(f"{EMOJIS['target']} Take Profit", callback_data=f"set_tp_{trade_id}")
        ],
        [
            InlineKeyboardButton(f"📉 Trailing Stop", callback_data=f"set_trailing_{trade_id}")
        ],
        [
            InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_trades")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== إدارة الصفقات ====================

def trade_actions_keyboard(trade_id: str):
    """إجراءات الصفقة"""
    keyboard = [
        [
            InlineKeyboardButton(f"{COLORS['red']} إغلاق كامل", callback_data=f"close_full_{trade_id}")
        ],
        [
            InlineKeyboardButton("إغلاق 25%", callback_data=f"close_25_{trade_id}"),
            InlineKeyboardButton("إغلاق 50%", callback_data=f"close_50_{trade_id}")
        ],
        [
            InlineKeyboardButton("إغلاق 75%", callback_data=f"close_75_{trade_id}")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['settings']} إدارة المخاطر", callback_data=f"risk_manage_{trade_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trades")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== الصفقات المفتوحة ====================

def open_trades_keyboard(trades: List[dict]):
    """عرض الصفقات المفتوحة"""
    keyboard = []
    
    for trade in trades[:10]:  # عرض أول 10 صفقات
        symbol = trade['symbol']
        side = trade['side']
        pnl = trade.get('profit_loss', 0)
        
        emoji = COLORS['green'] if pnl >= 0 else COLORS['red']
        label = f"{emoji} {symbol} - {side.upper()} ({pnl:+.2f}$)"
        
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"view_trade_{trade['trade_id']}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔄 تحديث", callback_data="refresh_trades")
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== إشارات Nagdat ====================

def nagdat_signals_keyboard(is_subscribed: bool):
    """قائمة إشارات Nagdat"""
    keyboard = []
    
    if is_subscribed:
        keyboard.append([
            InlineKeyboardButton(
                f"{EMOJIS['muted']} إلغاء الاشتراك", 
                callback_data="unsubscribe_nagdat"
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                f"{EMOJIS['bell']} الإشارات الأخيرة",
                callback_data="view_recent_signals"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                f"{EMOJIS['bell']} اشترك في إشارات Nagdat",
                callback_data="subscribe_nagdat"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(f"ℹ️ عن الإشارات", callback_data="about_signals")
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== لوحة المطور ====================

def admin_panel_keyboard():
    """لوحة المطور"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['signal']} إرسال إشارة", callback_data="admin_send_signal"),
        ],
        [
            InlineKeyboardButton(f"👥 المشتركين ({0})", callback_data="admin_subscribers"),
            InlineKeyboardButton(f"📊 الإحصائيات", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(f"📢 رسالة جماعية", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(f"🔙 رجوع", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def signal_type_keyboard():
    """نوع الإشارة"""
    keyboard = [
        [
            InlineKeyboardButton(f"{COLORS['green']} شراء (BUY)", callback_data="signal_buy"),
            InlineKeyboardButton(f"{COLORS['red']} بيع (SELL)", callback_data="signal_sell")
        ],
        [
            InlineKeyboardButton("🔙 إلغاء", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_signal_keyboard(signal_data: dict):
    """تأكيد إرسال الإشارة"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['success']} إرسال الآن", callback_data="confirm_send_signal"),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['error']} إلغاء", callback_data="admin_panel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== الإعدادات ====================

def settings_keyboard(user_data: dict):
    """قائمة الإعدادات"""
    mode = user_data.get('mode', 'demo')
    mode_emoji = "🎮" if mode == 'demo' else "🔥"
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{mode_emoji} الحساب: {mode.upper()}", 
                callback_data="settings_switch_mode"
            )
        ],
        [
            InlineKeyboardButton(f"🔧 الرافعة المالية", callback_data="settings_leverage"),
        ],
        [
            InlineKeyboardButton(f"🔑 إعدادات API", callback_data="settings_api")
        ],
        [
            InlineKeyboardButton(f"🌐 Webhook الخاص", callback_data="settings_webhook")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== التأكيد ====================

def confirmation_keyboard(action: str, data: str = ""):
    """أزرار تأكيد"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['success']} تأكيد", callback_data=f"confirm_{action}_{data}"),
            InlineKeyboardButton(f"{EMOJIS['error']} إلغاء", callback_data=f"cancel_{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== الرجوع ====================

def back_button(callback: str = "back_to_main"):
    """زر الرجوع فقط"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=callback)]]
    return InlineKeyboardMarkup(keyboard)

