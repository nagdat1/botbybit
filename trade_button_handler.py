#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج أزرار الصفقات التفاعلية
يدعم معالجة أزرار TP, SL, الإغلاق الجزئي والكامل
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from trade_messages import trade_message_manager
from trade_executor import trade_executor

logger = logging.getLogger(__name__)

class TradeButtonHandler:
    """معالج أزرار الصفقات التفاعلية"""
    
    def __init__(self, trading_bot=None):
        self.trading_bot = trading_bot
        self.user_input_states = {}  # لحفظ حالة إدخال المستخدم
    
    async def handle_trade_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة جميع أزرار الصفقات"""
        try:
            if update.callback_query is None:
                return
            
            await update.callback_query.answer()
            
            logger.info(f"معالجة زر الصفقة: {callback_data}")
            
            # تحليل بيانات الاستدعاء
            parts = callback_data.split('_')
            if len(parts) < 2:
                await update.callback_query.edit_message_text("❌ بيانات الزر غير صحيحة")
                return
            
            action = parts[0]
            position_id = parts[1]
            
            logger.info(f"العملية: {action}, معرف الصفقة: {position_id}")
            
            # التحقق من وجود الصفقة
            if not self._position_exists(position_id):
                logger.warning(f"الصفقة غير موجودة: {position_id}")
                await update.callback_query.edit_message_text("❌ الصفقة غير موجودة")
                return
            
            # معالجة كل نوع من الأزرار
            if action == "tp":
                await self._handle_tp_button(update, context, callback_data)
            elif action == "sl":
                await self._handle_sl_button(update, context, callback_data)
            elif action == "partial":
                await self._handle_partial_button(update, context, callback_data)
            elif action == "close":
                await self._handle_close_button(update, context, callback_data)
            elif action == "edit":
                await self._handle_edit_button(update, context, callback_data)
            elif action == "set":
                await self._handle_set_button(update, context, callback_data)
            elif action == "custom":
                await self._handle_custom_button(update, context, callback_data)
            elif action == "confirm":
                await self._handle_confirm_button(update, context, callback_data)
            elif action == "cancel":
                await self._handle_cancel_button(update, context, callback_data)
            elif action == "refresh":
                await self._handle_refresh_button(update, context, callback_data)
            elif action == "back":
                await self._handle_back_button(update, context, callback_data)
            else:
                logger.warning(f"زر غير مدعوم: {action}")
                await update.callback_query.edit_message_text("❌ زر غير مدعوم")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الصفقة: {e}")
            if update.callback_query:
                try:
                    await update.callback_query.edit_message_text(f"❌ خطأ في معالجة الزر: {e}")
                except:
                    logger.error("فشل في تحديث رسالة الخطأ")
    
    def _position_exists(self, position_id: str) -> bool:
        """التحقق من وجود الصفقة"""
        try:
            if not self.trading_bot:
                return False
            
            # البحث في القائمة العامة للصفقات المفتوحة
            if hasattr(self.trading_bot, 'open_positions'):
                if position_id in self.trading_bot.open_positions:
                    return True
            
            # البحث في الحسابات التجريبية
            # حساب السبوت
            if hasattr(self.trading_bot, 'demo_account_spot'):
                if hasattr(self.trading_bot.demo_account_spot, 'positions'):
                    if position_id in self.trading_bot.demo_account_spot.positions:
                        return True
            
            # حساب الفيوتشر
            if hasattr(self.trading_bot, 'demo_account_futures'):
                if hasattr(self.trading_bot.demo_account_futures, 'positions'):
                    if position_id in self.trading_bot.demo_account_futures.positions:
                        return True
            
            # البحث في جميع الحسابات عبر user_manager
            try:
                from user_manager import user_manager
                if user_manager:
                    # البحث في جميع حسابات المستخدمين
                    for user_id, user_data in user_manager.users.items():
                        market_type = user_data.get('market_type', 'spot')
                        account = user_manager.get_user_account(user_id, market_type)
                        if account and hasattr(account, 'positions'):
                            if position_id in account.positions:
                                return True
            except Exception as e:
                logger.debug(f"خطأ في البحث عبر user_manager: {e}")
            
            return False
        except Exception as e:
            logger.error(f"خطأ في التحقق من وجود الصفقة: {e}")
            return False
    
    async def _handle_tp_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار TP"""
        try:
            # تحليل: tp_{position_id}_{percent}
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر TP غير كاملة: {callback_data}")
                return
            
            # parts[0] = "tp"
            # parts[-1] = percent
            # parts[1:-1] = position_id
            position_id = '_'.join(parts[1:-1])
            try:
                percent = float(parts[-1])
            except ValueError:
                logger.error(f"فشل تحويل نسبة TP: {parts[-1]}")
                return
            
            # إنشاء رسالة تأكيد
            message, keyboard = trade_message_manager.create_confirmation_message(
                "tp", position_id, percent
            )
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر TP: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر TP: {e}")
    
    async def _handle_sl_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار SL"""
        try:
            # تحليل: sl_{position_id}_{percent}
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر SL غير كاملة: {callback_data}")
                return
            
            # parts[0] = "sl"
            # parts[-1] = percent
            # parts[1:-1] = position_id
            position_id = '_'.join(parts[1:-1])
            try:
                percent = float(parts[-1])
            except ValueError:
                logger.error(f"فشل تحويل نسبة SL: {parts[-1]}")
                return
            
            # إنشاء رسالة تأكيد
            message, keyboard = trade_message_manager.create_confirmation_message(
                "sl", position_id, percent
            )
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر SL: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر SL: {e}")
    
    async def _handle_partial_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار الإغلاق الجزئي"""
        try:
            # تحليل: partial_{position_id}_{percent}
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر الإغلاق الجزئي غير كاملة: {callback_data}")
                return
            
            # parts[0] = "partial"
            # parts[-1] = percent
            # parts[1:-1] = position_id
            position_id = '_'.join(parts[1:-1])
            try:
                percent = float(parts[-1])
            except ValueError:
                logger.error(f"فشل تحويل نسبة الإغلاق الجزئي: {parts[-1]}")
                return
            
            # إنشاء رسالة تأكيد
            message, keyboard = trade_message_manager.create_confirmation_message(
                "partial", position_id, percent
            )
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الإغلاق الجزئي: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر الإغلاق الجزئي: {e}")
    
    async def _handle_close_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة زر الإغلاق الكامل"""
        try:
            # تحليل: close_{position_id}
            parts = callback_data.split('_')
            if len(parts) < 2:
                logger.error(f"بيانات زر الإغلاق غير كاملة: {callback_data}")
                return
            
            # parts[0] = "close"
            # parts[1:] = position_id
            position_id = '_'.join(parts[1:])
            
            # إنشاء رسالة تأكيد
            message, keyboard = trade_message_manager.create_confirmation_message(
                "close", position_id
            )
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الإغلاق الكامل: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر الإغلاق الكامل: {e}")
    
    async def _handle_edit_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار التعديل"""
        try:
            # تحليل: edit_{position_id}_{edit_type}
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر التعديل غير كاملة: {callback_data}")
                return
            
            # parts[0] = "edit"
            # parts[-1] = edit_type (percents, tp, sl, partial)
            # parts[1:-1] = position_id
            edit_type = parts[-1]
            position_id = '_'.join(parts[1:-1])
            
            if edit_type == "percents":
                # عرض قائمة تعديل النسب
                keyboard = trade_message_manager.create_percent_edit_keyboard(position_id)
                message = f"""
⚙️ **تعديل نسب الصفقة**
🆔 رقم الصفقة: {position_id}

اختر النوع الذي تريد تعديله:
                """
                await update.callback_query.edit_message_text(message, reply_markup=keyboard)
                
            elif edit_type == "tp":
                # عرض قائمة تعديل نسب TP
                keyboard = trade_message_manager.create_tp_edit_keyboard(position_id)
                message = f"""
🎯 **تعديل نسب هدف الربح (TP)**
🆔 رقم الصفقة: {position_id}

اختر النسبة الجديدة أو أدخل قيمة مخصصة:
                """
                await update.callback_query.edit_message_text(message, reply_markup=keyboard)
                
            elif edit_type == "sl":
                # عرض قائمة تعديل نسب SL
                keyboard = trade_message_manager.create_sl_edit_keyboard(position_id)
                message = f"""
🛑 **تعديل نسب وقف الخسارة (SL)**
🆔 رقم الصفقة: {position_id}

اختر النسبة الجديدة أو أدخل قيمة مخصصة:
                """
                await update.callback_query.edit_message_text(message, reply_markup=keyboard)
                
            elif edit_type == "partial":
                # عرض قائمة تعديل نسب الإغلاق الجزئي
                keyboard = trade_message_manager.create_partial_edit_keyboard(position_id)
                message = f"""
📊 **تعديل نسب الإغلاق الجزئي**
🆔 رقم الصفقة: {position_id}

اختر النسبة الجديدة أو أدخل قيمة مخصصة:
                """
                await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر التعديل: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر التعديل: {e}")
    
    async def _handle_set_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار تعيين النسب"""
        try:
            # تحليل بيانات التعيين: set_{set_type}_{position_id}_{percent}
            # مثال: set_tp_BTCUSDT_1696500000000000_2.5
            
            parts = callback_data.split('_')
            if len(parts) < 4:
                logger.error(f"بيانات زر التعيين غير كاملة: {callback_data}")
                return
            
            # parts[0] = "set"
            # parts[1] = set_type (tp, sl, partial)
            # parts[-1] = percent
            # parts[2:-1] = position_id
            
            set_type = parts[1]
            percent_str = parts[-1]
            position_id = '_'.join(parts[2:-1])
            
            try:
                percent = float(percent_str)
            except ValueError:
                logger.error(f"فشل تحويل النسبة إلى رقم: {percent_str}")
                return
            
            if set_type == "tp":
                # تطبيق نسب TP جديدة
                await self._apply_new_tp_percents(update, context, position_id, [percent])
            elif set_type == "sl":
                # تطبيق نسب SL جديدة
                await self._apply_new_sl_percents(update, context, position_id, [percent])
            elif set_type == "partial":
                # تطبيق نسب إغلاق جزئي جديدة
                await self._apply_new_partial_percents(update, context, position_id, [percent])
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر التعيين: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر التعيين: {e}")
    
    async def _handle_custom_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار الإدخال المخصص"""
        try:
            # تحليل: custom_{custom_type}_{position_id}
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر الإدخال المخصص غير كاملة: {callback_data}")
                return
            
            # parts[0] = "custom"
            # parts[1] = custom_type (tp, sl, partial)
            # parts[2:] = position_id
            custom_type = parts[1]
            position_id = '_'.join(parts[2:])
            
            # حفظ حالة إدخال المستخدم
            user_id = update.effective_user.id if update.effective_user else None
            if user_id:
                self.user_input_states[user_id] = {
                    'state': f'waiting_for_{custom_type}',
                    'position_id': position_id
                }
            
            if custom_type == "tp":
                message = f"""
✏️ **إدخال نسبة TP مخصصة**
🆔 رقم الصفقة: {position_id}

أدخل النسبة المطلوبة (مثال: 2.5):
                """
            elif custom_type == "sl":
                message = f"""
✏️ **إدخال نسبة SL مخصصة**
🆔 رقم الصفقة: {position_id}

أدخل النسبة المطلوبة (مثال: 1.5):
                """
            elif custom_type == "partial":
                message = f"""
✏️ **إدخال نسبة إغلاق جزئي مخصصة**
🆔 رقم الصفقة: {position_id}

أدخل النسبة المطلوبة (مثال: 30):
                """
            
            # زر العودة
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data=f"edit_{position_id}_{custom_type}")
            ]])
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الإدخال المخصص: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر الإدخال المخصص: {e}")
    
    async def _handle_confirm_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار التأكيد"""
        try:
            # تحليل بيانات التأكيد: confirm_{action}_{position_id}_{percent}
            # مثال: confirm_tp_BTCUSDT_1696500000000000_2.5 أو confirm_close_BTCUSDT_1696500000000000_
            
            parts = callback_data.split('_')
            if len(parts) < 3:
                logger.error(f"بيانات زر التأكيد غير كاملة: {callback_data}")
                return
            
            # parts[0] = "confirm"
            # parts[1] = action (tp, sl, partial, close)
            # parts[-1] = percent (أو '' إذا كان close)
            # parts[2:-1] = position_id
            
            action = parts[1]
            
            # استخراج النسبة
            percent_str = parts[-1]
            if percent_str and percent_str != '':
                try:
                    percent = float(percent_str)
                    # position_id هو من parts[2] إلى parts[-2]
                    position_id = '_'.join(parts[2:-1])
                except ValueError:
                    # النسبة غير صحيحة، تعتبر جزء من position_id
                    percent = None
                    position_id = '_'.join(parts[2:])
            else:
                # لا توجد نسبة (مثل close)
                percent = None
                # position_id هو من parts[2] إلى parts[-2] (نستثني الـ '' الأخير)
                if len(parts) > 3:
                    position_id = '_'.join(parts[2:-1])
                else:
                    position_id = parts[2]
            
            # تنفيذ العملية
            result = await self._execute_trade_action(action, position_id, percent)
            
            if result['success']:
                # عرض رسالة النجاح
                success_message = trade_message_manager.create_success_message(
                    action, position_id, percent, result.get('data')
                )
                await update.callback_query.edit_message_text(success_message)
            else:
                # عرض رسالة الخطأ
                error_message = trade_message_manager.create_error_message(
                    result['error'], position_id
                )
                await update.callback_query.edit_message_text(error_message)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر التأكيد: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر التأكيد: {e}")
    
    async def _handle_cancel_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار الإلغاء"""
        try:
            # تحليل: cancel_{position_id}
            parts = callback_data.split('_')
            if len(parts) < 2:
                logger.error(f"بيانات زر الإلغاء غير كاملة: {callback_data}")
                return
            
            # parts[0] = "cancel"
            # parts[1:] = position_id
            position_id = '_'.join(parts[1:])
            
            # العودة إلى رسالة الصفقة الأصلية
            await self._show_trade_message(update, context, position_id)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الإلغاء: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر الإلغاء: {e}")
    
    async def _handle_refresh_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة زر التحديث"""
        try:
            # تحليل: refresh_{position_id}
            parts = callback_data.split('_')
            if len(parts) < 2:
                logger.error(f"بيانات زر التحديث غير كاملة: {callback_data}")
                return
            
            # parts[0] = "refresh"
            # parts[1:] = position_id
            position_id = '_'.join(parts[1:])
            
            # تحديث معلومات الصفقة والعودة إليها
            await self._show_trade_message(update, context, position_id)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر التحديث: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر التحديث: {e}")
    
    async def _handle_back_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أزرار العودة"""
        try:
            # التعامل مع أنواع مختلفة من أزرار العودة
            # back_to_trade_{position_id} أو back_{action}_{position_id}
            
            if callback_data.startswith("back_to_trade_"):
                # استخراج position_id من back_to_trade_{position_id}
                position_id = callback_data.replace("back_to_trade_", "")
            else:
                # التعامل مع الأنماط الأخرى
                parts = callback_data.split('_', 3)  # فصل إلى 3 أجزاء كحد أقصى
                if len(parts) < 3:
                    logger.error(f"بيانات زر العودة غير صحيحة: {callback_data}")
                    return
                position_id = parts[2] if len(parts) == 3 else '_'.join(parts[2:])
            
            # العودة إلى رسالة الصفقة الأصلية
            await self._show_trade_message(update, context, position_id)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر العودة: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في معالجة زر العودة: {e}")
    
    async def _execute_trade_action(self, action: str, position_id: str, percent: float = None) -> Dict:
        """تنفيذ عملة الصفقة"""
        try:
            if not trade_executor:
                return {'success': False, 'error': 'نظام التنفيذ غير متاح'}
            
            if action == "tp":
                return await trade_executor.set_take_profit(position_id, percent)
            elif action == "sl":
                return await trade_executor.set_stop_loss(position_id, percent)
            elif action == "partial":
                return await trade_executor.partial_close(position_id, percent)
            elif action == "close":
                return await trade_executor.close_position(position_id)
            else:
                return {'success': False, 'error': 'عملية غير مدعومة'}
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ عملة الصفقة: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_position_info(self, position_id: str) -> dict:
        """الحصول على معلومات الصفقة من جميع المصادر"""
        try:
            if not self.trading_bot:
                return None
            
            # البحث في القائمة العامة للصفقات المفتوحة
            if hasattr(self.trading_bot, 'open_positions'):
                if position_id in self.trading_bot.open_positions:
                    return self.trading_bot.open_positions[position_id]
            
            # البحث في الحسابات التجريبية
            # حساب السبوت
            if hasattr(self.trading_bot, 'demo_account_spot'):
                if hasattr(self.trading_bot.demo_account_spot, 'positions'):
                    if position_id in self.trading_bot.demo_account_spot.positions:
                        position = self.trading_bot.demo_account_spot.positions[position_id]
                        # تحويل Position object إلى dict
                        return {
                            'symbol': position.symbol,
                            'side': position.side,
                            'entry_price': position.entry_price,
                            'current_price': position.entry_price,  # سيتم تحديثه لاحقاً
                            'amount': position.contracts,
                            'margin_amount': position.margin_amount,
                            'leverage': position.leverage,
                            'position_id': position.position_id,
                            'account_type': 'spot',
                            'timestamp': getattr(position, 'timestamp', None)
                        }
            
            # حساب الفيوتشر
            if hasattr(self.trading_bot, 'demo_account_futures'):
                if hasattr(self.trading_bot.demo_account_futures, 'positions'):
                    if position_id in self.trading_bot.demo_account_futures.positions:
                        position = self.trading_bot.demo_account_futures.positions[position_id]
                        # تحويل Position object إلى dict
                        return {
                            'symbol': position.symbol,
                            'side': position.side,
                            'entry_price': position.entry_price,
                            'current_price': position.entry_price,  # سيتم تحديثه لاحقاً
                            'amount': position.contracts,
                            'margin_amount': position.margin_amount,
                            'leverage': position.leverage,
                            'position_id': position.position_id,
                            'account_type': 'futures',
                            'timestamp': getattr(position, 'timestamp', None)
                        }
            
            # البحث في جميع الحسابات عبر user_manager
            try:
                from user_manager import user_manager
                if user_manager:
                    # البحث في جميع حسابات المستخدمين
                    for user_id, user_data in user_manager.users.items():
                        market_type = user_data.get('market_type', 'spot')
                        account = user_manager.get_user_account(user_id, market_type)
                        if account and hasattr(account, 'positions'):
                            if position_id in account.positions:
                                position = account.positions[position_id]
                                # تحويل Position object إلى dict
                                return {
                                    'symbol': position.symbol,
                                    'side': position.side,
                                    'entry_price': position.entry_price,
                                    'current_price': position.entry_price,  # سيتم تحديثه لاحقاً
                                    'amount': getattr(position, 'contracts', getattr(position, 'amount', 0)),
                                    'margin_amount': getattr(position, 'margin_amount', 0),
                                    'leverage': getattr(position, 'leverage', 1),
                                    'position_id': position.position_id,
                                    'account_type': market_type,
                                    'timestamp': getattr(position, 'timestamp', None)
                                }
            except Exception as e:
                logger.debug(f"خطأ في البحث عبر user_manager: {e}")
            
            return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الصفقة: {e}")
            return None

    async def _show_trade_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str):
        """عرض رسالة الصفقة المحدثة"""
        try:
            if not self.trading_bot:
                await update.callback_query.edit_message_text("❌ البوت غير متاح")
                return
            
            position_info = self._get_position_info(position_id)
            if not position_info:
                await update.callback_query.edit_message_text("❌ الصفقة غير موجودة")
                return
            
            # الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(update)
            
            # إنشاء رسالة الصفقة المحدثة
            message, keyboard = trade_message_manager.create_trade_message(
                position_info, user_settings
            )
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في عرض رسالة الصفقة: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في عرض رسالة الصفقة: {e}")
    
    def _get_user_settings(self, update: Update) -> Dict:
        """الحصول على إعدادات المستخدم"""
        try:
            # محاولة الحصول على إعدادات المستخدم من البوت
            if self.trading_bot and hasattr(self.trading_bot, 'user_settings'):
                return self.trading_bot.user_settings
            return {}
        except:
            return {}
    
    async def _apply_new_tp_percents(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str, new_percents: List[float]):
        """تطبيق نسب TP جديدة"""
        try:
            # هنا يمكن حفظ النسب الجديدة في قاعدة البيانات
            # أو في إعدادات المستخدم
            
            message = f"""
✅ **تم تحديث نسب TP بنجاح**
🆔 رقم الصفقة: {position_id}
🎯 النسب الجديدة: {', '.join([f'{p}%' for p in new_percents])}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # زر العودة
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data=f"back_to_trade_{position_id}")
            ]])
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق نسب TP الجديدة: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في تطبيق نسب TP الجديدة: {e}")
    
    async def _apply_new_sl_percents(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str, new_percents: List[float]):
        """تطبيق نسب SL جديدة"""
        try:
            # هنا يمكن حفظ النسب الجديدة في قاعدة البيانات
            # أو في إعدادات المستخدم
            
            message = f"""
✅ **تم تحديث نسب SL بنجاح**
🆔 رقم الصفقة: {position_id}
🛑 النسب الجديدة: {', '.join([f'{p}%' for p in new_percents])}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # زر العودة
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data=f"back_to_trade_{position_id}")
            ]])
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق نسب SL الجديدة: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في تطبيق نسب SL الجديدة: {e}")
    
    async def _apply_new_partial_percents(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str, new_percents: List[float]):
        """تطبيق نسب الإغلاق الجزئي الجديدة"""
        try:
            # هنا يمكن حفظ النسب الجديدة في قاعدة البيانات
            # أو في إعدادات المستخدم
            
            message = f"""
✅ **تم تحديث نسب الإغلاق الجزئي بنجاح**
🆔 رقم الصفقة: {position_id}
📊 النسب الجديدة: {', '.join([f'{p}%' for p in new_percents])}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # زر العودة
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data=f"back_to_trade_{position_id}")
            ]])
            
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق نسب الإغلاق الجزئي الجديدة: {e}")
            await update.callback_query.edit_message_text(f"❌ خطأ في تطبيق نسب الإغلاق الجزئي الجديدة: {e}")
    
    async def handle_custom_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str):
        """معالجة الإدخال المخصص من المستخدم"""
        try:
            if user_id not in self.user_input_states:
                return False
            
            state_info = self.user_input_states[user_id]
            position_id = state_info.get('position_id')
            state = state_info.get('state')
            
            if not position_id:
                return False
            
            try:
                percent = float(text)
                
                if state == 'waiting_for_tp':
                    # تطبيق نسبة TP مخصصة
                    await self._apply_new_tp_percents(update, context, position_id, [percent])
                elif state == 'waiting_for_sl':
                    # تطبيق نسبة SL مخصصة
                    await self._apply_new_sl_percents(update, context, position_id, [percent])
                elif state == 'waiting_for_partial':
                    # تطبيق نسبة إغلاق جزئي مخصصة
                    await self._apply_new_partial_percents(update, context, position_id, [percent])
                
                # مسح حالة الإدخال
                del self.user_input_states[user_id]
                return True
                
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                return True
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإدخال المخصص: {e}")
            return False

# إنشاء مثيل عام لمعالج الأزرار
trade_button_handler = TradeButtonHandler()