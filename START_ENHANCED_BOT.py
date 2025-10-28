#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل النهائي - START HERE
هذا الملف يشغل النظام المحسن مع الحفاظ على النظام الحالي
"""

import logging
import asyncio
import sys

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def show_welcome_message():
    """عرض رسالة الترحيب"""
    print("\n" + "="*80)
    print("🎉 مرحباً بك في النظام المحسن للتداول")
    print("="*80)
    print("\n🎯 الميزات الجديدة:")
    print("  • 🔑 تعديل مفاتيح API من خلال البوت")
    print("  • ⚡ تعديل الرافعة المالية (1x-100x)")
    print("  • 💰 تعديل مبلغ التداول")
    print("  • 🏪 التبديل بين Spot و Futures")
    print("  • 👤 التبديل بين الحساب الحقيقي والتجريبي")
    print("\n🛡️ الميزات المحفوظة:")
    print("  • ✅ آلية التوقيع الحالية محفوظة 100%")
    print("  • ✅ آلية حساب السعر الحالية محفوظة 100%")
    print("  • ✅ جميع الصفقات الحالية تعمل بنفس الطريقة")
    print("\n📱 الأوامر المتاحة في البوت:")
    print("  • /start - بدء البوت")
    print("  • /enhanced_settings - الإعدادات المحسنة")
    print("  • /config_summary - عرض الإعدادات")
    print("  • /test_trade - اختبار الصفقات")
    print("\n" + "="*80)
    print("🚀 بدء التشغيل...\n")

async def main():
    """الدالة الرئيسية"""
    try:
        show_welcome_message()
        
        logger.info("🔄 تهيئة النظام المحسن...")
        
        # استيراد المكونات
        try:
            from flexible_config_manager import flexible_config_manager
            logger.info("✅ تم تحميل مدير الإعدادات المرن")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل مدير الإعدادات: {e}")
            return False
        
        try:
            from enhanced_bot_interface import enhanced_bot_interface
            logger.info("✅ تم تحميل واجهة البوت المحسنة")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل واجهة البوت: {e}")
            return False
        
        try:
            from enhanced_trade_executor import enhanced_trade_executor
            logger.info("✅ تم تحميل منفذ الصفقات المحسن")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل منفذ الصفقات: {e}")
            return False
        
        try:
            from integrated_trading_system import integrated_trading_system
            logger.info("✅ تم تحميل النظام المتكامل")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل النظام المتكامل: {e}")
            return False
        
        # تهيئة المكونات
        logger.info("🔧 تهيئة المكونات...")
        await flexible_config_manager.initialize_system()
        await enhanced_bot_interface.initialize_interface()
        await enhanced_trade_executor.initialize_executor()
        await integrated_trading_system.initialize_system()
        
        # تشغيل النظام المحسن
        logger.info("🚀 تشغيل النظام المحسن...")
        await integrated_trading_system.run_enhanced_system()
        
        logger.info("✅ النظام المحسن يعمل بنجاح!")
        print("\n" + "="*80)
        print("✅ النظام المحسن يعمل الآن!")
        print("📱 افتح البوت على Telegram واستخدم /start")
        print("="*80 + "\n")
        
        # إبقاء النظام يعمل
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف النظام بواسطة المستخدم")
        print("\n⏹️ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        print(f"\n❌ خطأ في التشغيل: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 وداعاً!")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

