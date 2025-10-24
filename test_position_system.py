#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إدارة الصفقات المحسن
"""

import asyncio
import logging
from datetime import datetime

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_portfolio_sync():
    """اختبار مزامنة الصفقات"""
    print("\n" + "="*60)
    print("اختبار 1: مزامنة الصفقات بين الذاكرة وقاعدة البيانات")
    print("="*60)
    
    try:
        from enhanced_portfolio_manager import portfolio_factory
        from user_manager import user_manager
        
        # إنشاء مستخدم اختباري
        test_user_id = 999999
        
        # إضافة صفقة وهمية في الذاكرة
        if test_user_id not in user_manager.user_positions:
            user_manager.user_positions[test_user_id] = {}
        
        user_manager.user_positions[test_user_id]['test_pos_1'] = {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'position_size': 0.1,
            'account_type': 'futures',
            'exchange': 'bybit',
            'leverage': 10,
            'current_price': 51000.0,
            'pnl_percent': 2.0
        }
        
        print(f"تم إضافة صفقة وهمية في الذاكرة: test_pos_1")
        
        # الحصول على مدير المحفظة
        portfolio_manager = portfolio_factory.get_portfolio_manager(test_user_id)
        
        # تنفيذ المزامنة
        print("\nتنفيذ المزامنة...")
        result = portfolio_manager.sync_positions_with_memory()
        
        if result:
            print("نجح: تمت المزامنة بنجاح")
        else:
            print("فشل: فشلت المزامنة")
        
        # التحقق من النتيجة
        portfolio = portfolio_manager.get_user_portfolio(force_refresh=True)
        open_positions = portfolio.get('open_positions', [])
        
        print(f"\nعدد الصفقات المفتوحة في المحفظة: {len(open_positions)}")
        
        # تنظيف
        if test_user_id in user_manager.user_positions:
            del user_manager.user_positions[test_user_id]
        
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_positions():
    """اختبار جمع الصفقات الموحد"""
    print("\n" + "="*60)
    print("اختبار 2: جمع الصفقات من جميع المصادر")
    print("="*60)
    
    try:
        from enhanced_portfolio_manager import portfolio_factory
        from user_manager import user_manager
        
        # إنشاء مستخدم اختباري
        test_user_id = 999998
        
        # إضافة صفقات وهمية في الذاكرة
        if test_user_id not in user_manager.user_positions:
            user_manager.user_positions[test_user_id] = {}
        
        # صفقة 1
        user_manager.user_positions[test_user_id]['test_pos_1'] = {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'position_size': 0.1,
            'account_type': 'futures',
            'exchange': 'bybit',
            'leverage': 10
        }
        
        # صفقة 2
        user_manager.user_positions[test_user_id]['test_pos_2'] = {
            'symbol': 'ETHUSDT',
            'side': 'sell',
            'entry_price': 3000.0,
            'position_size': 1.0,
            'account_type': 'futures',
            'exchange': 'bybit',
            'leverage': 5
        }
        
        # صفقة 3
        user_manager.user_positions[test_user_id]['test_pos_3'] = {
            'symbol': 'BNBUSDT',
            'side': 'buy',
            'entry_price': 300.0,
            'amount': 10.0,
            'account_type': 'spot',
            'exchange': 'bybit'
        }
        
        print(f"تم إضافة 3 صفقات وهمية في الذاكرة")
        
        # الحصول على مدير المحفظة
        portfolio_manager = portfolio_factory.get_portfolio_manager(test_user_id)
        
        # جمع الصفقات الموحد
        print("\nجمع الصفقات من جميع المصادر...")
        all_positions = portfolio_manager.get_all_user_positions_unified('demo')
        
        print(f"\nعدد الصفقات المجموعة: {len(all_positions)}")
        
        # عرض الصفقات
        for idx, pos in enumerate(all_positions, 1):
            print(f"\nصفقة {idx}:")
            print(f"  - الرمز: {pos.get('symbol')}")
            print(f"  - الجهة: {pos.get('side')}")
            print(f"  - السوق: {pos.get('market_type')}")
            print(f"  - المصدر: {pos.get('source')}")
        
        # تنظيف
        if test_user_id in user_manager.user_positions:
            del user_manager.user_positions[test_user_id]
        
        return len(all_positions) == 3
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_position_deduplication():
    """اختبار إزالة التكرار"""
    print("\n" + "="*60)
    print("اختبار 3: إزالة تكرار الصفقات")
    print("="*60)
    
    try:
        from enhanced_portfolio_manager import portfolio_factory
        from user_manager import user_manager
        from database import db_manager
        
        # إنشاء مستخدم اختباري
        test_user_id = 999997
        
        # إضافة صفقة في الذاكرة
        if test_user_id not in user_manager.user_positions:
            user_manager.user_positions[test_user_id] = {}
        
        user_manager.user_positions[test_user_id]['duplicate_test'] = {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'position_size': 0.1,
            'account_type': 'futures',
            'exchange': 'bybit',
            'leverage': 10
        }
        
        print("تم إضافة صفقة في الذاكرة: duplicate_test")
        
        # الحصول على مدير المحفظة
        portfolio_manager = portfolio_factory.get_portfolio_manager(test_user_id)
        
        # حفظ في قاعدة البيانات
        position_data = {
            'order_id': 'duplicate_test',
            'user_id': test_user_id,
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 50000.0,
            'quantity': 0.1,
            'market_type': 'futures',
            'exchange': 'bybit',
            'leverage': 10,
            'status': 'OPEN'
        }
        
        db_manager.create_order(position_data)
        print("تم حفظ نفس الصفقة في قاعدة البيانات")
        
        # جمع الصفقات
        print("\nجمع الصفقات (يجب أن تظهر مرة واحدة فقط)...")
        all_positions = portfolio_manager.get_all_user_positions_unified('demo')
        
        print(f"\nعدد الصفقات الفريدة: {len(all_positions)}")
        
        # يجب أن تكون صفقة واحدة فقط (بدون تكرار)
        success = len(all_positions) == 1
        
        if success:
            print("نجح: تم إزالة التكرار بنجاح")
        else:
            print(f"فشل: عدد الصفقات {len(all_positions)} بدلاً من 1")
        
        # تنظيف
        if test_user_id in user_manager.user_positions:
            del user_manager.user_positions[test_user_id]
        
        # حذف من قاعدة البيانات
        db_manager.close_order('duplicate_test', 50000.0, 0.0)
        
        return success
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("\n" + "="*60)
    print("بدء اختبار نظام إدارة الصفقات المحسن")
    print("="*60)
    print(f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # الاختبار 1
    try:
        result1 = test_portfolio_sync()
        results.append(("مزامنة الصفقات", result1))
    except Exception as e:
        print(f"خطأ في الاختبار 1: {e}")
        results.append(("مزامنة الصفقات", False))
    
    # الاختبار 2
    try:
        result2 = test_unified_positions()
        results.append(("جمع الصفقات الموحد", result2))
    except Exception as e:
        print(f"خطأ في الاختبار 2: {e}")
        results.append(("جمع الصفقات الموحد", False))
    
    # الاختبار 3
    try:
        result3 = test_position_deduplication()
        results.append(("إزالة التكرار", result3))
    except Exception as e:
        print(f"خطأ في الاختبار 3: {e}")
        results.append(("إزالة التكرار", False))
    
    # عرض النتائج
    print("\n" + "="*60)
    print("ملخص النتائج")
    print("="*60)
    
    for test_name, result in results:
        status = "نجح" if result else "فشل"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"\nالإجمالي: {passed_tests}/{total_tests} اختبار نجح")
    
    if passed_tests == total_tests:
        print("\nجميع الاختبارات نجحت!")
        return 0
    else:
        print(f"\n{total_tests - passed_tests} اختبار فشل")
        return 1

if __name__ == "__main__":
    exit(main())

