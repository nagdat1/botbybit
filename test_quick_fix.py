#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لإصلاح خطأ user_id
"""

import requests
import json

def test_quick_fix():
    """اختبار سريع للإصلاح"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print("🔧 اختبار الإصلاح السريع")
    print("=" * 50)
    print(f"🔗 الرابط: {webhook_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 50)
    
    # إشارة اختبار بسيطة
    signal_data = {
        "symbol": "BTCUSDT",
        "action": "buy"
    }
    
    print("📡 إرسال إشارة اختبار...")
    print(json.dumps(signal_data, indent=2))
    print("-" * 50)
    
    try:
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print("📊 النتيجة:")
        print(f"   📈 Status Code: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ نجح الإصلاح!")
            print("📋 تحقق من البوت في Telegram")
            print("📋 يجب أن تظهر رسائل تأكيد")
        else:
            print("❌ لا يزال هناك مشكلة")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    test_quick_fix()
