#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مباشر لـ API keys بدون استخدام النظام المدمج
"""

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_bybit_api_direct():
    """اختبار مباشر لـ Bybit API"""
    
    # API keys المقدمة من المستخدم
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    base_url = "https://api.bybit.com"
    
    print("=== اختبار مباشر لـ Bybit API ===")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
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
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # بناء query string
        params_str = urlencode(sorted(params.items())) if params else ""
        
        # توليد التوقيع
        signature = generate_signature(timestamp, recv_window, params_str)
        
        # Headers
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{base_url}{endpoint}"
        if params_str:
            url += f"?{params_str}"
        
        print(f"Request: {method} {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                return None
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response JSON: {result}")
                
                if result.get('retCode') == 0:
                    print("نجح الطلب!")
                    return result.get('result')
                else:
                    print(f"خطأ API - retCode: {result.get('retCode')}, retMsg: {result.get('retMsg')}")
                    return None
            else:
                print(f"خطأ HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"خطأ في الطلب: {e}")
            return None
    
    # اختبار 1: جلب معلومات الحساب
    print("اختبار 1: جلب معلومات الحساب...")
    result = make_request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
    
    if result:
        print("نجح جلب معلومات الحساب!")
        if 'list' in result and result['list']:
            account = result['list'][0]
            print(f"الرصيد الإجمالي: {account.get('totalEquity', 0)}")
            print(f"الرصيد المتاح: {account.get('totalAvailableBalance', 0)}")
        else:
            print("لا توجد حسابات متاحة")
    else:
        print("فشل جلب معلومات الحساب")
    
    print()
    
    # اختبار 2: جلب السعر
    print("اختبار 2: جلب السعر...")
    result = make_request('GET', '/v5/market/tickers', {'category': 'spot', 'symbol': 'BTCUSDT'})
    
    if result:
        print("نجح جلب السعر!")
        if 'list' in result and result['list']:
            ticker = result['list'][0]
            print(f"سعر BTCUSDT: ${ticker.get('lastPrice', 0)}")
        else:
            print("لا توجد بيانات سعر متاحة")
    else:
        print("فشل جلب السعر")
    
    print()
    
    # اختبار 3: جلب الصفقات المفتوحة
    print("اختبار 3: جلب الصفقات المفتوحة...")
    result = make_request('GET', '/v5/position/list', {'category': 'linear'})
    
    if result:
        print("نجح جلب الصفقات المفتوحة!")
        if 'list' in result and result['list']:
            print(f"عدد الصفقات المفتوحة: {len(result['list'])}")
            for pos in result['list']:
                print(f"  - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
        else:
            print("لا توجد صفقات مفتوحة")
    else:
        print("فشل جلب الصفقات المفتوحة")

if __name__ == "__main__":
    test_bybit_api_direct()
