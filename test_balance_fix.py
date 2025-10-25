#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إصلاح مشكلة عدم كفاية الرصيد
"""

import asyncio
import logging
from balance_fix_system import enhanced_signal_executor, balance_validator
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_balance_validation():
    """اختبار التحقق من الرصيد"""
    print("🧪 اختبار نظام التحقق من الرصيد...")
    
    # بيانات اختبار وهمية
    test_user_id = 12345
    test_signal_data = {
        'action': 'buy',
        'symbol': 'BTCUSDT',
        'price': 111084.4,
        'signal_id': '4',
        'has_signal_id': True
    }
    
    test_user_data = {
        'account_type': 'real',
        'exchange': 'bybit',
        'market_type': 'futures',
        'trade_amount': 55.0,
        'leverage': 1,
        'bybit_api_key': 'test_key',
        'bybit_api_secret': 'test_secret'
    }
    
    try:
        # اختبار تنفيذ الإشارة
        result = await enhanced_signal_executor.execute_signal_with_balance_check(
            test_user_id, test_signal_data, test_user_data
        )
        
        print(f"📊 نتيجة الاختبار: {result}")
        
        if result.get('success'):
            print("✅ الاختبار نجح!")
        else:
            print(f"❌ الاختبار فشل: {result.get('message')}")
            
            # إذا كان السبب عدم كفاية الرصيد، اعرض الاقتراحات
            if result.get('error') == 'INSUFFICIENT_BALANCE':
                suggestion = result.get('suggestion', {})
                if suggestion:
                    optimal_qty = suggestion.get('optimal_quantity', 0)
                    print(f"💡 الكمية المقترحة: {optimal_qty:.6f} BTC")
                    
                    validation_info = suggestion.get('validation_info', {})
                    if validation_info:
                        print(f"💰 الرصيد المتاح: {validation_info.get('available_balance', 0):.2f} USDT")
                        print(f"💸 المبلغ المطلوب: {validation_info.get('total_required', 0):.2f} USDT")
                        print(f"📉 النقص: {validation_info.get('shortage', 0):.2f} USDT")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

def test_balance_validator():
    """اختبار مدقق الرصيد"""
    print("🧪 اختبار مدقق الرصيد...")
    
    # إنشاء حساب وهمي للاختبار
    class MockAccount:
        def get_wallet_balance(self, account_type):
            return {
                'coins': {
                    'USDT': {
                        'equity': 50.0,  # رصيد غير كافي للاختبار
                        'available': 50.0,
                        'wallet_balance': 50.0,
                        'unrealized_pnl': 0.0
                    }
                }
            }
    
    mock_account = MockAccount()
    
    # اختبار التحقق من الرصيد
    is_valid, validation_info = balance_validator.validate_balance_before_order(
        mock_account, 'BTCUSDT', 'buy', 0.001, 111084.4, 'futures', 1
    )
    
    print(f"📊 نتيجة التحقق: {is_valid}")
    print(f"📋 معلومات التحقق: {validation_info}")
    
    if not is_valid:
        print(f"❌ السبب: {validation_info.get('message')}")
        
        # اختبار اقتراح الكمية المثلى
        success, optimal_qty, suggestion_info = balance_validator.suggest_optimal_quantity(
            mock_account, 'BTCUSDT', 'buy', 111084.4, 'futures', 1
        )
        
        if success:
            print(f"💡 الكمية المثلى المقترحة: {optimal_qty:.6f} BTC")
            print(f"📊 معلومات الاقتراح: {suggestion_info}")
        else:
            print(f"❌ فشل في اقتراح الكمية: {suggestion_info}")

async def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار نظام إصلاح مشكلة عدم كفاية الرصيد")
    print("=" * 60)
    
    # اختبار مدقق الرصيد
    test_balance_validator()
    
    print("\n" + "=" * 60)
    
    # اختبار تنفيذ الإشارة
    await test_balance_validation()
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار")

if __name__ == "__main__":
    asyncio.run(main())
