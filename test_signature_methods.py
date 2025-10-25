#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار توليد التوقيع لـ MEXC بطريقة مختلفة
"""

import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_signature_methods():
    """اختبار طرق مختلفة لتوليد التوقيع"""
    
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    # معاملات الاختبار
    params = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.0001',
        'timestamp': int(time.time() * 1000)
    }
    
    print("=== اختبار طرق توليد التوقيع ===")
    print(f"المعاملات: {params}")
    print(f"API Secret: {api_secret[:8]}...{api_secret[-4:]}")
    
    # الطريقة الحالية
    print("\n1. الطريقة الحالية:")
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params)
    signature1 = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    print(f"Query String: {query_string}")
    print(f"Signature: {signature1}")
    
    # طريقة أخرى - بدون ترتيب
    print("\n2. بدون ترتيب:")
    query_string2 = urlencode(params)
    signature2 = hmac.new(
        api_secret.encode('utf-8'),
        query_string2.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    print(f"Query String: {query_string2}")
    print(f"Signature: {signature2}")
    
    # طريقة أخرى - مع timestamp في النهاية
    print("\n3. مع timestamp في النهاية:")
    params3 = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.0001'
    }
    sorted_params3 = sorted(params3.items())
    query_string3 = urlencode(sorted_params3)
    query_string3 += f"&timestamp={params['timestamp']}"
    signature3 = hmac.new(
        api_secret.encode('utf-8'),
        query_string3.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    print(f"Query String: {query_string3}")
    print(f"Signature: {signature3}")
    
    # طريقة أخرى - مع recvWindow
    print("\n4. مع recvWindow:")
    params4 = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.0001',
        'timestamp': params['timestamp'],
        'recvWindow': 5000
    }
    sorted_params4 = sorted(params4.items())
    query_string4 = urlencode(sorted_params4)
    signature4 = hmac.new(
        api_secret.encode('utf-8'),
        query_string4.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    print(f"Query String: {query_string4}")
    print(f"Signature: {signature4}")

if __name__ == "__main__":
    test_signature_methods()
