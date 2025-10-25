#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لتعديل الرافعة المالية
"""

import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_leverage_simple():
    """اختبار بسيط لتعديل الرافعة المالية"""
    
    print("اختبار تعديل الرافعة المالية")
    print("=" * 40)
    
    # الحصول على الحساب الحقيقي
    user_id = 1
    account = real_account_manager.get_account(user_id)
    
    if not account:
        print("لا يوجد حساب حقيقي مفعّل")
        print("يرجى إضافة مفاتيح API صحيحة")
        return False
    
    print(f"تم العثور على حساب حقيقي للمستخدم {user_id}")
    
    # اختبار تعديل الرافعة المالية
    test_symbol = 'BTCUSDT'
    test_leverage = 1
    test_category = 'linear'
    
    print(f"\nاختبار تعديل الرافعة المالية:")
    print(f"الرمز: {test_symbol}")
    print(f"الرافعة: {test_leverage}x")
    print(f"النوع: {test_category}")
    
    try:
        # محاولة تعديل الرافعة المالية
        result = account.set_leverage(
            category=test_category,
            symbol=test_symbol,
            leverage=test_leverage
        )
        
        if result:
            print("نجح تعديل الرافعة المالية!")
            return True
        else:
            print("فشل تعديل الرافعة المالية")
            return False
            
    except Exception as e:
        print(f"خطأ في تعديل الرافعة المالية: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_placement():
    """اختبار وضع أمر"""
    
    print("\nاختبار وضع أمر")
    print("=" * 30)
    
    # الحصول على الحساب الحقيقي
    user_id = 1
    account = real_account_manager.get_account(user_id)
    
    if not account:
        print("لا يوجد حساب حقيقي مفعّل")
        return False
    
    # بيانات الأمر
    order_params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'order_type': 'Market',
        'qty': 0.001,  # كمية صغيرة للاختبار
        'leverage': 1
    }
    
    print("بيانات الأمر:")
    for key, value in order_params.items():
        print(f"  {key}: {value}")
    
    try:
        # وضع الأمر
        result = account.place_order(**order_params)
        
        if result and result.get('success'):
            print("نجح وضع الأمر!")
            print(f"Order ID: {result.get('order_id')}")
            return True
        else:
            print("فشل وضع الأمر")
            if result:
                print(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        print(f"خطأ في وضع الأمر: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("بدء اختبار تعديل الرافعة المالية...")
    
    try:
        # اختبار تعديل الرافعة المالية
        leverage_test = test_leverage_simple()
        
        # اختبار وضع الأمر
        order_test = test_order_placement()
        
        print("\nملخص النتائج:")
        print(f"اختبار الرافعة المالية: {'نجح' if leverage_test else 'فشل'}")
        print(f"اختبار الأمر: {'نجح' if order_test else 'فشل'}")
        
        if leverage_test and order_test:
            print("\nجميع الاختبارات نجحت! تعديل الرافعة المالية يعمل بشكل صحيح.")
        else:
            print("\nبعض الاختبارات فشلت. راجع السجلات للتفاصيل.")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
