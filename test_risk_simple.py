#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط لنظام إدارة المخاطر
"""

def test_risk_management_simple():
    """اختبار مبسط لنظام إدارة المخاطر"""
    print("اختبار نظام إدارة المخاطر")
    print("=" * 50)
    
    # محاكاة بيانات المستخدم
    user_data = {
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
    
    # اختبار 1: صفقة رابحة
    print("\nاختبار 1: صفقة رابحة")
    result = mock_check_risk_management(user_data, 50.0)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # اختبار 2: خسارة صغيرة
    print("\nاختبار 2: خسارة صغيرة")
    result = mock_check_risk_management(user_data, -50.0)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # تحديث البيانات للاختبار التالي
    user_data['daily_loss'] = result['daily_loss']
    user_data['weekly_loss'] = result['weekly_loss']
    user_data['total_loss'] = result['total_loss']
    
    # اختبار 3: خسارة كبيرة
    print("\nاختبار 3: خسارة كبيرة")
    result = mock_check_risk_management(user_data, -600.0)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # اختبار 4: عرض الإحصائيات
    print("\nاختبار 4: إحصائيات المخاطر")
    risk_settings = user_data.get('risk_management', {})
    print(f"إدارة المخاطر مفعلة: {'نعم' if risk_settings.get('enabled') else 'لا'}")
    print(f"الحد اليومي: {risk_settings.get('daily_loss_limit', 0)} USDT")
    print(f"الحد الأسبوعي: {risk_settings.get('weekly_loss_limit', 0)} USDT")
    print(f"الحد المئوي: {risk_settings.get('max_loss_percent', 0)}%")
    print(f"الحد بالمبلغ: {risk_settings.get('max_loss_amount', 0)} USDT")
    print(f"الخسارة اليومية: {user_data.get('daily_loss', 0)} USDT")
    print(f"الخسارة الأسبوعية: {user_data.get('weekly_loss', 0)} USDT")
    print(f"إجمالي الخسارة: {user_data.get('total_loss', 0)} USDT")
    
    print("\nانتهى اختبار نظام إدارة المخاطر")

if __name__ == "__main__":
    test_risk_management_simple()
