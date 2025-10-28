#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الحل الشامل لمشكلة Bybit API
"""

import sys
import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
import json

def comprehensive_bybit_fix():
    """الحل الشامل لمشكلة Bybit API"""
    
    print("=== الحل الشامل لمشكلة Bybit API ===")
    print()
    
    print("المشكلة: خطأ 401 Unauthorized")
    print("السبب: مشكلة في المصادقة")
    print()
    
    print("الحلول المحتملة:")
    print("1. API Key أو Secret غير صحيح")
    print("2. صلاحيات API Key غير كافية")
    print("3. قيود IP")
    print("4. مشكلة في التوقيع")
    print("5. مشكلة في الوقت")
    print()
    
    # اختبار مع مفاتيح جديدة
    print("أدخل API Key الجديد:")
    api_key = input("API Key: ").strip()
    
    print("أدخل API Secret الجديد:")
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("API Key أو Secret فارغ!")
        return False
    
    print()
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
        print("إرسال الطلب...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('retCode') == 0:
                print("الطلب نجح! المفاتيح صحيحة")
                print(f"الرصيد: {result.get('result', {}).get('list', [{}])[0].get('totalEquity', 'N/A')}")
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

def create_new_api_key_guide():
    """دليل إنشاء API Key جديد"""
    
    print("=== دليل إنشاء API Key جديد ===")
    print()
    
    print("1. اذهب إلى Bybit.com")
    print("2. سجل دخول إلى حسابك")
    print("3. اذهب إلى Account → API Management")
    print("4. اضغط على Create New Key")
    print("5. اختر الصلاحيات التالية:")
    print("   - Read (مطلوب)")
    print("   - Trade (مطلوب)")
    print("   - Position Management (مطلوب)")
    print("   - Wallet Transfer (اختياري)")
    print("6. لا تضع قيود IP (اتركه فارغ)")
    print("7. اضغط على Create")
    print("8. انسخ API Key و API Secret")
    print()
    
    print("ملاحظات مهمة:")
    print("- تأكد من أن الصلاحيات مفعلة")
    print("- لا تضع قيود IP")
    print("- احفظ المفاتيح في مكان آمن")
    print()

if __name__ == "__main__":
    print("اختيار نوع الاختبار:")
    print("1. اختبار مع مفاتيح جديدة")
    print("2. دليل إنشاء API Key جديد")
    
    choice = input("اختر (1 أو 2): ").strip()
    
    if choice == "1":
        success = comprehensive_bybit_fix()
    elif choice == "2":
        create_new_api_key_guide()
        success = True
    else:
        print("اختيار غير صحيح")
        sys.exit(1)
    
    if success:
        print("الاختبار نجح!")
    else:
        print("الاختبار فشل")
        sys.exit(1)
