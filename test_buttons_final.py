#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي للأزرار
"""

def test_keyboard():
    """اختبار الكيبورد"""
    print("=" * 60)
    print("اختبار الكيبورد")
    print("=" * 60)
    
    # الكيبورد من الكود
    keyboard = [
        ["الاعدادات", "حالة الحساب"],
        ["الصفقات المفتوحة", "تاريخ التداول"],
        ["المحفظة", "احصائيات"],
        ["الادوات المتقدمة", "نظام الاشارات"]
    ]
    
    print("الكيبورد:")
    for i, row in enumerate(keyboard, 1):
        print(f"  Row {i}: {row}")
    
    # التحقق من الأزرار
    all_buttons = []
    for row in keyboard:
        all_buttons.extend(row)
    
    required_buttons = ["الادوات المتقدمة", "نظام الاشارات"]
    
    print("\nالتحقق من الأزرار:")
    for button in required_buttons:
        if button in all_buttons:
            print(f"  OK: {button}")
        else:
            print(f"  MISSING: {button}")
    
    return True

def test_code():
    """اختبار الكود"""
    print("\n" + "=" * 60)
    print("اختبار الكود")
    print("=" * 60)
    
    try:
        with open('bybit_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن الأزرار
        if "الادوات المتقدمة" in content:
            print("  OK: زر الادوات المتقدمة موجود في الكود")
        else:
            print("  ERROR: زر الادوات المتقدمة غير موجود!")
        
        if "نظام الاشارات" in content:
            print("  OK: زر نظام الاشارات موجود في الكود")
        else:
            print("  ERROR: زر نظام الاشارات غير موجود!")
        
        # البحث عن المعالجات
        if 'if text == "الادوات المتقدمة":' in content:
            print("  OK: معالج الادوات المتقدمة موجود")
        else:
            print("  ERROR: معالج الادوات المتقدمة غير موجود!")
        
        if 'elif text == "نظام الاشارات":' in content:
            print("  OK: معالج نظام الاشارات موجود")
        else:
            print("  ERROR: معالج نظام الاشارات غير موجود!")
    
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")

def test_system():
    """اختبار النظام"""
    print("\n" + "=" * 60)
    print("اختبار النظام")
    print("=" * 60)
    
    try:
        from signal_system_integration import signal_system_integration
        
        is_available = signal_system_integration.is_available()
        print(f"النظام متاح: {is_available}")
        
        if is_available:
            status = signal_system_integration.get_integration_status()
            print(f"الاصدار: {status['version']}")
            print(f"الحالة: {status['status']}")
            print(f"الانظمة: {status['available_systems']}/{status['total_systems']}")
    
    except Exception as e:
        print(f"خطأ: {e}")

def main():
    """الاختبار الرئيسي"""
    print("اختبار الازرار")
    print("=" * 80)
    
    test_keyboard()
    test_code()
    test_system()
    
    print("\n" + "=" * 80)
    print("انتهى الاختبار")
    print("=" * 80)

if __name__ == "__main__":
    main()
