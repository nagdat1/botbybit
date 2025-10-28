#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
حذف المفاتيح القديمة واستبدالها بالمفاتيح الجديدة المختبرة
"""

import sqlite3
import os
from datetime import datetime

def clean_and_update_all_keys():
    """حذف جميع المفاتيح القديمة واستبدالها بالمفاتيح الجديدة"""
    
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
        cursor.execute("""
            UPDATE users 
            SET bybit_api_key = NULL, bybit_api_secret = NULL
        """)
        
        # حذف مفاتيح MEXC القديمة
        cursor.execute("""
            UPDATE users 
            SET mexc_api_key = NULL, mexc_api_secret = NULL
        """)
        
        # حذف المفاتيح العامة القديمة
        cursor.execute("""
            UPDATE users 
            SET api_key = NULL, api_secret = NULL
        """)
        
        print("   ✅ تم حذف جميع المفاتيح القديمة")
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
        
        print(f"   ✅ تم إضافة المفاتيح الجديدة للمستخدم {user_id}")
        print()
        
        # 3. تحديث الإعدادات الافتراضية
        print("3. تحديث الإعدادات الافتراضية...")
        
        # تحديث إعدادات التداول
        cursor.execute("""
            UPDATE users 
            SET exchange = ?, trade_amount = ?, leverage = ?
            WHERE user_id = ?
        """, ('bybit', 50.0, 2, user_id))
        
        print("   ✅ تم تحديث الإعدادات الافتراضية")
        print()
        
        # 4. التحقق من التحديث
        print("4. التحقق من التحديث...")
        
        cursor.execute("""
            SELECT user_id, bybit_api_key, bybit_api_secret, exchange, trade_amount, leverage 
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        updated_user = cursor.fetchone()
        
        if updated_user:
            print(f"   بيانات المستخدم المحدثة:")
            print(f"     user_id: {updated_user[0]}")
            print(f"     bybit_api_key: {updated_user[1]}")
            print(f"     bybit_api_secret: {updated_user[2][:10] if updated_user[2] else 'None'}...")
            print(f"     exchange: {updated_user[3]}")
            print(f"     trade_amount: {updated_user[4]}")
            print(f"     leverage: {updated_user[5]}")
        
        # حفظ التغييرات
        conn.commit()
        conn.close()
        
        print()
        print("=" * 60)
        print("تم التحديث بنجاح!")
        print("=" * 60)
        print()
        print("النتيجة:")
        print("✅ تم حذف جميع المفاتيح القديمة")
        print("✅ تم إضافة المفاتيح الجديدة المختبرة")
        print("✅ تم تحديث الإعدادات الافتراضية")
        print()
        print("البوت الآن جاهز للتداول مع المفاتيح الجديدة!")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحديث: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_cleanup():
    """التحقق من تنظيف المفاتيح"""
    
    print("=" * 60)
    print("التحقق من تنظيف المفاتيح")
    print("=" * 60)
    print()
    
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # فحص جميع المستخدمين
        cursor.execute("""
            SELECT user_id, bybit_api_key, bybit_api_secret, mexc_api_key, mexc_api_secret, api_key, api_secret
            FROM users
        """)
        
        users = cursor.fetchall()
        
        print(f"عدد المستخدمين: {len(users)}")
        print()
        
        for user in users:
            user_id = user[0]
            bybit_key = user[1]
            bybit_secret = user[2]
            mexc_key = user[3]
            mexc_secret = user[4]
            api_key = user[5]
            api_secret = user[6]
            
            print(f"المستخدم {user_id}:")
            print(f"  bybit_api_key: {bybit_key or 'None'}")
            print(f"  bybit_api_secret: {bybit_secret[:10] + '...' if bybit_secret else 'None'}")
            print(f"  mexc_api_key: {mexc_key or 'None'}")
            print(f"  mexc_api_secret: {mexc_secret[:10] + '...' if mexc_secret else 'None'}")
            print(f"  api_key: {api_key or 'None'}")
            print(f"  api_secret: {api_secret[:10] + '...' if api_secret else 'None'}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في التحقق: {e}")

if __name__ == "__main__":
    print("اختيار العملية:")
    print("1. حذف المفاتيح القديمة وإضافة الجديدة")
    print("2. التحقق من تنظيف المفاتيح")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = clean_and_update_all_keys()
    elif choice == "2":
        verify_cleanup()
        success = True
    else:
        print("اختيار غير صحيح")
        success = False
    
    if success:
        print("\n🎉 العملية نجحت!")
    else:
        print("\n❌ العملية فشلت!")
        sys.exit(1)
