#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار بسيط لمشكلة MEXC بدون رموز تعبيرية
"""

import os
import sys
import time
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def test_mexc_order():
    """اختبار وضع أمر على MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== اختبار MEXC Order Placement ===")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"API Secret: {api_secret[:8]}...{api_secret[-4:]}")
    
    # إنشاء البوت
    bot = MEXCTradingBot(api_key, api_secret)
    
    # اختبار الاتصال
    print("\n1. اختبار الاتصال...")
    ping_result = bot._make_request('GET', '/api/v3/ping', signed=False)
    print(f"Ping Result: {ping_result}")
    
    # اختبار الحصول على السعر
    print("\n2. اختبار الحصول على السعر...")
    price = bot.get_ticker_price('BTCUSDT')
    print(f"BTCUSDT Price: {price}")
    
    if not price:
        print("فشل في الحصول على السعر")
        return
    
    # اختبار معلومات الرمز
    print("\n3. اختبار معلومات الرمز...")
    symbol_info = bot.get_symbol_info('BTCUSDT')
    print(f"Symbol Info: {symbol_info}")
    
    if not symbol_info:
        print("فشل في الحصول على معلومات الرمز")
        return
    
    # اختبار الرصيد
    print("\n4. اختبار الرصيد...")
    balance = bot.get_account_balance()
    print(f"Balance: {balance}")
    
    # اختبار وضع أمر صغير
    print("\n5. اختبار وضع أمر...")
    quantity = 0.0001  # كمية صغيرة جداً
    
    print(f"محاولة وضع أمر: BUY {quantity} BTCUSDT")
    result = bot.place_spot_order(
        symbol='BTCUSDT',
        side='BUY',
        quantity=quantity,
        order_type='MARKET'
    )
    
    print(f"نتيجة الأمر: {result}")
    
    if result:
        print("نجح وضع الأمر!")
    else:
        print("فشل وضع الأمر")
        
        # تشخيص إضافي
        print("\n=== تشخيص إضافي ===")
        
        # اختبار تنسيق الكمية
        formatted_qty = bot._format_quantity(quantity, symbol_info)
        print(f"الكمية المنسقة: {formatted_qty}")
        
        # اختبار معاملات الأمر
        params = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': formatted_qty
        }
        
        print(f"معاملات الأمر: {params}")
        
        # اختبار التوقيع
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp
        signature = bot._generate_signature(params)
        params['signature'] = signature
        
        print(f"التوقيع: {signature}")
        
        # اختبار الطلب المباشر
        print("\nاختبار الطلب المباشر...")
        direct_result = bot._make_request('POST', '/api/v3/order', params, signed=True)
        print(f"النتيجة المباشرة: {direct_result}")

if __name__ == "__main__":
    test_mexc_order()
