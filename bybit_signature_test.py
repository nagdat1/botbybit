#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشكلة التوقيع في Bybit API V5
المشكلة: Signature for this request is not valid
الحل: تصحيح طريقة توليد التوقيع
"""

import hmac
import hashlib
import time
import json
import requests
from urllib.parse import urlencode

def test_bybit_signature():
    """اختبار طريقة التوقيع الصحيحة"""
    
    # مفاتيح API التجريبية
    api_key = "RKk6fTapgDqys6vt5S"
    api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print("اختبار طريقة التوقيع الصحيحة لـ Bybit API V5")
    print("="*60)
    
    # اختبار 1: طلب GET (wallet balance)
    print("\nاختبار 1: طلب GET - جلب الرصيد")
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # معاملات GET
    get_params = {'accountType': 'UNIFIED'}
    get_params_str = urlencode(sorted(get_params.items()))
    
    # بناء التوقيع لـ GET
    get_sign_str = timestamp + api_key + recv_window + get_params_str
    get_signature = hmac.new(
        api_secret.encode('utf-8'),
        get_sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"GET sign_str: {get_sign_str}")
    print(f"GET signature: {get_signature}")
    
    # إرسال طلب GET
    get_url = f"https://api.bybit.com/v5/account/wallet-balance?{get_params_str}"
    get_headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': get_signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window
    }
    
    try:
        get_response = requests.get(get_url, headers=get_headers, timeout=10)
        print(f"GET Response Status: {get_response.status_code}")
        if get_response.status_code == 200:
            print("نجح طلب GET!")
        else:
            print(f"فشل طلب GET: {get_response.text}")
    except Exception as e:
        print(f"خطأ في طلب GET: {e}")
    
    # اختبار 2: طلب POST (place order)
    print("\nاختبار 2: طلب POST - وضع أمر")
    timestamp = str(int(time.time() * 1000))
    
    # معاملات POST
    post_params = {
        'category': 'spot',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '0.001'
    }
    
    # بناء التوقيع لـ POST - الطريقة الصحيحة
    post_params_str = json.dumps(post_params, separators=(',', ':'))
    post_sign_str = timestamp + api_key + recv_window + post_params_str
    post_signature = hmac.new(
        api_secret.encode('utf-8'),
        post_sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"POST params: {post_params}")
    print(f"POST params_str: {post_params_str}")
    print(f"POST sign_str: {post_sign_str}")
    print(f"POST signature: {post_signature}")
    
    # إرسال طلب POST
    post_url = "https://api.bybit.com/v5/order/create"
    post_headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': post_signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    try:
        post_response = requests.post(post_url, headers=post_headers, json=post_params, timeout=10)
        print(f"POST Response Status: {post_response.status_code}")
        print(f"POST Response: {post_response.text}")
        
        if post_response.status_code == 200:
            result = post_response.json()
            if result.get('retCode') == 0:
                print("نجح طلب POST!")
            else:
                print(f"فشل طلب POST: {result.get('retMsg')}")
        else:
            print(f"فشل طلب POST: {post_response.text}")
            
    except Exception as e:
        print(f"خطأ في طلب POST: {e}")
    
    print("\n" + "="*60)
    print("ملخص الاختبار:")
    print("1. تأكد من استخدام json.dumps مع separators=(',', ':')")
    print("2. تأكد من إرسال المعاملات في JSON body للطلبات POST")
    print("3. تأكد من صحة مفاتيح API")
    print("4. تأكد من وجود رصيد كافي في الحساب")

if __name__ == "__main__":
    test_bybit_signature()
