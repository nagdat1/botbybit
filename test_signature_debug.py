#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مفصل لمشكلة التوقيع في MEXC
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode

def test_signature():
    """اختبار مفصل لمشكلة التوقيع"""
    
    print("=" * 60)
    print("اختبار مفصل لمشكلة التوقيع في MEXC")
    print("=" * 60)
    
    # إعداد البيانات
    api_key = 'mx0vglb3kLs2Rbe8pG'
    api_secret = 'cd479996b38a4944933bbe79015ffa09'
    
    # إعداد الطلب
    url = "https://api.mexc.com/api/v3/order"
    timestamp = int(time.time() * 1000)
    
    params = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.0001',
        'timestamp': timestamp
    }
    
    print(f"المعاملات الأصلية: {params}")
    
    # ترتيب المعاملات أبجدياً
    sorted_params = sorted(params.items())
    print(f"المعاملات المرتبة: {sorted_params}")
    
    # إنشاء query string
    query_string = urlencode(sorted_params)
    print(f"Query String: {query_string}")
    
    # إنشاء التوقيع
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"التوقيع: {signature}")
    
    # إضافة التوقيع للمعاملات
    params['signature'] = signature
    
    headers = {
        'X-MEXC-APIKEY': api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"\nإرسال الطلب...")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=15)
        print(f"\nالنتيجة:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("نجح الطلب!")
        else:
            print("فشل الطلب!")
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")

if __name__ == "__main__":
    test_signature()
