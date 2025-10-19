#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار أزرار النظام الجديد
"""

def test_signal_system_integration():
    """اختبار نظام تكامل الإشارات"""
    print("=" * 60)
    print("اختبار نظام تكامل الإشارات")
    print("=" * 60)
    
    try:
        from signal_system_integration import signal_system_integration
        
        # اختبار توفر النظام
        is_available = signal_system_integration.is_available()
        print(f"✅ النظام متاح: {is_available}")
        
        if is_available:
            # اختبار حالة التكامل
            status = signal_system_integration.get_integration_status()
            print(f"📊 حالة التكامل: {status['status']}")
            print(f"📊 الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
            
            # اختبار معالجة إشارة
            test_signal = {
                'signal': 'buy',
                'symbol': 'BTCUSDT',
                'id': 'TEST_001'
            }
            
            result = signal_system_integration.process_signal(test_signal, 12345)
            print(f"🧪 نتيجة معالجة الإشارة: {result['success']}")
            if result['success']:
                print(f"   النظام المستخدم: {result.get('system_used', 'غير محدد')}")
            else:
                print(f"   الخطأ: {result.get('message', 'غير محدد')}")
        else:
            print("⚠️ النظام غير متاح")
            
    except ImportError as e:
        print(f"❌ خطأ في استيراد النظام: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")


def test_advanced_signal_manager():
    """اختبار مدير الإشارات المتقدم"""
    print("\n" + "=" * 60)
    print("اختبار مدير الإشارات المتقدم")
    print("=" * 60)
    
    try:
        from advanced_signal_manager import advanced_signal_manager
        
        # اختبار معالجة إشارة
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_ADV_001'
        }
        
        result = advanced_signal_manager.process_signal(test_signal, 12345)
        print(f"🧪 نتيجة معالجة الإشارة: {result['success']}")
        if result['success']:
            print(f"   ID الإشارة: {result['signal_id']}")
            print(f"   نوع الإشارة: {result['signal_type']}")
            print(f"   الرمز: {result['symbol']}")
        
        # اختبار الإحصائيات
        stats = advanced_signal_manager.get_signal_statistics(12345)
        print(f"📊 الإحصائيات: {stats['total_signals']} إشارة")
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد مدير الإشارات: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")


def test_enhanced_account_manager():
    """اختبار مدير الحسابات المحسن"""
    print("\n" + "=" * 60)
    print("اختبار مدير الحسابات المحسن")
    print("=" * 60)
    
    try:
        from enhanced_account_manager import enhanced_account_manager
        
        # اختبار إنشاء حساب
        account_result = enhanced_account_manager.create_account(12345, 'demo', 'futures', 'bybit')
        print(f"🧪 نتيجة إنشاء الحساب: {account_result['success']}")
        if account_result['success']:
            print(f"   ID الحساب: {account_result['account_id']}")
        
        # اختبار فتح صفقة
        signal_data = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_ACC_001'
        }
        
        position_result = enhanced_account_manager.open_position(12345, signal_data, 'demo', 'futures', 'bybit')
        print(f"🧪 نتيجة فتح الصفقة: {position_result['success']}")
        if position_result['success']:
            print(f"   ID الصفقة: {position_result['position_id']}")
            print(f"   ID الإشارة: {position_result['signal_id']}")
        
        # اختبار الإحصائيات
        stats = enhanced_account_manager.get_account_statistics(12345)
        print(f"📊 الإحصائيات: {stats['total_accounts']} حساب، {stats['total_positions']} صفقة")
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد مدير الحسابات: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")


def test_final_signal_processor():
    """اختبار معالج الإشارات النهائي"""
    print("\n" + "=" * 60)
    print("اختبار معالج الإشارات النهائي")
    print("=" * 60)
    
    try:
        from final_signal_processor import final_signal_processor
        
        # اختبار معالجة إشارة شراء
        test_signal_buy = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_PROC_001'
        }
        
        result = final_signal_processor.process_signal(test_signal_buy, 12345)
        print(f"🧪 نتيجة معالجة إشارة شراء: {result['success']}")
        if result['success']:
            print(f"   الإجراء: {result['action']}")
        
        # اختبار معالجة إشارة إغلاق
        test_signal_close = {
            'signal': 'close',
            'symbol': 'BTCUSDT',
            'id': 'TEST_PROC_002'
        }
        
        result2 = final_signal_processor.process_signal(test_signal_close, 12345)
        print(f"🧪 نتيجة معالجة إشارة إغلاق: {result2['success']}")
        if result2['success']:
            print(f"   الإجراء: {result2['action']}")
        
        # اختبار الإحصائيات
        stats = final_signal_processor.get_processing_statistics(12345)
        print(f"📊 الإحصائيات: {len(stats['supported_signals'])} نوع إشارة مدعوم")
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد معالج الإشارات: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")


def test_complete_signal_integration():
    """اختبار التكامل الكامل للإشارات"""
    print("\n" + "=" * 60)
    print("اختبار التكامل الكامل للإشارات")
    print("=" * 60)
    
    try:
        from complete_signal_integration import complete_signal_integration
        
        # اختبار حالة التكامل
        status = complete_signal_integration.get_integration_status()
        print(f"📊 حالة التكامل: {status['status']}")
        print(f"📊 المكونات المتاحة: {status['available_components']}/{status['total_components']}")
        
        # اختبار معالجة إشارة
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_COMPLETE_001'
        }
        
        result = complete_signal_integration.process_signal(test_signal, 12345)
        print(f"🧪 نتيجة معالجة الإشارة الكاملة: {result['success']}")
        if result['success']:
            print(f"   ID الإشارة: {result.get('signal_id', 'غير محدد')}")
            print(f"   ID الصفقة: {result.get('position_id', 'غير محدد')}")
            print(f"   المكونات المستخدمة: {result.get('components_used', [])}")
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد التكامل الكامل: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")


def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار النظام الجديد")
    print("=" * 80)
    
    # اختبار جميع المكونات
    test_signal_system_integration()
    test_advanced_signal_manager()
    test_enhanced_account_manager()
    test_final_signal_processor()
    test_complete_signal_integration()
    
    print("\n" + "=" * 80)
    print("✅ انتهى اختبار النظام الجديد")
    print("=" * 80)


if __name__ == "__main__":
    main()
