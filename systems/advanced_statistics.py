#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الإحصائيات المتقدم مع تحليل الأداء الشامل
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class AdvancedStatistics:
    """نظام إحصائيات متقدم مع تحليل شامل"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def generate_ascii_chart(self, data_points: List[float], width: int = 20, height: int = 5) -> str:
        """إنشاء رسم بياني نصي بسيط"""
        try:
            if not data_points or len(data_points) < 2:
                return "📊 لا توجد بيانات كافية"
            
            # تطبيع البيانات
            min_val = min(data_points)
            max_val = max(data_points)
            
            if max_val == min_val:
                return "━" * width + "\n" + "📊 القيم ثابتة"
            
            # إنشاء الرسم
            chart_lines = []
            
            # عنوان الرسم
            chart_lines.append(f"📈 Max: {max_val:,.2f}")
            
            # الرسم البياني
            normalized = [(v - min_val) / (max_val - min_val) for v in data_points]
            
            # إنشاء خط الاتجاه
            trend_line = ""
            for i, val in enumerate(normalized):
                if i == 0:
                    trend_line += "●"
                else:
                    prev_val = normalized[i-1]
                    if val > prev_val:
                        trend_line += "╱"
                    elif val < prev_val:
                        trend_line += "╲"
                    else:
                        trend_line += "━"
            
            chart_lines.append(trend_line[:width])
            chart_lines.append(f"📉 Min: {min_val:,.2f}")
            
            return "\n".join(chart_lines)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الرسم البياني: {e}")
            return "❌ خطأ في الرسم"
    
    def calculate_trade_statistics(self, user_id: int, account_type: str, days: int = 30) -> Dict:
        """حساب إحصائيات الصفقات المتقدمة"""
        try:
            from datetime import datetime, timedelta
            
            # جلب الصفقات المغلقة
            filters = {
                'status': 'CLOSED',
                'account_type': account_type,
                'days': days
            }
            
            trades = self.db_manager.get_user_trade_history(user_id, filters)
            
            if not trades:
                return self._empty_statistics()
            
            # تصنيف الصفقات
            winning_trades = []
            losing_trades = []
            breakeven_trades = []
            
            spot_trades = []
            futures_trades = []
            
            total_volume = 0.0
            total_pnl = 0.0
            
            for trade in trades:
                pnl = trade.get('pnl_value', trade.get('pnl', 0))
                entry_price = trade.get('entry_price', 0)
                quantity = trade.get('quantity', 0)
                market_type = trade.get('market_type', 'spot')
                
                # حساب الحجم
                volume = entry_price * quantity
                total_volume += volume
                total_pnl += pnl
                
                # تصنيف حسب الربح/الخسارة
                if pnl > 0:
                    winning_trades.append(trade)
                elif pnl < 0:
                    losing_trades.append(trade)
                else:
                    breakeven_trades.append(trade)
                
                # تصنيف حسب نوع السوق
                if market_type == 'spot':
                    spot_trades.append(trade)
                else:
                    futures_trades.append(trade)
            
            # حساب المقاييس
            total_trades = len(trades)
            win_count = len(winning_trades)
            loss_count = len(losing_trades)
            
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
            
            # أفضل وأسوأ صفقة
            best_trade = max(trades, key=lambda t: t.get('pnl_value', t.get('pnl', 0)))
            worst_trade = min(trades, key=lambda t: t.get('pnl_value', t.get('pnl', 0)))
            
            # متوسط الربح والخسارة
            avg_win = (sum(t.get('pnl_value', t.get('pnl', 0)) for t in winning_trades) / win_count) if win_count > 0 else 0.0
            avg_loss = (sum(t.get('pnl_value', t.get('pnl', 0)) for t in losing_trades) / loss_count) if loss_count > 0 else 0.0
            
            # Profit Factor
            total_wins = sum(t.get('pnl_value', t.get('pnl', 0)) for t in winning_trades)
            total_losses = abs(sum(t.get('pnl_value', t.get('pnl', 0)) for t in losing_trades))
            profit_factor = (total_wins / total_losses) if total_losses > 0 else 0.0
            
            # متوسط مدة الصفقة
            durations = []
            for trade in trades:
                open_time = trade.get('open_time')
                close_time = trade.get('close_time')
                if open_time and close_time:
                    try:
                        dt_open = datetime.fromisoformat(open_time.replace('Z', '+00:00'))
                        dt_close = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                        duration = (dt_close - dt_open).total_seconds() / 3600  # ساعات
                        durations.append(duration)
                    except:
                        pass
            
            avg_duration_hours = (sum(durations) / len(durations)) if durations else 0.0
            
            # تحليل حسب الرمز
            symbol_stats = {}
            for trade in trades:
                symbol = trade.get('symbol', 'UNKNOWN')
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'count': 0,
                        'wins': 0,
                        'losses': 0,
                        'total_pnl': 0.0
                    }
                
                symbol_stats[symbol]['count'] += 1
                pnl = trade.get('pnl_value', trade.get('pnl', 0))
                symbol_stats[symbol]['total_pnl'] += pnl
                
                if pnl > 0:
                    symbol_stats[symbol]['wins'] += 1
                elif pnl < 0:
                    symbol_stats[symbol]['losses'] += 1
            
            # ترتيب الرموز حسب الربحية
            top_symbols = sorted(
                symbol_stats.items(),
                key=lambda x: x[1]['total_pnl'],
                reverse=True
            )[:5]
            
            return {
                'total_trades': total_trades,
                'winning_trades': win_count,
                'losing_trades': loss_count,
                'breakeven_trades': len(breakeven_trades),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_volume': total_volume,
                'best_trade': {
                    'symbol': best_trade.get('symbol'),
                    'pnl': best_trade.get('pnl_value', best_trade.get('pnl', 0)),
                    'date': best_trade.get('close_time', '')
                },
                'worst_trade': {
                    'symbol': worst_trade.get('symbol'),
                    'pnl': worst_trade.get('pnl_value', worst_trade.get('pnl', 0)),
                    'date': worst_trade.get('close_time', '')
                },
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'avg_duration_hours': avg_duration_hours,
                'spot_trades': len(spot_trades),
                'futures_trades': len(futures_trades),
                'top_symbols': top_symbols,
                'symbol_stats': symbol_stats
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب إحصائيات الصفقات: {e}")
            return self._empty_statistics()
    
    def _empty_statistics(self) -> Dict:
        """إرجاع إحصائيات فارغة"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'breakeven_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'total_volume': 0.0,
            'best_trade': {'symbol': 'N/A', 'pnl': 0.0, 'date': ''},
            'worst_trade': {'symbol': 'N/A', 'pnl': 0.0, 'date': ''},
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'avg_duration_hours': 0.0,
            'spot_trades': 0,
            'futures_trades': 0,
            'top_symbols': [],
            'symbol_stats': {}
        }
    
    def format_statistics_message(self, user_id: int, account_type: str, days: int = 30) -> Tuple[str, InlineKeyboardMarkup]:
        """تنسيق رسالة الإحصائيات الشاملة"""
        try:
            # جلب الإحصائيات
            trade_stats = self.calculate_trade_statistics(user_id, account_type, days)
            portfolio_stats = self.db_manager.get_portfolio_statistics(user_id, account_type, days)
            
            # المؤشرات
            account_indicator = "💼 حساب حقيقي" if account_type == 'real' else "🎮 حساب تجريبي"
            pnl_indicator = "🟢" if trade_stats['total_pnl'] > 0 else ("🔴" if trade_stats['total_pnl'] < 0 else "⚪")
            
            # بناء الرسالة
            message = f"""{account_indicator}
📊 ADVANCED STATISTICS ({days} يوم)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **أداء المحفظة:**
• العائد الإجمالي: {portfolio_stats.get('total_return', 0):+,.2f} USDT ({portfolio_stats.get('total_return_percent', 0):+.2f}%)
• أعلى رصيد: {portfolio_stats.get('max_balance', 0):,.2f} USDT
• أدنى رصيد: {portfolio_stats.get('min_balance', 0):,.2f} USDT
• Max Drawdown: {portfolio_stats.get('max_drawdown', 0):.2f}%

📊 **مقاييس الأداء:**
• متوسط العائد اليومي: {portfolio_stats.get('avg_daily_return', 0):+.2f}%
• التقلب (Volatility): {portfolio_stats.get('volatility', 0):.2f}%
• Sharpe Ratio: {portfolio_stats.get('sharpe_ratio', 0):.2f}
• أيام رابحة: {portfolio_stats.get('profitable_days', 0)} | خاسرة: {portfolio_stats.get('losing_days', 0)}

💼 **إحصائيات الصفقات:**
• إجمالي الصفقات: {trade_stats['total_trades']}
• معدل الفوز: {trade_stats['win_rate']:.1f}% ({trade_stats['winning_trades']}W / {trade_stats['losing_trades']}L)
• إجمالي P&L: {trade_stats['total_pnl']:+,.2f} USDT {pnl_indicator}
• حجم التداول: {trade_stats['total_volume']:,.2f} USDT

💰 **تحليل الربح/الخسارة:**
• متوسط الربح: {trade_stats['avg_win']:+,.2f} USDT
• متوسط الخسارة: {trade_stats['avg_loss']:+,.2f} USDT
• Profit Factor: {trade_stats['profit_factor']:.2f}

🏆 **أفضل/أسوأ صفقة:**
• أفضل: {trade_stats['best_trade']['symbol']} ({trade_stats['best_trade']['pnl']:+,.2f} USDT)
• أسوأ: {trade_stats['worst_trade']['symbol']} ({trade_stats['worst_trade']['pnl']:+,.2f} USDT)

📊 **توزيع الصفقات:**
• Spot: {trade_stats['spot_trades']} | Futures: {trade_stats['futures_trades']}
• متوسط المدة: {trade_stats['avg_duration_hours']:.1f} ساعة
"""
            
            # إضافة أفضل الرموز
            if trade_stats['top_symbols']:
                message += "\n🌟 **أفضل 5 رموز:**\n"
                for symbol, stats in trade_stats['top_symbols']:
                    win_rate_symbol = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
                    indicator = "🟢" if stats['total_pnl'] > 0 else "🔴"
                    message += f"{indicator} {symbol}: {stats['total_pnl']:+,.2f} USDT ({win_rate_symbol:.0f}%)\n"
            
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            # الأزرار
            keyboard = [
                [
                    InlineKeyboardButton("📅 7 أيام", callback_data=f"stats_{account_type}_7"),
                    InlineKeyboardButton("📅 30 يوم", callback_data=f"stats_{account_type}_30"),
                    InlineKeyboardButton("📅 90 يوم", callback_data=f"stats_{account_type}_90")
                ],
                [
                    InlineKeyboardButton("📊 تطور المحفظة", callback_data=f"portfolio_evolution_{account_type}_{days}"),
                ],
                [
                    InlineKeyboardButton("🔄 تحديث", callback_data=f"stats_{account_type}_{days}"),
                    InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
                ]
            ]
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة الإحصائيات: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return "❌ خطأ في تحميل الإحصائيات", InlineKeyboardMarkup([[]])
    
    def format_portfolio_evolution_message(self, user_id: int, account_type: str, days: int = 30) -> Tuple[str, InlineKeyboardMarkup]:
        """تنسيق رسالة تطور المحفظة مع رسم بياني"""
        try:
            # جلب تطور المحفظة
            snapshots = self.db_manager.get_portfolio_evolution(user_id, account_type, days)
            
            if not snapshots:
                return "📊 لا توجد بيانات لتطور المحفظة بعد", InlineKeyboardMarkup([[]])
            
            # استخراج البيانات
            dates = [s['date'] for s in snapshots]
            balances = [s['balance'] for s in snapshots]
            
            # حساب التغيرات
            initial_balance = balances[0]
            current_balance = balances[-1]
            change = current_balance - initial_balance
            change_percent = (change / initial_balance * 100) if initial_balance > 0 else 0.0
            
            # المؤشرات
            account_indicator = "💼 حساب حقيقي" if account_type == 'real' else "🎮 حساب تجريبي"
            trend_indicator = "📈" if change > 0 else ("📉" if change < 0 else "➡️")
            color_indicator = "🟢" if change > 0 else ("🔴" if change < 0 else "⚪")
            
            # إنشاء الرسم البياني
            chart = self.generate_ascii_chart(balances, width=25, height=5)
            
            # بناء الرسالة
            message = f"""{account_indicator}
📊 PORTFOLIO EVOLUTION ({days} يوم)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chart}

💰 **الرصيد:**
• البداية: {initial_balance:,.2f} USDT
• الحالي: {current_balance:,.2f} USDT
• التغير: {change:+,.2f} USDT ({change_percent:+.2f}%) {color_indicator}

{trend_indicator} **الاتجاه:** {"صاعد" if change > 0 else ("هابط" if change < 0 else "مستقر")}

📅 **الفترة:**
• من: {dates[0]}
• إلى: {dates[-1]}
• عدد الأيام: {len(snapshots)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # إضافة تفاصيل آخر 5 أيام
            if len(snapshots) >= 5:
                message += "\n📊 **آخر 5 أيام:**\n"
                for snapshot in snapshots[-5:]:
                    day_balance = snapshot['balance']
                    day_date = snapshot['date']
                    message += f"• {day_date}: {day_balance:,.2f} USDT\n"
            
            # الأزرار
            keyboard = [
                [
                    InlineKeyboardButton("📅 7 أيام", callback_data=f"portfolio_evolution_{account_type}_7"),
                    InlineKeyboardButton("📅 30 يوم", callback_data=f"portfolio_evolution_{account_type}_30"),
                ],
                [
                    InlineKeyboardButton("📅 90 يوم", callback_data=f"portfolio_evolution_{account_type}_90"),
                    InlineKeyboardButton("📅 365 يوم", callback_data=f"portfolio_evolution_{account_type}_365")
                ],
                [
                    InlineKeyboardButton("📊 الإحصائيات", callback_data=f"stats_{account_type}_{days}"),
                    InlineKeyboardButton("🔄 تحديث", callback_data=f"portfolio_evolution_{account_type}_{days}")
                ],
                [
                    InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
                ]
            ]
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق تطور المحفظة: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return "❌ خطأ في تحميل تطور المحفظة", InlineKeyboardMarkup([[]])
    
    def save_daily_snapshot(self, user_id: int, account_type: str) -> bool:
        """حفظ لقطة يومية للمحفظة (يتم استدعاؤها تلقائياً)"""
        try:
            # جلب بيانات المستخدم
            user_data = self.db_manager.get_user(user_id)
            if not user_data:
                return False
            
            # جلب الصفقات المفتوحة والمغلقة
            open_positions = self.db_manager.get_user_orders(user_id, status='OPEN')
            closed_trades = self.db_manager.get_user_trade_history(user_id, {'status': 'CLOSED', 'account_type': account_type})
            
            # حساب الإحصائيات
            winning_trades = sum(1 for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) > 0))
            losing_trades = sum(1 for t in closed_trades if (t.get('pnl_value', t.get('pnl', 0)) < 0))
            total_pnl = sum(t.get('pnl_value', t.get('pnl', 0)) for t in closed_trades)
            total_volume = sum(t.get('entry_price', 0) * t.get('quantity', 0) for t in closed_trades)
            
            # حساب الرصيد Spot/Futures (من الصفقات المفتوحة)
            spot_balance = 0.0
            futures_balance = 0.0
            
            for pos in open_positions:
                market_type = pos.get('market_type', 'spot')
                value = pos.get('entry_price', 0) * pos.get('quantity', 0)
                
                if market_type == 'spot':
                    spot_balance += value
                else:
                    futures_balance += value
            
            # بيانات اللقطة
            snapshot_data = {
                'balance': user_data.get('balance', 10000.0),
                'total_pnl': total_pnl,
                'open_positions_count': len(open_positions),
                'closed_trades_count': len(closed_trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_volume': total_volume,
                'spot_balance': spot_balance,
                'futures_balance': futures_balance
            }
            
            # حفظ اللقطة
            success = self.db_manager.save_portfolio_snapshot(user_id, account_type, snapshot_data)
            
            if success:
                logger.info(f"✅ تم حفظ لقطة المحفظة اليومية للمستخدم {user_id} ({account_type})")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ اللقطة اليومية: {e}")
            return False

