#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
شاشة سجل الصفقات مع فلاتر وتقارير
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class TradeHistoryDisplay:
    """عرض سجل الصفقات مع فلاتر"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """تنسيق الأرقام"""
        try:
            return f"{number:,.{decimals}f}"
        except:
            return str(number)
    
    @staticmethod
    def format_datetime(dt_string: str) -> str:
        """تنسيق التاريخ والوقت"""
        try:
            if not dt_string:
                return "غير محدد"
            
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return dt_string
    
    @staticmethod
    def calculate_duration(open_time: str, close_time: str) -> str:
        """حساب مدة الصفقة"""
        try:
            if not open_time or not close_time:
                return "غير محدد"
            
            dt_open = datetime.fromisoformat(open_time.replace('Z', '+00:00'))
            dt_close = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
            
            duration = dt_close - dt_open
            
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if days > 0:
                return f"{days}d {hours}h"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "غير محدد"
    
    def format_trade_summary(self, trade: Dict) -> str:
        """تنسيق ملخص صفقة واحدة"""
        try:
            symbol = trade.get('symbol', 'UNKNOWN')
            side = trade.get('side', 'BUY').upper()
            status = trade.get('status', 'OPEN')
            market_type = trade.get('market_type', 'spot').upper()
            account_type = trade.get('account_type', 'demo')
            
            # السعر والكمية
            entry_price = trade.get('entry_price', 0)
            close_price = trade.get('close_price', trade.get('closing_price', 0))
            quantity = trade.get('quantity', 0)
            
            # PnL
            pnl_value = trade.get('pnl_value', trade.get('pnl', 0))
            pnl_percent = trade.get('pnl_percent', 0)
            
            # حساب PnL إذا لم يكن موجوداً
            if not pnl_value and close_price and entry_price:
                if side == 'BUY':
                    pnl_value = (close_price - entry_price) * quantity
                else:
                    pnl_value = (entry_price - close_price) * quantity
                
                amount = entry_price * quantity
                if amount > 0:
                    pnl_percent = (pnl_value / amount) * 100
            
            # المؤشرات
            pnl_indicator = "🟢" if pnl_value > 0 else ("🔴" if pnl_value < 0 else "⚪")
            status_indicator = "✅" if status == 'CLOSED' else "🔄"
            account_indicator = "💼" if account_type == 'real' else "🎮"
            
            # التواريخ
            open_time = self.format_datetime(trade.get('open_time', ''))
            close_time = self.format_datetime(trade.get('close_time', '')) if status == 'CLOSED' else "مفتوحة"
            duration = self.calculate_duration(trade.get('open_time', ''), trade.get('close_time', '')) if status == 'CLOSED' else "---"
            
            # Signal ID
            signal_id = trade.get('signal_id', '')
            signal_display = f" • 📊 {signal_id}" if signal_id else ""
            
            # التنسيق
            summary = f"{status_indicator} {pnl_indicator} {symbol} • {side} • {market_type}{signal_display}\n"
            summary += f"{account_indicator} Entry: {self.format_number(entry_price, 4)}"
            
            if status == 'CLOSED':
                summary += f" → Close: {self.format_number(close_price, 4)}\n"
                summary += f"📅 {open_time} → {close_time} ({duration})\n"
                summary += f"💰 P&L: {self.format_number(pnl_value, 2):+} USDT ({pnl_percent:+.2f}%)"
            else:
                summary += f"\n📅 Opened: {open_time}\n"
                summary += f"💰 Size: {self.format_number(quantity, 4)}"
            
            return summary
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق ملخص الصفقة: {e}")
            return "خطأ في عرض الصفقة"
    
    def format_trade_history_message(self, trades: List[Dict], filters: Dict = None) -> tuple:
        """تنسيق رسالة سجل الصفقات"""
        try:
            if not trades:
                message = "📊 TRADE HISTORY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📭 لا توجد صفقات في السجل"
                return message, self._create_filter_keyboard(filters)
            
            # حساب الإحصائيات
            total_trades = len(trades)
            closed_trades = [t for t in trades if t.get('status') == 'CLOSED']
            open_trades = [t for t in trades if t.get('status') == 'OPEN']
            
            total_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in closed_trades)
            winning_trades = [t for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) > 0)]
            losing_trades = [t for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) < 0)]
            
            win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
            
            # العنوان مع الفلاتر
            header = "📊 TRADE HISTORY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # عرض الفلاتر النشطة
            if filters:
                active_filters = []
                if filters.get('status'):
                    active_filters.append(f"Status: {filters['status']}")
                if filters.get('account_type'):
                    active_filters.append(f"Account: {filters['account_type']}")
                if filters.get('market_type'):
                    active_filters.append(f"Market: {filters['market_type']}")
                if filters.get('symbol'):
                    active_filters.append(f"Symbol: {filters['symbol']}")
                
                if active_filters:
                    header += f"🔍 Filters: {' • '.join(active_filters)}\n\n"
            
            # الإحصائيات
            stats = f"📈 STATISTICS\n"
            stats += f"Total: {total_trades} • Open: {len(open_trades)} • Closed: {len(closed_trades)}\n"
            
            if closed_trades:
                pnl_indicator = "🟢" if total_pnl > 0 else "🔴"
                stats += f"Win Rate: {win_rate:.1f}% ({len(winning_trades)}W/{len(losing_trades)}L)\n"
                stats += f"Total P&L: {self.format_number(total_pnl, 2):+} USDT {pnl_indicator}\n"
            
            stats += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # عرض الصفقات (محدود بـ 10 صفقات)
            trades_display = ""
            display_limit = min(10, len(trades))
            
            for i, trade in enumerate(trades[:display_limit], 1):
                trades_display += f"{i}. {self.format_trade_summary(trade)}\n"
                trades_display += "─────────────────────────────────\n"
            
            if len(trades) > display_limit:
                trades_display += f"\n... وهناك {len(trades) - display_limit} صفقة أخرى\n"
            
            message = header + stats + trades_display
            
            # لوحة المفاتيح
            keyboard = self._create_filter_keyboard(filters)
            
            return message, keyboard
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة سجل الصفقات: {e}")
            return "خطأ في عرض السجل", None
    
    def _create_filter_keyboard(self, current_filters: Dict = None) -> InlineKeyboardMarkup:
        """إنشاء لوحة مفاتيح الفلاتر"""
        try:
            if not current_filters:
                current_filters = {}
            
            keyboard = []
            
            # فلتر الحالة
            status_row = [
                InlineKeyboardButton("📊 All", callback_data="history_filter_status_all"),
                InlineKeyboardButton("🔄 Open", callback_data="history_filter_status_open"),
                InlineKeyboardButton("✅ Closed", callback_data="history_filter_status_closed")
            ]
            keyboard.append(status_row)
            
            # فلتر نوع الحساب
            account_row = [
                InlineKeyboardButton("💼 Real", callback_data="history_filter_account_real"),
                InlineKeyboardButton("🎮 Demo", callback_data="history_filter_account_demo"),
                InlineKeyboardButton("🔀 Both", callback_data="history_filter_account_all")
            ]
            keyboard.append(account_row)
            
            # فلتر نوع السوق
            market_row = [
                InlineKeyboardButton("💱 Spot", callback_data="history_filter_market_spot"),
                InlineKeyboardButton("⚡ Futures", callback_data="history_filter_market_futures"),
                InlineKeyboardButton("🔀 Both", callback_data="history_filter_market_all")
            ]
            keyboard.append(market_row)
            
            # التحكم
            control_row = [
                InlineKeyboardButton("🔄 تحديث", callback_data="history_refresh"),
                InlineKeyboardButton("📊 تقرير", callback_data="history_report"),
                InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
            ]
            keyboard.append(control_row)
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة المفاتيح: {e}")
            return None
    
    def generate_detailed_report(self, trades: List[Dict]) -> str:
        """توليد تقرير مفصل للصفقات"""
        try:
            if not trades:
                return "📊 لا توجد بيانات لعرض التقرير"
            
            # فصل الصفقات حسب الحالة
            closed_trades = [t for t in trades if t.get('status') == 'CLOSED']
            open_trades = [t for t in trades if t.get('status') == 'OPEN']
            
            # الإحصائيات العامة
            total_trades = len(trades)
            total_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in closed_trades)
            
            winning_trades = [t for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) > 0)]
            losing_trades = [t for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) < 0)]
            
            avg_win = sum(t.get('pnl_value', t.get('pnl', 0)) for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t.get('pnl_value', t.get('pnl', 0)) for t in losing_trades) / len(losing_trades) if losing_trades else 0
            
            win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
            
            # الإحصائيات حسب نوع السوق
            spot_trades = [t for t in closed_trades if t.get('market_type') == 'spot']
            futures_trades = [t for t in closed_trades if t.get('market_type') == 'futures']
            
            spot_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in spot_trades)
            futures_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in futures_trades)
            
            # الإحصائيات حسب نوع الحساب
            real_trades = [t for t in closed_trades if t.get('account_type') == 'real']
            demo_trades = [t for t in closed_trades if t.get('account_type') == 'demo']
            
            real_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in real_trades)
            demo_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in demo_trades)
            
            # بناء التقرير
            report = "📊 DETAILED TRADING REPORT\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # القسم 1: الإحصائيات العامة
            report += "📈 OVERALL STATISTICS\n"
            report += f"Total Trades: {total_trades}\n"
            report += f"Open: {len(open_trades)} • Closed: {len(closed_trades)}\n"
            report += f"Winning: {len(winning_trades)} • Losing: {len(losing_trades)}\n"
            report += f"Win Rate: {win_rate:.1f}%\n\n"
            
            # القسم 2: الأداء المالي
            pnl_indicator = "🟢" if total_pnl > 0 else "🔴"
            report += "💰 FINANCIAL PERFORMANCE\n"
            report += f"Total P&L: {self.format_number(total_pnl, 2):+} USDT {pnl_indicator}\n"
            report += f"Avg Win: {self.format_number(avg_win, 2):+} USDT\n"
            report += f"Avg Loss: {self.format_number(avg_loss, 2):+} USDT\n"
            
            if avg_loss != 0:
                profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if losing_trades else 0
                report += f"Profit Factor: {profit_factor:.2f}\n"
            
            report += "\n"
            
            # القسم 3: حسب نوع السوق
            report += "📊 BY MARKET TYPE\n"
            spot_indicator = "🟢" if spot_pnl > 0 else "🔴"
            futures_indicator = "🟢" if futures_pnl > 0 else "🔴"
            report += f"Spot: {len(spot_trades)} trades • P&L: {self.format_number(spot_pnl, 2):+} USDT {spot_indicator}\n"
            report += f"Futures: {len(futures_trades)} trades • P&L: {self.format_number(futures_pnl, 2):+} USDT {futures_indicator}\n\n"
            
            # القسم 4: حسب نوع الحساب
            report += "💼 BY ACCOUNT TYPE\n"
            real_indicator = "🟢" if real_pnl > 0 else "🔴"
            demo_indicator = "🟢" if demo_pnl > 0 else "🔴"
            report += f"Real: {len(real_trades)} trades • P&L: {self.format_number(real_pnl, 2):+} USDT {real_indicator}\n"
            report += f"Demo: {len(demo_trades)} trades • P&L: {self.format_number(demo_pnl, 2):+} USDT {demo_indicator}\n\n"
            
            # القسم 5: أفضل وأسوأ صفقة
            if closed_trades:
                best_trade = max(closed_trades, key=lambda t: t.get('pnl_value', t.get('pnl', 0)))
                worst_trade = min(closed_trades, key=lambda t: t.get('pnl_value', t.get('pnl', 0)))
                
                report += "🏆 BEST & WORST TRADES\n"
                report += f"Best: {best_trade['symbol']} • {self.format_number(best_trade.get('pnl_value', best_trade.get('pnl', 0)), 2):+} USDT\n"
                report += f"Worst: {worst_trade['symbol']} • {self.format_number(worst_trade.get('pnl_value', worst_trade.get('pnl', 0)), 2):+} USDT\n"
            
            report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في توليد التقرير المفصل: {e}")
            return "خطأ في توليد التقرير"
    
    def get_trade_history(self, user_id: int, filters: Dict = None) -> List[Dict]:
        """جلب سجل الصفقات مع الفلاتر"""
        try:
            return self.db_manager.get_user_trade_history(user_id, filters)
        except Exception as e:
            logger.error(f"خطأ في جلب سجل الصفقات: {e}")
            return []


# دالة مساعدة
def create_trade_history_display(db_manager):
    """إنشاء مثيل من عرض سجل الصفقات"""
    return TradeHistoryDisplay(db_manager)

