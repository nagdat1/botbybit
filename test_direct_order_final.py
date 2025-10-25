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

async def test_direct_order():
    """اختبار وضع أمر مباشر"""
    
    print("=== اختبار وضع أمر مباشر ===")
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
        
        # جلب السعر
        print("2. جلب السعر...")
        ticker = account.get_ticker('linear', 'BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            price = float(ticker['lastPrice'])
            print(f"سعر BTCUSDT: ${price:,.2f}")
        else:
            print("فشل في جلب السعر")
            return False
        
        print()
        
        # وضع أمر Futures مباشرة (بدون set leverage)
        print("3. وضع أمر Futures (0.001 BTC)...")
        print(f"الكمية: 0.001 BTC")
        print(f"السعر: ${price:,.2f}")
        print(f"القيمة: ${price * 0.001:,.2f}")
        print()
        
        result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001,
            leverage=2
        )
        
        if result and result.get('success'):
            print("=" * 50)
            print("نجح وضع الأمر!")
            print("=" * 50)
            print(f"Order ID: {result.get('order_id', 'N/A')}")
            print()
            print("افتح Bybit الآن وشاهد الصفقة!")
            return True
        else:
            print("=" * 50)
            print("فشل في وضع الأمر")
            print("=" * 50)
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
    success = asyncio.run(test_direct_order())
    if success:
        print("الاختبار نجح! الصفقة تم فتحها بنجاح!")
        sys.exit(0)
    else:
        print("الاختبار فشل!")
        sys.exit(1)
