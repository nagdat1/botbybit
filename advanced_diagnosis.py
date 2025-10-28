#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أداة تشخيص متقدمة لمشكلة Bybit API
"""

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
import json

def advanced_bybit_diagnosis():
    """تشخيص متقدم لمشكلة Bybit API"""
    
    # API keys المقدمة من المستخدم
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    base_url = "https://api.bybit.com"
    
    print("=== تشخيص متقدم لمشكلة Bybit API ===")
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
    
    # اختبار 1: فحص معلومات الحساب
    print("اختبار 1: فحص معلومات الحساب...")
    account_info = make_request('GET', '/v5/account/info')
    
    if account_info:
        print("نجح جلب معلومات الحساب!")
        print(f"معلومات الحساب: {account_info}")
    else:
        print("فشل جلب معلومات الحساب")
    
    print()
    
    # اختبار 2: فحص الرصيد
    print("اختبار 2: فحص الرصيد...")
    balance = make_request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
    
    if balance:
        print("نجح جلب الرصيد!")
        if 'list' in balance and balance['list']:
            account = balance['list'][0]
            print(f"الرصيد الإجمالي: {account.get('totalEquity', 0)}")
            print(f"الرصيد المتاح: {account.get('totalAvailableBalance', 0)}")
        else:
            print("لا توجد حسابات متاحة")
    else:
        print("فشل جلب الرصيد")
    
    print()
    
    # اختبار 3: فحص الصفقات المفتوحة
    print("اختبار 3: فحص الصفقات المفتوحة...")
    positions = make_request('GET', '/v5/position/list', {'category': 'linear'})
    
    if positions:
        print("نجح جلب الصفقات المفتوحة!")
        if 'list' in positions and positions['list']:
            print(f"عدد الصفقات المفتوحة: {len(positions['list'])}")
            for pos in positions['list']:
                print(f"  - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
        else:
            print("لا توجد صفقات مفتوحة")
    else:
        print("فشل جلب الصفقات المفتوحة")
    
    print()
    
    # اختبار 4: فحص الأوامر المفتوحة
    print("اختبار 4: فحص الأوامر المفتوحة...")
    orders = make_request('GET', '/v5/order/realtime', {'category': 'linear'})
    
    if orders:
        print("نجح جلب الأوامر المفتوحة!")
        if 'list' in orders and orders['list']:
            print(f"عدد الأوامر المفتوحة: {len(orders['list'])}")
            for order in orders['list']:
                print(f"  - {order.get('symbol')}: {order.get('side')} {order.get('qty')} - {order.get('orderStatus')}")
        else:
            print("لا توجد أوامر مفتوحة")
    else:
        print("فشل جلب الأوامر المفتوحة")
    
    print()
    
    # اختبار 5: فحص صلاحيات API
    print("اختبار 5: فحص صلاحيات API...")
    
    # اختبار وضع أمر صغير
    test_params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '0.0001'
    }
    
    order_result = make_request('POST', '/v5/order/create', test_params)
    
    if order_result:
        print("نجح وضع الأمر!")
        print(f"Order ID: {order_result.get('orderId')}")
    else:
        print("فشل وضع الأمر - هذا متوقع إذا لم تكن هناك صلاحيات")
    
    print()
    
    # اختبار 6: فحص إعدادات الحساب
    print("اختبار 6: فحص إعدادات الحساب...")
    settings = make_request('GET', '/v5/account/contracts', {'category': 'linear'})
    
    if settings:
        print("نجح جلب إعدادات الحساب!")
        print(f"إعدادات الحساب: {settings}")
    else:
        print("فشل جلب إعدادات الحساب")
    
    print()
    print("=== انتهى التشخيص ===")
    print()
    print("الخلاصة:")
    print("1. إذا فشلت جميع الطلبات الخاصة (account, balance, positions, orders):")
    print("   - API Key غير صحيح أو منتهي الصلاحية")
    print("   - API Key لا يحتوي على صلاحيات كافية")
    print()
    print("2. إذا نجحت الطلبات العامة (tickers) وفشلت الخاصة:")
    print("   - API Key صحيح لكن لا يحتوي على صلاحيات التداول")
    print("   - يجب إنشاء API Key جديد بصلاحيات كاملة")
    print()
    print("3. إذا نجحت بعض الطلبات وفشلت أخرى:")
    print("   - API Key صحيح لكن صلاحيات محدودة")
    print("   - يجب تحديث صلاحيات API Key")

if __name__ == "__main__":
    advanced_bybit_diagnosis()
