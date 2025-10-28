#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح نهائي لمشكلة Bybit API في المشروع
"""

import sys
import os
import asyncio
import logging

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def final_bybit_fix():
    """إصلاح نهائي لمشكلة Bybit API"""
    
    print("=== إصلاح نهائي لمشكلة Bybit API ===")
    print()
    
    print("المشكلة: خطأ 401 Unauthorized")
    print("السبب: مشكلة في المصادقة")
    print()
    
    print("الحلول المحتملة:")
    print("1. API Key أو Secret غير صحيح")
    print("2. صلاحيات API Key غير كافية")
    print("3. قيود IP")
    print("4. مشكلة في التوقيع")
    print("5. مشكلة في الوقت")
    print()
    
    # اختبار مع مفاتيح جديدة
    print("أدخل API Key الجديد:")
    api_key = input("API Key: ").strip()
    
    print("أدخل API Secret الجديد:")
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("API Key أو Secret فارغ!")
        return False
    
    print()
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
    try:
        # إنشاء حساب حقيقي
        user_id = 999999
        print(f"إنشاء حساب حقيقي للمستخدم {user_id}")
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        
        # الحصول على الحساب
        account = real_account_manager.get_account(user_id)
        if not account:
            print("فشل في إنشاء الحساب الحقيقي")
            return False
        
        print("تم إنشاء الحساب الحقيقي بنجاح")
        print()
        
        # اختبار جلب الرصيد
        print("1. اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('UNIFIED')
        if balance:
            print(f"الرصيد: {balance}")
        else:
            print("فشل في جلب الرصيد")
            return False
        
        print()
        
        # اختبار جلب السعر
        print("2. اختبار جلب السعر...")
        ticker = account.get_ticker('linear', 'BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            price = float(ticker['lastPrice'])
            print(f"سعر BTCUSDT: ${price:,.2f}")
        else:
            print("فشل في جلب السعر")
            return False
        
        print()
        
        # اختبار وضع الرافعة المالية
        print("3. اختبار وضع الرافعة المالية (1x)...")
        leverage_result = account.set_leverage('linear', 'BTCUSDT', 1)
        if leverage_result:
            print("تم وضع الرافعة المالية بنجاح!")
        else:
            print("فشل في وضع الرافعة المالية")
            print("المشكلة: صلاحيات Position Management")
            return False
        
        print()
        
        # اختبار وضع أمر Futures (كمية صغيرة)
        print("4. اختبار وضع أمر Futures...")
        print(f"الكمية: 0.0001 BTC")
        print(f"السعر: ${price:,.2f}")
        print(f"الرافعة: 1x")
        print()
        
        # حساب الكمية
        qty = 0.0001  # كمية صغيرة جداً للاختبار
        
        # وضع أمر Buy
        result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=qty,
            leverage=1
        )
        
        if result and result.get('success'):
            print("تم وضع الأمر بنجاح!")
            print(f"Order ID: {result.get('order_id', 'N/A')}")
            print()
            print("الآن يجب أن ترى الصفقة في Bybit!")
            return True
        else:
            print("فشل في وضع الأمر")
            if result:
                print(f"الخطأ: {result.get('error', 'Unknown error')}")
                print(f"تفاصيل الخطأ: {result.get('error_details', 'No details')}")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

def create_api_key_guide():
    """دليل إنشاء API Key جديد"""
    
    print("=== دليل إنشاء API Key جديد ===")
    print()
    
    print("1. اذهب إلى Bybit.com")
    print("2. سجل دخول إلى حسابك")
    print("3. اذهب إلى Account → API Management")
    print("4. اضغط على Create New Key")
    print("5. اختر الصلاحيات التالية:")
    print("   - Read (مطلوب)")
    print("   - Trade (مطلوب)")
    print("   - Position Management (مطلوب)")
    print("   - Wallet Transfer (اختياري)")
    print("6. لا تضع قيود IP (اتركه فارغ)")
    print("7. اضغط على Create")
    print("8. انسخ API Key و API Secret")
    print()
    
    print("ملاحظات مهمة:")
    print("- تأكد من أن الصلاحيات مفعلة")
    print("- لا تضع قيود IP")
    print("- احفظ المفاتيح في مكان آمن")
    print()

if __name__ == "__main__":
    print("اختيار نوع الاختبار:")
    print("1. اختبار مع مفاتيح جديدة")
    print("2. دليل إنشاء API Key جديد")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = asyncio.run(final_bybit_fix())
    elif choice == "2":
        create_api_key_guide()
        success = True
    else:
        print("اختيار غير صحيح")
        sys.exit(1)
    
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل")
        sys.exit(1)
