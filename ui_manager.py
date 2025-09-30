#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الواجهة الديناميكية مع InlineKeyboard
يدعم واجهات مخصصة لكل مستخدم
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from user_manager import user_manager
from order_manager import order_manager
from api_manager import api_manager

logger = logging.getLogger(__name__)

class UIManager:
    """مدير الواجهة الديناميكية"""
    
    def __init__(self):
        self.user_states: Dict[int, str] = {}
        self.user_context: Dict[int, Dict] = {}
    
    def get_main_menu_keyboard(self, user_id: int) -> ReplyKeyboardMarkup:
        """الحصول على لوحة المفاتيح الرئيسية"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            is_active = user_env.is_active
            has_api = user_env.has_api_keys()
            
            # الأزرار الأساسية
            keyboard = [
                [KeyboardButton("🔗 الربط"), KeyboardButton("⚙️ الإعدادات")],
                [KeyboardButton("💰 الرصيد"), KeyboardButton("📊 الصفقات المفتوحة")],
                [KeyboardButton("📈 تاريخ التداول"), KeyboardButton("📊 الإحصائيات")]
            ]
            
            # أزرار التحكم في البوت
            if has_api:
                if is_active:
                    keyboard.append([KeyboardButton("⏹️ إيقاف البوت")])
                else:
                    keyboard.append([KeyboardButton("▶️ تشغيل البوت")])
            else:
                keyboard.append([KeyboardButton("🔗 ربط مفاتيح API")])
            
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة المفاتيح الرئيسية للمستخدم {user_id}: {e}")
            return ReplyKeyboardMarkup([], resize_keyboard=True)
    
    def get_settings_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح الإعدادات"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            
            keyboard = [
                [InlineKeyboardButton("💰 مبلغ التداول", callback_data=f"set_amount_{user_id}")],
                [InlineKeyboardButton("🏪 نوع السوق", callback_data=f"set_market_{user_id}")],
                [InlineKeyboardButton("⚡ الرافعة المالية", callback_data=f"set_leverage_{user_id}")],
                [InlineKeyboardButton("🎯 أهداف الأرباح", callback_data=f"set_tp_{user_id}")],
                [InlineKeyboardButton("🛡️ وقف الخسارة", callback_data=f"set_sl_{user_id}")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"main_menu_{user_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح الإعدادات للمستخدم {user_id}: {e}")
            return InlineKeyboardMarkup([])
    
    def get_orders_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح الصفقات المفتوحة"""
        try:
            orders = order_manager.get_user_orders(user_id)
            keyboard = []
            
            for order in orders:
                order_id = order['order_id']
                symbol = order['symbol']
                side = order['side']
                pnl = order['unrealized_pnl']
                
                # زر الصفقة الرئيسي
                pnl_text = f"({pnl:+.2f})" if pnl != 0 else ""
                order_button = InlineKeyboardButton(
                    f"📊 {symbol} {side.upper()} {pnl_text}",
                    callback_data=f"order_details_{order_id}"
                )
                keyboard.append([order_button])
            
            # أزرار إضافية
            if orders:
                keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data=f"refresh_orders_{user_id}")])
            
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data=f"main_menu_{user_id}")])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح الصفقات للمستخدم {user_id}: {e}")
            return InlineKeyboardMarkup([])
    
    def get_order_details_keyboard(self, order_id: str) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح تفاصيل الصفقة"""
        try:
            order = order_manager.get_order(order_id)
            if not order:
                return InlineKeyboardMarkup([])
            
            user_id = order['user_id']
            keyboard = []
            
            # أزرار الإدارة الأساسية
            keyboard.append([
                InlineKeyboardButton("📅 تاريخ الصفقة", callback_data=f"order_time_{order_id}"),
                InlineKeyboardButton("💰 إغلاق جزئي", callback_data=f"partial_close_{order_id}")
            ])
            
            # أزرار أهداف الأرباح
            tps = order.get('tps', [])
            if len(tps) < 3:  # يمكن إضافة حتى 3 أهداف ربح
                keyboard.append([
                    InlineKeyboardButton("🎯 TP1", callback_data=f"add_tp_{order_id}_1"),
                    InlineKeyboardButton("🎯 TP2", callback_data=f"add_tp_{order_id}_2"),
                    InlineKeyboardButton("🎯 TP3", callback_data=f"add_tp_{order_id}_3")
                ])
            else:
                # عرض الأهداف الموجودة
                tp_buttons = []
                for i, tp in enumerate(tps[:3], 1):
                    tp_buttons.append(InlineKeyboardButton(f"TP{i}: {tp['percentage']}%", callback_data=f"tp_details_{order_id}_{i}"))
                keyboard.append(tp_buttons)
            
            # أزرار وقف الخسارة والإغلاق
            keyboard.append([
                InlineKeyboardButton("🛡️ Stop Loss", callback_data=f"set_sl_{order_id}"),
                InlineKeyboardButton("❌ إلغاء الصفقة", callback_data=f"close_order_{order_id}")
            ])
            
            # زر العودة
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data=f"user_orders_{user_id}")])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح تفاصيل الصفقة {order_id}: {e}")
            return InlineKeyboardMarkup([])
    
    def get_partial_close_keyboard(self, order_id: str) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح الإغلاق الجزئي"""
        try:
            keyboard = [
                [InlineKeyboardButton("25%", callback_data=f"partial_25_{order_id}")],
                [InlineKeyboardButton("50%", callback_data=f"partial_50_{order_id}")],
                [InlineKeyboardButton("75%", callback_data=f"partial_75_{order_id}")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"order_details_{order_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح الإغلاق الجزئي: {e}")
            return InlineKeyboardMarkup([])
    
    def get_tp_settings_keyboard(self, order_id: str, tp_level: int) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح إعدادات هدف الربح"""
        try:
            keyboard = [
                [InlineKeyboardButton("1%", callback_data=f"tp_percent_{order_id}_{tp_level}_1")],
                [InlineKeyboardButton("2%", callback_data=f"tp_percent_{order_id}_{tp_level}_2")],
                [InlineKeyboardButton("3%", callback_data=f"tp_percent_{order_id}_{tp_level}_3")],
                [InlineKeyboardButton("5%", callback_data=f"tp_percent_{order_id}_{tp_level}_5")],
                [InlineKeyboardButton("10%", callback_data=f"tp_percent_{order_id}_{tp_level}_10")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"order_details_{order_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح إعدادات TP: {e}")
            return InlineKeyboardMarkup([])
    
    def get_sl_settings_keyboard(self, order_id: str) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح إعدادات وقف الخسارة"""
        try:
            keyboard = [
                [InlineKeyboardButton("1%", callback_data=f"sl_percent_{order_id}_1")],
                [InlineKeyboardButton("2%", callback_data=f"sl_percent_{order_id}_2")],
                [InlineKeyboardButton("3%", callback_data=f"sl_percent_{order_id}_3")],
                [InlineKeyboardButton("5%", callback_data=f"sl_percent_{order_id}_5")],
                [InlineKeyboardButton("10%", callback_data=f"sl_percent_{order_id}_10")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"order_details_{order_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح إعدادات SL: {e}")
            return InlineKeyboardMarkup([])
    
    def get_market_type_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح نوع السوق"""
        try:
            keyboard = [
                [InlineKeyboardButton("🏪 Spot", callback_data=f"market_spot_{user_id}")],
                [InlineKeyboardButton("📈 Futures", callback_data=f"market_futures_{user_id}")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"settings_{user_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح نوع السوق: {e}")
            return InlineKeyboardMarkup([])
    
    def get_leverage_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """الحصول على لوحة مفاتيح الرافعة المالية"""
        try:
            keyboard = [
                [InlineKeyboardButton("1x", callback_data=f"leverage_{user_id}_1")],
                [InlineKeyboardButton("5x", callback_data=f"leverage_{user_id}_5")],
                [InlineKeyboardButton("10x", callback_data=f"leverage_{user_id}_10")],
                [InlineKeyboardButton("20x", callback_data=f"leverage_{user_id}_20")],
                [InlineKeyboardButton("50x", callback_data=f"leverage_{user_id}_50")],
                [InlineKeyboardButton("100x", callback_data=f"leverage_{user_id}_100")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"settings_{user_id}")]
            ]
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة مفاتيح الرافعة المالية: {e}")
            return InlineKeyboardMarkup([])
    
    def format_user_info(self, user_id: int) -> str:
        """تنسيق معلومات المستخدم"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            user_data = user_env.user_data
            balance_info = user_env.get_balance_info()
            trading_stats = user_env.get_trading_stats()
            settings = user_env.get_settings()
            
            # معلومات المستخدم الأساسية
            username = user_data.get('username', 'غير محدد') if user_data else 'غير محدد'
            first_name = user_data.get('first_name', '') if user_data else ''
            last_name = user_data.get('last_name', '') if user_data else ''
            
            # حالة البوت
            bot_status = "🟢 نشط" if user_env.is_active else "🔴 متوقف"
            api_status = "🔗 مرتبط" if user_env.has_api_keys() else "❌ غير مرتبط"
            
            # نوع السوق
            market_type = settings.get('market_type', 'spot').upper()
            leverage = settings.get('leverage', 1)
            
            info_text = f"""
👤 معلومات المستخدم:
• الاسم: {first_name} {last_name}
• المعرف: @{username}
• ID: {user_id}

🤖 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

💰 معلومات الرصيد:
• الرصيد الكلي: {balance_info['balance']:.2f}
• الرصيد المتاح: {balance_info['available_balance']:.2f}
• الهامش المحجوز: {balance_info['margin_locked']:.2f}
• إجمالي PnL: {balance_info['total_pnl']:.2f}

📊 إحصائيات التداول:
• إجمالي الصفقات: {trading_stats['total_trades']}
• الصفقات الرابحة: {trading_stats['winning_trades']}
• الصفقات الخاسرة: {trading_stats['losing_trades']}
• معدل النجاح: {trading_stats['win_rate']:.1f}%

⚙️ الإعدادات الحالية:
• نوع السوق: {market_type}
• الرافعة المالية: {leverage}x
• مبلغ التداول: {settings.get('trade_amount', 100)}
            """
            
            return info_text
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق معلومات المستخدم {user_id}: {e}")
            return "❌ خطأ في تحميل معلومات المستخدم"
    
    def format_order_info(self, order_id: str) -> str:
        """تنسيق معلومات الصفقة"""
        try:
            order = order_manager.get_order(order_id)
            if not order:
                return "❌ الصفقة غير موجودة"
            
            symbol = order['symbol']
            side = order['side']
            entry_price = order['entry_price']
            current_price = order['current_price']
            quantity = order['quantity']
            leverage = order['leverage']
            unrealized_pnl = order['unrealized_pnl']
            open_time = order['open_time']
            
            # حساب النسبة المئوية للربح/الخسارة
            if side.lower() == "buy":
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            # مؤشرات بصرية
            pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
            pnl_arrow = "⬆️" if unrealized_pnl >= 0 else "⬇️"
            
            # تنسيق الوقت
            if isinstance(open_time, datetime):
                time_str = open_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = str(open_time)
            
            order_text = f"""
📊 تفاصيل الصفقة: {symbol}

🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
📊 الكمية: {quantity:.6f}
⚡ الرافعة: {leverage}x

{pnl_emoji} الربح/الخسارة: {unrealized_pnl:.2f} ({pnl_percent:.2f}%)
{pnl_arrow} الحالة: {'رابحة' if unrealized_pnl >= 0 else 'خاسرة'}

📅 وقت الفتح: {time_str}
🆔 رقم الصفقة: {order_id}
            """
            
            # إضافة معلومات إضافية للفيوتشر
            if leverage > 1:
                margin_amount = order.get('margin_amount', 0)
                liquidation_price = order.get('liquidation_price', 0)
                
                order_text += f"""
💰 الهامش المحجوز: {margin_amount:.2f}
⚠️ سعر التصفية: {liquidation_price:.6f}
                """
            
            # إضافة معلومات TP/SL
            tps = order.get('tps', [])
            sl = order.get('sl', 0)
            
            if tps:
                order_text += "\n🎯 أهداف الأرباح:\n"
                for i, tp in enumerate(tps, 1):
                    status = "✅ مفعل" if tp.get('triggered', False) else "⏳ في الانتظار"
                    order_text += f"• TP{i}: {tp['percentage']}% - {status}\n"
            
            if sl > 0:
                order_text += f"\n🛡️ وقف الخسارة: {sl}%"
            
            return order_text
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق معلومات الصفقة {order_id}: {e}")
            return "❌ خطأ في تحميل معلومات الصفقة"
    
    def format_orders_list(self, user_id: int) -> str:
        """تنسيق قائمة الصفقات المفتوحة"""
        try:
            orders = order_manager.get_user_orders(user_id)
            
            if not orders:
                return "📭 لا توجد صفقات مفتوحة حالياً"
            
            orders_text = f"📊 الصفقات المفتوحة ({len(orders)} صفقة):\n\n"
            
            for i, order in enumerate(orders, 1):
                symbol = order['symbol']
                side = order['side']
                unrealized_pnl = order['unrealized_pnl']
                leverage = order['leverage']
                
                # مؤشرات بصرية
                pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
                leverage_text = f" {leverage}x" if leverage > 1 else ""
                
                orders_text += f"""
{i}. {pnl_emoji} {symbol} {side.upper()}{leverage_text}
   💰 PnL: {unrealized_pnl:+.2f}
   🆔 {order['order_id'][:12]}...
                """
            
            return orders_text
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق قائمة الصفقات للمستخدم {user_id}: {e}")
            return "❌ خطأ في تحميل الصفقات المفتوحة"
    
    def format_trade_history(self, user_id: int, limit: int = 10) -> str:
        """تنسيق تاريخ التداول"""
        try:
            history = user_manager.get_user_trade_history(user_id, limit)
            
            if not history:
                return "📋 لا يوجد تاريخ تداول حتى الآن"
            
            history_text = f"📈 تاريخ التداول (آخر {len(history)} صفقة):\n\n"
            
            for i, trade in enumerate(history, 1):
                symbol = trade['symbol']
                side = trade['side']
                pnl = trade['pnl']
                leverage = trade['leverage']
                closed_at = trade['closed_at']
                
                # مؤشرات بصرية
                pnl_emoji = "🟢💰" if pnl > 0 else "🔴💸"
                leverage_text = f" {leverage}x" if leverage > 1 else ""
                
                # تنسيق الوقت
                if isinstance(closed_at, datetime):
                    time_str = closed_at.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = str(closed_at)
                
                history_text += f"""
{i}. {pnl_emoji} {symbol} {side.upper()}{leverage_text}
   💰 PnL: {pnl:+.2f}
   📅 {time_str}
                """
            
            return history_text
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق تاريخ التداول للمستخدم {user_id}: {e}")
            return "❌ خطأ في تحميل تاريخ التداول"
    
    def set_user_state(self, user_id: int, state: str, context: Dict = None):
        """تحديد حالة المستخدم"""
        self.user_states[user_id] = state
        if context:
            self.user_context[user_id] = context
        elif user_id in self.user_context:
            del self.user_context[user_id]
    
    def get_user_state(self, user_id: int) -> Optional[str]:
        """الحصول على حالة المستخدم"""
        return self.user_states.get(user_id)
    
    def get_user_context(self, user_id: int) -> Optional[Dict]:
        """الحصول على سياق المستخدم"""
        return self.user_context.get(user_id)
    
    def clear_user_state(self, user_id: int):
        """مسح حالة المستخدم"""
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.user_context:
            del self.user_context[user_id]

# إنشاء مثيل عام لمدير الواجهة
ui_manager = UIManager()
