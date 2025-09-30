#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بدء سريع للبوت الذكي
للتشغيل السريع والاختبار
"""

import asyncio
import logging
import sys
import os

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل المبسط
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_welcome():
    """طباعة رسالة الترحيب"""
    welcome = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 البوت الذكي للتداول على Bybit 🚀                ║
║                                                              ║
║  ✨ البدء السريع:                                            ║
║  1. تأكد من تحديث config.py بمفاتيحك                        ║
║  2. شغل البوت: python run_smart_bot.py                      ║
║  3. ابدأ بـ /start في التليجرام                              ║
║  4. اربط مفاتيح API باستخدام زر "🔗 الربط"                  ║
║                                                              ║
║  🔧 للاختبار: python test_smart_bot.py                       ║
║  📖 للتوثيق: README_SMART_BOT.md                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(welcome)

def check_config():
    """فحص الإعدادات"""
    try:
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_telegram_token_here":
            logger.error("❌ يرجى تحديث TELEGRAM_TOKEN في config.py")
            return False
        
        if not ADMIN_USER_ID or ADMIN_USER_ID == 0:
            logger.error("❌ يرجى تحديث ADMIN_USER_ID في config.py")
            return False
        
        logger.info("✅ الإعدادات صحيحة")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في فحص الإعدادات: {e}")
        return False

async def quick_test():
    """اختبار سريع للمكونات الأساسية"""
    try:
        logger.info("🔍 اختبار سريع للمكونات...")
        
        # اختبار قاعدة البيانات
        from database import db_manager
        db_manager.init_database()
        logger.info("✅ قاعدة البيانات جاهزة")
        
        # اختبار مدير المستخدمين
        from user_manager import user_manager
        user_env = user_manager.get_user_environment(99999)
        logger.info("✅ مدير المستخدمين جاهز")
        
        # اختبار مدير API
        from api_manager import api_manager
        logger.info("✅ مدير API جاهز")
        
        # اختبار مدير الصفقات
        from order_manager import order_manager
        logger.info("✅ مدير الصفقات جاهز")
        
        # اختبار مدير الواجهة
        from ui_manager import ui_manager
        logger.info("✅ مدير الواجهة جاهز")
        
        # اختبار مدير الأمان
        from security_manager import security_manager
        logger.info("✅ مدير الأمان جاهز")
        
        # اختبار تحكم البوت
        from bot_controller import bot_controller
        logger.info("✅ تحكم البوت جاهز")
        
        logger.info("🎉 جميع المكونات جاهزة!")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في الاختبار السريع: {e}")
        return False

def show_usage():
    """عرض كيفية الاستخدام"""
    usage = """
📱 كيفية استخدام البوت:

1. 🔗 الربط:
   - اضغط على "🔗 الربط"
   - أدخل مفاتيح API: API_KEY API_SECRET

2. ⚙️ الإعدادات:
   - اضغط على "⚙️ الإعدادات"
   - اختر الإعدادات المطلوبة

3. 💰 التداول:
   - /buy BTCUSDT 0.001
   - /sell ETHUSDT 0.1
   - /balance

4. 📊 إدارة الصفقات:
   - اضغط على "📊 الصفقات المفتوحة"
   - اختر الصفقة لإدارتها
   - أضف TP/SL أو أغلق جزئياً

5. 📈 المتابعة:
   - اضغط على "📈 تاريخ التداول"
   - اضغط على "📊 الإحصائيات"

🔧 الأوامر المتاحة:
• /start - بدء البوت
• /balance - عرض الرصيد
• /buy SYMBOL QUANTITY - شراء
• /sell SYMBOL QUANTITY - بيع
• /help - المساعدة

🛡️ الحماية:
• كل مستخدم له بيئة منفصلة
• لا يمكن الوصول لبيانات الآخرين
• نظام حماية من الأنشطة المشبوهة
• مراقبة تلقائية للصفقات
    """
    print(usage)

async def main():
    """الدالة الرئيسية"""
    try:
        print_welcome()
        
        # فحص الإعدادات
        if not check_config():
            logger.error("❌ يرجى إصلاح الإعدادات أولاً")
            return
        
        # اختبار سريع
        if await quick_test():
            logger.info("🚀 البوت جاهز للتشغيل!")
            show_usage()
            
            # سؤال المستخدم
            choice = input("\nهل تريد تشغيل البوت الآن؟ (y/n): ").lower().strip()
            
            if choice in ['y', 'yes', 'نعم', 'ن']:
                logger.info("🚀 بدء تشغيل البوت...")
                
                # تشغيل البوت الذكي
                from smart_trading_bot import smart_bot
                await smart_bot.start()
            else:
                logger.info("👋 يمكنك تشغيل البوت لاحقاً باستخدام: python run_smart_bot.py")
        else:
            logger.error("❌ يرجى إصلاح الأخطاء أولاً")
            
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
