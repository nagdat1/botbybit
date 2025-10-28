#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار لإرسال إشارات تجريبية للبوت
"""

import requests
import json

# روابط webhook
BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook"

def test_signal(signal, symbol, action="buy"):
    """
    اختبار إرسال إشارة للبوت
    
    Args:
        signal: نوع الإشارة (buy, sell, close)
        symbol: رمز العملة (BTCUSDT, ETHUSDT, ...)
        action: الإجراء (buy, sell, close)
    """
    
    # بناء بيانات الإشارة
    data = {
        "signal": signal,
        "symbol": symbol,
        "action": action,
        "id": f"TEST_{signal.upper()}_{symbol}"
    }
    
    print(f"\n{'='*60}")
    print(f"🧪 اختبار إرسال إشارة")
    print(f"{'='*60}")
    print(f"📊 الرمز: {symbol}")
    print(f"🔄 الإجراء: {action}")
    print(f"📡 رابط الإشارة: {WEBHOOK_URL}")
    print(f"\n📦 البيانات:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        # إرسال الإشارة
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        print(f"\n✅ الرد:")
        print(f"📋 الحالة: {response.status_code}")
        print(f"📝 المحتوى: {response.text}")
        
        if response.status_code == 200:
            print(f"\n🎉 الإشارة أُرسلت بنجاح!")
        else:
            print(f"\n❌ فشل إرسال الإشارة!")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ خطأ: البوت غير متاح في {BASE_URL}")
        print(f"💡 تأكد من تشغيل البوت أولاً: python app.py")
        return None
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 اختبار إشارات البوت")
    print("="*60)
    
    # أمثلة للاختبار
    test_cases = [
        {"signal": "buy", "symbol": "BTCUSDT", "action": "buy"},
        {"signal": "sell", "symbol": "ETHUSDT", "action": "sell"},
        {"signal": "close", "symbol": "BTCUSDT", "action": "close"},
    ]
    
    print("\n📋 سيتم اختبار الإشارات التالية:")
    for i, test in enumerate(test_cases, 1):
        print(f"  {i}. {test['action'].upper()} {test['symbol']}")
    
    print("\n⚠️ تأكد من أن البوت يعمل!")
    print("💡 شغل البوت في terminal آخر: python app.py")
    
    input("\n⏸️ اضغط Enter للمتابعة...")
    
    # اختبار أول إشارة
    test_data = test_cases[0]
    test_signal(test_data['signal'], test_data['symbol'], test_data['action'])
    
    # خيار للمزيد من الاختبارات
    while True:
        print("\n" + "="*60)
        print("❓ هل تريد اختبار إشارة أخرى؟")
        print("1. نعم - اختبار إشارة شراء BTCUSDT")
        print("2. نعم - اختبار إشارة بيع ETHUSDT")
        print("3. نعم - إرسال إشارة مخصصة")
        print("4. لا - الخروج")
        
        choice = input("\n👉 اختيارك (1-4): ")
        
        if choice == "1":
            test_signal("buy", "BTCUSDT", "buy")
        elif choice == "2":
            test_signal("sell", "ETHUSDT", "sell")
        elif choice == "3":
            symbol = input("📝 أدخل الرمز (مثل BTCUSDT): ").upper()
            action = input("📝 أدخل الإجراء (buy/sell/close): ").lower()
            test_signal(action, symbol, action)
        elif choice == "4":
            print("\n👋 مع السلامة!")
            break
        else:
            print("❌ اختيار غير صحيح!")

