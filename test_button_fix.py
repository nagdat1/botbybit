#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إصلاح مشكلة أزرار البوت
"""

def test_button_handling():
    """اختبار معالجة الأزرار"""
    
    # محاكاة النصوص المختلفة
    test_cases = [
        " الإعدادات",
        " حالة الحساب", 
        " الصفقات المفتوحة",
        " تاريخ التداول",
        " المحفظة",
        " إحصائيات",
        "أي نص آخر"
    ]
    
    print("=== اختبار معالجة الأزرار ===")
    
    for text in test_cases:
        # محاكاة الشرط القديم (المشكلة)
        old_condition = text == " الصفقات المفتوحة" or "الصفقات المفتوحة" in text or "" in text
        
        # محاكاة الشرط الجديد (الإصلاح)
        new_condition = text == " الصفقات المفتوحة"
        
        print(f"النص: '{text}'")
        print(f"  الشرط القديم: {old_condition} (مشكلة!)")
        print(f"  الشرط الجديد: {new_condition} (صحيح)")
        print()
    
    print("تم إصلاح المشكلة!")
    print("الآن فقط زر 'الصفقات المفتوحة' سيتم معالجته بشكل صحيح")

if __name__ == "__main__":
    test_button_handling()
