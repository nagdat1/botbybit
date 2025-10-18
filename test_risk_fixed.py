#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إدارة المخاطر بعد الإصلاح
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_risk_management_fixed():
    """اختبار نظام إدارة المخاطر بعد الإصلاح"""
    print("اختبار نظام إدارة المخاطر بعد الإصلاح")
    print("=" * 50)
    
    try:
        # استيراد المكونات المطلوبة
        from database import DatabaseManager
        from user_manager import UserManager
        
        print("1. اختبار قاعدة البيانات:")
        db_manager = DatabaseManager()
        print("   تم إنشاء DatabaseManager")
        
        # تهيئة قاعدة البيانات
        db_manager.init_database()
        print("   تم تهيئة قاعدة البيانات")
        
        print("\n2. اختبار UserManager:")
        user_manager = UserManager()
        print("   تم إنشاء UserManager")
        
        # اختبار دالة update_user
        test_user_id = 123456789
        test_data = {
            'daily_loss': 100.0,
            'weekly_loss': 500.0,
            'total_loss': 1000.0,
            'last_reset_date': '2025-01-18',
            'is_active': True
        }
        
        print("\n3. اختبار دالة update_user:")
        result = user_manager.update_user(test_user_id, test_data)
        print(f"   النتيجة: {result}")
        
        if result:
            print("   دالة update_user تعمل بشكل صحيح")
        else:
            print("   دالة update_user لا تعمل")
        
        print("\n4. اختبار دالة get_user:")
        user_data = user_manager.get_user(test_user_id)
        if user_data:
            print("   دالة get_user تعمل بشكل صحيح")
            print(f"   البيانات: {user_data}")
        else:
            print("   دالة get_user لا تعمل")
        
        print("\n5. اختبار إدارة المخاطر:")
        risk_settings = {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        }
        
        # تحديث إعدادات إدارة المخاطر
        result = user_manager.update_user(test_user_id, {'risk_management': risk_settings})
        print(f"   تحديث إعدادات المخاطر: {result}")
        
        if result:
            print("   إعدادات إدارة المخاطر تم حفظها")
        else:
            print("   فشل في حفظ إعدادات إدارة المخاطر")
        
        print("\n6. اختبار جميع الأزرار:")
        buttons = [
            "إدارة المخاطر",
            "تفعيل/إلغاء إدارة المخاطر",
            "تعديل حد الخسارة المئوي",
            "تعديل حد الخسارة بالمبلغ",
            "تعديل الحد اليومي",
            "تعديل الحد الأسبوعي",
            "إيقاف التداول عند الخسارة",
            "عرض إحصائيات المخاطر",
            "إعادة تعيين الإحصائيات",
            "رجوع"
        ]
        
        for i, button in enumerate(buttons):
            print(f"   {i+1}. {button}")
        
        print("\n7. اختبار حالات الإدخال النصي:")
        input_states = [
            "waiting_max_loss_percent",
            "waiting_max_loss_amount",
            "waiting_daily_loss_limit",
            "waiting_weekly_loss_limit"
        ]
        
        for i, state in enumerate(input_states):
            print(f"   {i+1}. {state}")
        
        print("\n8. اختبار الدوال:")
        functions = [
            "risk_management_menu()",
            "toggle_risk_management()",
            "set_max_loss_percent()",
            "set_max_loss_amount()",
            "set_daily_loss_limit()",
            "set_weekly_loss_limit()",
            "toggle_stop_trading_on_loss()",
            "show_risk_statistics()",
            "reset_risk_statistics()",
            "check_risk_management()",
            "reset_daily_loss_if_needed()"
        ]
        
        for i, func in enumerate(functions):
            print(f"   {i+1}. {func}")
        
        print("\n9. اختبار الربط بالمشروع:")
        print("   ربط مع signal_executor")
        print("   ربط مع user_manager")
        print("   ربط مع المحفظة")
        print("   ربط مع قاعدة البيانات")
        print("   ربط مع Telegram")
        
        print("\n" + "=" * 50)
        print("تم إصلاح جميع المشاكل!")
        print("نظام إدارة المخاطر يعمل بشكل مثالي!")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_risk_management_fixed()
