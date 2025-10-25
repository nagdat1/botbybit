#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح نهائي لمشكلة التوقيع في Bybit API V5
المشكلة: Signature for this request is not valid
الحل: تصحيح طريقة توليد التوقيع لطلبات POST
"""

import hmac
import hashlib
import time
import json
import requests
from urllib.parse import urlencode

def test_correct_bybit_signature():
    """اختبار الطريقة الصحيحة لتوقيع طلبات Bybit POST"""
    
    # مفاتيح API التجريبية
    api_key = "RKk6fTapgDqys6vt5S"
    api_secret = "Rm1TEZnF8hJhZgoj2btSJCr7lx64qAP55dhp"
    
    print("اختبار الطريقة الصحيحة لتوقيع طلبات Bybit POST")
    print("="*60)
    
    # اختبار طلب POST مع الطريقة الصحيحة
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # معاملات POST
    post_params = {
        'category': 'spot',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '0.001'
    }
    
    # الطريقة الصحيحة: استخدام JSON string للتوقيع
    post_params_str = json.dumps(post_params, separators=(',', ':'))
    
    # بناء التوقيع
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
                return True
            else:
                print(f"فشل طلب POST: {result.get('retMsg')}")
                return False
        else:
            print(f"فشل طلب POST: {post_response.text}")
            return False
            
    except Exception as e:
        print(f"خطأ في طلب POST: {e}")
        return False

def apply_signature_fix():
    """تطبيق الإصلاح على ملف real_account_manager.py"""
    
    print("\nتطبيق الإصلاح على ملف real_account_manager.py")
    print("="*60)
    
    # قراءة الملف الحالي
    try:
        with open('real_account_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من وجود المشكلة
        if 'json.dumps(params, separators=(\',\', \':\'))' in content:
            print("تم العثور على الكود الصحيح بالفعل")
            return True
        
        # تطبيق الإصلاح إذا لم يكن موجوداً
        old_code = 'json.dumps(params, separators=(\', \', \': \'))'
        new_code = 'json.dumps(params, separators=(\',\', \':\'))'
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            
            with open('real_account_manager.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("تم تطبيق الإصلاح بنجاح!")
            return True
        else:
            print("لم يتم العثور على الكود الذي يحتاج إصلاح")
            return False
            
    except Exception as e:
        print(f"خطأ في تطبيق الإصلاح: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("إصلاح نهائي لمشكلة التوقيع في Bybit API V5")
    print("="*60)
    
    # اختبار الطريقة الصحيحة
    test_success = test_correct_bybit_signature()
    
    if test_success:
        print("\nتم إصلاح المشكلة بنجاح!")
        print("الطريقة الصحيحة:")
        print("1. استخدام json.dumps مع separators=(',', ':')")
        print("2. إرسال المعاملات في JSON body")
        print("3. استخدام التوقيع الصحيح")
    else:
        print("\nلا تزال هناك مشكلة في التوقيع")
        print("تحقق من:")
        print("1. صحة مفاتيح API")
        print("2. وجود رصيد كافي")
        print("3. صحة المعاملات")
    
    # تطبيق الإصلاح
    fix_success = apply_signature_fix()
    
    if fix_success:
        print("\nتم تطبيق الإصلاح على الملفات")
    else:
        print("\nفشل في تطبيق الإصلاح")

if __name__ == "__main__":
    main()
