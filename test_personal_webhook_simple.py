#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للـ webhook الشخصي
"""

import requests
import json
import sys

def test_personal_webhook(user_id, base_url="http://localhost:5000"):
    """
    اختبار webhook شخصي
    
    Args:
        user_id: معرّف المستخدم
        base_url: عنوان السيرفر (افتراضي: localhost:5000)
    """
    
    # بناء URL الكامل
    webhook_url = f"{base_url}/personal/{user_id}/webhook"
    
    # بيانات الاختبار
    test_data = {
        "symbol": "BTCUSDT",
        "action": "buy"
    }
    
    print("=" * 60)
    print(f"🧪 اختبار Webhook الشخصي")
    print(f"👤 المستخدم: {user_id}")
    print(f"🌐 الرابط: {webhook_url}")
    print(f"📊 البيانات: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print("=" * 60)
    
    try:
        # إرسال الطلب
        print("\n📡 جاري إرسال الطلب...")
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ تم استلام الرد:")
        print(f"📊 حالة الرد: {response.status_code}")
        print(f"📋 محتوى الرد: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 نجح الاختبار!")
            try:
                response_json = response.json()
                print(f"📝 البيانات المُرجعة:")
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
            except:
                pass
        else:
            print(f"\n❌ فشل الاختبار! رمز الحالة: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطأ: لا يمكن الاتصال بالسيرفر")
        print("تأكد من أن السيرفر يعمل على:", base_url)
    except requests.exceptions.Timeout:
        print("\n❌ خطأ: انتهت مهلة الاتصال")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # استخدام
    if len(sys.argv) < 2:
        print("الاستخدام:")
        print(f"  python {sys.argv[0]} <user_id> [base_url]")
        print("\nمثال:")
        print(f"  python {sys.argv[0]} 123456789")
        print(f"  python {sys.argv[0]} 123456789 https://your-app.railway.app")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
    
    test_personal_webhook(user_id, base_url)

