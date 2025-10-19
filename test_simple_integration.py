#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للتكامل بين النظام المحسن والنظام الأصلي
"""

import sys
import os

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_system_availability():
    """اختبار توفر النظام المحسن في جميع الملفات"""
    print("="*60)
    print("Testing Enhanced System Availability in All Files")
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
            print(f"\nTesting {file_name}...")
            
            if file_name == "bybit_trading_bot.py":
                from bybit_trading_bot import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   Enhanced System: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "signal_executor.py":
                from signal_executor import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   Enhanced System: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "signal_converter.py":
                from signal_converter import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   Enhanced System: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "user_manager.py":
                from user_manager import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   Enhanced System: {ENHANCED_SYSTEM_AVAILABLE}")
                
            elif file_name == "app.py":
                from app import ENHANCED_SYSTEM_AVAILABLE
                results[file_name] = ENHANCED_SYSTEM_AVAILABLE
                print(f"   Enhanced System: {ENHANCED_SYSTEM_AVAILABLE}")
                
        except Exception as e:
            print(f"   Error testing {file_name}: {e}")
            results[file_name] = False
    
    print(f"\nResults:")
    for file_name, available in results.items():
        status = "Available" if available else "Not Available"
        print(f"   {file_name}: {status}")
    
    return results

def test_trading_bot_integration():
    """اختبار تكامل النظام المحسن مع TradingBot"""
    print("\n" + "="*60)
    print("Testing TradingBot Integration")
    print("="*60)
    
    try:
        from bybit_trading_bot import TradingBot
        
        print("1. Creating TradingBot instance...")
        bot = TradingBot()
        print("   TradingBot created successfully")
        
        print("2. Checking Enhanced System in TradingBot...")
        if hasattr(bot, 'enhanced_system') and bot.enhanced_system:
            print("   Enhanced System is available in TradingBot")
            
            # اختبار معالجة إشارة
            print("3. Testing signal processing...")
            test_signal = {
                "action": "buy",
                "symbol": "BTCUSDT",
                "price": 50000,
                "quantity": 0.001
            }
            
            result = bot.enhanced_system.process_signal(12345, test_signal)
            print(f"   Signal processed: {result.get('status', 'unknown')}")
            
        else:
            print("   Enhanced System is not available in TradingBot")
            return False
        
        return True
        
    except Exception as e:
        print(f"   Error testing TradingBot: {e}")
        return False

def test_simple_enhanced_system():
    """اختبار النظام المحسن المبسط"""
    print("\n" + "="*60)
    print("Testing Simple Enhanced System")
    print("="*60)
    
    try:
        from simple_enhanced_system import SimpleEnhancedSystem
        
        print("1. Creating Simple Enhanced System instance...")
        system = SimpleEnhancedSystem()
        print("   Simple Enhanced System created successfully")
        
        print("2. Testing signal processing...")
        test_signal = {
            "action": "buy",
            "symbol": "BTCUSDT",
            "price": 50000,
            "quantity": 0.001
        }
        
        result = system.process_signal(12345, test_signal)
        print(f"   Signal processed: {result.get('status', 'unknown')}")
        
        print("3. Testing system status...")
        status = system.get_system_status()
        print(f"   System status: {status.get('system_type', 'unknown')}")
        
        print("4. Testing performance report...")
        report = system.get_performance_report()
        print(f"   Performance report generated")
        
        return True
        
    except Exception as e:
        print(f"   Error testing Simple Enhanced System: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("Comprehensive Integration Test")
    print("="*60)
    
    # اختبار توفر النظام المحسن
    availability_results = test_enhanced_system_availability()
    
    # اختبار التكامل مع TradingBot
    trading_bot_result = test_trading_bot_integration()
    
    # اختبار النظام المحسن المبسط
    simple_system_result = test_simple_enhanced_system()
    
    # عرض النتائج النهائية
    print("\n" + "="*60)
    print("Final Results")
    print("="*60)
    
    print("\nEnhanced System Availability:")
    for file_name, available in availability_results.items():
        status = "Available" if available else "Not Available"
        print(f"   {file_name}: {status}")
    
    print(f"\nTradingBot Integration: {'Success' if trading_bot_result else 'Failed'}")
    print(f"Simple Enhanced System: {'Success' if simple_system_result else 'Failed'}")
    
    # حساب النسبة المئوية للنجاح
    total_tests = len(availability_results) + 2
    successful_tests = sum(availability_results.values()) + (1 if trading_bot_result else 0) + (1 if simple_system_result else 0)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("Integration successful!")
    elif success_rate >= 60:
        print("Integration partially successful")
    else:
        print("Integration failed")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
