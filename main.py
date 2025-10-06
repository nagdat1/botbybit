"""
🤖 Bybit Trading Bot - Main Application
بوت تداول احترافي لمنصة Bybit
المطور: Nagdat
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# إعداد السجلات
from loguru import logger as loguru_logger
import sys

# إعداد loguru
loguru_logger.remove()
loguru_logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
loguru_logger.add(
    "bot.log",
    rotation="1 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)

# إعدادات التطبيق
from config import TELEGRAM_TOKEN, ADMIN_USER_ID, EMOJIS
from database import db

# المعالجات
from handlers.user_handler import UserHandler
from handlers.admin_handler import AdminHandler
from handlers.trading_handler import TradingHandler

# Webhook Server
from webhook_server import start_webhook_server_thread, set_bot_instance

# إنشاء logger للطباعة العادية
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BybitTradingBot:
    """البوت الرئيسي"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.application = None
        logger.info("🚀 Initializing Bybit Trading Bot...")
    
    def setup_handlers(self):
        """إعداد المعالجات"""
        app = self.application
        
        # ==================== الأوامر ====================
        app.add_handler(CommandHandler("start", UserHandler.start_command))
        app.add_handler(CommandHandler("help", UserHandler.help_command))
        app.add_handler(CommandHandler("setapi", UserHandler.setapi_command))
        
        # ==================== القوائم الرئيسية ====================
        app.add_handler(CallbackQueryHandler(UserHandler.back_to_main, pattern="^back_to_main$"))
        app.add_handler(CallbackQueryHandler(UserHandler.menu_wallet, pattern="^menu_wallet$"))
        app.add_handler(CallbackQueryHandler(UserHandler.menu_settings, pattern="^menu_settings$"))
        app.add_handler(CallbackQueryHandler(UserHandler.menu_help, pattern="^menu_help$"))
        
        # ==================== التداول ====================
        app.add_handler(CallbackQueryHandler(TradingHandler.menu_trading, pattern="^menu_trading$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.back_to_trading, pattern="^back_to_trading$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.trade_buy, pattern="^trade_buy$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.trade_sell, pattern="^trade_sell$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.set_type_spot, pattern="^set_type_spot$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.set_type_futures, pattern="^set_type_futures$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.set_leverage, pattern="^leverage_"))
        app.add_handler(CallbackQueryHandler(TradingHandler.select_symbol, pattern="^select_symbol_"))
        app.add_handler(CallbackQueryHandler(TradingHandler.show_all_symbols, pattern="^show_all_symbols$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.execute_trade, pattern="^confirm_execute_trade"))
        
        # ==================== الصفقات ====================
        app.add_handler(CallbackQueryHandler(TradingHandler.menu_my_trades, pattern="^menu_my_trades$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.view_trade, pattern="^view_trade_"))
        app.add_handler(CallbackQueryHandler(TradingHandler.close_trade_full, pattern="^close_full_"))
        app.add_handler(CallbackQueryHandler(TradingHandler.close_trade_partial, pattern="^close_[0-9]+_"))
        app.add_handler(CallbackQueryHandler(TradingHandler.refresh_trades, pattern="^refresh_trades$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.menu_my_trades, pattern="^back_to_trades$"))
        
        # ==================== إشارات Nagdat ====================
        app.add_handler(CallbackQueryHandler(TradingHandler.menu_signals, pattern="^menu_signals$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.subscribe_nagdat, pattern="^subscribe_nagdat$"))
        app.add_handler(CallbackQueryHandler(TradingHandler.unsubscribe_nagdat, pattern="^unsubscribe_nagdat$"))
        
        # ==================== الإعدادات ====================
        app.add_handler(CallbackQueryHandler(UserHandler.settings_switch_mode, pattern="^settings_switch_mode$"))
        app.add_handler(CallbackQueryHandler(UserHandler.account_demo, pattern="^account_demo$"))
        app.add_handler(CallbackQueryHandler(UserHandler.account_real, pattern="^account_real$"))
        app.add_handler(CallbackQueryHandler(UserHandler.settings_webhook, pattern="^settings_webhook$"))
        
        # ==================== لوحة المطور ====================
        app.add_handler(CallbackQueryHandler(AdminHandler.admin_panel, pattern="^admin_panel$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.admin_stats, pattern="^admin_stats$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.admin_subscribers, pattern="^admin_subscribers$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.admin_send_signal, pattern="^admin_send_signal$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.signal_buy, pattern="^signal_buy$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.signal_sell, pattern="^signal_sell$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.confirm_send_signal, pattern="^confirm_send_signal$"))
        app.add_handler(CallbackQueryHandler(AdminHandler.admin_broadcast, pattern="^admin_broadcast$"))
        
        # ==================== معالج الرسائل النصية ====================
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_messages
        ))
        
        logger.info("✅ Handlers setup completed")
    
    async def handle_text_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        
        # معالجة مدخلات الأدمن
        if user_id == ADMIN_USER_ID and context.user_data.get('admin_action'):
            if context.user_data['admin_action'] == 'send_signal':
                await AdminHandler.process_signal_input(update, context)
                return
            elif context.user_data['admin_action'] == 'broadcast':
                await AdminHandler.process_broadcast(update, context)
                return
        
        # معالجة مدخلات التداول
        if context.user_data.get('trade_action') in ['buy', 'sell']:
            await TradingHandler.process_trade_amount(update, context)
            return
        
        # رسالة افتراضية
        await update.message.reply_text(
            f"{EMOJIS['info']} استخدم الأزرار للتنقل في البوت\n"
            f"أو اكتب /help للمساعدة"
        )
    
    async def post_init(self, application: Application):
        """تهيئة ما بعد الإنشاء"""
        logger.info("✅ Bot initialized successfully")
        
        # إرسال رسالة للأدمن
        try:
            await application.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"{EMOJIS['rocket']} البوت يعمل الآن!\n\n"
                     f"{EMOJIS['success']} جميع الأنظمة جاهزة"
            )
        except Exception as e:
            logger.error(f"Failed to send startup message to admin: {e}")
    
    async def post_shutdown(self, application: Application):
        """تنظيف ما بعد الإغلاق"""
        logger.info("🛑 Bot shutting down...")
        
        try:
            await application.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"{EMOJIS['warning']} البوت متوقف الآن"
            )
        except Exception as e:
            logger.error(f"Failed to send shutdown message: {e}")
    
    def run(self):
        """تشغيل البوت"""
        try:
            # بناء التطبيق
            self.application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # إعداد المعالجات
            self.setup_handlers()
            
            # تعيين callbacks
            self.application.post_init = self.post_init
            self.application.post_shutdown = self.post_shutdown
            
            # تشغيل خادم Webhooks
            logger.info("🌐 Starting webhook server...")
            start_webhook_server_thread()
            set_bot_instance(self.application.bot)
            
            # تشغيل البوت
            logger.info("🚀 Starting bot polling...")
            loguru_logger.info(f"""
╔══════════════════════════════════════════╗
║   🤖 Bybit Trading Bot Started! 🚀      ║
╠══════════════════════════════════════════╣
║   Developer: Nagdat                      ║
║   Mode: Production                       ║
║   Status: ✅ Active                      ║
╚══════════════════════════════════════════╝
            """)
            
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("⚠️ Received keyboard interrupt")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            raise
        finally:
            logger.info("👋 Bot stopped")


def main():
    """نقطة البداية"""
    try:
        # إنشاء وتشغيل البوت
        bot = BybitTradingBot()
        bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

