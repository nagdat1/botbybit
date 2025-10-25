#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء مستخدم جديد بحساب حقيقي
"""

import sys
import os

def create_real_user():
    """إنشاء مستخدم جديد بحساب حقيقي"""
    
    print("=== إنشاء مستخدم جديد بحساب حقيقي ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from bybit_trading_bot import user_manager
        from real_account_manager import real_account_manager
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # إنشاء مستخدم جديد
        user_id = 999999  # معرف فريد
        api_key = "mx0vglb3kLs2Rbe8pG"  # API Key المقدم
        api_secret = "cd479996b38a4944933bbe79015ffa09"  # API Secret المقدم
        
        print(f"إنشاء مستخدم جديد:")
        print(f"  - User ID: {user_id}")
        print(f"  - API Key: {api_key}")
        print(f"  - Account Type: real")
        print(f"  - Exchange: bybit")
        print(f"  - Market Type: spot")
        print()
        
        # إنشاء المستخدم
        user_data = {
            'account_type': 'real',
            'exchange': 'bybit',
            'market_type': 'spot',
            'bybit_api_key': api_key,
            'bybit_api_secret': api_secret,
            'demo_balance': 10000.0,
            'risk_settings': {
                'max_daily_loss': 1000.0,
                'max_position_size': 0.1,
                'stop_loss_percentage': 2.0,
                'take_profit_percentage': 4.0
            }
        }
        
        # حفظ المستخدم
        user_manager.users[user_id] = user_data
        
        # حفظ في قاعدة البيانات
        from database import db_manager
        success = db_manager.create_user(user_id, api_key, api_secret)
        
        if success:
            print("تم حفظ المستخدم في قاعدة البيانات بنجاح!")
        else:
            print("فشل في حفظ المستخدم في قاعدة البيانات")
        
        print("تم إنشاء المستخدم بنجاح!")
        print()
        
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
        print("=== تم إنشاء المستخدم بنجاح ===")
        print(f"User ID: {user_id}")
        print("يمكنك الآن استخدام هذا المستخدم لتنفيذ الإشارات")
        
        return True
        
    except Exception as e:
        print(f"خطأ في إنشاء المستخدم: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_real_user()
    if not success:
        sys.exit(1)
