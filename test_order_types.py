#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار أنواع أوامر مختلفة في MEXC
"""

import os
import sys
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def test_different_order_types():
    """اختبار أنواع أوامر مختلفة في MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== اختبار أنواع أوامر مختلفة في MEXC ===")
    
    # إنشاء البوت
    bot = MEXCTradingBot(api_key, api_secret)
    
    # الحصول على جميع الرموز
    exchange_info = bot._make_request('GET', '/api/v3/exchangeInfo', signed=False)
    
    if exchange_info and 'symbols' in exchange_info:
        symbols = exchange_info['symbols']
        
        # البحث عن رموز BTC مع status = 1
        btc_symbols = [s for s in symbols if 'BTC' in s.get('symbol', '') and s.get('status') == '1']
        
        if btc_symbols:
            # فحص أول رمز BTC
            test_symbol = btc_symbols[0]
            print(f"فحص رمز: {test_symbol['symbol']}")
            
            # فحص أنواع الأوامر المدعومة
            order_types = test_symbol.get('orderTypes', [])
            print(f"أنواع الأوامر المدعومة: {order_types}")
            
            # الحصول على السعر الحالي
            current_price = bot.get_ticker_price(test_symbol['symbol'])
            print(f"السعر الحالي: {current_price}")
            
            if current_price:
                # اختبار أمر LIMIT
                if 'LIMIT' in order_types:
                    print(f"\nاختبار أمر LIMIT: BUY 0.01 {test_symbol['symbol']} بسعر {current_price * 0.99}")
                    
                    result = bot.place_spot_order(
                        symbol=test_symbol['symbol'],
                        side='BUY',
                        quantity=0.01,
                        order_type='LIMIT',
                        price=current_price * 0.99  # سعر أقل من السعر الحالي
                    )
                    
                    print(f"نتيجة أمر LIMIT: {result}")
                
                # اختبار أمر LIMIT_MAKER
                if 'LIMIT_MAKER' in order_types:
                    print(f"\nاختبار أمر LIMIT_MAKER: BUY 0.01 {test_symbol['symbol']} بسعر {current_price * 0.98}")
                    
                    result2 = bot.place_spot_order(
                        symbol=test_symbol['symbol'],
                        side='BUY',
                        quantity=0.01,
                        order_type='LIMIT_MAKER',
                        price=current_price * 0.98  # سعر أقل من السعر الحالي
                    )
                    
                    print(f"نتيجة أمر LIMIT_MAKER: {result2}")
            else:
                print("فشل في الحصول على السعر الحالي")
        else:
            print("لم يتم العثور على رموز BTC مدعومة")
    else:
        print("فشل في جلب معلومات الرموز")

if __name__ == "__main__":
    test_different_order_types()
