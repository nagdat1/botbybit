#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة التوقيع في MEXC
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

def test_mexc_connection():
    """اختبار الاتصال بـ MEXC"""
    print("=" * 60)
    print("اختبار إصلاح MEXC")
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
        if bot.test_connection():
            print("الاتصال ناجح!")
            
            # اختبار الحصول على الرصيد
            print("\nاختبار الرصيد...")
            balance = bot.get_account_balance()
            if balance:
                print("تم الحصول على الرصيد بنجاح")
                print(f"يمكن التداول: {balance.get('can_trade', False)}")
                
                # عرض بعض الأرصدة
                if 'balances' in balance:
                    count = 0
                    print("\nالأرصدة المتاحة:")
                    for asset, info in balance['balances'].items():
                        if info['total'] > 0 and count < 5:
                            print(f"   {asset}: {info['total']:.8f}")
                            count += 1
            else:
                print("فشل الحصول على الرصيد")
                return False
            
            # اختبار الحصول على السعر
            print("\nاختبار السعر...")
            price = bot.get_ticker_price('BTCUSDT')
            if price:
                print(f"سعر BTC/USDT: ${price:,.2f}")
            else:
                print("فشل الحصول على السعر")
                return False
            
            # اختبار معلومات الرمز
            print("\nاختبار معلومات الرمز...")
            symbol_info = bot.get_symbol_info('BTCUSDT')
            if symbol_info:
                print(f"معلومات BTCUSDT:")
                print(f"   التداول الفوري مسموح: {symbol_info['is_spot_trading_allowed']}")
                print(f"   الحالة: {symbol_info['status']}")
            else:
                print("فشل الحصول على معلومات الرمز")
                return False
            
            print("\n" + "=" * 60)
            print("جميع الاختبارات نجحت!")
            print("إصلاح MEXC يعمل بشكل صحيح")
            print("=" * 60)
            return True
            
        else:
            print("فشل الاتصال!")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signature_generation():
    """اختبار توليد التوقيع"""
    print("\nاختبار توليد التوقيع...")
    
    try:
        from mexc_trading_bot import MEXCTradingBot
        
        # إنشاء مثيل للاختبار
        bot = MEXCTradingBot("test_key", "test_secret")
        
        # اختبار التوقيع
        test_params = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': '0.001',
            'timestamp': 1640995200000
        }
        
        signature = bot._generate_signature(test_params)
        print(f"التوقيع المُولد: {signature}")
        
        # التحقق من أن التوقيع ليس فارغاً
        if signature and len(signature) == 64:  # SHA256 hex length
            print("التوقيع صحيح الطول")
            return True
        else:
            print("التوقيع غير صحيح")
            return False
            
    except Exception as e:
        print(f"خطأ في اختبار التوقيع: {e}")
        return False

if __name__ == "__main__":
    print("بدء اختبار إصلاح MEXC...")
    
    # اختبار توليد التوقيع أولاً
    signature_test = test_signature_generation()
    
    # اختبار الاتصال إذا كان التوقيع صحيحاً
    if signature_test:
        connection_test = test_mexc_connection()
        
        if connection_test:
            print("\nجميع الاختبارات نجحت!")
            print("إصلاح MEXC مكتمل ويعمل بشكل صحيح")
        else:
            print("\nفشل اختبار الاتصال")
    else:
        print("\nفشل اختبار التوقيع")
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)
