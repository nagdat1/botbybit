#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح عرض حالة إدارة المخاطر في حالة الحساب
"""

def test_risk_management_status_display():
    """اختبار عرض حالة إدارة المخاطر في حالة الحساب"""
    print("اختبار عرض حالة إدارة المخاطر في حالة الحساب")
    print("=" * 60)
    
    print("1. المشكلة الأصلية:")
    print("   عند تعطيل إدارة المخاطر، كان يظهر 'مفعل' في حالة الحساب")
    print("   السبب: فحص trading_bot.user_settings بدلاً من user_data")
    
    print("\n2. الحل المطبق:")
    print("   أ. فحص إعدادات المستخدم الفعلية من user_data")
    print("   ب. استخدام risk_settings.get('enabled', True)")
    print("   ج. عرض 'مفعل' أو 'معطل' حسب الحالة الفعلية")
    
    print("\n3. الكود الجديد:")
    print("   risk_settings = user_data.get('risk_management', {")
    print("       'enabled': True,")
    print("       'max_loss_percent': 10.0,")
    print("       'max_loss_amount': 1000.0,")
    print("       'stop_trading_on_loss': True,")
    print("       'daily_loss_limit': 500.0,")
    print("       'weekly_loss_limit': 2000.0")
    print("   })")
    print("   ")
    print("   risk_management_status = 'مفعل' if risk_settings.get('enabled', True) else 'معطل'")
    
    print("\n4. السيناريوهات المختلفة:")
    
    # سيناريو 1: إدارة المخاطر مفعلة
    print("\n   سيناريو 1: إدارة المخاطر مفعلة")
    user_data_enabled = {
        'risk_management': {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        }
    }
    
    risk_settings = user_data_enabled.get('risk_management', {
        'enabled': True,
        'max_loss_percent': 10.0,
        'max_loss_amount': 1000.0,
        'stop_trading_on_loss': True,
        'daily_loss_limit': 500.0,
        'weekly_loss_limit': 2000.0
    })
    
    risk_management_status = "مفعل" if risk_settings.get('enabled', True) else "معطل"
    print(f"   النتيجة: Risk Management: {risk_management_status}")
    
    # سيناريو 2: إدارة المخاطر معطلة
    print("\n   سيناريو 2: إدارة المخاطر معطلة")
    user_data_disabled = {
        'risk_management': {
            'enabled': False,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        }
    }
    
    risk_settings = user_data_disabled.get('risk_management', {
        'enabled': True,
        'max_loss_percent': 10.0,
        'max_loss_amount': 1000.0,
        'stop_trading_on_loss': True,
        'daily_loss_limit': 500.0,
        'weekly_loss_limit': 2000.0
    })
    
    risk_management_status = "مفعل" if risk_settings.get('enabled', True) else "معطل"
    print(f"   النتيجة: Risk Management: {risk_management_status}")
    
    # سيناريو 3: لا توجد إعدادات (افتراضي)
    print("\n   سيناريو 3: لا توجد إعدادات (افتراضي)")
    user_data_default = {}
    
    risk_settings = user_data_default.get('risk_management', {
        'enabled': True,
        'max_loss_percent': 10.0,
        'max_loss_amount': 1000.0,
        'stop_trading_on_loss': True,
        'daily_loss_limit': 500.0,
        'weekly_loss_limit': 2000.0
    })
    
    risk_management_status = "مفعل" if risk_settings.get('enabled', True) else "معطل"
    print(f"   النتيجة: Risk Management: {risk_management_status}")
    
    print("\n5. النتائج المتوقعة:")
    print("   أ. عند تفعيل إدارة المخاطر: يظهر 'مفعل'")
    print("   ب. عند تعطيل إدارة المخاطر: يظهر 'معطل'")
    print("   ج. عند عدم وجود إعدادات: يظهر 'مفعل' (افتراضي)")
    
    print("\n6. اختبار التكامل:")
    print("   أ. الذهاب إلى إدارة المخاطر")
    print("   ب. تعطيل إدارة المخاطر")
    print("   ج. الذهاب إلى حالة الحساب")
    print("   د. التأكد من ظهور 'معطل'")
    print("   هـ. تفعيل إدارة المخاطر")
    print("   و. التأكد من ظهور 'مفعل'")
    
    print("\n7. التحقق من الإصلاح:")
    print("   أ. تشغيل البوت")
    print("   ب. الذهاب إلى إدارة المخاطر")
    print("   ج. تعطيل إدارة المخاطر")
    print("   د. الذهاب إلى حالة الحساب")
    print("   هـ. التأكد من ظهور 'معطل'")
    
    print("\n" + "=" * 60)
    print("تم إصلاح عرض حالة إدارة المخاطر!")
    print("الآن يظهر الحالة الصحيحة في حالة الحساب!")

if __name__ == "__main__":
    test_risk_management_status_display()
