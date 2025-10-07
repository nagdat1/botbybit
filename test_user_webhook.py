#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار رابط الإشارة الشخصية للمستخدم 8169000394
"""

import requests
import json

def test_user_webhook():
    """اختبار رابط الإشارة الشخصية"""
    
    # إعدادات الاختبار
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print("🧪 اختبار رابط الإشارة الشخصية")
    print("=" * 60)
    print(f"🔗 الرابط: {webhook_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 60)
    
    # إشارة اختبار
    signal_data = {
        "symbol": "NFPUSDT",
        "action": "buy"
    }
    
    print("📡 إرسال إشارة:")
    print(json.dumps(signal_data, indent=2))
    print("-" * 60)
    
    try:
        # إرسال الطلب
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print("📊 النتيجة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ تم إرسال الإشارة بنجاح!")
            try:
                response_data = response.json()
                print(f"   Response Data: {json.dumps(response_data, indent=2)}")
            except:
                pass
        else:
            print("❌ فشل في إرسال الإشارة")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def test_health():
    """اختبار حالة السيرفر"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    health_url = f"{BASE_URL}/health"
    
    print("\n🏥 اختبار حالة السيرفر")
    print("=" * 60)
    print(f"🔗 الرابط: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ السيرفر يعمل بشكل طبيعي")
        else:
            print("❌ مشكلة في السيرفر")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار رابط الإشارة الشخصية")
    print("=" * 80)
    
    # اختبار حالة السيرفر
    test_health()
    
    # اختبار الإشارة الشخصية
    test_user_webhook()
    
    print("\n🏁 انتهى الاختبار")
    print("=" * 80)
    print("📋 تحقق من سجلات Railway لرؤية المزيد من التفاصيل")
    print("🔗 https://railway.app/dashboard")
