#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النظام المحسن للمحفظة والصفقات
"""

import asyncio
import sys
import os
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_portfolio():
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
        
        # إضافة صفقات تجريبية
        print("\nإضافة صفقات تجريبية...")
        
        test_positions = [
            {
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
            },
            {
                'order_id': 'TEST_002',
                'user_id': test_user_id,
                'symbol': 'ETHUSDT',
                'side': 'sell',
                'entry_price': 3000.0,
                'quantity': 1.0,
                'market_type': 'futures',
                'exchange': 'bybit',
                'leverage': 10,
                'status': 'OPEN',
                'notes': 'صفقة تجريبية ETH',
                'signal_id': 'SIGNAL_123'
            },
            {
                'order_id': 'TEST_003',
                'user_id': test_user_id,
                'symbol': 'ADAUSDT',
                'side': 'buy',
                'entry_price': 0.5,
                'quantity': 1000,
                'market_type': 'spot',
                'exchange': 'bybit',
                'leverage': 1,
                'status': 'OPEN',
                'notes': 'صفقة تجريبية ADA'
            }
        ]
        
        # إضافة الصفقات
        for i, position in enumerate(test_positions, 1):
            success = portfolio_manager.add_position(position)
            if success:
                print(f"✅ تم إضافة صفقة {i}: {position['symbol']} - {position['side']}")
            else:
                print(f"❌ فشل في إضافة صفقة {i}: {position['symbol']}")
        
        # اختبار جلب المحفظة
        print("\n📈 جلب بيانات المحفظة...")
        portfolio_data = portfolio_manager.get_user_portfolio(force_refresh=True)
        
        if portfolio_data:
            summary = portfolio_data.get('summary', {})
            stats = portfolio_data.get('portfolio_stats', {})
            
            print(f"✅ تم جلب بيانات المحفظة:")
            print(f"   • الصفقات المفتوحة: {summary.get('total_open_positions', 0)}")
            print(f"   • الصفقات المغلقة: {summary.get('total_closed_positions', 0)}")
            print(f"   • الرموز المتداولة: {summary.get('total_symbols', 0)}")
            print(f"   • قيمة المحفظة: {summary.get('portfolio_value', 0):.2f} USDT")
            print(f"   • معدل الفوز: {stats.get('win_rate', 0):.1f}%")
        else:
            print("❌ فشل في جلب بيانات المحفظة")
        
        # اختبار جلب الصفقات حسب الرمز
        print("\n🔍 اختبار جلب الصفقات حسب الرمز...")
        btc_positions = portfolio_manager.get_positions_by_symbol('BTCUSDT')
        print(f"✅ صفقات BTCUSDT: {len(btc_positions)}")
        
        eth_positions = portfolio_manager.get_positions_by_symbol('ETHUSDT')
        print(f"✅ صفقات ETHUSDT: {len(eth_positions)}")
        
        # اختبار حساب الربح/الخسارة
        print("\n💰 اختبار حساب الربح/الخسارة...")
        current_prices = {
            'BTCUSDT': 46000.0,  # ربح 2.2%
            'ETHUSDT': 2950.0,   # ربح 1.7% (لأنها صفقة بيع)
            'ADAUSDT': 0.48      # خسارة 4%
        }
        
        pnl_data = portfolio_manager.calculate_portfolio_pnl(current_prices)
        if pnl_data:
            print(f"✅ إجمالي الربح/الخسارة: {pnl_data['total_pnl']:.2f} USDT")
            for position_pnl in pnl_data['positions_pnl']:
                symbol = position_pnl['symbol']
                pnl = position_pnl['pnl']
                pnl_percent = position_pnl['pnl_percent']
                print(f"   • {symbol}: {pnl:.2f} USDT ({pnl_percent:.2f}%)")
        
        # اختبار إغلاق صفقة
        print("\n🔄 اختبار إغلاق صفقة...")
        close_success = portfolio_manager.close_position('TEST_001', 46000.0)
        if close_success:
            print("✅ تم إغلاق صفقة TEST_001 بنجاح")
        else:
            print("❌ فشل في إغلاق صفقة TEST_001")
        
        # اختبار ملخص المحفظة للعرض
        print("\n📋 ملخص المحفظة للعرض:")
        portfolio_summary = portfolio_manager.get_portfolio_summary_for_display()
        print(portfolio_summary)
        
        # تنظيف البيانات التجريبية
        print("\n🧹 تنظيف البيانات التجريبية...")
        db_manager.update_position_status('TEST_001', 'CLOSED')
        db_manager.update_position_status('TEST_002', 'CLOSED')
        db_manager.update_position_status('TEST_003', 'CLOSED')
        print("✅ تم تنظيف البيانات التجريبية")
        
        print("\n" + "=" * 60)
        print("🎉 تم إنجاز جميع الاختبارات بنجاح!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_functions():
    """اختبار دوال قاعدة البيانات المحسنة"""
    print("\n" + "=" * 60)
    print("🗄️ اختبار دوال قاعدة البيانات المحسنة")
    print("=" * 60)
    
    try:
        from database import db_manager
        
        test_user_id = 888888
        
        # إنشاء مستخدم تجريبي
        db_manager.create_user(test_user_id, "test_api_key", "test_api_secret")
        print(f"✅ تم إنشاء مستخدم تجريبي: {test_user_id}")
        
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
            print("✅ تم إنشاء صفقة شاملة في قاعدة البيانات")
        else:
            print("❌ فشل في إنشاء صفقة شاملة")
        
        # اختبار جلب جميع صفقات المستخدم
        all_positions = db_manager.get_all_user_positions(test_user_id)
        print(f"✅ جميع صفقات المستخدم: {len(all_positions)} صفقة")
        
        # اختبار ملخص المحفظة
        portfolio_summary = db_manager.get_user_portfolio_summary(test_user_id)
        print(f"✅ ملخص المحفظة:")
        print(f"   • الصفقات المفتوحة: {portfolio_summary.get('total_open_positions', 0)}")
        print(f"   • الصفقات المغلقة: {portfolio_summary.get('total_closed_positions', 0)}")
        print(f"   • قيمة المحفظة: {portfolio_summary.get('portfolio_value', 0):.2f} USDT")
        
        # تنظيف
        db_manager.update_position_status('DB_TEST_001', 'CLOSED')
        print("✅ تم تنظيف البيانات التجريبية")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """الدالة الرئيسية للاختبار"""
    print("بدء اختبار النظام المحسن للمحفظة والصفقات")
    print("الوقت:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # اختبار دوال قاعدة البيانات
    db_success = await test_database_functions()
    
    # اختبار النظام المحسن
    portfolio_success = await test_enhanced_portfolio()
    
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
    asyncio.run(main())
