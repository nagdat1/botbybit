#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الـ webhook الشخصي
"""

import requests
import json
import time
from datetime import datetime

# إعدادات الاختبار
BASE_URL = "https://botbybit-production.up.railway.app"
TEST_USER_ID = 8169000394

def print_section(title):
    """طباعة عنوان قسم"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_health_check():
    """اختبار 1: فحص صحة التطبيق"""
    print_section("🏥 اختبار 1: فحص صحة التطبيق")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ التطبيق يعمل بشكل صحيح")
            return True
        else:
            print("❌ التطبيق لا يعمل بشكل صحيح")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_personal_webhook_get():
    """اختبار 2: اختبار الرابط الشخصي (GET)"""
    print_section(f"🔍 اختبار 2: اختبار الرابط الشخصي (GET) للمستخدم {TEST_USER_ID}")
    
    try:
        url = f"{BASE_URL}/personal/{TEST_USER_ID}/test"
        print(f"🔗 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ الرابط الشخصي يعمل بشكل صحيح")
            return True
        else:
            print("❌ الرابط الشخصي لا يعمل")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_personal_webhook_post_buy():
    """اختبار 3: إرسال إشارة شراء"""
    print_section(f"📡 اختبار 3: إرسال إشارة شراء للمستخدم {TEST_USER_ID}")
    
    try:
        url = f"{BASE_URL}/personal/{TEST_USER_ID}/webhook"
        print(f"🔗 URL: {url}")
        
        signal_data = {
            "symbol": "BTCUSDT",
            "action": "buy"
        }
        
        print(f"📤 البيانات المرسلة: {json.dumps(signal_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ تم إرسال إشارة الشراء بنجاح")
                print(f"👤 User ID: {data.get('user_id')}")
                print(f"📊 Data: {data.get('data')}")
                return True
            else:
                print("❌ فشل إرسال إشارة الشراء")
                return False
        else:
            print("❌ خطأ في الاستجابة")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_personal_webhook_post_sell():
    """اختبار 4: إرسال إشارة بيع"""
    print_section(f"📡 اختبار 4: إرسال إشارة بيع للمستخدم {TEST_USER_ID}")
    
    try:
        url = f"{BASE_URL}/personal/{TEST_USER_ID}/webhook"
        print(f"🔗 URL: {url}")
        
        signal_data = {
            "symbol": "ETHUSDT",
            "action": "sell"
        }
        
        print(f"📤 البيانات المرسلة: {json.dumps(signal_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ تم إرسال إشارة البيع بنجاح")
                print(f"👤 User ID: {data.get('user_id')}")
                print(f"📊 Data: {data.get('data')}")
                return True
            else:
                print("❌ فشل إرسال إشارة البيع")
                return False
        else:
            print("❌ خطأ في الاستجابة")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_multiple_users():
    """اختبار 5: اختبار عدة مستخدمين"""
    print_section("👥 اختبار 5: اختبار عدة مستخدمين")
    
    users = [
        {"id": 8169000394, "symbol": "BTCUSDT", "action": "buy"},
        {"id": 123456789, "symbol": "ETHUSDT", "action": "sell"},
        {"id": 987654321, "symbol": "ADAUSDT", "action": "buy"}
    ]
    
    results = []
    
    for user in users:
        print(f"\n📡 اختبار المستخدم {user['id']}")
        print(f"   🔹 الرمز: {user['symbol']}")
        print(f"   🔹 الإجراء: {user['action']}")
        
        try:
            url = f"{BASE_URL}/personal/{user['id']}/webhook"
            signal_data = {
                "symbol": user['symbol'],
                "action": user['action']
            }
            
            response = requests.post(
                url,
                json=signal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ نجح")
                results.append(True)
            else:
                print(f"   ❌ فشل - Status Code: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
            results.append(False)
        
        time.sleep(2)  # انتظار بين الطلبات
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 النتائج: {success_count}/{total_count} نجح")
    
    return success_count == total_count

def test_invalid_data():
    """اختبار 6: اختبار بيانات غير صحيحة"""
    print_section(f"⚠️ اختبار 6: اختبار بيانات غير صحيحة")
    
    test_cases = [
        {"name": "بيانات فارغة", "data": {}},
        {"name": "رمز فقط", "data": {"symbol": "BTCUSDT"}},
        {"name": "إجراء فقط", "data": {"action": "buy"}},
        {"name": "رمز غير صحيح", "data": {"symbol": "INVALID", "action": "buy"}},
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 اختبار: {test_case['name']}")
        print(f"   📤 البيانات: {test_case['data']}")
        
        try:
            url = f"{BASE_URL}/personal/{TEST_USER_ID}/webhook"
            response = requests.post(
                url,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ تم قبول البيانات (قد يكون هذا متوقع أو غير متوقع)")
            else:
                print(f"   ⚠️ تم رفض البيانات")
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        time.sleep(1)
    
    return True

def test_main_webhook():
    """اختبار 7: اختبار الرابط الأساسي"""
    print_section("🌐 اختبار 7: اختبار الرابط الأساسي")
    
    try:
        url = f"{BASE_URL}/webhook"
        print(f"🔗 URL: {url}")
        
        signal_data = {
            "symbol": "BTCUSDT",
            "action": "buy"
        }
        
        print(f"📤 البيانات المرسلة: {json.dumps(signal_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ الرابط الأساسي يعمل بشكل صحيح")
            return True
        else:
            print("❌ الرابط الأساسي لا يعمل")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*80)
    print("  🧪 اختبار شامل لنظام الـ webhook الشخصي")
    print("="*80)
    print(f"🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"👤 Test User ID: {TEST_USER_ID}")
    
    # تشغيل الاختبارات
    results = {
        "health_check": test_health_check(),
        "personal_webhook_get": test_personal_webhook_get(),
        "personal_webhook_post_buy": test_personal_webhook_post_buy(),
    }
    
    # انتظار قليل بين الاختبارات
    print("\n⏳ انتظار 5 ثواني...")
    time.sleep(5)
    
    results["personal_webhook_post_sell"] = test_personal_webhook_post_sell()
    
    # انتظار قليل
    print("\n⏳ انتظار 5 ثواني...")
    time.sleep(5)
    
    results["multiple_users"] = test_multiple_users()
    results["invalid_data"] = test_invalid_data()
    results["main_webhook"] = test_main_webhook()
    
    # عرض النتائج النهائية
    print_section("📊 النتائج النهائية")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("الاختبارات:")
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"  {test_name}: {status}")
    
    print(f"\n📈 الإجمالي: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ النظام يعمل بشكل مثالي!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} اختبار(ات) فشل(ت)")
        print("🔧 يحتاج فحص إضافي")
    
    print("\n📋 الخطوات التالية:")
    print("  1. تحقق من البوت في Telegram")
    print("  2. تحقق من الـ logs في Railway")
    print("  3. تحقق من تنفيذ الصفقات")
    
    print("\n🔗 روابط مفيدة:")
    print(f"  📊 Railway Dashboard: https://railway.app/dashboard")
    print(f"  🏥 Health Check: {BASE_URL}/health")
    print(f"  🔗 Personal Webhook Test: {BASE_URL}/personal/{TEST_USER_ID}/test")
    print(f"  🔗 Personal Webhook: {BASE_URL}/personal/{TEST_USER_ID}/webhook")

if __name__ == "__main__":
    main()
