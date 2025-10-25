#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
حل نهائي لمشكلة تنفيذ الإشارات
"""

import sys
import os
import asyncio

async def final_solution():
    """الحل النهائي لمشكلة تنفيذ الإشارات"""
    
    print("=== الحل النهائي لمشكلة تنفيذ الإشارات ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from signal_executor import SignalExecutor
        from database import db_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # استخدام المستخدم المحدث
        user_id = 999999
        
        print(f"استخدام المستخدم: {user_id}")
        
        # إعادة تحميل بيانات المستخدم من قاعدة البيانات
        print("إعادة تحميل بيانات المستخدم من قاعدة البيانات...")
        user_data = db_manager.get_user(user_id)
        if not user_data:
            print("لم يتم العثور على المستخدم في قاعدة البيانات")
            return False
        
        # تحديث البيانات في الذاكرة
        user_manager.users[user_id] = user_data
        
        print(f"بيانات المستخدم: {user_data.get('account_type')} - {user_data.get('exchange')}")
        print(f"API Key: {user_data.get('bybit_api_key', 'None')[:10]}...")
        print()
        
        # إنشاء الحساب الحقيقي مباشرة
        print("إنشاء الحساب الحقيقي مباشرة...")
        api_key = user_data.get('bybit_api_key')
        api_secret = user_data.get('bybit_api_secret')
        exchange = user_data.get('exchange', 'bybit')
        
        if not api_key or not api_secret:
            print("API Key أو API Secret مفقود")
            return False
        
        try:
            real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
            account = real_account_manager.get_account(user_id)
            
            if account:
                print(f"تم إنشاء الحساب: {type(account).__name__}")
            else:
                print("فشل في إنشاء الحساب")
                return False
        except Exception as e:
            print(f"خطأ في إنشاء الحساب: {e}")
            return False
        
        # اختبار تنفيذ إشارة
        print("اختبار تنفيذ إشارة...")
        signal_data = {
            'action': 'buy',
            'symbol': 'BTCUSDT',
            'price': 110000.0,
            'signal_id': 'FINAL-SOLUTION-TEST',
            'has_signal_id': True
        }
        
        print(f"بيانات الإشارة: {signal_data}")
        print()
        
        # تنفيذ الإشارة
        print("تنفيذ الإشارة...")
        result = await SignalExecutor.execute_signal(user_id, signal_data, user_data)
        
        print(f"نتيجة التنفيذ: {result}")
        print()
        
        # تحليل النتيجة
        if result:
            print("تحليل النتيجة:")
            print(f"  - success: {result.get('success')}")
            print(f"  - message: {result.get('message')}")
            print(f"  - error: {result.get('error')}")
            print(f"  - order_id: {result.get('order_id')}")
            print(f"  - error_details: {result.get('error_details')}")
            
            if result.get('success'):
                print("تم تنفيذ الإشارة بنجاح!")
                print("يجب أن تظهر الصفقة في المنصة الآن")
                return True
            else:
                print("فشل تنفيذ الإشارة!")
                print(f"سبب الفشل: {result.get('message')}")
                
                # فحص تفاصيل الخطأ
                error_details = result.get('error_details')
                if error_details:
                    print(f"تفاصيل الخطأ: {error_details}")
                return False
        else:
            print("لم يتم إرجاع نتيجة!")
            return False
        
    except Exception as e:
        print(f"خطأ في الحل النهائي: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await final_solution()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
