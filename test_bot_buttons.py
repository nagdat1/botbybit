#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار أزرار البوت
"""

def test_signal_system_integration():
    """اختبار نظام تكامل الإشارات"""
    print("=" * 60)
    print("اختبار نظام تكامل الإشارات")
    print("=" * 60)
    
    try:
        from signal_system_integration import signal_system_integration
        
        # التحقق من توفر النظام
        is_available = signal_system_integration.is_available()
        print(f"النظام متاح: {is_available}")
        
        if is_available:
            # الحصول على حالة النظام
            status = signal_system_integration.get_integration_status()
            print(f"الإصدار: {status['version']}")
            print(f"الحالة: {status['status']}")
            print(f"الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
            
            print("\nالأنظمة المتاحة:")
            for system_name, system_status in status['systems'].items():
                status_text = "متاح" if system_status else "غير متاح"
                print(f"  - {system_name}: {status_text}")
            
            # اختبار معالجة إشارة
            test_signal = {
                'signal': 'buy',
                'symbol': 'BTCUSDT',
                'id': 'TEST_BUTTON_001'
            }
            
            result = signal_system_integration.process_signal(test_signal, 12345)
            print(f"\nمعالجة الإشارة: {'نجح' if result['success'] else 'فشل'}")
            if result['success']:
                print(f"النظام المستخدم: {result.get('system_used', 'غير محدد')}")
        else:
            print("النظام غير متاح")
        
    except Exception as e:
        print(f"خطأ: {e}")
        import traceback
        traceback.print_exc()

def test_button_handlers():
    """اختبار معالجات الأزرار"""
    print("\n" + "=" * 60)
    print("اختبار معالجات الأزرار")
    print("=" * 60)
    
    # قائمة الأزرار المتوقعة
    expected_buttons = [
        "system_stats",
        "signal_stats",
        "system_settings",
        "signal_settings",
        "test_system",
        "refresh_systems",
        "main_menu"
    ]
    
    print("\nالأزرار المتوقعة:")
    for button in expected_buttons:
        print(f"  - {button}")
    
    # التحقق من وجود معالجات في bybit_trading_bot.py
    try:
        with open('bybit_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\nالتحقق من المعالجات:")
        for button in expected_buttons:
            if f'data == "{button}"' in content or f"data == '{button}'" in content:
                print(f"  - {button}: موجود")
            else:
                print(f"  - {button}: غير موجود!")
    
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")

def test_imports():
    """اختبار استيراد الملفات"""
    print("\n" + "=" * 60)
    print("اختبار استيراد الملفات")
    print("=" * 60)
    
    modules_to_test = [
        'signal_system_integration',
        'advanced_signal_manager',
        'advanced_signal_processor',
        'advanced_trade_executor',
        'advanced_portfolio_manager',
        'advanced_risk_manager'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  - {module_name}: نجح")
        except Exception as e:
            print(f"  - {module_name}: فشل ({e})")

def main():
    """الاختبار الرئيسي"""
    print("بدء اختبار أزرار البوت")
    print("=" * 80)
    
    test_imports()
    test_signal_system_integration()
    test_button_handlers()
    
    print("\n" + "=" * 80)
    print("انتهى الاختبار")
    print("=" * 80)

if __name__ == "__main__":
    main()
