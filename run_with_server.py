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
from datetime import datetime
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram import ReplyKeyboardMarkup, KeyboardButton
from user_manager import user_manager

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
        self.current_account = None
        
        # إحصائيات النظام
        self.stats = {
            'total_users': 0,
            'active_users': 0,
            'total_orders': 0,
            'messages_processed': 0,
            'uptime': 0,
            'mode': 'integrated'
        }
    
    def get_current_account(self):
        """الحصول على الحساب الحالي"""
        return self.current_account
    
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
            from smart_trading_bot import SmartTradingBot
            from commands import command_handler
            
            # إنشاء مثيل البوت الذكي
            self.new_bot = SmartTradingBot()
            
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
            return ReplyKeyboardMarkup([], resize_keyboard=True)
    
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
            if self.old_bot:
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
                environment = "🚂 Railway Cloud"
            else:
                webhook_url = f"http://localhost:{PORT}/webhook"
                environment = "💻 Local Development"
            
            message = f"""
🌐 إشارات TradingView

🌍 البيئة: {environment}
📡 رابط استقبال الإشارات:
`{webhook_url}`

📋 كيفية الاستخدام:
1. انسخ الرابط أعلاه
2. اذهب إلى TradingView
3. أضف الرابط في إعدادات Webhook
4. أرسل الإشارات بالصيغة:
   {{"symbol": "BTCUSDT", "action": "buy"}}

✅ البوت جاهز لاستقبال الإشارات!
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"❌ خطأ في عرض رابط TradingView: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض رابط الإشارات")
    
    async def _handle_system_switch(self, update, context):
        """تبديل النظام"""
        try:
            message = """
🔄 تبديل النظام

🔧 النظام الذكي الجديد:
• دعم متعدد المستخدمين
• بيئات منفصلة لكل مستخدم
• إدارة صفقات متقدمة مع TP/SL
• نظام حماية شامل
• قاعدة بيانات متقدمة

📊 النظام التقليدي:
• مستخدم واحد
• إدارة صفقات بسيطة
• متوافق مع الإشارات الخارجية

💡 التوصية: استخدم النظام الذكي الجديد للحصول على أفضل تجربة
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"❌ خطأ في تبديل النظام: {e}")
            await update.message.reply_text("❌ حدث خطأ في تبديل النظام")
    
    async def _handle_callback(self, update, context):
        """معالجة الأزرار المضغوطة"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            data = query.data
            
            # استخدام النظام الجديد للمصادقة
            from security_manager import security_manager
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
            logger.error(f"❌ خطأ في معالجة الأزرار: {e}")
            await query.edit_message_text("❌ حدث خطأ في معالجة الزر")
    
    async def _handle_set_amount_callback(self, update, context, data):
        """معالجة زر تعيين مبلغ التداول"""
        try:
            user_id = int(data.split("_")[-1])
            
            from ui_manager import ui_manager
            ui_manager.set_user_state(user_id, "waiting_for_trade_amount")
            
            await update.callback_query.edit_message_text("💰 أدخل مبلغ التداول الجديد:")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة زر المبلغ: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_set_market_callback(self, update, context, data):
        """معالجة زر تعيين نوع السوق"""
        try:
            user_id = int(data.split("_")[-1])
            
            from ui_manager import ui_manager
            keyboard = ui_manager.get_market_type_keyboard(user_id)
            
            await update.callback_query.edit_message_text("🏪 اختر نوع السوق:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة زر السوق: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_set_leverage_callback(self, update, context, data):
        """معالجة زر تعيين الرافعة المالية"""
        try:
            user_id = int(data.split("_")[-1])
            
            from ui_manager import ui_manager
            keyboard = ui_manager.get_leverage_keyboard(user_id)
            
            await update.callback_query.edit_message_text("⚡ اختر الرافعة المالية:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة زر الرافعة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ")
    
    async def _handle_order_details_callback(self, update, context, data):
        """معالجة زر تفاصيل الصفقة"""
        try:
            order_id = data.split("_")[-1]
            
            from ui_manager import ui_manager
            order_text = ui_manager.format_order_info(order_id)
            keyboard = ui_manager.get_order_details_keyboard(order_id)
            
            await update.callback_query.edit_message_text(order_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة تفاصيل الصفقة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في عرض تفاصيل الصفقة")
    
    async def _handle_partial_close_callback(self, update, context, data):
        """معالجة زر الإغلاق الجزئي"""
        try:
            order_id = data.split("_")[-1]
            
            from ui_manager import ui_manager
            keyboard = ui_manager.get_partial_close_keyboard(order_id)
            
            await update.callback_query.edit_message_text("💰 اختر نسبة الإغلاق الجزئي:", reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإغلاق الجزئي: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في الإغلاق الجزئي")
    
    async def _handle_close_order_callback(self, update, context, data):
        """معالجة زر إغلاق الصفقة"""
        try:
            order_id = data.split("_")[-1]
            
            from order_manager import order_manager
            success = order_manager.close_order(order_id, "manual")
            
            if success:
                await update.callback_query.edit_message_text("✅ تم إغلاق الصفقة بنجاح")
            else:
                await update.callback_query.edit_message_text("❌ فشل في إغلاق الصفقة")
                
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقة: {e}")
            await update.callback_query.edit_message_text("❌ حدث خطأ في إغلاق الصفقة")
    
    async def _handle_error(self, update, context):
        """معالجة الأخطاء"""
        try:
            logger.error(f"خطأ في البوت المتكامل: {context.error}")
            
            # تسجيل الخطأ في إحصائيات الأمان
            if update and hasattr(update, 'effective_user') and update.effective_user:
                user_id = update.effective_user.id
                from security_manager import security_manager
                security_manager.record_failed_attempt(user_id, f"bot_error: {context.error}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الخطأ: {e}")
    
    def start_web_server(self):
        """بدء السيرفر الويب"""
        try:
            if self.web_server:
                self.web_server.run(debug=False, port=PORT)
            else:
                logger.error("❌ السيرفر الويب غير مهيأ")
                
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل السيرفر الويب: {e}")
    
    def get_stats(self):
        """الحصول على إحصائيات النظام"""
        try:
            uptime = 0
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                'is_running': self.is_running,
                'uptime': uptime,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'stats': self.stats.copy(),
                'mode': 'integrated',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            return {'error': str(e)}

def send_railway_url_notification(webhook_url):
    """إرسال إشعار برابط Railway عبر تلجرام"""
    try:
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        from telegram.ext import Application
        import asyncio
        
        async def send_message():
            try:
                application = Application.builder().token(TELEGRAM_TOKEN).build()
                
                # تحديد نوع البيئة
                if "railway" in webhook_url.lower() or "railway.app" in webhook_url:
                    environment = "🚂 Railway Cloud"
                elif "render" in webhook_url.lower():
                    environment = "☁️ Render Cloud"
                else:
                    environment = "💻 Local Development"
                
                message = f"🚀 بدء تشغيل البوت المتكامل\n\n"
                message += f"🌍 البيئة: {environment}\n"
                message += f"🌐 رابط استقبال الإشارات:\n`{webhook_url}`\n\n"
                message += f"📡 استخدم هذا الرابط في TradingView لإرسال الإشارات\n"
                message += f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                message += f"✅ البوت المتكامل جاهز لاستقبال الإشارات!"
                
                await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message, parse_mode='Markdown')
            except Exception as e:
                print(f"❌ خطأ في إرسال إشعار Railway: {e}")
        
        # تشغيل في thread منفصل
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_message())
            loop.close()
        
        threading.Thread(target=run_async, daemon=True).start()
        
    except Exception as e:
        print(f"❌ خطأ في إعداد إشعار Railway: {e}")

async def main():
    """الدالة الرئيسية لتشغيل النظام المتكامل"""
    try:
        print("🚀 بدء تشغيل النظام المتكامل للتداول على Bybit...")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # إنشاء مُهيئ النظام
        from system_initializer import SystemInitializer
        initializer = SystemInitializer()
        
        # تهيئة النظام بالكامل
        if not await initializer.initialize_system():
            raise Exception("فشل في تهيئة النظام")
        
        # الحصول على المكونات الأساسية
        web_server = initializer.get_component('web_server')
        telegram_bot = initializer.get_component('telegram')
        trading_bot = initializer.get_component('trading')
        
        # تشغيل السيرفر الويب في thread منفصل
        server_thread = threading.Thread(
            target=web_server.run,
            daemon=True
        )
        server_thread.start()
        
        print("✅ تم تشغيل السيرفر الويب بنجاح")
        
        # إعداد وإرسال إشعار برابط Webhook
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            if not railway_url.startswith('http'):
                railway_url = f"https://{railway_url}"
            webhook_url = f"{railway_url}/webhook"
            print("=" * 60)
            print("🌐 رابط Webhook للاستقبال من Railway:")
            print(f"   {webhook_url}")
            print("=" * 60)
            send_railway_url_notification(webhook_url)
        else:
            webhook_url = f"http://localhost:{PORT}/webhook"
            print("=" * 60)
            print("🌐 رابط Webhook:")
            print(f"   {webhook_url}")
            print("=" * 60)
            send_railway_url_notification(webhook_url)
        
        print("🤖 بدء تشغيل بوت التلجرام المتكامل...")
        
        # تشغيل بوت التليجرام
        await integrated_bot.start_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت المتكامل بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت المتكامل: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # For Windows compatibility
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    
    asyncio.run(main())