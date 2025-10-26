#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مع أزواج أخرى للتأكد من مشكلة التعطيل
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mexc_trading_bot import create_mexc_bot

def test_other_pairs():
    """اختبار مع أزواج أخرى"""
    
    print("=" * 60)
    print("اختبار مع أزواج أخرى للتأكد من مشكلة التعطيل")
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
    
    # اختبار أزواج مختلفة
    test_pairs = ['ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
    
    for pair in test_pairs:
        print(f"\nاختبار زوج {pair}...")
        
        # اختبار جلب السعر
        price = bot.get_ticker_price(pair)
        print(f"السعر: {price}")
        
        if price:
            # اختبار وضع أمر صغير
            quantity = 0.001  # كمية صغيرة للاختبار
            result = bot.place_spot_order(pair, 'BUY', quantity, 'MARKET')
            print(f"نتيجة الأمر: {result}")
            
            if result is not None:
                print(f"نجح وضع الأمر لزوج {pair}!")
                break
            else:
                print(f"فشل وضع الأمر لزوج {pair}")
        else:
            print(f"فشل جلب السعر لزوج {pair}")

if __name__ == "__main__":
    test_other_pairs()
