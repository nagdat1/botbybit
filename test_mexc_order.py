#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار وضع أمر على MEXC مع تشخيص مفصل
"""

import logging
import os
from dotenv import load_dotenv
from mexc_trading_bot import create_mexc_bot

# إعداد التسجيل المفصل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_mexc_order_placement():
    """اختبار وضع أمر على MEXC مع تشخيص مفصل"""
    print("=" * 60)
    print("اختبار وضع أمر على MEXC")
    print("=" * 60)
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    api_key = os.getenv('MEXC_API_KEY', '')
    api_secret = os.getenv('MEXC_API_SECRET', '')
    
    print(f"API Key موجود: {bool(api_key)}")
    print(f"API Secret موجود: {bool(api_secret)}")
    
    if not api_key or not api_secret:
        print("❌ يرجى تعيين MEXC_API_KEY و MEXC_API_SECRET في ملف .env")
        return False
    
    try:
        # إنشاء البوت
        print("\nإنشاء بوت MEXC...")
        bot = create_mexc_bot(api_key, api_secret)
        
        # اختبار الاتصال
        print("\nاختبار الاتصال...")
        if not bot.test_connection():
            print("❌ فشل الاتصال!")
            return False
        
        print("✅ الاتصال ناجح!")
        
        # اختبار جلب السعر
        print("\nاختبار جلب السعر...")
        price = bot.get_ticker_price('BTCUSDT')
        if not price:
            print("❌ فشل جلب السعر!")
            return False
        
        print(f"✅ السعر الحالي: ${price:,.2f}")
        
        # اختبار معلومات الرمز
        print("\nاختبار معلومات الرمز...")
        symbol_info = bot.get_symbol_info('BTCUSDT')
        if not symbol_info:
            print("❌ فشل الحصول على معلومات الرمز!")
            return False
        
        print(f"✅ معلومات الرمز:")
        print(f"   التداول الفوري مسموح: {symbol_info['is_spot_trading_allowed']}")
        print(f"   الحالة: {symbol_info['status']}")
        
        # اختبار وضع أمر صغير جداً (للتجربة)
        print("\nاختبار وضع أمر تجريبي...")
        print("⚠️ تحذير: هذا اختبار حقيقي - سيتم وضع أمر صغير!")
        
        # أمر صغير جداً للتجربة
        test_quantity = 0.0001  # كمية صغيرة جداً
        print(f"الكمية التجريبية: {test_quantity} BTC")
        
        result = bot.place_spot_order(
            symbol='BTCUSDT',
            side='BUY',
            quantity=test_quantity,
            order_type='MARKET'
        )
        
        if result:
            print("✅ تم وضع الأمر بنجاح!")
            print(f"تفاصيل الأمر: {result}")
            return True
        else:
            print("❌ فشل وضع الأمر!")
            return False
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_keys():
    """اختبار مفاتيح API"""
    print("\n" + "=" * 60)
    print("اختبار مفاتيح API")
    print("=" * 60)
    
    load_dotenv()
    
    api_key = os.getenv('MEXC_API_KEY', '')
    api_secret = os.getenv('MEXC_API_SECRET', '')
    
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else 'SHORT'}")
    print(f"API Secret: {'*' * len(api_secret) if api_secret else 'NOT_SET'}")
    
    if not api_key or not api_secret:
        print("مفاتيح API غير موجودة!")
        return False
    
    if len(api_key) < 10:
        print("API Key قصير جداً!")
        return False
    
    if len(api_secret) < 10:
        print("API Secret قصير جداً!")
        return False
    
    print("مفاتيح API تبدو صحيحة")
    return True

def test_signature_generation():
    """اختبار توليد التوقيع"""
    print("\n" + "=" * 60)
    print("اختبار توليد التوقيع")
    print("=" * 60)
    
    try:
        from mexc_trading_bot import MEXCTradingBot
        
        # إنشاء مثيل للاختبار
        bot = MEXCTradingBot("test_key_123456789", "test_secret_123456789")
        
        # اختبار التوقيع
        test_params = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': '0.001',
            'timestamp': 1640995200000
        }
        
        signature = bot._generate_signature(test_params)
        print(f"التوقيع المُولد: {signature}")
        
        # التحقق من أن التوقيع ليس فارغاً
        if signature and len(signature) == 64:  # SHA256 hex length
            print("التوقيع صحيح الطول")
            return True
        else:
            print("التوقيع غير صحيح")
            return False
            
    except Exception as e:
        print(f"خطأ في اختبار التوقيع: {e}")
        return False

if __name__ == "__main__":
    print("بدء اختبار وضع أمر على MEXC...")
    
    # اختبار مفاتيح API
    api_test = test_api_keys()
    
    # اختبار توليد التوقيع
    signature_test = test_signature_generation()
    
    # اختبار وضع الأمر إذا كانت الاختبارات السابقة نجحت
    if api_test and signature_test:
        order_test = test_mexc_order_placement()
        
        if order_test:
            print("\n🎉 جميع الاختبارات نجحت!")
            print("✅ وضع الأوامر على MEXC يعمل بشكل صحيح")
        else:
            print("\n❌ فشل اختبار وضع الأمر")
    else:
        print("\n❌ فشل اختبارات الأساس")
    
    print("\n" + "=" * 60)
    print("انتهى الاختبار")
    print("=" * 60)
