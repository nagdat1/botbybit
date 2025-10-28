#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث مفاتيح API للمستخدم تلقائياً
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

def update_user_api_keys_auto():
    """تحديث مفاتيح API للمستخدم تلقائياً"""
    
    print("=== تحديث مفاتيح API للمستخدم تلقائياً ===")
    print()
    
    # المفاتيح الجديدة المختبرة
    new_api_key = "RKk6fTapgDqys6vt5S"
    new_api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print(f"API Key الجديد: {new_api_key}")
    print(f"API Secret الجديد: {new_api_secret[:10]}...")
    print()
    
    # معرف المستخدم الرئيسي
    user_id = 8169000394
    
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
            print(f"• API Secret: {final_user.get('bybit_api_secret', 'N/A')[:10] if final_user.get('bybit_api_secret') else 'N/A'}...")
            
            return True
        else:
            print("فشل في تحديث المفاتيح!")
            return False
            
    except Exception as e:
        print(f"خطأ في تحديث المفاتيح: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_user_api_keys_auto()
    
    if success:
        print("\nالعملية نجحت! البوت الآن يستخدم المفاتيح الجديدة.")
    else:
        print("\nالعملية فشلت!")
        sys.exit(1)
