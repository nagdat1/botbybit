#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح مشكلة التوقيع في Bybit API V5
"""

import sys
import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
import json

def fix_bybit_signature():
    """إصلاح مشكلة التوقيع في Bybit API V5"""
    
    print("=== إصلاح مشكلة التوقيع في Bybit API V5 ===")
    print()
    
    # بيانات الاختبار
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
    # الطريقة الصحيحة لتوليد التوقيع
    print("الطريقة الصحيحة لتوليد التوقيع:")
    print()
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # للطلبات GET، استخدام query string
    params = {'accountType': 'UNIFIED'}
    params_str = urlencode(sorted(params.items()))
    
    print(f"1. Timestamp: {timestamp}")
    print(f"2. Recv Window: {recv_window}")
    print(f"3. Params: {params}")
    print(f"4. Params String: {params_str}")
    print()
    
    # توليد التوقيع الصحيح
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"5. Sign String: {sign_str}")
    print(f"6. Signature: {signature}")
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
    
    print(f"7. URL: {url}")
    print(f"8. Headers: {headers}")
    print()
    
    try:
        print("إرسال الطلب...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("الطلب نجح! التوقيع صحيح")
                return True
            else:
                print(f"خطأ في API: {result.get('retMsg')}")
                return False
        else:
            print(f"خطأ HTTP: {response.status_code}")
            if response.status_code == 401:
                print("خطأ 401: مشكلة في المصادقة")
                print("السبب المحتمل: API Key أو Secret غير صحيح")
            return False
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")
        return False

def test_post_request():
    """اختبار طلب POST مع التوقيع الصحيح"""
    
    print("=== اختبار طلب POST مع التوقيع الصحيح ===")
    print()
    
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # للطلبات POST، استخدام JSON string
    params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '0.0001'
    }
    
    # تحويل إلى JSON string للتوقيع
    params_str = json.dumps(params, separators=(',', ':'))
    
    print(f"1. Timestamp: {timestamp}")
    print(f"2. Recv Window: {recv_window}")
    print(f"3. Params: {params}")
    print(f"4. Params String (JSON): {params_str}")
    print()
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"5. Sign String: {sign_str}")
    print(f"6. Signature: {signature}")
    print()
    
    # إرسال الطلب POST
    url = "https://api.bybit.com/v5/order/create"
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    print(f"7. URL: {url}")
    print(f"8. Headers: {headers}")
    print()
    
    try:
        print("إرسال طلب POST...")
        response = requests.post(url, headers=headers, json=params, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("طلب POST نجح! التوقيع صحيح")
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

if __name__ == "__main__":
    print("اختيار نوع الاختبار:")
    print("1. اختبار طلب GET (wallet balance)")
    print("2. اختبار طلب POST (order create)")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = fix_bybit_signature()
    elif choice == "2":
        success = test_post_request()
    else:
        print("اختيار غير صحيح")
        sys.exit(1)
    
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل")
        sys.exit(1)
