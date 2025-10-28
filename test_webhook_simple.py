#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لإرسال إشارة للبوت
"""

import requests
import json

def test_webhook():
    """اختبار إرسال إشارة"""
    # اختبار الرابط المحلي
    url = "http://localhost:5000/personal/8169000394/webhook"
    
    # بيانات الإشارة
    data = {
        "action": "buy",
        "symbol": "BTCUSDT"
    }
    
    print("=" * 60)
    print("🧪 اختبار إرسال إشارة")
    print("=" * 60)
    print(f"📍 الرابط: {url}")
    print(f"📊 البيانات: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📡 الحالة: {response.status_code}")
        print(f"📝 الرد: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ الإشارة أُرسلت بنجاح!")
        else:
            print(f"\n⚠️ الحالة: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ البوت غير متاح!")
        print("💡 تأكد من تشغيل البوت: python app.py")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")

if __name__ == "__main__":
    test_webhook()

