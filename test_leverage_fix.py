#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار وإصلاح مشكلة تعديل الرافعة المالية
"""

import asyncio
import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_leverage_setting():
    """اختبار تعديل الرافعة المالية"""
    
    print("اختبار تعديل الرافعة المالية")
    print("=" * 50)
    
    # بيانات الاختبار
    test_cases = [
        {
            'symbol': 'BTCUSDT',
            'category': 'linear',
            'leverage': 1,
            'description': 'رافعة 1x لـ BTCUSDT'
        },
        {
            'symbol': 'BTCUSDT',
            'category': 'linear',
            'leverage': 5,
            'description': 'رافعة 5x لـ BTCUSDT'
        },
        {
            'symbol': 'BTCUSDT',
            'category': 'linear',
            'leverage': 10,
            'description': 'رافعة 10x لـ BTCUSDT'
        },
        {
            'symbol': 'ETHUSDT',
            'category': 'linear',
            'leverage': 3,
            'description': 'رافعة 3x لـ ETHUSDT'
        }
    ]
    
    # الحصول على الحساب الحقيقي
    user_id = 1  # يجب تحديثه حسب المستخدم الفعلي
    account = real_account_manager.get_account(user_id)
    
    if not account:
        print("لا يوجد حساب حقيقي مفعّل")
        print("يرجى إضافة مفاتيح API صحيحة")
        return False
    
    print(f"تم العثور على حساب حقيقي للمستخدم {user_id}")
    
    # اختبار كل حالة
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nاختبار {i}/{total_tests}: {test_case['description']}")
        print("-" * 40)
        
        try:
            # محاولة تعديل الرافعة المالية
            result = account.set_leverage(
                category=test_case['category'],
                symbol=test_case['symbol'],
                leverage=test_case['leverage']
            )
            
            if result:
                print(f"نجح تعديل الرافعة المالية: {test_case['leverage']}x")
                success_count += 1
            else:
                print(f"فشل تعديل الرافعة المالية: {test_case['leverage']}x")
                
                # محاولة الحصول على تفاصيل الخطأ
                print("تفاصيل الخطأ:")
                print("- تحقق من صحة الرمز")
                print("- تحقق من صلاحيات API")
                print("- تحقق من نوع الحساب")
                print("- تحقق من الحدود المسموحة للرافعة")
                
        except Exception as e:
            print(f"خطأ في اختبار الرافعة المالية: {e}")
    
    print(f"\nنتائج الاختبار:")
    print(f"نجح: {success_count}/{total_tests}")
    print(f"فشل: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("جميع الاختبارات نجحت!")
        return True
    else:
        print("بعض الاختبارات فشلت - راجع السجلات للتفاصيل")
        return False

async def test_order_with_leverage():
    """اختبار وضع أمر مع تعديل الرافعة المالية"""
    
    print("\nاختبار وضع أمر مع تعديل الرافعة المالية")
    print("=" * 60)
    
    # بيانات الاختبار
    test_order = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'order_type': 'Market',
        'qty': 0.001,  # كمية صغيرة للاختبار
        'leverage': 1
    }
    
    # الحصول على الحساب الحقيقي
    user_id = 1
    account = real_account_manager.get_account(user_id)
    
    if not account:
        print("❌ لا يوجد حساب حقيقي مفعّل")
        return False
    
    print(f"📋 بيانات الأمر:")
    for key, value in test_order.items():
        print(f"  {key}: {value}")
    
    try:
        # خطوة 1: تعديل الرافعة المالية
        print(f"\nخطوة 1: تعديل الرافعة المالية إلى {test_order['leverage']}x")
        leverage_result = account.set_leverage(
            category=test_order['category'],
            symbol=test_order['symbol'],
            leverage=test_order['leverage']
        )
        
        if leverage_result:
            print("✅ تم تعديل الرافعة المالية بنجاح")
        else:
            print("❌ فشل تعديل الرافعة المالية")
            return False
        
        # خطوة 2: وضع الأمر
        print(f"\nخطوة 2: وضع الأمر")
        order_result = account.place_order(
            category=test_order['category'],
            symbol=test_order['symbol'],
            side=test_order['side'],
            order_type=test_order['order_type'],
            qty=test_order['qty'],
            leverage=test_order['leverage']
        )
        
        if order_result and order_result.get('success'):
            print("✅ تم وضع الأمر بنجاح!")
            print(f"Order ID: {order_result.get('order_id')}")
            return True
        else:
            print("❌ فشل وضع الأمر")
            if order_result:
                print(f"تفاصيل الخطأ: {order_result}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الأمر: {e}")
        import traceback
        traceback.print_exc()
        return False

async def diagnose_leverage_issues():
    """تشخيص مشاكل الرافعة المالية"""
    
    print("\nتشخيص مشاكل الرافعة المالية")
    print("=" * 40)
    
    # الحصول على الحساب الحقيقي
    user_id = 1
    account = real_account_manager.get_account(user_id)
    
    if not account:
        print("❌ لا يوجد حساب حقيقي مفعّل")
        print("الحل: أضف مفاتيح API صحيحة")
        return
    
    print("🔍 فحص إعدادات الحساب...")
    
    try:
        # فحص الرصيد
        balance = account.get_wallet_balance('futures')
        if balance:
            print("✅ تم جلب الرصيد بنجاح")
            if 'coins' in balance and 'USDT' in balance['coins']:
                usdt_balance = balance['coins']['USDT'].get('equity', 0)
                print(f"💰 الرصيد المتاح: {usdt_balance} USDT")
            else:
                print("⚠️ لم يتم العثور على رصيد USDT")
        else:
            print("❌ فشل في جلب الرصيد")
        
        # فحص الصفقات المفتوحة
        positions = account.get_open_positions('linear')
        if positions is not None:
            print(f"📊 الصفقات المفتوحة: {len(positions)}")
            for pos in positions:
                print(f"  - {pos['symbol']}: {pos['side']} {pos['size']} (رافعة: {pos['leverage']})")
        else:
            print("❌ فشل في جلب الصفقات المفتوحة")
        
        # فحص معلومات الرمز
        ticker = account.get_ticker('linear', 'BTCUSDT')
        if ticker:
            print("✅ تم جلب معلومات BTCUSDT بنجاح")
            print(f"السعر الحالي: {ticker.get('lastPrice', 'غير متوفر')}")
        else:
            print("❌ فشل في جلب معلومات BTCUSDT")
        
    except Exception as e:
        print(f"❌ خطأ في التشخيص: {e}")

if __name__ == "__main__":
    print("بدء اختبار تعديل الرافعة المالية...")
    
    try:
        # تشغيل الاختبارات
        leverage_test = asyncio.run(test_leverage_setting())
        order_test = asyncio.run(test_order_with_leverage())
        asyncio.run(diagnose_leverage_issues())
        
        print("\n📋 ملخص النتائج:")
        print(f"اختبار الرافعة المالية: {'✅ نجح' if leverage_test else '❌ فشل'}")
        print(f"اختبار الأمر: {'✅ نجح' if order_test else '❌ فشل'}")
        
        if leverage_test and order_test:
            print("\n🎉 جميع الاختبارات نجحت! تعديل الرافعة المالية يعمل بشكل صحيح.")
        else:
            print("\n⚠️ بعض الاختبارات فشلت. راجع السجلات للتفاصيل.")
            print("\n💡 نصائح لحل المشاكل:")
            print("1. تأكد من صحة مفاتيح API")
            print("2. تحقق من صلاحيات التداول")
            print("3. تأكد من وجود رصيد كافي")
            print("4. تحقق من صحة الرمز")
            print("5. راجع حدود الرافعة المالية المسموحة")
        
    except KeyboardInterrupt:
        print("\nتم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\nخطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
