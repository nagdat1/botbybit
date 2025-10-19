#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للنظام المحسن المبسط
"""

import sys
import os

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_enhanced_system():
    """اختبار النظام المحسن المبسط"""
    print("Testing Simple Enhanced System...")
    
    try:
        # استيراد النظام المحسن المبسط
        from simple_enhanced_system import SimpleEnhancedSystem
        print("✓ Simple Enhanced System imported successfully!")
        
        # إنشاء مثيل من النظام
        system = SimpleEnhancedSystem()
        print("✓ System initialized successfully!")
        
        # اختبار معالجة إشارة
        test_signal = {
            "action": "buy",
            "symbol": "BTCUSDT",
            "price": 50000,
            "quantity": 0.001
        }
        
        result = system.process_signal(12345, test_signal)
        print(f"✓ Signal processed successfully: {result['status']}")
        
        # اختبار حالة النظام
        status = system.get_system_status()
        print(f"✓ System status: {status['system_type']}")
        
        # اختبار تقرير الأداء
        report = system.get_performance_report()
        print(f"✓ Performance report generated")
        
        print("All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_enhanced_system()
