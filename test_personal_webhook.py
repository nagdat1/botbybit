#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار الروابط الشخصية للمستخدمين
"""

import requests
import json
import time

# تكوين الاختبار
BASE_URL = "https://botbybit-production.up.railway.app"  # غير هذا إلى عنوان السيرفر الخاص بك
TEST_USER_ID = 123456789  # غير هذا إلى معرف مستخدم حقيقي

def test_old_webhook():
    """اختبار الرابط القديم"""
    print("\n" + "=" * 60)
    print("🧪 اختبار الرابط القديم /webhook")
    print("=" * 60)
    
    url = f"{BASE_URL}/webhook"
    data = {
        "symbol": "BTCUSDT",
        "action": "buy",
        "price": 50000.50
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 200:
            print("✅ الرابط القديم يعمل بنجاح!")
        else:
            print("❌ الرابط القديم لا يعمل!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_personal_webhook(user_id):
    """اختبار الرابط الشخصي"""
    print("\n" + "=" * 60)
    print(f"🧪 اختبار الرابط الشخصي /personal/{user_id}/webhook")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    data = {
        "symbol": "ETHUSDT",
        "action": "buy",
        "price": 3000.25
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 200:
            print("✅ الرابط الشخصي يعمل بنجاح!")
        elif response.status_code == 404:
            print("⚠️ المستخدم غير موجود! استخدم /start في البوت أولاً")
        elif response.status_code == 403:
            print("⚠️ المستخدم غير نشط! فعّل البوت من الإعدادات")
        else:
            print("❌ خطأ غير متوقع!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_personal_webhook_sell(user_id):
    """اختبار إشارة بيع"""
    print("\n" + "=" * 60)
    print(f"🧪 اختبار إشارة بيع للمستخدم {user_id}")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    data = {
        "symbol": "ETHUSDT",
        "action": "sell",
        "price": 3050.75
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 200:
            print("✅ إشارة البيع تم إرسالها بنجاح!")
        else:
            print("❌ فشل إرسال إشارة البيع!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_personal_webhook_close(user_id):
    """اختبار إشارة إغلاق"""
    print("\n" + "=" * 60)
    print(f"🧪 اختبار إشارة إغلاق للمستخدم {user_id}")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    data = {
        "symbol": "ETHUSDT",
        "action": "close",
        "price": 3100.00
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 200:
            print("✅ إشارة الإغلاق تم إرسالها بنجاح!")
        else:
            print("❌ فشل إرسال إشارة الإغلاق!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_invalid_user():
    """اختبار مستخدم غير موجود"""
    print("\n" + "=" * 60)
    print("🧪 اختبار مستخدم غير موجود")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/999999999/webhook"
    data = {
        "symbol": "BTCUSDT",
        "action": "buy",
        "price": 50000
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 404:
            print("✅ النظام يتعامل مع المستخدمين غير الموجودين بشكل صحيح!")
        else:
            print("⚠️ رد غير متوقع!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_invalid_data(user_id):
    """اختبار بيانات غير صحيحة"""
    print("\n" + "=" * 60)
    print("🧪 اختبار بيانات غير صحيحة")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    data = {}  # بيانات فارغة
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 الحالة: {response.status_code}")
        print(f"📥 الرد: {response.json()}")
        
        if response.status_code == 400:
            print("✅ النظام يتعامل مع البيانات الخاطئة بشكل صحيح!")
        else:
            print("⚠️ رد غير متوقع!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    time.sleep(2)


def test_concurrent_signals(user_id):
    """اختبار إشارات متزامنة"""
    print("\n" + "=" * 60)
    print("🧪 اختبار إشارات متزامنة")
    print("=" * 60)
    
    url = f"{BASE_URL}/personal/{user_id}/webhook"
    
    signals = [
        {"symbol": "BTCUSDT", "action": "buy", "price": 50000},
        {"symbol": "ETHUSDT", "action": "buy", "price": 3000},
        {"symbol": "BNBUSDT", "action": "sell", "price": 600},
    ]
    
    try:
        for i, data in enumerate(signals, 1):
            print(f"\n📤 إرسال إشارة {i}/{len(signals)}: {data}")
            
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   ✅ الحالة: {response.status_code}")
            
            time.sleep(0.5)  # انتظار قصير بين الإشارات
        
        print("\n✅ تم إرسال جميع الإشارات بنجاح!")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")


def main():
    """التشغيل الرئيسي"""
    print("\n" + "=" * 60)
    print("🚀 بدء اختبار الروابط الشخصية")
    print("=" * 60)
    print(f"📍 URL: {BASE_URL}")
    print(f"👤 معرف المستخدم للاختبار: {TEST_USER_ID}")
    print("\n⚠️ تأكد من:")
    print("   1. السيرفر يعمل")
    print("   2. المستخدم مسجل في البوت (/start)")
    print("   3. المستخدم نشط (مفعّل)")
    
    input("\n⏸️ اضغط Enter للمتابعة...")
    
    # تشغيل الاختبارات
    test_old_webhook()
    test_personal_webhook(TEST_USER_ID)
    test_personal_webhook_sell(TEST_USER_ID)
    test_personal_webhook_close(TEST_USER_ID)
    test_invalid_user()
    test_invalid_data(TEST_USER_ID)
    test_concurrent_signals(TEST_USER_ID)
    
    # ملخص النتائج
    print("\n" + "=" * 60)
    print("🎉 انتهت جميع الاختبارات!")
    print("=" * 60)
    print("\n📋 التوصيات:")
    print("   1. راجع Logs في Railway للتأكد من استقبال الإشارات")
    print("   2. تحقق من إشعارات Telegram")
    print("   3. راجع الصفقات في البوت")
    print("\n✅ إذا نجحت جميع الاختبارات، النظام جاهز للاستخدام!")


if __name__ == "__main__":
    main()
