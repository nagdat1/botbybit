#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تنفيذ الإشارة مع التشخيص المفصل
"""

import requests
import json
import time

def test_signal_execution():
    """اختبار تنفيذ الإشارة مع التشخيص"""
    
    # إعدادات الاختبار
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print("🧪 اختبار تنفيذ الإشارة مع التشخيص")
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
        # إرسال الطلب
        print("⏳ إرسال الطلب...")
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
            
            print("\n🔍 التحقق من تنفيذ الصفقة:")
            print("   📋 تحقق من البوت في Telegram")
            print("   📋 تحقق من سجلات Railway")
            print("   📋 يجب أن تظهر رسالة تأكيد الصفقة")
            
        else:
            print("❌ فشل في إرسال الإشارة")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def test_multiple_signals():
    """اختبار عدة إشارات"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    signals = [
        {"symbol": "BTCUSDT", "action": "buy"},
        {"symbol": "ETHUSDT", "action": "sell"},
        {"symbol": "ADAUSDT", "action": "buy"}
    ]
    
    print(f"\n🧪 اختبار {len(signals)} إشارات متتالية")
    print("=" * 70)
    
    for i, signal in enumerate(signals, 1):
        print(f"📡 الإشارة {i}: {signal['symbol']} {signal['action']}")
        
        try:
            response = requests.post(
                webhook_url,
                json=signal,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ نجح")
            else:
                print(f"   ❌ فشل - {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ خطأ - {e}")
        
        # انتظار ثانية بين الإشارات
        time.sleep(1)
        print()

def test_health_check():
    """اختبار حالة السيرفر"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    health_url = f"{BASE_URL}/health"
    
    print("\n🏥 اختبار حالة السيرفر")
    print("=" * 70)
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
    print("🚀 بدء اختبار تنفيذ الإشارة")
    print("=" * 80)
    
    # اختبار حالة السيرفر
    test_health_check()
    
    # اختبار إشارة واحدة
    test_signal_execution()
    
    # اختبار عدة إشارات
    test_multiple_signals()
    
    print("\n🏁 انتهى الاختبار")
    print("=" * 80)
    print("📋 تعليمات التحقق:")
    print("   1. تحقق من البوت في Telegram")
    print("   2. يجب أن تظهر رسالة تأكيد الصفقة")
    print("   3. تحقق من سجلات Railway لمزيد من التفاصيل")
    print("   4. تحقق من الصفقات المفتوحة في البوت")
    print("\n🔗 روابط مفيدة:")
    print("   📊 Railway Dashboard: https://railway.app/dashboard")
    print("   📋 Logs: https://railway.app/dashboard → Logs")
