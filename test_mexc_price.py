#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار جلب السعر من MEXC
"""

import logging
import os
from dotenv import load_dotenv
from mexc_trading_bot import create_mexc_bot

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_mexc_price_fetching():
    """اختبار جلب السعر من MEXC"""
    print("=" * 60)
    print("اختبار جلب السعر من MEXC")
    print("=" * 60)
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    api_key = os.getenv('MEXC_API_KEY', '')
    api_secret = os.getenv('MEXC_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("يرجى تعيين MEXC_API_KEY و MEXC_API_SECRET في ملف .env")
        return False
    
    try:
        # إنشاء البوت
        print("\nإنشاء بوت MEXC...")
        bot = create_mexc_bot(api_key, api_secret)
        
        # اختبار الاتصال
        print("\nاختبار الاتصال...")
        if not bot.test_connection():
            print("فشل الاتصال!")
            return False
        
        print("الاتصال ناجح!")
        
        # اختبار جلب السعر
        print("\nاختبار جلب السعر...")
        symbols_to_test = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in symbols_to_test:
            print(f"\nجلب السعر لـ {symbol}...")
            price = bot.get_ticker_price(symbol)
            
            if price:
                print(f" سعر {symbol}: ${price:,.2f}")
            else:
                print(f" فشل جلب السعر لـ {symbol}")
                return False
        
        # اختبار معلومات الرمز
        print("\nاختبار معلومات الرمز...")
        symbol_info = bot.get_symbol_info('BTCUSDT')
        if symbol_info:
            print(f" معلومات BTCUSDT:")
            print(f"   التداول الفوري مسموح: {symbol_info['is_spot_trading_allowed']}")
            print(f"   الحالة: {symbol_info['status']}")
        else:
            print(" فشل الحصول على معلومات الرمز")
            return False
        
        print("\n" + "=" * 60)
        print("جميع اختبارات جلب السعر نجحت!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_account_price_fetching():
    """اختبار جلب السعر عبر RealAccount"""
    print("\n" + "=" * 60)
    print("اختبار جلب السعر عبر RealAccount")
    print("=" * 60)
    
    try:
        from real_account_manager import MEXCRealAccount
        
        # تحميل متغيرات البيئة
        load_dotenv()
        
        api_key = os.getenv('MEXC_API_KEY', '')
        api_secret = os.getenv('MEXC_API_SECRET', '')
        
        if not api_key or not api_secret:
            print("يرجى تعيين MEXC_API_KEY و MEXC_API_SECRET في ملف .env")
            return False
        
        # إنشاء حساب حقيقي
        print("\nإنشاء MEXCRealAccount...")
        account = MEXCRealAccount(api_key, api_secret)
        
        # اختبار جلب السعر
        print("\nاختبار جلب السعر عبر RealAccount...")
        ticker_result = account.get_ticker('spot', 'BTCUSDT')
        
        if ticker_result and 'lastPrice' in ticker_result:
            price = float(ticker_result['lastPrice'])
            print(f" السعر عبر RealAccount: ${price:,.2f}")
            return True
        else:
            print(f" فشل جلب السعر عبر RealAccount: {ticker_result}")
            return False
        
    except Exception as e:
        print(f"خطأ في اختبار RealAccount: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("بدء اختبار جلب السعر من MEXC...")
    
    # اختبار مباشر
    direct_test = test_mexc_price_fetching()
    
    # اختبار عبر RealAccount
    if direct_test:
        real_account_test = test_real_account_price_fetching()
        
        if real_account_test:
            print("\nجميع الاختبارات نجحت!")
            print("جلب السعر من MEXC يعمل بشكل صحيح")
        else:
            print("\nفشل اختبار RealAccount")
    else:
        print("\nفشل الاختبار المباشر")
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)
