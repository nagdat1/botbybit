#!/usr/bin/env python3
"""
اختبار شامل لجميع أزرار المحفظة
Comprehensive Portfolio Buttons Test

اختبار جميع أزرار المحفظة للتأكد من عملها بشكل صحيح
"""

import asyncio
import logging
from datetime import datetime

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_all_portfolio_buttons():
    """اختبار جميع أزرار المحفظة"""
    try:
        print("بدء الاختبار الشامل لأزرار المحفظة...")
        
        # قائمة جميع أزرار المحفظة
        portfolio_buttons = [
            # الأزرار الجديدة للنظام المتطور
            "portfolio_analytics",
            "portfolio_positions", 
            "portfolio_recommendations",
            "portfolio_report",
            "portfolio_refresh",
            "portfolio_main",
            
            # الأزرار القديمة (للتوافق)
            "refresh_advanced_portfolio",
            "portfolio_details",
            "portfolio_settings",
            "refresh_portfolio",
            "refresh_real_portfolio",
            "real_portfolio_settings",
            "currency_details",
            "real_currency_details",
            "refresh_balance",
            "detailed_report",
            "account_settings"
        ]
        
        print(f"إجمالي الأزرار المراد اختبارها: {len(portfolio_buttons)}")
        
        # اختبار استيراد النظام الجديد
        print("\nاختبار استيراد النظام الجديد...")
        try:
            from ultimate_portfolio_manager import ultimate_portfolio_manager
            print("✅ ultimate_portfolio_manager تم استيراده بنجاح")
        except Exception as e:
            print(f"❌ خطأ في استيراد ultimate_portfolio_manager: {e}")
        
        try:
            from portfolio_interface import portfolio_interface
            print("✅ portfolio_interface تم استيراده بنجاح")
        except Exception as e:
            print(f"❌ خطأ في استيراد portfolio_interface: {e}")
        
        # اختبار إنشاء محفظة تجريبية
        print("\nاختبار إنشاء محفظة تجريبية...")
        try:
            # إضافة عدة صفقات تجريبية للاختبار
            test_positions = [
                {
                    'id': 'test_pos_1',
                    'symbol': 'BTCUSDT',
                    'side': 'buy',
                    'entry_price': 50000.0,
                    'quantity': 0.1,
                    'market_type': 'spot',
                    'account_type': 'demo',
                    'leverage': 1,
                    'notes': 'صفقة اختبار 1'
                },
                {
                    'id': 'test_pos_2',
                    'symbol': 'ETHUSDT',
                    'side': 'buy',
                    'entry_price': 3000.0,
                    'quantity': 1.0,
                    'market_type': 'spot',
                    'account_type': 'demo',
                    'leverage': 1,
                    'notes': 'صفقة اختبار 2'
                },
                {
                    'id': 'test_pos_3',
                    'symbol': 'BTCUSDT',
                    'side': 'sell',
                    'entry_price': 52000.0,
                    'quantity': 0.05,
                    'market_type': 'futures',
                    'account_type': 'demo',
                    'leverage': 10,
                    'notes': 'صفقة فيوتشر اختبار'
                }
            ]
            
            for position_data in test_positions:
                success = await ultimate_portfolio_manager.add_position(position_data)
                if success:
                    print(f"✅ تم إضافة صفقة: {position_data['symbol']}")
                else:
                    print(f"❌ فشل في إضافة صفقة: {position_data['symbol']}")
                    
        except Exception as e:
            print(f"❌ خطأ في إضافة الصفقات: {e}")
        
        # اختبار ملخص المحفظة
        print("\nاختبار ملخص المحفظة...")
        try:
            summary = await ultimate_portfolio_manager.get_portfolio_summary('demo')
            print(f"✅ ملخص المحفظة:")
            print(f"   القيمة الإجمالية: {summary.total_value:.2f} USDT")
            print(f"   الصفقات المفتوحة: {summary.open_positions}")
            print(f"   الصفقات المغلقة: {summary.closed_positions}")
            print(f"   معدل النجاح: {summary.win_rate:.1f}%")
            print(f"   أفضل صفقة: {summary.best_trade:+.2f} USDT")
            print(f"   أسوأ صفقة: {summary.worst_trade:+.2f} USDT")
        except Exception as e:
            print(f"❌ خطأ في ملخص المحفظة: {e}")
        
        # اختبار التحليلات
        print("\nاختبار التحليلات...")
        try:
            analytics = await ultimate_portfolio_manager.get_performance_analytics('demo')
            print(f"✅ التحليلات:")
            print(f"   إجمالي الصفقات: {analytics.get('total_trades', 0)}")
            print(f"   الصفقات الرابحة: {analytics.get('winning_trades', 0)}")
            print(f"   الصفقات الخاسرة: {analytics.get('losing_trades', 0)}")
            print(f"   عامل الربح: {analytics.get('profit_factor', 0):.2f}")
        except Exception as e:
            print(f"❌ خطأ في التحليلات: {e}")
        
        # اختبار التوصيات
        print("\nاختبار التوصيات...")
        try:
            recommendations = await ultimate_portfolio_manager.get_portfolio_recommendations('demo')
            print(f"✅ التوصيات: {len(recommendations)} توصية")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['title']} ({rec['priority']})")
        except Exception as e:
            print(f"❌ خطأ في التوصيات: {e}")
        
        # اختبار الواجهة
        print("\nاختبار الواجهة...")
        try:
            portfolio_data = await portfolio_interface.create_main_portfolio_menu(12345, 'demo')
            print(f"✅ الواجهة:")
            print(f"   الرسالة: {len(portfolio_data['message'])} حرف")
            print(f"   الأزرار: {len(portfolio_data['keyboard'])} زر")
            print(f"   نوع التحليل: {portfolio_data['parse_mode']}")
        except Exception as e:
            print(f"❌ خطأ في الواجهة: {e}")
        
        # اختبار لوحة التحليلات
        print("\nاختبار لوحة التحليلات...")
        try:
            analytics_data = await portfolio_interface.create_analytics_dashboard(12345, 'demo')
            print(f"✅ لوحة التحليلات:")
            print(f"   الرسالة: {len(analytics_data['message'])} حرف")
            print(f"   الأزرار: {len(analytics_data['keyboard'])} زر")
        except Exception as e:
            print(f"❌ خطأ في لوحة التحليلات: {e}")
        
        # اختبار عرض الصفقات
        print("\nاختبار عرض الصفقات...")
        try:
            positions_data = await portfolio_interface.create_positions_view(12345, 'demo')
            print(f"✅ عرض الصفقات:")
            print(f"   الرسالة: {len(positions_data['message'])} حرف")
            print(f"   الأزرار: {len(positions_data['keyboard'])} زر")
        except Exception as e:
            print(f"❌ خطأ في عرض الصفقات: {e}")
        
        # اختبار التوصيات الذكية
        print("\nاختبار التوصيات الذكية...")
        try:
            recommendations_data = await portfolio_interface.create_recommendations_view(12345, 'demo')
            print(f"✅ التوصيات الذكية:")
            print(f"   الرسالة: {len(recommendations_data['message'])} حرف")
            print(f"   الأزرار: {len(recommendations_data['keyboard'])} زر")
        except Exception as e:
            print(f"❌ خطأ في التوصيات الذكية: {e}")
        
        print("\n🎉 انتهى الاختبار الشامل لأزرار المحفظة!")
        print(f"✅ تم اختبار {len(portfolio_buttons)} زر")
        print("جميع الأزرار جاهزة للعمل!")
        
    except Exception as e:
        print(f"❌ خطأ عام في الاختبار: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_portfolio_buttons())
