#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نظام الربط المدمج في المشروع
"""

import sys
import os

def test_integrated_linking():
    """اختبار نظام الربط المدمج"""
    
    print("=== اختبار نظام الربط المدمج ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from database import db_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # اختبار إنشاء مستخدم تجريبي
        test_user_id = 12345
        test_api_key = "mx0vglb3kLs2Rbe8pG"
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
        
        # اختبار جلب الرصيد
        print("اختبار جلب الرصيد...")
        try:
            balance = account.get_wallet_balance('unified')
            if balance:
                print("نجح جلب الرصيد!")
                print(f"الرصيد الإجمالي: {balance.get('total_equity', 0)}")
                print(f"الرصيد المتاح: {balance.get('available_balance', 0)}")
            else:
                print("فشل جلب الرصيد - تحقق من API keys")
                return False
        except Exception as e:
            print(f"خطأ في جلب الرصيد: {e}")
            return False
        
        # اختبار جلب السعر
        print("اختبار جلب السعر...")
        try:
            price = account.get_ticker_price('BTCUSDT', 'spot')
            if price:
                print(f"نجح جلب السعر! سعر BTCUSDT: ${price}")
            else:
                print("فشل جلب السعر")
                return False
        except Exception as e:
            print(f"خطأ في جلب السعر: {e}")
            return False
        
        # تنظيف البيانات التجريبية
        print("تنظيف البيانات التجريبية...")
        real_account_manager.remove_account(test_user_id)
        if test_user_id in user_manager.users:
            del user_manager.users[test_user_id]
        
        print()
        print("جميع الاختبارات نجحت! نظام الربط المدمج يعمل بشكل صحيح.")
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integrated_linking()
    if not success:
        sys.exit(1)
