#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار البوت الذكي
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

async def test_database():
    """اختبار قاعدة البيانات"""
    try:
        from database import db_manager
        
        logger.info("🔍 اختبار قاعدة البيانات...")
        
        # اختبار إضافة مستخدم
        success = db_manager.add_user(12345, "test_user", "Test", "User")
        logger.info(f"✅ إضافة مستخدم: {success}")
        
        # اختبار الحصول على المستخدم
        user = db_manager.get_user(12345)
        logger.info(f"✅ الحصول على المستخدم: {user is not None}")
        
        # اختبار إضافة صفقة
        success = db_manager.add_order("test_order_123", 12345, "BTCUSDT", "buy", 50000.0, 0.001)
        logger.info(f"✅ إضافة صفقة: {success}")
        
        # اختبار الحصول على الصفقات
        orders = db_manager.get_user_orders(12345)
        logger.info(f"✅ الحصول على الصفقات: {len(orders)} صفقة")
        
        logger.info("✅ اختبار قاعدة البيانات نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        return False

async def test_user_manager():
    """اختبار مدير المستخدمين"""
    try:
        from user_manager import user_manager
        
        logger.info("🔍 اختبار مدير المستخدمين...")
        
        # اختبار الحصول على بيئة المستخدم
        user_env = user_manager.get_user_environment(12345)
        logger.info(f"✅ بيئة المستخدم: {user_env is not None}")
        
        # اختبار الإعدادات
        settings = user_env.get_settings()
        logger.info(f"✅ الإعدادات: {len(settings)} إعداد")
        
        # اختبار الرصيد
        balance = user_env.get_balance_info()
        logger.info(f"✅ الرصيد: {balance['balance']}")
        
        logger.info("✅ اختبار مدير المستخدمين نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار مدير المستخدمين: {e}")
        return False

async def test_api_manager():
    """اختبار مدير API"""
    try:
        from api_manager import api_manager
        
        logger.info("🔍 اختبار مدير API...")
        
        # اختبار إضافة مفاتيح API وهمية
        success = api_manager.add_user_api(12345, "test_key", "test_secret")
        logger.info(f"✅ إضافة مفاتيح API: {success}")
        
        # اختبار التحقق من وجود API
        has_api = api_manager.has_user_api(12345)
        logger.info(f"✅ وجود مفاتيح API: {has_api}")
        
        # اختبار الحصول على مثيل API
        api_instance = api_manager.get_user_api(12345)
        logger.info(f"✅ مثيل API: {api_instance is not None}")
        
        logger.info("✅ اختبار مدير API نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار مدير API: {e}")
        return False

async def test_order_manager():
    """اختبار مدير الصفقات"""
    try:
        from order_manager import order_manager
        
        logger.info("🔍 اختبار مدير الصفقات...")
        
        # اختبار إنشاء صفقة
        success, order_id = order_manager.create_order(
            user_id=12345,
            symbol="BTCUSDT",
            side="buy",
            quantity=0.001,
            price=50000.0,
            leverage=1
        )
        logger.info(f"✅ إنشاء صفقة: {success}, ID: {order_id}")
        
        # اختبار الحصول على صفقات المستخدم
        orders = order_manager.get_user_orders(12345)
        logger.info(f"✅ صفقات المستخدم: {len(orders)} صفقة")
        
        # اختبار إضافة هدف ربح
        if success:
            tp_success = order_manager.add_take_profit(order_id, 2.0, 50)
            logger.info(f"✅ إضافة هدف ربح: {tp_success}")
        
        logger.info("✅ اختبار مدير الصفقات نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار مدير الصفقات: {e}")
        return False

async def test_ui_manager():
    """اختبار مدير الواجهة"""
    try:
        from ui_manager import ui_manager
        
        logger.info("🔍 اختبار مدير الواجهة...")
        
        # اختبار لوحة المفاتيح الرئيسية
        keyboard = ui_manager.get_main_menu_keyboard(12345)
        logger.info(f"✅ لوحة المفاتيح الرئيسية: {keyboard is not None}")
        
        # اختبار لوحة مفاتيح الإعدادات
        settings_keyboard = ui_manager.get_settings_keyboard(12345)
        logger.info(f"✅ لوحة مفاتيح الإعدادات: {settings_keyboard is not None}")
        
        # اختبار تنسيق معلومات المستخدم
        user_info = ui_manager.format_user_info(12345)
        logger.info(f"✅ معلومات المستخدم: {len(user_info)} حرف")
        
        logger.info("✅ اختبار مدير الواجهة نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار مدير الواجهة: {e}")
        return False

async def test_security_manager():
    """اختبار مدير الأمان"""
    try:
        from security_manager import security_manager
        
        logger.info("🔍 اختبار مدير الأمان...")
        
        # اختبار المصادقة
        authenticated, message = security_manager.authenticate_user(12345, "test")
        logger.info(f"✅ المصادقة: {authenticated}, {message}")
        
        # اختبار التحقق من الوصول
        has_access = security_manager.validate_user_access(12345, "user_data")
        logger.info(f"✅ صلاحية الوصول: {has_access}")
        
        # اختبار كشف النشاط المشبوه
        suspicious = security_manager.detect_suspicious_activity(
            12345, "rapid_requests", {'count': 5}
        )
        logger.info(f"✅ كشف النشاط المشبوه: {suspicious}")
        
        logger.info("✅ اختبار مدير الأمان نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار مدير الأمان: {e}")
        return False

async def test_bot_controller():
    """اختبار تحكم البوت"""
    try:
        from bot_controller import bot_controller
        
        logger.info("🔍 اختبار تحكم البوت...")
        
        # اختبار حالة البوت للمستخدم
        status = bot_controller.get_user_bot_status(12345)
        logger.info(f"✅ حالة البوت: {status}")
        
        # اختبار إمكانية التداول
        can_trade = bot_controller.can_user_trade(12345)
        logger.info(f"✅ إمكانية التداول: {can_trade}")
        
        # اختبار الحصول على حالة النظام
        system_status = bot_controller.get_system_status()
        logger.info(f"✅ حالة النظام: {system_status['global_status']}")
        
        logger.info("✅ اختبار تحكم البوت نجح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار تحكم البوت: {e}")
        return False

async def run_all_tests():
    """تشغيل جميع الاختبارات"""
    logger.info("🚀 بدء اختبار البوت الذكي...")
    
    tests = [
        ("قاعدة البيانات", test_database),
        ("مدير المستخدمين", test_user_manager),
        ("مدير API", test_api_manager),
        ("مدير الصفقات", test_order_manager),
        ("مدير الواجهة", test_ui_manager),
        ("مدير الأمان", test_security_manager),
        ("تحكم البوت", test_bot_controller),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"اختبار {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار {test_name}: {e}")
            results.append((test_name, False))
    
    # عرض النتائج النهائية
    logger.info(f"\n{'='*50}")
    logger.info("النتائج النهائية")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nالنتيجة الإجمالية: {passed}/{total} اختبار نجح")
    
    if passed == total:
        logger.info("🎉 جميع الاختبارات نجحت! البوت جاهز للاستخدام")
    else:
        logger.warning(f"⚠️ {total - passed} اختبار فشل. يرجى مراجعة الأخطاء")
    
    return passed == total

async def main():
    """الدالة الرئيسية"""
    try:
        success = await run_all_tests()
        
        if success:
            logger.info("\n🚀 يمكنك الآن تشغيل البوت باستخدام:")
            logger.info("python run_smart_bot.py")
        else:
            logger.error("\n❌ يرجى إصلاح الأخطاء قبل تشغيل البوت")
            
    except Exception as e:
        logger.error(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
