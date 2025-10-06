"""
✅ Input Validators - التحقق من المدخلات
التحقق من صحة المدخلات والبيانات
"""
import re
from typing import Tuple, Optional


def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """التحقق من صحة رمز الزوج"""
    if not symbol:
        return False, "الرجاء إدخال رمز الزوج"
    
    # تنسيق الرمز
    symbol = symbol.upper().replace(" ", "")
    
    # التحقق من الصيغة
    if '/' not in symbol:
        # محاولة إضافة /USDT تلقائياً
        if not symbol.endswith('USDT'):
            symbol = f"{symbol}/USDT"
        else:
            # تحويل BTCUSDT إلى BTC/USDT
            symbol = symbol.replace('USDT', '/USDT')
    
    # التحقق من الصيغة النهائية
    pattern = r'^[A-Z0-9]+/[A-Z0-9]+$'
    if not re.match(pattern, symbol):
        return False, "صيغة الزوج غير صحيحة. استخدم صيغة مثل BTC/USDT"
    
    return True, symbol


def validate_amount(amount_str: str, min_amount: float = 10, 
                   max_amount: float = 100000) -> Tuple[bool, Optional[float], str]:
    """التحقق من صحة المبلغ"""
    try:
        amount = float(amount_str)
        
        if amount <= 0:
            return False, None, "المبلغ يجب أن يكون أكبر من صفر"
        
        if amount < min_amount:
            return False, None, f"الحد الأدنى للمبلغ هو {min_amount}$"
        
        if amount > max_amount:
            return False, None, f"الحد الأقصى للمبلغ هو {max_amount}$"
        
        return True, amount, "صحيح"
    
    except ValueError:
        return False, None, "الرجاء إدخال رقم صحيح"


def validate_leverage(leverage_str: str, min_lev: int = 1, 
                     max_lev: int = 20) -> Tuple[bool, Optional[int], str]:
    """التحقق من صحة الرافعة المالية"""
    try:
        leverage = int(leverage_str)
        
        if leverage < min_lev:
            return False, None, f"الحد الأدنى للرافعة هو {min_lev}x"
        
        if leverage > max_lev:
            return False, None, f"الحد الأقصى للرافعة هو {max_lev}x"
        
        return True, leverage, "صحيح"
    
    except ValueError:
        return False, None, "الرجاء إدخال رقم صحيح"


def validate_price(price_str: str) -> Tuple[bool, Optional[float], str]:
    """التحقق من صحة السعر"""
    try:
        price = float(price_str)
        
        if price <= 0:
            return False, None, "السعر يجب أن يكون أكبر من صفر"
        
        return True, price, "صحيح"
    
    except ValueError:
        return False, None, "الرجاء إدخال رقم صحيح"


def validate_percentage(percent_str: str, min_percent: float = 0.1,
                       max_percent: float = 50) -> Tuple[bool, Optional[float], str]:
    """التحقق من صحة النسبة المئوية"""
    try:
        percent = float(percent_str)
        
        if percent <= 0:
            return False, None, "النسبة يجب أن تكون أكبر من صفر"
        
        if percent < min_percent:
            return False, None, f"الحد الأدنى للنسبة هو {min_percent}%"
        
        if percent > max_percent:
            return False, None, f"الحد الأقصى للنسبة هو {max_percent}%"
        
        return True, percent, "صحيح"
    
    except ValueError:
        return False, None, "الرجاء إدخال رقم صحيح"


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """التحقق من صحة API Key"""
    if not api_key or len(api_key) < 10:
        return False, "API Key غير صحيح"
    
    # إزالة المسافات
    api_key = api_key.strip()
    
    return True, api_key


def validate_api_secret(api_secret: str) -> Tuple[bool, str]:
    """التحقق من صحة API Secret"""
    if not api_secret or len(api_secret) < 10:
        return False, "API Secret غير صحيح"
    
    # إزالة المسافات
    api_secret = api_secret.strip()
    
    return True, api_secret


def validate_webhook_token(token: str, expected_token: str) -> bool:
    """التحقق من توكن Webhook"""
    return token == expected_token


def validate_partial_close_percent(percent: int) -> Tuple[bool, str]:
    """التحقق من نسبة الإغلاق الجزئي"""
    valid_percents = [25, 50, 75, 100]
    
    if percent not in valid_percents:
        return False, f"النسبة يجب أن تكون من: {', '.join(map(str, valid_percents))}"
    
    return True, "صحيح"


def sanitize_input(text: str, max_length: int = 500) -> str:
    """تنظيف المدخلات من المحارف الخطرة"""
    # إزالة HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # إزالة المحارف الخاصة الخطرة
    text = re.sub(r'[<>\"\'&]', '', text)
    
    # تحديد الطول
    text = text[:max_length]
    
    return text.strip()


def validate_trade_type(trade_type: str) -> Tuple[bool, str]:
    """التحقق من نوع الصفقة"""
    valid_types = ['spot', 'futures', 'future']
    trade_type = trade_type.lower()
    
    if trade_type not in valid_types:
        return False, "نوع الصفقة يجب أن يكون spot أو futures"
    
    # توحيد التسمية
    if trade_type == 'future':
        trade_type = 'futures'
    
    return True, trade_type


def validate_trade_side(side: str) -> Tuple[bool, str]:
    """التحقق من اتجاه الصفقة"""
    valid_sides = ['buy', 'sell', 'long', 'short']
    side = side.lower()
    
    if side not in valid_sides:
        return False, "الاتجاه يجب أن يكون buy أو sell"
    
    # توحيد التسمية
    if side == 'long':
        side = 'buy'
    elif side == 'short':
        side = 'sell'
    
    return True, side


def calculate_stop_loss_price(entry_price: float, side: str, 
                              percent: float) -> float:
    """حساب سعر Stop Loss"""
    if side == 'buy':
        return entry_price * (1 - percent / 100)
    else:  # sell
        return entry_price * (1 + percent / 100)


def calculate_take_profit_price(entry_price: float, side: str,
                                percent: float) -> float:
    """حساب سعر Take Profit"""
    if side == 'buy':
        return entry_price * (1 + percent / 100)
    else:  # sell
        return entry_price * (1 - percent / 100)


def validate_stop_loss(entry_price: float, stop_loss: float, 
                      side: str) -> Tuple[bool, str]:
    """التحقق من صحة Stop Loss"""
    if side == 'buy':
        if stop_loss >= entry_price:
            return False, "Stop Loss يجب أن يكون أقل من سعر الدخول للشراء"
    else:  # sell
        if stop_loss <= entry_price:
            return False, "Stop Loss يجب أن يكون أعلى من سعر الدخول للبيع"
    
    return True, "صحيح"


def validate_take_profit(entry_price: float, take_profit: float,
                        side: str) -> Tuple[bool, str]:
    """التحقق من صحة Take Profit"""
    if side == 'buy':
        if take_profit <= entry_price:
            return False, "Take Profit يجب أن يكون أعلى من سعر الدخول للشراء"
    else:  # sell
        if take_profit >= entry_price:
            return False, "Take Profit يجب أن يكون أقل من سعر الدخول للبيع"
    
    return True, "صحيح"

