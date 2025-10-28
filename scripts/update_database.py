#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث قاعدة البيانات لضمان الإعدادات الصحيحة
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def update_database_settings():
    """تحديث إعدادات قاعدة البيانات لجميع المستخدمين"""
    
    print("=== تحديث إعدادات قاعدة البيانات ===")
    print()
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # التحقق من وجود الجدول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ جدول المستخدمين غير موجود!")
            return False
        
        # الحصول على جميع المستخدمين
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("📭 لا يوجد مستخدمين في قاعدة البيانات")
            return True
        
        print(f"👥 تم العثور على {len(users)} مستخدم")
        print()
        
        # الإعدادات الجديدة المحدثة
        new_settings = {
            'account_type': 'real',
            'market_type': 'futures', 
            'exchange': 'bybit',
            'trade_amount': 50.0,
            'leverage': 2,
            'min_quantity': 0.001,
            'auto_trade': True,
            'notifications': True
        }
        
        updated_count = 0
        
        for (user_id,) in users:
            print(f"تحديث المستخدم {user_id}...")
            
            # تحديث كل إعداد
            for key, value in new_settings.items():
                if key == 'min_quantity':
                    # إضافة عمود جديد إذا لم يكن موجوداً
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {key} REAL DEFAULT 0.001")
                        print(f"  ✅ تم إضافة عمود {key}")
                    except sqlite3.OperationalError:
                        pass  # العمود موجود بالفعل
                
                elif key in ['auto_trade', 'notifications']:
                    # إضافة عمود جديد إذا لم يكن موجوداً
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {key} BOOLEAN DEFAULT 1")
                        print(f"  ✅ تم إضافة عمود {key}")
                    except sqlite3.OperationalError:
                        pass  # العمود موجود بالفعل
                
                # تحديث القيمة
                cursor.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
            
            # تحديث وقت التحديث
            cursor.execute("UPDATE users SET updated_at = ? WHERE user_id = ?", (datetime.now().isoformat(), user_id))
            
            updated_count += 1
            print(f"  ✅ تم تحديث المستخدم {user_id}")
        
        # حفظ التغييرات
        conn.commit()
        conn.close()
        
        print()
        print(f"✅ تم تحديث {updated_count} مستخدم بنجاح!")
        print()
        print("الإعدادات المحدثة:")
        for key, value in new_settings.items():
            print(f"  • {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        return False

def verify_database_structure():
    """التحقق من هيكل قاعدة البيانات"""
    
    print("=== التحقق من هيكل قاعدة البيانات ===")
    print()
    
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # الحصول على أسماء الأعمدة
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("الأعمدة الموجودة:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحقق من قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("اختيار العملية:")
    print("1. تحديث إعدادات قاعدة البيانات")
    print("2. التحقق من هيكل قاعدة البيانات")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = update_database_settings()
    elif choice == "2":
        success = verify_database_structure()
    else:
        print("اختيار غير صحيح")
        success = False
    
    if success:
        print("العملية نجحت!")
    else:
        print("العملية فشلت!")
