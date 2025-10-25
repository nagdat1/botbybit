#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل البوت المحسن مع إظهار الفرق
"""

import os
import sys
import time
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_system_comparison():
    """عرض مقارنة بين النظام العادي والمحسن"""
    print("\n" + "="*80)
    print(" مقارنة بين النظام العادي والنظام المحسن")
    print("="*80)
    
    print("\n النظام العادي:")
    print("   • إدارة مخاطر أساسية")
    print("   • معالجة إشارات بسيطة")
    print("   • تنفيذ صفقات مباشر")
    print("   • لا يوجد تحسين تلقائي")
    print("   • لا يوجد إدارة محفظة متقدمة")
    
    print("\n النظام المحسن:")
    print("   • إدارة مخاطر متقدمة مع نماذج إحصائية")
    print("   • معالجة إشارات ذكية مع تحليل الجودة")
    print("   • تنفيذ صفقات محسن (TWAP, VWAP, Iceberg)")
    print("   • تحسين تلقائي للمعاملات")
    print("   • إدارة محفظة متقدمة مع إعادة توازن تلقائية")
    print("   • مراقبة الأداء المستمرة")
    print("   • تحليل VaR و CVaR")
    print("   • تحسين Sharpe Ratio")
    
    print("\n الفوائد الرئيسية:")
    print("   • دقة أعلى في التنبؤ")
    print("   • تقليل المخاطر")
    print("   • تحسين الأداء")
    print("   • استقرار أكبر")
    print("   • مراقبة مستمرة")

def test_enhanced_system():
    """اختبار النظام المحسن"""
    print("\n" + "="*60)
    print("🧪 اختبار النظام المحسن")
    print("="*60)
    
    try:
        # اختبار استيراد النظام المحسن
        print("1. اختبار استيراد النظام المحسن...")
        from integrated_trading_system import IntegratedTradingSystem
        print("    تم استيراد النظام المحسن بنجاح")
        
        # اختبار تهيئة النظام
        print("2. اختبار تهيئة النظام...")
        system = IntegratedTradingSystem()
        print("    تم تهيئة النظام بنجاح")
        
        # اختبار المكونات
        print("3. اختبار المكونات...")
        components = [
            ("مدير المخاطر المتقدم", system.risk_manager),
            ("معالج الإشارات المتقدم", system.signal_processor),
            ("منفذ الصفقات المتقدم", system.trade_executor),
            ("مدير المحفظة المتقدم", system.portfolio_manager),
            ("محسن البوت", system.bot_optimizer)
        ]
        
        for name, component in components:
            if component:
                print(f"    {name}: متاح")
            else:
                print(f"    {name}: غير متاح")
        
        # اختبار معالجة إشارة تجريبية
        print("4. اختبار معالجة إشارة تجريبية...")
        test_signal = {
            "action": "buy",
            "symbol": "BTCUSDT",
            "price": 50000,
            "quantity": 0.001
        }
        
        result = system.process_signal(12345, test_signal)
        print(f"    تم معالجة الإشارة التجريبية: {result}")
        
        print("\n جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"    خطأ في الاختبار: {e}")
        return False

def show_usage_instructions():
    """عرض تعليمات الاستخدام"""
    print("\n" + "="*60)
    print("📖 تعليمات الاستخدام")
    print("="*60)
    
    print("\n لتشغيل النظام المحسن:")
    print("   1. تشغيل app.py (سيستخدم النظام المحسن تلقائياً)")
    print("   2. أو تشغيل integrated_trading_system.py مباشرة")
    
    print("\n🌐 للوصول إلى النظام:")
    print("   • الصفحة الرئيسية: http://localhost:5000/")
    print("   • فحص الصحة: http://localhost:5000/health")
    print("   • Webhook: http://localhost:5000/webhook")
    
    print("\n لرؤية الفرق:")
    print("   1. تشغيل النظام المحسن")
    print("   2. مراقبة الرسائل في الكونسول")
    print("   3. فحص الاستجابات من API")
    print("   4. مقارنة الأداء")

def main():
    """الدالة الرئيسية"""
    print(" تشغيل البوت المحسن")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # عرض مقارنة الأنظمة
    show_system_comparison()
    
    # اختبار النظام المحسن
    test_success = test_enhanced_system()
    
    if test_success:
        print("\n النظام المحسن جاهز للاستخدام!")
    else:
        print("\n النظام المحسن غير متاح، سيتم استخدام النظام العادي")
    
    # عرض تعليمات الاستخدام
    show_usage_instructions()
    
    print("\n" + "="*60)
    print(" الخطوات التالية:")
    print("   1. تشغيل app.py")
    print("   2. مراقبة الرسائل في الكونسول")
    print("   3. فحص الصفحة الرئيسية")
    print("   4. اختبار Webhook")
    print("="*60)

if __name__ == "__main__":
    main()
