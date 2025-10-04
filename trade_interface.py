#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة تفاعلية لإدارة الصفقات مع TP/SL
"""

import logging
from typing import Dict, List, Optional, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from order_manager import PriceType, order_manager

logger = logging.getLogger(__name__)


class TradeInterface:
    """واجهة تفاعلية للتداول"""
    
    def __init__(self):
        # حالة إدخال المستخدم
        self.user_trade_state: Dict[int, Dict] = {}
    
    async def show_new_trade_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        market_type: str = 'spot',
        leverage: int = 1
    ):
        """عرض قائمة تحديد TP/SL لصفقة جديدة"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None:
                return
            
            # حفظ بيانات الصفقة في حالة المستخدم
            self.user_trade_state[user_id] = {
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'quantity': quantity,
                'market_type': market_type,
                'leverage': leverage,
                'take_profits': [],
                'stop_loss': None,
                'step': 'menu'
            }
            
            message = f"""
📊 إعداد صفقة جديدة

🔸 الرمز: {symbol}
🔸 النوع: {side.upper()}
🔸 السعر: {entry_price:.6f}
🔸 الكمية: {quantity}
🔸 السوق: {market_type.upper()}
{'🔸 الرافعة: ' + str(leverage) + 'x' if market_type == 'futures' else ''}

اختر خيار:
            """
            
            keyboard = [
                [InlineKeyboardButton("📈 إضافة Take Profit", callback_data=f"trade_add_tp")],
                [InlineKeyboardButton("🛡️ إضافة Stop Loss", callback_data=f"trade_add_sl")],
                [InlineKeyboardButton("✅ فتح الصفقة الآن", callback_data=f"trade_confirm")],
                [InlineKeyboardButton("❌ إلغاء", callback_data=f"trade_cancel")]
            ]
            
            # إذا كان هناك TP/SL محدد، عرضه
            trade_state = self.user_trade_state[user_id]
            if trade_state.get('take_profits'):
                tp_count = len(trade_state['take_profits'])
                message += f"\n✅ تم إضافة {tp_count} مستوى Take Profit"
            
            if trade_state.get('stop_loss'):
                message += f"\n✅ تم إضافة Stop Loss"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            elif update.message:
                await update.message.reply_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة الصفقة: {e}")
    
    async def handle_add_take_profit(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة إضافة Take Profit"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            tp_count = len(trade_state.get('take_profits', []))
            level_number = tp_count + 1
            
            # تحديث الحالة
            trade_state['step'] = 'add_tp_type'
            trade_state['current_tp_level'] = level_number
            
            message = f"""
📈 إضافة Take Profit {level_number}

اختر طريقة تحديد السعر:
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 نسبة مئوية (%)", callback_data=f"trade_tp_type_percentage")],
                [InlineKeyboardButton("💲 سعر محدد", callback_data=f"trade_tp_type_price")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"trade_back_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إضافة Take Profit: {e}")
    
    async def handle_tp_type_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        price_type: str
    ):
        """معالجة اختيار نوع تحديد سعر TP"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            trade_state['current_tp_type'] = price_type
            trade_state['step'] = 'add_tp_value'
            
            if price_type == 'percentage':
                message = f"""
📈 Take Profit {trade_state['current_tp_level']} - نسبة مئوية

أدخل النسبة المئوية للربح:
مثال: 5 (يعني +5% من سعر الدخول)

سعر الدخول: {trade_state['entry_price']:.6f}
                """
            else:
                message = f"""
📈 Take Profit {trade_state['current_tp_level']} - سعر محدد

أدخل السعر المستهدف:
مثال: {trade_state['entry_price'] * 1.05:.6f}

سعر الدخول: {trade_state['entry_price']:.6f}
                """
            
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data=f"trade_back_tp")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة اختيار نوع TP: {e}")
    
    async def handle_tp_value_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        value: float
    ):
        """معالجة إدخال قيمة TP"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            trade_state['current_tp_value'] = value
            trade_state['step'] = 'add_tp_percentage'
            
            message = f"""
📈 Take Profit {trade_state['current_tp_level']} - نسبة الإغلاق

أدخل نسبة الإغلاق من الصفقة (%):
مثال: 50 (يعني إغلاق 50% من الصفقة)

القيمة المحددة: {value}
            """
            
            keyboard = [
                [InlineKeyboardButton("25%", callback_data=f"trade_tp_close_25")],
                [InlineKeyboardButton("50%", callback_data=f"trade_tp_close_50")],
                [InlineKeyboardButton("75%", callback_data=f"trade_tp_close_75")],
                [InlineKeyboardButton("100%", callback_data=f"trade_tp_close_100")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"trade_back_tp")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.message:
                await update.message.reply_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة قيمة TP: {e}")
    
    async def handle_tp_percentage_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        percentage: float
    ):
        """معالجة اختيار نسبة الإغلاق"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            
            # إضافة TP إلى القائمة
            tp_data = {
                'level': trade_state['current_tp_level'],
                'price_type': trade_state['current_tp_type'],
                'value': trade_state['current_tp_value'],
                'close_percentage': percentage
            }
            
            if 'take_profits' not in trade_state:
                trade_state['take_profits'] = []
            
            trade_state['take_profits'].append(tp_data)
            
            # مسح البيانات المؤقتة
            trade_state.pop('current_tp_level', None)
            trade_state.pop('current_tp_type', None)
            trade_state.pop('current_tp_value', None)
            
            # العودة إلى القائمة الرئيسية
            await self.show_new_trade_menu(
                update, context,
                trade_state['symbol'],
                trade_state['side'],
                trade_state['entry_price'],
                trade_state['quantity'],
                trade_state['market_type'],
                trade_state['leverage']
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة نسبة الإغلاق: {e}")
    
    async def handle_add_stop_loss(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة إضافة Stop Loss"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            trade_state['step'] = 'add_sl_type'
            
            message = f"""
🛡️ إضافة Stop Loss

اختر طريقة تحديد السعر:
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 نسبة مئوية (%)", callback_data=f"trade_sl_type_percentage")],
                [InlineKeyboardButton("💲 سعر محدد", callback_data=f"trade_sl_type_price")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"trade_back_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إضافة Stop Loss: {e}")
    
    async def handle_sl_type_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        price_type: str
    ):
        """معالجة اختيار نوع تحديد سعر SL"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            trade_state['current_sl_type'] = price_type
            trade_state['step'] = 'add_sl_value'
            
            if price_type == 'percentage':
                message = f"""
🛡️ Stop Loss - نسبة مئوية

أدخل النسبة المئوية للخسارة:
مثال: 2 (يعني -2% من سعر الدخول)

سعر الدخول: {trade_state['entry_price']:.6f}
                """
            else:
                message = f"""
🛡️ Stop Loss - سعر محدد

أدخل سعر Stop Loss:
مثال: {trade_state['entry_price'] * 0.98:.6f}

سعر الدخول: {trade_state['entry_price']:.6f}
                """
            
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data=f"trade_back_sl")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة اختيار نوع SL: {e}")
    
    async def handle_sl_value_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        value: float
    ):
        """معالجة إدخال قيمة SL"""
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id is None or user_id not in self.user_trade_state:
                return
            
            trade_state = self.user_trade_state[user_id]
            
            # حفظ Stop Loss
            sl_data = {
                'price_type': trade_state['current_sl_type'],
                'value': value,
                'trailing': False
            }
            
            trade_state['stop_loss'] = sl_data
            
            # مسح البيانات المؤقتة
            trade_state.pop('current_sl_type', None)
            
            # العودة إلى القائمة الرئيسية
            await self.show_new_trade_menu(
                update, context,
                trade_state['symbol'],
                trade_state['side'],
                trade_state['entry_price'],
                trade_state['quantity'],
                trade_state['market_type'],
                trade_state['leverage']
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة قيمة SL: {e}")
    
    def get_trade_state(self, user_id: int) -> Optional[Dict]:
        """الحصول على حالة الصفقة للمستخدم"""
        return self.user_trade_state.get(user_id)
    
    def clear_trade_state(self, user_id: int):
        """مسح حالة الصفقة للمستخدم"""
        if user_id in self.user_trade_state:
            del self.user_trade_state[user_id]
    
    async def show_position_details(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        position_id: str
    ):
        """عرض تفاصيل صفقة مفتوحة مع أزرار إدارة TP/SL"""
        try:
            # الحصول على الصفقة من order_manager
            order = order_manager.get_order(position_id)
            
            if not order:
                if update.callback_query:
                    await update.callback_query.edit_message_text("❌ الصفقة غير موجودة")
                return
            
            # بناء رسالة التفاصيل
            message = f"""
📊 تفاصيل الصفقة

🔸 الرمز: {order.symbol}
🔸 النوع: {order.side.upper()}
🔸 سعر الدخول: {order.entry_price:.6f}
🔸 الكمية: {order.quantity}
🔸 الكمية المتبقية: {order.remaining_quantity}
🔸 الحالة: {order.status}
            """
            
            if order.current_price:
                message += f"🔸 السعر الحالي: {order.current_price:.6f}\n"
                message += f"🔸 PnL غير محقق: {order.unrealized_pnl:.2f}\n"
            
            if order.realized_pnl:
                message += f"🔸 PnL محقق: {order.realized_pnl:.2f}\n"
            
            # عرض Take Profits
            if order.take_profit_levels:
                message += "\n📈 Take Profit Levels:\n"
                for tp in order.take_profit_levels:
                    status = "✅" if tp.executed else "⏳"
                    message += f"{status} TP{tp.level_number}: {tp.target_price:.6f} ({tp.close_percentage}%)\n"
            
            # عرض Stop Loss
            if order.stop_loss:
                sl = order.stop_loss
                status = "✅" if sl.executed else "⏳"
                message += f"\n🛡️ Stop Loss:\n{status} SL: {sl.target_price:.6f}\n"
                if sl.trailing:
                    message += f"   Trailing: {sl.trailing_distance}%\n"
            
            # إنشاء الأزرار
            keyboard = [
                [InlineKeyboardButton("📈 إضافة TP", callback_data=f"pos_add_tp_{position_id}")],
                [InlineKeyboardButton("🛡️ تعديل SL", callback_data=f"pos_edit_sl_{position_id}")],
                [InlineKeyboardButton("📊 إغلاق جزئي", callback_data=f"pos_partial_close_{position_id}")],
                [InlineKeyboardButton("❌ إغلاق كامل", callback_data=f"pos_close_full_{position_id}")],
                [InlineKeyboardButton("🔄 تحديث", callback_data=f"pos_refresh_{position_id}")],
                [InlineKeyboardButton("🔙 العودة", callback_data="open_positions")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"خطأ في عرض تفاصيل الصفقة: {e}")


# إنشاء مثيل عام
trade_interface = TradeInterface()

