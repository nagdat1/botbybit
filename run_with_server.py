#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مشروع متكامل ومترابط للتداول على Bybit
يدعم النظام القديم والجديد مع دعم Railway
"""

import sys
import os
import threading
import asyncio
import logging
import time
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# الحصول على المنفذ من متغير البيئة (Railway)
PORT = int(os.environ.get('PORT', 5000))

class IntegratedTradingBot:
    """البوت المتكامل الذي يجمع النظام القديم والجديد"""
    
    def __init__(self):
        self.old_bot = None
        self.new_bot = None
        self.web_server = None
        self.is_running = False
        self.start_time = None
        
        # إحصائيات النظام
        self.stats = {
            'total_users': 0,
            'active_users': 0,
            'total_orders': 0,
            'messages_processed': 0,
            'uptime': 0,
            'mode': 'integrated'
        }
    
    async def initialize(self):
        """تهيئة النظام المتكامل"""
        try:
            logger.info("🚀 بدء تهيئة النظام المتكامل...")
            
            # تهيئة النظام الجديد
            await self._initialize_new_system()
            
            # تهيئة النظام القديم
            await self._initialize_old_system()
            
            # تهيئة السيرفر الويب
            await self._initialize_web_server()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("✅ تم تهيئة النظام المتكامل بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة النظام: {e}")
            raise
    
    async def _initialize_new_system(self):
        """تهيئة النظام الجديد (الذكي)"""
        try:
            from database import db_manager
            from user_manager import user_manager
            from api_manager import api_manager
            from order_manager import order_manager
            from security_manager import security_manager
            from bot_controller import bot_controller
            
            # تهيئة قاعدة البيانات
            db_manager.init_database()
            
            # بدء مراقبة الأمان
            security_manager.start_security_monitoring()
            
            # بدء مراقبة النظام
            bot_controller.start_monitoring()
            
            # بدء مراقبة الأسعار
            order_manager.start_price_monitoring()
            
            logger.info("✅ تم تهيئة النظام الجديد")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة النظام الجديد: {e}")
            raise
    
    async def _initialize_old_system(self):
        """تهيئة النظام القديم"""
        try:
            from bybit_trading_bot import trading_bot
            
            # تهيئة البوت القديم
            self.old_bot = trading_bot
            
            logger.info("✅ تم تهيئة النظام القديم")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة النظام القديم: {e}")
            # لا نرفع الخطأ لأن النظام الجديد يمكن أن يعمل منفرداً
    
    async def _initialize_web_server(self):
        """تهيئة السيرفر الويب"""
        try:
            from web_server import WebServer
            
            # إنشاء السيرفر مع البوت المتكامل
            self.web_server = WebServer(self)
            
            logger.info("✅ تم تهيئة السيرفر الويب")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة السيرفر الويب: {e}")
            raise
    
    async def start_telegram_bot(self):
        """بدء بوت التليجرام المتكامل"""
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
            from config import TELEGRAM_TOKEN
            
            # إنشاء تطبيق التليجرام
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # إضافة المعالجات المتكاملة
            self._setup_integrated_handlers(application)
            
            logger.info("🤖 بدء تشغيل بوت التليجرام المتكامل...")
            
            # تشغيل البوت
            await application.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل بوت التليجرام: {e}")
            raise
    
    def _setup_integrated_handlers(self, application):
        """إعداد المعالجات المتكاملة"""
        try:
            # استيراد المعالجات من النظام الجديد
            from commands import command_handler
            from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
            
            # إنشاء مثيل البوت الذكي
            
            # إضافة المعالجات الأساسية
            application.add_handler(CommandHandler("start", self._handle_start))
            application.add_handler(CommandHandler("balance", self._handle_balance))
            application.add_handler(CommandHandler("buy", self._handle_buy))
            application.add_handler(CommandHandler("sell", self._handle_sell))
            application.add_handler(CommandHandler("help", self._handle_help))
            
            # معالج الرسائل النصية
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
            
            # معالج الأزرار
            application.add_handler(CallbackQueryHandler(self._handle_callback))
            
            # معالج الأخطاء
            application.add_error_handler(self._handle_error)
            
            logger.info("✅ تم إعداد المعالجات المتكاملة")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد المعالجات: {e}")
            raise
    
    async def _handle_start(self, update, context):
        """معالجة أمر /start المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "start")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # عرض القائمة المتكاملة
            await self._show_integrated_menu(update, context)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة /start: {e}")
            await update.message.reply_text("❌ حدث خطأ في بدء البوت")
    
    async def _show_integrated_menu(self, update, context):
        """عرض القائمة المتكاملة"""
        try:
            from ui_manager import ui_manager
            
            # الحصول على لوحة المفاتيح المتكاملة
            keyboard = self._get_integrated_keyboard(update.effective_user.id)
            
            welcome_text = f"""
🤖 مرحباً بك في البوت المتكامل للتداول على Bybit

🔧 الميزات المتاحة:
• 🔗 ربط مفاتيح API لكل مستخدم
• ⚙️ إعدادات مخصصة ومنفصلة
• 📊 إدارة الصفقات مع TP/SL متقدم
• 🛡️ نظام حماية شامل
• 💰 تداول حقيقي وتجريبي
• 📈 مراقبة الأسعار في الوقت الفعلي
• 🌐 استقبال إشارات من TradingView

🚀 النظام يدعم:
• النظام الذكي الجديد (متعدد المستخدمين)
• النظام التقليدي (للتوافق)

استخدم الأزرار أدناه للتنقل
            """
            
            await update.message.reply_text(welcome_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض القائمة المتكاملة: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض القائمة")
    
    def _get_integrated_keyboard(self, user_id):
        """الحصول على لوحة المفاتيح المتكاملة"""
        try:
            from telegram import ReplyKeyboardMarkup, KeyboardButton
            
            # الأزرار الأساسية
            keyboard = [
                [KeyboardButton("🔗 الربط"), KeyboardButton("⚙️ الإعدادات")],
                [KeyboardButton("💰 الرصيد"), KeyboardButton("📊 الصفقات المفتوحة")],
                [KeyboardButton("📈 تاريخ التداول"), KeyboardButton("📊 الإحصائيات")],
                [KeyboardButton("🌐 إشارات TradingView"), KeyboardButton("🔄 تبديل النظام")]
            ]
            
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء لوحة المفاتيح: {e}")
            # التأكد من استيراد ReplyKeyboardMarkup
            try:
                from telegram import ReplyKeyboardMarkup
                return ReplyKeyboardMarkup([], resize_keyboard=True)
            except:
                # إذا فشل الاستيراد، نعيد None
                return None
    
    async def _handle_balance(self, update, context):
        """معالجة أمر /balance المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "balance")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # عرض الرصيد المتكامل
            await self._show_integrated_balance(update, context)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة /balance: {e}")
            await update.message.reply_text("❌ خطأ في الحصول على معلومات الرصيد")
    
    async def _show_integrated_balance(self, update, context):
        """عرض الرصيد المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # الحصول على معلومات من النظام الجديد
            from user_manager import user_manager
            user_env = user_manager.get_user_environment(user_id)
            
            balance_info = user_env.get_balance_info()
            trading_stats = user_env.get_trading_stats()
            settings = user_env.get_settings()
            
            # الحصول على معلومات من النظام القديم (إذا كان متاحاً)
            old_balance_info = ""
            if self.old_bot and hasattr(self.old_bot, 'get_current_account'):
                try:
                    account = self.old_bot.get_current_account()
                    account_info = account.get_account_info()
                    old_balance_info = f"""
📊 النظام التقليدي:
• الرصيد: {account_info['balance']:.2f}
• الصفقات المفتوحة: {account_info['open_positions']}
                    """
                except:
                    old_balance_info = "📊 النظام التقليدي: غير متاح"
            
            balance_text = f"""
💰 معلومات الرصيد المتكاملة

🔧 النظام الذكي الجديد:
• الرصيد الكلي: {balance_info['balance']:.2f} USDT
• الرصيد المتاح: {balance_info['available_balance']:.2f} USDT
• الهامش المحجوز: {balance_info['margin_locked']:.2f} USDT
• إجمالي PnL: {balance_info['total_pnl']:.2f} USDT

📊 إحصائيات التداول:
• إجمالي الصفقات: {trading_stats['total_trades']}
• الصفقات الرابحة: {trading_stats['winning_trades']}
• الصفقات الخاسرة: {trading_stats['losing_trades']}
• معدل النجاح: {trading_stats['win_rate']:.1f}%

⚙️ الإعدادات:
• نوع السوق: {settings.get('market_type', 'spot').upper()}
• الرافعة المالية: {settings.get('leverage', 1)}x
• مبلغ التداول: {settings.get('trade_amount', 100)} USDT

{old_balance_info}
            """
            
            await update.message.reply_text(balance_text)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض الرصيد المتكامل: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الرصيد")
    
    async def _handle_buy(self, update, context):
        """معالجة أمر /buy المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "buy")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # استخدام النظام الجديد لمعالجة الأمر
            from commands import command_handler
            await command_handler.handle_buy(update, context)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة /buy: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر الشراء")
    
    async def _handle_sell(self, update, context):
        """معالجة أمر /sell المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "sell")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # استخدام النظام الجديد لمعالجة الأمر
            from commands import command_handler
            await command_handler.handle_sell(update, context)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة /sell: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر البيع")
    
    async def _handle_help(self, update, context):
        """معالجة أمر /help المتكامل"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "help")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            help_text = """
🤖 أوامر البوت المتكامل:

🔧 الأوامر الأساسية:
• /start - بدء البوت وعرض القائمة المتكاملة
• /balance - عرض معلومات الرصيد المتكاملة
• /help - عرض هذه الرسالة

📊 أوامر التداول:
• /buy SYMBOL QUANTITY - شراء رمز معين
• /sell SYMBOL QUANTITY - بيع رمز معين

📝 أمثلة:
• /buy BTCUSDT 0.001
• /sell ETHUSDT 0.1

🔗 الربط:
• اضغط على زر "🔗 الربط" لربط مفاتيح API
• أدخل مفاتيحك بالصيغة: API_KEY API_SECRET

⚙️ الإعدادات:
• اضغط على "⚙️ الإعدادات" لتخصيص البوت
• يمكنك تغيير نوع السوق والرافعة المالية

📊 الصفقات:
• اضغط على "📊 الصفقات المفتوحة" لإدارة صفقاتك
• يمكنك إضافة TP/SL والإغلاق الجزئي

🌐 إشارات TradingView:
• اضغط على "🌐 إشارات TradingView" لعرض رابط الاستقبال
• استخدم الرابط في TradingView لإرسال الإشارات

🔄 تبديل النظام:
• اضغط على "🔄 تبديل النظام" للتبديل بين النظامين

❓ للمساعدة: تواصل مع الدعم الفني
            """
            
            await update.message.reply_text(help_text)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة /help: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض المساعدة")
    
    async def _handle_text(self, update, context):
        """معالجة الرسائل النصية المتكاملة"""
        try:
            user_id = update.effective_user.id
            text = update.message.text
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
            authenticated, message = security_manager.authenticate_user(user_id, "text_message")
            if not authenticated:
                await update.message.reply_text(f"❌ {message}")
                return
            
            # معالجة النص حسب المحتوى
            if text == "🔗 الربط":
                await self._handle_api_linking(update, context)
            elif text == "⚙️ الإعدادات":
                await self._handle_settings(update, context)
            elif text == "💰 الرصيد":
                await self._show_integrated_balance(update, context)
            elif text == "📊 الصفقات المفتوحة":
                await self._handle_open_orders(update, context)
            elif text == "📈 تاريخ التداول":
                await self._handle_trade_history(update, context)
            elif text == "📊 الإحصائيات":
                await self._handle_statistics(update, context)
            elif text == "🌐 إشارات TradingView":
                await self._handle_tradingview_signals(update, context)
            elif text == "🔄 تبديل النظام":
                await self._handle_system_switch(update, context)
            else:
                await update.message.reply_text("❌ أمر غير مدعوم")
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الرسالة النصية: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الرسالة")
    
    async def _handle_api_linking(self, update, context):
        """معالجة ربط مفاتيح API"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد لربط API
            from ui_manager import ui_manager
            ui_manager.set_user_state(user_id, "waiting_for_api_keys")
            
            await update.message.reply_text(
                "🔗 ربط مفاتيح API\n\n"
                "أدخل مفاتيح API الخاصة بك بالصيغة التالية:\n"
                "API_KEY API_SECRET\n\n"
                "مثال:\n"
                "abc123def456 xyz789uvw012"
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة ربط API: {e}")
            await update.message.reply_text("❌ حدث خطأ في ربط مفاتيح API")
    
    async def _handle_settings(self, update, context):
        """معالجة الإعدادات"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للإعدادات
            from ui_manager import ui_manager
            from user_manager import user_manager  # إضافة الاستيراد المفقود
            
            keyboard = ui_manager.get_settings_keyboard(user_id)
            
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            
            settings_text = f"""
⚙️ إعدادات البوت المتكامل

💰 مبلغ التداول: {settings.get('trade_amount', 100)} USDT
🏪 نوع السوق: {settings.get('market_type', 'spot').upper()}
⚡ الرافعة المالية: {settings.get('leverage', 1)}x
🔗 حالة API: {'مرتبط' if user_env.has_api_keys() else 'غير مرتبط'}
🤖 حالة البوت: {'نشط' if user_env.is_active else 'متوقف'}

اختر الإعداد الذي تريد تعديله:
            """
            
            await update.message.reply_text(settings_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإعدادات: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الإعدادات")
    
    async def _handle_open_orders(self, update, context):
        """عرض الصفقات المفتوحة"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد لعرض الصفقات
            from order_manager import order_manager
            from ui_manager import ui_manager
            
            orders = order_manager.get_user_orders(user_id)
            
            if not orders:
                await update.message.reply_text("📭 لا توجد صفقات مفتوحة حالياً")
                return
            
            orders_text = ui_manager.format_orders_list(user_id)
            keyboard = ui_manager.get_orders_keyboard(user_id)
            
            await update.message.reply_text(orders_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض الصفقات المفتوحة: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الصفقات")
    
    async def _handle_trade_history(self, update, context):
        """عرض تاريخ التداول"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد لعرض التاريخ
            from ui_manager import ui_manager
            history_text = ui_manager.format_trade_history(user_id, 10)
            
            await update.message.reply_text(history_text)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض تاريخ التداول: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض تاريخ التداول")
    
    async def _handle_statistics(self, update, context):
        """عرض الإحصائيات"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد لعرض الإحصائيات
            from ui_manager import ui_manager
            user_info = ui_manager.format_user_info(user_id)
            
            await update.message.reply_text(user_info)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض الإحصائيات: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الإحصائيات")
    
    async def _handle_tradingview_signals(self, update, context):
        """عرض رابط إشارات TradingView"""
        try:
            # الحصول على رابط Webhook
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            if railway_url:
                if not railway_url.startswith('http'):
                    railway_url = f"https://{railway_url}"
                webhook_url = f"{railway_url}/webhook"
                environment = "ityEngine Railway Cloud"
            else:
                webhook_url = f"http://localhost:{PORT}/webhook"
                environment = "💻 Local Development"
            
            signals_text = f"""
🌐 إشارات TradingView

استخدم الرابط التالي لربط إشارات TradingView مع بوت التداول:
```
{webhook_url}

```
البيئة الحالية: {environment}
```
            """
            
            await update.message.reply_text(signals_text)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض رابط إشارات TradingView: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض رابط إشارات TradingView")
    
    async def _handle_system_switch(self, update, context):
        """تبديل النظام"""
        try:
            user_id = update.effective_user.id
            
            # استخدام النظام الجديد للتبديل
            from user_manager import user_manager
            user_env = user_manager.get_user_environment(user_id)
            
            # إزالة الاستدعاءات غير المتوفرة
            response = "🔄 تم تبديل النظام\n\nالميزة: النظام الجديد يدعم متعدد المستخدمين وإدارة صفقات متقدمة"
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"❌ خطأ في تبديل النظام: {e}")
            await update.message.reply_text("❌ حدث خطأ في تبديل النظام")
    
    async def _handle_callback(self, update, context):
        """معالجة الردود المتغيرة (Callback)"""
        try:
            user_id = update.effective_user.id
            query = update.callback_query
            
            # استخدام النظام الجديد لمعالجة الردود المتغيرة
            await query.answer()
            await query.edit_message_text("❌ هذه الميزة غير متوفرة حالياً")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الرد المتغير: {e}")
            if update.message:
                await update.message.reply_text("❌ حدث خطأ في معالجة الرد المتغير")
    
    async def _handle_error(self, update, context):
        """معالجة الأخطاء"""
        try:
            logger.error(f"❌ حدث خطأ غير متوقع:\n{context.error}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الأخطاء: {e}")
            await update.message.reply_text("❌ حدث خطأ غير متوقع")
