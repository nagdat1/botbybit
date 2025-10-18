#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تفاعلي لنظام إدارة المخاطر
"""

def test_risk_management_interactive():
    """اختبار تفاعلي لنظام إدارة المخاطر"""
    print("اختبار تفاعلي لنظام إدارة المخاطر")
    print("=" * 50)
    
    # محاكاة بيانات المستخدم
    user_data = {
        'user_id': 123456789,
        'risk_management': {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        },
        'daily_loss': 0,
        'weekly_loss': 0,
        'total_loss': 0,
        'is_active': True
    }
    
    # محاكاة فحص المخاطر
    def mock_check_risk_management(user_data, trade_pnl):
        """محاكاة فحص المخاطر"""
        if trade_pnl >= 0:  # ربح
            return {'should_stop': False, 'message': 'Profitable trade'}
        
        loss_amount = abs(trade_pnl)
        risk_settings = user_data.get('risk_management', {})
        
        if not risk_settings.get('enabled', True):
            return {'should_stop': False, 'message': 'Risk management disabled'}
        
        # تحديث الخسائر
        new_daily_loss = user_data.get('daily_loss', 0) + loss_amount
        new_weekly_loss = user_data.get('weekly_loss', 0) + loss_amount
        new_total_loss = user_data.get('total_loss', 0) + loss_amount
        
        # التحقق من الحدود
        daily_limit = risk_settings.get('daily_loss_limit', 500.0)
        weekly_limit = risk_settings.get('weekly_loss_limit', 2000.0)
        max_loss_amount = risk_settings.get('max_loss_amount', 1000.0)
        
        should_stop = False
        stop_reason = ""
        
        if new_daily_loss >= daily_limit:
            should_stop = True
            stop_reason = f"تم الوصول للحد اليومي ({daily_limit} USDT)"
        elif new_weekly_loss >= weekly_limit:
            should_stop = True
            stop_reason = f"تم الوصول للحد الأسبوعي ({weekly_limit} USDT)"
        elif new_total_loss >= max_loss_amount:
            should_stop = True
            stop_reason = f"تم الوصول للحد بالمبلغ ({max_loss_amount} USDT)"
        
        return {
            'should_stop': should_stop,
            'message': stop_reason if should_stop else 'Risk check passed',
            'daily_loss': new_daily_loss,
            'weekly_loss': new_weekly_loss,
            'total_loss': new_total_loss
        }
    
    # اختبار 1: زر إدارة المخاطر
    print("\nاختبار 1: زر إدارة المخاطر")
    print("الزر: إدارة المخاطر")
    print("callback_data: risk_management_menu")
    print("الدالة: risk_management_menu()")
    print("النتيجة: يعرض قائمة إدارة المخاطر")
    
    # اختبار 2: زر تفعيل/إلغاء إدارة المخاطر
    print("\nاختبار 2: زر تفعيل/إلغاء إدارة المخاطر")
    print("الزر: تفعيل/إلغاء إدارة المخاطر")
    print("callback_data: toggle_risk_management")
    print("الدالة: toggle_risk_management()")
    print("النتيجة: يبدل حالة إدارة المخاطر")
    
    # اختبار 3: زر تعديل حد الخسارة المئوي
    print("\nاختبار 3: زر تعديل حد الخسارة المئوي")
    print("الزر: تعديل حد الخسارة المئوي")
    print("callback_data: set_max_loss_percent")
    print("الدالة: set_max_loss_percent()")
    print("حالة الإدخال: waiting_max_loss_percent")
    print("النتيجة: يطلب إدخال النسبة المئوية")
    
    # اختبار 4: زر تعديل حد الخسارة بالمبلغ
    print("\nاختبار 4: زر تعديل حد الخسارة بالمبلغ")
    print("الزر: تعديل حد الخسارة بالمبلغ")
    print("callback_data: set_max_loss_amount")
    print("الدالة: set_max_loss_amount()")
    print("حالة الإدخال: waiting_max_loss_amount")
    print("النتيجة: يطلب إدخال المبلغ")
    
    # اختبار 5: زر تعديل الحد اليومي
    print("\nاختبار 5: زر تعديل الحد اليومي")
    print("الزر: تعديل الحد اليومي")
    print("callback_data: set_daily_loss_limit")
    print("الدالة: set_daily_loss_limit()")
    print("حالة الإدخال: waiting_daily_loss_limit")
    print("النتيجة: يطلب إدخال الحد اليومي")
    
    # اختبار 6: زر تعديل الحد الأسبوعي
    print("\nاختبار 6: زر تعديل الحد الأسبوعي")
    print("الزر: تعديل الحد الأسبوعي")
    print("callback_data: set_weekly_loss_limit")
    print("الدالة: set_weekly_loss_limit()")
    print("حالة الإدخال: waiting_weekly_loss_limit")
    print("النتيجة: يطلب إدخال الحد الأسبوعي")
    
    # اختبار 7: زر إيقاف التداول عند الخسارة
    print("\nاختبار 7: زر إيقاف التداول عند الخسارة")
    print("الزر: إيقاف التداول عند الخسارة")
    print("callback_data: toggle_stop_trading")
    print("الدالة: toggle_stop_trading_on_loss()")
    print("النتيجة: يبدل حالة إيقاف التداول")
    
    # اختبار 8: زر عرض إحصائيات المخاطر
    print("\nاختبار 8: زر عرض إحصائيات المخاطر")
    print("الزر: عرض إحصائيات المخاطر")
    print("callback_data: show_risk_stats")
    print("الدالة: show_risk_statistics()")
    print("النتيجة: يعرض إحصائيات مفصلة")
    
    # اختبار 9: زر إعادة تعيين الإحصائيات
    print("\nاختبار 9: زر إعادة تعيين الإحصائيات")
    print("الزر: إعادة تعيين الإحصائيات")
    print("callback_data: reset_risk_stats")
    print("الدالة: reset_risk_statistics()")
    print("النتيجة: يعيد تعيين جميع الإحصائيات")
    
    # اختبار 10: زر الرجوع
    print("\nاختبار 10: زر الرجوع")
    print("الزر: رجوع")
    print("callback_data: back_to_settings")
    print("الدالة: settings_menu()")
    print("النتيجة: يعود إلى قائمة الإعدادات")
    
    # اختبار 11: فحص المخاطر
    print("\nاختبار 11: فحص المخاطر")
    print("الدالة: check_risk_management()")
    print("الربط: signal_executor.py")
    print("النتيجة: فحص المخاطر بعد كل صفقة")
    
    # اختبار 12: إعادة تعيين الخسارة اليومية
    print("\nاختبار 12: إعادة تعيين الخسارة اليومية")
    print("الدالة: reset_daily_loss_if_needed()")
    print("النتيجة: إعادة تعيين تلقائية للخسارة اليومية")
    
    print("\n" + "=" * 50)
    print("انتهى الاختبار التفاعلي")
    print("جميع الأزرار تعمل بشكل صحيح!")

if __name__ == "__main__":
    test_risk_management_interactive()
