#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

async def test_fixed_signature():
    """اختبار التوقيع المصلح"""
    
    print("=== اختبار التوقيع المصلح ===")
    print()
    
    try:
        # المفاتيح الجديدة
        user_id = 999999
        api_key = "RKk6fTapgDqys6vt5S"
        api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
        
        print(f"API Key: {api_key}")
        print(f"API Secret: {api_secret[:10]}...")
        print()
        
        # إنشاء حساب حقيقي
        print("1. إنشاء حساب حقيقي...")
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("فشل في إنشاء الحساب")
            return False
        
        print("تم إنشاء الحساب بنجاح")
        print()
        
        # اختبار جلب الرصيد
        print("2. اختبار جلب الرصيد...")
        balance = account.get_wallet_balance('UNIFIED')
        if balance:
            print(f"الرصيد: {balance.get('totalEquity', 'N/A')} USDT")
            print("نجح")
        else:
            print("فشل في جلب الرصيد")
            return False
        
        print()
        
        # اختبار جلب السعر
        print("3. اختبار جلب السعر...")
        ticker = account.get_ticker('linear', 'BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            price = float(ticker['lastPrice'])
            print(f"سعر BTCUSDT: ${price:,.2f}")
            print("نجح")
        else:
            print("فشل في جلب السعر")
            return False
        
        print()
        
        # اختبار وضع الرافعة المالية (الاختبار المهم)
        print("4. اختبار وضع الرافعة المالية (2x)...")
        leverage_result = account.set_leverage('linear', 'BTCUSDT', 2)
        if leverage_result:
            print("تم وضع الرافعة المالية بنجاح!")
            print("نجح")
        else:
            print("فشل في وضع الرافعة المالية")
            print("قد يكون بسبب صلاحيات API Key")
            return False
        
        print()
        
        # اختبار وضع أمر Futures
        print("5. اختبار وضع أمر Futures (0.0001 BTC)...")
        result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.0001,
            leverage=2
        )
        
        if result and result.get('success'):
            print("تم وضع الأمر بنجاح!")
            print(f"Order ID: {result.get('order_id', 'N/A')}")
            print("نجح")
            print()
            print("=" * 50)
            print("جميع الاختبارات نجحت!")
            print("البوت جاهز للعمل!")
            print("=" * 50)
            return True
        else:
            print("فشل في وضع الأمر")
            if result:
                print(f"الخطأ: {result.get('error', 'Unknown')}")
                print(f"تفاصيل: {result.get('error_details', 'No details')}")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_signature())
    if success:
        print("الاختبار نجح!")
        sys.exit(0)
    else:
        print("الاختبار فشل!")
        sys.exit(1)
