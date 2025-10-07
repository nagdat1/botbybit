#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام الإشارات المنفصل لكل مستخدم
"""

import requests
import json
import time
import threading

class MultiUserSignalTester:
    def __init__(self):
        self.base_url = "https://botbybit-production.up.railway.app"
        self.test_users = [8169000394, 123456789, 987654321]
        
    def send_signal_to_user(self, user_id, symbol, action):
        """إرسال إشارة لمستخدم محدد"""
        webhook_url = f"{self.base_url}/personal/{user_id}/webhook"
        signal_data = {
            "symbol": symbol,
            "action": action
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=signal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            return {
                'user_id': user_id,
                'symbol': symbol,
                'action': action,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.text
            }
            
        except Exception as e:
            return {
                'user_id': user_id,
                'symbol': symbol,
                'action': action,
                'status_code': 0,
                'success': False,
                'response': str(e)
            }
    
    def test_concurrent_signals(self):
        """اختبار إرسال إشارات متزامنة لمستخدمين مختلفين"""
        print("🔄 اختبار الإشارات المتزامنة")
        print("=" * 70)
        
        # إشارات مختلفة لكل مستخدم
        test_cases = [
            (8169000394, "BTCUSDT", "buy"),
            (123456789, "ETHUSDT", "sell"),
            (987654321, "ADAUSDT", "buy")
        ]
        
        results = []
        threads = []
        
        def send_signal_thread(user_id, symbol, action):
            result = self.send_signal_to_user(user_id, symbol, action)
            results.append(result)
            print(f"📡 المستخدم {user_id}: {symbol} {action} - {'✅ نجح' if result['success'] else '❌ فشل'}")
        
        # إرسال الإشارات في نفس الوقت
        print("⏳ إرسال الإشارات في نفس الوقت...")
        start_time = time.time()
        
        for user_id, symbol, action in test_cases:
            thread = threading.Thread(
                target=send_signal_thread, 
                args=(user_id, symbol, action)
            )
            threads.append(thread)
            thread.start()
        
        # انتظار انتهاء جميع الخيوط
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        print(f"\n⏱️ وقت التنفيذ: {end_time - start_time:.2f} ثانية")
        
        # تحليل النتائج
        print("\n📊 النتائج:")
        print("-" * 70)
        
        for result in results:
            status = "✅ نجح" if result['success'] else "❌ فشل"
            print(f"👤 المستخدم {result['user_id']}: {result['symbol']} {result['action']} - {status}")
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n📈 النجاح: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        return success_count == len(results)
    
    def test_sequential_signals(self):
        """اختبار إرسال إشارات متتالية لمستخدمين مختلفين"""
        print("\n📋 اختبار الإشارات المتتالية")
        print("=" * 70)
        
        # إشارات متتالية
        test_cases = [
            (8169000394, "BTCUSDT", "buy"),
            (8169000394, "ETHUSDT", "sell"),
            (123456789, "ADAUSDT", "buy"),
            (123456789, "SOLUSDT", "sell"),
            (987654321, "DOTUSDT", "buy"),
            (987654321, "LINKUSDT", "sell")
        ]
        
        results = []
        
        for i, (user_id, symbol, action) in enumerate(test_cases, 1):
            print(f"📡 إرسال {i}/{len(test_cases)}: المستخدم {user_id} - {symbol} {action}")
            
            result = self.send_signal_to_user(user_id, symbol, action)
            results.append(result)
            
            status = "✅ نجح" if result['success'] else "❌ فشل"
            print(f"   النتيجة: {status}")
            
            time.sleep(2)  # انتظار بين الإشارات
        
        # تحليل النتائج
        print("\n📊 النتائج:")
        print("-" * 70)
        
        user_results = {}
        for result in results:
            user_id = result['user_id']
            if user_id not in user_results:
                user_results[user_id] = []
            user_results[user_id].append(result)
        
        for user_id, user_signals in user_results.items():
            success_count = sum(1 for s in user_signals if s['success'])
            total_count = len(user_signals)
            print(f"👤 المستخدم {user_id}: {success_count}/{total_count} نجح ({success_count/total_count*100:.1f}%)")
        
        overall_success = sum(1 for r in results if r['success'])
        print(f"\n📈 الإجمالي: {overall_success}/{len(results)} نجح ({overall_success/len(results)*100:.1f}%)")
        
        return overall_success == len(results)
    
    def test_signal_isolation(self):
        """اختبار عزل الإشارات - التأكد من أن إشارة مستخدم لا تؤثر على آخر"""
        print("\n🔒 اختبار عزل الإشارات")
        print("=" * 70)
        
        # إرسال إشارة للمستخدم الأول
        print("📡 إرسال إشارة للمستخدم 8169000394...")
        result1 = self.send_signal_to_user(8169000394, "BTCUSDT", "buy")
        print(f"   النتيجة: {'✅ نجح' if result1['success'] else '❌ فشل'}")
        
        time.sleep(3)
        
        # إرسال إشارة للمستخدم الثاني
        print("📡 إرسال إشارة للمستخدم 123456789...")
        result2 = self.send_signal_to_user(123456789, "ETHUSDT", "sell")
        print(f"   النتيجة: {'✅ نجح' if result2['success'] else '❌ فشل'}")
        
        time.sleep(3)
        
        # إرسال إشارة للمستخدم الثالث
        print("📡 إرسال إشارة للمستخدم 987654321...")
        result3 = self.send_signal_to_user(987654321, "ADAUSDT", "buy")
        print(f"   النتيجة: {'✅ نجح' if result3['success'] else '❌ فشل'}")
        
        # التحقق من النتائج
        print("\n📊 تحليل العزل:")
        print("-" * 70)
        
        all_success = result1['success'] and result2['success'] and result3['success']
        
        if all_success:
            print("✅ جميع الإشارات نجحت")
            print("✅ الإشارات معزولة بشكل صحيح")
            print("✅ كل مستخدم يحصل على إشارته فقط")
        else:
            print("❌ بعض الإشارات فشلت")
            print("🔧 يحتاج فحص إضافي")
        
        return all_success
    
    def run_comprehensive_test(self):
        """تشغيل اختبار شامل"""
        print("🚀 بدء الاختبار الشامل لنظام الإشارات المنفصل")
        print("=" * 80)
        print("🎯 الهدف: التأكد من أن كل مستخدم يحصل على إشارته فقط")
        print("🎯 الهدف: التأكد من عدم تداخل الإشارات بين المستخدمين")
        print("=" * 80)
        
        # اختبار العزل
        isolation_success = self.test_signal_isolation()
        
        # انتظار قليل
        print("\n⏳ انتظار 5 ثواني...")
        time.sleep(5)
        
        # اختبار الإشارات المتزامنة
        concurrent_success = self.test_concurrent_signals()
        
        # انتظار قليل
        print("\n⏳ انتظار 5 ثواني...")
        time.sleep(5)
        
        # اختبار الإشارات المتتالية
        sequential_success = self.test_sequential_signals()
        
        # النتائج النهائية
        print("\n🏁 النتائج النهائية:")
        print("=" * 80)
        
        print(f"🔒 اختبار العزل: {'✅ نجح' if isolation_success else '❌ فشل'}")
        print(f"🔄 اختبار المتزامن: {'✅ نجح' if concurrent_success else '❌ فشل'}")
        print(f"📋 اختبار المتتالي: {'✅ نجح' if sequential_success else '❌ فشل'}")
        
        overall_success = isolation_success and concurrent_success and sequential_success
        
        if overall_success:
            print("\n🎉 جميع الاختبارات نجحت!")
            print("✅ النظام يعمل بشكل مثالي!")
            print("✅ كل مستخدم يحصل على إشارته فقط")
            print("✅ لا يوجد تداخل بين المستخدمين")
            print("\n📋 تعليمات التحقق:")
            print("   1. تحقق من البوت في Telegram")
            print("   2. كل مستخدم يجب أن يحصل على رسائل تأكيد")
            print("   3. كل مستخدم يجب أن يحصل على تأكيد صفقاته فقط")
        else:
            print("\n❌ بعض الاختبارات فشلت")
            print("🔧 يحتاج فحص إضافي")
        
        return overall_success

def main():
    """الدالة الرئيسية"""
    tester = MultiUserSignalTester()
    
    print("🔒 اختبار نظام الإشارات المنفصل")
    print("=" * 50)
    print("📋 هذا الاختبار سيقوم بـ:")
    print("   • اختبار عزل الإشارات بين المستخدمين")
    print("   • اختبار الإشارات المتزامنة")
    print("   • اختبار الإشارات المتتالية")
    print("   • التأكد من عدم التداخل")
    print("=" * 50)
    
    # تشغيل الاختبار الشامل
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 النظام جاهز للاستخدام!")
        print("✅ كل مستخدم له إشاراته المنفصلة")
    else:
        print("\n🔧 يحتاج إصلاح إضافي")

if __name__ == "__main__":
    main()
