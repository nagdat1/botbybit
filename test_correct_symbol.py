#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار رمز صحيح في MEXC
"""

import os
import sys
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def test_correct_symbol():
    """اختبار رمز صحيح في MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== اختبار رمز صحيح في MEXC ===")
    
    # إنشاء البوت
    bot = MEXCTradingBot(api_key, api_secret)
    
    # الحصول على جميع الرموز
    exchange_info = bot._make_request('GET', '/api/v3/exchangeInfo', signed=False)
    
    if exchange_info and 'symbols' in exchange_info:
        symbols = exchange_info['symbols']
        
        # البحث عن رموز BTC مع status = 1
        btc_symbols = [s for s in symbols if 'BTC' in s.get('symbol', '') and s.get('status') == '1']
        print(f"رموز BTC مدعومة: {len(btc_symbols)}")
        
        if btc_symbols:
            # اختبار أول رمز BTC
            test_symbol = btc_symbols[0]['symbol']
            print(f"\nاختبار رمز: {test_symbol}")
            
            # اختبار معلومات الرمز
            symbol_info = bot.get_symbol_info(test_symbol)
            print(f"معلومات الرمز: {symbol_info}")
            
            if symbol_info and symbol_info.get('is_spot_trading_allowed'):
                print(f"الرمز {test_symbol} مدعوم للتداول الفوري!")
                
                # اختبار وضع أمر صغير
                print(f"\nاختبار وضع أمر: BUY 0.0001 {test_symbol}")
                result = bot.place_spot_order(
                    symbol=test_symbol,
                    side='BUY',
                    quantity=0.0001,
                    order_type='MARKET'
                )
                
                print(f"نتيجة الأمر: {result}")
            else:
                print(f"الرمز {test_symbol} غير مدعوم للتداول الفوري")
                
                # جرب رمز آخر
                if len(btc_symbols) > 1:
                    test_symbol2 = btc_symbols[1]['symbol']
                    print(f"\nاختبار رمز آخر: {test_symbol2}")
                    
                    symbol_info2 = bot.get_symbol_info(test_symbol2)
                    print(f"معلومات الرمز: {symbol_info2}")
                    
                    if symbol_info2 and symbol_info2.get('is_spot_trading_allowed'):
                        print(f"الرمز {test_symbol2} مدعوم للتداول الفوري!")
                        
                        # اختبار وضع أمر صغير
                        print(f"\nاختبار وضع أمر: BUY 0.0001 {test_symbol2}")
                        result2 = bot.place_spot_order(
                            symbol=test_symbol2,
                            side='BUY',
                            quantity=0.0001,
                            order_type='MARKET'
                        )
                        
                        print(f"نتيجة الأمر: {result2}")
        else:
            print("لم يتم العثور على رموز BTC مدعومة")
    else:
        print("فشل في جلب معلومات الرموز")

if __name__ == "__main__":
    test_correct_symbol()
