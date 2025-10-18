#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام ربط الصفقات بالـ ID
يختبر جميع الوظائف الجديدة للنظام
"""

import requests
import json
import time
from datetime import datetime

# ===== الإعدادات =====
WEBHOOK_URL = "http://localhost:5000/webhook"
PERSONAL_WEBHOOK_URL = "http://localhost:5000/personal/{user_id}/webhook"
USER_ID = 123456789  # ضع معرف المستخدم الخاص بك

# ===== إشارات الاختبار مع الـ ID =====

# سيناريو كامل: شراء ثم TP1, TP2, TP3, SL
COMPLETE_SCENARIO = [
    {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": "SCENARIO_001"
    },
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 25,
        "id": "SCENARIO_TP1"
    },
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 50,
        "id": "SCENARIO_TP2"
    },
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 25,
        "id": "SCENARIO_TP3"
    },
    {
        "signal": "close",
        "symbol": "BTCUSDT",
        "id": "SCENARIO_SL"
    }
]

# سيناريو متعدد الصفقات على نفس الرمز
MULTIPLE_POSITIONS_SCENARIO = [
    {
        "signal": "buy",
        "symbol": "ETHUSDT",
        "id": "MULTI_001"
    },
    {
        "signal": "buy",
        "symbol": "ETHUSDT",
        "id": "MULTI_002"
    },
    {
        "signal": "partial_close",
        "symbol": "ETHUSDT",
        "percentage": 50,
        "id": "MULTI_TP1"
    }
]

# سيناريو صفقات مختلفة على رموز مختلفة
DIFFERENT_SYMBOLS_SCENARIO = [
    {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": "BTC_001"
    },
    {
        "signal": "buy",
        "symbol": "ETHUSDT",
        "id": "ETH_001"
    },
    {
        "signal": "buy",
        "symbol": "SOLUSDT",
        "id": "SOL_001"
    },
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 30,
        "id": "BTC_TP1"
    },
    {
        "signal": "close",
        "symbol": "ETHUSDT",
        "id": "ETH_CLOSE"
    }
]

# إشارات بدون ID (للاختبار المتوافق مع النظام القديم)
NO_ID_SIGNALS = [
    {
        "signal": "buy",
        "symbol": "ADAUSDT"
    },
    {
        "signal": "close",
        "symbol": "ADAUSDT"
    }
]

# إشارات غير صحيحة للاختبار
INVALID_SIGNALS = [
    {
        "signal": "buy",
        "symbol": "BTCUSDT",
        "id": ""  # ID فارغ
    },
    {
        "signal": "partial_close",
        "symbol": "BTCUSDT",
        "percentage": 150,  # نسبة غير صحيحة
        "id": "INVALID_001"
    },
    {
        "signal": "close",
        "symbol": "NONEXISTENT",  # رمز غير موجود
        "id": "INVALID_002"
    }
]


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
        if 'id' in signal_data:
            print(f"🆔 Signal ID: {signal_data['id']}")
        if 'percentage' in signal_data:
            print(f"📊 النسبة: {signal_data['percentage']}%")
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
    """اختبار محول الإشارات مع الـ ID"""
    print("\n" + "="*80)
    print("🧪 اختبار محول الإشارات مع الـ ID")
    print("="*80)
    
    try:
        from signal_converter import convert_simple_signal, validate_simple_signal
        
        test_signals = [
            {"signal": "buy", "symbol": "BTCUSDT", "id": "TEST_001"},
            {"signal": "partial_close", "symbol": "ETHUSDT", "percentage": 30, "id": "TEST_002"},
            {"signal": "close", "symbol": "SOLUSDT", "id": "TEST_003"},
            {"signal": "buy", "symbol": "ADAUSDT"},  # بدون ID
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
                    
                    # التحقق من وجود الـ ID
                    if converted.get('has_signal_id'):
                        print(f"🆔 ✅ الإشارة مرتبطة بالـ ID: {converted.get('signal_id')}")
                    else:
                        print(f"⚠️ الإشارة بدون ID - النظام القديم")
                else:
                    print(f"❌ فشل التحويل")
            
            print("-" * 80)
        
        print("\n✅ اكتمل اختبار محول الإشارات\n")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار محول الإشارات: {e}")
        import traceback
        traceback.print_exc()


def test_signal_position_manager():
    """اختبار مدير الصفقات المرتبطة بالـ ID"""
    print("\n" + "="*80)
    print("🧪 اختبار مدير الصفقات المرتبطة بالـ ID")
    print("="*80)
    
    try:
        from signal_position_manager import signal_position_manager
        
        test_signal_id = "TEST_POSITION_001"
        test_user_id = 123456789
        test_symbol = "BTCUSDT"
        
        print(f"\n📊 اختبار إنشاء صفقة:")
        print(f"Signal ID: {test_signal_id}")
        print(f"User ID: {test_user_id}")
        print(f"Symbol: {test_symbol}")
        
        # إنشاء صفقة اختبار
        success = signal_position_manager.create_position(
            signal_id=test_signal_id,
            user_id=test_user_id,
            symbol=test_symbol,
            side="Buy",
            entry_price=50000.0,
            quantity=0.001,
            exchange="bybit",
            market_type="spot",
            order_id="TEST_ORDER_001"
        )
        
        print(f"✅ نتيجة الإنشاء: {success}")
        
        if success:
            # الحصول على الصفقة
            position = signal_position_manager.get_position(test_signal_id, test_user_id, test_symbol)
            print(f"📊 الصفقة المنشأة: {position}")
            
            # اختبار الإغلاق الجزئي
            print(f"\n🟡 اختبار الإغلاق الجزئي 50%:")
            success, message = signal_position_manager.partial_close_position(
                test_signal_id, test_user_id, test_symbol, 50
            )
            print(f"✅ النتيجة: {success} - {message}")
            
            # اختبار الإغلاق الكامل
            print(f"\n⚪ اختبار الإغلاق الكامل:")
            success = signal_position_manager.close_position(test_signal_id, test_user_id, test_symbol)
            print(f"✅ النتيجة: {success}")
            
            # اختبار ملخص الصفقات
            print(f"\n📊 اختبار ملخص الصفقات:")
            summary = signal_position_manager.get_position_summary(test_user_id)
            print(f"📋 الملخص: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        
        print("\n✅ اكتمل اختبار مدير الصفقات\n")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار مدير الصفقات: {e}")
        import traceback
        traceback.print_exc()


def test_complete_scenario(webhook_url=None, use_personal=False, user_id=None, delay=3):
    """
    اختبار سيناريو كامل: شراء ثم TP1, TP2, TP3, SL
    
    Args:
        webhook_url: رابط الـ webhook
        use_personal: استخدام webhook شخصي
        user_id: معرف المستخدم
        delay: التأخير بين الإشارات (بالثواني)
    """
    print("\n" + "="*80)
    print("🎯 اختبار سيناريو كامل مع الـ ID")
    print("="*80)
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🆔 Signal ID: SCENARIO_001")
    print(f"🔗 الرابط: {webhook_url or WEBHOOK_URL}")
    print(f"⏱️ التأخير بين الإشارات: {delay} ثانية")
    print("="*80)
    
    results = {
        'success': 0,
        'failed': 0,
        'total': len(COMPLETE_SCENARIO)
    }
    
    for i, signal in enumerate(COMPLETE_SCENARIO, 1):
        print(f"\n[{i}/{results['total']}] خطوة {i}: {signal['signal'].upper()} {signal['symbol']}")
        if 'id' in signal:
            print(f"🆔 Signal ID: {signal['id']}")
        if 'percentage' in signal:
            print(f"📊 النسبة: {signal['percentage']}%")
        
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
    print("📊 ملخص النتائج - السيناريو الكامل")
    print("="*80)
    print(f"✅ نجح: {results['success']}/{results['total']}")
    print(f"❌ فشل: {results['failed']}/{results['total']}")
    print(f"📈 نسبة النجاح: {(results['success']/results['total']*100):.1f}%")
    print("="*80)


def test_multiple_positions_scenario(webhook_url=None, use_personal=False, user_id=None, delay=2):
    """اختبار سيناريو صفقات متعددة على نفس الرمز"""
    print("\n" + "="*80)
    print("🔄 اختبار صفقات متعددة على نفس الرمز")
    print("="*80)
    
    for i, signal in enumerate(MULTIPLE_POSITIONS_SCENARIO, 1):
        print(f"\n[{i}/{len(MULTIPLE_POSITIONS_SCENARIO)}] {signal['signal'].upper()} {signal['symbol']}")
        print(f"🆔 Signal ID: {signal['id']}")
        
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        
        if i < len(MULTIPLE_POSITIONS_SCENARIO):
            time.sleep(delay)


def test_different_symbols_scenario(webhook_url=None, use_personal=False, user_id=None, delay=2):
    """اختبار سيناريو صفقات مختلفة على رموز مختلفة"""
    print("\n" + "="*80)
    print("💎 اختبار صفقات مختلفة على رموز مختلفة")
    print("="*80)
    
    for i, signal in enumerate(DIFFERENT_SYMBOLS_SCENARIO, 1):
        print(f"\n[{i}/{len(DIFFERENT_SYMBOLS_SCENARIO)}] {signal['signal'].upper()} {signal['symbol']}")
        print(f"🆔 Signal ID: {signal['id']}")
        
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        
        if i < len(DIFFERENT_SYMBOLS_SCENARIO):
            time.sleep(delay)


def test_no_id_signals(webhook_url=None, use_personal=False, user_id=None):
    """اختبار إشارات بدون ID (التوافق مع النظام القديم)"""
    print("\n" + "="*80)
    print("🔄 اختبار إشارات بدون ID (النظام القديم)")
    print("="*80)
    
    for signal in NO_ID_SIGNALS:
        print(f"\n📤 إشارة بدون ID: {signal['signal'].upper()} {signal['symbol']}")
        send_signal(signal, webhook_url=webhook_url, use_personal=use_personal, user_id=user_id)
        time.sleep(2)


def test_invalid_signals(webhook_url=None):
    """اختبار إشارات غير صحيحة"""
    print("\n" + "="*80)
    print("❌ اختبار إشارات غير صحيحة")
    print("="*80)
    
    for signal in INVALID_SIGNALS:
        print(f"\n📤 إشارة غير صحيحة: {signal}")
        send_signal(signal, webhook_url=webhook_url)
        time.sleep(1)


def interactive_test():
    """اختبار تفاعلي شامل"""
    print("\n" + "="*80)
    print("🎯 اختبار تفاعلي شامل لنظام الـ ID")
    print("="*80)
    
    # اختيار نوع الاختبار
    print("\nاختر نوع الاختبار:")
    print("1. اختبار محول الإشارات مع الـ ID")
    print("2. اختبار مدير الصفقات المرتبطة بالـ ID")
    print("3. اختبار سيناريو كامل (شراء + TP1 + TP2 + TP3 + SL)")
    print("4. اختبار صفقات متعددة على نفس الرمز")
    print("5. اختبار صفقات مختلفة على رموز مختلفة")
    print("6. اختبار إشارات بدون ID (النظام القديم)")
    print("7. اختبار إشارات غير صحيحة")
    print("8. اختبار شامل (جميع الاختبارات)")
    print("9. اختبار إشارة واحدة مخصصة")
    print("0. خروج")
    
    choice = input("\nأدخل اختيارك (0-9): ").strip()
    
    if choice == "0":
        print("👋 إلى اللقاء!")
        return
    
    # إعدادات الاتصال
    if choice not in ["1", "2"]:
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
        test_signal_position_manager()
    elif choice == "3":
        test_complete_scenario(webhook_url, use_personal, user_id)
    elif choice == "4":
        test_multiple_positions_scenario(webhook_url, use_personal, user_id)
    elif choice == "5":
        test_different_symbols_scenario(webhook_url, use_personal, user_id)
    elif choice == "6":
        test_no_id_signals(webhook_url, use_personal, user_id)
    elif choice == "7":
        test_invalid_signals(webhook_url)
    elif choice == "8":
        # اختبار شامل
        print("\n🚀 بدء الاختبار الشامل...")
        test_signal_converter()
        test_signal_position_manager()
        test_complete_scenario(webhook_url, use_personal, user_id, delay=2)
        test_multiple_positions_scenario(webhook_url, use_personal, user_id, delay=1)
        test_different_symbols_scenario(webhook_url, use_personal, user_id, delay=1)
        test_no_id_signals(webhook_url, use_personal, user_id)
        test_invalid_signals(webhook_url)
        print("\n✅ اكتمل الاختبار الشامل!")
    elif choice == "9":
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
    print("=" * 80)
    print("اختبار نظام ربط الصفقات بالـ ID - Trading Bot")
    print("=" * 80)
    print("هذا السكريبت يختبر النظام الجديد لربط الصفقات بالـ ID")
    print("=" * 80)
    
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
