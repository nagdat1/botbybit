"""
🎨 واجهة المحفظة المتطورة
Advanced Portfolio Interface

واجهة مستخدم متطورة لنظام المحفظة تتضمن:
- عرض تفاعلي للمحفظة
- تحليلات بصرية
- إدارة ذكية للصفقات
- تقارير مفصلة
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class PortfolioInterface:
    """واجهة المحفظة المتطورة"""
    
    def __init__(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager
    
    async def create_main_portfolio_menu(self, user_id: int, account_type: str = "demo") -> Dict:
        """إنشاء القائمة الرئيسية للمحفظة"""
        try:
            # الحصول على ملخص المحفظة
            summary = await self.portfolio_manager.get_portfolio_summary(account_type)
            
            # إنشاء الرسالة الرئيسية
            message = await self._format_portfolio_summary(summary, account_type)
            
            # إنشاء الأزرار التفاعلية
            keyboard = await self._create_main_keyboard(account_type)
            
            return {
                'message': message,
                'keyboard': keyboard,
                'parse_mode': 'Markdown'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء قائمة المحفظة الرئيسية: {e}")
            return {
                'message': "❌ خطأ في تحميل المحفظة",
                'keyboard': [],
                'parse_mode': 'Markdown'
            }
    
    async def create_analytics_dashboard(self, user_id: int, account_type: str = "demo") -> Dict:
        """إنشاء لوحة التحليلات"""
        try:
            # الحصول على تحليلات الأداء
            analytics = await self.portfolio_manager.get_performance_analytics(account_type)
            
            # إنشاء الرسالة
            message = await self._format_analytics_dashboard(analytics, account_type)
            
            # إنشاء الأزرار
            keyboard = await self._create_analytics_keyboard()
            
            return {
                'message': message,
                'keyboard': keyboard,
                'parse_mode': 'Markdown'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة التحليلات: {e}")
            return {
                'message': "❌ خطأ في تحميل التحليلات",
                'keyboard': [],
                'parse_mode': 'Markdown'
            }
    
    async def create_positions_view(self, user_id: int, account_type: str = "demo") -> Dict:
        """إنشاء عرض الصفقات"""
        try:
            # الحصول على الصفقات المفتوحة
            open_positions = [p for p in self.portfolio_manager.positions.values() if p.account_type == account_type]
            
            # إنشاء الرسالة
            message = await self._format_positions_view(open_positions, account_type)
            
            # إنشاء الأزرار
            keyboard = await self._create_positions_keyboard(open_positions)
            
            return {
                'message': message,
                'keyboard': keyboard,
                'parse_mode': 'Markdown'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء عرض الصفقات: {e}")
            return {
                'message': "❌ خطأ في تحميل الصفقات",
                'keyboard': [],
                'parse_mode': 'Markdown'
            }
    
    async def create_recommendations_view(self, user_id: int, account_type: str = "demo") -> Dict:
        """إنشاء عرض التوصيات"""
        try:
            # الحصول على التوصيات
            recommendations = await self.portfolio_manager.get_portfolio_recommendations(account_type)
            
            # إنشاء الرسالة
            message = await self._format_recommendations_view(recommendations, account_type)
            
            # إنشاء الأزرار
            keyboard = await self._create_recommendations_keyboard()
            
            return {
                'message': message,
                'keyboard': keyboard,
                'parse_mode': 'Markdown'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء عرض التوصيات: {e}")
            return {
                'message': "❌ خطأ في تحميل التوصيات",
                'keyboard': [],
                'parse_mode': 'Markdown'
            }
    
    async def _format_portfolio_summary(self, summary, account_type: str) -> str:
        """تنسيق ملخص المحفظة"""
        try:
            # تحديد نوع الحساب
            account_emoji = "🟢" if account_type == "demo" else "🔵"
            account_name = "تجريبي" if account_type == "demo" else "حقيقي"
            
            # تحديد حالة الأداء
            if summary.pnl_percentage > 5:
                performance_emoji = "🚀"
                performance_status = "ممتاز"
            elif summary.pnl_percentage > 0:
                performance_emoji = "📈"
                performance_status = "جيد"
            elif summary.pnl_percentage > -5:
                performance_emoji = "📊"
                performance_status = "متوسط"
            else:
                performance_emoji = "📉"
                performance_status = "يحتاج تحسين"
            
            message = f"""
🎯 **المحفظة المتطورة** {account_emoji}

📊 **الحساب:** {account_name.upper()}
📈 **الأداء:** {performance_emoji} {performance_status}
🕒 **آخر تحديث:** {summary.last_updated.strftime('%Y-%m-%d %H:%M')}

💰 **القيمة الإجمالية:**
• القيمة السوقية: {summary.total_value:.2f} USDT
• المبلغ المستثمر: {summary.total_invested:.2f} USDT
• الربح/الخسارة: {summary.total_pnl:+.2f} USDT ({summary.pnl_percentage:+.2f}%)

📊 **إحصائيات التداول:**
• الصفقات المفتوحة: {summary.open_positions}
• الصفقات المغلقة: {summary.closed_positions}
• معدل النجاح: {summary.win_rate:.1f}%
• أفضل صفقة: {summary.best_trade:+.2f} USDT
• أسوأ صفقة: {summary.worst_trade:+.2f} USDT

🎯 **مؤشرات الأداء:**
• متوسط الصفقة: {summary.avg_trade:+.2f} USDT
• نسبة شارب: {summary.sharpe_ratio:.2f}
• أقصى انخفاض: {summary.max_drawdown:.2f} USDT
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق ملخص المحفظة: {e}")
            return "❌ خطأ في تنسيق ملخص المحفظة"
    
    async def _format_analytics_dashboard(self, analytics: Dict, account_type: str) -> str:
        """تنسيق لوحة التحليلات"""
        try:
            if not analytics:
                return "📊 **لوحة التحليلات**\n\n❌ لا توجد بيانات كافية للتحليل"
            
            message = f"""
📊 **لوحة التحليلات المتطورة**

📈 **الأداء العام:**
• إجمالي الصفقات: {analytics.get('total_trades', 0)}
• الصفقات الرابحة: {analytics.get('winning_trades', 0)}
• الصفقات الخاسرة: {analytics.get('losing_trades', 0)}
• متوسط الربح: {analytics.get('avg_win', 0):.2f} USDT
• متوسط الخسارة: {analytics.get('avg_loss', 0):.2f} USDT
• عامل الربح: {analytics.get('profit_factor', 0):.2f}

🎯 **تحليل العملات:**
"""
            
            # إضافة تحليل العملات
            currency_analysis = analytics.get('currency_analysis', {})
            for symbol, stats in list(currency_analysis.items())[:5]:  # أفضل 5 عملات
                message += f"• {symbol}: {stats['total_pnl']:+.2f} USDT ({stats['win_rate']:.1f}% نجاح)\n"
            
            message += f"\n🏪 **تحليل الأسواق:**\n"
            
            # إضافة تحليل الأسواق
            market_analysis = analytics.get('market_analysis', {})
            for market_type, stats in market_analysis.items():
                market_name = "السبوت" if market_type == "spot" else "الفيوتشر"
                message += f"• {market_name}: {stats['total_pnl']:+.2f} USDT ({stats['win_rate']:.1f}% نجاح)\n"
            
            message += f"\n⚠️ **تحليل المخاطر:**\n"
            
            # إضافة تحليل المخاطر
            risk_analysis = analytics.get('risk_analysis', {})
            if risk_analysis:
                message += f"• درجة المخاطر: {risk_analysis.get('risk_score', 0):.1f}/100\n"
                message += f"• الانحراف المعياري: {risk_analysis.get('standard_deviation', 0):.2f}\n"
                message += f"• VaR 95%: {risk_analysis.get('var_95', 0):.2f} USDT\n"
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق لوحة التحليلات: {e}")
            return "❌ خطأ في تنسيق لوحة التحليلات"
    
    async def _format_positions_view(self, positions: List, account_type: str) -> str:
        """تنسيق عرض الصفقات"""
        try:
            if not positions:
                return f"📊 **الصفقات المفتوحة**\n\n📭 لا توجد صفقات مفتوحة حالياً"
            
            message = f"📊 **الصفقات المفتوحة** ({len(positions)} صفقة)\n\n"
            
            # ترتيب الصفقات حسب الربح/الخسارة
            sorted_positions = sorted(positions, key=lambda p: p.pnl_absolute, reverse=True)
            
            for i, position in enumerate(sorted_positions[:10], 1):  # أفضل 10 صفقات
                # تحديد الرمز حسب نوع السوق
                market_emoji = "🟢" if position.market_type == "spot" else "⚡"
                side_emoji = "📈" if position.side.lower() == "buy" else "📉"
                pnl_emoji = "🟢" if position.pnl_absolute > 0 else "🔴" if position.pnl_absolute < 0 else "⚪"
                
                message += f"{i}. {market_emoji} **{position.symbol}** {side_emoji}\n"
                message += f"   💲 السعر: {position.entry_price:.6f} → {position.current_price:.6f}\n"
                message += f"   💰 الكمية: {position.quantity:.6f}\n"
                message += f"   {pnl_emoji} الربح/الخسارة: {position.pnl_absolute:+.2f} USDT ({position.pnl_percentage:+.2f}%)\n"
                message += f"   🆔 المعرف: {position.id}\n\n"
            
            if len(positions) > 10:
                message += f"... و {len(positions) - 10} صفقة أخرى"
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق عرض الصفقات: {e}")
            return "❌ خطأ في تنسيق عرض الصفقات"
    
    async def _format_recommendations_view(self, recommendations: List, account_type: str) -> str:
        """تنسيق عرض التوصيات"""
        try:
            if not recommendations:
                return f"💡 **التوصيات الذكية**\n\n✅ محفظتك في حالة ممتازة! لا توجد توصيات حالياً."
            
            message = f"💡 **التوصيات الذكية** ({len(recommendations)} توصية)\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                # تحديد رمز الأولوية
                priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                type_emoji = "💰" if rec['type'] == 'take_profit' else "⚠️" if rec['type'] == 'risk_management' else "📊"
                
                message += f"{i}. {priority_emoji} {type_emoji} **{rec['title']}**\n"
                message += f"   📝 {rec['description']}\n"
                message += f"   💡 {rec['action']}\n\n"
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق عرض التوصيات: {e}")
            return "❌ خطأ في تنسيق عرض التوصيات"
    
    async def _create_main_keyboard(self, account_type: str) -> List[List[InlineKeyboardButton]]:
        """إنشاء لوحة المفاتيح الرئيسية"""
        try:
            keyboard = [
                [InlineKeyboardButton("📊 لوحة التحليلات", callback_data="portfolio_analytics")],
                [InlineKeyboardButton("📈 الصفقات المفتوحة", callback_data="portfolio_positions")],
                [InlineKeyboardButton("💡 التوصيات الذكية", callback_data="portfolio_recommendations")],
                [InlineKeyboardButton("📋 تقرير مفصل", callback_data="portfolio_report")],
                [InlineKeyboardButton("⚙️ إعدادات المحفظة", callback_data="portfolio_settings")],
                [InlineKeyboardButton("🔄 تحديث المحفظة", callback_data="portfolio_refresh")]
            ]
            
            return keyboard
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة المفاتيح الرئيسية: {e}")
            return []
    
    async def _create_analytics_keyboard(self) -> List[List[InlineKeyboardButton]]:
        """إنشاء لوحة مفاتيح التحليلات"""
        try:
            keyboard = [
                [InlineKeyboardButton("📊 تحليل الأداء", callback_data="analytics_performance")],
                [InlineKeyboardButton("🎯 تحليل العملات", callback_data="analytics_currencies")],
                [InlineKeyboardButton("⚠️ تحليل المخاطر", callback_data="analytics_risk")],
                [InlineKeyboardButton("📈 الرسوم البيانية", callback_data="analytics_charts")],
                [InlineKeyboardButton("🔙 العودة للمحفظة", callback_data="portfolio_main")]
            ]
            
            return keyboard
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة مفاتيح التحليلات: {e}")
            return []
    
    async def _create_positions_keyboard(self, positions: List) -> List[List[InlineKeyboardButton]]:
        """إنشاء لوحة مفاتيح الصفقات"""
        try:
            keyboard = []
            
            # أزرار للصفقات المفتوحة
            if positions:
                keyboard.append([InlineKeyboardButton("🎯 إدارة الصفقات", callback_data="positions_manage")])
                keyboard.append([InlineKeyboardButton("📊 إغلاق جزئي", callback_data="positions_partial_close")])
                keyboard.append([InlineKeyboardButton("❌ إغلاق جميع الصفقات", callback_data="positions_close_all")])
            
            keyboard.append([InlineKeyboardButton("🔙 العودة للمحفظة", callback_data="portfolio_main")])
            
            return keyboard
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة مفاتيح الصفقات: {e}")
            return []
    
    async def _create_recommendations_keyboard(self) -> List[List[InlineKeyboardButton]]:
        """إنشاء لوحة مفاتيح التوصيات"""
        try:
            keyboard = [
                [InlineKeyboardButton("✅ تطبيق التوصيات", callback_data="recommendations_apply")],
                [InlineKeyboardButton("📊 تحليل مفصل", callback_data="recommendations_analyze")],
                [InlineKeyboardButton("🔙 العودة للمحفظة", callback_data="portfolio_main")]
            ]
            
            return keyboard
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة مفاتيح التوصيات: {e}")
            return []

# إنشاء مثيل عام للواجهة
from ultimate_portfolio_manager import ultimate_portfolio_manager
portfolio_interface = PortfolioInterface(ultimate_portfolio_manager)
