#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل سريع لاختبار إصلاح مشكلة عدم كفاية الرصيد
"""

import asyncio
import logging
import sys
import os

# إضافة المسار الحالي للنظام
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def quick_test():
    """اختبار سريع للنظام"""
    print("اختبار سريع لإصلاح مشكلة عدم كفاية الرصيد")
    print("=" * 60)
    
    try:
        # اختبار النظام الشامل
        from comprehensive_balance_fix import comprehensive_balance_fix
        
        print("تم تحميل النظام الشامل بنجاح")
        
        # بيانات اختبار
        test_user_id = 12345
        test_signal_data = {
            'action': 'buy',
            'symbol': 'BTCUSDT',
            'price': 111084.4,
            'signal_id': '4',
            'has_signal_id': True
        }
        
        test_user_data = {
            'account_type': 'real',
            'exchange': 'bybit',
            'market_type': 'futures',
            'trade_amount': 55.0,
            'leverage': 1
        }
        
        print(f"بيانات الاختبار:")
        print(f"  - المستخدم: {test_user_id}")
        print(f"  - الإشارة: {test_signal_data['action']} {test_signal_data['symbol']}")
        print(f"  - السعر: {test_signal_data['price']}")
        print(f"  - المبلغ: {test_user_data['trade_amount']} USDT")
        print(f"  - الرافعة: {test_user_data['leverage']}x")
        
        print("\nبدء الاختبار...")
        
        # اختبار التنفيذ
        result = await comprehensive_balance_fix.execute_signal_with_comprehensive_fix(
            test_user_id, test_signal_data, test_user_data
        )
        
        print(f"\nنتيجة الاختبار:")
        print(f"  - النجاح: {result.get('success', False)}")
        print(f"  - الرسالة: {result.get('message', 'لا توجد رسالة')}")
        print(f"  - الخطأ: {result.get('error', 'لا يوجد خطأ')}")
        
        if result.get('suggestion'):
            print(f"  - الاقتراح: {result.get('suggestion')}")
        
        if result.get('suggestions'):
            print(f"  - الحلول المقترحة:")
            for suggestion in result.get('suggestions', []):
                print(f"    * {suggestion}")
        
        # اختبار التشخيص
        print(f"\nاختبار التشخيص...")
        diagnosis = await comprehensive_balance_fix.diagnose_balance_issue(test_user_id)
        
        print(f"نتيجة التشخيص:")
        print(f"  - النجاح: {diagnosis.get('success', False)}")
        print(f"  - الرسالة: {diagnosis.get('message', 'لا توجد رسالة')}")
        
        if diagnosis.get('recommendations'):
            print(f"  - التوصيات:")
            for rec in diagnosis.get('recommendations', []):
                print(f"    * {rec}")
        
        print("\nانتهى الاختبار بنجاح!")
        
    except ImportError as e:
        print(f"خطأ في الاستيراد: {e}")
        print("تأكد من وجود جميع الملفات المطلوبة")
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

def test_imports():
    """اختبار استيراد الملفات"""
    print("اختبار استيراد الملفات...")
    
    try:
        from balance_fix_system import balance_validator, enhanced_signal_executor
        print("balance_fix_system - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"balance_fix_system - فشل الاستيراد: {e}")
    
    try:
        from comprehensive_balance_fix import comprehensive_balance_fix
        print("comprehensive_balance_fix - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"comprehensive_balance_fix - فشل الاستيراد: {e}")
    
    try:
        from signal_executor import signal_executor
        print("signal_executor - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"signal_executor - فشل الاستيراد: {e}")
    
    try:
        from real_account_manager import real_account_manager
        print("real_account_manager - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"real_account_manager - فشل الاستيراد: {e}")

async def main():
    """الدالة الرئيسية"""
    print("نظام إصلاح مشكلة عدم كفاية الرصيد")
    print("=" * 60)
    
    # اختبار الاستيراد أولاً
    test_imports()
    
    print("\n" + "=" * 60)
    
    # اختبار النظام
    await quick_test()

if __name__ == "__main__":
    asyncio.run(main())
