#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار بسيط لوضع الأوامر في MEXC
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mexc_trading_bot import create_mexc_bot

def test_order():
    """اختبار وضع الأمر"""
    
    print("=" * 50)
    print("اختبار بسيط لوضع الأوامر في MEXC")
    print("=" * 50)
    
    # إنشاء البوت
    bot = create_mexc_bot('mx0vglb3kLs2Rbe8pG', 'cd479996b38a4944933bbe79015ffa09')
    
    # اختبار الاتصال
    print("\n1. اختبار الاتصال...")
    connection_result = bot.test_connection()
    print(f"الاتصال: {'نجح' if connection_result else 'فشل'}")
    
    if not connection_result:
        print("فشل الاتصال!")
        return
    
    # اختبار جلب السعر
    print("\n2. اختبار جلب السعر...")
    price = bot.get_ticker_price('BTCUSDT')
    print(f"السعر: {price}")
    
    if not price:
        print("فشل جلب السعر!")
        return
    
    # اختبار جلب الرصيد
    print("\n3. اختبار جلب الرصيد...")
    balance = bot.get_account_balance()
    print(f"الرصيد: {balance}")
    
    if not balance:
        print("فشل جلب الرصيد!")
        return
    
    # اختبار وضع الأمر
    print("\n4. اختبار وضع الأمر...")
    quantity = 0.0001  # كمية صغيرة للاختبار
    print(f"الكمية: {quantity}")
    
    result = bot.place_spot_order('BTCUSDT', 'BUY', quantity, 'MARKET')
    print(f"نتيجة الأمر: {result}")
    
    if result is None:
        print("فشل وضع الأمر!")
    else:
        print("نجح وضع الأمر!")

if __name__ == "__main__":
    test_order()
