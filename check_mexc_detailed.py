#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص مفصل لاستجابة MEXC
"""

import os
import sys
import json
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def check_mexc_response():
    """فحص مفصل لاستجابة MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== فحص مفصل لاستجابة MEXC ===")
    
    # إنشاء البوت
    bot = MEXCTradingBot(api_key, api_secret)
    
    # اختبار ping
    print("\n1. اختبار ping...")
    ping_result = bot._make_request('GET', '/api/v3/ping', signed=False)
    print(f"Ping: {ping_result}")
    
    # اختبار server time
    print("\n2. اختبار server time...")
    time_result = bot._make_request('GET', '/api/v3/time', signed=False)
    print(f"Server Time: {time_result}")
    
    # اختبار exchange info
    print("\n3. اختبار exchange info...")
    exchange_info = bot._make_request('GET', '/api/v3/exchangeInfo', signed=False)
    print(f"Exchange Info Type: {type(exchange_info)}")
    print(f"Exchange Info Keys: {list(exchange_info.keys()) if isinstance(exchange_info, dict) else 'Not a dict'}")
    
    if isinstance(exchange_info, dict) and 'symbols' in exchange_info:
        symbols = exchange_info['symbols']
        print(f"عدد الرموز: {len(symbols)}")
        
        # البحث عن رموز BTC
        btc_symbols = [s for s in symbols if 'BTC' in s.get('symbol', '')]
        print(f"رموز BTC: {len(btc_symbols)}")
        
        if btc_symbols:
            print("أول 5 رموز BTC:")
            for symbol in btc_symbols[:5]:
                print(f"  {symbol['symbol']} - {symbol.get('status', 'UNKNOWN')}")
        
        # البحث عن رموز مدعومة
        enabled_symbols = [s for s in symbols if s.get('status') == 'ENABLED']
        print(f"رموز مدعومة: {len(enabled_symbols)}")
        
        if enabled_symbols:
            print("أول 5 رموز مدعومة:")
            for symbol in enabled_symbols[:5]:
                print(f"  {symbol['symbol']} - {symbol.get('permissions', [])}")
    else:
        print("فشل في جلب معلومات الرموز")
        print(f"الاستجابة الكاملة: {exchange_info}")

if __name__ == "__main__":
    check_mexc_response()
