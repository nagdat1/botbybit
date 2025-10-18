#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إدارة المخاطر
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد المكونات المطلوبة
try:
    from user_manager import user_manager
    from bybit_trading_bot import check_risk_management, reset_daily_loss_if_needed
    print("تم استيراد المكونات بنجاح")
except ImportError as e:
    print(f"خطأ في الاستيراد: {e}")
    sys.exit(1)

def test_risk_management():
    """اختبار نظام إدارة المخاطر"""
    print("اختبار نظام إدارة المخاطر")
    print("=" * 50)
    
    # إنشاء مستخدم تجريبي
    test_user_id = 999999999
    test_user_data = {
        'user_id': test_user_id,
        'username': 'test_user',
        'account_type': 'demo',
        'market_type': 'spot',
        'trade_amount': 100.0,
        'leverage': 10,
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
    
    # إضافة المستخدم
    user_manager.add_user(test_user_id, test_user_data)
    print(f"تم إنشاء مستخدم تجريبي: {test_user_id}")
    
    # اختبار 1: صفقة رابحة (لا يجب إيقاف البوت)
    print("\nاختبار 1: صفقة رابحة")
    profitable_trade = {
        'success': True,
        'pnl': 50.0,  # ربح 50 USDT
        'order_id': 'test_order_1'
    }
    
    result = check_risk_management(test_user_id, profitable_trade)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # اختبار 2: خسارة صغيرة (لا يجب إيقاف البوت)
    print("\nاختبار 2: خسارة صغيرة")
    small_loss_trade = {
        'success': True,
        'pnl': -50.0,  # خسارة 50 USDT
        'order_id': 'test_order_2'
    }
    
    result = check_risk_management(test_user_id, small_loss_trade)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # اختبار 3: خسارة كبيرة (يجب إيقاف البوت)
    print("\nاختبار 3: خسارة كبيرة")
    large_loss_trade = {
        'success': True,
        'pnl': -600.0,  # خسارة 600 USDT (أكبر من الحد اليومي 500)
        'order_id': 'test_order_3'
    }
    
    result = check_risk_management(test_user_id, large_loss_trade)
    print(f"النتيجة: {result}")
    print(f"يجب إيقاف البوت: {'نعم' if result['should_stop'] else 'لا'}")
    
    # اختبار 4: إعادة تعيين الخسارة اليومية
    print("\nاختبار 4: إعادة تعيين الخسارة اليومية")
    reset_daily_loss_if_needed(test_user_id)
    
    user_data = user_manager.get_user(test_user_id)
    print(f"الخسارة اليومية بعد الإعادة: {user_data.get('daily_loss', 0)}")
    
    # اختبار 5: عرض إحصائيات المخاطر
    print("\nاختبار 5: إحصائيات المخاطر")
    user_data = user_manager.get_user(test_user_id)
    risk_settings = user_data.get('risk_management', {})
    
    print(f"إدارة المخاطر مفعلة: {'نعم' if risk_settings.get('enabled') else 'لا'}")
    print(f"الحد اليومي: {risk_settings.get('daily_loss_limit', 0)} USDT")
    print(f"الحد الأسبوعي: {risk_settings.get('weekly_loss_limit', 0)} USDT")
    print(f"الحد المئوي: {risk_settings.get('max_loss_percent', 0)}%")
    print(f"الحد بالمبلغ: {risk_settings.get('max_loss_amount', 0)} USDT")
    print(f"الخسارة اليومية: {user_data.get('daily_loss', 0)} USDT")
    print(f"الخسارة الأسبوعية: {user_data.get('weekly_loss', 0)} USDT")
    print(f"إجمالي الخسارة: {user_data.get('total_loss', 0)} USDT")
    print(f"حالة البوت: {'نشط' if user_data.get('is_active') else 'متوقف'}")
    
    # تنظيف
    user_manager.delete_user(test_user_id)
    print(f"\nتم حذف المستخدم التجريبي: {test_user_id}")
    
    print("\nانتهى اختبار نظام إدارة المخاطر")

if __name__ == "__main__":
    test_risk_management()
