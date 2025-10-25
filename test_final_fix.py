#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نهائي للإصلاحات المطبقة
"""

import sys
import os

def test_fixed_error_handling():
    """اختبار معالجة الأخطاء المحسنة"""
    
    print("=== اختبار معالجة الأخطاء المحسنة ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # اختبار إنشاء مستخدم تجريبي
        test_user_id = 99999
        test_api_key = "mx0vglb3kLs2Rbe8pG"  # API key بدون صلاحيات
        test_api_secret = "cd479996b38a4944933bbe79015ffa09"
        
        print(f"إنشاء مستخدم تجريبي: {test_user_id}")
        
        # إنشاء المستخدم
        success = user_manager.create_user(test_user_id)
        if success:
            print("تم إنشاء المستخدم بنجاح")
        else:
            print("فشل في إنشاء المستخدم")
            return False
        
        # تحديث API keys للمستخدم
        print("تحديث API keys للمستخدم...")
        user_data = user_manager.get_user(test_user_id)
        if user_data:
            user_data['bybit_api_key'] = test_api_key
            user_data['bybit_api_secret'] = test_api_secret
            user_data['exchange'] = 'bybit'
            user_data['account_type'] = 'real'
            print("تم تحديث بيانات المستخدم")
        else:
            print("فشل في الحصول على بيانات المستخدم")
            return False
        
        # تهيئة الحساب الحقيقي
        print("تهيئة الحساب الحقيقي...")
        try:
            real_account_manager.initialize_account(test_user_id, 'bybit', test_api_key, test_api_secret)
            print("تم تهيئة الحساب الحقيقي بنجاح")
        except Exception as e:
            print(f"فشل في تهيئة الحساب الحقيقي: {e}")
            return False
        
        # اختبار الحصول على الحساب
        print("اختبار الحصول على الحساب...")
        account = real_account_manager.get_account(test_user_id)
        if account:
            print("تم الحصول على الحساب بنجاح")
            print(f"نوع الحساب: {type(account).__name__}")
        else:
            print("فشل في الحصول على الحساب")
            return False
        
        # اختبار وضع أمر (يجب أن يفشل بسبب عدم وجود صلاحيات)
        print("اختبار وضع أمر Spot...")
        try:
            result = account.place_order(
                category='spot',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Market',
                qty=0.0001
            )
            
            print(f"نتيجة وضع الأمر: {result}")
            
            if result and result.get('success'):
                print("خطأ: الأمر نجح رغم عدم وجود صلاحيات!")
                return False
            elif result and not result.get('success'):
                print("صحيح: الأمر فشل كما هو متوقع (لا توجد صلاحيات)")
                print(f"رسالة الخطأ: {result.get('message', 'غير محدد')}")
            else:
                print("خطأ: استجابة غير متوقعة")
                return False
                
        except Exception as e:
            print(f"خطأ في وضع الأمر: {e}")
            return False
        
        # تنظيف البيانات التجريبية
        print("تنظيف البيانات التجريبية...")
        real_account_manager.remove_account(test_user_id)
        if test_user_id in user_manager.users:
            del user_manager.users[test_user_id]
        
        print()
        print("جميع الاختبارات نجحت! معالجة الأخطاء تعمل بشكل صحيح.")
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_error_handling()
    if not success:
        sys.exit(1)
