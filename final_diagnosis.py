#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشخيص نهائي لتنفيذ الإشارات
"""

import sys
import os
import asyncio

async def final_diagnosis():
    """تشخيص نهائي لتنفيذ الإشارات"""
    
    print("=== التشخيص النهائي لتنفيذ الإشارات ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from signal_executor import SignalExecutor
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # استخدام المستخدم المحدث
        user_id = 999999
        
        print(f"استخدام المستخدم: {user_id}")
        
        # الحصول على بيانات المستخدم
        user_data = user_manager.get_user(user_id)
        if not user_data:
            print("لم يتم العثور على المستخدم")
            return False
        
        print(f"بيانات المستخدم: {user_data.get('account_type')} - {user_data.get('exchange')}")
        print(f"API Key: {user_data.get('bybit_api_key', 'None')[:10]}...")
        print()
        
        # الحصول على الحساب الحقيقي
        account = real_account_manager.get_account(user_id)
        if not account:
            print("لم يتم العثور على الحساب الحقيقي")
            return False
        
        print(f"تم العثور على الحساب: {type(account).__name__}")
        print()
        
        # اختبار تنفيذ إشارة
        print("اختبار تنفيذ إشارة...")
        signal_data = {
            'action': 'buy',
            'symbol': 'BTCUSDT',
            'price': 110000.0,
            'signal_id': 'FINAL-TEST',
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
            else:
                print("فشل تنفيذ الإشارة!")
                print(f"سبب الفشل: {result.get('message')}")
                
                # فحص تفاصيل الخطأ
                error_details = result.get('error_details')
                if error_details:
                    print(f"تفاصيل الخطأ: {error_details}")
        else:
            print("لم يتم إرجاع نتيجة!")
        
        return True
        
    except Exception as e:
        print(f"خطأ في التشخيص: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await final_diagnosis()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
