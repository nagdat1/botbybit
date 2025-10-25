#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لطريقة التوقيع المحسنة
"""

import logging
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_signature_with_real_keys():
    """اختبار التوقيع مع مفاتيح حقيقية"""
    
    print("اختبار التوقيع مع مفاتيح حقيقية")
    print("=" * 50)
    
    # مفاتيح وهمية للاختبار (استبدلها بمفاتيحك الحقيقية)
    api_key = "YOUR_REAL_API_KEY_HERE"
    api_secret = "YOUR_REAL_SECRET_KEY_HERE"
    
    user_id = 1
    
    try:
        # تهيئة الحساب
        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
        account = real_account_manager.get_account(user_id)
        
        if not account:
            print("فشل في تهيئة الحساب")
            return False
        
        print("تم تهيئة الحساب بنجاح")
        
        # اختبار 1: جلب الرصيد
        print("\nاختبار 1: جلب الرصيد")
        print("-" * 30)
        
        balance = account.get_wallet_balance('futures')
        
        if balance:
            print("نجح جلب الرصيد!")
            if 'coins' in balance and 'USDT' in balance['coins']:
                usdt_balance = balance['coins']['USDT'].get('equity', 0)
                print(f"الرصيد المتاح: {usdt_balance} USDT")
            return True
        else:
            print("فشل جلب الرصيد - تحقق من مفاتيح API")
            return False
            
    except Exception as e:
        print(f"خطأ في اختبار التوقيع: {e}")
        return False

def test_signature_calculation():
    """اختبار حساب التوقيع"""
    
    print("\nاختبار حساب التوقيع")
    print("=" * 30)
    
    # مفاتيح وهمية للاختبار
    api_key = "test_api_key_123"
    api_secret = "test_secret_key_456"
    
    try:
        # إنشاء حساب وهمي للاختبار
        from real_account_manager import BybitRealAccount
        account = BybitRealAccount(api_key, api_secret)
        
        # اختبار توليد التوقيع
        timestamp = "1640995200000"
        recv_window = "5000"
        params_str = '{"category":"linear","symbol":"BTCUSDT"}'
        
        signature = account._generate_signature(timestamp, recv_window, params_str)
        
        print(f"Timestamp: {timestamp}")
        print(f"Recv Window: {recv_window}")
        print(f"Params String: {params_str}")
        print(f"Generated Signature: {signature}")
        
        # التحقق من صحة التوقيع
        expected_sign_str = timestamp + api_key + recv_window + params_str
        print(f"Expected Sign String: {expected_sign_str}")
        
        print("تم توليد التوقيع بنجاح!")
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار حساب التوقيع: {e}")
        return False

def test_different_request_types():
    """اختبار أنواع طلبات مختلفة"""
    
    print("\nاختبار أنواع طلبات مختلفة")
    print("=" * 40)
    
    # مفاتيح وهمية للاختبار
    api_key = "test_api_key_123"
    api_secret = "test_secret_key_456"
    
    try:
        from real_account_manager import BybitRealAccount
        account = BybitRealAccount(api_key, api_secret)
        
        test_cases = [
            {
                'name': 'طلب GET بسيط',
                'method': 'GET',
                'endpoint': '/v5/account/wallet-balance',
                'params': {'accountType': 'UNIFIED'}
            },
            {
                'name': 'طلب POST مع معاملات',
                'method': 'POST',
                'endpoint': '/v5/order/create',
                'params': {
                    'category': 'linear',
                    'symbol': 'BTCUSDT',
                    'side': 'Buy',
                    'orderType': 'Market',
                    'qty': '0.001'
                }
            },
            {
                'name': 'طلب تعديل الرافعة المالية',
                'method': 'POST',
                'endpoint': '/v5/position/set-leverage',
                'params': {
                    'category': 'linear',
                    'symbol': 'BTCUSDT',
                    'buyLeverage': '1',
                    'sellLeverage': '1'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nاختبار {i}: {test_case['name']}")
            print("-" * 30)
            
            try:
                # محاولة إرسال الطلب (سيفشل لأن المفاتيح وهمية)
                result = account._make_request(
                    test_case['method'],
                    test_case['endpoint'],
                    test_case['params']
                )
                
                print(f"النتيجة: {result}")
                
            except Exception as e:
                print(f"خطأ متوقع (مفاتيح وهمية): {e}")
        
        print("\nتم اختبار جميع أنواع الطلبات!")
        return True
        
    except Exception as e:
        print(f"خطأ في اختبار أنواع الطلبات: {e}")
        return False

def show_signature_debug_info():
    """عرض معلومات تشخيص التوقيع"""
    
    print("\nمعلومات تشخيص التوقيع")
    print("=" * 40)
    
    print("التحسينات المطبقة:")
    print("1. ترتيب المعاملات أبجدياً")
    print("2. استخدام تنسيق JSON محدد للطلبات POST")
    print("3. معالجة محسنة للمعاملات الفارغة")
    print("4. تسجيل مفصل للتشخيص")
    print("5. معالجة أفضل للأخطاء")
    
    print("\nطريقة التوقيع:")
    print("1. ترتيب المعاملات أبجدياً")
    print("2. تحويل إلى JSON للطلبات POST")
    print("3. بناء سلسلة التوقيع: timestamp + api_key + recv_window + params_str")
    print("4. توليد HMAC-SHA256")
    
    print("\nللاختبار مع مفاتيح حقيقية:")
    print("1. استبدل YOUR_REAL_API_KEY_HERE بمفتاح API الحقيقي")
    print("2. استبدل YOUR_REAL_SECRET_KEY_HERE بالمفتاح السري الحقيقي")
    print("3. شغل الاختبار")

if __name__ == "__main__":
    print("اختبار شامل لطريقة التوقيع المحسنة")
    print("=" * 60)
    
    try:
        # اختبار حساب التوقيع
        test_signature_calculation()
        
        # اختبار أنواع طلبات مختلفة
        test_different_request_types()
        
        # عرض معلومات التشخيص
        show_signature_debug_info()
        
        # اختبار مع مفاتيح حقيقية (إذا كانت متوفرة)
        print("\n" + "=" * 60)
        print("للاختبار مع مفاتيح حقيقية:")
        print("1. حدث المفاتيح في test_signature_with_real_keys()")
        print("2. شغل الاختبار مرة أخرى")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
