#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض ID الإشارة في الصفقات المفتوحة
"""

import sys
import os
import asyncio
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_signal_id_display():
    """اختبار عرض ID الإشارة في الصفقات المفتوحة"""
    print("="*60)
    print("Testing Signal ID Display in Open Positions")
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
        
        # اختبار الحصول على ID الإشارة من رقم الصفقة
        retrieved_signal_id = manager.get_signal_id_from_position(position_id)
        print(f"5. Retrieved signal ID: {retrieved_signal_id}")
        
        # اختبار عرض ID الإشارة
        if retrieved_signal_id:
            signal_id_display = f"🆔 ID الإشارة: {retrieved_signal_id}\n"
            print(f"6. Signal ID Display: {signal_id_display.strip()}")
        else:
            print("6. Signal ID Display: No signal ID found")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_converter_with_id_display():
    """اختبار محول الإشارات مع عرض ID"""
    print("\n" + "="*60)
    print("Testing Signal Converter with ID Display")
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
            signal_id = converted_signal.get('signal_id', 'N/A')
            position_id = converted_signal.get('position_id', 'N/A')
            
            print(f"   Signal ID: {signal_id}")
            print(f"   Position ID: {position_id}")
            
            # اختبار عرض ID الإشارة
            if signal_id and signal_id != 'N/A':
                signal_id_display = f"🆔 ID الإشارة: {signal_id}\n"
                print(f"   Signal ID Display: {signal_id_display.strip()}")
            else:
                print("   Signal ID Display: No signal ID")
            
            return True
        else:
            print("   Failed to convert signal")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_open_positions_display():
    """اختبار عرض الصفقات المفتوحة مع ID الإشارة"""
    print("\n" + "="*60)
    print("Testing Open Positions Display with Signal ID")
    print("="*60)
    
    try:
        from signal_id_manager import get_signal_id_manager
        
        # إنشاء بيانات صفقة وهمية
        position_id = "demo_BTCUSDT_123"
        signal_id = "BTCUSDT-20251019-055526-QIFD"
        
        # ربط ID الإشارة برقم الصفقة
        manager = get_signal_id_manager()
        manager.link_signal_to_position(signal_id, position_id)
        
        print(f"1. Linked signal ID {signal_id} to position ID {position_id}")
        
        # اختبار الحصول على ID الإشارة من رقم الصفقة
        retrieved_signal_id = manager.get_signal_id_from_position(position_id)
        print(f"2. Retrieved signal ID: {retrieved_signal_id}")
        
        # اختبار عرض ID الإشارة
        if retrieved_signal_id:
            signal_id_display = f"🆔 ID الإشارة: {retrieved_signal_id}\n"
            print(f"3. Signal ID Display: {signal_id_display.strip()}")
            
            # محاكاة عرض الصفقة
            position_display = f"""
🟢💰 BTCUSDT
🔄 النوع: BUY
💲 سعر الدخول: 50000.000000
💲 السعر الحالي: 51000.000000
💰 المبلغ: 100.00
⬆️ الربح/الخسارة: 2.00 (2.00%) - رابح
{signal_id_display}🆔 رقم الصفقة: {position_id}
            """
            
            print("4. Complete Position Display:")
            print(position_display.strip())
            
            return True
        else:
            print("3. Signal ID Display: No signal ID found")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("Signal ID Display Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # اختبار النظام
    results = {}
    
    results['Signal ID Display'] = test_signal_id_display()
    results['Signal Converter with ID Display'] = test_signal_converter_with_id_display()
    results['Open Positions Display'] = test_open_positions_display()
    
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
        print("Signal ID Display System is ready!")
        print("\nNow when you send a signal with ID, it will appear in open positions:")
        print("Example:")
        print("🟢💰 BTCUSDT")
        print("🔄 النوع: BUY")
        print("💲 سعر الدخول: 50000.000000")
        print("💲 السعر الحالي: 51000.000000")
        print("💰 المبلغ: 100.00")
        print("⬆️ الربح/الخسارة: 2.00 (2.00%) - رابح")
        print("🆔 ID الإشارة: BTCUSDT-20251019-055526-QIFD")
        print("🆔 رقم الصفقة: demo_BTCUSDT_123")
    elif success_rate >= 60:
        print("Signal ID Display System is partially ready")
    else:
        print("Signal ID Display System is not ready")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
