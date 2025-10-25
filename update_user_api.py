#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث مفاتيح API للمستخدم في قاعدة البيانات
"""

import sys
import os
import logging

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_user_api_keys():
    """تحديث مفاتيح API للمستخدم"""
    
    print("=== تحديث مفاتيح API للمستخدم ===")
    print()
    
    # المفاتيح الجديدة المختبرة
    new_api_key = "RKk6fTapgDqys6vt5S"
    new_api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print(f"API Key الجديد: {new_api_key}")
    print(f"API Secret الجديد: {new_api_secret[:10]}...")
    print()
    
    # معرف المستخدم (يمكن تغييره حسب الحاجة)
    user_id = 8169000394  # معرف المستخدم الرئيسي
    
    try:
        # التحقق من وجود المستخدم
        user_data = db_manager.get_user(user_id)
        
        if not user_data:
            print(f"المستخدم {user_id} غير موجود. إنشاء مستخدم جديد...")
            db_manager.create_user(user_id)
            user_data = db_manager.get_user(user_id)
        
        print(f"المستخدم موجود: {user_id}")
        print(f"المفاتيح الحالية:")
        print(f"  API Key: {user_data.get('bybit_api_key', 'None')}")
        print(f"  API Secret: {user_data.get('bybit_api_secret', 'None')[:10] if user_data.get('bybit_api_secret') else 'None'}...")
        print()
        
        # تحديث المفاتيح
        print("تحديث المفاتيح...")
        success = db_manager.update_user_api(user_id, new_api_key, new_api_secret)
        
        if success:
            print("تم تحديث المفاتيح بنجاح!")
            
            # التحقق من التحديث
            updated_user = db_manager.get_user(user_id)
            print(f"المفاتيح المحدثة:")
            print(f"  API Key: {updated_user.get('bybit_api_key', 'None')}")
            print(f"  API Secret: {updated_user.get('bybit_api_secret', 'None')[:10] if updated_user.get('bybit_api_secret') else 'None'}...")
            
            # تحديث الإعدادات الأخرى
            print()
            print("تحديث الإعدادات الأخرى...")
            
            settings_update = {
                'account_type': 'real',
                'market_type': 'futures',
                'exchange': 'bybit',
                'trade_amount': 50.0,
                'leverage': 2
            }
            
            settings_success = db_manager.update_user_settings(user_id, settings_update)
            
            if settings_success:
                print("تم تحديث الإعدادات بنجاح!")
            else:
                print("فشل في تحديث الإعدادات!")
            
            print()
            print("=" * 50)
            print("تم التحديث بنجاح!")
            print("=" * 50)
            print()
            print("الإعدادات الجديدة:")
            final_user = db_manager.get_user(user_id)
            print(f"• نوع الحساب: {final_user.get('account_type', 'N/A')}")
            print(f"• نوع السوق: {final_user.get('market_type', 'N/A')}")
            print(f"• المنصة: {final_user.get('exchange', 'N/A')}")
            print(f"• مبلغ التداول: {final_user.get('trade_amount', 'N/A')} USDT")
            print(f"• الرافعة: {final_user.get('leverage', 'N/A')}x")
            print(f"• API Key: {final_user.get('bybit_api_key', 'N/A')}")
            print(f"• API Secret: {final_user.get('bybit_api_secret', 'N/A')[:10]}...")
            
            return True
        else:
            print("فشل في تحديث المفاتيح!")
            return False
            
    except Exception as e:
        print(f"خطأ في تحديث المفاتيح: {e}")
        return False

def check_all_users():
    """فحص جميع المستخدمين"""
    
    print("=== فحص جميع المستخدمين ===")
    print()
    
    try:
        # الحصول على جميع المستخدمين النشطين
        users = db_manager.get_all_active_users()
        
        if not users:
            print("لا يوجد مستخدمين نشطين")
            return
        
        print(f"عدد المستخدمين النشطين: {len(users)}")
        print()
        
        for user in users:
            user_id = user['user_id']
            api_key = user.get('bybit_api_key', 'None')
            api_secret = user.get('bybit_api_secret', 'None')
            account_type = user.get('account_type', 'N/A')
            market_type = user.get('market_type', 'N/A')
            exchange = user.get('exchange', 'N/A')
            
            print(f"المستخدم {user_id}:")
            print(f"  API Key: {api_key}")
            print(f"  API Secret: {api_secret[:10] if api_secret and api_secret != 'None' else 'None'}...")
            print(f"  نوع الحساب: {account_type}")
            print(f"  نوع السوق: {market_type}")
            print(f"  المنصة: {exchange}")
            print()
            
    except Exception as e:
        print(f"خطأ في فحص المستخدمين: {e}")

if __name__ == "__main__":
    print("اختيار العملية:")
    print("1. تحديث مفاتيح API للمستخدم")
    print("2. فحص جميع المستخدمين")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = update_user_api_keys()
    elif choice == "2":
        check_all_users()
        success = True
    else:
        print("اختيار غير صحيح")
        success = False
    
    if success:
        print("\nالعملية نجحت!")
    else:
        print("\nالعملية فشلت!")
