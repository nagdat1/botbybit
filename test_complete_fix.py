#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نهائي للإصلاح الكامل
"""

import sys
import os

async def test_complete_fix():
    """اختبار الإصلاح الكامل"""
    
    print("=== اختبار الإصلاح الكامل ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from signal_executor import SignalExecutor
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # اختبار إنشاء مستخدم تجريبي
        test_user_id = 88888
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
            user_data['market_type'] = 'spot'
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
        
        # اختبار تنفيذ إشارة (يجب أن يفشل بسبب عدم وجود صلاحيات)
        print("اختبار تنفيذ إشارة...")
        try:
            signal_data = {
                'action': 'buy',
                'symbol': 'BTCUSDT',
                'price': 110000.0,
                'signal_id': 'TEST-123',
                'has_signal_id': True
            }
            
            result = await SignalExecutor.execute_signal(test_user_id, signal_data, user_data)
            
            print(f"نتيجة تنفيذ الإشارة: {result}")
            
            if result and result.get('success'):
                print("خطأ: الإشارة نجحت رغم عدم وجود صلاحيات!")
                return False
            elif result and not result.get('success'):
                print("صحيح: الإشارة فشلت كما هو متوقع (لا توجد صلاحيات)")
                print(f"رسالة الخطأ: {result.get('message', 'غير محدد')}")
                print(f"تفاصيل الخطأ: {result.get('error_details', 'غير محدد')}")
            else:
                print("خطأ: استجابة غير متوقعة")
                return False
                
        except Exception as e:
            print(f"خطأ في تنفيذ الإشارة: {e}")
            return False
        
        # تنظيف البيانات التجريبية
        print("تنظيف البيانات التجريبية...")
        real_account_manager.remove_account(test_user_id)
        if test_user_id in user_manager.users:
            del user_manager.users[test_user_id]
        
        print()
        print("جميع الاختبارات نجحت! الإصلاح الكامل يعمل بشكل صحيح.")
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_complete_fix()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
