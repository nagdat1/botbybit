#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار API Key الجديد
"""

import sys
import os

def test_new_api_key():
    """اختبار API Key الجديد"""
    
    print("=== اختبار API Key الجديد ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from real_account_manager import BybitRealAccount
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # API Key الجديد
        api_key = "dqBHnPaItfmEZSB020"
        api_secret = input("ادخل API Secret: ").strip()
        
        print()
        print(f"API Key: {api_key}")
        print(f"API Secret: {api_secret[:10]}...")
        print()
        
        # إنشاء الحساب
        print("إنشاء الحساب...")
        account = BybitRealAccount(api_key, api_secret)
        print("تم إنشاء الحساب بنجاح")
        print()
        
        # اختبار 1: جلب معلومات الحساب
        print("اختبار 1: جلب معلومات الحساب...")
        balance = account.get_wallet_balance('unified')
        if balance:
            print(f"الرصيد: {balance}")
            print("نجح اختبار معلومات الحساب")
        else:
            print("فشل اختبار معلومات الحساب")
        print()
        
        # اختبار 2: جلب السعر الحالي
        print("اختبار 2: جلب السعر الحالي...")
        price = account.get_ticker_price('BTCUSDT', 'spot')
        if price:
            print(f"السعر الحالي لـ BTCUSDT: ${price}")
            print("نجح اختبار جلب السعر")
        else:
            print("فشل اختبار جلب السعر")
            return False
        print()
        
        # اختبار 3: وضع أمر تجريبي صغير جداً
        print("اختبار 3: وضع أمر تجريبي...")
        print(f"السعر الحالي: ${price}")
        
        # حساب كمية صغيرة جداً ($10 بدلاً من $50)
        test_amount = 10.0
        qty = round(test_amount / price, 6)
        
        print(f"المبلغ: ${test_amount}")
        print(f"الكمية: {qty} BTC")
        print()
        
        print("هل تريد تجربة وضع أمر حقيقي؟")
        print("تحذير: هذا سيضع أمر حقيقي على المنصة!")
        confirm = input("اكتب 'نعم' للمتابعة: ").strip()
        
        if confirm == 'نعم':
            result = account.place_order(
                category='spot',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Market',
                qty=qty
            )
            
            print()
            print(f"نتيجة الأمر: {result}")
            
            if result and result.get('order_id'):
                print("نجح وضع الأمر!")
                print(f"Order ID: {result.get('order_id')}")
                return True
            else:
                print("فشل وضع الأمر!")
                return False
        else:
            print("تم إلغاء الاختبار")
            return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_api_key()
    if not success:
        sys.exit(1)

