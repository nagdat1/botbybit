#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مفصل لمشكلة وضع الأوامر في MEXC
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mexc_trading_bot import create_mexc_bot
import logging

# إعداد التسجيل المفصل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_order_placement():
    """اختبار وضع الأمر مع تفاصيل مفصلة"""
    
    print("=" * 60)
    print("اختبار مفصل لوضع الأوامر في MEXC")
    print("=" * 60)
    
    # إنشاء البوت
    bot = create_mexc_bot('mx0vglb3kLs2Rbe8pG', 'cd479996b38a4944933bbe79015ffa09')
    
    # اختبار الاتصال
    print("\n1. اختبار الاتصال...")
    connection_result = bot.test_connection()
    print(f"الاتصال: {'نجح' if connection_result else 'فشل'}")
    
    # اختبار جلب السعر
    print("\n2. اختبار جلب السعر...")
    price = bot.get_ticker_price('BTCUSDT')
    print(f"سعر BTCUSDT: {price}")
    
    # اختبار جلب الرصيد
    print("\n3. اختبار جلب الرصيد...")
    balance = bot.get_account_balance()
    print(f"الرصيد: {balance}")
    
    if not price or not balance:
        print(" فشل في جلب البيانات الأساسية")
        return
    
    # حساب الكمية (60 USDT)
    trade_amount = 60.0
    quantity = trade_amount / price
    print(f"\n4. حساب الكمية:")
    print(f"   المبلغ المطلوب: {trade_amount} USDT")
    print(f"   السعر الحالي: {price}")
    print(f"   الكمية المحسوبة: {quantity}")
    
    # اختبار معلومات الرمز
    print("\n5. اختبار معلومات الرمز...")
    symbol_info = bot.get_symbol_info('BTCUSDT')
    if symbol_info:
        print(f"   baseSizePrecision: {symbol_info.get('baseSizePrecision')}")
        print(f"   baseAssetPrecision: {symbol_info.get('baseAssetPrecision')}")
        print(f"   isSpotTradingAllowed: {symbol_info.get('isSpotTradingAllowed')}")
    else:
        print("    فشل في جلب معلومات الرمز")
        return
    
    # اختبار تنسيق الكمية
    print("\n6. اختبار تنسيق الكمية...")
    if symbol_info:
        formatted_quantity = bot._format_quantity(quantity, symbol_info)
        print(f"   الكمية المنسقة: {formatted_quantity}")
    
    # اختبار وضع الأمر
    print("\n7. اختبار وضع الأمر...")
    print(f"   محاولة وضع أمر: BUY {quantity} BTCUSDT")
    
    try:
        result = bot.place_spot_order('BTCUSDT', 'BUY', quantity, 'MARKET')
        print(f"   النتيجة: {result}")
        
        if result is None:
            print("    فشل وضع الأمر - النتيجة None")
        else:
            print("    نجح وضع الأمر!")
            
    except Exception as e:
        print(f"    خطأ في وضع الأمر: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)

if __name__ == "__main__":
    test_order_placement()
