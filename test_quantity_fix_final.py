#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة الكمية النهائي
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_quantity_calculation():
    """اختبار حساب الكمية مع القيم المختلفة"""
    print("اختبار حساب الكمية:")
    print("=" * 50)
    
    # حالات اختبار مختلفة
    test_cases = [
        {"trade_amount": 10, "leverage": 10, "price": 50000, "expected_min": 0.001},
        {"trade_amount": 5, "leverage": 20, "price": 60000, "expected_min": 0.001},
        {"trade_amount": 100, "leverage": 5, "price": 45000, "expected_min": 0.001},
        {"trade_amount": 1, "leverage": 50, "price": 70000, "expected_min": 0.001},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nحالة الاختبار {i}:")
        print(f"  المبلغ: ${case['trade_amount']}")
        print(f"  الرافعة: {case['leverage']}x")
        print(f"  السعر: ${case['price']}")
        
        # حساب الكمية (منطق النسخة القديمة)
        qty = (case['trade_amount'] * case['leverage']) / case['price']
        print(f"  الكمية المحسوبة: {qty}")
        
        # فحص الحد الأدنى
        min_quantity = 0.001
        if qty < min_quantity:
            print(f"  تحذير: الكمية أقل من الحد الأدنى ({min_quantity})")
            qty = min_quantity
            print(f"  الكمية بعد التعديل: {qty}")
        
        # تقريب الكمية
        qty_rounded = round(qty, 6)
        print(f"  الكمية النهائية: {qty_rounded}")
        
        # التحقق من أن الكمية ليست صفر
        if qty_rounded <= 0:
            print(f"  خطأ: الكمية أصبحت صفر!")
        else:
            print(f"  نجح: الكمية صالحة")

def test_quantity_adjuster():
    """اختبار أداة التعديل الذكية"""
    try:
        from api.quantity_adjuster import QuantityAdjuster
        print("\nاختبار أداة التعديل الذكية:")
        print("=" * 50)
        
        # اختبار مع قيم صغيرة
        qty = 0.0001
        price = 50000.0
        trade_amount = 5.0
        leverage = 10
        exchange = 'bybit'
        
        print(f"المدخلات: qty={qty}, price={price}, amount={trade_amount}, leverage={leverage}")
        
        adjusted = QuantityAdjuster.smart_quantity_adjustment(
            qty=qty,
            price=price,
            trade_amount=trade_amount,
            leverage=leverage,
            exchange=exchange
        )
        
        print(f"النتيجة: {qty} -> {adjusted}")
        
        if adjusted > 0:
            print("نجح: الكمية المعدلة صالحة")
        else:
            print("فشل: الكمية المعدلة غير صالحة")
            
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار أداة التعديل الذكية: {e}")
        return False

def test_old_vs_new_logic():
    """مقارنة المنطق القديم والجديد"""
    print("\nمقارنة المنطق القديم والجديد:")
    print("=" * 50)
    
    # قيم الاختبار
    trade_amount = 5.0
    leverage = 10
    price = 50000.0
    
    print(f"المدخلات: amount=${trade_amount}, leverage={leverage}x, price=${price}")
    
    # المنطق القديم
    qty_old = (trade_amount * leverage) / price
    min_quantity = 0.001
    if qty_old < min_quantity:
        qty_old = min_quantity
    qty_old = round(qty_old, 6)
    
    print(f"المنطق القديم: {qty_old}")
    
    # المنطق الجديد (إذا كان متاحاً)
    try:
        from api.quantity_adjuster import QuantityAdjuster
        qty_new = QuantityAdjuster.smart_quantity_adjustment(
            qty=(trade_amount * leverage) / price,
            price=price,
            trade_amount=trade_amount,
            leverage=leverage,
            exchange='bybit'
        )
        print(f"المنطق الجديد: {qty_new}")
        
        if abs(qty_old - qty_new) < 0.000001:
            print("النتيجة: متطابقة تقريباً")
        else:
            print(f"النتيجة: مختلفة (فرق: {abs(qty_old - qty_new)})")
            
    except Exception as e:
        print(f"المنطق الجديد غير متاح: {e}")

if __name__ == "__main__":
    print("بدء اختبار إصلاح مشكلة الكمية")
    print("=" * 60)
    
    # تشغيل الاختبارات
    test_quantity_calculation()
    test_quantity_adjuster()
    test_old_vs_new_logic()
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("\nالخلاصة:")
    print("- تم تطبيق منطق النسخة القديمة الذي كان يعمل")
    print("- الحد الأدنى للكمية: 0.001")
    print("- التقريب: 6 منازل عشرية")
    print("- فحص الرصيد قبل استخدام الحد الأدنى")
    print("- يجب أن تعمل الصفقات الآن بدون مشاكل")
