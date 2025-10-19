#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للتأكد من أن التحديثات تعمل على Railway
"""

import sys
import os

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_system():
    """اختبار النظام المحسن"""
    print("="*60)
    print("Testing Enhanced System")
    print("="*60)
    
    try:
        # اختبار النظام المحسن المبسط
        print("1. Testing Simple Enhanced System...")
        from simple_enhanced_system import SimpleEnhancedSystem
        system = SimpleEnhancedSystem()
        print("   Simple Enhanced System created successfully")
        
        # اختبار معالجة إشارة
        print("2. Testing signal processing...")
        test_signal = {
            "action": "buy",
            "symbol": "BTCUSDT",
            "price": 50000,
            "quantity": 0.001
        }
        
        result = system.process_signal(12345, test_signal)
        print(f"   Signal processed: {result.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

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
        print(f"   Error: {e}")
        return False

def test_signal_executor_integration():
    """اختبار تكامل النظام المحسن مع SignalExecutor"""
    print("\n" + "="*60)
    print("Testing SignalExecutor Integration")
    print("="*60)
    
    try:
        from signal_executor import ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. Enhanced system available: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   Enhanced system is available in SignalExecutor")
            return True
        else:
            print("   Enhanced system is not available in SignalExecutor")
            return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_signal_converter_integration():
    """اختبار تكامل النظام المحسن مع SignalConverter"""
    print("\n" + "="*60)
    print("Testing SignalConverter Integration")
    print("="*60)
    
    try:
        from signal_converter import ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. Enhanced system available: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   Enhanced system is available in SignalConverter")
            return True
        else:
            print("   Enhanced system is not available in SignalConverter")
            return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_app_integration():
    """اختبار تكامل النظام المحسن مع app.py"""
    print("\n" + "="*60)
    print("Testing App Integration")
    print("="*60)
    
    try:
        from app import ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. Enhanced system available: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   Enhanced system is available in app.py")
            return True
        else:
            print("   Enhanced system is not available in app.py")
            return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("Railway Deployment Test")
    print("="*60)
    
    # اختبار التكامل
    results = {}
    
    results['Enhanced System'] = test_enhanced_system()
    results['TradingBot'] = test_trading_bot_integration()
    results['SignalExecutor'] = test_signal_executor_integration()
    results['SignalConverter'] = test_signal_converter_integration()
    results['App'] = test_app_integration()
    
    # عرض النتائج النهائية
    print("\n" + "="*60)
    print("Final Results")
    print("="*60)
    
    for test_name, success in results.items():
        status = "Success" if success else "Failed"
        print(f"   {test_name}: {status}")
    
    # حساب النسبة المئوية للنجاح
    total_tests = len(results)
    successful_tests = sum(results.values())
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("Railway deployment ready!")
    elif success_rate >= 60:
        print("Railway deployment partially ready")
    else:
        print("Railway deployment not ready")
    
    print("\n" + "="*60)
    
    # تعليمات النشر
    if success_rate >= 80:
        print("\nDeployment Instructions:")
        print("1. git add .")
        print("2. git commit -m 'Enhanced system integration'")
        print("3. git push origin main")
        print("4. Railway will automatically redeploy")
        print("5. Check logs for enhanced system messages")
    
    print("="*60)

if __name__ == "__main__":
    main()
