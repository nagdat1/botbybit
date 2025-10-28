#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث المستخدم ليصبح حساب حقيقي
"""

import sys
import os

def update_user_to_real():
    """تحديث المستخدم ليصبح حساب حقيقي"""
    
    print("=== تحديث المستخدم ليصبح حساب حقيقي ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        from database import db_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # استخدام المستخدم الجديد
        user_id = 999999
        api_key = "mx0vglb3kLs2Rbe8pG"
        api_secret = "cd479996b38a4944933bbe79015ffa09"
        
        print(f"تحديث المستخدم: {user_id}")
        print(f"API Key: {api_key}")
        print()
        
        # تحديث إعدادات المستخدم في قاعدة البيانات
        settings_data = {
            'account_type': 'real',
            'market_type': 'spot'
        }
        
        success = db_manager.update_user_settings(user_id, settings_data)
        
        # تحديث بيانات المستخدم الأخرى
        user_data = {
            'exchange': 'bybit',
            'bybit_api_key': api_key,
            'bybit_api_secret': api_secret
        }
        
        success2 = db_manager.update_user_data(user_id, user_data)
        
        if success and success2:
            print("تم تحديث بيانات المستخدم في قاعدة البيانات بنجاح!")
        else:
            print("فشل في تحديث بيانات المستخدم في قاعدة البيانات")
            return False
        
        # تحديث بيانات المستخدم في الذاكرة
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data.update(user_data)
            user_data['account_type'] = 'real'
            user_data['market_type'] = 'spot'
            user_manager.users[user_id] = user_data
            print("تم تحديث بيانات المستخدم في الذاكرة بنجاح!")
        else:
            print("لم يتم العثور على المستخدم في الذاكرة")
            return False
        
        # إنشاء الحساب الحقيقي
        print("إنشاء الحساب الحقيقي...")
        from real_account_manager import BybitRealAccount
        
        account = BybitRealAccount(
            api_key=api_key,
            api_secret=api_secret
        )
        
        real_account_manager.accounts[user_id] = account
        
        print("تم إنشاء الحساب الحقيقي بنجاح!")
        print()
        
        # اختبار الحساب
        print("اختبار الحساب...")
        try:
            balance = account.get_wallet_balance('unified')
            if balance:
                print(f"الرصيد: {balance.get('total_equity', 0)}")
            else:
                print("فشل جلب الرصيد")
        except Exception as e:
            print(f"خطأ في جلب الرصيد: {e}")
        
        print()
        print("=== تم تحديث المستخدم بنجاح ===")
        print(f"User ID: {user_id}")
        print("Account Type: real")
        print("Exchange: bybit")
        print("Market Type: spot")
        print("يمكنك الآن استخدام هذا المستخدم لتنفيذ الإشارات")
        
        return True
        
    except Exception as e:
        print(f"خطأ في التحديث: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_user_to_real()
    if not success:
        sys.exit(1)
