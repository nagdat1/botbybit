#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث النظام الرئيسي - دمج النظام المحسن مع النظام الحالي
يحافظ على آلية التوقيع وحساب السعر مع دعم تعديل المتغيرات
"""

import logging
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from integrated_trading_system import integrated_trading_system
from flexible_config_manager import flexible_config_manager
from enhanced_trade_executor import enhanced_trade_executor
from database import db_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class EnhancedTradingBot:
    """البوت المحسن مع دعم تعديل المتغيرات"""
    
    def __init__(self):
        self.application = None
        self.system_active = True
        
    def setup_enhanced_handlers(self, application: Application):
        """إعداد معالجات البوت المحسن"""
        try:
            # إضافة معالجات الواجهة المحسنة
            application.add_handler(CallbackQueryHandler(
                integrated_trading_system.handle_enhanced_callback,
                pattern="^(enhanced_settings|api_settings|trade_amount_settings|leverage_settings|market_type_settings|account_type_settings|exchange_settings|settings_summary|reset_settings|update_bybit_api|update_mexc_api|test_api_connection|amount_|custom_amount|leverage_|custom_leverage|market_|account_|exchange_)"
            ))
            
            # إضافة معالجات الرسائل المحسنة
            application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                integrated_trading_system.handle_enhanced_message
            ))
            
            # إضافة أوامر محسنة
            application.add_handler(CommandHandler("enhanced_settings", self.show_enhanced_settings_command))
            application.add_handler(CommandHandler("config_summary", self.show_config_summary_command))
            application.add_handler(CommandHandler("test_trade", self.test_trade_command))
            
            logger.info("تم إعداد معالجات البوت المحسن بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد معالجات البوت المحسن: {e}")
    
    async def show_enhanced_settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإعدادات المحسنة عبر الأمر"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            
            # التحقق من وجود المستخدم
            user_data = user_manager.get_user(user_id)
            if not user_data:
                await update.message.reply_text("❌ يرجى استخدام /start أولاً")
                return
            
            # عرض قائمة الإعدادات المحسنة
            await integrated_trading_system.handle_enhanced_callback(update, context)
            
        except Exception as e:
            logger.error(f"خطأ في عرض الإعدادات المحسنة: {e}")
            await update.message.reply_text(f"خطأ: {e}")
    
    async def show_config_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض ملخص الإعدادات عبر الأمر"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            
            # الحصول على ملخص الإعدادات
            summary = flexible_config_manager.get_trading_summary(user_id)
            
            # إضافة معلومات إضافية
            execution_summary = enhanced_trade_executor.get_execution_summary(user_id)
            
            full_summary = f"{summary}\n\n**📊 إحصائيات التنفيذ:**\n"
            full_summary += f"• إجمالي الصفقات: {execution_summary['total_trades']}\n"
            full_summary += f"• الصفقات المفتوحة: {execution_summary['open_trades']}\n"
            full_summary += f"• الصفقات المغلقة: {execution_summary['closed_trades']}\n"
            full_summary += f"• معدل النجاح: {execution_summary['success_rate']:.1f}%\n"
            
            await update.message.reply_text(full_summary, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في عرض ملخص الإعدادات: {e}")
            await update.message.reply_text(f"خطأ: {e}")
    
    async def test_trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختبار تنفيذ صفقة عبر الأمر"""
        try:
            if update.effective_user is None:
                return
            
            user_id = update.effective_user.id
            
            # التحقق من وجود المستخدم
            user_data = user_manager.get_user(user_id)
            if not user_data:
                await update.message.reply_text("❌ يرجى استخدام /start أولاً")
                return
            
            # إنشاء إشارة اختبار
            test_signal = {
                'symbol': 'BTCUSDT',
                'side': 'buy',
                'signal_id': f'test_{int(time.time())}',
                'timestamp': time.time()
            }
            
            # تنفيذ الصفقة الاختبارية
            result = await integrated_trading_system.execute_enhanced_signal(user_id, test_signal)
            
            # عرض النتيجة
            if result['success']:
                message = f"✅ تم تنفيذ الصفقة الاختبارية بنجاح!\n\n"
                message += f"**الرمز:** {result['symbol']}\n"
                message += f"**الجانب:** {result['side']}\n"
                message += f"**الكمية:** {result['quantity']:.6f}\n"
                message += f"**السعر:** {result['price']:.2f}\n"
                message += f"**المبلغ:** {result['trade_amount']} USDT\n"
                message += f"**الرافعة:** {result['leverage']}x\n"
                message += f"**نوع الحساب:** {result['account_type']}"
                        else:
                message = f"❌ فشل في تنفيذ الصفقة الاختبارية\n\n"
                message += f"**السبب:** {result['message']}\n"
                message += f"**نوع الخطأ:** {result.get('error_type', 'غير محدد')}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في اختبار الصفقة: {e}")
            await update.message.reply_text(f"خطأ: {e}")
    
    def integrate_with_existing_system(self, existing_bot):
        """دمج النظام المحسن مع النظام الحالي"""
        try:
            # الحفاظ على النظام الحالي
            self.existing_bot = existing_bot
            
            # إضافة معالجات محسنة للنظام الحالي
            if hasattr(existing_bot, 'application') and existing_bot.application:
                self.setup_enhanced_handlers(existing_bot.application)
            
            # تحديث معالجات الإشارات الموجودة
            self._enhance_existing_signal_handlers()
            
            logger.info("تم دمج النظام المحسن مع النظام الحالي بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في دمج النظام المحسن: {e}")
    
    def _enhance_existing_signal_handlers(self):
        """تحسين معالجات الإشارات الموجودة"""
        try:
            # استبدال معالج الإشارات الحالي بالمعالج المحسن
            if hasattr(self, 'existing_bot') and self.existing_bot:
                # حفظ المعالج الأصلي
                original_process_signal = getattr(self.existing_bot, 'process_signal', None)
                
                # إنشاء معالج محسن
                async def enhanced_process_signal(signal_data):
                    try:
                        # استخدام النظام المحسن لتنفيذ الإشارة
                        user_id = getattr(self.existing_bot, 'user_id', None)
                        if user_id:
                            result = await integrated_trading_system.execute_enhanced_signal(user_id, signal_data)
                            return result
                    else:
                            # استخدام المعالج الأصلي كاحتياطي
                            if original_process_signal:
                                return await original_process_signal(signal_data)
                            return {'success': False, 'message': 'معرف المستخدم غير متوفر'}
        except Exception as e:
                        logger.error(f"خطأ في المعالج المحسن للإشارات: {e}")
                        return {'success': False, 'message': f'خطأ: {e}'}
                
                # استبدال المعالج
                self.existing_bot.process_signal = enhanced_process_signal
                
                logger.info("تم تحسين معالج الإشارات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين معالجات الإشارات: {e}")
    
    def get_enhanced_main_menu(self, user_id: int) -> ReplyKeyboardMarkup:
        """الحصول على القائمة الرئيسية المحسنة"""
        try:
            keyboard = [
                [KeyboardButton("⚙️ الإعدادات المحسنة"), KeyboardButton("📊 ملخص الإعدادات")],
                [KeyboardButton("🧪 اختبار الصفقة"), KeyboardButton("📈 الصفقات المفتوحة")],
                [KeyboardButton("💰 المحفظة"), KeyboardButton("📊 الإحصائيات")],
                [KeyboardButton("🔧 الإعدادات"), KeyboardButton("❓ المساعدة")]
            ]
            
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء القائمة الرئيسية المحسنة: {e}")
            return ReplyKeyboardMarkup([["⚙️ الإعدادات"]], resize_keyboard=True)
    
    async def handle_enhanced_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة القائمة الرئيسية المحسنة"""
        try:
            if update.message is None:
                return
            
            text = update.message.text
            
            if text == "⚙️ الإعدادات المحسنة":
                await integrated_trading_system.handle_enhanced_callback(update, context)
            
            elif text == "📊 ملخص الإعدادات":
                await self.show_config_summary_command(update, context)
            
            elif text == "🧪 اختبار الصفقة":
                await self.test_trade_command(update, context)
            
            # باقي المعالجات يمكن إضافتها هنا
            
        except Exception as e:
            logger.error(f"خطأ في معالجة القائمة الرئيسية المحسنة: {e}")
    
    def get_system_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة تكامل النظام"""
        try:
            return {
                'enhanced_system_active': self.system_active,
                'integration_complete': True,
                'config_manager_status': 'active',
                'bot_interface_status': 'active',
                'trade_executor_status': 'active',
                'existing_system_preserved': True,
                'signature_logic_preserved': True,
                'price_calculation_preserved': True
            }
        except Exception as e:
            logger.error(f"خطأ في جلب حالة التكامل: {e}")
            return {
                'enhanced_system_active': False,
                'error': str(e)
            }

# إنشاء مثيل عام للبوت المحسن
enhanced_trading_bot = EnhancedTradingBot()

# دالة مساعدة لدمج النظام مع النظام الحالي
def integrate_enhanced_system(existing_bot):
    """دمج النظام المحسن مع النظام الحالي"""
    try:
        enhanced_trading_bot.integrate_with_existing_system(existing_bot)
        logger.info("تم دمج النظام المحسن بنجاح")
        return True
        except Exception as e:
        logger.error(f"خطأ في دمج النظام المحسن: {e}")
        return False

# دالة مساعدة لإعداد النظام المحسن
def setup_enhanced_system(application: Application):
    """إعداد النظام المحسن"""
    try:
        enhanced_trading_bot.setup_enhanced_handlers(application)
        logger.info("تم إعداد النظام المحسن بنجاح")
        return True
        except Exception as e:
        logger.error(f"خطأ في إعداد النظام المحسن: {e}")
        return False