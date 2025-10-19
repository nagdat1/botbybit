#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للتأكد من أن التحديثات تعمل على Railway
"""

import sys
import os
import asyncio
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_system_integration():
    """اختبار تكامل النظام المحسن"""
    print("="*60)
    print("Testing Enhanced System Integration")
    print("="*60)
    
    try:
        # اختبار النظام المحسن المبسط
        print("1. Testing Simple Enhanced System...")
        from simple_enhanced_system import SimpleEnhancedSystem
        system = SimpleEnhancedSystem()
        print("   ✓ Simple Enhanced System created successfully")
        
        # اختبار معالجة إشارة
        print("2. Testing signal processing...")
        test_signal = {
            "action": "buy",
            "symbol": "BTCUSDT",
            "price": 50000,
            "quantity": 0.001
        }
        
        result = system.process_signal(12345, test_signal)
        print(f"   ✓ Signal processed: {result.get('status', 'unknown')}")
        
        # اختبار النظام المحسن مع النظام الأصلي
        print("3. Testing integration with original system...")
        from bybit_trading_bot import TradingBot
        
        bot = TradingBot()
        if hasattr(bot, 'enhanced_system') and bot.enhanced_system:
            print("   ✓ Enhanced system integrated with TradingBot")
            
            # اختبار معالجة إشارة مع النظام المحسن
            enhanced_result = bot.enhanced_system.process_signal(12345, test_signal)
            print(f"   ✓ Enhanced signal processing: {enhanced_result.get('status', 'unknown')}")
        else:
            print("   ✗ Enhanced system not integrated with TradingBot")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_signal_executor_integration():
    """اختبار تكامل النظام المحسن مع SignalExecutor"""
    print("\n" + "="*60)
    print("Testing SignalExecutor Integration")
    print("="*60)
    
    try:
        from signal_executor import SignalExecutor, ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. Enhanced system available: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✓ Enhanced system available in SignalExecutor")
            
            # اختبار تنفيذ إشارة
            print("2. Testing signal execution...")
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
            
            print(f"   ✓ Signal execution: {result.get('success', False)}")
            
        else:
            print("   ✗ Enhanced system not available in SignalExecutor")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_signal_converter_integration():
    """اختبار تكامل النظام المحسن مع SignalConverter"""
    print("\n" + "="*60)
    print("Testing SignalConverter Integration")
    print("="*60)
    
    try:
        from signal_converter import SignalConverter, ENHANCED_SYSTEM_AVAILABLE
        
        print(f"1. Enhanced system available: {ENHANCED_SYSTEM_AVAILABLE}")
        
        if ENHANCED_SYSTEM_AVAILABLE:
            print("   ✓ Enhanced system available in SignalConverter")
            
            # اختبار تحويل إشارة
            print("2. Testing signal conversion...")
            test_signal = {
                "signal": "buy",
                "symbol": "BTCUSDT",
                "id": "TEST_001"
            }
            
            result = SignalConverter.convert_signal(test_signal)
            
            if result:
                print(f"   ✓ Signal converted: {result.get('action', 'unknown')}")
            else:
                print("   ✗ Signal conversion failed")
                
        else:
            print("   ✗ Enhanced system not available in SignalConverter")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
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
            print("   ✓ Enhanced system available in app.py")
            
            # اختبار Flask app
            print("2. Testing Flask app...")
            from app import app
            
            with app.test_client() as client:
                response = client.get('/')
                data = response.get_json()
                
                if data and data.get('system_type') == 'enhanced':
                    print("   ✓ Flask app shows enhanced system")
                else:
                    print("   ✗ Flask app does not show enhanced system")
                    return False
            
        else:
            print("   ✗ Enhanced system not available in app.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("Railway Deployment Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # اختبار التكامل
    results = {}
    
    results['Enhanced System'] = test_enhanced_system_integration()
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
        print("✓ Railway deployment ready!")
    elif success_rate >= 60:
        print("⚠ Railway deployment partially ready")
    else:
        print("✗ Railway deployment not ready")
    
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
