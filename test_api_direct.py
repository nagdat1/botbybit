#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مباشر لـ API Key مع صفقة حقيقية
"""

import sys
import os
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_api_key_directly():
    """اختبار مباشر لـ API Key مع صفقة حقيقية"""
    
    print("=== اختبار مباشر لـ API Key مع صفقة حقيقية ===")
    print()
    
    # API Key الجديد
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
    base_url = "https://api.bybit.com"
    
    def generate_signature(timestamp, recv_window, params_str):
        """توليد التوقيع"""
        sign_str = timestamp + api_key + recv_window + params_str
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def make_request(method, endpoint, params=None):
        """إرسال طلب إلى API"""
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        if params is None:
            params = {}
        
        params_str = urlencode(params) if params else ""
        
        signature = generate_signature(timestamp, recv_window, params_str)
        
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = base_url + endpoint
        
        if method == 'GET':
            if params_str:
                url += '?' + params_str
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=params)
        
        print(f"Request: {method} {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        return response.json() if response.text else None
    
    try:
        # اختبار 1: معلومات الحساب
        print("اختبار 1: معلومات الحساب...")
        account_info = make_request('GET', '/v5/account/wallet-balance', {
            'accountType': 'UNIFIED'
        })
        
        if account_info and account_info.get('retCode') == 0:
            print("نجح اختبار معلومات الحساب")
            balance = account_info.get('result', {}).get('list', [{}])[0]
            print(f"الرصيد: {balance}")
        else:
            print(f"فشل اختبار معلومات الحساب: {account_info}")
            return False
        print()
        
        # اختبار 2: السعر الحالي
        print("اختبار 2: السعر الحالي...")
        ticker_info = make_request('GET', '/v5/market/tickers', {
            'category': 'spot',
            'symbol': 'BTCUSDT'
        })
        
        if ticker_info and ticker_info.get('retCode') == 0:
            print("نجح اختبار السعر")
            price_data = ticker_info.get('result', {}).get('list', [{}])[0]
            price = float(price_data.get('lastPrice', 0))
            print(f"السعر الحالي: ${price}")
        else:
            print(f"فشل اختبار السعر: {ticker_info}")
            return False
        print()
        
        # اختبار 3: صفقة حقيقية صغيرة
        print("اختبار 3: صفقة حقيقية صغيرة...")
        
        # كمية صغيرة جداً ($5)
        test_amount = 5.0
        qty = round(test_amount / price, 6)
        
        print(f"المبلغ: ${test_amount}")
        print(f"السعر: ${price}")
        print(f"الكمية: {qty} BTC")
        print()
        
        print("تحذير: هذا سيضع صفقة حقيقية!")
        print("هل تريد المتابعة؟ (اكتب 'نعم' للمتابعة)")
        
        # يمكنك تغيير هذا إلى input() للاختبار اليدوي
        confirm = "نعم"  # أو input() للاختبار اليدوي
        
        if confirm == "نعم":
            print("وضع صفقة حقيقية...")
            
            order_params = {
                'category': 'spot',
                'symbol': 'BTCUSDT',
                'side': 'Buy',
                'orderType': 'Market',
                'qty': str(qty)
            }
            
            order_result = make_request('POST', '/v5/order/create', order_params)
            
            if order_result and order_result.get('retCode') == 0:
                print("نجح وضع الصفقة!")
                order_data = order_result.get('result', {})
                print(f"Order ID: {order_data.get('orderId')}")
                print(f"Order Link ID: {order_data.get('orderLinkId')}")
                return True
            else:
                print(f"فشل وضع الصفقة: {order_result}")
                
                # تحليل الخطأ
                ret_code = order_result.get('retCode') if order_result else 'Unknown'
                ret_msg = order_result.get('retMsg') if order_result else 'Unknown'
                
                print(f"كود الخطأ: {ret_code}")
                print(f"رسالة الخطأ: {ret_msg}")
                
                if ret_code == 10005:
                    print("السبب: API Key لا يملك صلاحية وضع الأوامر")
                    print("الحل: تأكد من تفعيل صلاحية 'Spot Trading - Trade'")
                elif ret_code == 10003:
                    print("السبب: API Key غير صحيح أو منتهي الصلاحية")
                elif ret_code == 10001:
                    print("السبب: معاملات غير صحيحة")
                
                return False
        else:
            print("تم إلغاء الاختبار")
            return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_key_directly()
    if not success:
        sys.exit(1)
