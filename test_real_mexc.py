#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع مع مفاتيح API حقيقية
"""

import logging
from mexc_trading_bot import create_mexc_bot

# إعداد التسجيل المفصل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_with_real_keys():
    """اختبار مع مفاتيح API حقيقية"""
    print("=" * 60)
    print("اختبار مع مفاتيح API حقيقية")
    print("=" * 60)
    
    # المفاتيح الحقيقية
    api_key = "mx0vglBqh6abc123xyz456"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"API Secret: {'*' * len(api_secret)}")
    
    try:
        # إنشاء البوت
        print("\nإنشاء بوت MEXC...")
        bot = create_mexc_bot(api_key, api_secret)
        
        # اختبار الاتصال
        print("\nاختبار الاتصال...")
        if bot.test_connection():
            print(" الاتصال ناجح!")
        else:
            print(" فشل الاتصال!")
            return False
        
        # اختبار جلب السعر
        print("\nاختبار جلب السعر...")
        price = bot.get_ticker_price('BTCUSDT')
        if price:
            print(f" السعر الحالي: ${price:,.2f}")
        else:
            print(" فشل جلب السعر!")
            return False
        
        # اختبار معلومات الرمز
        print("\nاختبار معلومات الرمز...")
        symbol_info = bot.get_symbol_info('BTCUSDT')
        if symbol_info:
            print(f" معلومات الرمز:")
            print(f"   التداول الفوري مسموح: {symbol_info['is_spot_trading_allowed']}")
            print(f"   الحالة: {symbol_info['status']}")
        else:
            print(" فشل الحصول على معلومات الرمز!")
            return False
        
        # اختبار الرصيد
        print("\nاختبار الرصيد...")
        balance = bot.get_account_balance()
        if balance:
            print(f" الرصيد:")
            print(f"   يمكن التداول: {balance.get('can_trade', False)}")
            print(f"   يمكن السحب: {balance.get('can_withdraw', False)}")
            print(f"   يمكن الإيداع: {balance.get('can_deposit', False)}")
            
            # عرض بعض الأرصدة
            if 'balances' in balance:
                count = 0
                print(f"\nالأرصدة المتاحة:")
                for asset, info in balance['balances'].items():
                    if info['total'] > 0 and count < 5:
                        print(f"   {asset}: {info['total']:.8f}")
                        count += 1
        else:
            print(" فشل الحصول على الرصيد!")
            return False
        
        print("\n" + "=" * 60)
        print(" جميع الاختبارات نجحت!")
        print(" المشروع يعمل بشكل صحيح مع مفاتيح API الحقيقية")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f" خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("بدء الاختبار مع مفاتيح API حقيقية...")
    
    success = test_with_real_keys()
    
    if success:
        print("\n النتيجة: المشروع يعمل بشكل مثالي!")
        print(" يمكنك الآن استخدام MEXC للتداول")
    else:
        print("\n النتيجة: هناك مشاكل تحتاج إصلاح")
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)
