#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح الرابط الشخصي ليعمل بنفس طريقة الرابط الأساسي
"""

import requests
import json
import time

def test_personal_vs_main_webhook():
    """مقارنة بين الرابط الشخصي والرابط الأساسي"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    # الروابط
    main_webhook = f"{BASE_URL}/webhook"
    personal_webhook = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    # إشارة اختبار
    test_signal = {
        "symbol": "BTCUSDT",
        "action": "buy"
    }
    
    print("🔍 مقارنة بين الرابط الشخصي والرابط الأساسي")
    print("=" * 70)
    print(f"🔗 الرابط الأساسي: {main_webhook}")
    print(f"🔗 الرابط الشخصي: {personal_webhook}")
    print(f"📡 الإشارة: {json.dumps(test_signal, indent=2)}")
    print("-" * 70)
    
    # اختبار الرابط الأساسي
    print("📡 اختبار الرابط الأساسي...")
    try:
        start_time = time.time()
        main_response = requests.post(
            main_webhook,
            json=test_signal,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        main_time = time.time() - start_time
        
        print(f"   ⏱️ وقت الاستجابة: {main_time:.2f} ثانية")
        print(f"   📈 Status Code: {main_response.status_code}")
        print(f"   📄 Response: {main_response.text}")
        
        if main_response.status_code == 200:
            print("   ✅ نجح الرابط الأساسي")
            main_success = True
        else:
            print("   ❌ فشل الرابط الأساسي")
            main_success = False
            
    except Exception as e:
        print(f"   ❌ خطأ في الرابط الأساسي: {e}")
        main_success = False
    
    print()
    
    # اختبار الرابط الشخصي
    print("📡 اختبار الرابط الشخصي...")
    try:
        start_time = time.time()
        personal_response = requests.post(
            personal_webhook,
            json=test_signal,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        personal_time = time.time() - start_time
        
        print(f"   ⏱️ وقت الاستجابة: {personal_time:.2f} ثانية")
        print(f"   📈 Status Code: {personal_response.status_code}")
        print(f"   📄 Response: {personal_response.text}")
        
        if personal_response.status_code == 200:
            print("   ✅ نجح الرابط الشخصي")
            personal_success = True
        else:
            print("   ❌ فشل الرابط الشخصي")
            personal_success = False
            
    except Exception as e:
        print(f"   ❌ خطأ في الرابط الشخصي: {e}")
        personal_success = False
    
    print()
    print("📊 النتائج:")
    print("=" * 70)
    print(f"🔗 الرابط الأساسي: {'✅ نجح' if main_success else '❌ فشل'}")
    print(f"🔗 الرابط الشخصي: {'✅ نجح' if personal_success else '❌ فشل'}")
    
    if main_success and personal_success:
        print("🎉 كلا الرابطين يعمل بنجاح!")
        print("✅ الإصلاح نجح!")
    elif main_success and not personal_success:
        print("❌ الرابط الشخصي لا يزال لا يعمل")
        print("🔧 يحتاج إصلاح إضافي")
    elif not main_success and personal_success:
        print("⚠️ الرابط الشخصي يعمل لكن الأساسي لا يعمل")
    else:
        print("❌ كلا الرابطين لا يعمل")
        print("🔧 مشكلة في السيرفر")
    
    return main_success and personal_success

def test_multiple_personal_signals():
    """اختبار عدة إشارات على الرابط الشخصي"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    USER_ID = 8169000394
    
    personal_webhook = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    test_signals = [
        {"symbol": "BTCUSDT", "action": "buy"},
        {"symbol": "ETHUSDT", "action": "sell"},
        {"symbol": "ADAUSDT", "action": "buy"},
        {"symbol": "SOLUSDT", "action": "sell"}
    ]
    
    print("\n🎯 اختبار عدة إشارات على الرابط الشخصي")
    print("=" * 70)
    print(f"🔗 الرابط: {personal_webhook}")
    print("-" * 70)
    
    results = []
    
    for i, signal in enumerate(test_signals, 1):
        print(f"📡 اختبار {i}/{len(test_signals)}: {signal['symbol']} {signal['action']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                personal_webhook,
                json=signal,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time
            
            print(f"   ⏱️ وقت الاستجابة: {response_time:.2f} ثانية")
            print(f"   📈 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ نجح")
                results.append(True)
            else:
                print("   ❌ فشل")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
            results.append(False)
        
        time.sleep(2)  # انتظار بين الإشارات
        print()
    
    success_count = sum(results)
    print(f"📊 النتائج: {success_count}/{len(test_signals)} نجح ({success_count/len(test_signals)*100:.1f}%)")
    
    return success_count == len(test_signals)

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار إصلاح الرابط الشخصي")
    print("=" * 80)
    print("🎯 الهدف: التأكد من أن الرابط الشخصي يعمل بنفس طريقة الرابط الأساسي")
    print("=" * 80)
    
    # اختبار المقارنة
    comparison_success = test_personal_vs_main_webhook()
    
    # انتظار قليل
    print("\n⏳ انتظار 5 ثواني...")
    time.sleep(5)
    
    # اختبار عدة إشارات
    multiple_success = test_multiple_personal_signals()
    
    print("\n🏁 النتائج النهائية:")
    print("=" * 80)
    
    if comparison_success and multiple_success:
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ الرابط الشخصي يعمل بنفس طريقة الرابط الأساسي")
        print("📋 تعليمات التحقق:")
        print("   1. تحقق من البوت في Telegram")
        print("   2. يجب أن تظهر رسائل تأكيد")
        print("   3. يجب أن تظهر رسائل تأكيد الصفقات")
    else:
        print("❌ بعض الاختبارات فشلت")
        if not comparison_success:
            print("🔧 مشكلة في المقارنة بين الروابط")
        if not multiple_success:
            print("🔧 مشكلة في اختبار عدة إشارات")
    
    print("\n🔗 روابط مفيدة:")
    print("   📊 Railway Dashboard: https://railway.app/dashboard")
    print("   🏥 Health Check: https://botbybit-production.up.railway.app/health")

if __name__ == "__main__":
    main()
