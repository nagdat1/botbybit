#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت للتحقق من الصفقات المرتبطة بالـ Signal ID
"""

import sqlite3
from datetime import datetime

def check_signal_positions():
    """التحقق من جدول signal_positions"""
    try:
        conn = sqlite3.connect('trading_bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 80)
        print("🔍 فحص جدول signal_positions")
        print("=" * 80)
        print()
        
        # عد جميع الصفقات
        cursor.execute("SELECT COUNT(*) as count FROM signal_positions")
        total = cursor.fetchone()['count']
        print(f"📊 إجمالي الصفقات: {total}")
        print()
        
        # عد الصفقات المفتوحة
        cursor.execute("SELECT COUNT(*) as count FROM signal_positions WHERE status = 'OPEN'")
        open_count = cursor.fetchone()['count']
        print(f"🟢 الصفقات المفتوحة: {open_count}")
        print()
        
        # عد الصفقات المغلقة
        cursor.execute("SELECT COUNT(*) as count FROM signal_positions WHERE status = 'CLOSED'")
        closed_count = cursor.fetchone()['count']
        print(f"🔴 الصفقات المغلقة: {closed_count}")
        print()
        
        # عرض جميع الصفقات المفتوحة
        if open_count > 0:
            print("=" * 80)
            print("📋 الصفقات المفتوحة:")
            print("=" * 80)
            cursor.execute("""
                SELECT signal_id, user_id, symbol, side, entry_price, quantity, 
                       market_type, created_at, status
                FROM signal_positions 
                WHERE status = 'OPEN'
                ORDER BY created_at DESC
            """)
            
            for row in cursor.fetchall():
                print(f"""
🆔 Signal ID: {row['signal_id']}
👤 User ID: {row['user_id']}
💰 Symbol: {row['symbol']}
📊 Side: {row['side']}
💵 Entry Price: {row['entry_price']}
📦 Quantity: {row['quantity']}
🏪 Market Type: {row['market_type']}
📅 Created: {row['created_at']}
✅ Status: {row['status']}
{'-' * 80}
                """)
        
        # البحث عن Signal ID: 4
        print("=" * 80)
        print("🔍 البحث عن Signal ID: 4")
        print("=" * 80)
        cursor.execute("""
            SELECT * FROM signal_positions 
            WHERE signal_id = '4'
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        if rows:
            print(f"✅ تم العثور على {len(rows)} صفقة مرتبطة بـ Signal ID: 4")
            for row in rows:
                print(f"""
🆔 Signal ID: {row['signal_id']}
👤 User ID: {row['user_id']}
💰 Symbol: {row['symbol']}
📊 Side: {row['side']}
💵 Entry Price: {row['entry_price']}
📦 Quantity: {row['quantity']}
🏪 Market Type: {row['market_type']}
📅 Created: {row['created_at']}
✅ Status: {row['status']}
{'-' * 80}
                """)
        else:
            print("❌ لم يتم العثور على أي صفقات مرتبطة بـ Signal ID: 4")
            print()
            print("💡 الأسباب المحتملة:")
            print("   1. لم يتم فتح صفقة بهذا الـ ID")
            print("   2. تم إغلاق الصفقة بالفعل")
            print("   3. تم حذف البيانات من قاعدة البيانات")
            print("   4. الصفقة تم فتحها بدون Signal ID")
        
        print()
        print("=" * 80)
        print("🔍 عرض آخر 10 صفقات:")
        print("=" * 80)
        cursor.execute("""
            SELECT signal_id, user_id, symbol, side, status, created_at
            FROM signal_positions 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"{i}. ID:{row['signal_id']} | {row['symbol']} | {row['side']} | {row['status']} | {row['created_at']}")
        else:
            print("❌ لا توجد صفقات في قاعدة البيانات")
        
        print()
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    check_signal_positions()

