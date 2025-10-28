#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص المستخدمين الموجودين
"""

import sys
import os

def check_existing_users():
    """فحص المستخدمين الموجودين"""
    
    print("=== فحص المستخدمين الموجودين ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # فحص جميع المستخدمين
        print("المستخدمين الموجودين:")
        for user_id, user_data in user_manager.users.items():
            print(f"  - User ID: {user_id}")
            print(f"    Account Type: {user_data.get('account_type', 'unknown')}")
            print(f"    Exchange: {user_data.get('exchange', 'unknown')}")
            print(f"    Market Type: {user_data.get('market_type', 'unknown')}")
            print(f"    Has API Key: {bool(user_data.get('bybit_api_key'))}")
            api_key = user_data.get('bybit_api_key', 'None')
            if api_key and api_key != 'None':
                print(f"    API Key: {api_key[:10]}...")
            else:
                print(f"    API Key: None")
            print()
        
        # فحص الحسابات الحقيقية
        print("الحسابات الحقيقية:")
        for user_id in real_account_manager.accounts.keys():
            print(f"  - User ID: {user_id}")
            account = real_account_manager.accounts[user_id]
            print(f"    Account Type: {type(account).__name__}")
            print()
        
        # البحث عن مستخدم بحساب حقيقي
        print("البحث عن مستخدم بحساب حقيقي...")
        real_user = None
        for user_id, user_data in user_manager.users.items():
            if user_data.get('account_type') == 'real':
                real_user = user_id
                break
        
        if real_user:
            print(f"تم العثور على مستخدم بحساب حقيقي: {real_user}")
            
            # فحص الحساب الحقيقي
            account = real_account_manager.get_account(real_user)
            if account:
                print(f"الحساب الحقيقي موجود: {type(account).__name__}")
                
                # اختبار بسيط للحساب
                try:
                    balance = account.get_wallet_balance('unified')
                    if balance:
                        print(f"الرصيد: {balance.get('total_equity', 0)}")
                    else:
                        print("فشل جلب الرصيد")
                except Exception as e:
                    print(f"خطأ في جلب الرصيد: {e}")
            else:
                print("الحساب الحقيقي غير موجود")
        else:
            print("لم يتم العثور على مستخدم بحساب حقيقي")
            print()
            print("الحلول المتاحة:")
            print("1. إنشاء مستخدم جديد بحساب حقيقي")
            print("2. تحديث مستخدم موجود ليصبح حساب حقيقي")
            print("3. ربط API Key جديد")
        
        return True
        
    except Exception as e:
        print(f"خطأ في الفحص: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_existing_users()
    if not success:
        sys.exit(1)
