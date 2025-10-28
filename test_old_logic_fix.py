#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المنطق القديم المطبق
"""

def test_old_quantity_logic():
    """اختبار منطق حساب الكمية القديم"""
    print("اختبار منطق حساب الكمية القديم:")
    print("=" * 50)
    
    # حالات اختبار مختلفة
    test_cases = [
        {"trade_amount": 10, "leverage": 10, "price": 50000, "market_type": "futures"},
        {"trade_amount": 5, "leverage": 20, "price": 60000, "market_type": "futures"},
        {"trade_amount": 100, "leverage": 5, "price": 45000, "market_type": "futures"},
        {"trade_amount": 1, "leverage": 50, "price": 70000, "market_type": "futures"},
        {"trade_amount": 0.5, "leverage": 100, "price": 80000, "market_type": "futures"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nحالة الاختبار {i}:")
        print(f"  المبلغ: ${case['trade_amount']}")
        print(f"  الرافعة: {case['leverage']}x")
        print(f"  السعر: ${case['price']}")
        print(f"  نوع السوق: {case['market_type']}")
        
        # حساب الكمية (منطق النسخة القديمة)
        if case['market_type'] == 'futures':
            qty = (case['trade_amount'] * case['leverage']) / case['price']
        else:
            qty = case['trade_amount'] / case['price']
        
        print(f"  الكمية المحسوبة: {qty}")
        
        # ضمان الحد الأدنى للكمية (منطق النسخة القديمة)
        min_quantity = 0.001  # الحد الأدنى لـ Bybit
        
        if qty < min_quantity:
            print(f"  تحذير: الكمية أقل من الحد الأدنى ({min_quantity})")
            qty = min_quantity
            print(f"  الكمية بعد التعديل: {qty}")
        
        # تقريب الكمية حسب دقة الرمز (منطق النسخة القديمة)
        qty = round(qty, 6)
        print(f"  الكمية بعد التقريب: {qty}")
        
        # التأكد النهائي من أن الكمية ليست صفر
        if qty <= 0:
            print(f"  خطأ: الكمية أصبحت صفر!")
            qty = min_quantity
            print(f"  تم إصلاحها إلى: {qty}")
        else:
            print(f"  ✅ نجح: الكمية صالحة")
        
        print(f"  النتيجة النهائية: {qty}")

def test_round_quantity_function():
    """اختبار دالة تقريب الكمية الجديدة"""
    print("\nاختبار دالة تقريب الكمية الجديدة:")
    print("=" * 50)
    
    # محاكاة دالة round_quantity
    def round_quantity(qty, category, symbol):
        """تقريب الكمية - المنطق القديم البسيط الذي كان يعمل"""
        try:
            # تحويل إلى float إذا كان string
            if isinstance(qty, str):
                qty = float(qty)
            
            # ضمان الحد الأدنى للكمية (منطق النسخة القديمة)
            min_quantity = 0.001  # الحد الأدنى لـ Bybit
            
            if qty < min_quantity:
                print(f"الكمية صغيرة جداً: {qty}, تم تعديلها إلى الحد الأدنى: {min_quantity}")
                qty = min_quantity
            
            # تقريب الكمية حسب دقة الرمز (منطق النسخة القديمة)
            rounded_qty = round(qty, 6)
            
            # التأكد من أن الكمية ليست صفر
            if rounded_qty <= 0:
                print(f"الكمية أصبحت صفر بعد التقريب، استخدام الحد الأدنى: {min_quantity}")
                rounded_qty = min_quantity
            
            print(f"تم تقريب الكمية: {qty} → {rounded_qty}")
            return rounded_qty
            
        except Exception as e:
            print(f"خطأ في تقريب الكمية: {e}")
            # في حالة الخطأ، استخدم الحد الأدنى الآمن
            return 0.001
    
    # اختبار قيم مختلفة
    test_values = [0.0, 0.0001, 0.0005, 0.001, 0.002, 0.123456789, 1.0, 10.5]
    
    for qty in test_values:
        print(f"\nاختبار الكمية: {qty}")
        result = round_quantity(qty, "linear", "BTCUSDT")
        print(f"النتيجة: {result}")

if __name__ == "__main__":
    print("بدء اختبار المنطق القديم المطبق")
    print("=" * 60)
    
    test_old_quantity_logic()
    test_round_quantity_function()
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("\nالخلاصة:")
    print("- تم تطبيق المنطق القديم البسيط")
    print("- الحد الأدنى: 0.001")
    print("- التقريب: 6 منازل عشرية")
    print("- ضمان عدم وصول الكمية للصفر")
    print("- يجب أن تعمل الصفقات الآن بدون مشاكل")
