#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشخيص متقدم لـ API Key الجديد
"""

import sys
import os

def advanced_api_diagnosis():
    """تشخيص متقدم لـ API Key الجديد"""
    
    print("=== تشخيص متقدم لـ API Key الجديد ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from real_account_manager import BybitRealAccount
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # API Key الجديد
        api_key = "dqBHnPaItfmEZSB020"
        api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
        
        print(f"API Key: {api_key}")
        print(f"API Secret: {api_secret[:10]}...")
        print()
        
        # إنشاء الحساب
        print("إنشاء الحساب...")
        account = BybitRealAccount(api_key, api_secret)
        print("تم إنشاء الحساب بنجاح")
        print()
        
        # اختبار 1: معلومات الحساب
        print("🔍 اختبار 1: معلومات الحساب...")
        try:
            balance = account.get_wallet_balance('unified')
            if balance:
                print(f"✅ نجح: الرصيد = {balance}")
            else:
                print("❌ فشل: لم يتم جلب الرصيد")
        except Exception as e:
            print(f"❌ خطأ: {e}")
        print()
        
        # اختبار 2: السعر الحالي
        print("🔍 اختبار 2: السعر الحالي...")
        try:
            price = account.get_ticker_price('BTCUSDT', 'spot')
            if price:
                print(f"✅ نجح: السعر = ${price}")
            else:
                print("❌ فشل: لم يتم جلب السعر")
                return False
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
        print()
        
        # اختبار 3: الصفقات المفتوحة
        print("🔍 اختبار 3: الصفقات المفتوحة...")
        try:
            positions = account.get_open_positions('spot')
            print(f"✅ نجح: الصفقات المفتوحة = {len(positions)}")
            if positions:
                for pos in positions[:3]:  # أول 3 صفقات فقط
                    print(f"   - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
        except Exception as e:
            print(f"❌ خطأ: {e}")
        print()
        
        # اختبار 4: سجل الأوامر
        print("🔍 اختبار 4: سجل الأوامر...")
        try:
            orders = account.get_order_history('spot', 5)
            print(f"✅ نجح: عدد الأوامر = {len(orders)}")
            if orders:
                for order in orders[:3]:  # أول 3 أوامر فقط
                    print(f"   - {order.get('symbol')}: {order.get('side')} {order.get('qty')} - {order.get('status')}")
        except Exception as e:
            print(f"❌ خطأ: {e}")
        print()
        
        # اختبار 5: أمر تجريبي صغير جداً
        print("🔍 اختبار 5: أمر تجريبي صغير جداً...")
        try:
            # كمية صغيرة جداً ($1 بدلاً من $100)
            test_amount = 1.0
            qty = round(test_amount / price, 8)  # دقة أعلى
            
            print(f"المبلغ: ${test_amount}")
            print(f"السعر: ${price}")
            print(f"الكمية: {qty} BTC")
            print()
            
            print("⚠️ تحذير: هذا سيضع أمر حقيقي!")
            print("هل تريد المتابعة؟ (اكتب 'نعم' للمتابعة)")
            
            # في بيئة الإنتاج، يمكنك إزالة هذا السطر وتفعيل الاختبار مباشرة
            confirm = "نعم"  # يمكنك تغيير هذا إلى input() للاختبار اليدوي
            
            if confirm == "نعم":
                print("وضع أمر تجريبي...")
                result = account.place_order(
                    category='spot',
                    symbol='BTCUSDT',
                    side='Buy',
                    order_type='Market',
                    qty=qty
                )
                
                print(f"نتيجة الأمر: {result}")
                
                if result and result.get('order_id'):
                    print("✅ نجح وضع الأمر!")
                    print(f"Order ID: {result.get('order_id')}")
                    return True
                else:
                    print("❌ فشل وضع الأمر!")
                    print("السبب المحتمل: الكمية صغيرة جداً أو صلاحيات غير كافية")
                    return False
            else:
                print("تم إلغاء الاختبار")
                return True
                
        except Exception as e:
            print(f"❌ خطأ في وضع الأمر: {e}")
            return False
        
    except Exception as e:
        print(f"خطأ في التشخيص: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = advanced_api_diagnosis()
    if not success:
        sys.exit(1)
