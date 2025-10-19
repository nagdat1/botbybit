#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام ربط ID الإشارة برقم الصفقة
"""

import sys
import os
import asyncio
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_signal_id_manager():
    """اختبار مدير معرفات الإشارات"""
    print("="*60)
    print("Testing Signal ID Manager")
    print("="*60)
    
    try:
        from signal_id_manager import SignalIDManager
        
        # إنشاء مثيل مدير معرفات الإشارات
        manager = SignalIDManager()
        print("1. Signal ID Manager created successfully")
        
        # اختبار توليد ID عشوائي
        random_id = manager.generate_random_id("BTCUSDT")
        print(f"2. Random ID generated: {random_id}")
        
        # اختبار توليد رقم صفقة
        position_id = manager.generate_position_id(random_id)
        print(f"3. Position ID generated: {position_id}")
        
        # اختبار ربط ID الإشارة برقم الصفقة
        link_result = manager.link_signal_to_position(random_id, position_id)
        print(f"4. Link result: {link_result}")
        
        # اختبار الحصول على رقم الصفقة من ID الإشارة
        retrieved_position_id = manager.get_position_id_from_signal(random_id)
        print(f"5. Retrieved position ID: {retrieved_position_id}")
        
        # اختبار الحصول على ID الإشارة من رقم الصفقة
        retrieved_signal_id = manager.get_signal_id_from_position(position_id)
        print(f"6. Retrieved signal ID: {retrieved_signal_id}")
        
        # اختبار معالجة بيانات الإشارة
        test_signal = {
            "signal": "buy",
            "symbol": "BTCUSDT",
            "price": 50000
        }
        
        processed_signal = manager.process_signal_id(test_signal)
        print(f"7. Processed signal: {processed_signal}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_converter_with_id():
    """اختبار محول الإشارات مع نظام ID"""
    print("\n" + "="*60)
    print("Testing Signal Converter with ID System")
    print("="*60)
    
    try:
        from signal_converter import SignalConverter
        
        print("1. SignalConverter imported successfully")
        
        # اختبار إشارة بدون ID
        signal_without_id = {
            "signal": "buy",
            "symbol": "BTCUSDT"
        }
        
        print("2. Testing signal without ID...")
        converted_signal = SignalConverter.convert_signal(signal_without_id)
        
        if converted_signal:
            print(f"   Converted signal: {converted_signal}")
            print(f"   Signal ID: {converted_signal.get('signal_id', 'N/A')}")
            print(f"   Position ID: {converted_signal.get('position_id', 'N/A')}")
            print(f"   Generated ID: {converted_signal.get('generated_id', 'N/A')}")
        else:
            print("   Failed to convert signal")
            return False
        
        # اختبار إشارة مع ID محدد
        signal_with_id = {
            "signal": "sell",
            "symbol": "ETHUSDT",
            "id": "TV_ETH_001"
        }
        
        print("3. Testing signal with predefined ID...")
        converted_signal_with_id = SignalConverter.convert_signal(signal_with_id)
        
        if converted_signal_with_id:
            print(f"   Converted signal: {converted_signal_with_id}")
            print(f"   Signal ID: {converted_signal_with_id.get('signal_id', 'N/A')}")
            print(f"   Position ID: {converted_signal_with_id.get('position_id', 'N/A')}")
            print(f"   Generated ID: {converted_signal_with_id.get('generated_id', 'N/A')}")
        else:
            print("   Failed to convert signal")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_executor_with_id():
    """اختبار منفذ الإشارات مع نظام ID"""
    print("\n" + "="*60)
    print("Testing Signal Executor with ID System")
    print("="*60)
    
    try:
        from signal_executor import SIGNAL_ID_MANAGER_AVAILABLE
        
        print(f"1. Signal ID Manager available: {SIGNAL_ID_MANAGER_AVAILABLE}")
        
        if SIGNAL_ID_MANAGER_AVAILABLE:
            print("   Signal ID Manager is available in Signal Executor")
            return True
        else:
            print("   Signal ID Manager is not available in Signal Executor")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_bybit_trading_bot_with_id():
    """اختبار بوت التداول مع نظام ID"""
    print("\n" + "="*60)
    print("Testing Bybit Trading Bot with ID System")
    print("="*60)
    
    try:
        from bybit_trading_bot import SIGNAL_ID_MANAGER_AVAILABLE
        
        print(f"1. Signal ID Manager available: {SIGNAL_ID_MANAGER_AVAILABLE}")
        
        if SIGNAL_ID_MANAGER_AVAILABLE:
            print("   Signal ID Manager is available in Bybit Trading Bot")
            return True
        else:
            print("   Signal ID Manager is not available in Bybit Trading Bot")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_complete_workflow():
    """اختبار سير العمل الكامل"""
    print("\n" + "="*60)
    print("Testing Complete Workflow")
    print("="*60)
    
    try:
        from signal_converter import SignalConverter
        from signal_id_manager import get_signal_id_manager
        
        print("1. Testing complete signal processing workflow...")
        
        # إشارة بدون ID
        signal_data = {
            "signal": "buy",
            "symbol": "BTCUSDT",
            "price": 50000
        }
        
        # تحويل الإشارة
        converted_signal = SignalConverter.convert_signal(signal_data)
        
        if converted_signal:
            signal_id = converted_signal.get('signal_id')
            position_id = converted_signal.get('position_id')
            
            print(f"   Signal ID: {signal_id}")
            print(f"   Position ID: {position_id}")
            
            # التحقق من الربط
            manager = get_signal_id_manager()
            retrieved_position_id = manager.get_position_id_from_signal(signal_id)
            retrieved_signal_id = manager.get_signal_id_from_position(position_id)
            
            print(f"   Retrieved position ID: {retrieved_position_id}")
            print(f"   Retrieved signal ID: {retrieved_signal_id}")
            
            if retrieved_position_id == position_id and retrieved_signal_id == signal_id:
                print("   ✅ ID linking works correctly")
                return True
            else:
                print("   ❌ ID linking failed")
                return False
        else:
            print("   ❌ Signal conversion failed")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("Signal ID System Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # اختبار النظام
    results = {}
    
    results['Signal ID Manager'] = test_signal_id_manager()
    results['Signal Converter'] = test_signal_converter_with_id()
    results['Signal Executor'] = test_signal_executor_with_id()
    results['Bybit Trading Bot'] = test_bybit_trading_bot_with_id()
    results['Complete Workflow'] = test_complete_workflow()
    
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
        print("Signal ID System is ready for deployment!")
        print("\nUsage Examples:")
        print("1. Signal without ID (auto-generated):")
        print('   {"signal": "buy", "symbol": "BTCUSDT"}')
        print("2. Signal with predefined ID:")
        print('   {"signal": "sell", "symbol": "ETHUSDT", "id": "TV_ETH_001"}')
        print("3. Partial close with ID:")
        print('   {"signal": "partial_close", "symbol": "BTCUSDT", "percentage": 50, "id": "BTCUSDT-20251019-031540-7KQ2"}')
    elif success_rate >= 60:
        print("Signal ID System is partially ready")
    else:
        print("Signal ID System is not ready")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
