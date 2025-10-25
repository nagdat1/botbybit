#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص مشكلة التوقيع في المشروع
"""

import sys
import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
import json

def test_signature_issue():
    """فحص مشكلة التوقيع في المشروع"""
    
    print("=== فحص مشكلة التوقيع في المشروع ===")
    print()
    
    # بيانات الاختبار
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
    # اختبار طلب بسيط
    print("1. اختبار طلب بسيط (wallet balance)...")
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    params = {'accountType': 'UNIFIED'}
    params_str = urlencode(sorted(params.items()))
    
    print(f"Timestamp: {timestamp}")
    print(f"Recv Window: {recv_window}")
    print(f"Params: {params}")
    print(f"Params String: {params_str}")
    print()
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"Sign String: {sign_str}")
    print(f"Signature: {signature}")
    print()
    
    # إرسال الطلب
    url = f"https://api.bybit.com/v5/account/wallet-balance?{params_str}"
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("الطلب نجح!")
                return True
            else:
                print(f"خطأ في API: {result.get('retMsg')}")
                return False
        else:
            print(f"خطأ HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")
        return False

def test_different_signature_methods():
    """اختبار طرق مختلفة لتوليد التوقيع"""
    
    print("=== اختبار طرق مختلفة لتوليد التوقيع ===")
    print()
    
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    params = {'accountType': 'UNIFIED'}
    
    # الطريقة 1: Query string مرتب
    params_str1 = urlencode(sorted(params.items()))
    sign_str1 = timestamp + api_key + recv_window + params_str1
    signature1 = hmac.new(
        api_secret.encode('utf-8'),
        sign_str1.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print("الطريقة 1: Query string مرتب")
    print(f"Params String: {params_str1}")
    print(f"Sign String: {sign_str1}")
    print(f"Signature: {signature1}")
    print()
    
    # الطريقة 2: Query string غير مرتب
    params_str2 = urlencode(params)
    sign_str2 = timestamp + api_key + recv_window + params_str2
    signature2 = hmac.new(
        api_secret.encode('utf-8'),
        sign_str2.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print("الطريقة 2: Query string غير مرتب")
    print(f"Params String: {params_str2}")
    print(f"Sign String: {sign_str2}")
    print(f"Signature: {signature2}")
    print()
    
    # الطريقة 3: JSON string
    params_str3 = json.dumps(params, separators=(',', ':'))
    sign_str3 = timestamp + api_key + recv_window + params_str3
    signature3 = hmac.new(
        api_secret.encode('utf-8'),
        sign_str3.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print("الطريقة 3: JSON string")
    print(f"Params String: {params_str3}")
    print(f"Sign String: {sign_str3}")
    print(f"Signature: {signature3}")
    print()
    
    return True

if __name__ == "__main__":
    print("اختيار نوع الاختبار:")
    print("1. اختبار طلب بسيط")
    print("2. اختبار طرق مختلفة للتوقيع")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = test_signature_issue()
    elif choice == "2":
        success = test_different_signature_methods()
    else:
        print("اختيار غير صحيح")
        sys.exit(1)
    
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل")
        sys.exit(1)
