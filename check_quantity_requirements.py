#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص متطلبات الكمية في MEXC
"""

import os
import sys
from dotenv import load_dotenv

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from mexc_trading_bot import MEXCTradingBot

def check_quantity_requirements():
    """فحص متطلبات الكمية في MEXC"""
    
    # مفاتيح API الحقيقية
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print("=== فحص متطلبات الكمية في MEXC ===")
    
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
            print(f"المعلومات الكاملة: {test_symbol}")
            
            # فحص filters
            if 'filters' in test_symbol:
                print(f"\nFilters: {test_symbol['filters']}")
                
                # البحث عن LOT_SIZE filter
                for filter_item in test_symbol['filters']:
                    if filter_item.get('filterType') == 'LOT_SIZE':
                        print(f"LOT_SIZE Filter: {filter_item}")
                        min_qty = float(filter_item.get('minQty', 0))
                        max_qty = float(filter_item.get('maxQty', 0))
                        step_size = float(filter_item.get('stepSize', 0))
                        
                        print(f"الحد الأدنى للكمية: {min_qty}")
                        print(f"الحد الأقصى للكمية: {max_qty}")
                        print(f"حجم الخطوة: {step_size}")
                        
                        # اختبار كمية صحيحة
                        test_quantity = max(min_qty, 0.01)  # استخدام الحد الأدنى أو 0.01
                        print(f"\nاختبار كمية: {test_quantity}")
                        
                        # اختبار وضع أمر
                        result = bot.place_spot_order(
                            symbol=test_symbol['symbol'],
                            side='BUY',
                            quantity=test_quantity,
                            order_type='MARKET'
                        )
                        
                        print(f"نتيجة الأمر: {result}")
                        break
                else:
                    print("لم يتم العثور على LOT_SIZE filter")
            else:
                print("لم يتم العثور على filters")
        else:
            print("لم يتم العثور على رموز BTC مدعومة")
    else:
        print("فشل في جلب معلومات الرموز")

if __name__ == "__main__":
    check_quantity_requirements()
