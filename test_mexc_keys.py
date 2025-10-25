#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي لمفاتيح MEXC API
"""

import logging
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_mexc_api_keys():
    """اختبار مفاتيح MEXC API"""
    print("=" * 60)
    print("اختبار مفاتيح MEXC API")
    print("=" * 60)
    
    # المفاتيح المقدمة
    api_key = "mx0vglBqh6abc123xyz456"
    api_secret = "cd479996b38a4944933bbe79015ffa09"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {'*' * len(api_secret)}")
    
    # اختبار الاتصال العام أولاً
    print("\n1. اختبار الاتصال العام...")
    try:
        response = requests.get('https://api.mexc.com/api/v3/ping', timeout=10)
        if response.status_code == 200:
            print(" الاتصال العام ناجح")
        else:
            print(f" فشل الاتصال العام: {response.status_code}")
            return False
    except Exception as e:
        print(f" خطأ في الاتصال العام: {e}")
        return False
    
    # اختبار جلب السعر
    print("\n2. اختبار جلب السعر...")
    try:
        response = requests.get('https://api.mexc.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" السعر الحالي: ${float(data['price']):,.2f}")
        else:
            print(f" فشل جلب السعر: {response.status_code}")
            return False
    except Exception as e:
        print(f" خطأ في جلب السعر: {e}")
        return False
    
    # اختبار التوقيع
    print("\n3. اختبار التوقيع...")
    try:
        timestamp = int(time.time() * 1000)
        params = {'timestamp': timestamp}
        
        # ترتيب المعاملات أبجدياً
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        # إنشاء التوقيع
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"Timestamp: {timestamp}")
        print(f"Query String: {query_string}")
        print(f"Signature: {signature}")
        
        # اختبار الطلب الموقع
        headers = {'X-MEXC-APIKEY': api_key}
        params['signature'] = signature
        
        response = requests.get(
            'https://api.mexc.com/api/v3/account',
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print(" التوقيع صحيح!")
            return True
        else:
            print(" التوقيع غير صحيح!")
            return False
            
    except Exception as e:
        print(f" خطأ في اختبار التوقيع: {e}")
        return False

def show_solution():
    """عرض الحلول المقترحة"""
    print("\n" + "=" * 60)
    print("الحلول المقترحة")
    print("=" * 60)
    
    print("""
المشكلة: مفاتيح API غير صحيحة أو غير مفعلة

الحلول:

1. تحقق من صحة المفاتيح:
   - تأكد من نسخ المفاتيح بشكل صحيح
   - لا توجد مسافات إضافية في البداية أو النهاية

2. تحقق من تفعيل API في حسابك:
   - اذهب إلى MEXC.com
   - Account → API Management
   - تأكد من أن API Key مفعل

3. تحقق من الصلاحيات:
   - تأكد من تفعيل صلاحية "Read Info"
   - تأكد من تفعيل صلاحية "Spot Trading"

4. تحقق من تقييد IP:
   - إذا كان هناك تقييد IP، تأكد من إضافة IP الخاص بك
   - أو قم بإزالة تقييد IP للاختبار

5. إنشاء مفاتيح جديدة:
   - احذف المفاتيح القديمة
   - أنشئ مفاتيح جديدة مع الصلاحيات المطلوبة

6. تحقق من حالة الحساب:
   - تأكد من أن الحساب مفعل
   - تأكد من إكمال التحقق المطلوب (KYC)

بعد تطبيق هذه الحلول، جرب الاختبار مرة أخرى.
""")

if __name__ == "__main__":
    print("بدء اختبار مفاتيح MEXC API...")
    
    success = test_mexc_api_keys()
    
    if success:
        print("\n النتيجة: مفاتيح API صحيحة!")
        print(" يمكنك الآن استخدام MEXC للتداول")
    else:
        print("\n النتيجة: مفاتيح API غير صحيحة!")
        show_solution()
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)
