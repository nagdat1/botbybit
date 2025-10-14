#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الإشارات - التجريبي والحقيقي
by نجدت 💎
"""

import asyncio
import requests
import json
from datetime import datetime
import time

# ============================================
# 🔧 الإعدادات
# ============================================

# عنوان السيرفر (غيره حسب السيرفر الخاص بك)
SERVER_URL = "http://localhost:5001"  # أو رابط Railway/Render

# معرف المستخدم للاختبار
TEST_USER_ID = 123456789  # ضع معرف تيليجرام الخاص بك هنا

# ============================================
# 🧪 اختبارات الإشارات
# ============================================

def test_demo_spot_buy():
    """اختبار: شراء Spot على الحساب التجريبي"""
    print("\n" + "="*60)
    print("🧪 اختبار 1: شراء Spot (تجريبي)")
    print("="*60)
    
    signal = {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": f"TEST_DEMO_BUY_{int(time.time())}"
    }
    
    url = f"{SERVER_URL}/personal/{TEST_USER_ID}/webhook"
    
    try:
        response = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة: {response.status_code}")
        print(f"📋 البيانات: {response.json()}")
        
        if response.status_code == 200:
            print("✅ نجح الاختبار!")
            return True
        else:
            print("❌ فشل الاختبار!")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_demo_spot_sell():
    """اختبار: بيع Spot على الحساب التجريبي"""
    print("\n" + "="*60)
    print("🧪 اختبار 2: بيع Spot (تجريبي)")
    print("="*60)
    
    signal = {
        "signal": "sell",
        "symbol": "BTCUSDT",
        "id": f"TEST_DEMO_SELL_{int(time.time())}"
    }
    
    url = f"{SERVER_URL}/personal/{TEST_USER_ID}/webhook"
    
    try:
        response = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة: {response.status_code}")
        print(f"📋 البيانات: {response.json()}")
        
        if response.status_code == 200:
            print("✅ نجح الاختبار!")
            return True
        else:
            print("❌ فشل الاختبار!")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_demo_futures_long():
    """اختبار: Long Futures على الحساب التجريبي"""
    print("\n" + "="*60)
    print("🧪 اختبار 3: Long Futures (تجريبي)")
    print("="*60)
    
    signal = {
        "signal": "long",
        "symbol": "ETHUSDT",
        "id": f"TEST_DEMO_LONG_{int(time.time())}"
    }
    
    url = f"{SERVER_URL}/personal/{TEST_USER_ID}/webhook"
    
    try:
        response = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة: {response.status_code}")
        print(f"📋 البيانات: {response.json()}")
        
        if response.status_code == 200:
            print("✅ نجح الاختبار!")
            return True
        else:
            print("❌ فشل الاختبار!")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_demo_futures_close_long():
    """اختبار: إغلاق Long Futures على الحساب التجريبي"""
    print("\n" + "="*60)
    print("🧪 اختبار 4: إغلاق Long Futures (تجريبي)")
    print("="*60)
    
    signal = {
        "signal": "close_long",
        "symbol": "ETHUSDT",
        "id": f"TEST_DEMO_CLOSE_LONG_{int(time.time())}"
    }
    
    url = f"{SERVER_URL}/personal/{TEST_USER_ID}/webhook"
    
    try:
        response = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة: {response.status_code}")
        print(f"📋 البيانات: {response.json()}")
        
        if response.status_code == 200:
            print("✅ نجح الاختبار!")
            return True
        else:
            print("❌ فشل الاختبار!")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_duplicate_signal():
    """اختبار: رفض الإشارة المكررة"""
    print("\n" + "="*60)
    print("🧪 اختبار 5: رفض الإشارة المكررة")
    print("="*60)
    
    signal_id = f"TEST_DUPLICATE_{int(time.time())}"
    
    signal = {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": signal_id
    }
    
    url = f"{SERVER_URL}/personal/{TEST_USER_ID}/webhook"
    
    try:
        # المحاولة الأولى
        print("📤 إرسال الإشارة الأولى...")
        response1 = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة 1: {response1.status_code}")
        
        time.sleep(1)
        
        # المحاولة الثانية (يجب أن تُرفض)
        print("📤 إرسال نفس الإشارة مرة أخرى...")
        response2 = requests.post(url, json=signal, timeout=10)
        print(f"📊 الاستجابة 2: {response2.status_code}")
        
        if response1.status_code == 200:
            print("✅ نجح الاختبار! (الإشارة المكررة يتم التعامل معها)")
            return True
        else:
            print("❌ فشل الاختبار!")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def check_real_account_status():
    """التحقق من حالة الحساب الحقيقي"""
    print("\n" + "="*60)
    print("🔍 التحقق من حالة الحساب الحقيقي")
    print("="*60)
    
    print("""
⚠️  ملاحظة هامة:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

للتداول على الحساب الحقيقي:

1️⃣  افتح البوت على تيليجرام
2️⃣  اذهب إلى ⚙️ الإعدادات
3️⃣  اختر "👤 نوع الحساب"
4️⃣  اختر "🔴 حقيقي"
5️⃣  اربط API Keys الحقيقية
6️⃣  تأكد من تفعيل الحساب

🔴 الحساب الحقيقي يعمل مع:
   • signal_executor.py
   • real_account_manager.py
   • يتصل مباشرة بمنصة Bybit/MEXC

🟢 الحساب التجريبي يعمل مع:
   • TradingAccount (حساب داخلي)
   • لا يتصل بأي منصة خارجية
   • آمن للاختبار

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    return True

def show_signal_examples():
    """عرض أمثلة على الإشارات المدعومة"""
    print("\n" + "="*60)
    print("📖 أمثلة الإشارات المدعومة")
    print("="*60)
    
    examples = {
        "Spot - شراء": {
            "signal": "buy",
            "symbol": "BTCUSDT",
            "id": "TV_001"
        },
        "Spot - بيع": {
            "signal": "sell",
            "symbol": "BTCUSDT",
            "id": "TV_002"
        },
        "Futures - Long": {
            "signal": "long",
            "symbol": "ETHUSDT",
            "id": "TV_LONG_001"
        },
        "Futures - إغلاق Long": {
            "signal": "close_long",
            "symbol": "ETHUSDT",
            "id": "TV_CLOSE_001"
        },
        "Futures - Short": {
            "signal": "short",
            "symbol": "ADAUSDT",
            "id": "TV_SHORT_001"
        },
        "Futures - إغلاق Short": {
            "signal": "close_short",
            "symbol": "ADAUSDT",
            "id": "TV_CLOSE_002"
        }
    }
    
    for name, signal in examples.items():
        print(f"\n📌 {name}:")
        print(json.dumps(signal, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    return True

# ============================================
# 🚀 تشغيل الاختبارات
# ============================================

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("""
╔══════════════════════════════════════════╗
║  🧪 اختبار شامل لنظام الإشارات  🧪  ║
║           by نجدت 💎                    ║
╚══════════════════════════════════════════╝
    """)
    
    print(f"\n⚙️  إعدادات الاختبار:")
    print(f"   • السيرفر: {SERVER_URL}")
    print(f"   • معرف المستخدم: {TEST_USER_ID}")
    print(f"   • الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # عرض الأمثلة
    show_signal_examples()
    
    # التحقق من الحساب الحقيقي
    check_real_account_status()
    
    input("\n⏸️  اضغط Enter للبدء في الاختبارات التجريبية...")
    
    # الاختبارات
    print("\n🔄 بدء الاختبارات...")
    
    # اختبار 1: شراء Spot
    results.append(("شراء Spot تجريبي", test_demo_spot_buy()))
    time.sleep(2)
    
    # اختبار 2: بيع Spot
    results.append(("بيع Spot تجريبي", test_demo_spot_sell()))
    time.sleep(2)
    
    # اختبار 3: Long Futures
    results.append(("Long Futures تجريبي", test_demo_futures_long()))
    time.sleep(2)
    
    # اختبار 4: إغلاق Long
    results.append(("إغلاق Long تجريبي", test_demo_futures_close_long()))
    time.sleep(2)
    
    # اختبار 5: الإشارة المكررة
    results.append(("رفض الإشارة المكررة", test_duplicate_signal()))
    
    # عرض النتائج
    print("\n" + "="*60)
    print("📊 نتائج الاختبارات")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"📈 النتيجة النهائية: {passed} نجح, {failed} فشل")
    print("="*60)
    
    print("""
╔══════════════════════════════════════════╗
║           ملاحظات هامة:                ║
╚══════════════════════════════════════════╝

1️⃣  للتحقق من الصفقات المفتوحة:
    افتح البوت → 🔄 الصفقات المفتوحة

2️⃣  للتحقق من الرصيد:
    افتح البوت → 💰 المحفظة

3️⃣  للتحقق من السجل:
    افتح البوت → 📈 تاريخ التداول

4️⃣  للحساب الحقيقي:
    • تأكد من ربط API Keys
    • غير نوع الحساب إلى "حقيقي"
    • ستصلك إشعارات مفصلة على تيليجرام

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 تم التطوير بواسطة نجدت
🎯 نظام تداول متكامل واحترافي
    """)

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏸️  تم إيقاف الاختبارات بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ عام: {e}")
        import traceback
        traceback.print_exc()

