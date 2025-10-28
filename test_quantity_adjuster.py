#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار أداة التعديل الذكية للكمية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_quantity_adjuster():
    """اختبار أداة التعديل الذكية"""
    try:
        from api.quantity_adjuster import QuantityAdjuster
        print("تم استيراد QuantityAdjuster بنجاح")
        
        # اختبار التعديل الذكي
        qty = 0.00123456
        price = 50000.0
        trade_amount = 100.0
        leverage = 10
        exchange = 'bybit'
        
        print(f"\nاختبار التعديل الذكي:")
        print(f"   المدخلات: qty={qty}, price={price}, amount={trade_amount}, leverage={leverage}")
        
        adjusted = QuantityAdjuster.smart_quantity_adjustment(
            qty=qty,
            price=price,
            trade_amount=trade_amount,
            leverage=leverage,
            exchange=exchange
        )
        
        print(f"   النتيجة: {qty} -> {adjusted}")
        
        # اختبار الخيارات المتعددة
        print(f"\nاختبار الخيارات المتعددة:")
        options = QuantityAdjuster.get_multiple_quantity_options(qty, price, exchange)
        print(f"   الخيارات: {options}")
        
        # اختبار التحقق من الصحة
        print(f"\nاختبار التحقق من الصحة:")
        validation = QuantityAdjuster.validate_quantity(adjusted, price, exchange)
        print(f"   صالح: {validation['valid']}")
        if validation['errors']:
            print(f"   أخطاء: {validation['errors']}")
        if validation['warnings']:
            print(f"   تحذيرات: {validation['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار QuantityAdjuster: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_executor():
    """اختبار منفذ الإشارات"""
    try:
        from signals.signal_executor import SignalExecutor, QUANTITY_ADJUSTER_AVAILABLE
        print(f"تم استيراد SignalExecutor بنجاح")
        print(f"   أداة التعديل الذكية متاحة: {QUANTITY_ADJUSTER_AVAILABLE}")
        
        # اختبار دالة التعديل
        qty = 0.00123456
        price = 50000.0
        trade_amount = 100.0
        leverage = 10
        exchange = 'bybit'
        
        print(f"\nاختبار دالة التعديل في SignalExecutor:")
        adjusted = SignalExecutor._calculate_adjusted_quantity(
            qty=qty,
            price=price,
            trade_amount=trade_amount,
            leverage=leverage,
            exchange=exchange
        )
        
        print(f"   النتيجة: {qty} → {adjusted}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار SignalExecutor: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exchange_base():
    """اختبار الفئة الأساسية للمنصات"""
    try:
        from api.exchanges.bybit_exchange import BybitExchange
        
        # إنشاء مثيل تجريبي
        exchange = BybitExchange(name='bybit', api_key='test', api_secret='test')
        
        print(f"تم إنشاء BybitExchange بنجاح")
        print(f"   اسم المنصة: {exchange.name}")
        print(f"   exchange_name: {getattr(exchange, 'exchange_name', 'غير موجود')}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار Exchange: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("بدء اختبار المشروع المرتب")
    print("=" * 50)
    
    tests = [
        ("أداة التعديل الذكية", test_quantity_adjuster),
        ("منفذ الإشارات", test_signal_executor),
        ("الفئة الأساسية للمنصات", test_exchange_base)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nاختبار {test_name}:")
        print("-" * 30)
        
        if test_func():
            print(f"{test_name}: نجح")
            passed += 1
        else:
            print(f"{test_name}: فشل")
    
    print("\n" + "=" * 50)
    print(f"النتائج النهائية: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("جميع الاختبارات نجحت! المشروع مرتب بشكل صحيح.")
    else:
        print("بعض الاختبارات فشلت. يحتاج المشروع إلى مراجعة.")
