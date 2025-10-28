#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص الرموز المدعومة في MEXC
"""

import os
import sys
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def check_supported_symbols():
    """فحص الرموز المدعومة في MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== فحص الرموز المدعومة في MEXC ===")
    
    # إنشاء البوت
    bot = MEXCTradingBot(api_key, api_secret)
    
    # الحصول على جميع الرموز
    print("\nجلب جميع الرموز...")
    symbols = bot._make_request('GET', '/api/v3/exchangeInfo', signed=False)
    
    if symbols and 'symbols' in symbols:
        print(f"تم العثور على {len(symbols['symbols'])} رمز")
        
        # البحث عن رموز BTC
        btc_symbols = []
        for symbol in symbols['symbols']:
            if 'BTC' in symbol['symbol'] and symbol['status'] == 'ENABLED':
                btc_symbols.append(symbol)
        
        print(f"\nرموز BTC المدعومة ({len(btc_symbols)}):")
        for symbol in btc_symbols[:10]:  # أول 10 رموز
            print(f"  {symbol['symbol']} - {symbol['status']}")
        
        # البحث عن رموز مدعومة للتداول الفوري
        spot_symbols = []
        for symbol in symbols['symbols']:
            if symbol['status'] == 'ENABLED' and 'SPOT' in symbol.get('permissions', []):
                spot_symbols.append(symbol)
        
        print(f"\nرموز SPOT المدعومة ({len(spot_symbols)}):")
        for symbol in spot_symbols[:10]:  # أول 10 رموز
            print(f"  {symbol['symbol']} - {symbol['status']}")
        
        # اختبار رمز مختلف
        if spot_symbols:
            test_symbol = spot_symbols[0]['symbol']
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
    else:
        print("فشل في جلب الرموز")

if __name__ == "__main__":
    check_supported_symbols()
