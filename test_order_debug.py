#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار عميق لفحص مشكلة عدم ظهور الصفقات في المنصة
"""

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_bybit_order_placement():
    """اختبار وضع أمر حقيقي على Bybit"""
    
    # API keys المقدمة من المستخدم
    api_key = "mx0vglb3kLs2Rbe8pG"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    base_url = "https://api.bybit.com"
    
    print("=== اختبار وضع أمر حقيقي على Bybit ===")
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
    
    # اختبار 1: جلب السعر أولاً
    print("اختبار 1: جلب السعر...")
    price_result = make_request('GET', '/v5/market/tickers', {'category': 'spot', 'symbol': 'BTCUSDT'})
    
    if not price_result:
        print("فشل جلب السعر - لا يمكن المتابعة")
        return
    
    current_price = float(price_result['list'][0]['lastPrice'])
    print(f"السعر الحالي: ${current_price}")
    
    # اختبار 2: حساب الكمية
    trade_amount = 10.0  # مبلغ صغير للاختبار
    qty = trade_amount / current_price
    qty = round(qty, 6)
    
    print(f"مبلغ التداول: ${trade_amount}")
    print(f"الكمية المحسوبة: {qty} BTC")
    print()
    
    # اختبار 3: وضع أمر Spot
    print("اختبار 3: وضع أمر Spot...")
    spot_params = {
        'category': 'spot',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': str(qty)
    }
    
    spot_result = make_request('POST', '/v5/order/create', spot_params)
    
    if spot_result:
        print("نجح وضع أمر Spot!")
        print(f"Order ID: {spot_result.get('orderId')}")
        print(f"Order Link ID: {spot_result.get('orderLinkId')}")
    else:
        print("فشل وضع أمر Spot")
    
    print()
    
    # اختبار 4: وضع أمر Futures
    print("اختبار 4: وضع أمر Futures...")
    futures_params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': str(qty)
    }
    
    futures_result = make_request('POST', '/v5/order/create', futures_params)
    
    if futures_result:
        print("نجح وضع أمر Futures!")
        print(f"Order ID: {futures_result.get('orderId')}")
        print(f"Order Link ID: {futures_result.get('orderLinkId')}")
    else:
        print("فشل وضع أمر Futures")
    
    print()
    
    # اختبار 5: فحص الصفقات المفتوحة
    print("اختبار 5: فحص الصفقات المفتوحة...")
    
    # فحص Spot positions
    spot_positions = make_request('GET', '/v5/position/list', {'category': 'spot'})
    if spot_positions:
        print(f"Spot positions: {len(spot_positions.get('list', []))}")
        for pos in spot_positions.get('list', []):
            print(f"  - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
    
    # فحص Futures positions
    futures_positions = make_request('GET', '/v5/position/list', {'category': 'linear'})
    if futures_positions:
        print(f"Futures positions: {len(futures_positions.get('list', []))}")
        for pos in futures_positions.get('list', []):
            print(f"  - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
    
    print()
    
    # اختبار 6: فحص الأوامر المفتوحة
    print("اختبار 6: فحص الأوامر المفتوحة...")
    
    # فحص Spot orders
    spot_orders = make_request('GET', '/v5/order/realtime', {'category': 'spot'})
    if spot_orders:
        print(f"Spot orders: {len(spot_orders.get('list', []))}")
        for order in spot_orders.get('list', []):
            print(f"  - {order.get('symbol')}: {order.get('side')} {order.get('qty')} - {order.get('orderStatus')}")
    
    # فحص Futures orders
    futures_orders = make_request('GET', '/v5/order/realtime', {'category': 'linear'})
    if futures_orders:
        print(f"Futures orders: {len(futures_orders.get('list', []))}")
        for order in futures_orders.get('list', []):
            print(f"  - {order.get('symbol')}: {order.get('side')} {order.get('qty')} - {order.get('orderStatus')}")

if __name__ == "__main__":
    test_bybit_order_placement()
