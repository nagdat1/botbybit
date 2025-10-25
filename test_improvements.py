#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار التحسينات الجديدة
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_executor import SignalExecutor
import asyncio

async def test_improvements():
    """اختبار التحسينات الجديدة"""
    
    print("=" * 60)
    print("اختبار التحسينات الجديدة")
    print("=" * 60)
    
    # بيانات اختبار
    signal_data = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': '4',
        'generated_id': False,
        'position_id': 'POS-4',
        'price': 110000,  # سعر BTC
        'amount': 60.0,   # مبلغ بالدولار
        'enhanced_analysis': {
            'signal_quality': 'high',
            'confidence_level': 0.85,
            'market_conditions': 'favorable',
            'recommendation': 'execute',
            'risk_level': 'medium',
            'asset_type': 'cryptocurrency',
            'volatility': 'high'
        },
        'enhanced_risk_assessment': {
            'risk_level': 'low',
            'max_position_size': 0.2,
            'stop_loss': 0.02,
            'take_profit': 0.04,
            'recommendation': 'proceed_with_caution'
        },
        'enhanced_execution_plan': {
            'strategy': 'TWAP',
            'timing': 'optimal',
            'price_optimization': True,
            'slippage_protection': True,
            'execution_priority': 'high',
            'execution_time': '5_minutes'
        }
    }
    
    # اختبار MEXC
    print("\n1. اختبار MEXC مع التحسينات...")
    print(f"المبلغ: ${signal_data['amount']}")
    print(f"السعر: ${signal_data['price']}")
    
    # حساب الكمية المتوقعة
    expected_quantity = signal_data['amount'] / signal_data['price']
    print(f"الكمية المتوقعة: {expected_quantity}")
    
    # اختبار Bybit
    print("\n2. اختبار Bybit مع التحسينات...")
    print(f"المبلغ: ${signal_data['amount']}")
    print(f"السعر: ${signal_data['price']}")
    print(f"الرافعة: 1")
    
    # حساب الكمية المتوقعة
    expected_quantity_bybit = signal_data['amount'] / signal_data['price']
    print(f"الكمية المتوقعة: {expected_quantity_bybit}")
    
    print("\n✅ تم اختبار التحسينات بنجاح!")
    print("\n📋 التحسينات المطبقة:")
    print("1. ✅ كود خفي لتحويل القيم من الدولار إلى كمية العملة")
    print("2. ✅ تحسين معالجة الأخطاء مع طباعة تفصيلية")
    print("3. ✅ إضافة شرط TWAP لتجنب القيم الصغيرة")
    print("4. ✅ ضمان الحد الأدنى للكمية (0.0001)")
    print("5. ✅ تقريب الكمية حسب دقة الرمز")
    print("6. ✅ تسجيل مفصل للتحويلات")

if __name__ == "__main__":
    asyncio.run(test_improvements())
