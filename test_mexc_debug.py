#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مفصل لمشكلة MEXC
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mexc_trading_bot import create_mexc_bot
import logging

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_mexc_debug():
    """اختبار مفصل لمشكلة MEXC"""
    
    print("=" * 60)
    print("اختبار مفصل لمشكلة MEXC")
    print("=" * 60)
    
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
    
    # اختبار جلب معلومات الرمز
    print("\n4. اختبار جلب معلومات الرمز...")
    symbol_info = bot.get_symbol_info('BTCUSDT')
    print(f"معلومات الرمز: {symbol_info}")
    
    if not symbol_info:
        print("فشل جلب معلومات الرمز!")
        return
    
    # اختبار وضع الأمر
    print("\n5. اختبار وضع الأمر...")
    quantity = 0.0001  # كمية صغيرة للاختبار
    print(f"الكمية: {quantity}")
    
    result = bot.place_spot_order('BTCUSDT', 'BUY', quantity, 'MARKET')
    print(f"نتيجة الأمر: {result}")
    
    if result is None:
        print("فشل وضع الأمر!")
        print("\nفحص السبب الدقيق...")
        
        # فحص السبب الدقيق
        print("\nفحص السبب الدقيق...")
        
        # اختبار الطلب المباشر
        print("\n6. اختبار الطلب المباشر...")
        try:
            import requests
            import time
            import hmac
            import hashlib
            from urllib.parse import urlencode
            
            # إعداد الطلب
            url = "https://api.mexc.com/api/v3/order"
            timestamp = int(time.time() * 1000)
            
            params = {
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'type': 'MARKET',
                'quantity': '0.0001',
                'timestamp': timestamp
            }
            
            # توليد التوقيع
            query_string = urlencode(sorted(params.items()))
            signature = hmac.new(
                'cd479996b38a4944933bbe79015ffa09'.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            params['signature'] = signature
            
            headers = {
                'X-MEXC-APIKEY': 'mx0vglb3kLs2Rbe8pG',
                'Content-Type': 'application/json'
            }
            
            print(f"URL: {url}")
            print(f"Params: {params}")
            print(f"Headers: {headers}")
            
            response = requests.post(url, params=params, headers=headers, timeout=15)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"خطأ في الطلب المباشر: {e}")
    else:
        print("نجح وضع الأمر!")

if __name__ == "__main__":
    test_mexc_debug()
