#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الروابط الشخصية
"""

import requests
import json
import time
import random

class PersonalWebhookTester:
    def __init__(self):
        self.base_url = "https://botbybit-production.up.railway.app"
        self.test_users = [8169000394, 123456789, 987654321, 555666777]
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]
        
    def test_health(self):
        """اختبار حالة السيرفر"""
        print("🏥 اختبار حالة السيرفر")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                print("✅ السيرفر يعمل بشكل طبيعي")
                return True
            else:
                print("❌ السيرفر لا يعمل")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def test_personal_webhook(self, user_id, symbol, action):
        """اختبار رابط شخصي مع إشارة"""
        print(f"\n📡 اختبار رابط شخصي للمستخدم {user_id}")
        print("-" * 50)
        
        webhook_url = f"{self.base_url}/personal/{user_id}/webhook"
        signal_data = {
            "symbol": symbol,
            "action": action
        }
        
        print(f"🔗 الرابط: {webhook_url}")
        print(f"📡 الإشارة: {json.dumps(signal_data, indent=2)}")
        
        try:
            start_time = time.time()
            response = requests.post(
                webhook_url,
                json=signal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = time.time()
            
            print(f"⏱️ وقت الاستجابة: {end_time - start_time:.2f} ثانية")
            print(f"📈 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ نجح الاختبار!")
                return True
            else:
                print("❌ فشل الاختبار")
                return False
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def test_start_project(self, user_id):
        """اختبار بدء المشروع بدون إشارة"""
        print(f"\n🚀 اختبار بدء المشروع للمستخدم {user_id}")
        print("-" * 50)
        
        start_url = f"{self.base_url}/personal/{user_id}/start"
        
        try:
            response = requests.post(start_url, json={}, timeout=30)
            print(f"📈 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ تم بدء المشروع بنجاح!")
                return True
            else:
                print("❌ فشل في بدء المشروع")
                return False
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def test_endpoint_status(self, user_id):
        """اختبار حالة جميع الـ endpoints"""
        print(f"\n🔍 اختبار حالة الـ endpoints للمستخدم {user_id}")
        print("-" * 50)
        
        endpoints = [
            (f"/personal/{user_id}/test", "GET", "اختبار الرابط"),
            (f"/personal/{user_id}/start", "POST", "بدء المشروع"),
            (f"/personal/{user_id}/webhook", "POST", "رابط الإشارة")
        ]
        
        for endpoint, method, description in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"📡 {description}: {method} {url}")
            
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json={}, timeout=10)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 400]:
                    print("   ✅ يعمل")
                else:
                    print("   ❌ لا يعمل")
                    
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
            
            print()
    
    def test_multiple_users(self):
        """اختبار عدة مستخدمين"""
        print("\n👥 اختبار عدة مستخدمين")
        print("=" * 50)
        
        results = []
        
        for user_id in self.test_users:
            print(f"\n📡 اختبار المستخدم: {user_id}")
            
            # اختبار بدء المشروع
            start_result = self.test_start_project(user_id)
            
            # انتظار قليل
            time.sleep(2)
            
            # اختبار إشارة
            symbol = random.choice(self.test_symbols)
            action = random.choice(["buy", "sell"])
            signal_result = self.test_personal_webhook(user_id, symbol, action)
            
            results.append({
                'user_id': user_id,
                'start_success': start_result,
                'signal_success': signal_result
            })
            
            time.sleep(3)  # انتظار بين المستخدمين
        
        # عرض النتائج
        print("\n📊 النتائج النهائية:")
        print("=" * 50)
        
        for result in results:
            status = "✅ نجح" if result['start_success'] and result['signal_success'] else "❌ فشل"
            print(f"المستخدم {result['user_id']}: {status}")
        
        success_count = sum(1 for r in results if r['start_success'] and r['signal_success'])
        total_count = len(results)
        
        print(f"\n📈 النجاح: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        return success_count == total_count
    
    def test_different_signals(self, user_id):
        """اختبار إشارات مختلفة"""
        print(f"\n🎯 اختبار إشارات مختلفة للمستخدم {user_id}")
        print("=" * 50)
        
        test_cases = [
            {"symbol": "BTCUSDT", "action": "buy"},
            {"symbol": "ETHUSDT", "action": "sell"},
            {"symbol": "ADAUSDT", "action": "buy"},
            {"symbol": "SOLUSDT", "action": "sell"},
            {"symbol": "DOTUSDT", "action": "buy"}
        ]
        
        results = []
        
        for i, signal in enumerate(test_cases, 1):
            print(f"\n📡 اختبار {i}/{len(test_cases)}: {signal['symbol']} {signal['action']}")
            
            result = self.test_personal_webhook(user_id, signal['symbol'], signal['action'])
            results.append(result)
            
            if result:
                print("✅ نجح")
            else:
                print("❌ فشل")
            
            time.sleep(2)  # انتظار بين الإشارات
        
        success_count = sum(results)
        print(f"\n📈 النجاح: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
        
        return success_count == len(test_cases)
    
    def run_full_test(self):
        """تشغيل اختبار شامل"""
        print("🚀 بدء الاختبار الشامل لنظام الروابط الشخصية")
        print("=" * 80)
        
        # 1. اختبار حالة السيرفر
        if not self.test_health():
            print("❌ السيرفر لا يعمل، إيقاف الاختبار")
            return False
        
        # 2. اختبار مستخدم واحد مع إشارات مختلفة
        main_user = self.test_users[0]
        print(f"\n🎯 اختبار مستخدم رئيسي: {main_user}")
        
        if not self.test_different_signals(main_user):
            print("❌ فشل في اختبار الإشارات المختلفة")
            return False
        
        # 3. اختبار عدة مستخدمين
        if not self.test_multiple_users():
            print("❌ فشل في اختبار عدة مستخدمين")
            return False
        
        # 4. اختبار حالة الـ endpoints
        self.test_endpoint_status(main_user)
        
        print("\n🎉 انتهى الاختبار الشامل!")
        print("=" * 80)
        print("✅ النظام يعمل بشكل مثالي!")
        print("📋 تعليمات التحقق:")
        print("   1. تحقق من البوت في Telegram")
        print("   2. يجب أن تظهر رسائل ترحيب وتأكيد")
        print("   3. يجب أن تظهر رسائل تأكيد الصفقات")
        print("\n🔗 روابط مفيدة:")
        print("   📊 Railway Dashboard: https://railway.app/dashboard")
        print("   🏥 Health Check: https://botbybit-production.up.railway.app/health")
        
        return True

def main():
    """الدالة الرئيسية"""
    tester = PersonalWebhookTester()
    
    print("🎯 اختبار نظام الروابط الشخصية")
    print("=" * 50)
    print("📋 هذا الاختبار سيقوم بـ:")
    print("   • اختبار حالة السيرفر")
    print("   • اختبار روابط شخصية متعددة")
    print("   • اختبار إشارات مختلفة")
    print("   • اختبار عدة مستخدمين")
    print("=" * 50)
    
    # تشغيل الاختبار
    success = tester.run_full_test()
    
    if success:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ النظام جاهز للاستخدام")
    else:
        print("\n❌ بعض الاختبارات فشلت")
        print("🔧 يرجى التحقق من الأخطاء")

if __name__ == "__main__":
    main()
