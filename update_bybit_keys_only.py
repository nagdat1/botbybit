#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث مفاتيح Bybit API فقط
"""

import sqlite3
from datetime import datetime

def update_bybit_keys_only():
    """تحديث مفاتيح Bybit API فقط"""
    
    print("=== تحديث مفاتيح Bybit API فقط ===")
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
        
        # تحديث مفاتيح Bybit فقط
        print("تحديث مفاتيح Bybit...")
        cursor.execute("""
            UPDATE users 
            SET bybit_api_key = ?, bybit_api_secret = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_api_key, new_api_secret, datetime.now().isoformat(), user_id))
        
        conn.commit()
        
        # التحقق من التحديث
        cursor.execute("SELECT bybit_api_key, bybit_api_secret FROM users WHERE user_id = ?", (user_id,))
        updated_user = cursor.fetchone()
        
        conn.close()
        
        print("تم التحديث بنجاح!")
        print()
        print("=" * 50)
        print("المفاتيح المحدثة:")
        print("=" * 50)
        print(f"• Bybit API Key: {updated_user[0]}")
        print(f"• Bybit API Secret: {updated_user[1][:10] if updated_user[1] else 'None'}...")
        
        return True
        
    except Exception as e:
        print(f"خطأ في تحديث المفاتيح: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_bybit_keys_only()
    
    if success:
        print("\nالعملية نجحت! البوت الآن يستخدم المفاتيح الجديدة.")
        print("يمكنك الآن إرسال إشارة جديدة وسيتم تنفيذها بنجاح!")
    else:
        print("\nالعملية فشلت!")
        sys.exit(1)
