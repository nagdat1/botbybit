#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الأنظمة المتقدمة
"""

def test_advanced_signal_manager():
    """اختبار مدير الإشارات المتقدم"""
    print("=" * 60)
    print("اختبار مدير الإشارات المتقدم")
    print("=" * 60)
    
    try:
        from advanced_signal_manager import process_signal, get_signal_statistics
        
        # اختبار إشارة مع ID
        test_signal_with_id = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TV_B01'
        }
        
        result1 = process_signal(test_signal_with_id, 12345)
        print(f"اختبار إشارة مع ID: {'نجح' if result1['success'] else 'فشل'}")
        if result1['success']:
            print(f"   ID الإشارة: {result1['signal_id']}")
        
        # اختبار إشارة بدون ID
        test_signal_without_id = {
            'signal': 'sell',
            'symbol': 'ETHUSDT'
        }
        
        result2 = process_signal(test_signal_without_id, 12345)
        print(f"اختبار إشارة بدون ID: {'نجح' if result2['success'] else 'فشل'}")
        if result2['success']:
            print(f"   ID الإشارة: {result2['signal_id']}")
        
        # اختبار الإحصائيات
        stats = get_signal_statistics(12345)
        print(f"عدد الإشارات: {stats['total_signals']}")
        
    except Exception as e:
        print(f"خطأ في اختبار مدير الإشارات: {e}")

def test_advanced_signal_processor():
    """اختبار معالج الإشارات المتقدم"""
    print("\n" + "=" * 60)
    print("اختبار معالج الإشارات المتقدم")
    print("=" * 60)
    
    try:
        from advanced_signal_processor import AdvancedSignalProcessor
        
        # إنشاء معالج إشارات
        processor = AdvancedSignalProcessor(12345)
        
        # اختبار إشارة
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'action': 'buy',
            'id': 'TEST_001'
        }
        
        result = processor.process_signal(test_signal)
        print(f"معالجة الإشارة: {'نجح' if result['success'] else 'فشل'}")
        if result['success']:
            print(f"   جودة الإشارة: {result['quality_analysis']['quality_level']}")
            print(f"   مستوى الثقة: {result['quality_analysis']['confidence']:.2f}")
        
        # اختبار الإحصائيات
        stats = processor.get_signal_statistics()
        print(f"إجمالي الإشارات: {stats['total_signals']}")
        
    except Exception as e:
        print(f"خطأ في اختبار معالج الإشارات: {e}")

def test_advanced_trade_executor():
    """اختبار منفذ الصفقات المتقدم"""
    print("\n" + "=" * 60)
    print("اختبار منفذ الصفقات المتقدم")
    print("=" * 60)
    
    try:
        from advanced_trade_executor import AdvancedTradeExecutor
        
        # إنشاء منفذ صفقات
        executor = AdvancedTradeExecutor(12345, 'bybit')
        
        # اختبار صفقة
        test_trade = {
            'symbol': 'BTCUSDT',
            'action': 'buy',
            'quantity': 0.01,
            'price': 50000
        }
        
        import asyncio
        result = asyncio.run(executor.execute_trade(test_trade))
        print(f"تنفيذ الصفقة: {'نجح' if result.success else 'فشل'}")
        if result.success:
            print(f"   معرف الأمر: {result.order_id}")
            print(f"   السعر المنفذ: {result.executed_price}")
        
        # اختبار الإحصائيات
        stats = executor.get_execution_statistics()
        print(f"إجمالي الأوامر: {stats['performance_metrics']['total_orders']}")
        
    except Exception as e:
        print(f"خطأ في اختبار منفذ الصفقات: {e}")

def test_advanced_portfolio_manager():
    """اختبار مدير المحفظة المتقدم"""
    print("\n" + "=" * 60)
    print("اختبار مدير المحفظة المتقدم")
    print("=" * 60)
    
    try:
        from advanced_portfolio_manager import AdvancedPortfolioManager
        
        # إنشاء مدير محفظة
        manager = AdvancedPortfolioManager(12345, 10000.0)
        
        # إضافة أصل
        success = manager.add_asset('BTCUSDT', 'Bitcoin', 0.1, 50000.0, 48000.0)
        print(f"إضافة أصل BTC: {'نجح' if success else 'فشل'}")
        
        # إضافة أصل آخر
        success = manager.add_asset('ETHUSDT', 'Ethereum', 1.0, 3000.0, 2900.0)
        print(f"إضافة أصل ETH: {'نجح' if success else 'فشل'}")
        
        # تحديث سعر
        manager.update_asset_price('BTCUSDT', 51000.0)
        print("تم تحديث سعر BTC إلى 51000")
        
        # اختبار تقرير المحفظة
        report = manager.get_portfolio_report()
        print(f"القيمة الإجمالية: {report['portfolio_metrics']['total_value']:.2f}")
        print(f"الربح/الخسارة: {report['portfolio_metrics']['unrealized_pnl']:.2f}")
        
    except Exception as e:
        print(f"خطأ في اختبار مدير المحفظة: {e}")

def test_advanced_risk_manager():
    """اختبار مدير المخاطر المتقدم"""
    print("\n" + "=" * 60)
    print("اختبار مدير المخاطر المتقدم")
    print("=" * 60)
    
    try:
        from advanced_risk_manager import AdvancedRiskManager
        
        # إنشاء مدير مخاطر
        risk_manager = AdvancedRiskManager(12345)
        
        # تحديث بيانات السوق
        risk_manager.update_market_data('BTCUSDT', 50000.0, 0.03)
        print("تم تحديث بيانات السوق لـ BTC")
        
        # تقييم مخاطر صفقة
        risk_assessment = risk_manager.assess_position_risk(
            'BTCUSDT', 'buy', 0.01, 50000.0, 2.0
        )
        
        print(f"تقييم مخاطر الصفقة: {'نجح' if 'position_risk' in risk_assessment else 'فشل'}")
        if 'position_risk' in risk_assessment:
            risk_score = risk_assessment['position_risk'].risk_score
            print(f"   درجة المخاطرة: {risk_score:.2f}")
        
        # اختبار فحص حدود المخاطر
        trade_data = {
            'symbol': 'BTCUSDT',
            'size': 0.01,
            'leverage': 2
        }
        
        risk_check = risk_manager.check_risk_limits(trade_data)
        print(f"فحص حدود المخاطر: {'مسموح' if risk_check['allowed'] else 'ممنوع'}")
        
    except Exception as e:
        print(f"خطأ في اختبار مدير المخاطر: {e}")

def test_signal_system_integration():
    """اختبار نظام تكامل الإشارات"""
    print("\n" + "=" * 60)
    print("اختبار نظام تكامل الإشارات")
    print("=" * 60)
    
    try:
        from signal_system_integration import get_integration_status, is_system_available, process_signal_integrated
        
        # حالة النظام
        status = get_integration_status()
        print(f"حالة النظام: {status['status']}")
        print(f"الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
        
        # قائمة الأنظمة
        print("الأنظمة المتاحة:")
        for system_name, is_available in status['systems'].items():
            status_text = "متاح" if is_available else "غير متاح"
            print(f"   {system_name}: {status_text}")
        
        # اختبار معالجة إشارة
        if is_system_available():
            test_signal = {
                'signal': 'buy',
                'symbol': 'BTCUSDT',
                'id': 'INTEGRATION_TEST_001'
            }
            
            result = process_signal_integrated(test_signal, 12345)
            print(f"معالجة الإشارة المتكاملة: {'نجح' if result['success'] else 'فشل'}")
            if result['success']:
                print(f"   النظام المستخدم: {result.get('system_used', 'غير محدد')}")
            else:
                print(f"   الخطأ: {result.get('message', 'غير محدد')}")
        else:
            print("لا توجد أنظمة متاحة للاختبار")
        
    except Exception as e:
        print(f"خطأ في اختبار نظام التكامل: {e}")

def test_system():
    """اختبار جميع الأنظمة"""
    print("بدء اختبار الأنظمة المتقدمة")
    print("=" * 80)
    
    # اختبار جميع الأنظمة
    test_advanced_signal_manager()
    test_advanced_signal_processor()
    test_advanced_trade_executor()
    test_advanced_portfolio_manager()
    test_advanced_risk_manager()
    test_signal_system_integration()
    
    print("\n" + "=" * 80)
    print("انتهى اختبار الأنظمة المتقدمة")
    print("=" * 80)

if __name__ == "__main__":
    test_system()
