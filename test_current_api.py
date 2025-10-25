#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مفاتيح API الحالية
"""

import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_current_api_keys():
    """اختبار مفاتيح API الحالية"""
    
    print("اختبار مفاتيح API الحالية")
    print("=" * 40)
    
    user_id = 1  # معرف المستخدم الافتراضي
    
    try:
        # محاولة الحصول على الحساب
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("لا يوجد حساب مفعّل للمستخدم", user_id)
            print("المشكلة: مفاتيح API مفقودة أو غير صحيحة")
            print()
            print("الحل:")
            print("1. اذهب إلى Bybit.com")
            print("2. سجل الدخول إلى حسابك")
            print("3. اذهب إلى Account & Security > API Management")
            print("4. اضغط على Create New Key")
            print("5. اختر الصلاحيات: Read, Trade, Derivatives")
            print("6. انسخ API Key و Secret Key")
            print("7. أضف المفاتيح إلى النظام")
            return False
        
        print("تم العثور على حساب مفعّل!")
        
        # اختبار جلب الرصيد
        print("اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('futures')
        
        if balance:
            print("مفاتيح API صحيحة!")
            
            # عرض الرصيد إذا كان متوفراً
            if 'coins' in balance and 'USDT' in balance['coins']:
                usdt_balance = balance['coins']['USDT'].get('equity', 0)
                print(f"الرصيد المتاح: {usdt_balance} USDT")
            
            # اختبار تعديل الرافعة المالية
            print("اختبار تعديل الرافعة المالية...")
            leverage_result = account.set_leverage('linear', 'BTCUSDT', 1)
            
            if leverage_result:
                print("تم تعديل الرافعة المالية بنجاح!")
                
                # اختبار وضع أمر صغير
                print("اختبار وضع أمر...")
                order_result = account.place_order(
                    category='linear',
                    symbol='BTCUSDT',
                    side='Buy',
                    order_type='Market',
                    qty=0.001,  # كمية صغيرة للاختبار
                    leverage=1
                )
                
                if order_result and order_result.get('success'):
                    print("تم وضع الأمر بنجاح!")
                    print(f"Order ID: {order_result.get('order_id')}")
                    print()
                    print("النظام يعمل بشكل مثالي!")
                    return True
                else:
                    print("فشل وضع الأمر")
                    if order_result:
                        print(f"تفاصيل الخطأ: {order_result}")
                    return False
            else:
                print("فشل تعديل الرافعة المالية")
                return False
        else:
            print("مفاتيح API غير صحيحة!")
            print("يرجى التحقق من صحة المفاتيح")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    print("بدء اختبار مفاتيح API...")
    
    try:
        result = test_current_api_keys()
        
        if result:
            print("جميع الاختبارات نجحت!")
        else:
            print("بعض الاختبارات فشلت - راجع التعليمات أعلاه")
            
    except Exception as e:
        print(f"خطأ عام: {e}")
