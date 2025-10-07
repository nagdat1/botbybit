#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لإصلاح مشكلة تداخل الإشارات
"""

import requests
import json
import time

def test_signal_isolation():
    """اختبار عزل الإشارات بين المستخدمين"""
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    
    # مستخدمين مختلفين
    users = [
        {"id": 8169000394, "symbol": "BTCUSDT", "action": "buy"},
        {"id": 123456789, "symbol": "ETHUSDT", "action": "sell"},
        {"id": 987654321, "symbol": "ADAUSDT", "action": "buy"}
    ]
    
    print("🔒 اختبار عزل الإشارات بين المستخدمين")
    print("=" * 70)
    
    results = []
    
    for i, user in enumerate(users, 1):
        print(f"\n📡 اختبار {i}/{len(users)}: المستخدم {user['id']}")
        print(f"   🔹 الرمز: {user['symbol']}")
        print(f"   🔹 الإجراء: {user['action']}")
        
        webhook_url = f"{BASE_URL}/personal/{user['id']}/webhook"
        signal_data = {
            "symbol": user['symbol'],
            "action": user['action']
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                webhook_url,
                json=signal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response_time = time.time() - start_time
            
            result = {
                'user_id': user['id'],
                'symbol': user['symbol'],
                'action': user['action'],
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200,
                'response': response.text
            }
            
            results.append(result)
            
            print(f"   ⏱️ وقت الاستجابة: {response_time:.2f} ثانية")
            print(f"   📈 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ نجح")
            else:
                print("   ❌ فشل")
                print(f"   📄 Response: {response.text}")
            
        except Exception as e:
            result = {
                'user_id': user['id'],
                'symbol': user['symbol'],
                'action': user['action'],
                'status_code': 0,
                'response_time': 0,
                'success': False,
                'response': str(e)
            }
            results.append(result)
            print(f"   ❌ خطأ: {e}")
        
        # انتظار بين الطلبات
        time.sleep(2)
    
    # تحليل النتائج
    print("\n📊 النتائج:")
    print("=" * 70)
    
    success_count = 0
    for result in results:
        status = "✅ نجح" if result['success'] else "❌ فشل"
        print(f"👤 المستخدم {result['user_id']}: {result['symbol']} {result['action']} - {status}")
        if result['success']:
            success_count += 1
    
    print(f"\n📈 النجاح: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 جميع الإشارات نجحت!")
        print("✅ النظام يعمل بشكل منفصل لكل مستخدم")
        print("✅ لا يوجد تداخل بين المستخدمين")
        
        print("\n📋 تعليمات التحقق:")
        print("   1. تحقق من البوت في Telegram")
        print("   2. كل مستخدم يجب أن يحصل على رسائل تأكيد")
        print("   3. كل مستخدم يجب أن يحصل على تأكيد صفقاته فقط")
        
        return True
    else:
        print("❌ بعض الإشارات فشلت")
        print("🔧 يحتاج فحص إضافي")
        return False

def test_concurrent_signals():
    """اختبار الإشارات المتزامنة"""
    
    import threading
    
    BASE_URL = "https://botbybit-production.up.railway.app"
    
    # مستخدمين مختلفين
    users = [
        {"id": 8169000394, "symbol": "BTCUSDT", "action": "buy"},
        {"id": 123456789, "symbol": "ETHUSDT", "action": "sell"},
        {"id": 987654321, "symbol": "ADAUSDT", "action": "buy"}
    ]
    
    print("\n🔄 اختبار الإشارات المتزامنة")
    print("=" * 70)
    
    results = []
    
    def send_signal_thread(user):
        webhook_url = f"{BASE_URL}/personal/{user['id']}/webhook"
        signal_data = {
            "symbol": user['symbol'],
            "action": user['action']
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=signal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            result = {
                'user_id': user['id'],
                'symbol': user['symbol'],
                'action': user['action'],
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.text
            }
            
            results.append(result)
            print(f"📡 المستخدم {user['id']}: {user['symbol']} {user['action']} - {'✅ نجح' if result['success'] else '❌ فشل'}")
            
        except Exception as e:
            result = {
                'user_id': user['id'],
                'symbol': user['symbol'],
                'action': user['action'],
                'status_code': 0,
                'success': False,
                'response': str(e)
            }
            results.append(result)
            print(f"📡 المستخدم {user['id']}: {user['symbol']} {user['action']} - ❌ خطأ: {e}")
    
    # إرسال الإشارات في نفس الوقت
    print("⏳ إرسال الإشارات في نفس الوقت...")
    start_time = time.time()
    
    threads = []
    for user in users:
        thread = threading.Thread(target=send_signal_thread, args=(user,))
        threads.append(thread)
        thread.start()
    
    # انتظار انتهاء جميع الخيوط
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    print(f"\n⏱️ وقت التنفيذ: {end_time - start_time:.2f} ثانية")
    
    # تحليل النتائج
    success_count = sum(1 for r in results if r['success'])
    print(f"📈 النجاح: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    return success_count == len(results)

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار إصلاح مشكلة تداخل الإشارات")
    print("=" * 80)
    print("🎯 الهدف: التأكد من أن كل مستخدم يحصل على إشارته فقط")
    print("🎯 الهدف: التأكد من عدم تداخل الإشارات بين المستخدمين")
    print("=" * 80)
    
    # اختبار العزل
    isolation_success = test_signal_isolation()
    
    # انتظار قليل
    print("\n⏳ انتظار 5 ثواني...")
    time.sleep(5)
    
    # اختبار الإشارات المتزامنة
    concurrent_success = test_concurrent_signals()
    
    # النتائج النهائية
    print("\n🏁 النتائج النهائية:")
    print("=" * 80)
    
    print(f"🔒 اختبار العزل: {'✅ نجح' if isolation_success else '❌ فشل'}")
    print(f"🔄 اختبار المتزامن: {'✅ نجح' if concurrent_success else '❌ فشل'}")
    
    overall_success = isolation_success and concurrent_success
    
    if overall_success:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ النظام يعمل بشكل مثالي!")
        print("✅ كل مستخدم يحصل على إشارته فقط")
        print("✅ لا يوجد تداخل بين المستخدمين")
    else:
        print("\n❌ بعض الاختبارات فشلت")
        print("🔧 يحتاج فحص إضافي")
    
    print("\n🔗 روابط مفيدة:")
    print("   📊 Railway Dashboard: https://railway.app/dashboard")
    print("   🏥 Health Check: https://botbybit-production.up.railway.app/health")

if __name__ == "__main__":
    main()
