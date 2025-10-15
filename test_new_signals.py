#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار شامل للإشارات الجديدة
يختبر جميع أنواع الإشارات المدعومة مع التنسيق الجديد
"""

import requests
import json
import time
from datetime import datetime

# ===== الإعدادات =====
# قم بتغيير هذه القيم حسب إعدادك
WEBHOOK_URL = "http://localhost:5000/webhook"  # أو رابط Railway/Render
PERSONAL_WEBHOOK_URL = "http://localhost:5000/personal/{user_id}/webhook"  # استبدل {user_id} بمعرف المستخدم الحقيقي
USER_ID = 123456789  # ضع معرف المستخدم الخاص بك

# ===== الإشارات للاختبار =====

# إشارات الشراء والبيع
BUY_SELL_SIGNALS = [
    {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": "TEST_B01"
    },
    {
        "signal": "sell",
        "symbol": "BTCUSDT",
        "id": "TEST_S01"
    }
]

# إشارات الإغلاق
CLOSE_SIGNALS = [
    {
        "signal": "close",
        "symbol": "BTCUSDT",
        "id": "TEST_C01"
    }
]

# إشارات الإغلاق الجزئي
PARTIAL_CLOSE_SIGNALS = [
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 50,
        "id": "TEST_PC01"
    },
    {
        "signal": "partial_close",
        "symbol": "ETHUSDT",
        "percentage": 25,
        "id": "TEST_PC02"
    },
    {
        "signal": "partial_close",
        "symbol": "SOLUSDT",
        "percentage": 75,
        "id": "TEST_PC03"
    }
]

# جميع الإشارات
ALL_SIGNALS = BUY_SELL_SIGNALS + CLOSE_SIGNALS + PARTIAL_CLOSE_SIGNALS


def send_signal(signal_data, webhook_url=None, use_personal=False, user_id=None):
    """
    إرسال إشارة إلى البوت
    
    Args:
        signal_data: بيانات الإشارة
        webhook_url: رابط الـ webhook (اختياري)
        use_personal: استخدام الـ webhook الشخصي
        user_id: معرف المستخدم (مطلوب إذا كان use_personal=True)
        
    Returns:
        استجابة السيرفر
    """
    try:
        # تحديد الرابط
        if use_personal and user_id:
            url = PERSONAL_WEBHOOK_URL.format(user_id=user_id)
        else:
            url = webhook_url or WEBHOOK_URL
        
        # إرسال الإشارة
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=signal_data, headers=headers)
        
        # طباعة النتيجة
        print(f"\n{'='*80}")
        print(f"📤 إرسال إشارة: {signal_data['signal'].upper()} {signal_data['symbol']}")
        print(f"🔗 الرابط: {url}")
        print(f"📋 البيانات: {json.dumps(signal_data, indent=2, ensure_ascii=False)}")
        print(f"📥 الاستجابة: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print(f"✅ نجح الإرسال!")
        else:
            print(f"❌ فشل الإرسال!")
        
        print(f"{'='*80}\n")
        
        return response
        
    except Exception as e:
        print(f"❌ خطأ في إرسال الإشارة: {e}")
        return None


def test_signal_converter():
    """اختبار محول الإشارات"""
    print("\n" + "="*80)
    print("🧪 اختبار محول الإشارات")
    print("="*80)
    
    try:
        from signal_converter import convert_simple_signal, validate_simple_signal
        
        test_signals = [
            {"signal": "buy", "symbol": "BTCUSDT", "id": "TEST_001"},
            {"signal": "long", "symbol": "ETHUSDT", "id": "TEST_002"},
            {"signal": "close_short", "symbol": "SOLUSDT", "id": "TEST_003"}
        ]
        
        test_user_settings = {
            'trade_amount': 100.0,
            'leverage': 10,
            'exchange': 'bybit',
            'account_type': 'demo',
            'market_type': 'spot'
        }
        
        for signal in test_signals:
            print(f"\n📥 اختبار: {signal}")
            
            # التحقق من صحة الإشارة
            is_valid, message = validate_simple_signal(signal)
            print(f"✅ صحة الإشارة: {is_valid} - {message}")
            
            if is_valid:
                # تحويل الإشارة
                converted = convert_simple_signal(signal, test_user_settings)
                if converted:
                    print(f"📤 الإشارة المحولة:")
                    for key, value in converted.items():
                        if key != 'original_signal':
                            print(f"   {key}: {value}")
                else:
                    print(f"❌ فشل التحويل")
            
            print("-" * 80)
        
        print("\n✅ اكتمل اختبار محول الإشارات\n")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار محول الإشارات: {e}")
        import traceback
        traceback.print_exc()


def test_all_signals(webhook_url=None, use_personal=False, user_id=None, delay=2):
    """
    اختبار جميع أنواع الإشارات
    
    Args:
        webhook_url: رابط الـ webhook
        use_personal: استخدام webhook شخصي
        user_id: معرف المستخدم
        delay: التأخير بين الإشارات (بالثواني)
    """
    print("\n" + "="*80)
    print("🚀 بدء اختبار جميع أنواع الإشارات")
    print("="*80)
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if use_personal and user_id:
        print(f"👤 المستخدم: {user_id}")
    
    print(f"🔗 الرابط: {webhook_url or WEBHOOK_URL}")
    print(f"⏱️ التأخير بين الإشارات: {delay} ثانية")
    print("="*80)
    
    results = {
        'success': 0,
        'failed': 0,
        'total': len(ALL_SIGNALS)
    }
    
    for i, signal in enumerate(ALL_SIGNALS, 1):
        print(f"\n[{i}/{results['total']}] اختبار إشارة: {signal['signal'].upper()} {signal['symbol']}")
        
        response = send_signal(
            signal, 
            webhook_url=webhook_url,
            use_personal=use_personal,
            user_id=user_id
        )
        
        if response and response.status_code == 200:
            results['success'] += 1
        else:
            results['failed'] += 1
        
        # انتظار قبل الإشارة التالية
        if i < results['total']:
            print(f"⏳ انتظار {delay} ثانية...")
            time.sleep(delay)
    
    # عرض النتائج
    print("\n" + "="*80)
    print("📊 ملخص النتائج")
    print("="*80)
    print(f"✅ نجح: {results['success']}/{results['total']}")
    print(f"❌ فشل: {results['failed']}/{results['total']}")
    print(f"📈 نسبة النجاح: {(results['success']/results['total']*100):.1f}%")
    print("="*80)


def test_buy_sell_only(webhook_url=None, use_personal=False, user_id=None):
    """اختبار إشارات Buy و Sell فقط"""
    print("\n🟢🔴 اختبار إشارات Buy و Sell")
    
    for signal in BUY_SELL_SIGNALS:
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        time.sleep(2)


def test_close_only(webhook_url=None, use_personal=False, user_id=None):
    """اختبار إشارات Close فقط"""
    print("\n⚪ اختبار إشارات Close")
    
    for signal in CLOSE_SIGNALS:
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        time.sleep(2)


def test_partial_close_only(webhook_url=None, use_personal=False, user_id=None):
    """اختبار إشارات الإغلاق الجزئي فقط"""
    print("\n📊 اختبار إشارات الإغلاق الجزئي")
    
    for signal in PARTIAL_CLOSE_SIGNALS:
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        time.sleep(2)


def test_invalid_signals(webhook_url=None):
    """اختبار إشارات غير صحيحة للتأكد من معالجة الأخطاء"""
    print("\n❌ اختبار إشارات غير صحيحة")
    
    invalid_signals = [
        {"signal": "invalid_type", "symbol": "BTCUSDT", "id": "TEST_INV_001"},  # نوع غير صحيح
        {"symbol": "BTCUSDT", "id": "TEST_INV_002"},  # بدون signal
        {"signal": "buy", "id": "TEST_INV_003"},  # بدون symbol
        {"signal": "buy", "symbol": "BTC", "id": "TEST_INV_004"},  # رمز قصير جداً
    ]
    
    for signal in invalid_signals:
        print(f"\n📤 اختبار إشارة غير صحيحة: {signal}")
        send_signal(signal, webhook_url=webhook_url)
        time.sleep(1)


def interactive_test():
    """اختبار تفاعلي"""
    print("\n" + "="*80)
    print("🎯 اختبار تفاعلي للإشارات الجديدة")
    print("="*80)
    
    # اختيار نوع الاختبار
    print("\nاختر نوع الاختبار:")
    print("1. اختبار محول الإشارات فقط (بدون إرسال)")
    print("2. اختبار جميع الإشارات (Buy, Sell, Close, Partial)")
    print("3. اختبار Buy و Sell فقط")
    print("4. اختبار Close فقط")
    print("5. اختبار Partial Close فقط")
    print("6. اختبار إشارات غير صحيحة")
    print("7. اختبار إشارة واحدة مخصصة")
    print("0. خروج")
    
    choice = input("\nأدخل اختيارك (0-7): ").strip()
    
    if choice == "0":
        print("👋 إلى اللقاء!")
        return
    
    # إعدادات الاتصال
    if choice != "1":
        use_custom_url = input("\nهل تريد استخدام رابط مخصص؟ (y/n): ").strip().lower() == 'y'
        webhook_url = None
        use_personal = False
        user_id = None
        
        if use_custom_url:
            webhook_url = input("أدخل رابط الـ Webhook: ").strip()
        
        use_personal_webhook = input("هل تريد استخدام webhook شخصي؟ (y/n): ").strip().lower() == 'y'
        if use_personal_webhook:
            use_personal = True
            user_id = int(input("أدخل معرف المستخدم: ").strip())
    
    # تنفيذ الاختبار المختار
    if choice == "1":
        test_signal_converter()
    elif choice == "2":
        test_all_signals(webhook_url, use_personal, user_id)
    elif choice == "3":
        test_buy_sell_only(webhook_url, use_personal, user_id)
    elif choice == "4":
        test_close_only(webhook_url, use_personal, user_id)
    elif choice == "5":
        test_partial_close_only(webhook_url, use_personal, user_id)
    elif choice == "6":
        test_invalid_signals(webhook_url)
    elif choice == "7":
        # اختبار مخصص
        print("\nأنواع الإشارات المدعومة:")
        print("🟢 buy - شراء")
        print("🔴 sell - بيع")
        print("⚪ close - إغلاق كامل")
        print("🟡 partial_close - إغلاق جزئي")
        
        signal_type = input("\nأدخل نوع الإشارة: ").strip().lower()
        symbol = input("أدخل رمز العملة (مثل BTCUSDT): ").strip().upper()
        signal_id = input("أدخل معرف الإشارة (اختياري): ").strip()
        
        custom_signal = {
            "signal": signal_type,
            "symbol": symbol,
            "id": signal_id or f"CUSTOM_{int(time.time())}"
        }
        
        # إذا كان إغلاق جزئي، أضف النسبة
        if 'partial_close' in signal_type:
            percentage = input("أدخل النسبة المئوية (1-100، افتراضي 50): ").strip()
            if percentage:
                custom_signal['percentage'] = float(percentage)
            else:
                custom_signal['percentage'] = 50
        
        send_signal(custom_signal, webhook_url, use_personal, user_id)
    else:
        print("❌ اختيار غير صحيح!")


def main():
    """الدالة الرئيسية"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🧪 اختبار الإشارات الجديدة - Trading Bot            ║
║                                                                  ║
║  هذا السكريبت يختبر جميع أنواع الإشارات الجديدة المدعومة    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # التحقق من توفر المكتبات
    try:
        import requests
        print("✅ مكتبة requests متوفرة")
    except ImportError:
        print("❌ مكتبة requests غير متوفرة. قم بتثبيتها باستخدام:")
        print("   pip install requests")
        return
    
    # بدء الاختبار التفاعلي
    interactive_test()


if __name__ == "__main__":
    main()

