"""
🎨 UI Enhancer - محسّن الواجهة
تحسين شكل وتصميم واجهة البوت
"""
from typing import List, Dict
from utils.formatters import format_price, format_percentage
from config import EMOJIS, COLORS


class UIEnhancer:
    """محسّن الواجهة"""
    
    @staticmethod
    def create_progress_bar(percent: float, length: int = 10) -> str:
        """إنشاء شريط تقدم"""
        filled = int((percent / 100) * length)
        empty = length - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percent:.1f}%"
    
    @staticmethod
    def create_price_chart(prices: List[float], width: int = 20) -> str:
        """رسم مخطط بسيط للأسعار"""
        if not prices or len(prices) < 2:
            return "━" * width
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return "━" * width
        
        # تحويل الأسعار إلى ارتفاعات
        heights = [
            int(((price - min_price) / price_range) * 5)
            for price in prices[-width:]
        ]
        
        # رسم المخطط
        lines = []
        for level in range(5, -1, -1):
            line = ""
            for height in heights:
                if height >= level:
                    line += "█"
                else:
                    line += " "
            lines.append(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_trade_card(trade: Dict) -> str:
        """تنسيق بطاقة صفقة محسّنة"""
        symbol = trade['symbol']
        side = trade['side']
        entry = trade['entry_price']
        current = trade.get('current_price', entry)
        pnl = trade.get('profit_loss', 0)
        pnl_percent = trade.get('profit_loss_percent', 0)
        
        # تحديد الاتجاه واللون
        side_emoji = COLORS['green'] if side == 'buy' else COLORS['red']
        pnl_emoji = COLORS['green'] if pnl >= 0 else COLORS['red']
        
        # شريط التقدم
        progress = UIEnhancer.create_progress_bar(abs(pnl_percent))
        
        card = f"""
╔══════════════════════════════════╗
║  {side_emoji} {symbol} - {side.upper()}
╠══════════════════════════════════╣
║ 💰 دخول: {format_price(entry, 4)}
║ 💹 حالي: {format_price(current, 4)}
║ 
║ {pnl_emoji} الربح/الخسارة
║ {progress}
║ {pnl:+.2f}$ ({pnl_percent:+.2f}%)
╚══════════════════════════════════╝
"""
        return card
    
    @staticmethod
    def format_wallet_card(balance: float, pnl_today: float) -> str:
        """تنسيق بطاقة المحفظة"""
        pnl_emoji = COLORS['green'] if pnl_today >= 0 else COLORS['red']
        
        card = f"""
╔═══════════════════════════════════╗
║        💰 المحفظة
╠═══════════════════════════════════╣
║ 
║  {EMOJIS['wallet']} الرصيد الإجمالي
║  {format_price(balance)}
║ 
║  {pnl_emoji} الربح/الخسارة اليوم
║  {pnl_today:+.2f}$
║ 
╚═══════════════════════════════════╝
"""
        return card
    
    @staticmethod
    def format_market_overview(ticker: Dict) -> str:
        """نظرة عامة على السوق"""
        price = ticker['price']
        change = ticker.get('change', 0)
        high = ticker.get('high', price)
        low = ticker.get('low', price)
        
        change_emoji = COLORS['green'] if change >= 0 else COLORS['red']
        
        # نسبة التغيير
        range_percent = ((price - low) / (high - low) * 100) if high > low else 50
        position_bar = UIEnhancer.create_progress_bar(range_percent, 15)
        
        overview = f"""
╔═══════════════════════════════════╗
║        📊 نظرة السوق
╠═══════════════════════════════════╣
║ 
║  💹 السعر الحالي
║  {format_price(price, 4)}
║ 
║  {change_emoji} التغيير (24س)
║  {change:+.2f}%
║ 
║  📈 أعلى: {format_price(high, 4)}
║  📉 أقل: {format_price(low, 4)}
║ 
║  📍 موقع السعر
║  {position_bar}
║ 
╚═══════════════════════════════════╝
"""
        return overview
    
    @staticmethod
    def format_signal_card(signal: Dict) -> str:
        """تنسيق بطاقة إشارة"""
        symbol = signal['symbol']
        action = signal['action']
        leverage = signal.get('leverage', 1)
        
        action_emoji = COLORS['green'] if action == 'buy' else COLORS['red']
        
        card = f"""
╔═══════════════════════════════════╗
║     {EMOJIS['signal']} إشارة من Nagdat
╠═══════════════════════════════════╣
║ 
║  {action_emoji} {action.upper()}
║  💱 {symbol}
║  📊 رافعة: {leverage}x
║ 
"""
        
        if signal.get('stop_loss'):
            card += f"║  {EMOJIS['shield']} SL: {format_price(signal['stop_loss'], 4)}\n"
        
        if signal.get('take_profit'):
            card += f"║  {EMOJIS['target']} TP: {format_price(signal['take_profit'], 4)}\n"
        
        if signal.get('message'):
            card += f"║ \n║  📝 {signal['message']}\n"
        
        card += "║ \n╚═══════════════════════════════════╝"
        
        return card
    
    @staticmethod
    def format_stats_card(stats: Dict) -> str:
        """تنسيق بطاقة الإحصائيات"""
        total = stats.get('total_trades', 0)
        winning = stats.get('winning_trades', 0)
        losing = stats.get('losing_trades', 0)
        win_rate = (winning / total * 100) if total > 0 else 0
        
        profit = stats.get('total_profit', 0)
        loss = stats.get('total_loss', 0)
        net = profit - loss
        
        win_bar = UIEnhancer.create_progress_bar(win_rate, 15)
        net_emoji = COLORS['green'] if net >= 0 else COLORS['red']
        
        card = f"""
╔═══════════════════════════════════╗
║        📈 إحصائياتك
╠═══════════════════════════════════╣
║ 
║  🎯 معدل النجاح
║  {win_bar}
║  ({winning}/{total} صفقة)
║ 
║  💰 الأرباح: +{format_price(profit)}
║  💸 الخسائر: -{format_price(loss)}
║ 
║  {net_emoji} الصافي
║  {net:+.2f}$
║ 
╚═══════════════════════════════════╝
"""
        return card
    
    @staticmethod
    def create_menu_header(title: str, icon: str = "📋") -> str:
        """إنشاء رأس قائمة"""
        border_length = len(title) + 4
        border = "═" * border_length
        
        return f"""
╔{border}╗
║ {icon} {title} ║
╚{border}╝
"""
    
    @staticmethod
    def format_button_row(buttons: List[str], per_row: int = 2) -> str:
        """تنسيق صف أزرار"""
        rows = []
        for i in range(0, len(buttons), per_row):
            row = buttons[i:i+per_row]
            rows.append(" │ ".join(row))
        return "\n".join(rows)
    
    @staticmethod
    def add_decorative_border(text: str, style: str = "double") -> str:
        """إضافة إطار زخرفي"""
        lines = text.strip().split("\n")
        max_length = max(len(line) for line in lines)
        
        if style == "double":
            top = "╔" + "═" * (max_length + 2) + "╗"
            bottom = "╚" + "═" * (max_length + 2) + "╝"
            middle = "║"
        else:  # single
            top = "┌" + "─" * (max_length + 2) + "┐"
            bottom = "└" + "─" * (max_length + 2) + "┘"
            middle = "│"
        
        bordered = [top]
        for line in lines:
            padded = line.ljust(max_length)
            bordered.append(f"{middle} {padded} {middle}")
        bordered.append(bottom)
        
        return "\n".join(bordered)
    
    @staticmethod
    def format_notification(message: str, type: str = "info") -> str:
        """تنسيق إشعار"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon = icons.get(type, "📢")
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  {icon} {message}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""


# تصدير
__all__ = ['UIEnhancer']

