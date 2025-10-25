#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إصلاح مشكلة Bybit
"""

import os
import sys
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from signal_executor import SignalExecutor
from real_account_manager import BybitRealAccount
from bybit_trading_bot import TradingBot

def test_bybit_order():
    """اختبار وضع أمر على Bybit"""
    
    print("=== اختبار Bybit Order Placement ===")
    
    # مفاتيح API (يجب أن تكون في .env)
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print(" مفاتيح Bybit API غير موجودة في .env")
        return
    
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"API Secret: {api_secret[:8]}...{api_secret[-4:]}")
    
    # إنشاء البوت والحساب
    bot = TradingBot()
    bot.set_api_keys(api_key, api_secret)
    account = BybitRealAccount(bot)
    
    # بيانات الإشارة التجريبية
    signal_data = {
        'action': 'buy',
        'symbol': 'BTCUSDT',
        'price': 110000.0,
        'signal_id': 'TEST-123',
        'has_signal_id': True
    }
    
    print(f"\nبيانات الإشارة: {signal_data}")
    
    # اختبار تنفيذ الإشارة
    print("\nاختبار تنفيذ الإشارة...")
    
    try:
        import asyncio
        
        async def run_test():
            result = await SignalExecutor.execute_signal(
                account=account,
                signal_data=signal_data,
                market_type='futures',
                trade_amount=10.0,  # $10
                leverage=1,
                user_id=12345
            )
            
            print(f"نتيجة التنفيذ: {result}")
            
            if result.get('success'):
                print(" نجح تنفيذ الإشارة!")
            else:
                print(f" فشل تنفيذ الإشارة: {result.get('message')}")
        
        # تشغيل الاختبار
        asyncio.run(run_test())
        
    except Exception as e:
        print(f" خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bybit_order()
