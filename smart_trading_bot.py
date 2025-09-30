#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت التداول الذكي على Bybit
نظام متكامل يدعم بيئات منفصلة لكل مستخدم مع حماية شاملة
"""

import logging
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters
)

# استيراد الوحدات المطورة
from database import db_manager
from user_manager import user_manager
from api_manager import api_manager
from order_manager import order_manager
from ui_manager import ui_manager
from commands import command_handler
from bot_controller import bot_controller
from security_manager import security_manager

# استيراد الإعدادات
from config import TELEGRAM_TOKEN, ADMIN_USER_ID, LOGGING_SETTINGS

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    handlers=[
        logging.FileHandler(LOGGING_SETTINGS['log_file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartTradingBot:
    """البوت الرئيسي للتداول الذكي"""
    
    def __init__(self):
        self.application = None
        self.is_running = False
        self.start_time = None
        
        # إحصائيات البوت
        self.stats = {
            'total_users': 0,
            'active_users': 0,
            'total_orders': 0,
            'messages_processed': 0,
            'uptime': 0
        }
    
    async def initialize(self):
        """تهيئة البوت"""
        try:
            logger.info("بدء تهيئة البوت الذكي...")
            
            # تهيئة قاعدة البيانات
            db_manager.init_database()
            
            # بدء مراقبة الأمان
            security_manager.start_security_monitoring()
            
            # بدء مراقبة النظام
            bot_controller.start_monitoring()
            
            # بدء مراقبة الأسعار
            order_manager.start_price_monitoring()
            
            logger.info("تم تهيئة البوت بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة البوت: {e}")
            raise
    
    async def start(self):
        """بدء تشغيل البوت"""
        try:
            await self.initialize()
            
            # إنشاء تطبيق Telegram
            self.application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # إضافة المعالجات
            self._setup_handlers()
            
            # بدء التطبيق
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("بدء تشغيل البوت الذكي...")
            await self.application.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت: {e}")
            raise
    
    def _setup_handlers(self):
        """إعداد معالجات الأحداث"""
        try:
            # معالجات الأوامر
            self.application.add_handler(CommandHandler("start", self._handle_start))
            self.application.add_handler(CommandHandler("balance", self._handle_balance))
            self.application.add_handler(CommandHandler("buy", self._handle_buy))
            self.application.add_handler(CommandHandler("sell", self._handle_sell))
            self.application.add_handler(CommandHandler("help", self._handle_help))
            
            # معالج الرسائل النصية
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
            
            # معالج الأزرار
            self.application.add_handler(CallbackQueryHandler(self._handle_callback))
            
            # معالج الأخطاء
            self.application.add_error_handler(self._handle_error)
            
            logger.info("تم إعداد معالجات الأحداث")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد المعالجات: {e}")
            raise
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /start"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "start")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # معالجة الأمر
            await command_handler.handle_start(update, context)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة /start: {e}")
            await update.message.reply_text("❌ حدث خطأ في بدء البوت")
    
    async def _handle_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /balance"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "balance")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # التحقق من صلاحية الوصول
            if not security_manager.validate_user_access(user_id, "user_data"):
                await update.message.reply_text("❌ غير مصرح لك بالوصول لهذه المعلومات")
                return
            
            # معالجة الأمر
            await command_handler.handle_balance(update, context)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة /balance: {e}")
            await update.message.reply_text("❌ خطأ في الحصول على معلومات الرصيد")
    
    async def _handle_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /buy"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "buy")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # التحقق من صلاحية التداول
            if not security_manager.validate_user_access(user_id, "trading"):
                await update.message.reply_text("❌ غير مصرح لك بالتداول")
                return
            
            # كشف النشاط المشبوه
            if context.args:
                symbol = context.args[0].upper()
                quantity = float(context.args[1]) if len(context.args) > 1 else 0
                
                suspicious = security_manager.detect_suspicious_activity(
                    user_id, "unusual_trading", {
                        'symbol': symbol,
                        'amount': quantity,
                        'action': 'buy'
                    }
                )
                
                if suspicious:
                    await update.message.reply_text("❌ تم رفض الطلب بسبب نشاط مشبوه")
                    return
            
            # معالجة الأمر
            await command_handler.handle_buy(update, context)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة /buy: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر الشراء")
    
    async def _handle_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /sell"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "sell")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # التحقق من صلاحية التداول
            if not security_manager.validate_user_access(user_id, "trading"):
                await update.message.reply_text("❌ غير مصرح لك بالتداول")
                return
            
            # كشف النشاط المشبوه
            if context.args:
                symbol = context.args[0].upper()
                quantity = float(context.args[1]) if len(context.args) > 1 else 0
                
                suspicious = security_manager.detect_suspicious_activity(
                    user_id, "unusual_trading", {
                        'symbol': symbol,
                        'amount': quantity,
                        'action': 'sell'
                    }
                )
                
                if suspicious:
                    await update.message.reply_text("❌ تم رفض الطلب بسبب نشاط مشبوه")
                    return
            
            # معالجة الأمر
            await command_handler.handle_sell(update, context)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة /sell: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر البيع")
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /help"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "help")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # معالجة الأمر
            await command_handler.handle_help(update, context)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة /help: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض المساعدة")
    
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        try:
            user_id = update.effective_user.id
            text = update.message.text
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "text_message")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # كشف النشاط المشبوه
            suspicious = security_manager.detect_suspicious_activity(
                user_id, "rapid_requests", {'message_length': len(text)}
            )
            
            if suspicious:
                await update.message.reply_text("❌ تم رفض الطلب بسبب نشاط مشبوه")
                return
            
            # معالجة النص حسب المحتوى
            await self._process_text_message(update, context, text)
            
            # تحديث الإحصائيات
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة النصية: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الرسالة")
    
    async def _process_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة الرسالة النصية حسب المحتوى"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من حالة إدخال المستخدم
            user_state = ui_manager.get_user_state(user_id)
            
            if user_state:
                await self._handle_user_input_state(update, context, text, user_state)
                return
            
            # معالجة الأزرار الرئيسية
            if text == "🔗 الربط":
                await self._handle_api_linking(update, context)
            elif text == "⚙️ الإعدادات":
                await self._handle_settings(update, context)
            elif text == "💰 الرصيد":
                await self._handle_balance_display(update, context)
            elif text == "📊 الصفقات المفتوحة":
                await self._handle_open_orders(update, context)
            elif text == "📈 تاريخ التداول":
                await self._handle_trade_history(update, context)
            elif text == "📊 الإحصائيات":
                await self._handle_statistics(update, context)
            elif text == "▶️ تشغيل البوت":
                await self._handle_start_bot(update, context)
            elif text == "⏹️ إيقاف البوت":
                await self._handle_stop_bot(update, context)
            else:
                await update.message.reply_text("❌ أمر غير مدعوم")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة النصية: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الرسالة")
    
    async def _handle_user_input_state(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     text: str, state: str):
        """معالجة حالة إدخال المستخدم"""
        try:
            user_id = update.effective_user.id
            
            if state == "waiting_for_api_keys":
                await self._process_api_keys_input(update, context, text)
            elif state == "waiting_for_trade_amount":
                await self._process_trade_amount_input(update, context, text)
            elif state == "waiting_for_leverage":
                await self._process_leverage_input(update, context, text)
            else:
                # مسح الحالة غير المعروفة
                ui_manager.clear_user_state(user_id)
                await update.message.reply_text("❌ تم إلغاء العملية")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة حالة إدخال المستخدم: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الإدخال")
    
    async def _process_api_keys_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال مفاتيح API"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من صيغة الإدخال
            parts = text.strip().split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ صيغة خاطئة!\n"
                    "أدخل مفاتيح API بالصيغة:\n"
                    "API_KEY API_SECRET"
                )
                return
            
            api_key, api_secret = parts
            
            # التحقق من صحة المفاتيح
            if api_manager.validate_api_keys(api_key, api_secret):
                # ربط المفاتيح
                if api_manager.add_user_api(user_id, api_key, api_secret):
                    # تحديث قاعدة البيانات
                    user_manager.set_user_api_keys(user_id, api_key, api_secret)
                    
                    # مسح الحالة
                    ui_manager.clear_user_state(user_id)
                    
                    await update.message.reply_text(
                        "✅ تم ربط مفاتيح API بنجاح!\n"
                        "يمكنك الآن استخدام البوت للتداول"
                    )
                else:
                    await update.message.reply_text("❌ فشل في ربط مفاتيح API")
            else:
                await update.message.reply_text("❌ مفاتيح API غير صحيحة")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة مفاتيح API: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة مفاتيح API")
    
    async def _process_trade_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال مبلغ التداول"""
        try:
            user_id = update.effective_user.id
            
            try:
                amount = float(text)
                if amount > 0:
                    # تحديث الإعدادات
                    settings = user_manager.get_user_settings(user_id)
                    settings['trade_amount'] = amount
                    user_manager.update_user_settings(user_id, settings)
                    
                    # مسح الحالة
                    ui_manager.clear_user_state(user_id)
                    
                    await update.message.reply_text(f"✅ تم تحديث مبلغ التداول إلى: {amount}")
                else:
                    await update.message.reply_text("❌ المبلغ يجب أن يكون أكبر من صفر")
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة مبلغ التداول: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة المبلغ")
    
    async def _process_leverage_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إدخال الرافعة المالية"""
        try:
            user_id = update.effective_user.id
            
            try:
                leverage = int(text)
                if 1 <= leverage <= 100:
                    # تحديث الإعدادات
                    settings = user_manager.get_user_settings(user_id)
                    settings['leverage'] = leverage
                    user_manager.update_user_settings(user_id, settings)
                    
                    # مسح الحالة
                    ui_manager.clear_user_state(user_id)
                    
                    await update.message.reply_text(f"✅ تم تحديث الرافعة المالية إلى: {leverage}x")
                else:
                    await update.message.reply_text("❌ الرافعة يجب أن تكون بين 1 و 100")
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الرافعة المالية: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الرافعة")
    
    async def _handle_api_linking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة ربط مفاتيح API"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "api_linking")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # تعيين حالة انتظار إدخال المفاتيح
            ui_manager.set_user_state(user_id, "waiting_for_api_keys")
            
            await update.message.reply_text(
                "🔗 ربط مفاتيح API\n\n"
                "أدخل مفاتيح API الخاصة بك بالصيغة التالية:\n"
                "API_KEY API_SECRET\n\n"
                "مثال:\n"
                "abc123def456 xyz789uvw012"
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة ربط API: {e}")
            await update.message.reply_text("❌ حدث خطأ في ربط مفاتيح API")
    
    async def _handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الإعدادات"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "settings")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # الحصول على لوحة مفاتيح الإعدادات
            keyboard = ui_manager.get_settings_keyboard(user_id)
            
            # الحصول على معلومات الإعدادات الحالية
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            
            settings_text = f"""
⚙️ إعدادات البوت

💰 مبلغ التداول: {settings.get('trade_amount', 100)} USDT
🏪 نوع السوق: {settings.get('market_type', 'spot').upper()}
⚡ الرافعة المالية: {settings.get('leverage', 1)}x
🔗 حالة API: {'مرتبط' if user_env.has_api_keys() else 'غير مرتبط'}
🤖 حالة البوت: {'نشط' if user_env.is_active else 'متوقف'}

اختر الإعداد الذي تريد تعديله:
            """
            
            await update.message.reply_text(settings_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإعدادات: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الإعدادات")
    
    async def _handle_balance_display(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الرصيد"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "balance_display")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # الحصول على معلومات الرصيد
            balance_info = user_manager.get_user_balance(user_id)
            trading_stats = user_manager.get_user_stats(user_id)
            
            balance_text = f"""
💰 معلومات الرصيد

📊 الرصيد الكلي: {balance_info['balance']:.2f} USDT
💳 الرصيد المتاح: {balance_info['available_balance']:.2f} USDT
🔒 الهامش المحجوز: {balance_info['margin_locked']:.2f} USDT
📈 إجمالي PnL: {balance_info['total_pnl']:.2f} USDT

📊 إحصائيات التداول:
• إجمالي الصفقات: {trading_stats['total_trades']}
• الصفقات الرابحة: {trading_stats['winning_trades']}
• الصفقات الخاسرة: {trading_stats['losing_trades']}
• معدل النجاح: {trading_stats['win_rate']:.1f}%
            """
            
            await update.message.reply_text(balance_text)
            
        except Exception as e:
            logger.error(f"خطأ في عرض الرصيد: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الرصيد")
    
    async def _handle_open_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الصفقات المفتوحة"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "open_orders")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # الحصول على الصفقات المفتوحة
            orders = order_manager.get_user_orders(user_id)
            
            if not orders:
                await update.message.reply_text("📭 لا توجد صفقات مفتوحة حالياً")
                return
            
            # تنسيق قائمة الصفقات
            orders_text = ui_manager.format_orders_list(user_id)
            
            # الحصول على لوحة المفاتيح
            keyboard = ui_manager.get_orders_keyboard(user_id)
            
            await update.message.reply_text(orders_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في عرض الصفقات المفتوحة: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الصفقات")
    
    async def _handle_trade_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض تاريخ التداول"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "trade_history")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # الحصول على تاريخ التداول
            history_text = ui_manager.format_trade_history(user_id, 10)
            
            await update.message.reply_text(history_text)
            
        except Exception as e:
            logger.error(f"خطأ في عرض تاريخ التداول: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض تاريخ التداول")
    
    async def _handle_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "statistics")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # الحصول على إحصائيات المستخدم
            user_info = ui_manager.format_user_info(user_id)
            
            await update.message.reply_text(user_info)
            
        except Exception as e:
            logger.error(f"خطأ في عرض الإحصائيات: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الإحصائيات")
    
    async def _handle_start_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تشغيل البوت للمستخدم"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "start_bot")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # تشغيل البوت للمستخدم
            success = bot_controller.set_user_bot_status(user_id, bot_controller.BotStatus.RUNNING)
            
            if success:
                await update.message.reply_text("✅ تم تشغيل البوت بنجاح")
            else:
                await update.message.reply_text("❌ فشل في تشغيل البوت")
                
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت: {e}")
            await update.message.reply_text("❌ حدث خطأ في تشغيل البوت")
    
    async def _handle_stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف البوت للمستخدم"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "stop_bot")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # إيقاف البوت للمستخدم
            success = bot_controller.set_user_bot_status(user_id, bot_controller.BotStatus.STOPPED)
            
            if success:
                await update.message.reply_text("⏹️ تم إيقاف البوت بنجاح")
            else:
                await update.message.reply_text("❌ فشل في إيقاف البوت")
                
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت: {e}")
            await update.message.reply_text("❌ حدث خطأ في إيقاف البوت")
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الأزرار المضغوطة"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            data = query.data
            
            # التحقق من الأمان
            authenticated, message = security_manager.authenticate_user(user_id, "callback")
            if not authenticated:
                await query.edit_message_text(f"❌ {message}")
                return
            
            # معالجة البيانات حسب النوع
            if data.startswith("set_amount_"):
                await self._handle_set_amount_callback(update, context, data)
            elif data.startswith("set_market_"):
                await self._handle_set_market_callback(update, context, data)
            elif data.startswith("set_leverage_"):
                await self._handle_set_leverage_callback(update, context, data)
            elif data.startswith("order_details_"):
                await self._handle_order_details_callback(update, context, data)
            elif data.startswith("partial_close_"):
                await self._handle_partial_close_callback(update, context, data)
            elif data.startswith("close_order_"):
                await self._handle_close_order_callback(update, context, data)
            else:
                await query.edit_message_text("❌ زر غير مدعوم")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الأزرار: {e}")
            await query.edit_message_text("❌ حدث خطأ في معالجة الزر")
    
    async def _handle_set_amount_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر تعيين مبلغ التداول"""
        try:
            user_id = int(data.split("_")[-1])
            
            # تعيين حالة انتظار إدخال المبلغ
            ui_manager.set_user_state(user_id, "waiting_for_trade_amount")
            
            await update.callback_query.edit_message_text("💰 أدخل مبلغ التداول الجديد:")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر المبلغ: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_set_market_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر تعيين نوع السوق"""
        try:
            user_id = int(data.split("_")[-1])
            
            # الحصول على لوحة مفاتيح نوع السوق
            keyboard = ui_manager.get_market_type_keyboard(user_id)
            
            await update.callback_query.edit_message_text("🏪 اختر نوع السوق:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر السوق: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_set_leverage_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر تعيين الرافعة المالية"""
        try:
            user_id = int(data.split("_")[-1])
            
            # الحصول على لوحة مفاتيح الرافعة المالية
            keyboard = ui_manager.get_leverage_keyboard(user_id)
            
            await update.callback_query.edit_message_text("⚡ اختر الرافعة المالية:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة زر الرافعة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_order_details_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر تفاصيل الصفقة"""
        try:
            order_id = data.split("_")[-1]
            
            # الحصول على تفاصيل الصفقة
            order_text = ui_manager.format_order_info(order_id)
            
            # الحصول على لوحة المفاتيح
            keyboard = ui_manager.get_order_details_keyboard(order_id)
            
            await update.callback_query.edit_message_text(order_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة تفاصيل الصفقة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في عرض تفاصيل الصفقة")
    
    async def _handle_partial_close_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر الإغلاق الجزئي"""
        try:
            order_id = data.split("_")[-1]
            
            # الحصول على لوحة مفاتيح الإغلاق الجزئي
            keyboard = ui_manager.get_partial_close_keyboard(order_id)
            
            await update.callback_query.edit_message_text("💰 اختر نسبة الإغلاق الجزئي:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الجزئي: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في الإغلاق الجزئي")
    
    async def _handle_close_order_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """معالجة زر إغلاق الصفقة"""
        try:
            order_id = data.split("_")[-1]
            
            # إغلاق الصفقة
            success = order_manager.close_order(order_id, "manual")
            
            if success:
                await update.callback_query.edit_message_text("✅ تم إغلاق الصفقة بنجاح")
            else:
                await update.callback_query.edit_message_text("❌ فشل في إغلاق الصفقة")
                
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في إغلاق الصفقة")
    
    async def _handle_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الأخطاء"""
        try:
            logger.error(f"خطأ في البوت: {context.error}")
            
            # تسجيل الخطأ في إحصائيات الأمان
            if update and hasattr(update, 'effective_user') and update.effective_user:
                user_id = update.effective_user.id
                security_manager.record_failed_attempt(user_id, f"bot_error: {context.error}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الخطأ: {e}")
    
    def get_bot_stats(self) -> Dict:
        """الحصول على إحصائيات البوت"""
        try:
            uptime = 0
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                'is_running': self.is_running,
                'uptime': uptime,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'stats': self.stats.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات البوت: {e}")
            return {'error': str(e)}

# إنشاء مثيل البوت
smart_bot = SmartTradingBot()

async def main():
    """الدالة الرئيسية"""
    try:
        await smart_bot.start()
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
    finally:
        # تنظيف الموارد
        try:
            security_manager.stop_security_monitoring()
            bot_controller.stop_monitoring()
            order_manager.stop_price_monitoring()
            logger.info("تم تنظيف الموارد")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد: {e}")

if __name__ == "__main__":
    asyncio.run(main())
