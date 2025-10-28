#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث مفاتيح Bybit API للمستخدم مباشرة في قاعدة البيانات
"""

import sys
import os
import sqlite3
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_bybit_api_direct():
    """تحديث مفاتيح Bybit API مباشرة في قاعدة البيانات"""
    
    print("=== تحديث مفاتيح Bybit API مباشرة ===")
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
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # التحقق من وجود المستخدم
        cursor.execute("SELECT user_id, bybit_api_key, bybit_api_secret FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"المستخدم {user_id} غير موجود!")
            return False
        
        print(f"المستخدم موجود: {user_id}")
        print(f"المفاتيح الحالية:")
        print(f"  Bybit API Key: {user[1] or 'None'}")
        print(f"  Bybit API Secret: {user[2][:10] if user[2] else 'None'}...")
        print()
        
        # تحديث مفاتيح Bybit مباشرة
        print("تحديث مفاتيح Bybit...")
        cursor.execute("""
            UPDATE users 
            SET bybit_api_key = ?, bybit_api_secret = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_api_key, new_api_secret, datetime.now().isoformat(), user_id))
        
        # تحديث الإعدادات الأخرى
        print("تحديث الإعدادات الأخرى...")
        cursor.execute("""
            UPDATE users 
            SET account_type = ?, market_type = ?, exchange = ?, trade_amount = ?, leverage = ?
            WHERE user_id = ?
        """, ('real', 'futures', 'bybit', 50.0, 2, user_id))
        
        conn.commit()
        
        # التحقق من التحديث
        cursor.execute("SELECT bybit_api_key, bybit_api_secret, account_type, market_type, exchange, trade_amount, leverage FROM users WHERE user_id = ?", (user_id,))
        updated_user = cursor.fetchone()
        
        conn.close()
        
        print("تم التحديث بنجاح!")
        print()
        print("=" * 50)
        print("الإعدادات المحدثة:")
        print("=" * 50)
        print(f"• نوع الحساب: {updated_user[2]}")
        print(f"• نوع السوق: {updated_user[3]}")
        print(f"• المنصة: {updated_user[4]}")
        print(f"• مبلغ التداول: {updated_user[5]} USDT")
        print(f"• الرافعة: {updated_user[6]}x")
        print(f"• Bybit API Key: {updated_user[0]}")
        print(f"• Bybit API Secret: {updated_user[1][:10] if updated_user[1] else 'None'}...")
        
        return True
        
    except Exception as e:
        print(f"خطأ في تحديث المفاتيح: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_bybit_api_direct()
    
    if success:
        print("\nالعملية نجحت! البوت الآن يستخدم المفاتيح الجديدة.")
        print("يمكنك الآن إرسال إشارة جديدة وسيتم تنفيذها بنجاح!")
    else:
        print("\nالعملية فشلت!")
        sys.exit(1)
