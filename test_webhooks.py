#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبارات للتحقق من عمل webhook الجديد
"""

import requests
import json
import time

# إعدادات الاختبار
BASE_URL = "https://botbybit-production.up.railway.app"  # عدل هذا حسب رابط Railway الخاص بك
# للاختبار المحلي: BASE_URL = "http://localhost:5000"

TEST_USER_ID = 8169000394  # ضع user_id صحيح من قاعدة البيانات

def test_old_webhook():
    """اختبار الرابط القديم"""
    print("\n" + "="*60)
    print("🧪 اختبار الرابط القديم /webhook")
    print("="*60)
    
    url = f"{BASE_URL}/webhook"
    
    # إشارة شراء
    signal = {
        "symbol": "BTCUSDT",
        "action": "buy",
        "price": 50000
    }
    
    print(f"\n📤 إرسال إشارة إلى: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ الاختبار نجح - الرابط القديم يعمل!")
            return True
        else:
            print("\n❌ الاختبار فشل - الرابط القديم لا يعمل!")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def test_personal_webhook(user_id):
    """اختبار الرابط الشخصي"""
    print("\n" + "="*60)
    print(f"🧪 اختبار الرابط الشخصي /personal/{user_id}/webhook")
    print("="*60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    
    # إشارة شراء
    signal = {
        "symbol": "ETHUSDT",
        "action": "buy",
        "price": 3000
    }
    
    print(f"\n📤 إرسال إشارة إلى: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"\n✅ الاختبار نجح - الرابط الشخصي يعمل للمستخدم {user_id}!")
            return True
        elif response.status_code == 404:
            print(f"\n⚠️ المستخدم {user_id} غير موجود في قاعدة البيانات")
            return False
        elif response.status_code == 403:
            print(f"\n⚠️ المستخدم {user_id} غير نشط")
            return False
        else:
            print(f"\n❌ الاختبار فشل - خطأ غير متوقع!")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def test_personal_webhook_invalid_user():
    """اختبار الرابط الشخصي مع مستخدم غير موجود"""
    print("\n" + "="*60)
    print("🧪 اختبار الرابط الشخصي مع مستخدم غير موجود")
    print("="*60)
    
    invalid_user_id = 999999999
    url = f"{BASE_URL}/personal/{invalid_user_id}/webhook"
    
    signal = {
        "symbol": "BTCUSDT",
        "action": "buy",
        "price": 50000
    }
    
    print(f"\n📤 إرسال إشارة إلى: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 404:
            print("\n✅ الاختبار نجح - تم اكتشاف المستخدم غير الموجود!")
            return True
        else:
            print("\n❌ الاختبار فشل - يجب أن يرجع 404!")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def test_close_signal(user_id):
    """اختبار إشارة الإغلاق"""
    print("\n" + "="*60)
    print(f"🧪 اختبار إشارة الإغلاق للمستخدم {user_id}")
    print("="*60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    
    # إشارة إغلاق
    signal = {
        "symbol": "ETHUSDT",
        "action": "close",
        "price": 3100
    }
    
    print(f"\n📤 إرسال إشارة إلى: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"\n✅ الاختبار نجح - إشارة الإغلاق تم إرسالها!")
            return True
        else:
            print(f"\n❌ الاختبار فشل!")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def test_multiple_actions(user_id):
    """اختبار أنواع مختلفة من الإشارات"""
    print("\n" + "="*60)
    print(f"🧪 اختبار أنواع مختلفة من الإشارات للمستخدم {user_id}")
    print("="*60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    
    # قائمة الإشارات للاختبار
    signals = [
        {"symbol": "BTCUSDT", "action": "buy", "price": 50000},
        {"symbol": "ETHUSDT", "action": "sell", "price": 3000},
        {"symbol": "BTCUSDT", "action": "long", "price": 50100},
        {"symbol": "ETHUSDT", "action": "short", "price": 2950},
        {"symbol": "BTCUSDT", "action": "close"},
        {"symbol": "ETHUSDT", "action": "exit"},
    ]
    
    results = []
    
    for i, signal in enumerate(signals, 1):
        print(f"\n📤 الإشارة {i}/{len(signals)}: {signal['action'].upper()} {signal['symbol']}")
        
        try:
            response = requests.post(
                url,
                json=signal,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            results.append(success)
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} Status: {response.status_code}")
            
            # انتظار قليل بين الإشارات
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
            results.append(False)
    
    # النتيجة النهائية
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 النتيجة: {success_count}/{total_count} نجحت")
    
    if success_count == total_count:
        print("✅ جميع الاختبارات نجحت!")
        return True
    else:
        print("⚠️ بعض الاختبارات فشلت")
        return False

def test_health_endpoint():
    """اختبار endpoint الصحة"""
    print("\n" + "="*60)
    print("🧪 اختبار endpoint الصحة")
    print("="*60)
    
    url = f"{BASE_URL}/health"
    
    print(f"\n📤 إرسال طلب إلى: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ السيرفر يعمل بشكل صحيح!")
            return True
        else:
            print("\n❌ مشكلة في السيرفر!")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ في الاتصال: {e}")
        print("⚠️ تأكد من أن السيرفر يعمل وأن BASE_URL صحيح")
        return False

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "🚀"*30)
    print("بدء اختبارات Webhook")
    print("🚀"*30)
    
    results = {}
    
    # اختبار الصحة أولاً
    print("\n" + "="*60)
    print("الخطوة 1: التحقق من أن السيرفر يعمل")
    print("="*60)
    results['health'] = test_health_endpoint()
    
    if not results['health']:
        print("\n❌ السيرفر لا يعمل! توقف الاختبار.")
        print("\n💡 تأكد من:")
        print("   1. أن السيرفر يعمل")
        print("   2. أن BASE_URL صحيح في ملف الاختبار")
        print(f"   3. الرابط الحالي: {BASE_URL}")
        return
    
    # الاختبارات الأخرى
    print("\n" + "="*60)
    print("الخطوة 2: اختبار الروابط")
    print("="*60)
    
    results['old_webhook'] = test_old_webhook()
    time.sleep(2)
    
    results['personal_webhook'] = test_personal_webhook(TEST_USER_ID)
    time.sleep(2)
    
    results['invalid_user'] = test_personal_webhook_invalid_user()
    time.sleep(2)
    
    results['close_signal'] = test_close_signal(TEST_USER_ID)
    time.sleep(2)
    
    results['multiple_actions'] = test_multiple_actions(TEST_USER_ID)
    
    # النتيجة النهائية
    print("\n" + "="*60)
    print("📊 ملخص النتائج")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {test_name}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 النتيجة الإجمالية: {success_count}/{total_count} اختبار نجح")
    
    if success_count == total_count:
        print("\n🎉 مبروك! جميع الاختبارات نجحت!")
    else:
        print("\n⚠️ بعض الاختبارات فشلت. راجع التفاصيل أعلاه.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\n📋 معلومات الاختبار:")
    print(f"   BASE_URL: {BASE_URL}")
    print(f"   TEST_USER_ID: {TEST_USER_ID}")
    print("\n⚠️ تأكد من تحديث BASE_URL و TEST_USER_ID في ملف الاختبار!")
    print("\n" + "-"*60)
    
    input("\n⏸️  اضغط Enter للمتابعة أو Ctrl+C للإلغاء...")
    
    run_all_tests()

