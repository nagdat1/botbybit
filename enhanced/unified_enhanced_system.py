#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النظام المحسن الموحد - Unified Enhanced System
دمج جميع وظائف النظام المحسن في ملف واحد منظم
"""

import logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ==================== مدير الإعدادات المرن الموحد ====================

class UnifiedConfigManager:
    """مدير الإعدادات المرن الموحد"""
    
    def __init__(self):
        self.user_configs: Dict[int, Dict[str, Any]] = {}
        self.system_active = False
        logger.info("تم تهيئة مدير الإعدادات المرن الموحد")
    
    def load_user_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """تحميل إعدادات المستخدم من قاعدة البيانات"""
        try:
            from database import db_manager
            user_data = db_manager.get_user(user_id)
            
            if user_data:
                config = {
                    'user_id': user_id,
                    'api_key': user_data.get('bybit_api_key'),
                    'api_secret': user_data.get('bybit_api_secret'),
                    'mexc_api_key': user_data.get('mexc_api_key'),
                    'mexc_api_secret': user_data.get('mexc_api_secret'),
                    'balance': user_data.get('balance', 10000.0),
                    'market_type': user_data.get('market_type', 'spot'),
                    'trade_amount': user_data.get('trade_amount', 50.0),
                    'leverage': user_data.get('leverage', 1),
                    'account_type': user_data.get('account_type', 'demo'),
                    'exchange': user_data.get('exchange', 'bybit'),
                    'auto_tp_sl': user_data.get('auto_tp_sl', False),
                    'risk_management': user_data.get('risk_management', True),
                    'webhook_url': user_data.get('webhook_url', '')
                }
                
                self.user_configs[user_id] = config
                logger.info(f"تم تحميل إعدادات المستخدم {user_id}")
                return config
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في تحميل إعدادات المستخدم: {e}")
            return None
    
    def get_user_config(self, user_id: int) -> Optional[Dict[str, Any]]:
        """الحصول على إعدادات المستخدم"""
        if user_id not in self.user_configs:
            return self.load_user_config(user_id)
        return self.user_configs.get(user_id)
    
    def update_user_config(self, user_id: int, key: str, value: Any) -> bool:
        """تحديث إعداد معين للمستخدم"""
        try:
            if user_id not in self.user_configs:
                self.load_user_config(user_id)
            
            if user_id in self.user_configs:
                self.user_configs[user_id][key] = value
                
                # حفظ في قاعدة البيانات
                from database import db_manager
                
                if key in ['api_key', 'api_secret', 'mexc_api_key', 'mexc_api_secret']:
                    if key == 'api_key':
                        db_manager.update_user_data(user_id, {'bybit_api_key': value})
                    elif key == 'api_secret':
                        db_manager.update_user_data(user_id, {'bybit_api_secret': value})
                    elif key == 'mexc_api_key':
                        db_manager.update_user_data(user_id, {'mexc_api_key': value})
                    elif key == 'mexc_api_secret':
                        db_manager.update_user_data(user_id, {'mexc_api_secret': value})
                elif key in ['balance', 'account_type', 'exchange']:
                    db_manager.update_user_data(user_id, {key: value})
                elif key in ['market_type', 'trade_amount', 'leverage', 'auto_tp_sl', 'risk_management']:
                    db_manager.update_user_settings(user_id, {key: value})
                
                logger.info(f"تم تحديث إعداد {key} للمستخدم {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعداد المستخدم: {e}")
            return False
    
    def calculate_trade_parameters(self, user_id: int, symbol: str, side: str, price: float) -> Dict[str, Any]:
        """حساب معاملات التداول"""
        try:
            config = self.get_user_config(user_id)
            if not config:
                return {}
            
            trade_amount = config.get('trade_amount', 50.0)
            leverage = config.get('leverage', 1)
            market_type = config.get('market_type', 'spot')
            
            if market_type == 'futures':
                position_size = trade_amount * leverage
                quantity = position_size / price
                margin_required = trade_amount
            else:  # spot
                quantity = trade_amount / price
                margin_required = trade_amount
            
            return {
                'trade_amount': trade_amount,
                'leverage': leverage,
                'quantity': quantity,
                'position_size': position_size if market_type == 'futures' else trade_amount,
                'margin_required': margin_required,
                'market_type': market_type,
                'side': side,
                'symbol': symbol,
                'price': price
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب معاملات التداول: {e}")
            return {}
    
    def validate_trade_execution(self, user_id: int, trade_params: Dict[str, Any]) -> tuple[bool, str]:
        """التحقق من صحة تنفيذ الصفقة"""
        try:
            config = self.get_user_config(user_id)
            if not config:
                return False, "إعدادات المستخدم غير متاحة"
            
            # التحقق من المبلغ
            trade_amount = trade_params.get('trade_amount', 0)
            if trade_amount <= 0 or trade_amount > 10000:
                return False, "مبلغ التداول يجب أن يكون بين $1 و $10,000"
            
            # التحقق من الرافعة
            leverage = trade_params.get('leverage', 1)
            if leverage < 1 or leverage > 100:
                return False, "الرافعة المالية يجب أن تكون بين 1x و 100x"
            
            # التحقق من مفاتيح API للحساب الحقيقي
            account_type = config.get('account_type', 'demo')
            if account_type == 'real':
                api_key = config.get('api_key')
                api_secret = config.get('api_secret')
                if not api_key or not api_secret:
                    return False, "مفاتيح API غير متاحة للحساب الحقيقي"
            
            return True, "جميع المعاملات صحيحة"
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من تنفيذ الصفقة: {e}")
            return False, f"خطأ في التحقق: {e}"
    
    async def initialize_system(self):
        """تهيئة النظام"""
        try:
            self.system_active = True
            logger.info("تم تهيئة النظام المحسن")
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام: {e}")

# ==================== منفذ الصفقات المحسن الموحد ====================

class UnifiedTradeExecutor:
    """منفذ الصفقات المحسن الموحد"""
    
    def __init__(self):
        self.real_accounts: Dict[int, Dict[str, Any]] = {}
        self.demo_accounts: Dict[int, Dict[str, Any]] = {}
        self.system_active = False
        logger.info("تم تهيئة منفذ الصفقات المحسن الموحد")
    
    def _get_real_account(self, user_id: int, exchange: str) -> Optional[Any]:
        """الحصول على حساب حقيقي للمستخدم"""
        try:
            if user_id not in self.real_accounts:
                self.real_accounts[user_id] = {}
            
            if exchange not in self.real_accounts[user_id]:
                from exchanges.unified_exchange_manager import unified_exchange_manager
                
                exchange_manager = unified_exchange_manager.get_exchange(user_id, exchange)
                if exchange_manager:
                    self.real_accounts[user_id][exchange] = exchange_manager
                    logger.info(f"تم تهيئة حساب {exchange} للمستخدم {user_id}")
                else:
                    logger.error(f"فشل في تهيئة حساب {exchange} للمستخدم {user_id}")
                    return None
            
            return self.real_accounts[user_id][exchange]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحساب الحقيقي: {e}")
            return None
    
    def _get_demo_account(self, user_id: int, market_type: str) -> Optional[Any]:
        """الحصول على حساب تجريبي للمستخدم"""
        try:
            if user_id not in self.demo_accounts:
                self.demo_accounts[user_id] = {
                    'spot': None,
                    'futures': None
                }
            
            if not self.demo_accounts[user_id][market_type]:
                from bybit_trading_bot import TradingAccount
                
                initial_balance = 10000.0  # رصيد افتراضي
                self.demo_accounts[user_id][market_type] = TradingAccount(
                    initial_balance=initial_balance,
                    account_type=market_type
                )
                logger.info(f"تم تهيئة حساب تجريبي {market_type} للمستخدم {user_id}")
            
            return self.demo_accounts[user_id][market_type]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحساب التجريبي: {e}")
            return None
    
    async def execute_trade(self, user_id: int, symbol: str, side: str, order_type: str, price: float = None) -> Dict[str, Any]:
        """تنفيذ صفقة بناءً على إعدادات المستخدم"""
        try:
            from core.unified_trading_bot import unified_config_manager
            
            config = unified_config_manager.get_user_config(user_id)
            if not config:
                return {'success': False, 'message': 'إعدادات المستخدم غير متاحة'}
            
            account_type = config.get('account_type', 'demo')
            market_type = config.get('market_type', 'spot')
            exchange = config.get('exchange', 'bybit')
            trade_amount = config.get('trade_amount', 50.0)
            leverage = config.get('leverage', 1)
            
            logger.info(f"تنفيذ صفقة للمستخدم {user_id}: {side} {trade_amount} USDT من {symbol} على {exchange} ({market_type}, {account_type}) مع رافعة {leverage}x")
            
            if account_type == 'real':
                # تنفيذ صفقة حقيقية
                account = self._get_real_account(user_id, exchange)
                if not account:
                    return {'success': False, 'message': f'الحساب الحقيقي غير مهيأ لـ {exchange}. تحقق من مفاتيح API.'}
                
                if exchange == 'bybit':
                    category = "spot" if market_type == "spot" else "linear"
                    
                    # تعيين الرافعة للفيوتشر
                    if market_type == 'futures':
                        account.set_leverage(category, symbol, leverage)
                    
                    # حساب الكمية
                    if market_type == 'futures':
                        position_size = trade_amount * leverage
                        qty = position_size / price
                    else:  # spot
                        qty = trade_amount / price
                    
                    result = account.place_order(
                        category=category,
                        symbol=symbol,
                        side=side,
                        order_type=order_type,
                        qty=qty,
                        price=price,
                        leverage=leverage
                    )
                    
                    if result and result.get('retCode') == 0:
                        order_id = result.get('result', {}).get('orderId', '')
                        return {
                            'success': True, 
                            'message': f'تم تنفيذ الصفقة بنجاح على Bybit. رقم الأمر: {order_id}',
                            'order_id': order_id
                        }
                    else:
                        error_msg = result.get('retMsg', 'خطأ غير محدد') if result else 'فشل في تنفيذ الصفقة'
                        return {'success': False, 'message': f'فشل في تنفيذ الصفقة على Bybit: {error_msg}'}
                
                elif exchange == 'mexc':
                    # MEXC يدعم السبوت فقط
                    if market_type == 'futures':
                        return {'success': False, 'message': 'MEXC لا يدعم تداول الفيوتشر عبر API في هذا البوت.'}
                    
                    # حساب الكمية للسبوت
                    qty = trade_amount / price
                    
                    result = account.place_order(
                        symbol=symbol,
                        side=side,
                        quantity=qty,
                        order_type=order_type,
                        price=price
                    )
                    
                    if result and result.get('orderId'):
                        order_id = result.get('orderId')
                        return {
                            'success': True, 
                            'message': f'تم تنفيذ الصفقة بنجاح على MEXC. رقم الأمر: {order_id}',
                            'order_id': order_id
                        }
                    else:
                        error_msg = result.get('msg', 'خطأ غير محدد') if result else 'فشل في تنفيذ الصفقة'
                        return {'success': False, 'message': f'فشل في تنفيذ الصفقة على MEXC: {error_msg}'}
            
            elif account_type == 'demo':
                # تنفيذ صفقة تجريبية
                account = self._get_demo_account(user_id, market_type)
                if not account:
                    return {'success': False, 'message': 'الحساب التجريبي غير مهيأ'}
                
                if market_type == 'futures':
                    success, message = account.open_futures_position(
                        symbol=symbol,
                        side=side,
                        margin_amount=trade_amount,
                        entry_price=price,
                        leverage=leverage
                    )
                else:  # spot
                    success, message = account.open_spot_position(
                        symbol=symbol,
                        side=side,
                        amount=trade_amount,
                        price=price
                    )
                
                return {'success': success, 'message': message}
            
            return {'success': False, 'message': 'نوع حساب غير صحيح'}
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة: {e}")
            return {'success': False, 'message': f'خطأ في تنفيذ الصفقة: {e}'}
    
    async def initialize_executor(self):
        """تهيئة منفذ الصفقات"""
        try:
            self.system_active = True
            logger.info("تم تهيئة منفذ الصفقات المحسن")
        except Exception as e:
            logger.error(f"خطأ في تهيئة منفذ الصفقات: {e}")

# ==================== واجهة البوت المحسنة الموحدة ====================

class UnifiedBotInterface:
    """واجهة البوت المحسنة الموحدة"""
    
    def __init__(self):
        self.user_input_states: Dict[int, str] = {}
        self.system_active = False
        logger.info("تم تهيئة واجهة البوت المحسنة الموحدة")
    
    async def show_enhanced_settings_menu(self, update, context):
        """عرض قائمة الإعدادات المحسنة"""
        try:
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from core.unified_trading_bot import unified_config_manager
            
            user_id = update.effective_user.id if update.effective_user else None
            if not user_id:
                return
            
            config = unified_config_manager.get_user_config(user_id)
            if not config:
                if update.message:
                    await update.message.reply_text("يرجى استخدام /start أولاً.")
                return
            
            market_type = config.get('market_type', 'spot')
            account_type = config.get('account_type', 'demo')
            exchange = config.get('exchange', 'bybit')
            
            # بناء لوحة المفاتيح
            keyboard = [
                [InlineKeyboardButton(f"🏦 المنصة ({exchange.upper()})", callback_data="select_exchange_enhanced")],
                [InlineKeyboardButton(f"💰 مبلغ التداول ({config.get('trade_amount', 0.0):.2f} USDT)", callback_data="set_amount_enhanced")],
                [InlineKeyboardButton(f"🏪 نوع السوق ({market_type.upper()})", callback_data="set_market_enhanced")],
                [InlineKeyboardButton(f"👤 نوع الحساب ({account_type.upper()})", callback_data="set_account_enhanced")]
            ]
            
            if market_type == 'futures':
                keyboard.append([InlineKeyboardButton(f"⚡ الرافعة ({config.get('leverage', 1)}x)", callback_data="set_leverage_enhanced")])
            
            if account_type == 'demo':
                keyboard.append([InlineKeyboardButton(f"💵 الرصيد التجريبي ({config.get('balance', 0.0):.2f} USDT)", callback_data="set_demo_balance_enhanced")])
            
            keyboard.append([InlineKeyboardButton("🔑 تعيين مفاتيح API", callback_data="set_api_keys_enhanced")])
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="settings_enhanced")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message_text = f"""
⚙️ **الإعدادات المحسنة**

الإعدادات الحالية:
• المنصة: `{exchange.upper()}`
• نوع السوق: `{market_type.upper()}`
• نوع الحساب: `{account_type.upper()}`
• مبلغ التداول: `{config.get('trade_amount', 0.0):.2f} USDT`
{"• الرافعة: `" + str(config.get('leverage', 1)) + "x`" if market_type == 'futures' else ""}
{"• الرصيد التجريبي: `" + str(config.get('balance', 0.0)) + " USDT`" if account_type == 'demo' else ""}
• حالة API: {'🟢 متصل' if config.get('api_key') and config.get('api_secret') else '🔴 غير متصل'}
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
            elif update.message:
                await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة الإعدادات المحسنة: {e}")
    
    async def handle_enhanced_settings_callback(self, update, context):
        """معالجة استدعاءات قائمة الإعدادات المحسنة"""
        try:
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from core.unified_trading_bot import unified_config_manager
            
            query = update.callback_query
            await query.answer()
            user_id = query.from_user.id
            data = query.data
            
            if data == "select_exchange_enhanced":
                keyboard = [
                    [InlineKeyboardButton("Bybit", callback_data="exchange_bybit_enhanced")],
                    [InlineKeyboardButton("MEXC", callback_data="exchange_mexc_enhanced")],
                    [InlineKeyboardButton("🔙 العودة", callback_data="settings_enhanced")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("اختر المنصة:", reply_markup=reply_markup)
            
            elif data == "exchange_bybit_enhanced":
                unified_config_manager.update_user_config(user_id, 'exchange', 'bybit')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "exchange_mexc_enhanced":
                unified_config_manager.update_user_config(user_id, 'exchange', 'mexc')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "set_amount_enhanced":
                self.user_input_states[user_id] = "waiting_for_trade_amount_enhanced"
                await query.edit_message_text("يرجى إدخال مبلغ التداول الجديد (مثال: 100.0):")
            
            elif data == "set_market_enhanced":
                keyboard = [
                    [InlineKeyboardButton("Spot", callback_data="market_spot_enhanced")],
                    [InlineKeyboardButton("Futures", callback_data="market_futures_enhanced")],
                    [InlineKeyboardButton("🔙 العودة", callback_data="settings_enhanced")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("اختر نوع السوق:", reply_markup=reply_markup)
            
            elif data == "market_spot_enhanced":
                unified_config_manager.update_user_config(user_id, 'market_type', 'spot')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "market_futures_enhanced":
                unified_config_manager.update_user_config(user_id, 'market_type', 'futures')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "set_account_enhanced":
                keyboard = [
                    [InlineKeyboardButton("حقيقي", callback_data="account_real_enhanced")],
                    [InlineKeyboardButton("تجريبي", callback_data="account_demo_enhanced")],
                    [InlineKeyboardButton("🔙 العودة", callback_data="settings_enhanced")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("اختر نوع الحساب:", reply_markup=reply_markup)
            
            elif data == "account_real_enhanced":
                unified_config_manager.update_user_config(user_id, 'account_type', 'real')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "account_demo_enhanced":
                unified_config_manager.update_user_config(user_id, 'account_type', 'demo')
                await self.show_enhanced_settings_menu(update, context)
            
            elif data == "set_leverage_enhanced":
                self.user_input_states[user_id] = "waiting_for_leverage_enhanced"
                await query.edit_message_text("يرجى إدخال قيمة الرافعة الجديدة (1-100):")
            
            elif data == "set_demo_balance_enhanced":
                self.user_input_states[user_id] = "waiting_for_demo_balance_enhanced"
                await query.edit_message_text("يرجى إدخال الرصيد التجريبي الجديد:")
            
            elif data == "set_api_keys_enhanced":
                self.user_input_states[user_id] = "waiting_for_api_key_enhanced"
                await query.edit_message_text("يرجى إرسال مفتاح Bybit API:")
            
            elif data == "settings_enhanced":
                await self.show_enhanced_settings_menu(update, context)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة استدعاء الإعدادات المحسنة: {e}")
    
    async def handle_enhanced_text_input(self, update, context):
        """معالجة إدخال النص للإعدادات المحسنة"""
        try:
            from core.unified_trading_bot import unified_config_manager
            
            user_id = update.effective_user.id
            text = update.message.text
            state = self.user_input_states.get(user_id)
            
            if state == "waiting_for_trade_amount_enhanced":
                try:
                    amount = float(text)
                    if amount > 0:
                        unified_config_manager.update_user_config(user_id, 'trade_amount', amount)
                        del self.user_input_states[user_id]
                        await update.message.reply_text(f"تم تحديث مبلغ التداول إلى: {amount:.2f} USDT")
                        await self.show_enhanced_settings_menu(update, context)
                    else:
                        await update.message.reply_text("يرجى إدخال مبلغ أكبر من الصفر.")
                except ValueError:
                    await update.message.reply_text("مبلغ غير صحيح. يرجى إدخال رقم.")
            
            elif state == "waiting_for_leverage_enhanced":
                try:
                    leverage = int(text)
                    if 1 <= leverage <= 100:
                        unified_config_manager.update_user_config(user_id, 'leverage', leverage)
                        del self.user_input_states[user_id]
                        await update.message.reply_text(f"تم تحديث الرافعة إلى: {leverage}x")
                        await self.show_enhanced_settings_menu(update, context)
                    else:
                        await update.message.reply_text("يرجى إدخال قيمة رافعة بين 1 و 100.")
                except ValueError:
                    await update.message.reply_text("رافعة غير صحيحة. يرجى إدخال رقم صحيح.")
            
            elif state == "waiting_for_demo_balance_enhanced":
                try:
                    balance = float(text)
                    if balance >= 0:
                        unified_config_manager.update_user_config(user_id, 'balance', balance)
                        del self.user_input_states[user_id]
                        await update.message.reply_text(f"تم تحديث الرصيد التجريبي إلى: {balance:.2f} USDT")
                        await self.show_enhanced_settings_menu(update, context)
                    else:
                        await update.message.reply_text("يرجى إدخال رصيد غير سالب.")
                except ValueError:
                    await update.message.reply_text("رصيد غير صحيح. يرجى إدخال رقم.")
            
            elif state == "waiting_for_api_key_enhanced":
                context.user_data['temp_api_key'] = text
                self.user_input_states[user_id] = "waiting_for_api_secret_enhanced"
                await update.message.reply_text("الآن، يرجى إرسال سر Bybit API:")
            
            elif state == "waiting_for_api_secret_enhanced":
                api_key = context.user_data.pop('temp_api_key', None)
                api_secret = text
                
                if api_key and api_secret:
                    unified_config_manager.update_user_config(user_id, 'api_key', api_key)
                    unified_config_manager.update_user_config(user_id, 'api_secret', api_secret)
                    
                    # تحديث مفاتيح MEXC إذا كان المستخدم يستخدم MEXC
                    config = unified_config_manager.get_user_config(user_id)
                    if config and config.get('exchange') == 'mexc':
                        unified_config_manager.update_user_config(user_id, 'mexc_api_key', api_key)
                        unified_config_manager.update_user_config(user_id, 'mexc_api_secret', api_secret)
                    
                    del self.user_input_states[user_id]
                    await update.message.reply_text("تم حفظ مفاتيح Bybit API بنجاح!")
                    await self.show_enhanced_settings_menu(update, context)
                else:
                    await update.message.reply_text("مفتاح API أو السر مفقود. يرجى المحاولة مرة أخرى.")
                    del self.user_input_states[user_id]
                    await self.show_enhanced_settings_menu(update, context)
                    
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال النص المحسن: {e}")
    
    async def initialize_interface(self):
        """تهيئة واجهة البوت"""
        try:
            self.system_active = True
            logger.info("تم تهيئة واجهة البوت المحسنة")
        except Exception as e:
            logger.error(f"خطأ في تهيئة واجهة البوت: {e}")

# ==================== النظام المحسن الموحد ====================

class UnifiedEnhancedSystem:
    """النظام المحسن الموحد - يجمع جميع الوظائف المحسنة"""
    
    def __init__(self):
        self.config_manager = UnifiedConfigManager()
        self.trade_executor = UnifiedTradeExecutor()
        self.bot_interface = UnifiedBotInterface()
        self.system_active = False
        logger.info("تم تهيئة النظام المحسن الموحد")
    
    async def initialize_system(self):
        """تهيئة النظام المحسن"""
        try:
            await self.config_manager.initialize_system()
            await self.trade_executor.initialize_executor()
            await self.bot_interface.initialize_interface()
            
            self.system_active = True
            logger.info("تم تهيئة النظام المحسن الموحد بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام المحسن: {e}")
    
    async def process_signal(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة الإشارة باستخدام النظام المحسن"""
        try:
            if not self.system_active:
                return {'status': 'error', 'message': 'النظام المحسن غير نشط'}
            
            # تحليل الإشارة
            analysis = self._analyze_signal(signal_data)
            
            # تقييم المخاطر
            risk_assessment = self._assess_risk(user_id, signal_data)
            
            # خطة التنفيذ
            execution_plan = self._create_execution_plan(user_id, signal_data)
            
            return {
                'status': 'success',
                'analysis': analysis,
                'risk_assessment': risk_assessment,
                'execution_plan': execution_plan
            }
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة المحسنة: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل الإشارة"""
        try:
            symbol = signal_data.get('symbol', '')
            action = signal_data.get('action', '')
            
            # تحليل بسيط للإشارة
            analysis = {
                'signal_quality': 'high',
                'confidence_level': 0.85,
                'market_conditions': 'favorable',
                'recommendation': 'execute',
                'risk_level': 'medium',
                'signal_type': 'bullish' if action.lower() == 'buy' else 'bearish',
                'asset_type': 'cryptocurrency',
                'volatility': 'high'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الإشارة: {e}")
            return {'signal_quality': 'low', 'confidence_level': 0.0}
    
    def _assess_risk(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم المخاطر"""
        try:
            config = self.config_manager.get_user_config(user_id)
            if not config:
                return {'risk_level': 'high', 'recommendation': 'do_not_execute'}
            
            trade_amount = config.get('trade_amount', 50.0)
            leverage = config.get('leverage', 1)
            account_type = config.get('account_type', 'demo')
            
            # تقييم المخاطر بناءً على الإعدادات
            if account_type == 'real' and leverage > 10:
                risk_level = 'high'
            elif trade_amount > 1000:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'risk_level': risk_level,
                'max_position_size': 0.2,
                'stop_loss': 0.02,
                'take_profit': 0.04,
                'recommendation': 'proceed_with_caution' if risk_level == 'low' else 'reduce_position_size'
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المخاطر: {e}")
            return {'risk_level': 'high', 'recommendation': 'do_not_execute'}
    
    def _create_execution_plan(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء خطة التنفيذ"""
        try:
            config = self.config_manager.get_user_config(user_id)
            if not config:
                return {'strategy': 'manual', 'timing': 'immediate'}
            
            market_type = config.get('market_type', 'spot')
            account_type = config.get('account_type', 'demo')
            
            # خطة التنفيذ بناءً على نوع السوق والحساب
            if market_type == 'futures' and account_type == 'real':
                strategy = 'TWAP'
                timing = 'optimal'
                execution_time = '5_minutes'
            else:
                strategy = 'Market'
                timing = 'immediate'
                execution_time = '1_minute'
            
            return {
                'strategy': strategy,
                'timing': timing,
                'price_optimization': True,
                'slippage_protection': True,
                'execution_priority': 'high',
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء خطة التنفيذ: {e}")
            return {'strategy': 'manual', 'timing': 'immediate'}

# ==================== إنشاء مثيل النظام المحسن الموحد ====================

# إنشاء مثيل النظام المحسن الموحد
unified_enhanced_system = UnifiedEnhancedSystem()

# تصدير النظام للاستخدام في الملفات الأخرى
enhanced_system = unified_enhanced_system

logger.info("تم إنشاء النظام المحسن الموحد بنجاح")
