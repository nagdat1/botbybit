#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تطبيق API Key الجديد مباشرة
"""

import sys
import os

def apply_new_api_key():
    """تطبيق API Key الجديد مباشرة"""
    
    print("=== تطبيق API Key الجديد ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from database import db_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # API Key الجديد
        new_api_key = "dqBHnPaItfmEZSB020"
        new_api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
        
        print(f"API Key: {new_api_key}")
        print(f"API Secret: {new_api_secret[:10]}...")
        print()
        
        # تحديث المستخدم 999999
        user_id = 999999
        
        print(f"تحديث المستخدم: {user_id}")
        print()
        
        # تحديث في قاعدة البيانات
        print("1. تحديث قاعدة البيانات...")
        update_data = {
            'bybit_api_key': new_api_key,
            'bybit_api_secret': new_api_secret,
            'exchange': 'bybit'
        }
        
        success = db_manager.update_user_data(user_id, update_data)
        
        if success:
            print("   تم التحديث في قاعدة البيانات")
        else:
            print("   فشل التحديث في قاعدة البيانات")
        
        # تحديث إعدادات المستخدم
        print("2. تحديث إعدادات المستخدم...")
        settings_data = {
            'account_type': 'real',
            'market_type': 'spot'
        }
        
        success2 = db_manager.update_user_settings(user_id, settings_data)
        
        if success2:
            print("   تم تحديث الإعدادات")
        else:
            print("   فشل تحديث الإعدادات")
        
        # تحديث في الذاكرة
        print("3. تحديث في الذاكرة...")
        user_data = db_manager.get_user(user_id)
        if user_data:
            user_manager.users[user_id] = user_data
            print("   تم التحديث في الذاكرة")
        else:
            print("   فشل التحديث في الذاكرة")
        
        # إنشاء الحساب الحقيقي
        print("4. إنشاء الحساب الحقيقي...")
        try:
            real_account_manager.initialize_account(user_id, 'bybit', new_api_key, new_api_secret)
            account = real_account_manager.get_account(user_id)
            
            if account:
                print("   تم إنشاء الحساب الحقيقي")
            else:
                print("   فشل إنشاء الحساب الحقيقي")
        except Exception as e:
            print(f"   خطأ في إنشاء الحساب: {e}")
        
        print()
        print("=== تم التطبيق بنجاح ===")
        print()
        print("الآن يمكنك اختبار تنفيذ إشارة:")
        print("python final_solution.py")
        
        return True
        
    except Exception as e:
        print(f"خطأ في التطبيق: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_new_api_key()
    if not success:
        sys.exit(1)

