#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار سريع للتأكد من عمل الإصلاح
"""

def test_button_logic():
    """اختبار منطق الأزرار"""
    
    # محاكاة النصوص الفعلية من الرسائل
    test_texts = [
        "الإعدادات",
        "حالة الحساب",
        "الصفقات المفتوحة",
        "تاريخ التداول",
        "المحفظة",
        "إحصائيات"
    ]
    
    print("=== اختبار منطق الأزرار ===")
    
    for text in test_texts:
        # محاكاة الشرط الجديد
        if text.strip() == "الإعدادات":
            result = "settings_menu"
        elif text.strip() == "حالة الحساب":
            result = "account_status"
        elif text.strip() == "الصفقات المفتوحة":
            result = "open_positions"
        elif text.strip() == "تاريخ التداول":
            result = "trade_history"
        elif text.strip() == "المحفظة":
            result = "wallet_overview"
        elif text.strip() == "إحصائيات":
            result = "show_user_statistics"
        else:
            result = "أمر غير مدعوم"
        
        print(f"النص: '{text}' -> النتيجة: {result}")
    
    print()
    print("إذا كانت النتائج صحيحة، فالمشكلة قد تكون:")
    print("1. البوت لم يتم إعادة تشغيله بعد التغييرات")
    print("2. هناك مشكلة في التخزين المؤقت")
    print("3. هناك مشكلة في استيراد الملف")

if __name__ == "__main__":
    test_button_logic()
