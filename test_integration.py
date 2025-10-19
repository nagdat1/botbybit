#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للتكامل بين النظام المحسن والنظام الأصلي
"""

import sys
import os
import asyncio
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_system_availability():
    """اختبار توفر النظام المحسن في جميع الملفات"""
    print("="*60)
    print("🧪 اختبار توفر النظام المحسن في جميع الملفات")
    print("="*60)
    
    files_to_test = [
        "bybit_trading_bot.py",
        "signal_executor.py", 
        "signal_converter.py",
        "user_manager.py",
        "app.py"
    ]
    
    results = {}
    
    for file_name in files_to_test:
        try:
            print(f"\n📁 اختبار {file_name}...")
            
            if file_name == "bybit_trading_bot.py":
                from bybit_trading_bot import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   {'✅' if ENHANCED_SYSTEM_AVAILABLE else '❌'} النظام المحسن: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "signal_executor.py":
                from signal_executor import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   {'✅' if ENHANCED_SYSTEM_AVAILABLE else '❌'} النظام المحسن: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "signal_converter.py":
                from signal_converter import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   {'✅' if ENHANCED_SYSTEM_AVAILABLE else '❌'} النظام المحسن: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "user_manager.py":
                from user_manager import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   {'✅' if ENHANCED_SYSTEM_AVAILABLE else '❌'} النظام المحسن: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "app.py":
                from app import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   {'✅' if ENHANCED_SYSTEM_AVAILABLE else '❌'} النظام المحسن: {ENHANCED_SYSTEM_AVAILABLE}")
                
        except Exception as e:
            print(f"   ❌ خطأ في اختبار {file_name}: {e}")
            results[file_name] = False
    
    print(f"\n📊 النتائج:")
    for file_name, available in results.items():
        status = "✅ متاح" if available else "❌ غير متاح"
        print(f"   {file_name}: {status}")
    
    return results

def test_trading_bot_integration():
    """اختبار تكامل النظام المحسن مع TradingBot"""
    print("\n" + "="*60)
    print("🧪 اختبار تكامل النظام المحسن مع TradingBot")
    print("="*60)
    
    try:
        from bybit_trading_bot import TradingBot
        
        print("1. إنشاء مثيل من TradingBot...")
        bot = TradingBot()
        print("   ✅ تم إنشاء TradingBot بنجاح")
        
        print("2. فحص النظام المحسن في TradingBot...")
        if hasattr(bot, 'enhanced_system') and bot.enhanced_system:
            print("   ✅ النظام المحسن متاح في TradingBot")
            
            # اختبار معالجة إشارة
            print("3. اختبار معالجة إشارة...")
            test_signal = {
                "action": "buy",
                "symbol": "BTCUSDT",
                "price": 50000,
                "quantity": 0.001
            }
            
            result = bot.enhanced_system.process_signal(12345, test_signal)
            print(f"   ✅ تم معالجة الإشارة: {result.get('status', 'unknown')}")
            
        else:
            print("   ❌ النظام المحسن غير متاح في TradingBot")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في اختبار TradingBot: {e}")
        return False

def test_signal_executor_integration():
    """اختبار تكامل النظام المحسن مع SignalExecutor"""
    print("\n" + "="*60)
    print("🧪 اختبار تكامل النظام المحسن مع SignalExecutor")
    print("="*60)
    
    try:
        from signal_executor import SignalExecutor, ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. فحص النظام المحسن في SignalExecutor: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✅ النظام المحسن متاح في SignalExecutor")
            
            # اختبار تنفيذ إشارة
            print("2. اختبار تنفيذ إشارة...")
            test_signal = {
                "action": "buy",
                "symbol": "BTCUSDT",
                "price": 50000,
                "quantity": 0.001
            }
            
            test_user_data = {
                "account_type": "demo",
                "exchange": "bybit",
                "market_type": "spot"
            }
            
            # اختبار غير متزامن
            async def test_execution():
                result = await SignalExecutor.execute_signal(12345, test_signal, test_user_data)
                return result
            
            # تشغيل الاختبار
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_execution())
            loop.close()
            
            print(f"   ✅ تم تنفيذ الإشارة: {result.get('success', False)}")
            
        else:
            print("   ❌ النظام المحسن غير متاح في SignalExecutor")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في اختبار SignalExecutor: {e}")
        return False

def test_signal_converter_integration():
    """اختبار تكامل النظام المحسن مع SignalConverter"""
    print("\n" + "="*60)
    print("🧪 اختبار تكامل النظام المحسن مع SignalConverter")
    print("="*60)
    
    try:
        from signal_converter import SignalConverter, ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. فحص النظام المحسن في SignalConverter: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✅ النظام المحسن متاح في SignalConverter")
            
            # اختبار تحويل إشارة
            print("2. اختبار تحويل إشارة...")
            test_signal = {
                "signal": "buy",
                "symbol": "BTCUSDT",
                "id": "TEST_001"
            }
            
            result = SignalConverter.convert_signal(test_signal)
            
            if result:
                print(f"   ✅ تم تحويل الإشارة: {result.get('action', 'unknown')}")
            else:
                print("   ❌ فشل في تحويل الإشارة")
                
        else:
            print("   ❌ النظام المحسن غير متاح في SignalConverter")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في اختبار SignalConverter: {e}")
        return False

def test_user_manager_integration():
    """اختبار تكامل النظام المحسن مع UserManager"""
    print("\n" + "="*60)
    print("🧪 اختبار تكامل النظام المحسن مع UserManager")
    print("="*60)
    
    try:
        from user_manager import UserManager, ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. فحص النظام المحسن في UserManager: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✅ النظام المحسن متاح في UserManager")
            
            # اختبار إنشاء UserManager
            print("2. اختبار إنشاء UserManager...")
            user_manager = UserManager()
            
            if hasattr(user_manager, 'enhanced_system') and user_manager.enhanced_system:
                print("   ✅ النظام المحسن متاح في UserManager")
                
                # اختبار معالجة إشارة
                print("3. اختبار معالجة إشارة...")
                test_signal = {
                    "action": "buy",
                    "symbol": "BTCUSDT",
                    "price": 50000,
                    "quantity": 0.001
                }
                
                result = user_manager.enhanced_system.process_signal(12345, test_signal)
                print(f"   ✅ تم معالجة الإشارة: {result.get('status', 'unknown')}")
                
            else:
                print("   ❌ النظام المحسن غير متاح في UserManager")
                return False
                
        else:
            print("   ❌ النظام المحسن غير متاح في UserManager")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في اختبار UserManager: {e}")
        return False

def test_app_integration():
    """اختبار تكامل النظام المحسن مع app.py"""
    print("\n" + "="*60)
    print("🧪 اختبار تكامل النظام المحسن مع app.py")
    print("="*60)
    
    try:
        from app import ENHANCED_SYSTEM_AVAILABLE, enhanced_system
        
        print(f"1. فحص النظام المحسن في app.py: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✅ النظام المحسن متاح في app.py")
            
            if enhanced_system:
                print("   ✅ تم تهيئة النظام المحسن في app.py")
            else:
                print("   ⚠️ النظام المحسن متاح لكن لم يتم تهيئته بعد")
                
        else:
            print("   ❌ النظام المحسن غير متاح في app.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في اختبار app.py: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار شامل للتكامل بين النظام المحسن والنظام الأصلي")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # اختبار توفر النظام المحسن
    availability_results = test_enhanced_system_availability()
    
    # اختبار التكامل مع كل ملف
    integration_results = {}
    
    integration_results['TradingBot'] = test_trading_bot_integration()
    integration_results['SignalExecutor'] = test_signal_executor_integration()
    integration_results['SignalConverter'] = test_signal_converter_integration()
    integration_results['UserManager'] = test_user_manager_integration()
    integration_results['app.py'] = test_app_integration()
    
    # عرض النتائج النهائية
    print("\n" + "="*60)
    print("📊 النتائج النهائية")
    print("="*60)
    
    print("\n🔍 توفر النظام المحسن:")
    for file_name, available in availability_results.items():
        status = "✅ متاح" if available else "❌ غير متاح"
        print(f"   {file_name}: {status}")
    
    print("\n🔗 التكامل:")
    for component, success in integration_results.items():
        status = "✅ نجح" if success else "❌ فشل"
        print(f"   {component}: {status}")
    
    # حساب النسبة المئوية للنجاح
    total_tests = len(availability_results) + len(integration_results)
    successful_tests = sum(availability_results.values()) + sum(integration_results.values())
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n📈 معدل النجاح: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 التكامل نجح بنجاح!")
    elif success_rate >= 60:
        print("⚠️ التكامل نجح جزئياً")
    else:
        print("❌ التكامل فشل")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
