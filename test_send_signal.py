#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار إرسال إشارة تداول إلى البوت
محاكاة إشارة من TradingView
"""

import requests
import json
import os

def test_send_signal():
    """اختبار إرسال إشارة للبوت"""
    print("=" * 60)
    print("📡 اختبار إرسال إشارة تداول")
    print("=" * 60)
    
    # الحصول على URL من المتغيرات البيئية أو استخدام localhost
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        base_url = railway_url
    elif render_url:
        base_url = render_url
    else:
        base_url = "http://localhost:5000"
    
    print(f"\n🌐 URL الأساسي: {base_url}")
    
    # طلب user_id من المستخدم
    print("\n📝 أدخل معلومات الاختبار:")
    user_id = input("User ID (Telegram): ").strip()
    
    if not user_id or not user_id.isdigit():
        print("❌ يجب إدخال User ID صحيح (رقم)")
        return
    
    # اختيار نوع الإشارة
    print("\n📊 اختر نوع الإشارة:")
    print("1. شراء (BUY)")
    print("2. بيع (SELL)")
    signal_type = input("اختر (1 أو 2): ").strip()
    
    action = "buy" if signal_type == "1" else "sell"
    action_ar = "شراء" if action == "buy" else "بيع"
    
    # اختيار المنصة
    print("\n🏦 اختر المنصة:")
    print("1. Bybit (يدعم Spot و Futures)")
    print("2. MEXC (يدعم Spot فقط)")
    exchange_choice = input("اختر (1 أو 2): ").strip()
    
    if exchange_choice == "2":
        exchange = "MEXC"
        print("   ⚠️ ملاحظة: MEXC تدعم التداول الفوري (Spot) فقط")
    else:
        exchange = "BYBIT"
    
    # اختيار الزوج
    print("\n💱 أدخل الزوج (مثال: BTCUSDT):")
    symbol = input("الزوج: ").strip().upper()
    
    if not symbol:
        symbol = "BTCUSDT"
        print(f"   استخدام الزوج الافتراضي: {symbol}")
    
    # بناء الإشارة
    signal_data = {
        "action": action,
        "symbol": symbol,
        "price": "{{close}}",  # سيتم استبداله بالسعر الحالي من المنصة
        "time": "{{time}}",
        "exchange": exchange
    }
    
    # إنشاء URL الشخصي
    personal_webhook_url = f"{base_url}/personal/{user_id}/webhook"
    
    print("\n" + "=" * 60)
    print("📤 جاري إرسال الإشارة...")
    print("=" * 60)
    print(f"\n📍 URL: {personal_webhook_url}")
    print(f"📊 البيانات: {json.dumps(signal_data, indent=2, ensure_ascii=False)}")
    
    try:
        # إرسال الطلب
        response = requests.post(
            personal_webhook_url,
            json=signal_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   • كود الحالة: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ تم إرسال الإشارة بنجاح!")
            try:
                response_data = response.json()
                print(f"   • الرد: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   • الرد: {response.text}")
        elif response.status_code == 404:
            print("   ❌ المستخدم غير موجود!")
            print("   💡 تأكد من:")
            print("      • استخدام /start في البوت أولاً")
            print("      • User ID صحيح")
        elif response.status_code == 403:
            print("   ❌ المستخدم غير نشط!")
            print("   💡 قم بتفعيل البوت من الإعدادات")
        else:
            print(f"   ❌ خطأ: {response.status_code}")
            print(f"   • الرد: {response.text}")
        
        print("\n" + "=" * 60)
        print("📱 تحقق من تطبيق Telegram")
        print("=" * 60)
        print(f"\nيجب أن تصلك رسالة في البوت تحتوي على:")
        print(f"   • نوع الإشارة: {action_ar}")
        print(f"   • الزوج: {symbol}")
        print(f"   • تفاصيل الصفقة")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ خطأ في الاتصال!")
        print("💡 تأكد من:")
        print("   • البوت يعمل (python app.py)")
        print("   • URL صحيح")
        print("   • الاتصال بالإنترنت")
    except requests.exceptions.Timeout:
        print("\n❌ انتهت مهلة الاتصال!")
        print("💡 البوت قد يكون بطيئاً أو لا يستجيب")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

def test_webhook_health():
    """اختبار صحة الخادم"""
    print("\n" + "=" * 60)
    print("🏥 اختبار صحة الخادم")
    print("=" * 60)
    
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        base_url = railway_url
    elif render_url:
        base_url = render_url
    else:
        base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ الخادم يعمل بشكل صحيح!")
            try:
                data = response.json()
                print(f"   البيانات: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                pass
        else:
            print(f"⚠️ الخادم يستجيب بكود: {response.status_code}")
    except Exception as e:
        print(f"❌ الخادم لا يستجيب: {e}")

if __name__ == "__main__":
    print("\n🧪 سكريبت اختبار إرسال الإشارات")
    print("=" * 60)
    
    # اختبار صحة الخادم أولاً
    test_webhook_health()
    
    # ثم اختبار إرسال الإشارة
    print("\n")
    try:
        test_send_signal()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إلغاء الاختبار")
    except Exception as e:
        print(f"\n\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار")
    print("=" * 60)

