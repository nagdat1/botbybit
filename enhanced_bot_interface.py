#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة البوت المحسنة - دعم تعديل المتغيرات مع الحفاظ على آلية التوقيع
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from flexible_config_manager import flexible_config_manager
from database import db_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class EnhancedBotInterface:
    """واجهة البوت المحسنة لدعم تعديل المتغيرات"""
    
    def __init__(self):
        self.user_input_states = {}  # حالات إدخال المستخدمين
        
    async def show_enhanced_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الإعدادات المحسنة"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء القائمة المحسنة
            keyboard = [
                [InlineKeyboardButton("🔑 إعدادات API", callback_data="api_settings")],
                [InlineKeyboardButton("💰 مبلغ التداول", callback_data="trade_amount_settings")],
                [InlineKeyboardButton("⚡ الرافعة المالية", callback_data="leverage_settings")],
                [InlineKeyboardButton("🏪 نوع السوق", callback_data="market_type_settings")],
                [InlineKeyboardButton("👤 نوع الحساب", callback_data="account_type_settings")],
                [InlineKeyboardButton("🏦 المنصة", callback_data="exchange_settings")],
                [InlineKeyboardButton("📊 ملخص الإعدادات", callback_data="settings_summary")],
                [InlineKeyboardButton("🔄 إعادة تعيين الإعدادات", callback_data="reset_settings")],
                [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # رسالة الترحيب مع الإعدادات الحالية
            message = f"""
**⚙️ الإعدادات المحسنة**

**الإعدادات الحالية:**
🏦 المنصة: {config['exchange'].upper()}
🏪 نوع السوق: {config['market_type'].upper()}
👤 نوع الحساب: {config['account_type'].upper()}
💰 مبلغ التداول: {config['trade_amount']} USDT
⚡ الرافعة المالية: {config['leverage']}x
🔗 حالة API: {'🟢 متصل' if config['api_connected'] else '🔴 غير متصل'}

اختر الإعداد الذي تريد تعديله:
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            elif update.message:
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة الإعدادات المحسنة: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_api_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات API"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة إعدادات API
            keyboard = [
                [InlineKeyboardButton("🔑 تحديث مفاتيح Bybit", callback_data="update_bybit_api")],
                [InlineKeyboardButton("🔑 تحديث مفاتيح MEXC", callback_data="update_mexc_api")],
                [InlineKeyboardButton("🧪 اختبار الاتصال", callback_data="test_api_connection")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # رسالة إعدادات API
            api_status = "🟢 متصل" if config['api_connected'] else "🔴 غير متصل"
            message = f"""
**🔑 إعدادات API**

**المنصة الحالية:** {config['exchange'].upper()}
**حالة الاتصال:** {api_status}

**مفاتيح Bybit:**
🔑 API Key: {'✅ محفوظ' if config['bybit_api_key'] else '❌ غير محفوظ'}
🔐 API Secret: {'✅ محفوظ' if config['bybit_api_secret'] else '❌ غير محفوظ'}

**مفاتيح MEXC:**
🔑 API Key: {'✅ محفوظ' if config['mexc_api_key'] else '❌ غير محفوظ'}
🔐 API Secret: {'✅ محفوظ' if config['mexc_api_secret'] else '❌ غير محفوظ'}

اختر الإجراء المطلوب:
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات API: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_trade_amount_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات مبلغ التداول"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة مبالغ سريعة
            keyboard = [
                [InlineKeyboardButton("$10", callback_data="amount_10"),
                 InlineKeyboardButton("$25", callback_data="amount_25"),
                 InlineKeyboardButton("$50", callback_data="amount_50")],
                [InlineKeyboardButton("$100", callback_data="amount_100"),
                 InlineKeyboardButton("$250", callback_data="amount_250"),
                 InlineKeyboardButton("$500", callback_data="amount_500")],
                [InlineKeyboardButton("✏️ إدخال مخصص", callback_data="custom_amount")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
**💰 إعدادات مبلغ التداول**

**المبلغ الحالي:** {config['trade_amount']} USDT

**اختر مبلغاً سريعاً أو أدخل مبلغاً مخصصاً:**

**ملاحظات مهمة:**
• الحد الأدنى: $1
• الحد الأقصى: $10,000
• سيتم حساب الكمية تلقائياً حسب السعر الحالي
• للفيوتشر: سيتم ضرب المبلغ في الرافعة المالية
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات مبلغ التداول: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_leverage_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات الرافعة المالية"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة رافعات سريعة
            keyboard = [
                [InlineKeyboardButton("1x", callback_data="leverage_1"),
                 InlineKeyboardButton("2x", callback_data="leverage_2"),
                 InlineKeyboardButton("5x", callback_data="leverage_5")],
                [InlineKeyboardButton("10x", callback_data="leverage_10"),
                 InlineKeyboardButton("20x", callback_data="leverage_20"),
                 InlineKeyboardButton("50x", callback_data="leverage_50")],
                [InlineKeyboardButton("✏️ إدخال مخصص", callback_data="custom_leverage")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
**⚡ إعدادات الرافعة المالية**

**الرافعة الحالية:** {config['leverage']}x

**اختر رافعة سريعة أو أدخل رافعة مخصصة:**

**ملاحظات مهمة:**
• الحد الأدنى: 1x
• الحد الأقصى: 100x
• الرافعة العالية = مخاطر عالية
• الرافعة المنخفضة = مخاطر منخفضة
• يُنصح بـ 2-5x للمبتدئين
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات الرافعة المالية: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_market_type_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات نوع السوق"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة أنواع السوق
            keyboard = [
                [InlineKeyboardButton("🏪 Spot (فوري)", callback_data="market_spot")],
                [InlineKeyboardButton("⚡ Futures (آجل)", callback_data="market_futures")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
**🏪 إعدادات نوع السوق**

**النوع الحالي:** {config['market_type'].upper()}

**اختر نوع السوق:**

**🏪 Spot (فوري):**
• تداول فوري للعملات
• لا توجد رافعة مالية
• مخاطر منخفضة
• مناسب للمبتدئين

**⚡ Futures (آجل):**
• تداول بالرافعة المالية
• مخاطر عالية
• أرباح وخسائر مضاعفة
• مناسب للمتقدمين
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات نوع السوق: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_account_type_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات نوع الحساب"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة أنواع الحساب
            keyboard = [
                [InlineKeyboardButton("👤 حساب حقيقي", callback_data="account_real")],
                [InlineKeyboardButton("🎮 حساب تجريبي", callback_data="account_demo")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
**👤 إعدادات نوع الحساب**

**النوع الحالي:** {config['account_type'].upper()}

**اختر نوع الحساب:**

**👤 حساب حقيقي:**
• تداول بأموال حقيقية
• يتطلب مفاتيح API صحيحة
• أرباح وخسائر حقيقية
• مناسب للمتداولين ذوي الخبرة

**🎮 حساب تجريبي:**
• تداول بأموال وهمية
• لا يتطلب مفاتيح API
• مناسب للتعلم والتدريب
• لا توجد مخاطر مالية
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات نوع الحساب: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_exchange_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إعدادات المنصة"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            config = flexible_config_manager.get_user_config(user_id)
            
            # بناء قائمة المنصات
            keyboard = [
                [InlineKeyboardButton("🏦 Bybit", callback_data="exchange_bybit")],
                [InlineKeyboardButton("🏦 MEXC", callback_data="exchange_mexc")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
**🏦 إعدادات المنصة**

**المنصة الحالية:** {config['exchange'].upper()}

**اختر المنصة:**

**🏦 Bybit:**
• منصة تداول عالمية
• دعم Spot و Futures
• رسوم منخفضة
• واجهة سهلة الاستخدام

**🏦 MEXC:**
• منصة تداول متنوعة
• دعم Spot فقط
• رسوم تنافسية
• دعم عملات متنوعة
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض إعدادات المنصة: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def show_settings_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض ملخص الإعدادات"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            summary = flexible_config_manager.get_trading_summary(user_id)
            
            keyboard = [
                [InlineKeyboardButton("🔄 تحديث", callback_data="settings_summary")],
                [InlineKeyboardButton("🔙 العودة", callback_data="enhanced_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(summary, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطأ في عرض ملخص الإعدادات: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"خطأ: {e}")
    
    async def handle_custom_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الإدخال المخصص للمستخدمين"""
        try:
            if update.effective_user is None or update.message is None:
                return
            
            user_id = update.effective_user.id
            text = update.message.text.strip()
            
            # التحقق من حالة الإدخال
            if user_id not in self.user_input_states:
                return
            
            state = self.user_input_states[user_id]
            
            if state == "waiting_for_custom_amount":
                await self._handle_custom_amount_input(update, context, text)
            elif state == "waiting_for_custom_leverage":
                await self._handle_custom_leverage_input(update, context, text)
            elif state == "waiting_for_bybit_api_key":
                await self._handle_bybit_api_key_input(update, context, text)
            elif state == "waiting_for_bybit_api_secret":
                await self._handle_bybit_api_secret_input(update, context, text)
            elif state == "waiting_for_mexc_api_key":
                await self._handle_mexc_api_key_input(update, context, text)
            elif state == "waiting_for_mexc_api_secret":
                await self._handle_mexc_api_secret_input(update, context, text)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإدخال المخصص: {e}")
            if update.message:
                await update.message.reply_text(f"خطأ: {e}")
    
    async def _handle_custom_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال المبلغ المخصص"""
        try:
            user_id = update.effective_user.id
            
            try:
                amount = float(text)
                if 1 <= amount <= 10000:
                    # تحديث الإعدادات
                    success, message = flexible_config_manager.update_user_config(
                        user_id, {'trade_amount': amount}
                    )
                    
                    if success:
                        await update.message.reply_text(f"✅ تم تحديث مبلغ التداول إلى: {amount} USDT")
                        await self.show_trade_amount_settings(update, context)
                    else:
                        await update.message.reply_text(f"❌ {message}")
                else:
                    await update.message.reply_text("❌ المبلغ يجب أن يكون بين $1 و $10,000")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
            
            # إزالة حالة الإدخال
            if user_id in self.user_input_states:
                del self.user_input_states[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال المبلغ المخصص: {e}")
    
    async def _handle_custom_leverage_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال الرافعة المخصصة"""
        try:
            user_id = update.effective_user.id
            
            try:
                leverage = int(text)
                if 1 <= leverage <= 100:
                    # تحديث الإعدادات
                    success, message = flexible_config_manager.update_user_config(
                        user_id, {'leverage': leverage}
                    )
                    
                    if success:
                        await update.message.reply_text(f"✅ تم تحديث الرافعة المالية إلى: {leverage}x")
                        await self.show_leverage_settings(update, context)
                    else:
                        await update.message.reply_text(f"❌ {message}")
                else:
                    await update.message.reply_text("❌ الرافعة يجب أن تكون بين 1 و 100")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
            
            # إزالة حالة الإدخال
            if user_id in self.user_input_states:
                del self.user_input_states[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال الرافعة المخصصة: {e}")
    
    async def _handle_bybit_api_key_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال مفتاح Bybit API"""
        try:
            user_id = update.effective_user.id
            
            if len(text) >= 10:  # التحقق من طول المفتاح
                # حفظ المفتاح مؤقتاً
                if 'temp_api_data' not in context.user_data:
                    context.user_data['temp_api_data'] = {}
                context.user_data['temp_api_data']['bybit_api_key'] = text
                
                # طلب إدخال الـ secret
                self.user_input_states[user_id] = "waiting_for_bybit_api_secret"
                await update.message.reply_text("🔐 أدخل مفتاح Bybit API Secret:")
            else:
                await update.message.reply_text("❌ مفتاح API قصير جداً، يرجى إدخال مفتاح صحيح")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال مفتاح Bybit API: {e}")
    
    async def _handle_bybit_api_secret_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال سر Bybit API"""
        try:
            user_id = update.effective_user.id
            
            if len(text) >= 10:  # التحقق من طول السر
                # حفظ البيانات
                temp_data = context.user_data.get('temp_api_data', {})
                api_key = temp_data.get('bybit_api_key', '')
                api_secret = text
                
                # تحديث الإعدادات
                success, message = flexible_config_manager.update_user_config(
                    user_id, {
                        'bybit_api_key': api_key,
                        'bybit_api_secret': api_secret,
                        'exchange': 'bybit'
                    }
                )
                
                if success:
                    await update.message.reply_text("✅ تم حفظ مفاتيح Bybit API بنجاح")
                    await self.show_api_settings(update, context)
                else:
                    await update.message.reply_text(f"❌ {message}")
                
                # تنظيف البيانات المؤقتة
                if 'temp_api_data' in context.user_data:
                    del context.user_data['temp_api_data']
            else:
                await update.message.reply_text("❌ سر API قصير جداً، يرجى إدخال سر صحيح")
            
            # إزالة حالة الإدخال
            if user_id in self.user_input_states:
                del self.user_input_states[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال سر Bybit API: {e}")
    
    async def _handle_mexc_api_key_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال مفتاح MEXC API"""
        try:
            user_id = update.effective_user.id
            
            if len(text) >= 10:  # التحقق من طول المفتاح
                # حفظ المفتاح مؤقتاً
                if 'temp_api_data' not in context.user_data:
                    context.user_data['temp_api_data'] = {}
                context.user_data['temp_api_data']['mexc_api_key'] = text
                
                # طلب إدخال الـ secret
                self.user_input_states[user_id] = "waiting_for_mexc_api_secret"
                await update.message.reply_text("🔐 أدخل مفتاح MEXC API Secret:")
            else:
                await update.message.reply_text("❌ مفتاح API قصير جداً، يرجى إدخال مفتاح صحيح")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال مفتاح MEXC API: {e}")
    
    async def _handle_mexc_api_secret_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال سر MEXC API"""
        try:
            user_id = update.effective_user.id
            
            if len(text) >= 10:  # التحقق من طول السر
                # حفظ البيانات
                temp_data = context.user_data.get('temp_api_data', {})
                api_key = temp_data.get('mexc_api_key', '')
                api_secret = text
                
                # تحديث الإعدادات
                success, message = flexible_config_manager.update_user_config(
                    user_id, {
                        'mexc_api_key': api_key,
                        'mexc_api_secret': api_secret,
                        'exchange': 'mexc'
                    }
                )
                
                if success:
                    await update.message.reply_text("✅ تم حفظ مفاتيح MEXC API بنجاح")
                    await self.show_api_settings(update, context)
                else:
                    await update.message.reply_text(f"❌ {message}")
                
                # تنظيف البيانات المؤقتة
                if 'temp_api_data' in context.user_data:
                    del context.user_data['temp_api_data']
            else:
                await update.message.reply_text("❌ سر API قصير جداً، يرجى إدخال سر صحيح")
            
            # إزالة حالة الإدخال
            if user_id in self.user_input_states:
                del self.user_input_states[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في معالجة إدخال سر MEXC API: {e}")

# إنشاء مثيل عام للواجهة المحسنة
enhanced_bot_interface = EnhancedBotInterface()
