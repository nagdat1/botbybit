#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط للنظام الجديد
"""

def test_system():
    """اختبار النظام"""
    print("=" * 60)
    print("اختبار نظام تكامل الإشارات")
    print("=" * 60)
    
    try:
        from signal_system_integration import signal_system_integration
        
        # اختبار توفر النظام
        is_available = signal_system_integration.is_available()
        print(f"النظام متاح: {is_available}")
        
        if is_available:
            # اختبار حالة التكامل
            status = signal_system_integration.get_integration_status()
            print(f"حالة التكامل: {status['status']}")
            print(f"الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
            
            # اختبار معالجة إشارة
            test_signal = {
                'signal': 'buy',
                'symbol': 'BTCUSDT',
                'id': 'TEST_001'
            }
            
            result = signal_system_integration.process_signal(test_signal, 12345)
            print(f"نتيجة معالجة الإشارة: {result['success']}")
            if result['success']:
                print(f"النظام المستخدم: {result.get('system_used', 'غير محدد')}")
            else:
                print(f"الخطأ: {result.get('message', 'غير محدد')}")
        else:
            print("النظام غير متاح")
            
    except ImportError as e:
        print(f"خطأ في استيراد النظام: {e}")
    except Exception as e:
        print(f"خطأ عام: {e}")


if __name__ == "__main__":
    test_system()
