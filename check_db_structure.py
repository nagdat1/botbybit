#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_database_structure():
    """فحص هيكل قاعدة البيانات"""
    
    print("=== فحص هيكل قاعدة البيانات ===")
    print()
    
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # فحص أعمدة جدول المستخدمين
        cursor.execute('PRAGMA table_info(users)')
        columns = cursor.fetchall()
        
        print("الأعمدة الموجودة في جدول users:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        print()
        
        # فحص بيانات المستخدم
        cursor.execute("SELECT user_id, bybit_api_key, bybit_api_secret FROM users WHERE user_id = 8169000394")
        user = cursor.fetchone()
        
        if user:
            print(f"بيانات المستخدم 8169000394:")
            print(f"  user_id: {user[0]}")
            print(f"  bybit_api_key: {user[1]}")
            print(f"  bybit_api_secret: {user[2][:10] if user[2] else 'None'}...")
        else:
            print("المستخدم 8169000394 غير موجود")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    check_database_structure()
