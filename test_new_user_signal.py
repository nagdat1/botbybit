#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار تنفيذ إشارة مع المستخدم الجديد
"""

import sys
import os
import asyncio

async def test_signal_execution():
    """اختبار تنفيذ إشارة مع المستخدم الجديد"""
    
    print("=== اختبار تنفيذ إشارة مع المستخدم الجديد ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from signal_executor import SignalExecutor
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # استخدام المستخدم الجديد
        user_id = 999999
        
        print(f"استخدام المستخدم: {user_id}")
        
        # الحصول على بيانات المستخدم
        user_data = user_manager.get_user(user_id)
        if not user_data:
            print("لم يتم العثور على المستخدم")
            return False
        
        print(f"بيانات المستخدم: {user_data.get('account_type')} - {user_data.get('exchange')}")
        
        # الحصول على الحساب الحقيقي
        account = real_account_manager.get_account(user_id)
        if not account:
            print("لم يتم العثور على الحساب الحقيقي")
            return False
        
        print(f"تم العثور على الحساب: {type(account).__name__}")
        
        # اختبار تنفيذ إشارة
        print("اختبار تنفيذ إشارة...")
        signal_data = {
            'action': 'buy',
            'symbol': 'BTCUSDT',
            'price': 110000.0,
            'signal_id': 'TEST-NEW-USER',
            'has_signal_id': True
        }
        
        print(f"بيانات الإشارة: {signal_data}")
        
        # تنفيذ الإشارة
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
            else:
                print("فشل تنفيذ الإشارة!")
                print(f"سبب الفشل: {result.get('message')}")
        else:
            print("لم يتم إرجاع نتيجة!")
        
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_signal_execution()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
