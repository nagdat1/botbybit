"""
✨ Message Formatters - تنسيق الرسائل
تنسيق الرسائل بشكل احترافي مع الألوان والرموز
"""
from datetime import datetime
from typing import Dict, List
from config import EMOJIS, COLORS, MESSAGES


def format_price(price: float, decimals: int = 2) -> str:
    """تنسيق السعر"""
    if price >= 1000:
        return f"${price:,.{decimals}f}"
    elif price >= 1:
        return f"${price:.{decimals}f}"
    else:
        # للأسعار الصغيرة جداً
        return f"${price:.8f}".rstrip('0').rstrip('.')


def format_percentage(percent: float) -> str:
    """تنسيق النسبة المئوية مع اللون"""
    emoji = COLORS['green'] if percent >= 0 else COLORS['red']
    return f"{emoji} {percent:+.2f}%"


def format_profit_loss(pnl: float, pnl_percent: float) -> str:
    """تنسيق الربح/الخسارة"""
    emoji = COLORS['green'] if pnl >= 0 else COLORS['red']
    sign = "+" if pnl >= 0 else ""
    return f"{emoji} {sign}{pnl:.2f}$ ({sign}{pnl_percent:.2f}%)"


def format_timestamp(timestamp) -> str:
    """تنسيق الوقت"""
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return "غير معروف"
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"منذ {diff.days} يوم"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"منذ {hours} ساعة"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"منذ {minutes} دقيقة"
    else:
        return "الآن"


# ==================== رسائل الترحيب ====================

def format_welcome_message(user_name: str, is_new: bool = True) -> str:
    """رسالة الترحيب"""
    if is_new:
        msg = MESSAGES['welcome'].format(**EMOJIS)
        msg = msg.replace("{rocket}", EMOJIS['rocket'])
        msg = msg.replace("{star}", EMOJIS['star'])
        msg = msg.replace("{chart_up}", EMOJIS['chart_up'])
        msg = msg.replace("{shield}", EMOJIS['shield'])
        msg = msg.replace("{signal}", EMOJIS['signal'])
        return msg
    else:
        return f"""
{EMOJIS['rocket']} مرحباً بعودتك، {user_name}!

اختر ما تريد من القائمة الرئيسية:
        """


# ==================== معلومات المحفظة ====================

def format_wallet_info(user_data: Dict, trades: List[Dict] = None) -> str:
    """تنسيق معلومات المحفظة"""
    mode = user_data.get('mode', 'demo')
    mode_emoji = "🎮" if mode == 'demo' else "🔥"
    
    msg = f"""
{EMOJIS['wallet']} ━━━━━ المحفظة ━━━━━

{mode_emoji} نوع الحساب: {mode.upper()}
"""
    
    if mode == 'demo':
        balance = user_data.get('demo_balance', 0)
        msg += f"{EMOJIS['money']} الرصيد: {format_price(balance)}\n"
    else:
        msg += f"{EMOJIS['money']} الرصيد: متصل بـ Bybit API\n"
    
    # الصفقات المفتوحة
    if trades:
        total_pnl = sum(t.get('profit_loss', 0) for t in trades)
        msg += f"\n{EMOJIS['chart_up']} صفقات مفتوحة: {len(trades)}\n"
        msg += f"الربح/الخسارة: {format_profit_loss(total_pnl, 0)}\n"
    
    msg += "\n━━━━━━━━━━━━━━━"
    
    return msg


# ==================== معلومات الصفقة ====================

def format_trade_info(trade: Dict, current_price: float = None) -> str:
    """تنسيق معلومات صفقة واحدة"""
    symbol = trade['symbol']
    trade_type = trade['trade_type']
    side = trade['side']
    entry_price = trade['entry_price']
    quantity = trade['quantity']
    leverage = trade.get('leverage', 1)
    
    # السعر الحالي
    if current_price is None:
        current_price = trade.get('current_price', entry_price)
    
    # الربح/الخسارة
    pnl = trade.get('profit_loss', 0)
    pnl_percent = trade.get('profit_loss_percent', 0)
    
    # الرموز
    side_emoji = COLORS['green'] if side == 'buy' else COLORS['red']
    type_emoji = "📊" if trade_type == 'spot' else "🚀"
    
    msg = f"""
{type_emoji} ━━━━━ معلومات الصفقة ━━━━━

{side_emoji} الاتجاه: {side.upper()}
💱 الزوج: {symbol}
⚙️ النوع: {trade_type.upper()}
"""
    
    if leverage > 1:
        msg += f"📊 الرافعة: {leverage}x\n"
    
    msg += f"""
━━━━━━━━━━━━━━━━━━
💰 سعر الدخول: {format_price(entry_price, 4)}
💹 السعر الحالي: {format_price(current_price, 4)}
📦 الكمية: {quantity:.6f}

━━━━━━━━━━━━━━━━━━
{format_profit_loss(pnl, pnl_percent)}
━━━━━━━━━━━━━━━━━━
"""
    
    # Stop Loss & Take Profit
    if trade.get('stop_loss'):
        msg += f"\n{EMOJIS['shield']} Stop Loss: {format_price(trade['stop_loss'], 4)}"
    
    if trade.get('take_profit'):
        msg += f"\n{EMOJIS['target']} Take Profit: {format_price(trade['take_profit'], 4)}"
    
    if trade.get('trailing_stop_percent'):
        msg += f"\n📉 Trailing Stop: {trade['trailing_stop_percent']}%"
    
    # الوقت
    opened_at = format_timestamp(trade['opened_at'])
    msg += f"\n\n🕐 الوقت: {opened_at}"
    
    return msg


# ==================== قائمة الصفقات ====================

def format_trades_list(trades: List[Dict]) -> str:
    """تنسيق قائمة الصفقات"""
    if not trades:
        return f"""
{EMOJIS['info']} لا توجد صفقات مفتوحة حالياً

ابدأ التداول الآن من قائمة التداول!
        """
    
    msg = f"{EMOJIS['chart_up']} ━━━ الصفقات المفتوحة ({len(trades)}) ━━━\n\n"
    
    total_pnl = 0
    
    for i, trade in enumerate(trades[:10], 1):
        symbol = trade['symbol']
        side = trade['side']
        pnl = trade.get('profit_loss', 0)
        pnl_percent = trade.get('profit_loss_percent', 0)
        
        side_emoji = COLORS['green'] if side == 'buy' else COLORS['red']
        
        msg += f"{i}. {side_emoji} {symbol} - {side.upper()}\n"
        msg += f"   {format_profit_loss(pnl, pnl_percent)}\n\n"
        
        total_pnl += pnl
    
    msg += "━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 الإجمالي: {format_profit_loss(total_pnl, 0)}\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    
    return msg


# ==================== معلومات السعر ====================

def format_ticker_info(symbol: str, ticker: Dict) -> str:
    """تنسيق معلومات السعر"""
    price = ticker['price']
    change = ticker.get('change', 0)
    high = ticker.get('high', price)
    low = ticker.get('low', price)
    volume = ticker.get('volume', 0)
    
    msg = f"""
📊 ━━━━━ {symbol} ━━━━━

💹 السعر: {format_price(price, 4)}
{format_percentage(change)}

━━━━━━━━━━━━━━━━━━
📈 أعلى سعر: {format_price(high, 4)}
📉 أقل سعر: {format_price(low, 4)}
📊 الحجم: {format_price(volume, 0)}

🕐 آخر تحديث: {format_timestamp(ticker['timestamp'])}
    """
    
    return msg


# ==================== إشارة Nagdat ====================

def format_nagdat_signal(signal: Dict, ticker: Dict = None) -> str:
    """تنسيق إشارة Nagdat"""
    symbol = signal['symbol']
    action = signal['action']
    
    action_emoji = COLORS['green'] if action == 'buy' else COLORS['red']
    
    msg = f"""
{EMOJIS['signal']} ━━━━━ إشارة من Nagdat ━━━━━

{action_emoji} الإجراء: {action.upper()}
💱 الزوج: {symbol}
"""
    
    if ticker:
        msg += f"💹 السعر: {format_price(ticker['price'], 4)}\n"
    
    if signal.get('leverage'):
        msg += f"📊 الرافعة المقترحة: {signal['leverage']}x\n"
    
    if signal.get('stop_loss'):
        msg += f"\n{EMOJIS['shield']} Stop Loss: {format_price(signal['stop_loss'], 4)}"
    
    if signal.get('take_profit'):
        msg += f"\n{EMOJIS['target']} Take Profit: {format_price(signal['take_profit'], 4)}"
    
    if signal.get('message'):
        msg += f"\n\n📝 ملاحظات: {signal['message']}"
    
    msg += f"\n\n🕐 {format_timestamp(signal['created_at'])}"
    msg += "\n━━━━━━━━━━━━━━━━━━"
    
    return msg


# ==================== لوحة المطور ====================

def format_admin_stats(stats: Dict) -> str:
    """تنسيق إحصائيات البوت"""
    msg = f"""
{EMOJIS['star']} ━━━━━ إحصائيات البوت ━━━━━

👥 إجمالي المستخدمين: {stats.get('total_users', 0)}
✅ المستخدمين النشطين: {stats.get('active_users', 0)}
{EMOJIS['bell']} المشتركين: {stats.get('subscribers', 0)}

{EMOJIS['signal']} إشارات مرسلة: {stats.get('signals_sent', 0)}
{EMOJIS['chart_up']} صفقات نشطة: {stats.get('active_trades', 0)}

🕐 آخر تحديث: {format_timestamp(datetime.now())}
━━━━━━━━━━━━━━━━━━
    """
    return msg


# ==================== تأكيد الإجراء ====================

def format_confirmation_message(action: str, details: str = "") -> str:
    """رسالة تأكيد إجراء"""
    return f"""
{EMOJIS['warning']} تأكيد العملية

الإجراء: {action}
{details}

هل أنت متأكد من المتابعة؟
    """


# ==================== رسالة نجاح ====================

def format_success_message(message: str) -> str:
    """رسالة نجاح"""
    return f"{EMOJIS['success']} {message}"


# ==================== رسالة خطأ ====================

def format_error_message(message: str) -> str:
    """رسالة خطأ"""
    return f"{EMOJIS['error']} {message}"


# ==================== معلومات Webhook ====================

def format_webhook_info(webhook_url: str, webhook_token: str) -> str:
    """معلومات Webhook الشخصي"""
    return f"""
{EMOJIS['info']} ━━━━━ Webhook الخاص بك ━━━━━

🌐 الرابط:
`{webhook_url}`

🔑 التوكن:
`{webhook_token}`

━━━━━━━━━━━━━━━━━━
📖 كيفية الاستخدام:

أرسل POST request إلى الرابط أعلاه مع:

```json
{{
  "token": "{webhook_token}",
  "symbol": "BTC/USDT",
  "action": "buy",
  "leverage": 10,
  "stop_loss": 50000,
  "take_profit": 60000
}}
```

{EMOJIS['shield']} احتفظ بالتوكن سرياً!
    """

