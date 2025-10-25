#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تشخيصي لوضع أمر على MEXC
"""

import logging
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_mexc_order_without_real_keys():
    """اختبار وضع أمر بدون مفاتيح API حقيقية (للتشخيص)"""
    print("=" * 60)
    print("اختبار تشخيصي لوضع أمر على MEXC")
    print("=" * 60)
    
    # مفاتيح تجريبية
    api_key = "test_key_123456789"
    api_secret = "test_secret_123456789"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {'*' * len(api_secret)}")
    
    # معاملات الأمر
    params = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.001'
    }
    
    print(f"معاملات الأمر: {params}")
    
    # إضافة timestamp
    timestamp = int(time.time() * 1000)
    params['timestamp'] = timestamp
    print(f"Timestamp: {timestamp}")
    
    # توليد التوقيع
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params)
    print(f"Query String: {query_string}")
    
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    print(f"Signature: {signature}")
    
    # إرسال الطلب
    url = "https://api.mexc.com/api/v3/order"
    headers = {
        'X-MEXC-APIKEY': api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Final Params: {params}")
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=15)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("الطلب نجح!")
            return True
        else:
            print("الطلب فشل!")
            return False
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")
        return False

def test_mexc_public_endpoints():
    """اختبار endpoints العامة"""
    print("\n" + "=" * 60)
    print("اختبار endpoints العامة")
    print("=" * 60)
    
    endpoints = [
        '/api/v3/ping',
        '/api/v3/ticker/price?symbol=BTCUSDT',
        '/api/v3/exchangeInfo'
    ]
    
    for endpoint in endpoints:
        print(f"\nاختبار: {endpoint}")
        try:
            url = f"https://api.mexc.com{endpoint}"
            response = requests.get(url, timeout=10)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("نجح!")
            else:
                print(f"فشل: {response.text}")
                
        except Exception as e:
            print(f"خطأ: {e}")

if __name__ == "__main__":
    print("بدء الاختبار التشخيصي...")
    
    # اختبار endpoints العامة
    test_mexc_public_endpoints()
    
    # اختبار وضع أمر (سيفشل لكن سنرى السبب)
    test_mexc_order_without_real_keys()
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار التشخيصي")
    print("=" * 60)
