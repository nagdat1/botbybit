#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النظام الكامل - رابط الإشارة كبديل كامل للمشروع
"""

import requests
import json
import time

def test_full_project_start():
    """اختبار بدء المشروع كاملاً لمستخدم"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    start_url = f"{BASE_URL}/personal/{USER_ID}/start"
    
    print("🚀 اختبار بدء المشروع كاملاً")
    print("=" * 70)
    print(f"🔗 الرابط: {start_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 70)
    
    try:
        print("⏳ إرسال طلب بدء المشروع...")
        start_time = time.time()
        
        response = requests.post(
            start_url,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print("📊 النتيجة:")
        print(f"   ⏱️ وقت الاستجابة: {response_time:.2f} ثانية")
        print(f"   📈 Status Code: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ تم بدء المشروع بنجاح!")
            try:
                response_data = response.json()
                print(f"   📊 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                pass
            
            print("\n🔍 التحقق من بدء المشروع:")
            print("   📋 تحقق من البوت في Telegram")
            print("   📋 يجب أن تظهر رسالة ترحيب")
            print("   📋 يجب أن يظهر رابط الإشارة الشخصي")
            
        else:
            print("❌ فشل في بدء المشروع")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def test_webhook_with_signal():
    """اختبار رابط الإشارة مع إشارة تداول"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print("\n📡 اختبار رابط الإشارة مع إشارة تداول")
    print("=" * 70)
    print(f"🔗 الرابط: {webhook_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 70)
    
    # إشارة اختبار
    signal_data = {
        "symbol": "NFPUSDT",
        "action": "buy"
    }
    
    print("📡 إرسال إشارة:")
    print(json.dumps(signal_data, indent=2))
    print("-" * 70)
    
    try:
        print("⏳ إرسال الإشارة...")
        start_time = time.time()
        
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print("📊 النتيجة:")
        print(f"   ⏱️ وقت الاستجابة: {response_time:.2f} ثانية")
        print(f"   📈 Status Code: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ تم إرسال الإشارة بنجاح!")
            try:
                response_data = response.json()
                print(f"   📊 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                pass
            
            print("\n🔍 التحقق من تنفيذ الإشارة:")
            print("   📋 تحقق من البوت في Telegram")
            print("   📋 يجب أن تظهر رسالة ترحيب")
            print("   📋 يجب أن تظهر رسالة تأكيد الإشارة")
            print("   📋 يجب أن تظهر رسالة تأكيد الصفقة")
            
        else:
            print("❌ فشل في إرسال الإشارة")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def test_endpoint_status():
    """اختبار حالة جميع الـ endpoints"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    endpoints = [
        ("/health", "GET", "فحص حالة السيرفر"),
        (f"/personal/{USER_ID}/test", "GET", "اختبار رابط الإشارة"),
        (f"/personal/{USER_ID}/start", "POST", "بدء المشروع كاملاً"),
        (f"/personal/{USER_ID}/webhook", "POST", "رابط الإشارة مع بيانات")
    ]
    
    print("\n🔍 اختبار حالة جميع الـ endpoints")
    print("=" * 70)
    
    for endpoint, method, description in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"📡 {description}")
        print(f"   🔗 {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json={}, timeout=10)
            
            print(f"   📈 Status: {response.status_code}")
            
            if response.status_code in [200, 400]:  # 400 مقبول للـ POST بدون بيانات
                print("   ✅ يعمل")
            else:
                print("   ❌ لا يعمل")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        print()

def test_multiple_users():
    """اختبار عدة مستخدمين"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    users = [8169000394, 123456789, 987654321]
    
    print("\n👥 اختبار عدة مستخدمين")
    print("=" * 70)
    
    for user_id in users:
        print(f"📡 اختبار المستخدم: {user_id}")
        
        # اختبار بدء المشروع
        start_url = f"{BASE_URL}/personal/{user_id}/start"
        
        try:
            response = requests.post(start_url, json={}, timeout=10)
            print(f"   🚀 بدء المشروع: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ نجح")
            else:
                print("   ❌ فشل")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        time.sleep(1)
        print()

if __name__ == "__main__":
    print("🚀 بدء اختبار النظام الكامل")
    print("=" * 80)
    print("🎯 الهدف: رابط الإشارة كبديل كامل للمشروع")
    print("=" * 80)
    
    # اختبار حالة الـ endpoints
    test_endpoint_status()
    
    # اختبار بدء المشروع
    test_full_project_start()
    
    # انتظار قليل
    print("\n⏳ انتظار 5 ثواني...")
    time.sleep(5)
    
    # اختبار رابط الإشارة
    test_webhook_with_signal()
    
    # اختبار عدة مستخدمين
    test_multiple_users()
    
    print("\n🏁 انتهى الاختبار")
    print("=" * 80)
    print("📋 تعليمات التحقق:")
    print("   1. تحقق من البوت في Telegram")
    print("   2. يجب أن تظهر رسائل ترحيب وتأكيد")
    print("   3. يجب أن يظهر رابط الإشارة الشخصي")
    print("   4. يجب أن تظهر رسالة تأكيد الصفقة")
    print("\n🔗 روابط مفيدة:")
    print("   📊 Railway Dashboard: https://railway.app/dashboard")
    print("   📋 Logs: https://railway.app/dashboard → Logs")
    print("   🏥 Health Check: https://botbybit-production.up.railway.app/health")
    print("\n🎯 النتيجة المتوقعة:")
    print("   ✅ رابط الإشارة يعمل كبديل كامل للمشروع")
    print("   ✅ كل مستخدم يحصل على تجربة كاملة")
    print("   ✅ الإشارات تُنفذ تلقائياً")
    print("   ✅ المستخدم يحصل على جميع الميزات")
