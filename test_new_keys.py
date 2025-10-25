#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
import json

def test_new_bybit_keys():
    """اختبار مفاتيح Bybit الجديدة"""
    
    print("=== اختبار مفاتيح Bybit الجديدة ===")
    print()
    
    # المفاتيح الجديدة
    api_key = "RKk6fTapgDqys6vt5S"
    api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print()
    
    # ========================================
    # اختبار 1: جلب الرصيد (Wallet Balance)
    # ========================================
    print("=" * 50)
    print("اختبار 1: جلب الرصيد (Wallet Balance)")
    print("=" * 50)
    print()
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = {'accountType': 'UNIFIED'}
    params_str = urlencode(sorted(params.items()))
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
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
    print(f"Timestamp: {timestamp}")
    print(f"Signature: {signature}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("نتيجة الاختبار 1: نجح")
                wallet_data = result.get('result', {}).get('list', [])
                if wallet_data:
                    total_equity = wallet_data[0].get('totalEquity', '0')
                    print(f"الرصيد الكلي: {total_equity} USDT")
                print()
            else:
                print(f"نتيجة الاختبار 1: فشل")
                print(f"خطأ: {result.get('retMsg')}")
                print(f"رمز الخطأ: {result.get('retCode')}")
                return False
        else:
            print(f"نتيجة الاختبار 1: فشل")
            print(f"خطأ HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"نتيجة الاختبار 1: فشل")
        print(f"خطأ: {e}")
        return False
    
    # ========================================
    # اختبار 2: جلب السعر (Ticker)
    # ========================================
    print("=" * 50)
    print("اختبار 2: جلب السعر (Ticker)")
    print("=" * 50)
    print()
    
    timestamp = str(int(time.time() * 1000))
    params = {'category': 'linear', 'symbol': 'BTCUSDT'}
    params_str = urlencode(sorted(params.items()))
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # إرسال الطلب
    url = f"https://api.bybit.com/v5/market/tickers?{params_str}"
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text[:200]}...")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("نتيجة الاختبار 2: نجح")
                ticker_list = result.get('result', {}).get('list', [])
                if ticker_list:
                    last_price = ticker_list[0].get('lastPrice', '0')
                    print(f"سعر BTCUSDT: ${float(last_price):,.2f}")
                print()
            else:
                print(f"نتيجة الاختبار 2: فشل")
                print(f"خطأ: {result.get('retMsg')}")
                return False
        else:
            print(f"نتيجة الاختبار 2: فشل")
            print(f"خطأ HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"نتيجة الاختبار 2: فشل")
        print(f"خطأ: {e}")
        return False
    
    # ========================================
    # اختبار 3: وضع الرافعة المالية (Set Leverage)
    # ========================================
    print("=" * 50)
    print("اختبار 3: وضع الرافعة المالية (Set Leverage)")
    print("=" * 50)
    print()
    
    timestamp = str(int(time.time() * 1000))
    params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'buyLeverage': '2',
        'sellLeverage': '2'
    }
    
    # للطلبات POST، استخدام JSON string للتوقيع
    params_str = json.dumps(params, separators=(',', ':'))
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # إرسال الطلب
    url = "https://api.bybit.com/v5/position/set-leverage"
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Sign String: {sign_str}")
    print(f"Signature: {signature}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=params, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("نتيجة الاختبار 3: نجح")
                print("تم وضع الرافعة المالية: 2x")
                print()
            else:
                print(f"نتيجة الاختبار 3: فشل")
                print(f"خطأ: {result.get('retMsg')}")
                print(f"رمز الخطأ: {result.get('retCode')}")
                if result.get('retCode') in [10003, 10005]:
                    print("المشكلة: صلاحيات API Key غير كافية")
                    print("الحل: تفعيل Position Management في Bybit")
                return False
        else:
            print(f"نتيجة الاختبار 3: فشل")
            print(f"خطأ HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"نتيجة الاختبار 3: فشل")
        print(f"خطأ: {e}")
        return False
    
    # ========================================
    # الخلاصة
    # ========================================
    print("=" * 50)
    print("الخلاصة")
    print("=" * 50)
    print()
    print("جميع الاختبارات نجحت!")
    print("المفاتيح صحيحة ويمكن استخدامها للتداول")
    print()
    
    return True

if __name__ == "__main__":
    success = test_new_bybit_keys()
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل!")
        print("يرجى التحقق من:")
        print("1. صحة API Key و Secret")
        print("2. صلاحيات API Key (Read, Trade, Position Management)")
        print("3. عدم وجود قيود IP")
