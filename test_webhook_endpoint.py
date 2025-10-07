#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار endpoint رابط الإشارة الشخصية
"""

import requests
import json
import time

def test_webhook_endpoint():
    """اختبار endpoint رابط الإشارة الشخصية"""
    
    # إعدادات الاختبار
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    # اختبار endpoint
    test_url = f"{BASE_URL}/personal/{USER_ID}/test"
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print("🧪 اختبار endpoint رابط الإشارة الشخصية")
    print("=" * 70)
    print(f"🔗 رابط الاختبار: {test_url}")
    print(f"🔗 رابط Webhook: {webhook_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 70)
    
    # اختبار 1: فحص endpoint
    print("📡 اختبار 1: فحص endpoint")
    try:
        response = requests.get(test_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ endpoint يعمل بشكل صحيح")
        else:
            print("   ❌ endpoint لا يعمل")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    print("-" * 70)
    
    # اختبار 2: فحص health
    print("📡 اختبار 2: فحص حالة السيرفر")
    health_url = f"{BASE_URL}/health"
    try:
        response = requests.get(health_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ السيرفر يعمل بشكل صحيح")
        else:
            print("   ❌ السيرفر لا يعمل")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    print("-" * 70)
    
    # اختبار 3: إرسال إشارة
    print("📡 اختبار 3: إرسال إشارة")
    signal_data = {
        "symbol": "NFPUSDT",
        "action": "buy"
    }
    
    print(f"   البيانات: {json.dumps(signal_data, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ تم إرسال الإشارة بنجاح")
            try:
                response_data = response.json()
                print(f"   📊 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                pass
        else:
            print("   ❌ فشل في إرسال الإشارة")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    print("-" * 70)
    
    # اختبار 4: إرسال إشارة بدون بيانات
    print("📡 اختبار 4: إرسال إشارة بدون بيانات")
    try:
        response = requests.post(
            webhook_url,
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400:
            print("   ✅ تم رفض الطلب بدون بيانات (كما هو متوقع)")
        else:
            print("   ❌ لم يتم رفض الطلب بدون بيانات")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def test_different_users():
    """اختبار مستخدمين مختلفين"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    users = [8169000394, 123456789, 987654321]
    
    print("\n🧪 اختبار مستخدمين مختلفين")
    print("=" * 70)
    
    for user_id in users:
        print(f"📡 اختبار المستخدم: {user_id}")
        
        test_url = f"{BASE_URL}/personal/{user_id}/test"
        
        try:
            response = requests.get(test_url, timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ يعمل")
            else:
                print("   ❌ لا يعمل")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 بدء اختبار endpoint رابط الإشارة الشخصية")
    print("=" * 80)
    
    # اختبار أساسي
    test_webhook_endpoint()
    
    # اختبار مستخدمين مختلفين
    test_different_users()
    
    print("\n🏁 انتهى الاختبار")
    print("=" * 80)
    print("📋 تعليمات التحقق:")
    print("   1. تحقق من أن جميع الاختبارات تعطي ✅")
    print("   2. إذا كان هناك ❌، تحقق من سجلات Railway")
    print("   3. تأكد من أن السيرفر يعمل على Railway")
    print("\n🔗 روابط مفيدة:")
    print("   📊 Railway Dashboard: https://railway.app/dashboard")
    print("   📋 Logs: https://railway.app/dashboard → Logs")
    print("   🏥 Health Check: https://botbybit-production.up.railway.app/health")
