#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التكامل المحسن - ربط المكونات الجديدة مع النظام الحالي
يحافظ على آلية التوقيع وحساب السعر مع دعم تعديل المتغيرات
"""

import logging
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from flexible_config_manager import flexible_config_manager
from enhanced_bot_interface import enhanced_bot_interface
from enhanced_trade_executor import enhanced_trade_executor
from database import db_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class IntegratedTradingSystem:
    """نظام التداول المتكامل المحسن"""
    
    def __init__(self):
        self.system_active = True
        self.integration_log = []
        
    async def handle_enhanced_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة استدعاءات الواجهة المحسنة"""
        try:
            if update.callback_query is None:
                return
            
            query = update.callback_query
            data = query.data
            user_id = query.from_user.id
            
            # معالجة استدعاءات الإعدادات المحسنة
            if data == "enhanced_settings":
                await enhanced_bot_interface.show_enhanced_settings_menu(update, context)
            
            elif data == "api_settings":
                await enhanced_bot_interface.show_api_settings(update, context)
            
            elif data == "trade_amount_settings":
                await enhanced_bot_interface.show_trade_amount_settings(update, context)
            
            elif data == "leverage_settings":
                await enhanced_bot_interface.show_leverage_settings(update, context)
            
            elif data == "market_type_settings":
                await enhanced_bot_interface.show_market_type_settings(update, context)
            
            elif data == "account_type_settings":
                await enhanced_bot_interface.show_account_type_settings(update, context)
            
            elif data == "exchange_settings":
                await enhanced_bot_interface.show_exchange_settings(update, context)
            
            elif data == "settings_summary":
                await enhanced_bot_interface.show_settings_summary(update, context)
            
            # معالجة استدعاءات API
            elif data == "update_bybit_api":
                enhanced_bot_interface.user_input_states[user_id] = "waiting_for_bybit_api_key"
                await query.edit_message_text("🔑 أدخل مفتاح Bybit API Key:")
            
            elif data == "update_mexc_api":
                enhanced_bot_interface.user_input_states[user_id] = "waiting_for_mexc_api_key"
                await query.edit_message_text("🔑 أدخل مفتاح MEXC API Key:")
            
            elif data == "test_api_connection":
                await self._test_api_connection(update, context)
            
            # معالجة استدعاءات المبالغ السريعة
            elif data.startswith("amount_"):
                amount = float(data.split("_")[1])
                await self._update_trade_amount(update, context, amount)
            
            elif data == "custom_amount":
                enhanced_bot_interface.user_input_states[user_id] = "waiting_for_custom_amount"
                await query.edit_message_text("💰 أدخل مبلغ التداول المخصص (1-10000):")
            
            # معالجة استدعاءات الرافعة السريعة
            elif data.startswith("leverage_"):
                leverage = int(data.split("_")[1])
                await self._update_leverage(update, context, leverage)
            
            elif data == "custom_leverage":
                enhanced_bot_interface.user_input_states[user_id] = "waiting_for_custom_leverage"
                await query.edit_message_text("⚡ أدخل الرافعة المالية المخصصة (1-100):")
            
            # معالجة استدعاءات نوع السوق
            elif data == "market_spot":
                await self._update_market_type(update, context, "spot")
            
            elif data == "market_futures":
                await self._update_market_type(update, context, "futures")
            
            # معالجة استدعاءات نوع الحساب
            elif data == "account_real":
                await self._update_account_type(update, context, "real")
            
            elif data == "account_demo":
                await self._update_account_type(update, context, "demo")
            
            # معالجة استدعاءات المنصة
            elif data == "exchange_bybit":
                await self._update_exchange(update, context, "bybit")
            
            elif data == "exchange_mexc":
                await self._update_exchange(update, context, "mexc")
            
            # معالجة إعادة تعيين الإعدادات
            elif data == "reset_settings":
                await self._reset_user_settings(update, context)
            
            await query.answer()
            
        except Exception as e:
            logger.error(f"خطأ في معالجة استدعاء الواجهة المحسنة: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def handle_enhanced_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل للواجهة المحسنة"""
        try:
            if update.message is None:
                return
            
            # تمرير الرسالة لمعالج الإدخال المخصص
            await enhanced_bot_interface.handle_custom_input(update, context)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة رسالة الواجهة المحسنة: {e}")
    
    async def execute_enhanced_signal(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ إشارة باستخدام النظام المحسن"""
        try:
            # التحقق من حالة النظام
            if not self.system_active:
                return {
                    'success': False,
                    'message': 'النظام معطل حالياً',
                    'error_type': 'SYSTEM_DISABLED'
                }
            
            # تنفيذ الصفقة باستخدام النظام المحسن
            result = await enhanced_trade_executor.execute_trade(user_id, signal_data)
            
            # تسجيل التنفيذ
            self.integration_log.append({
                'user_id': user_id,
                'timestamp': result.get('timestamp', ''),
                'signal_id': signal_data.get('signal_id', ''),
                'result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإشارة المحسنة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الإشارة: {e}',
                'error_type': 'SIGNAL_EXECUTION_ERROR'
            }
    
    async def _test_api_connection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختبار اتصال API"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            if config['account_type'] == 'demo':
                await update.callback_query.edit_message_text(
                    "ℹ️ الحساب التجريبي لا يتطلب اختبار API",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 العودة", callback_data="api_settings")
                    ]])
                )
                return
            
            # اختبار API للحساب الحقيقي
            if config['exchange'] == 'bybit':
                api_key = config.get('bybit_api_key', '')
                api_secret = config.get('bybit_api_secret', '')
            else:
                api_key = config.get('mexc_api_key', '')
                api_secret = config.get('mexc_api_secret', '')
            
            if not api_key or not api_secret:
                await update.callback_query.edit_message_text(
                    "❌ مفاتيح API غير محفوظة",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 العودة", callback_data="api_settings")
                    ]])
                )
                return
            
            # اختبار الاتصال
            success, message = flexible_config_manager._test_api_connection(user_id, {
                'api_key': api_key,
                'api_secret': api_secret,
                'exchange': config['exchange']
            })
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="api_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في اختبار API: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def _update_trade_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
        """تحديث مبلغ التداول"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            success, message = flexible_config_manager.update_user_config(user_id, {'trade_amount': amount})
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="trade_amount_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مبلغ التداول: {e}")
    
    async def _update_leverage(self, update: Update, context: ContextTypes.DEFAULT_TYPE, leverage: int):
        """تحديث الرافعة المالية"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            success, message = flexible_config_manager.update_user_config(user_id, {'leverage': leverage})
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="leverage_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الرافعة المالية: {e}")
    
    async def _update_market_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, market_type: str):
        """تحديث نوع السوق"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            success, message = flexible_config_manager.update_user_config(user_id, {'market_type': market_type})
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="market_type_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تحديث نوع السوق: {e}")
    
    async def _update_account_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_type: str):
        """تحديث نوع الحساب"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            success, message = flexible_config_manager.update_user_config(user_id, {'account_type': account_type})
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="account_type_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تحديث نوع الحساب: {e}")
    
    async def _update_exchange(self, update: Update, context: ContextTypes.DEFAULT_TYPE, exchange: str):
        """تحديث المنصة"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            success, message = flexible_config_manager.update_user_config(user_id, {'exchange': exchange})
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="exchange_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تحديث المنصة: {e}")
    
    async def _reset_user_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعادة تعيين إعدادات المستخدم"""
        try:
            if update.callback_query is None:
                return
            
            user_id = update.callback_query.from_user.id
            
            # إعادة تعيين الإعدادات إلى القيم الافتراضية
            default_config = flexible_config_manager._get_default_config()
            default_config['user_id'] = user_id
            
            success, message = flexible_config_manager.update_user_config(user_id, default_config)
            
            status_icon = "✅" if success else "❌"
            await update.callback_query.edit_message_text(
                f"{status_icon} {message}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين الإعدادات: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        try:
            return {
                'system_active': self.system_active,
                'config_manager_active': True,
                'bot_interface_active': True,
                'trade_executor_active': True,
                'integration_log_count': len(self.integration_log),
                'last_integration': self.integration_log[-1] if self.integration_log else None
            }
        except Exception as e:
            logger.error(f"خطأ في جلب حالة النظام: {e}")
            return {
                'system_active': False,
                'error': str(e)
            }
    
    def toggle_system(self, active: bool = None):
        """تبديل حالة النظام"""
        try:
            if active is None:
                self.system_active = not self.system_active
            else:
                self.system_active = active
            
            logger.info(f"تم تبديل حالة النظام إلى: {'نشط' if self.system_active else 'معطل'}")
            
        except Exception as e:
            logger.error(f"خطأ في تبديل حالة النظام: {e}")

# إنشاء مثيل عام للنظام المتكامل
integrated_trading_system = IntegratedTradingSystem()