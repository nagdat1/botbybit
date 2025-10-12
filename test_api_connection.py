#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار للتحقق من اتصال API
يمكن استخدامه لاختبار Bybit و MEXC API بشكل مستقل
"""

import sys
import os

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bybit_trading_bot import check_api_connection, BybitAPI, MEXCAPI
import logging

# إعداد logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_bybit_api(api_key: str, api_secret: str):
    """اختبار Bybit API"""
    print("\n" + "="*60)
    print("🟦 اختبار Bybit API")
    print("="*60)
    
    try:
        result = check_api_connection(api_key, api_secret, 'bybit')
        
        if result:
            print("\n✅ نجح الاختبار!")
            print("🟢 Bybit API يعمل بشكل صحيح")
            
            # محاولة جلب معلومات الحساب
            api = BybitAPI(api_key, api_secret)
            balance = api.get_account_balance()
            
            if balance.get('retCode') == 0:
                print("\n📊 معلومات الحساب:")
                print(f"   الرصيد: {balance}")
        else:
            print("\n❌ فشل الاختبار!")
            print("🔴 Bybit API غير صحيح أو هناك مشكلة")
            
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        print(traceback.format_exc())

def test_mexc_api(api_key: str, api_secret: str):
    """اختبار MEXC API"""
    print("\n" + "="*60)
    print("🟩 اختبار MEXC API")
    print("="*60)
    
    try:
        result = check_api_connection(api_key, api_secret, 'mexc')
        
        if result:
            print("\n✅ نجح الاختبار!")
            print("🟢 MEXC API يعمل بشكل صحيح")
            
            # محاولة جلب معلومات الحساب
            api = MEXCAPI(api_key, api_secret)
            test_result = api.test_connection()
            
            print("\n📊 نتيجة الاختبار السريع:")
            print(f"   {test_result}")
        else:
            print("\n❌ فشل الاختبار!")
            print("🔴 MEXC API غير صحيح أو هناك مشكلة")
            
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        print(traceback.format_exc())

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🧪 اختبار اتصال API للمنصات")
    print("="*60)
    
    print("\nاختر المنصة:")
    print("1. Bybit")
    print("2. MEXC")
    print("3. اختبار كلاهما")
    
    choice = input("\nاختيارك (1/2/3): ").strip()
    
    if choice == "1":
        print("\n📝 أدخل بيانات Bybit API:")
        api_key = input("API Key: ").strip()
        api_secret = input("API Secret: ").strip()
        test_bybit_api(api_key, api_secret)
        
    elif choice == "2":
        print("\n📝 أدخل بيانات MEXC API:")
        api_key = input("API Key: ").strip()
        api_secret = input("API Secret: ").strip()
        test_mexc_api(api_key, api_secret)
        
    elif choice == "3":
        print("\n📝 أدخل بيانات Bybit API:")
        bybit_key = input("Bybit API Key: ").strip()
        bybit_secret = input("Bybit API Secret: ").strip()
        
        print("\n📝 أدخل بيانات MEXC API:")
        mexc_key = input("MEXC API Key: ").strip()
        mexc_secret = input("MEXC API Secret: ").strip()
        
        test_bybit_api(bybit_key, bybit_secret)
        test_mexc_api(mexc_key, mexc_secret)
    else:
        print("\n❌ اختيار غير صحيح!")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        print(traceback.format_exc())

