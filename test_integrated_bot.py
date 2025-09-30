#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البوت المتكامل
للتأكد من عمل جميع المكونات بشكل صحيح
"""

import asyncio
import logging
import sys
import os

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_integrated_system():
    """اختبار النظام المتكامل"""
    try:
        logger.info("🔍 اختبار النظام المتكامل...")
        
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
        
        # اختبار النظام القديم
        from bybit_trading_bot import trading_bot
        logger.info("✅ النظام القديم جاهز")
        
        # اختبار السيرفر الويب
        from web_server import WebServer
        logger.info("✅ السيرفر الويب جاهز")
        
        logger.info("🎉 جميع المكونات جاهزة!")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار النظام المتكامل: {e}")
        return False

async def test_railway_compatibility():
    """اختبار التوافق مع Railway"""
    try:
        logger.info("🔍 اختبار التوافق مع Railway...")
        
        # فحص متغيرات البيئة
        port = os.environ.get('PORT', '5000')
        logger.info(f"✅ المنفذ: {port}")
        
        # فحص متغيرات Railway
        railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        if railway_url:
            logger.info(f"✅ Railway URL: {railway_url}")
        else:
            logger.info("ℹ️ Railway URL غير متاح (تشغيل محلي)")
        
        # فحص الإعدادات
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        if TELEGRAM_TOKEN and TELEGRAM_TOKEN != "your_telegram_token_here":
            logger.info("✅ TELEGRAM_TOKEN محدد")
        else:
            logger.warning("⚠️ TELEGRAM_TOKEN غير محدد")
        
        if ADMIN_USER_ID and ADMIN_USER_ID != 0:
            logger.info("✅ ADMIN_USER_ID محدد")
        else:
            logger.warning("⚠️ ADMIN_USER_ID غير محدد")
        
        logger.info("✅ اختبار التوافق مع Railway نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار التوافق مع Railway: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    try:
        logger.info("🚀 بدء اختبار البوت المتكامل...")
        
        # اختبار النظام المتكامل
        system_ok = await test_integrated_system()
        
        # اختبار التوافق مع Railway
        railway_ok = await test_railway_compatibility()
        
        # النتائج النهائية
        if system_ok and railway_ok:
            logger.info("🎉 جميع الاختبارات نجحت!")
            logger.info("🚀 يمكنك الآن تشغيل البوت باستخدام:")
            logger.info("python run_with_server.py")
        else:
            logger.error("❌ بعض الاختبارات فشلت")
            if not system_ok:
                logger.error("❌ مشاكل في النظام المتكامل")
            if not railway_ok:
                logger.error("❌ مشاكل في التوافق مع Railway")
            
    except Exception as e:
        logger.error(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
