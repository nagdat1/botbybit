#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار رابط الإشارة الشخصية
"""

import requests
import json
import time

# إعدادات الاختبار
BASE_URL = "https://botbybit-production.up.railway.app"  # استبدل برابطك
USER_ID = 8169000394  # استبدل برقمك

def test_personal_webhook():
    """اختبار رابط الإشارة الشخصية"""
    
    # رابط الإشارة الشخصي
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    print(f"🧪 اختبار رابط الإشارة الشخصية")
    print(f"🔗 الرابط: {webhook_url}")
    print(f"👤 معرف المستخدم: {USER_ID}")
    print("-" * 50)
    
    # بيانات الإشارة
    signal_data = {
        "symbol": "BTCUSDT",
        "action": "buy",
        "price": 50000
    }
    
    print(f"📡 إرسال إشارة:")
    print(f"   Symbol: {signal_data['symbol']}")
    print(f"   Action: {signal_data['action']}")
    print(f"   Price: {signal_data['price']}")
    print()
    
    try:
        # إرسال الطلب
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 النتيجة:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ تم إرسال الإشارة بنجاح!")
        else:
            print("❌ فشل في إرسال الإشارة")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

def test_multiple_signals():
    """اختبار إرسال عدة إشارات"""
    
    webhook_url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    signals = [
        {"symbol": "BTCUSDT", "action": "buy", "price": 50000},
        {"symbol": "ETHUSDT", "action": "sell", "price": 3000},
        {"symbol": "ADAUSDT", "action": "buy", "price": 0.5}
    ]
    
    print(f"🧪 اختبار إرسال {len(signals)} إشارات")
    print("-" * 50)
    
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

if __name__ == "__main__":
    print("🚀 بدء اختبار رابط الإشارة الشخصية")
    print("=" * 60)
    
    # اختبار إشارة واحدة
    test_personal_webhook()
    
    print("\n" + "=" * 60)
    
    # اختبار عدة إشارات
    test_multiple_signals()
    
    print("🏁 انتهى الاختبار")
