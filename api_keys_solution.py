#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حل مشكلة مفاتيح API - دليل عملي خطوة بخطوة
"""

import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def show_api_keys_instructions():
    """عرض تعليمات الحصول على مفاتيح API"""
    
    print("=" * 60)
    print("دليل الحصول على مفاتيح API من Bybit")
    print("=" * 60)
    
    print("\nالخطوة 1: تسجيل الدخول إلى Bybit")
    print("- اذهب إلى: https://www.bybit.com")
    print("- سجل الدخول إلى حسابك")
    
    print("\nالخطوة 2: إنشاء مفاتيح API")
    print("- اذهب إلى: Account & Security")
    print("- اضغط على: API Management")
    print("- اضغط على: Create New Key")
    
    print("\nالخطوة 3: إعداد الصلاحيات")
    print("اختر الصلاحيات التالية:")
    print("✓ Read - قراءة البيانات (مطلوب)")
    print("✓ Trade - التداول (مطلوب)")
    print("✓ Derivatives - التداول على المشتقات (مطلوب للرافعة المالية)")
    
    print("\nالخطوة 4: نسخ المفاتيح")
    print("- انسخ API Key (مفتاح API)")
    print("- انسخ Secret Key (المفتاح السري)")
    print("- احفظهما في مكان آمن")
    
    print("\nالخطوة 5: إضافة المفاتيح إلى النظام")
    print("ستحتاج إلى تحديث إعدادات المستخدم في النظام")

def add_api_keys_to_system(user_id: int, api_key: str, api_secret: str):
    """إضافة مفاتيح API إلى النظام"""
    
    print(f"\nإضافة مفاتيح API للمستخدم {user_id}...")
    
    try:
        # التحقق من صحة المفاتيح
        if not api_key or not api_secret:
            print("خطأ: مفاتيح API فارغة!")
            return False
        
        if len(api_key) < 10 or len(api_secret) < 10:
            print("خطأ: مفاتيح API قصيرة جداً!")
            return False
        
        # تهيئة الحساب
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("خطأ: فشل في تهيئة الحساب!")
            return False
        
        print("تم إضافة مفاتيح API بنجاح!")
        return True
        
    except Exception as e:
        print(f"خطأ في إضافة مفاتيح API: {e}")
        return False

def test_api_keys_comprehensive(user_id: int):
    """اختبار شامل لمفاتيح API"""
    
    print(f"\nاختبار شامل لمفاتيح API للمستخدم {user_id}")
    print("-" * 50)
    
    try:
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("لا يوجد حساب مفعّل!")
            return False
        
        # اختبار 1: جلب الرصيد
        print("اختبار 1: جلب الرصيد...")
        balance = account.get_wallet_balance('futures')
        
        if not balance:
            print("فشل في جلب الرصيد - مفاتيح API غير صحيحة!")
            return False
        
        print("نجح جلب الرصيد!")
        
        # عرض الرصيد
        if 'coins' in balance and 'USDT' in balance['coins']:
            usdt_balance = balance['coins']['USDT'].get('equity', 0)
            print(f"الرصيد المتاح: {usdt_balance} USDT")
        
        # اختبار 2: تعديل الرافعة المالية
        print("\nاختبار 2: تعديل الرافعة المالية...")
        leverage_result = account.set_leverage('linear', 'BTCUSDT', 1)
        
        if not leverage_result:
            print("فشل تعديل الرافعة المالية!")
            return False
        
        print("نجح تعديل الرافعة المالية!")
        
        # اختبار 3: وضع أمر صغير
        print("\nاختبار 3: وضع أمر صغير...")
        order_result = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001,  # كمية صغيرة جداً للاختبار
            leverage=1
        )
        
        if order_result and order_result.get('success'):
            print("نجح وضع الأمر!")
            print(f"Order ID: {order_result.get('order_id')}")
            return True
        else:
            print("فشل وضع الأمر!")
            if order_result:
                print(f"تفاصيل الخطأ: {order_result}")
            return False
            
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

def show_current_status():
    """عرض الحالة الحالية للنظام"""
    
    print("الحالة الحالية للنظام")
    print("=" * 40)
    
    user_id = 1  # معرف المستخدم الافتراضي
    
    try:
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("الحالة: مفاتيح API مفقودة أو غير صحيحة")
            print("المشكلة: لا يمكن الوصول إلى حساب Bybit")
            print("الحل: إضافة مفاتيح API صحيحة")
            return False
        else:
            print("الحالة: مفاتيح API موجودة")
            
            # اختبار سريع
            balance = account.get_wallet_balance('futures')
            if balance:
                print("النتيجة: مفاتيح API صحيحة!")
                return True
            else:
                print("النتيجة: مفاتيح API غير صحيحة!")
                return False
                
    except Exception as e:
        print(f"خطأ في فحص الحالة: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    
    print("حل مشكلة مفاتيح API لـ Bybit")
    print("=" * 50)
    
    # عرض الحالة الحالية
    current_status = show_current_status()
    
    if current_status:
        print("\nالنظام يعمل بشكل صحيح!")
        return
    
    # عرض التعليمات
    show_api_keys_instructions()
    
    print("\n" + "=" * 60)
    print("بعد الحصول على مفاتيح API:")
    print("=" * 60)
    
    print("\n1. استخدم الدالة التالية لإضافة المفاتيح:")
    print("   add_api_keys_to_system(user_id, api_key, api_secret)")
    
    print("\n2. اختبر المفاتيح:")
    print("   test_api_keys_comprehensive(user_id)")
    
    print("\n3. مثال عملي:")
    print("   add_api_keys_to_system(1, 'YOUR_API_KEY', 'YOUR_SECRET_KEY')")
    print("   test_api_keys_comprehensive(1)")

if __name__ == "__main__":
    main()
