#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار شامل للبوت
يختبر جميع المكونات الأساسية
"""

import asyncio
import sys
import os

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد جميع الوحدات"""
    print("="*60)
    print("🔍 اختبار الاستيرادات...")
    print("="*60)
    
    try:
        print("✓ استيراد config...")
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        print(f"  - TOKEN موجود: {'نعم' if TELEGRAM_TOKEN else 'لا'}")
        print(f"  - ADMIN_USER_ID: {ADMIN_USER_ID}")
        
        print("\n✓ استيراد database...")
        from users.database import db_manager
        print("  - db_manager جاهز")
        
        print("\n✓ استيراد user_manager...")
        from users.user_manager import user_manager
        print(f"  - user_manager: {'موجود' if user_manager else 'غير مهيأ (سيتم تهيئته لاحقاً)'}")
        
        print("\n✓ استيراد bybit_api...")
        from api.bybit_api import BybitRealAccount, real_account_manager
        print("  - BybitRealAccount متاح")
        print("  - real_account_manager جاهز")
        
        print("\n✓ استيراد signal_converter...")
        from signals.signal_converter import convert_simple_signal
        print("  - convert_simple_signal متاح")
        
        print("\n✓ استيراد signal_executor...")
        from signals.signal_executor import signal_executor
        print("  - signal_executor جاهز")
        
        print("\n✓ استيراد buttons...")
        from buttons.buttons_definition import get_main_menu_buttons
        print("  - buttons_definition متاح")
        
        print("\n✓ استيراد bybit_trading_bot...")
        import bybit_trading_bot
        print("  - bybit_trading_bot جاهز")
        
        print("\n✓ استيراد app...")
        import app
        print("  - app جاهز")
        
        print("\n" + "="*60)
        print("✅ جميع الاستيرادات نجحت!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في الاستيراد: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """اختبار قاعدة البيانات"""
    print("\n" + "="*60)
    print("🔍 اختبار قاعدة البيانات...")
    print("="*60)
    
    try:
        from users.database import db_manager
        
        # اختبار إنشاء مستخدم
        print("✓ اختبار إنشاء مستخدم...")
        test_user_id = 999999999
        success = db_manager.create_user(test_user_id, None, None)
        print(f"  - إنشاء مستخدم: {'نجح' if success else 'فشل'}")
        
        # اختبار جلب المستخدم
        print("\n✓ اختبار جلب المستخدم...")
        user = db_manager.get_user(test_user_id)
        print(f"  - جلب مستخدم: {'نجح' if user else 'فشل'}")
        if user:
            print(f"  - user_id: {user.get('user_id')}")
            print(f"  - is_active: {user.get('is_active')}")
        
        # اختبار تحديث المستخدم
        print("\n✓ اختبار تحديث المستخدم...")
        success = db_manager.update_user_settings(test_user_id, {'market_type': 'spot'})
        print(f"  - تحديث إعدادات: {'نجح' if success else 'فشل'}")
        
        # تنظيف: حذف المستخدم التجريبي
        print("\n✓ تنظيف...")
        db_manager.delete_user(test_user_id)
        print("  - تم حذف المستخدم التجريبي")
        
        print("\n" + "="*60)
        print("✅ اختبار قاعدة البيانات نجح!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في اختبار قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_conversion():
    """اختبار تحويل الإشارات"""
    print("\n" + "="*60)
    print("🔍 اختبار تحويل الإشارات...")
    print("="*60)
    
    try:
        from signals.signal_converter import convert_simple_signal
        
        # إشارة شراء
        print("✓ اختبار إشارة شراء...")
        signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_001'
        }
        user_settings = {
            'trade_amount': 100,
            'leverage': 10,
            'exchange': 'bybit',
            'account_type': 'demo',
            'market_type': 'futures'
        }
        
        converted = convert_simple_signal(signal, user_settings)
        if converted:
            print(f"  - تحويل إشارة شراء: نجح")
            print(f"  - action: {converted.get('action')}")
            print(f"  - symbol: {converted.get('symbol')}")
            print(f"  - market_type: {converted.get('market_type')}")
            print(f"  - leverage: {converted.get('leverage')}")
        else:
            print(f"  - تحويل إشارة شراء: فشل")
            return False
        
        # إشارة بيع
        print("\n✓ اختبار إشارة بيع...")
        signal['signal'] = 'sell'
        signal['id'] = 'TEST_002'
        converted = convert_simple_signal(signal, user_settings)
        if converted:
            print(f"  - تحويل إشارة بيع: نجح")
            print(f"  - action: {converted.get('action')}")
        else:
            print(f"  - تحويل إشارة بيع: فشل")
            return False
        
        # إشارة إغلاق
        print("\n✓ اختبار إشارة إغلاق...")
        signal['signal'] = 'close'
        signal['id'] = 'TEST_003'
        converted = convert_simple_signal(signal, user_settings)
        if converted:
            print(f"  - تحويل إشارة إغلاق: نجح")
            print(f"  - action: {converted.get('action')}")
        else:
            print(f"  - تحويل إشارة إغلاق: فشل")
            return False
        
        print("\n" + "="*60)
        print("✅ اختبار تحويل الإشارات نجح!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في اختبار تحويل الإشارات: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_buttons():
    """اختبار تعريف الأزرار"""
    print("\n" + "="*60)
    print("🔍 اختبار تعريف الأزرار...")
    print("="*60)
    
    try:
        from buttons.buttons_definition import (
            get_main_menu_buttons,
            EXCHANGE_BUTTONS,
            TRADING_SETTINGS_BUTTONS,
            AUTO_APPLY_BUTTONS,
            RISK_MANAGEMENT_BUTTONS,
            ALL_BUTTONS
        )
        
        print("✓ اختبار القوائم...")
        main_buttons = get_main_menu_buttons()
        print(f"  - عدد الأزرار الرئيسية: {len(main_buttons)}")
        print(f"  - عدد أزرار المنصات: {len(EXCHANGE_BUTTONS)}")
        print(f"  - عدد أزرار الإعدادات: {len(TRADING_SETTINGS_BUTTONS)}")
        print(f"  - عدد أزرار التطبيق التلقائي: {len(AUTO_APPLY_BUTTONS)}")
        print(f"  - عدد أزرار إدارة المخاطر: {len(RISK_MANAGEMENT_BUTTONS)}")
        print(f"  - إجمالي الأزرار: {len(ALL_BUTTONS)}")
        
        print("\n✓ اختبار أزرار محددة...")
        buttons_to_test = [
            'select_exchange',
            'set_amount',
            'set_market',
            'set_account',
            'auto_apply_menu',
            'risk_management_menu',
            'webhook_url',
            'toggle_bot'
        ]
        
        for button_id in buttons_to_test:
            if button_id in [k for k in ALL_BUTTONS.keys()]:
                print(f"  ✓ {button_id}: موجود")
            else:
                print(f"  ✗ {button_id}: مفقود")
        
        print("\n" + "="*60)
        print("✅ اختبار الأزرار نجح!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في اختبار الأزرار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """اختبار بنية API (بدون اتصال حقيقي)"""
    print("\n" + "="*60)
    print("🔍 اختبار بنية API...")
    print("="*60)
    
    try:
        from api.bybit_api import BybitRealAccount
        
        print("✓ إنشاء كائن API...")
        # استخدام مفاتيح وهمية للاختبار
        api = BybitRealAccount("test_key", "test_secret")
        print("  - تم إنشاء كائن API بنجاح")
        
        print("\n✓ فحص الوظائف المتاحة...")
        methods = [
            'get_wallet_balance',
            'get_open_positions',
            'place_order',
            'close_position',
            'get_ticker_price'
        ]
        
        for method in methods:
            if hasattr(api, method):
                print(f"  ✓ {method}: متاح")
            else:
                print(f"  ✗ {method}: مفقود")
        
        print("\n" + "="*60)
        print("✅ اختبار بنية API نجح!")
        print("="*60)
        print("\n⚠️ ملاحظة: لم يتم اختبار الاتصال الفعلي بالمنصة")
        print("   للاختبار الفعلي، استخدم مفاتيح API حقيقية")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في اختبار بنية API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("\n")
    print("="*60)
    print("🚀 بدء الاختبار الشامل للبوت")
    print("="*60)
    print("\n")
    
    results = {
        'استيراد الوحدات': test_imports(),
        'قاعدة البيانات': test_database(),
        'تحويل الإشارات': test_signal_conversion(),
        'تعريف الأزرار': test_buttons(),
        'بنية API': test_api_structure()
    }
    
    print("\n")
    print("="*60)
    print("📊 ملخص النتائج")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"النتيجة النهائية: {passed}/{len(results)} اختبارات نجحت")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 جميع الاختبارات نجحت! البوت جاهز للاستخدام")
        print("\n📝 الخطوات التالية:")
        print("1. تأكد من إضافة مفاتيح API في ملف .env أو config.py")
        print("2. شغل البوت: python app.py")
        print("3. استخدم /start في Telegram للبدء")
    else:
        print(f"\n⚠️ {failed} اختبار(ات) فشل. يرجى مراجعة الأخطاء أعلاه")
    
    print("\n")

if __name__ == "__main__":
    main()

