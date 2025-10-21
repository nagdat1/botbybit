#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض الأزرار في البوت
"""

def test_keyboard_buttons():
    """اختبار أزرار الكيبورد"""
    print("=" * 60)
    print("اختبار أزرار الكيبورد")
    print("=" * 60)
    
    # محاكاة الكيبورد من الكود
    keyboard = [
        ["⚙️ الإعدادات", "📊 حالة الحساب"],
        ["🔄 الصفقات المفتوحة", "📈 تاريخ التداول"],
        ["💰 المحفظة", "📊 إحصائيات"],
        ["🔧 الأدوات المتقدمة", "🎯 نظام الإشارات"]
    ]
    
    print("الكيبورد المحدد:")
    for i, row in enumerate(keyboard, 1):
        print(f"  الصف {i}: {row}")
    
    # التحقق من وجود الأزرار المطلوبة
    all_buttons = []
    for row in keyboard:
        all_buttons.extend(row)
    
    required_buttons = ["🔧 الأدوات المتقدمة", "🎯 نظام الإشارات"]
    
    print(f"\nالتحقق من الأزرار المطلوبة:")
    for button in required_buttons:
        if button in all_buttons:
            print(f"  ✅ {button} - موجود")
        else:
            print(f"  ❌ {button} - غير موجود!")
    
    return required_buttons

def test_message_handling():
    """اختبار معالجة الرسائل"""
    print("\n" + "=" * 60)
    print("اختبار معالجة الرسائل")
    print("=" * 60)
    
    # محاكاة النصوص المتوقعة
    test_messages = [
        "🔧 الأدوات المتقدمة",
        "🎯 نظام الإشارات"
    ]
    
    print("النصوص المتوقعة:")
    for msg in test_messages:
        print(f"  - '{msg}'")
    
    # التحقق من وجود معالجات في الكود
    try:
        with open('bybit_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\nالتحقق من المعالجات:")
        for msg in test_messages:
            if f'if text == "{msg}":' in content:
                print(f"  ✅ معالج لـ '{msg}' - موجود")
            else:
                print(f"  ❌ معالج لـ '{msg}' - غير موجود!")
    
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")

def test_signal_system():
    """اختبار نظام الإشارات"""
    print("\n" + "=" * 60)
    print("اختبار نظام الإشارات")
    print("=" * 60)
    
    try:
        from signal_system_integration import signal_system_integration
        
        is_available = signal_system_integration.is_available()
        print(f"نظام تكامل الإشارات متاح: {is_available}")
        
        if is_available:
            status = signal_system_integration.get_integration_status()
            print(f"الإصدار: {status['version']}")
            print(f"الحالة: {status['status']}")
            print(f"الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
            
            print("الأنظمة:")
            for system_name, system_status in status['systems'].items():
                status_text = "متاح" if system_status else "غير متاح"
                print(f"  - {system_name}: {status_text}")
        else:
            print("النظام غير متاح")
    
    except Exception as e:
        print(f"خطأ في اختبار نظام الإشارات: {e}")

def main():
    """الاختبار الرئيسي"""
    print("اختبار عرض الأزرار في البوت")
    print("=" * 80)
    
    test_keyboard_buttons()
    test_message_handling()
    test_signal_system()
    
    print("\n" + "=" * 80)
    print("انتهى الاختبار")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("ملاحظات مهمة:")
    print("=" * 80)
    print("1. إذا كانت الأزرار موجودة في الكود ولكن لا تظهر في البوت:")
    print("   - تأكد من استخدام البوت الصحيح")
    print("   - جرب إرسال /start مرة أخرى")
    print("   - تأكد من أن البوت يعمل على Railway")
    print()
    print("2. إذا ظهرت الأزرار ولكن لا تعمل عند الضغط:")
    print("   - تحقق من سجل Railway للأخطاء")
    print("   - تأكد من أن جميع الملفات موجودة")
    print()
    print("3. للاختبار:")
    print("   - افتح البوت")
    print("   - اكتب /start")
    print("   - اضغط على '🔧 الأدوات المتقدمة'")
    print("   - اضغط على '🎯 نظام الإشارات'")

if __name__ == "__main__":
    main()
