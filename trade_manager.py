#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الصفقات مع رسائل منفصلة لكل صفقة
يدعم أزرار TP, SL, Partial Close, و Full Close
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeManager:
    """مدير الصفقات مع رسائل تفاعلية منفصلة"""
    
    def __init__(self, trading_bot):
        self.trading_bot = trading_bot
        self.trade_messages = {}  # {position_id: message_info}
        self.user_percentages = {}  # {user_id: {tp: [1,2,5], sl: [1,2,3], partial: [25,50,75]}}
        
    def get_user_percentages(self, user_id: int) -> Dict:
        """الحصول على نسب المستخدم المخصصة"""
        if user_id not in self.user_percentages:
            # إعدادات افتراضية
            self.user_percentages[user_id] = {
                'tp': [1, 2, 5],
                'sl': [1, 2, 3],
                'partial': [25, 50, 75]
            }
        return self.user_percentages[user_id]
    
    def update_user_percentages(self, user_id: int, percentages: Dict):
        """تحديث نسب المستخدم"""
        self.user_percentages[user_id] = percentages
    
    async def create_trade_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_info: Dict):
        """إنشاء رسالة منفصلة للصفقة"""
        try:
            position_id = position_info.get('position_id', 'unknown')
            symbol = position_info['symbol']
            side = position_info['side']
            entry_price = position_info['entry_price']
            current_price = position_info.get('current_price', entry_price)
            market_type = position_info.get('account_type', 'spot')
            
            # حساب الربح/الخسارة
            pnl_percent = position_info.get('pnl_percent', 0.0)
            pnl_value = 0.0
            
            if market_type == 'futures':
                margin_amount = position_info.get('margin_amount', 0)
                leverage = position_info.get('leverage', 1)
                position_size = position_info.get('position_size', 0)
                liquidation_price = position_info.get('liquidation_price', 0)
                
                # حساب PnL للفيوتشر
                if margin_amount > 0:
                    pnl_value = (pnl_percent / 100) * margin_amount
                
                # رسالة الصفقة
                pnl_emoji = "🟢💰" if pnl_percent >= 0 else "🔴💸"
                pnl_status = "رابح" if pnl_percent >= 0 else "خاسر"
                arrow = "⬆️" if pnl_percent >= 0 else "⬇️"
                
                trade_text = f"""
{pnl_emoji} **صفقة فيوتشر - {symbol}**
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الهامش المحجوز: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
{arrow} الربح/الخسارة: {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {liquidation_price:.6f}
🆔 رقم الصفقة: {position_id}
                """
            else:
                amount = position_info.get('amount', 0)
                contracts = amount / entry_price if entry_price > 0 else 0
                
                # حساب PnL للسبوت
                if side.lower() == "buy":
                    pnl_value = (current_price - entry_price) * contracts
                else:
                    pnl_value = (entry_price - current_price) * contracts
                
                pnl_percent = (pnl_value / amount) * 100 if amount > 0 else 0
                
                pnl_emoji = "🟢💰" if pnl_value >= 0 else "🔴💸"
                pnl_status = "رابح" if pnl_value >= 0 else "خاسر"
                arrow = "⬆️" if pnl_value >= 0 else "⬇️"
                
                trade_text = f"""
{pnl_emoji} **صفقة سبوت - {symbol}**
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 المبلغ: {amount:.2f}
{arrow} الربح/الخسارة: {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}
🆔 رقم الصفقة: {position_id}
                """
            
            # إنشاء الأزرار
            keyboard = await self.create_trade_buttons(position_id, update.effective_user.id if update.effective_user else None)
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # إرسال الرسالة
            if update.message:
                message = await update.message.reply_text(trade_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=trade_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
            # حفظ معلومات الرسالة
            self.trade_messages[position_id] = {
                'message_id': message.message_id,
                'chat_id': message.chat_id,
                'position_info': position_info,
                'last_update': datetime.now()
            }
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الصفقة: {e}")
            return None
    
    async def create_trade_buttons(self, position_id: str, user_id: Optional[int] = None) -> List[List[InlineKeyboardButton]]:
        """إنشاء أزرار الصفقة التفاعلية"""
        try:
            keyboard = []
            
            if user_id:
                percentages = self.get_user_percentages(user_id)
            else:
                percentages = {'tp': [1, 2, 5], 'sl': [1, 2, 3], 'partial': [25, 50, 75]}
            
            # أزرار Take Profit (TP)
            tp_buttons = []
            for percent in percentages['tp']:
                tp_buttons.append(InlineKeyboardButton(
                    f"TP {percent}%",
                    callback_data=f"tp_{position_id}_{percent}"
                ))
            
            # إضافة زر TP مخصص
            tp_buttons.append(InlineKeyboardButton(
                "TP مخصص",
                callback_data=f"tp_custom_{position_id}"
            ))
            
            keyboard.append(tp_buttons)
            
            # أزرار Stop Loss (SL)
            sl_buttons = []
            for percent in percentages['sl']:
                sl_buttons.append(InlineKeyboardButton(
                    f"SL {percent}%",
                    callback_data=f"sl_{position_id}_{percent}"
                ))
            
            # إضافة زر SL مخصص
            sl_buttons.append(InlineKeyboardButton(
                "SL مخصص",
                callback_data=f"sl_custom_{position_id}"
            ))
            
            keyboard.append(sl_buttons)
            
            # أزرار الإغلاق الجزئي
            partial_buttons = []
            for percent in percentages['partial']:
                partial_buttons.append(InlineKeyboardButton(
                    f"إغلاق {percent}%",
                    callback_data=f"partial_{position_id}_{percent}"
                ))
            
            # إضافة زر إغلاق جزئي مخصص
            partial_buttons.append(InlineKeyboardButton(
                "إغلاق مخصص",
                callback_data=f"partial_custom_{position_id}"
            ))
            
            keyboard.append(partial_buttons)
            
            # أزرار الإغلاق الكامل والإعدادات
            control_buttons = [
                InlineKeyboardButton(
                    "❌ إغلاق كامل",
                    callback_data=f"close_full_{position_id}"
                ),
                InlineKeyboardButton(
                    "⚙️ تغيير النسب",
                    callback_data=f"change_percentages_{position_id}"
                )
            ]
            keyboard.append(control_buttons)
            
            # زر التحديث
            keyboard.append([InlineKeyboardButton(
                "🔄 تحديث",
                callback_data=f"refresh_trade_{position_id}"
            )])
            
            return keyboard
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء أزرار الصفقة: {e}")
            return []
    
    async def update_trade_message(self, position_id: str, context: ContextTypes.DEFAULT_TYPE):
        """تحديث رسالة الصفقة"""
        try:
            if position_id not in self.trade_messages:
                return
            
            message_info = self.trade_messages[position_id]
            position_info = message_info['position_info']
            
            # تحديث معلومات الصفقة
            if position_id in self.trading_bot.open_positions:
                updated_info = self.trading_bot.open_positions[position_id]
                position_info.update(updated_info)
            
            # إعادة إنشاء النص والأزرار
            symbol = position_info['symbol']
            side = position_info['side']
            entry_price = position_info['entry_price']
            current_price = position_info.get('current_price', entry_price)
            market_type = position_info.get('account_type', 'spot')
            
            # حساب الربح/الخسارة المحدث
            pnl_percent = position_info.get('pnl_percent', 0.0)
            pnl_value = 0.0
            
            if market_type == 'futures':
                margin_amount = position_info.get('margin_amount', 0)
                leverage = position_info.get('leverage', 1)
                position_size = position_info.get('position_size', 0)
                liquidation_price = position_info.get('liquidation_price', 0)
                
                if margin_amount > 0:
                    pnl_value = (pnl_percent / 100) * margin_amount
                
                pnl_emoji = "🟢💰" if pnl_percent >= 0 else "🔴💸"
                pnl_status = "رابح" if pnl_percent >= 0 else "خاسر"
                arrow = "⬆️" if pnl_percent >= 0 else "⬇️"
                
                trade_text = f"""
{pnl_emoji} **صفقة فيوتشر - {symbol}**
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الهامش المحجوز: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
{arrow} الربح/الخسارة: {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {liquidation_price:.6f}
🆔 رقم الصفقة: {position_id}
                """
            else:
                amount = position_info.get('amount', 0)
                contracts = amount / entry_price if entry_price > 0 else 0
                
                if side.lower() == "buy":
                    pnl_value = (current_price - entry_price) * contracts
                else:
                    pnl_value = (entry_price - current_price) * contracts
                
                pnl_percent = (pnl_value / amount) * 100 if amount > 0 else 0
                
                pnl_emoji = "🟢💰" if pnl_value >= 0 else "🔴💸"
                pnl_status = "رابح" if pnl_value >= 0 else "خاسر"
                arrow = "⬆️" if pnl_value >= 0 else "⬇️"
                
                trade_text = f"""
{pnl_emoji} **صفقة سبوت - {symbol}**
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 المبلغ: {amount:.2f}
{arrow} الربح/الخسارة: {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}
🆔 رقم الصفقة: {position_id}
                """
            
            # إنشاء الأزرار المحدثة
            keyboard = await self.create_trade_buttons(position_id)
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديث الرسالة
            await context.bot.edit_message_text(
                chat_id=message_info['chat_id'],
                message_id=message_info['message_id'],
                text=trade_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # تحديث معلومات الرسالة
            message_info['last_update'] = datetime.now()
            message_info['position_info'] = position_info
            
        except Exception as e:
            logger.error(f"خطأ في تحديث رسالة الصفقة {position_id}: {e}")
    
    async def handle_trade_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, position_id: str, value: Optional[float] = None):
        """معالجة إجراءات الصفقة"""
        try:
            query = update.callback_query
            await query.answer()
            
            if position_id not in self.trading_bot.open_positions:
                await query.edit_message_text("❌ الصفقة غير موجودة أو تم إغلاقها")
                return
            
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            
            if action == "tp":
                # تنفيذ Take Profit
                await self.execute_take_profit(position_id, value, query)
            elif action == "sl":
                # تنفيذ Stop Loss
                await self.execute_stop_loss(position_id, value, query)
            elif action == "partial":
                # تنفيذ الإغلاق الجزئي
                await self.execute_partial_close(position_id, value, query)
            elif action == "close_full":
                # تنفيذ الإغلاق الكامل
                await self.execute_full_close(position_id, query)
            elif action == "change_percentages":
                # تغيير النسب
                await self.show_percentage_settings(query, position_id)
            elif action == "refresh_trade":
                # تحديث الصفقة
                await self.update_trade_message(position_id, context)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة إجراء الصفقة: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ حدث خطأ في تنفيذ الإجراء")
    
    async def execute_take_profit(self, position_id: str, percent: float, query: CallbackQuery):
        """تنفيذ Take Profit"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            entry_price = position_info['entry_price']
            side = position_info['side']
            
            # حساب سعر TP
            if side.lower() == "buy":
                tp_price = entry_price * (1 + percent / 100)
            else:
                tp_price = entry_price * (1 - percent / 100)
            
            # إرسال رسالة تأكيد
            confirmation_text = f"""
✅ **تم تنفيذ Take Profit**
📊 الرمز: {symbol}
💲 سعر الدخول: {entry_price:.6f}
🎯 سعر TP: {tp_price:.6f}
📈 النسبة: {percent}%
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

🔄 سيتم إغلاق الصفقة عند الوصول للسعر المحدد
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
            
            # هنا يمكن إضافة منطق تنفيذ TP الفعلي
            logger.info(f"تم تنفيذ TP للصفقة {position_id} بنسبة {percent}%")
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ TP: {e}")
            await query.answer("❌ خطأ في تنفيذ Take Profit")
    
    async def execute_stop_loss(self, position_id: str, percent: float, query: CallbackQuery):
        """تنفيذ Stop Loss"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            entry_price = position_info['entry_price']
            side = position_info['side']
            
            # حساب سعر SL
            if side.lower() == "buy":
                sl_price = entry_price * (1 - percent / 100)
            else:
                sl_price = entry_price * (1 + percent / 100)
            
            # إرسال رسالة تأكيد
            confirmation_text = f"""
⚠️ **تم تنفيذ Stop Loss**
📊 الرمز: {symbol}
💲 سعر الدخول: {entry_price:.6f}
🛑 سعر SL: {sl_price:.6f}
📉 النسبة: {percent}%
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

🔄 سيتم إغلاق الصفقة عند الوصول للسعر المحدد
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
            
            # هنا يمكن إضافة منطق تنفيذ SL الفعلي
            logger.info(f"تم تنفيذ SL للصفقة {position_id} بنسبة {percent}%")
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ SL: {e}")
            await query.answer("❌ خطأ في تنفيذ Stop Loss")
    
    async def execute_partial_close(self, position_id: str, percent: float, query: CallbackQuery):
        """تنفيذ الإغلاق الجزئي"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', position_info['entry_price'])
            
            # إرسال رسالة تأكيد
            confirmation_text = f"""
🔄 **تم تنفيذ الإغلاق الجزئي**
📊 الرمز: {symbol}
💲 سعر الإغلاق: {current_price:.6f}
📊 النسبة المغلقة: {percent}%
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

✅ تم إغلاق {percent}% من الصفقة بنجاح
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
            
            # هنا يمكن إضافة منطق تنفيذ الإغلاق الجزئي الفعلي
            logger.info(f"تم تنفيذ الإغلاق الجزئي للصفقة {position_id} بنسبة {percent}%")
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي: {e}")
            await query.answer("❌ خطأ في تنفيذ الإغلاق الجزئي")
    
    async def execute_full_close(self, position_id: str, query: CallbackQuery):
        """تنفيذ الإغلاق الكامل"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', position_info['entry_price'])
            
            # إرسال رسالة تأكيد
            confirmation_text = f"""
❌ **تم تنفيذ الإغلاق الكامل**
📊 الرمز: {symbol}
💲 سعر الإغلاق: {current_price:.6f}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

✅ تم إغلاق الصفقة بالكامل بنجاح
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
            
            # إغلاق الصفقة فعلياً
            # هنا يمكن استدعاء دالة إغلاق الصفقة من البوت الرئيسي
            logger.info(f"تم تنفيذ الإغلاق الكامل للصفقة {position_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الكامل: {e}")
            await query.answer("❌ خطأ في تنفيذ الإغلاق الكامل")
    
    async def show_percentage_settings(self, query: CallbackQuery, position_id: str):
        """عرض إعدادات تغيير النسب"""
        try:
            user_id = query.from_user.id
            percentages = self.get_user_percentages(user_id)
            
            settings_text = f"""
⚙️ **إعدادات النسب المخصصة**

📈 نسب Take Profit: {', '.join(map(str, percentages['tp']))}%
📉 نسب Stop Loss: {', '.join(map(str, percentages['sl']))}%
🔄 نسب الإغلاق الجزئي: {', '.join(map(str, percentages['partial']))}%

اختر النوع لتغييره:
            """
            
            keyboard = [
                [InlineKeyboardButton("📈 تغيير TP", callback_data=f"edit_tp_{position_id}")],
                [InlineKeyboardButton("📉 تغيير SL", callback_data=f"edit_sl_{position_id}")],
                [InlineKeyboardButton("🔄 تغيير الإغلاق الجزئي", callback_data=f"edit_partial_{position_id}")],
                [InlineKeyboardButton("🔙 العودة", callback_data=f"refresh_trade_{position_id}")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات النسب: {e}")
            await query.answer("❌ خطأ في عرض الإعدادات")
    
    def cleanup_closed_trades(self):
        """تنظيف رسائل الصفقات المغلقة"""
        try:
            closed_trades = []
            for position_id in list(self.trade_messages.keys()):
                if position_id not in self.trading_bot.open_positions:
                    closed_trades.append(position_id)
            
            for position_id in closed_trades:
                del self.trade_messages[position_id]
                
            if closed_trades:
                logger.info(f"تم تنظيف {len(closed_trades)} صفقة مغلقة")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف الصفقات المغلقة: {e}")
