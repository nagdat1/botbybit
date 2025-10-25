#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مساعد إضافة مفاتيح API لـ Bybit
"""

import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def add_api_keys(user_id: int, api_key: str, api_secret: str) -> bool:
    """إضافة مفاتيح API للمستخدم"""
    
    try:
        print(f"إضافة مفاتيح API للمستخدم {user_id}...")
        
        # التحقق من صحة المفاتيح
        if not api_key or not api_secret:
            print("❌ مفاتيح API فارغة!")
            return False
        
        if len(api_key) < 10 or len(api_secret) < 10:
            print("❌ مفاتيح API قصيرة جداً!")
            return False
        
        # تهيئة الحساب
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("❌ فشل في تهيئة الحساب!")
            return False
        
        print("✅ تم إضافة مفاتيح API بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة مفاتيح API: {e}")
        return False

def test_api_keys(user_id: int) -> bool:
    """اختبار مفاتيح API"""
    
    try:
        print(f"اختبار مفاتيح API للمستخدم {user_id}...")
        
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("❌ لا يوجد حساب مفعّل!")
            return False
        
        # اختبار جلب الرصيد
        print("اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('futures')
        
        if balance:
            print("✅ مفاتيح API صحيحة!")
            
            # عرض الرصيد إذا كان متوفراً
            if 'coins' in balance and 'USDT' in balance['coins']:
                usdt_balance = balance['coins']['USDT'].get('equity', 0)
                print(f"💰 الرصيد المتاح: {usdt_balance} USDT")
            
            return True
        else:
            print("❌ مفاتيح API غير صحيحة!")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار مفاتيح API: {e}")
        return False

def test_leverage_setting(user_id: int) -> bool:
    """اختبار تعديل الرافعة المالية"""
    
    try:
        print("اختبار تعديل الرافعة المالية...")
        
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("❌ لا يوجد حساب مفعّل!")
            return False
        
        # اختبار تعديل الرافعة المالية
        result = account.set_leverage('linear', 'BTCUSDT', 1)
        
        if result:
            print("✅ تم تعديل الرافعة المالية بنجاح!")
            return True
        else:
            print("❌ فشل تعديل الرافعة المالية!")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الرافعة المالية: {e}")
        return False

def test_order_placement(user_id: int) -> bool:
    """اختبار وضع أمر"""
    
    try:
        print("اختبار وضع أمر...")
        
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("❌ لا يوجد حساب مفعّل!")
            return False
        
        # اختبار وضع أمر صغير
        result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001,  # كمية صغيرة للاختبار
            leverage=1
        )
        
        if result and result.get('success'):
            print("✅ تم وضع الأمر بنجاح!")
            print(f"Order ID: {result.get('order_id')}")
            return True
        else:
            print("❌ فشل وضع الأمر!")
            if result:
                print(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار وضع الأمر: {e}")
        return False

def interactive_setup():
    """إعداد تفاعلي لمفاتيح API"""
    
    print("إعداد مفاتيح API لـ Bybit")
    print("=" * 40)
    
    # الحصول على معرف المستخدم
    try:
        user_id = int(input("أدخل معرف المستخدم (رقم): "))
    except ValueError:
        print("❌ معرف المستخدم يجب أن يكون رقماً!")
        return False
    
    # الحصول على مفتاح API
    api_key = input("أدخل مفتاح API: ").strip()
    if not api_key:
        print("❌ مفتاح API فارغ!")
        return False
    
    # الحصول على المفتاح السري
    api_secret = input("أدخل المفتاح السري: ").strip()
    if not api_secret:
        print("❌ المفتاح السري فارغ!")
        return False
    
    print(f"\nإضافة مفاتيح API للمستخدم {user_id}...")
    
    # إضافة المفاتيح
    if not add_api_keys(user_id, api_key, api_secret):
        return False
    
    # اختبار المفاتيح
    print("\nاختبار مفاتيح API...")
    if not test_api_keys(user_id):
        return False
    
    # اختبار تعديل الرافعة المالية
    print("\nاختبار تعديل الرافعة المالية...")
    if not test_leverage_setting(user_id):
        return False
    
    # اختبار وضع الأمر
    print("\nاختبار وضع الأمر...")
    if not test_order_placement(user_id):
        return False
    
    print("\n🎉 تم إعداد مفاتيح API بنجاح!")
    print("النظام جاهز للاستخدام!")
    
    return True

def quick_test():
    """اختبار سريع للنظام"""
    
    print("اختبار سريع للنظام")
    print("=" * 30)
    
    user_id = 1  # معرف المستخدم الافتراضي
    
    # اختبار المفاتيح الموجودة
    if test_api_keys(user_id):
        print("✅ مفاتيح API تعمل بشكل صحيح!")
        
        # اختبار تعديل الرافعة المالية
        if test_leverage_setting(user_id):
            print("✅ تعديل الرافعة المالية يعمل!")
        else:
            print("❌ مشكلة في تعديل الرافعة المالية")
        
        # اختبار وضع الأمر
        if test_order_placement(user_id):
            print("✅ وضع الأمر يعمل!")
        else:
            print("❌ مشكلة في وضع الأمر")
        
        return True
    else:
        print("❌ مفاتيح API غير صحيحة أو مفقودة!")
        print("يرجى إضافة مفاتيح API صحيحة")
        return False

if __name__ == "__main__":
    print("مساعد مفاتيح API لـ Bybit")
    print("=" * 40)
    
    print("اختر الخيار:")
    print("1. إعداد مفاتيح API جديدة")
    print("2. اختبار مفاتيح API الموجودة")
    
    try:
        choice = input("أدخل رقم الخيار (1 أو 2): ").strip()
        
        if choice == "1":
            interactive_setup()
        elif choice == "2":
            quick_test()
        else:
            print("❌ خيار غير صحيح!")
            
    except KeyboardInterrupt:
        print("\nتم إلغاء العملية")
    except Exception as e:
        print(f"❌ خطأ: {e}")
