#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث إلى API Key الجديد
"""

import sys
import os

def update_to_new_api():
    """تحديث إلى API Key الجديد"""
    
    print("=== تحديث إلى API Key الجديد ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from database import db_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # API Key الجديد
        new_api_key = "dqBHnPaItfmEZSB020"
        
        print("يرجى توفير API Secret للمفتاح الجديد:")
        print("API Key: dqBHnPaItfmEZSB020")
        print()
        print("ملاحظة: يجب عليك نسخ API Secret من صفحة Bybit API Management")
        print()
        
        # البحث عن المستخدمين الموجودين
        print("البحث عن المستخدمين...")
        users_with_real_account = []
        
        for user_id, user_data in user_manager.users.items():
            if user_data.get('account_type') == 'real' and user_data.get('exchange') == 'bybit':
                users_with_real_account.append(user_id)
        
        if not users_with_real_account:
            print("لم يتم العثور على مستخدمين بحساب حقيقي")
            print()
            print("سأقوم بإنشاء مستخدم جديد...")
            user_id = 999999
        else:
            user_id = users_with_real_account[0]
            print(f"تم العثور على مستخدم: {user_id}")
        
        print()
        print("لتحديث API Key، قم بالخطوات التالية:")
        print()
        print("1. افتح ملف .env في المشروع")
        print("2. أضف أو حدث السطور التالية:")
        print()
        print(f"BYBIT_API_KEY={new_api_key}")
        print("BYBIT_API_SECRET=<ضع API Secret هنا>")
        print()
        print("3. أو استخدم البوت للربط:")
        print("   - شغل البوت: python bybit_trading_bot.py")
        print("   - اضغط 'الإعدادات'")
        print("   - اضغط 'ربط API'")
        print("   - اختر 'Bybit'")
        print(f"   - أدخل API Key: {new_api_key}")
        print("   - أدخل API Secret: <من صفحة Bybit>")
        print()
        
        return True
        
    except Exception as e:
        print(f"خطأ في التحديث: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_to_new_api()
    if not success:
        sys.exit(1)

