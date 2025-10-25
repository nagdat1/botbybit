#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مباشر لوضع الأوامر في Futures Trading
"""

import sys
import os
import asyncio
import logging

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_direct_order_placement():
    """اختبار مباشر لوضع الأوامر"""
    
    print("=== اختبار مباشر لوضع الأوامر في Futures Trading ===")
    print()
    
    try:
        # إنشاء حساب حقيقي
        user_id = 999999
        api_key = "dqBHnPaItfmEZSB020"
        api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
        
        print(f"إنشاء حساب حقيقي للمستخدم {user_id}")
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        
        # الحصول على الحساب
        account = real_account_manager.get_account(user_id)
        if not account:
            print("فشل في إنشاء الحساب الحقيقي")
            return False
        
        print("تم إنشاء الحساب الحقيقي بنجاح")
        print()
        
        # اختبار جلب الرصيد
        print("1. اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('UNIFIED')
        if balance:
            print(f"الرصيد: {balance}")
        else:
            print("فشل في جلب الرصيد")
            return False
        
        print()
        
        # اختبار جلب السعر
        print("2. اختبار جلب السعر...")
        ticker = account.get_ticker('linear', 'BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            price = float(ticker['lastPrice'])
            print(f"سعر BTCUSDT: ${price:,.2f}")
        else:
            print("فشل في جلب السعر")
            return False
        
        print()
        
        # اختبار وضع الرافعة المالية
        print("3. اختبار وضع الرافعة المالية...")
        leverage_result = account.set_leverage('linear', 'BTCUSDT', 2)
        if leverage_result:
            print("تم وضع الرافعة المالية بنجاح!")
        else:
            print("فشل في وضع الرافعة المالية - هذا قد يكون السبب!")
            print("تحقق من صلاحيات Position Management في API Key")
            return False
        
        print()
        
        # اختبار وضع أمر Futures
        print("4. اختبار وضع أمر Futures...")
        print(f"الكمية: 0.001 BTC")
        print(f"السعر: ${price:,.2f}")
        print(f"الرافعة: 2x")
        print()
        
        # حساب الكمية
        qty = 0.001  # كمية صغيرة للاختبار
        
        # وضع أمر Buy
        result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=qty,
            leverage=2
        )
        
        if result and result.get('success'):
            print("تم وضع الأمر بنجاح!")
            print(f"Order ID: {result.get('order_id', 'N/A')}")
            print()
            print("الآن يجب أن ترى الصفقة في Bybit!")
            return True
        else:
            print("فشل في وضع الأمر")
            if result:
                print(f"الخطأ: {result.get('error', 'Unknown error')}")
                print(f"تفاصيل الخطأ: {result.get('error_details', 'No details')}")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_order_placement())
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل")
        sys.exit(1)
