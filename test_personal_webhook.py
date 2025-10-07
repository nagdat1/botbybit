#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الرابط الشخصي للمستخدم
"""

import requests
import json

# إعدادات الاختبار
BASE_URL = "https://botbybit-production.up.railway.app"  # عدّل هذا إلى رابط Railway الخاص بك
USER_ID = 8169000394  # ضع user_id الخاص بك

def test_personal_webhook():
    """اختبار الرابط الشخصي"""
    
    url = f"{BASE_URL}/personal/{USER_ID}/webhook"
    
    signal = {
        "symbol": "BTCUSDT",
        "action": "buy"
    }
    
    print("="*60)
    print(f"🧪 اختبار الرابط الشخصي")
    print("="*60)
    print(f"\n📤 URL: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    print(f"👤 User ID: {USER_ID}")
    print("\n⏳ جاري إرسال الإشارة...")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"   Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ نجح! الرابط الشخصي يعمل بشكل صحيح!")
            return True
        elif response.status_code == 404:
            print("\n❌ خطأ 404: المستخدم غير موجود")
            print("\n💡 الحل:")
            print("   1. افتح البوت في Telegram")
            print("   2. أرسل /start")
            print("   3. سيتم إنشاء حسابك تلقائيًا")
            print("   4. جرب مرة أخرى")
            return False
        elif response.status_code == 403:
            print("\n❌ خطأ 403: المستخدم غير نشط")
            print("\n💡 الحل:")
            print("   1. افتح البوت في Telegram")
            print("   2. اضغط على زر '▶️ تشغيل البوت'")
            print("   3. جرب مرة أخرى")
            return False
        else:
            print(f"\n❌ خطأ: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ خطأ في الاتصال!")
        print("\n💡 تأكد من:")
        print(f"   1. أن السيرفر يعمل على: {BASE_URL}")
        print("   2. أن الرابط صحيح")
        print("   3. أن لديك اتصال بالإنترنت")
        return False
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def test_old_webhook():
    """اختبار الرابط القديم للمقارنة"""
    
    url = f"{BASE_URL}/webhook"
    
    signal = {
        "symbol": "BTCUSDT",
        "action": "buy"
    }
    
    print("\n" + "="*60)
    print(f"🧪 اختبار الرابط القديم (للمقارنة)")
    print("="*60)
    print(f"\n📤 URL: {url}")
    print(f"📊 البيانات: {json.dumps(signal, indent=2)}")
    print("\n⏳ جاري إرسال الإشارة...")
    
    try:
        response = requests.post(
            url,
            json=signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\n📥 الاستجابة:")
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"   Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ الرابط القديم يعمل!")
            return True
        else:
            print(f"\n❌ الرابط القديم لا يعمل: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False

def check_user_in_database():
    """التحقق من وجود المستخدم في قاعدة البيانات"""
    print("\n" + "="*60)
    print("🔍 التحقق من وجود المستخدم في قاعدة البيانات")
    print("="*60)
    
    try:
        from database import db_manager
        
        user = db_manager.get_user(USER_ID)
        
        if user:
            print(f"\n✅ المستخدم موجود في قاعدة البيانات")
            print(f"   User ID: {user['user_id']}")
            print(f"   Is Active: {user.get('is_active')}")
            print(f"   Market Type: {user.get('market_type')}")
            print(f"   Trade Amount: {user.get('trade_amount')}")
            print(f"   Account Type: {user.get('account_type')}")
            
            if not user.get('is_active'):
                print("\n⚠️ تحذير: المستخدم غير نشط!")
                print("   قم بتفعيله من البوت أو قم بتشغيل:")
                print(f"   db_manager.toggle_user_active({USER_ID})")
            
            return True
        else:
            print(f"\n❌ المستخدم غير موجود في قاعدة البيانات")
            print("\n💡 لإنشاء المستخدم، قم بتشغيل:")
            print(f"   from database import db_manager")
            print(f"   db_manager.create_user({USER_ID})")
            print("\nأو ببساطة:")
            print("   1. افتح البوت في Telegram")
            print("   2. أرسل /start")
            
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ في التحقق من قاعدة البيانات: {e}")
        print("\nهذا طبيعي إذا كنت تختبر من جهاز آخر غير السيرفر")
        return None

if __name__ == "__main__":
    print("\n" + "🚀"*30)
    print("اختبار الرابط الشخصي للمستخدم")
    print("🚀"*30)
    
    print(f"\n📋 معلومات الاختبار:")
    print(f"   BASE_URL: {BASE_URL}")
    print(f"   USER_ID: {USER_ID}")
    
    # 1. التحقق من قاعدة البيانات (إذا كنا على نفس الجهاز)
    db_check = check_user_in_database()
    
    # 2. اختبار الرابط الشخصي
    personal_result = test_personal_webhook()
    
    # 3. اختبار الرابط القديم للمقارنة
    old_result = test_old_webhook()
    
    # الخلاصة
    print("\n" + "="*60)
    print("📊 الخلاصة")
    print("="*60)
    
    if db_check is not None:
        print(f"   قاعدة البيانات: {'✅ موجود' if db_check else '❌ غير موجود'}")
    print(f"   الرابط الشخصي: {'✅ يعمل' if personal_result else '❌ لا يعمل'}")
    print(f"   الرابط القديم: {'✅ يعمل' if old_result else '❌ لا يعمل'}")
    
    if personal_result:
        print("\n🎉 كل شيء يعمل بشكل صحيح!")
    elif not db_check and db_check is not None:
        print("\n💡 المشكلة: المستخدم غير موجود في قاعدة البيانات")
        print("   الحل: أرسل /start في البوت")
    else:
        print("\n⚠️ هناك مشكلة في الرابط الشخصي")
        print("   راجع الأخطاء أعلاه")
    
    print("\n" + "="*60)

