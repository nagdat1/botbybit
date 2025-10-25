#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار API keys لـ Bybit للتأكد من عملها
"""

import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def test_bybit_api():
    """اختبار API keys لـ Bybit"""
    
    # قراءة API keys من متغيرات البيئة
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    print("=== اختبار API Keys لـ Bybit ===")
    print()
    
    if not api_key or not api_secret:
        print("خطأ: لم يتم العثور على API keys في ملف .env")
        print("تأكد من وجود:")
        print("BYBIT_API_KEY=your_api_key")
        print("BYBIT_API_SECRET=your_api_secret")
        return False
    
    print(f"API Key موجود: {api_key[:10]}...")
    print(f"API Secret موجود: {api_secret[:10]}...")
    print()
    
    try:
        # استيراد BybitRealAccount
        from real_account_manager import BybitRealAccount
        
        # إنشاء حساب تجريبي
        account = BybitRealAccount(api_key, api_secret)
        
        print("تم إنشاء BybitRealAccount بنجاح")
        print()
        
        # اختبار جلب الرصيد
        print("اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('unified')
        
        if balance:
            print("نجح جلب الرصيد!")
            print(f"الرصيد الإجمالي: {balance.get('total_equity', 0)}")
            print(f"الرصيد المتاح: {balance.get('available_balance', 0)}")
        else:
            print("فشل جلب الرصيد - تحقق من API keys")
            return False
        
        print()
        
        # اختبار جلب السعر
        print("اختبار جلب السعر...")
        price = account.get_ticker_price('BTCUSDT', 'spot')
        
        if price:
            print(f"نجح جلب السعر! سعر BTCUSDT: ${price}")
        else:
            print("فشل جلب السعر")
            return False
        
        print()
        print("جميع الاختبارات نجحت! API keys تعمل بشكل صحيح.")
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    success = test_bybit_api()
    if not success:
        sys.exit(1)
