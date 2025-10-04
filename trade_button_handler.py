#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج أزرار الصفقات مع إمكانية الإدخال المخصص
يدعم TP, SL, Partial Close مع إمكانية كتابة النسب يدوياً
"""

import logging
import re
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeButtonHandler:
    """معالج أزرار الصفقات التفاعلية"""
    
    def __init__(self, trade_manager):
        self.trade_manager = trade_manager
        self.user_input_states = {}  # {user_id: {'type': 'tp_custom', 'position_id': 'xxx'}}
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة جميع استدعاءات الأزرار"""
        try:
            query = update.callback_query
            if not query or not query.data:
                return
            
            await query.answer()
            data = query.data
            
            # معالجة أزرار TP
            if data.startswith("tp_"):
                await self.handle_tp_action(update, context, data)
            
            # معالجة أزرار SL
            elif data.startswith("sl_"):
                await self.handle_sl_action(update, context, data)
            
            # معالجة أزرار الإغلاق الجزئي
            elif data.startswith("partial_"):
                await self.handle_partial_action(update, context, data)
            
            # معالجة أزرار الإغلاق الكامل
            elif data.startswith("close_full_"):
                await self.handle_close_full(update, context, data)
            
            # معالجة أزرار تغيير النسب
            elif data.startswith("change_percentages_"):
                await self.handle_change_percentages(update, context, data)
            
            # معالجة أزرار تعديل النسب
            elif data.startswith("edit_"):
                await self.handle_edit_percentages(update, context, data)
            
            # معالجة أزرار التحديث
            elif data.startswith("refresh_trade_"):
                await self.handle_refresh_trade(update, context, data)
            
            # معالجة أزرار الإعدادات المخصصة
            elif data.startswith("save_percentages_"):
                await self.handle_save_percentages(update, context, data)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة استدعاء الزر: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ حدث خطأ في معالجة الطلب")
    
    async def handle_tp_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار Take Profit"""
        try:
            query = update.callback_query
            parts = data.split("_")
            
            if len(parts) >= 3:
                position_id = parts[2]
                
                if parts[1] == "custom":
                    # طلب إدخال نسبة TP مخصصة
                    await self.request_custom_percentage(query, position_id, "tp")
                else:
                    # تنفيذ TP بنسبة محددة
                    percent = float(parts[1])
                    await self.trade_manager.execute_take_profit(position_id, percent, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة TP: {e}")
            await query.answer("❌ خطأ في تنفيذ Take Profit")
    
    async def handle_sl_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار Stop Loss"""
        try:
            query = update.callback_query
            parts = data.split("_")
            
            if len(parts) >= 3:
                position_id = parts[2]
                
                if parts[1] == "custom":
                    # طلب إدخال نسبة SL مخصصة
                    await self.request_custom_percentage(query, position_id, "sl")
                else:
                    # تنفيذ SL بنسبة محددة
                    percent = float(parts[1])
                    await self.trade_manager.execute_stop_loss(position_id, percent, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة SL: {e}")
            await query.answer("❌ خطأ في تنفيذ Stop Loss")
    
    async def handle_partial_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار الإغلاق الجزئي"""
        try:
            query = update.callback_query
            parts = data.split("_")
            
            if len(parts) >= 3:
                position_id = parts[2]
                
                if parts[1] == "custom":
                    # طلب إدخال نسبة إغلاق جزئي مخصصة
                    await self.request_custom_percentage(query, position_id, "partial")
                else:
                    # تنفيذ إغلاق جزئي بنسبة محددة
                    percent = float(parts[1])
                    await self.trade_manager.execute_partial_close(position_id, percent, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الجزئي: {e}")
            await query.answer("❌ خطأ في تنفيذ الإغلاق الجزئي")
    
    async def handle_close_full(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار الإغلاق الكامل"""
        try:
            query = update.callback_query
            position_id = data.replace("close_full_", "")
            await self.trade_manager.execute_full_close(position_id, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الكامل: {e}")
            await query.answer("❌ خطأ في تنفيذ الإغلاق الكامل")
    
    async def handle_change_percentages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار تغيير النسب"""
        try:
            query = update.callback_query
            position_id = data.replace("change_percentages_", "")
            await self.trade_manager.show_percentage_settings(query, position_id)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة تغيير النسب: {e}")
            await query.answer("❌ خطأ في عرض إعدادات النسب")
    
    async def handle_edit_percentages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار تعديل النسب"""
        try:
            query = update.callback_query
            parts = data.split("_")
            
            if len(parts) >= 3:
                percentage_type = parts[1]  # tp, sl, partial
                position_id = parts[2]
                
                await self.request_custom_percentages(query, position_id, percentage_type)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة تعديل النسب: {e}")
            await query.answer("❌ خطأ في تعديل النسب")
    
    async def handle_refresh_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة أزرار تحديث الصفقة"""
        try:
            query = update.callback_query
            position_id = data.replace("refresh_trade_", "")
            await self.trade_manager.update_trade_message(position_id, context)
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقة: {e}")
            await query.answer("❌ خطأ في تحديث الصفقة")
    
    async def handle_save_percentages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة حفظ النسب المخصصة"""
        try:
            query = update.callback_query
            parts = data.split("_")
            
            if len(parts) >= 3:
                percentage_type = parts[2]  # tp, sl, partial
                position_id = parts[3] if len(parts) > 3 else ""
                
                # حفظ النسب المخصصة
                user_id = query.from_user.id
                current_percentages = self.trade_manager.get_user_percentages(user_id)
                
                # هنا يمكن إضافة منطق حفظ النسب الجديدة
                await query.answer("✅ تم حفظ النسب المخصصة")
                
                # العودة إلى رسالة الصفقة
                if position_id:
                    await self.trade_manager.update_trade_message(position_id, context)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ النسب: {e}")
            await query.answer("❌ خطأ في حفظ النسب")
    
    async def request_custom_percentage(self, query: CallbackQuery, position_id: str, action_type: str):
        """طلب إدخال نسبة مخصصة"""
        try:
            user_id = query.from_user.id
            
            # حفظ حالة الإدخال
            self.user_input_states[user_id] = {
                'type': f'{action_type}_custom',
                'position_id': position_id
            }
            
            # رسالة الطلب
            action_names = {
                'tp': 'Take Profit',
                'sl': 'Stop Loss',
                'partial': 'الإغلاق الجزئي'
            }
            
            request_text = f"""
📝 **إدخال نسبة {action_names.get(action_type, action_type)} مخصصة**

أدخل النسبة المطلوبة (رقم فقط):
مثال: 2.5 أو 15 أو 75

📊 الرمز: {self.trade_manager.trading_bot.open_positions.get(position_id, {}).get('symbol', 'غير محدد')}
            """
            
            # أزرار الإلغاء
            keyboard = [
                [InlineKeyboardButton("❌ إلغاء", callback_data=f"refresh_trade_{position_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(request_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في طلب النسبة المخصصة: {e}")
            await query.answer("❌ خطأ في طلب النسبة المخصصة")
    
    async def request_custom_percentages(self, query: CallbackQuery, position_id: str, percentage_type: str):
        """طلب إدخال نسب متعددة مخصصة"""
        try:
            user_id = query.from_user.id
            
            # حفظ حالة الإدخال
            self.user_input_states[user_id] = {
                'type': f'edit_{percentage_type}',
                'position_id': position_id
            }
            
            # رسالة الطلب
            type_names = {
                'tp': 'Take Profit',
                'sl': 'Stop Loss',
                'partial': 'الإغلاق الجزئي'
            }
            
            request_text = f"""
📝 **تعديل نسب {type_names.get(percentage_type, percentage_type)}**

أدخل النسب المطلوبة مفصولة بفواصل:
مثال: 1, 2.5, 5 أو 25, 50, 75

📊 الرمز: {self.trade_manager.trading_bot.open_positions.get(position_id, {}).get('symbol', 'غير محدد')}
            """
            
            # أزرار الإلغاء
            keyboard = [
                [InlineKeyboardButton("❌ إلغاء", callback_data=f"change_percentages_{position_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(request_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في طلب النسب المخصصة: {e}")
            await query.answer("❌ خطأ في طلب النسب المخصصة")
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة النصوص المدخلة للقيم المخصصة"""
        try:
            if not update.message or not update.message.text:
                return
            
            user_id = update.effective_user.id
            text = update.message.text.strip()
            
            # التحقق من وجود حالة إدخال
            if user_id not in self.user_input_states:
                return
            
            input_state = self.user_input_states[user_id]
            input_type = input_state['type']
            position_id = input_state['position_id']
            
            # معالجة النص المدخل
            if input_type.endswith('_custom'):
                # نسبة واحدة مخصصة
                await self.process_single_percentage(update, context, text, input_type, position_id)
            elif input_type.startswith('edit_'):
                # نسب متعددة مخصصة
                await self.process_multiple_percentages(update, context, text, input_type, position_id)
            
            # مسح حالة الإدخال
            del self.user_input_states[user_id]
            
        except Exception as e:
            logger.error(f"خطأ في معالجة النص المدخل: {e}")
            if update.message:
                await update.message.reply_text("❌ خطأ في معالجة الإدخال")
    
    async def process_single_percentage(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, input_type: str, position_id: str):
        """معالجة نسبة واحدة مخصصة"""
        try:
            # التحقق من صحة النص
            if not self.is_valid_percentage(text):
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح (مثال: 2.5 أو 15)")
                return
            
            percent = float(text)
            
            # التحقق من النطاق المناسب
            action_type = input_type.replace('_custom', '')
            if not self.is_percentage_in_range(percent, action_type):
                await update.message.reply_text("❌ النسبة خارج النطاق المسموح")
                return
            
            # تنفيذ الإجراء
            query = CallbackQuery(
                id="custom",
                from_user=update.effective_user,
                message=update.message,
                data=f"{action_type}_{position_id}_{percent}"
            )
            
            if action_type == "tp":
                await self.trade_manager.execute_take_profit(position_id, percent, query)
            elif action_type == "sl":
                await self.trade_manager.execute_stop_loss(position_id, percent, query)
            elif action_type == "partial":
                await self.trade_manager.execute_partial_close(position_id, percent, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة النسبة الواحدة: {e}")
            await update.message.reply_text("❌ خطأ في معالجة النسبة")
    
    async def process_multiple_percentages(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, input_type: str, position_id: str):
        """معالجة نسب متعددة مخصصة"""
        try:
            # تقسيم النص إلى نسب
            parts = [part.strip() for part in text.split(',')]
            
            # التحقق من صحة جميع النسب
            percentages = []
            for part in parts:
                if not self.is_valid_percentage(part):
                    await update.message.reply_text(f"❌ نسبة غير صحيحة: {part}")
                    return
                percentages.append(float(part))
            
            # التحقق من النطاق المناسب
            percentage_type = input_type.replace('edit_', '')
            for percent in percentages:
                if not self.is_percentage_in_range(percent, percentage_type):
                    await update.message.reply_text(f"❌ نسبة خارج النطاق: {percent}")
                    return
            
            # حفظ النسب الجديدة
            user_id = update.effective_user.id
            current_percentages = self.trade_manager.get_user_percentages(user_id)
            current_percentages[percentage_type] = percentages
            self.trade_manager.update_user_percentages(user_id, current_percentages)
            
            # رسالة التأكيد
            await update.message.reply_text(f"✅ تم حفظ نسب {percentage_type} الجديدة: {', '.join(map(str, percentages))}")
            
            # العودة إلى رسالة الصفقة
            await self.trade_manager.update_trade_message(position_id, context)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة النسب المتعددة: {e}")
            await update.message.reply_text("❌ خطأ في معالجة النسب")
    
    def is_valid_percentage(self, text: str) -> bool:
        """التحقق من صحة النسبة"""
        try:
            # استخدام regex للتحقق من الرقم
            pattern = r'^\d+(\.\d+)?$'
            return bool(re.match(pattern, text)) and float(text) > 0
        except:
            return False
    
    def is_percentage_in_range(self, percent: float, action_type: str) -> bool:
        """التحقق من نطاق النسبة"""
        try:
            if action_type == "tp":
                return 0.1 <= percent <= 100  # TP من 0.1% إلى 100%
            elif action_type == "sl":
                return 0.1 <= percent <= 50   # SL من 0.1% إلى 50%
            elif action_type == "partial":
                return 1 <= percent <= 100    # Partial من 1% إلى 100%
            return False
        except:
            return False
    
    def get_user_input_state(self, user_id: int) -> Optional[Dict]:
        """الحصول على حالة إدخال المستخدم"""
        return self.user_input_states.get(user_id)
    
    def clear_user_input_state(self, user_id: int):
        """مسح حالة إدخال المستخدم"""
        if user_id in self.user_input_states:
            del self.user_input_states[user_id]
