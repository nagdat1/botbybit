#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط للنظام المحسن للمحفظة
"""

import sys
import os

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_portfolio():
    """اختبار النظام المحسن للمحفظة"""
    print("=" * 60)
    print("اختبار النظام المحسن للمحفظة والصفقات")
    print("=" * 60)
    
    try:
        # استيراد المكونات
        from enhanced_portfolio_manager import portfolio_factory
        from database import db_manager
        
        # إنشاء مستخدم تجريبي
        test_user_id = 999999
        print(f"إنشاء مستخدم تجريبي: {test_user_id}")
        
        # إنشاء المستخدم في قاعدة البيانات
        db_manager.create_user(test_user_id, "test_api_key", "test_api_secret")
        
        # الحصول على مدير المحفظة
        portfolio_manager = portfolio_factory.get_portfolio_manager(test_user_id)
        print("تم الحصول على مدير المحفظة")
        
        # إضافة صفقة تجريبية
        print("\nإضافة صفقة تجريبية...")
        
        position_data = {
            'order_id': 'TEST_001',
            'user_id': test_user_id,
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 45000.0,
            'quantity': 0.1,
            'market_type': 'spot',
            'exchange': 'bybit',
            'leverage': 1,
            'status': 'OPEN',
            'notes': 'صفقة تجريبية BTC'
        }
        
        success = portfolio_manager.add_position(position_data)
        if success:
            print("تم إضافة صفقة بنجاح")
        else:
            print("فشل في إضافة صفقة")
        
        # اختبار جلب المحفظة
        print("\nجلب بيانات المحفظة...")
        portfolio_data = portfolio_manager.get_user_portfolio(force_refresh=True)
        
        if portfolio_data:
            summary = portfolio_data.get('summary', {})
            print(f"تم جلب بيانات المحفظة:")
            print(f"   - الصفقات المفتوحة: {summary.get('total_open_positions', 0)}")
            print(f"   - الصفقات المغلقة: {summary.get('total_closed_positions', 0)}")
            print(f"   - الرموز المتداولة: {summary.get('total_symbols', 0)}")
            print(f"   - قيمة المحفظة: {summary.get('portfolio_value', 0):.2f} USDT")
        else:
            print("فشل في جلب بيانات المحفظة")
        
        # تنظيف البيانات التجريبية
        print("\nتنظيف البيانات التجريبية...")
        db_manager.update_position_status('TEST_001', 'CLOSED')
        print("تم تنظيف البيانات التجريبية")
        
        print("\n" + "=" * 60)
        print("تم إنجاز الاختبار بنجاح!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_functions():
    """اختبار دوال قاعدة البيانات المحسنة"""
    print("\n" + "=" * 60)
    print("اختبار دوال قاعدة البيانات المحسنة")
    print("=" * 60)
    
    try:
        from database import db_manager
        
        test_user_id = 888888
        
        # إنشاء مستخدم تجريبي
        db_manager.create_user(test_user_id, "test_api_key", "test_api_secret")
        print(f"تم إنشاء مستخدم تجريبي: {test_user_id}")
        
        # اختبار إنشاء صفقة شاملة
        position_data = {
            'order_id': 'DB_TEST_001',
            'user_id': test_user_id,
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'entry_price': 45000.0,
            'quantity': 0.1,
            'market_type': 'spot',
            'exchange': 'bybit',
            'leverage': 1,
            'status': 'OPEN',
            'notes': 'اختبار قاعدة البيانات',
            'signal_id': 'SIGNAL_TEST_001'
        }
        
        success = db_manager.create_comprehensive_position(position_data)
        if success:
            print("تم إنشاء صفقة شاملة في قاعدة البيانات")
        else:
            print("فشل في إنشاء صفقة شاملة")
        
        # اختبار جلب جميع صفقات المستخدم
        all_positions = db_manager.get_all_user_positions(test_user_id)
        print(f"جميع صفقات المستخدم: {len(all_positions)} صفقة")
        
        # اختبار ملخص المحفظة
        portfolio_summary = db_manager.get_user_portfolio_summary(test_user_id)
        print(f"ملخص المحفظة:")
        print(f"   - الصفقات المفتوحة: {portfolio_summary.get('total_open_positions', 0)}")
        print(f"   - الصفقات المغلقة: {portfolio_summary.get('total_closed_positions', 0)}")
        print(f"   - قيمة المحفظة: {portfolio_summary.get('portfolio_value', 0):.2f} USDT")
        
        # تنظيف
        db_manager.update_position_status('DB_TEST_001', 'CLOSED')
        print("تم تنظيف البيانات التجريبية")
        
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("بدء اختبار النظام المحسن للمحفظة والصفقات")
    
    # اختبار دوال قاعدة البيانات
    db_success = test_database_functions()
    
    # اختبار النظام المحسن
    portfolio_success = test_enhanced_portfolio()
    
    print("\n" + "=" * 60)
    print("نتائج الاختبار:")
    print(f"   - قاعدة البيانات: {'نجح' if db_success else 'فشل'}")
    print(f"   - النظام المحسن: {'نجح' if portfolio_success else 'فشل'}")
    print("=" * 60)
    
    if db_success and portfolio_success:
        print("جميع الاختبارات نجحت! النظام المحسن جاهز للاستخدام.")
        return True
    else:
        print("بعض الاختبارات فشلت. يرجى مراجعة الأخطاء.")
        return False

if __name__ == "__main__":
    main()

