#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار فحص النص الفعلي للأزرار
"""

def analyze_text():
    """تحليل النص الفعلي للأزرار"""
    
    # النصوص المتوقعة من الكود
    expected_texts = [
        " الإعدادات",
        " حالة الحساب", 
        " الصفقات المفتوحة",
        " تاريخ التداول",
        " المحفظة",
        " إحصائيات"
    ]
    
    # النصوص الفعلية من الرسائل
    actual_texts = [
        "الإعدادات",
        "حالة الحساب"
    ]
    
    print("=== تحليل النصوص ===")
    print()
    
    print("النصوص المتوقعة من الكود:")
    for i, text in enumerate(expected_texts, 1):
        print(f"{i}. '{text}' (الطول: {len(text)}, البايتات: {text.encode('utf-8')})")
    
    print()
    print("النصوص الفعلية من الرسائل:")
    for i, text in enumerate(actual_texts, 1):
        print(f"{i}. '{text}' (الطول: {len(text)}, البايتات: {text.encode('utf-8')})")
    
    print()
    print("=== مقارنة ===")
    
    for expected in expected_texts:
        for actual in actual_texts:
            if expected.strip() == actual.strip():
                print(f"تطابق: '{expected}' == '{actual}'")
            else:
                print(f"عدم تطابق: '{expected}' != '{actual}'")
                print(f"   المتوقع: {expected.encode('utf-8')}")
                print(f"   الفعلي: {actual.encode('utf-8')}")
    
    print()
    print("=== الحل المقترح ===")
    print("يجب إضافة معالجة للنصوص بدون المسافات الإضافية:")
    print("elif text.strip() == 'الإعدادات':")
    print("elif text.strip() == 'حالة الحساب':")
    print("إلخ...")

if __name__ == "__main__":
    analyze_text()
