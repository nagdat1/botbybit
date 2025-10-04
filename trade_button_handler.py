# -*- coding: utf-8 -*-
"""
معالج الأزرار التفاعلية للصفقات
"""

import logging
from typing import Dict, Any, Optional
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from trade_manager import TradeManager
from trade_interactive_messages import TradeInteractiveMessages
from trade_executor import TradeExecutor
from trade_messages import TRADE_SUCCESS_MESSAGES, TRADE_ERROR_MESSAGES

logger = logging.getLogger(__name__)

class TradeButtonHandler:
    """معالج الأزرار التفاعلية للصفقات"""
    
    def __init__(self, trade_manager: TradeManager, trade_executor: TradeExecutor):
        self.trade_manager = trade_manager
        self.trade_executor = trade_executor
        self.interactive_messages = TradeInteractiveMessages(trade_manager)
        self.user_editing_settings = {}  # تتبع المستخدمين الذين يعدلون الإعدادات
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """معالجة استعلامات الأزرار"""
        try:
            query = update.callback_query
            await query.answer()  # إزالة مؤشر التحميل
            
            user_id = query.from_user.id
            data = query.data
            
            # تحليل البيانات
            parts = data.split('_')
            if len(parts) < 2:
                await query.edit_message_text("❌ خطأ في معالجة الأمر")
                return
            
            action = parts[0]
            trade_id = parts[1]
            
            # التحقق من وجود الصفقة
            trade_info = self.trade_manager.get_trade_info(trade_id)
            if not trade_info:
                await query.edit_message_text("❌ الصفقة غير موجودة")
                return
            
            # معالجة الأوامر المختلفة
            if action == "tp":
                await self._handle_tp(query, trade_id, parts[2])
            elif action == "sl":
                await self._handle_sl(query, trade_id, parts[2])
            elif action == "partial":
                await self._handle_partial_close(query, trade_id, parts[2])
            elif action == "close":
                await self._handle_full_close(query, trade_id)
            elif action == "refresh":
                await self._handle_refresh(query, trade_id, user_id)
            elif action == "settings":
                await self._handle_settings(query, trade_id, user_id)
            elif action == "back":
                await self._handle_back(query, trade_id, user_id)
            elif action == "edit":
                await self._handle_edit_settings(query, trade_id, user_id, parts[2])
            elif action == "reset":
                await self._handle_reset_settings(query, trade_id, user_id)
            else:
                await query.edit_message_text("❌ أمر غير معروف")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة استعلام الأزرار: {e}")
            try:
                await query.edit_message_text("❌ حدث خطأ غير متوقع")
            except:
                pass
    
    async def _handle_tp(self, query: CallbackQuery, trade_id: str, percentage_str: str) -> None:
        """معالجة هدف الربح"""
        try:
            percentage = float(percentage_str)
            
            # تنفيذ هدف الربح
            success, message = self.trade_manager.execute_tp(trade_id, percentage)
            
            if success:
                # إنشاء رسالة التأكيد
                confirmation_msg = self.interactive_messages.create_confirmation_message(
                    "tp", trade_id, percentage
                )
                
                # إنشاء لوحة مفاتيح جديدة
                trade_info = self.trade_manager.get_trade_info(trade_id)
                if trade_info and trade_info['status'] == 'OPEN':
                    # إعادة إنشاء رسالة الصفقة المحدثة
                    updated_msg, keyboard = self.interactive_messages.create_trade_message(
                        trade_id, query.from_user.id
                    )
                    await query.edit_message_text(
                        text=updated_msg,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                    
                    # إرسال رسالة تأكيد منفصلة
                    await query.message.reply_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
            else:
                error_msg = self.interactive_messages.create_error_message(message)
                await query.edit_message_text(error_msg, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في معالجة TP: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ هدف الربح")
    
    async def _handle_sl(self, query: CallbackQuery, trade_id: str, percentage_str: str) -> None:
        """معالجة وقف الخسارة"""
        try:
            percentage = float(percentage_str)
            
            # تنفيذ وقف الخسارة
            success, message = self.trade_manager.execute_sl(trade_id, percentage)
            
            if success:
                # إنشاء رسالة التأكيد
                confirmation_msg = self.interactive_messages.create_confirmation_message(
                    "sl", trade_id, percentage
                )
                
                # إنشاء لوحة مفاتيح جديدة
                trade_info = self.trade_manager.get_trade_info(trade_id)
                if trade_info and trade_info['status'] == 'OPEN':
                    # إعادة إنشاء رسالة الصفقة المحدثة
                    updated_msg, keyboard = self.interactive_messages.create_trade_message(
                        trade_id, query.from_user.id
                    )
                    await query.edit_message_text(
                        text=updated_msg,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                    
                    # إرسال رسالة تأكيد منفصلة
                    await query.message.reply_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
            else:
                error_msg = self.interactive_messages.create_error_message(message)
                await query.edit_message_text(error_msg, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في معالجة SL: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ وقف الخسارة")
    
    async def _handle_partial_close(self, query: CallbackQuery, trade_id: str, percentage_str: str) -> None:
        """معالجة الإغلاق الجزئي"""
        try:
            percentage = float(percentage_str)
            
            # تنفيذ الإغلاق الجزئي
            success, message = self.trade_manager.execute_partial_close(trade_id, percentage)
            
            if success:
                # إنشاء رسالة التأكيد
                confirmation_msg = self.interactive_messages.create_confirmation_message(
                    "partial", trade_id, percentage
                )
                
                # إنشاء لوحة مفاتيح جديدة
                trade_info = self.trade_manager.get_trade_info(trade_id)
                if trade_info and trade_info['status'] == 'OPEN':
                    # إعادة إنشاء رسالة الصفقة المحدثة
                    updated_msg, keyboard = self.interactive_messages.create_trade_message(
                        trade_id, query.from_user.id
                    )
                    await query.edit_message_text(
                        text=updated_msg,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                    
                    # إرسال رسالة تأكيد منفصلة
                    await query.message.reply_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        confirmation_msg,
                        parse_mode='Markdown'
                    )
            else:
                error_msg = self.interactive_messages.create_error_message(message)
                await query.edit_message_text(error_msg, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الجزئي: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ الإغلاق الجزئي")
    
    async def _handle_full_close(self, query: CallbackQuery, trade_id: str) -> None:
        """معالجة الإغلاق الكامل"""
        try:
            # تنفيذ الإغلاق الكامل
            success, message = self.trade_manager.close_trade_completely(trade_id)
            
            if success:
                # إنشاء رسالة التأكيد
                confirmation_msg = self.interactive_messages.create_confirmation_message(
                    "close", trade_id
                )
                await query.edit_message_text(
                    confirmation_msg,
                    parse_mode='Markdown'
                )
            else:
                error_msg = self.interactive_messages.create_error_message(message)
                await query.edit_message_text(error_msg, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الكامل: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ الإغلاق الكامل")
    
    async def _handle_refresh(self, query: CallbackQuery, trade_id: str, user_id: int) -> None:
        """معالجة تحديث الصفقة"""
        try:
            # محاولة تحديث سعر الصفقة (هنا يمكن إضافة منطق الحصول على السعر الحالي)
            # trade_manager.update_trade_price(trade_id, current_price)
            
            # إعادة إنشاء رسالة الصفقة
            updated_msg, keyboard = self.interactive_messages.create_trade_message(
                trade_id, user_id
            )
            
            if updated_msg and keyboard:
                await query.edit_message_text(
                    text=updated_msg,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ خطأ في تحديث الصفقة")
                
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقة: {e}")
            await query.edit_message_text("❌ خطأ في تحديث الصفقة")
    
    async def _handle_settings(self, query: CallbackQuery, trade_id: str, user_id: int) -> None:
        """معالجة فتح إعدادات النسب"""
        try:
            settings_msg, keyboard = self.interactive_messages.create_settings_message(
                trade_id, user_id
            )
            
            await query.edit_message_text(
                text=settings_msg,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطأ في فتح الإعدادات: {e}")
            await query.edit_message_text("❌ خطأ في فتح الإعدادات")
    
    async def _handle_back(self, query: CallbackQuery, trade_id: str, user_id: int) -> None:
        """معالجة العودة لرسالة الصفقة"""
        try:
            updated_msg, keyboard = self.interactive_messages.create_trade_message(
                trade_id, user_id
            )
            
            if updated_msg and keyboard:
                await query.edit_message_text(
                    text=updated_msg,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ خطأ في العودة للصفقة")
                
        except Exception as e:
            logger.error(f"خطأ في العودة للصفقة: {e}")
            await query.edit_message_text("❌ خطأ في العودة للصفقة")
    
    async def _handle_edit_settings(self, query: CallbackQuery, trade_id: str, user_id: int, setting_type: str) -> None:
        """معالجة تعديل الإعدادات"""
        try:
            # حفظ نوع الإعداد المراد تعديله
            self.user_editing_settings[user_id] = {
                'setting_type': setting_type,
                'trade_id': trade_id
            }
            
            # إنشاء رسالة التعديل
            edit_msg = self.interactive_messages.create_settings_edit_message(setting_type, trade_id)
            
            await query.edit_message_text(
                text=edit_msg,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطأ في تعديل الإعدادات: {e}")
            await query.edit_message_text("❌ خطأ في تعديل الإعدادات")
    
    async def _handle_reset_settings(self, query: CallbackQuery, trade_id: str, user_id: int) -> None:
        """معالجة إعادة تعيين الإعدادات"""
        try:
            # إعادة تعيين الإعدادات للافتراضية
            default_settings = {
                'tp_percentages': [1.0, 2.0, 5.0],
                'sl_percentages': [1.0, 2.0, 3.0],
                'partial_close_percentages': [25.0, 50.0, 75.0]
            }
            
            self.interactive_messages.update_user_settings(user_id, default_settings)
            
            # العودة لإعدادات الصفقة
            await self._handle_settings(query, trade_id, user_id)
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين الإعدادات: {e}")
            await query.edit_message_text("❌ خطأ في إعادة تعيين الإعدادات")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """معالجة الرسائل النصية لتعديل الإعدادات"""
        try:
            user_id = update.message.from_user.id
            
            # التحقق من أن المستخدم يعدل إعدادات
            if user_id not in self.user_editing_settings:
                return False
            
            text = update.message.text.strip()
            
            # التحقق من إلغاء التعديل
            if text.lower() in ['إلغاء', 'cancel', 'الغاء']:
                del self.user_editing_settings[user_id]
                await update.message.reply_text("✅ تم إلغاء التعديل")
                return True
            
            # تحليل النسب الجديدة
            try:
                percentages = self.interactive_messages.parse_percentages(text)
                
                # الحصول على الإعدادات الحالية
                user_settings = self.interactive_messages.get_user_settings(user_id)
                setting_info = self.user_editing_settings[user_id]
                setting_type = setting_info['setting_type']
                trade_id = setting_info['trade_id']
                
                # تحديث الإعدادات
                if setting_type == 'tp':
                    user_settings['tp_percentages'] = percentages
                elif setting_type == 'sl':
                    user_settings['sl_percentages'] = percentages
                elif setting_type == 'partial':
                    user_settings['partial_close_percentages'] = percentages
                
                # حفظ الإعدادات المحدثة
                self.interactive_messages.update_user_settings(user_id, user_settings)
                
                # حذف من قائمة التعديل
                del self.user_editing_settings[user_id]
                
                # إنشاء رسالة النجاح
                success_msg = f"""✅ **تم تحديث الإعدادات بنجاح!**

🎯 **أهداف الربح:** {', '.join([f'{p}%' for p in user_settings['tp_percentages']])}
🛑 **وقف الخسارة:** {', '.join([f'{p}%' for p in user_settings['sl_percentages']])}
✂️ **الإغلاق الجزئي:** {', '.join([f'{p}%' for p in user_settings['partial_close_percentages']])}

💡 **الإعدادات الجديدة ستنطبق على الصفقات الحالية**"""
                
                await update.message.reply_text(
                    success_msg,
                    parse_mode='Markdown'
                )
                
                return True
                
            except ValueError as e:
                error_msg = f"""❌ **خطأ في النسب المدخلة**

⚠️ **السبب:** {str(e)}

💡 **مثال صحيح:** `1, 2, 5` أو `1.5, 3, 7.5`

📝 **أعد المحاولة أو أرسل "إلغاء" للعودة**"""
                
                await update.message.reply_text(
                    error_msg,
                    parse_mode='Markdown'
                )
                return True
                
        except Exception as e:
            logger.error(f"خطأ في معالجة رسالة النص: {e}")
            return False
    
    def is_user_editing_settings(self, user_id: int) -> bool:
        """التحقق من أن المستخدم يعدل إعدادات"""
        return user_id in self.user_editing_settings
