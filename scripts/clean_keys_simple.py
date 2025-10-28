#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
حذف المفاتيح القديمة واستبدالها بالمفاتيح الجديدة - مبسط
"""

import sqlite3
from datetime import datetime

def clean_and_update_keys_simple():
    """حذف المفاتيح القديمة واستبدالها بالمفاتيح الجديدة - مبسط"""
    
    print("=" * 60)
    print("حذف المفاتيح القديمة واستبدالها بالمفاتيح الجديدة")
    print("=" * 60)
    print()
    
    # المفاتيح الجديدة المختبرة
    NEW_BYBIT_API_KEY = "RKk6fTapgDqys6vt5S"
    NEW_BYBIT_API_SECRET = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print(f"المفاتيح الجديدة:")
    print(f"  Bybit API Key: {NEW_BYBIT_API_KEY}")
    print(f"  Bybit API Secret: {NEW_BYBIT_API_SECRET[:10]}...")
    print()
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # 1. حذف جميع المفاتيح القديمة
        print("1. حذف جميع المفاتيح القديمة...")
        
        # حذف مفاتيح Bybit القديمة
        cursor.execute("UPDATE users SET bybit_api_key = NULL, bybit_api_secret = NULL")
        
        # حذف مفاتيح MEXC القديمة  
        cursor.execute("UPDATE users SET mexc_api_key = NULL, mexc_api_secret = NULL")
        
        # حذف المفاتيح العامة القديمة
        cursor.execute("UPDATE users SET api_key = NULL, api_secret = NULL")
        
        print("   تم حذف جميع المفاتيح القديمة")
        print()
        
        # 2. إضافة المفاتيح الجديدة للمستخدم الرئيسي
        print("2. إضافة المفاتيح الجديدة للمستخدم الرئيسي...")
        
        user_id = 8169000394
        
        # التحقق من وجود المستخدم
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            print(f"   إنشاء مستخدم جديد: {user_id}")
            cursor.execute("""
                INSERT INTO users (user_id, balance, is_active, notifications, created_at, updated_at)
                VALUES (?, 10000.0, 1, 1, ?, ?)
            """, (user_id, datetime.now().isoformat(), datetime.now().isoformat()))
        
        # إضافة المفاتيح الجديدة
        cursor.execute("""
            UPDATE users 
            SET bybit_api_key = ?, bybit_api_secret = ?, updated_at = ?
            WHERE user_id = ?
        """, (NEW_BYBIT_API_KEY, NEW_BYBIT_API_SECRET, datetime.now().isoformat(), user_id))
        
        print(f"   تم إضافة المفاتيح الجديدة للمستخدم {user_id}")
        print()
        
        # 3. التحقق من التحديث
        print("3. التحقق من التحديث...")
        
        cursor.execute("""
            SELECT user_id, bybit_api_key, bybit_api_secret 
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        updated_user = cursor.fetchone()
        
        if updated_user:
            print(f"   بيانات المستخدم المحدثة:")
            print(f"     user_id: {updated_user[0]}")
            print(f"     bybit_api_key: {updated_user[1]}")
            print(f"     bybit_api_secret: {updated_user[2][:10] if updated_user[2] else 'None'}...")
        
        # حفظ التغييرات
        conn.commit()
        conn.close()
        
        print()
        print("=" * 60)
        print("تم التحديث بنجاح!")
        print("=" * 60)
        print()
        print("النتيجة:")
        print("تم حذف جميع المفاتيح القديمة")
        print("تم إضافة المفاتيح الجديدة المختبرة")
        print()
        print("البوت الآن جاهز للتداول مع المفاتيح الجديدة!")
        
        return True
        
    except Exception as e:
        print(f"خطأ في التحديث: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_final_result():
    """التحقق من النتيجة النهائية"""
    
    print("=" * 60)
    print("التحقق من النتيجة النهائية")
    print("=" * 60)
    print()
    
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # فحص المستخدم الرئيسي
        cursor.execute("""
            SELECT user_id, bybit_api_key, bybit_api_secret, mexc_api_key, mexc_api_secret, api_key, api_secret
            FROM users WHERE user_id = 8169000394
        """)
        
        user = cursor.fetchone()
        
        if user:
            print(f"المستخدم الرئيسي (8169000394):")
            print(f"  bybit_api_key: {user[1] or 'None'}")
            print(f"  bybit_api_secret: {user[2][:10] + '...' if user[2] else 'None'}")
            print(f"  mexc_api_key: {user[3] or 'None'}")
            print(f"  mexc_api_secret: {user[4][:10] + '...' if user[4] else 'None'}")
            print(f"  api_key: {user[5] or 'None'}")
            print(f"  api_secret: {user[6][:10] + '...' if user[6] else 'None'}")
            print()
            
            # التحقق من نجاح التحديث
            if user[1] == "RKk6fTapgDqys6vt5S" and user[2] == "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp":
                print("✅ تم تحديث المفاتيح بنجاح!")
                print("✅ البوت الآن يستخدم المفاتيح الجديدة المختبرة!")
            else:
                print("❌ فشل في تحديث المفاتيح!")
        else:
            print("❌ المستخدم الرئيسي غير موجود!")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ في التحقق: {e}")

if __name__ == "__main__":
    # تشغيل التحديث تلقائياً
    success = clean_and_update_keys_simple()
    
    if success:
        print("\nالعملية نجحت!")
        print("\nالتحقق من النتيجة النهائية:")
        verify_final_result()
    else:
        print("\nالعملية فشلت!")
