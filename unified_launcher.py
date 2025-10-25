#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل الموحد النهائي - Final Unified Launcher
تشغيل النظام الموحد مع جميع الوظائف المدمجة
"""

import logging
import asyncio
import sys
import os
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def show_unified_welcome():
    """عرض رسالة الترحيب للنظام الموحد"""
    print("\n" + "="*80)
    print("🚀 مرحباً بك في النظام الموحد للتداول")
    print("="*80)
    print("\n🎯 الميزات الموحدة:")
    print("  • 🔑 إدارة مفاتيح API لكل مستخدم")
    print("  • ⚡ تعديل الرافعة المالية (1x-100x)")
    print("  • 💰 تعديل مبلغ التداول")
    print("  • 🏪 التبديل بين Spot و Futures")
    print("  • 👤 التبديل بين الحساب الحقيقي والتجريبي")
    print("  • 🏦 دعم متعدد المنصات (Bybit & MEXC)")
    print("\n🛡️ الميزات المحفوظة:")
    print("  • ✅ آلية التوقيع محفوظة 100%")
    print("  • ✅ آلية حساب السعر محفوظة 100%")
    print("  • ✅ جميع الصفقات تعمل بنفس الطريقة")
    print("  • ✅ النظام منظم وموحد")
    print("\n📱 الأوامر المتاحة:")
    print("  • /start - بدء البوت")
    print("  • /enhanced_settings - الإعدادات المحسنة")
    print("  • /config_summary - عرض الإعدادات")
    print("  • /test_trade - اختبار الصفقات")
    print("\n" + "="*80)
    print("🚀 بدء التشغيل...\n")

async def initialize_unified_system():
    """تهيئة النظام الموحد"""
    try:
        logger.info("🔄 تهيئة النظام الموحد...")
        
        # 1. تهيئة النظام المحسن الموحد
        try:
            from enhanced.unified_enhanced_system import unified_enhanced_system
            await unified_enhanced_system.initialize_system()
            logger.info("✅ تم تحميل النظام المحسن الموحد")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل النظام المحسن: {e}")
            return False
        
        # 2. تهيئة مدير المنصات الموحد
        try:
            from exchanges.unified_exchange_manager import unified_exchange_manager
            logger.info("✅ تم تحميل مدير المنصات الموحد")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل مدير المنصات: {e}")
            return False
        
        # 3. تهيئة البوت الموحد
        try:
            from core.unified_trading_bot import unified_trading_bot
            logger.info("✅ تم تحميل البوت الموحد")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل البوت الموحد: {e}")
            return False
        
        # 4. تهيئة قاعدة البيانات
        try:
            from database import db_manager
            db_manager.init_database()
            logger.info("✅ تم تهيئة قاعدة البيانات")
        except Exception as e:
            logger.error(f"❌ فشل في تهيئة قاعدة البيانات: {e}")
            return False
        
        # 5. تهيئة مدير المستخدمين
        try:
            from user_manager import user_manager
            logger.info("✅ تم تحميل مدير المستخدمين")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل مدير المستخدمين: {e}")
            return False
        
        logger.info("✅ تم تهيئة النظام الموحد بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة النظام الموحد: {e}")
        return False

async def setup_telegram_handlers():
    """إعداد معالجات Telegram"""
    try:
        logger.info("📱 إعداد معالجات Telegram...")
        
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
        from config import TELEGRAM_TOKEN
        
        # إنشاء التطبيق
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # استيراد المعالجات من النظام المحسن
        from enhanced.unified_enhanced_system import unified_enhanced_system
        
        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", handle_start))
        application.add_handler(CommandHandler("enhanced_settings", unified_enhanced_system.bot_interface.show_enhanced_settings_menu))
        application.add_handler(CommandHandler("config_summary", show_config_summary))
        application.add_handler(CommandHandler("test_trade", test_trade))
        
        # إضافة معالجات الاستدعاءات
        application.add_handler(CallbackQueryHandler(
            unified_enhanced_system.bot_interface.handle_enhanced_settings_callback,
            pattern=r"^(select_exchange_enhanced|exchange_bybit_enhanced|exchange_mexc_enhanced|set_amount_enhanced|set_market_enhanced|market_spot_enhanced|market_futures_enhanced|set_account_enhanced|account_real_enhanced|account_demo_enhanced|set_leverage_enhanced|set_demo_balance_enhanced|set_api_keys_enhanced|settings_enhanced)$"
        ))
        
        # إضافة معالجات الرسائل
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unified_enhanced_system.bot_interface.handle_enhanced_text_input
        ))
        
        logger.info("✅ تم إعداد معالجات Telegram بنجاح")
        return application
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد معالجات Telegram: {e}")
        return None

async def handle_start(update, context):
    """معالجة أمر /start"""
    try:
        from telegram import Update
        from user_manager import user_manager
        from enhanced.unified_enhanced_system import unified_enhanced_system
        
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # إنشاء المستخدم إذا لم يكن موجوداً
        user_data = user_manager.get_user(user_id)
        if not user_data:
            user_manager.create_user(user_id)
            logger.info(f"تم إنشاء مستخدم جديد: {user_id}")
        
        # تحميل إعدادات المستخدم
        unified_enhanced_system.config_manager.load_user_config(user_id)
        
        welcome_message = f"""
🤖 مرحباً {user_name}!

أهلاً وسهلاً بك في النظام الموحد للتداول

**الميزات المتاحة:**
• 🔑 إدارة مفاتيح API لكل مستخدم
• ⚡ تعديل الرافعة المالية (1x-100x)
• 💰 تعديل مبلغ التداول
• 🏪 التبديل بين Spot و Futures
• 👤 التبديل بين الحساب الحقيقي والتجريبي
• 🏦 دعم متعدد المنصات (Bybit & MEXC)

**للبدء:**
استخدم /enhanced_settings لضبط إعداداتك

**الأوامر المتاحة:**
/enhanced_settings - الإعدادات المحسنة
/config_summary - عرض الإعدادات الحالية
/test_trade - اختبار الصفقات
        """
        
        await update.message.reply_text(welcome_message)
        
        # عرض قائمة الإعدادات المحسنة
        await unified_enhanced_system.bot_interface.show_enhanced_settings_menu(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في معالجة أمر /start: {e}")
        if update.message:
            await update.message.reply_text("حدث خطأ في بدء البوت. يرجى المحاولة مرة أخرى.")

async def show_config_summary(update, context):
    """عرض ملخص الإعدادات"""
    try:
        from enhanced.unified_enhanced_system import unified_enhanced_system
        
        user_id = update.effective_user.id
        config = unified_enhanced_system.config_manager.get_user_config(user_id)
        
        if not config:
            await update.message.reply_text("لم يتم العثور على إعدادات المستخدم. استخدم /start أولاً.")
            return
        
        summary_message = f"""
📊 **ملخص الإعدادات الحالية**

👤 المستخدم: {user_id}
🏦 المنصة: {config.get('exchange', 'bybit').upper()}
🏪 نوع السوق: {config.get('market_type', 'spot').upper()}
👤 نوع الحساب: {config.get('account_type', 'demo').upper()}
💰 مبلغ التداول: {config.get('trade_amount', 0.0):.2f} USDT
⚡ الرافعة: {config.get('leverage', 1)}x
💵 الرصيد التجريبي: {config.get('balance', 0.0):.2f} USDT
🔑 حالة API: {'🟢 متصل' if config.get('api_key') and config.get('api_secret') else '🔴 غير متصل'}
🤖 Auto TP/SL: {'🟢 مفعل' if config.get('auto_tp_sl') else '🔴 معطل'}
🛡️ إدارة المخاطر: {'🟢 مفعلة' if config.get('risk_management') else '🔴 معطلة'}

**لتعديل الإعدادات:**
استخدم /enhanced_settings
        """
        
        await update.message.reply_text(summary_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض ملخص الإعدادات: {e}")
        if update.message:
            await update.message.reply_text("حدث خطأ في عرض الإعدادات.")

async def test_trade(update, context):
    """اختبار الصفقات"""
    try:
        from enhanced.unified_enhanced_system import unified_enhanced_system
        
        user_id = update.effective_user.id
        
        # اختبار تنفيذ صفقة تجريبية
        test_result = await unified_enhanced_system.trade_executor.execute_trade(
            user_id=user_id,
            symbol='BTCUSDT',
            side='buy',
            order_type='Market',
            price=50000.0
        )
        
        if test_result.get('success'):
            await update.message.reply_text(f"✅ اختبار الصفقة نجح!\n\n{test_result.get('message', '')}")
        else:
            await update.message.reply_text(f"❌ اختبار الصفقة فشل!\n\n{test_result.get('message', '')}")
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الصفقة: {e}")
        if update.message:
            await update.message.reply_text("حدث خطأ في اختبار الصفقة.")

async def run_unified_system():
    """تشغيل النظام الموحد"""
    try:
        show_unified_welcome()
        
        # تهيئة النظام الموحد
        init_success = await initialize_unified_system()
        if not init_success:
            logger.error("❌ فشل في تهيئة النظام الموحد")
            return False
        
        # إعداد معالجات Telegram
        application = await setup_telegram_handlers()
        if not application:
            logger.error("❌ فشل في إعداد معالجات Telegram")
            return False
        
        logger.info("✅ النظام الموحد جاهز للتشغيل!")
        print("\n" + "="*80)
        print("✅ النظام الموحد يعمل الآن!")
        print("📱 افتح البوت على Telegram واستخدم /start")
        print("="*80 + "\n")
        
        # تشغيل البوت
        await application.run_polling(allowed_updates=['message', 'callback_query'])
        
        return True
        
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف النظام بواسطة المستخدم")
        print("\n⏹️ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل النظام الموحد: {e}")
        print(f"\n❌ خطأ في تشغيل النظام الموحد: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    try:
        print("🚀 بدء تشغيل النظام الموحد...")
        asyncio.run(run_unified_system())
    except KeyboardInterrupt:
        print("\n👋 وداعاً!")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
