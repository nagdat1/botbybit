#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث نوع السوق إلى Futures للمستخدم
"""

import sys
import os

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def update_market_type_to_futures():
    """تحديث نوع السوق إلى Futures للمستخدم"""
    
    print("=== تحديث نوع السوق إلى Futures ===")
    print()
    
    try:
        # تحديث نوع السوق إلى futures
        success = db_manager.update_user_settings(999999, {
            'market_type': 'futures'
        })
        
        if success:
            print("تم تحديث نوع السوق إلى Futures بنجاح!")
            print()
            print("الآن البوت سيستخدم Futures بدلاً من Spot")
            print()
            print("الخطوات التالية:")
            print("1. أعد تشغيل البوت")
            print("2. جرب وضع إشارة جديدة")
            print("3. يجب أن تعمل الآن!")
            print()
        else:
            print("فشل في تحديث نوع السوق")
            print()
            
    except Exception as e:
        print(f"خطأ في تحديث نوع السوق: {e}")
        print()
    
    return True

if __name__ == "__main__":
    success = update_market_type_to_futures()
    if not success:
        sys.exit(1)
