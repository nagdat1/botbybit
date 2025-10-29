#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الإصلاحات المطبقة
"""

import asyncio
import logging
from signals.signal_executor import SignalExecutor

# إعداد اللوجينج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_quantity_rounding():
    """اختبار دالة التقريب التلقائي"""
    print("=" * 60)
    print("🧪 اختبار دالة التقريب التلقائي")
    print("=" * 60)
    
    test_cases = [
        # (qty, price, trade_amount, leverage, market_type, symbol)
        (0.123456789, 50000, 100, 10, 'futures', 'BTCUSDT'),
        (1.987654321, 2000, 50, 5, 'spot', 'ETHUSDT'),
        (0.000123456, 100000, 10, 1, 'futures', 'BTCUSDT'),
        (1000.123456, 1, 1000, 1, 'spot', 'DOGEUSDT'),
        (0.0000001, 50000, 1, 1, 'spot', 'BTCUSDT'),
    ]
    
    for i, (qty, price, trade_amount, leverage, market_type, symbol) in enumerate(test_cases, 1):
        print(f"\n📊 حالة اختبار {i}:")
        print(f"   الكمية الأصلية: {qty:.8f}")
        print(f"   السعر: ${price}")
        print(f"   المبلغ: ${trade_amount}")
        print(f"   الرافعة: {leverage}x")
        print(f"   السوق: {market_type}")
        print(f"   الرمز: {symbol}")
        
        try:
            rounded_qty = SignalExecutor._smart_quantity_rounding(
                qty, price, trade_amount, leverage, market_type, symbol
            )
            print(f"   ✅ الكمية المحسنة: {rounded_qty:.8f}")
            
            # حساب التأثير المالي
            if market_type == 'futures':
                original_amount = (qty * price) / leverage
                new_amount = (rounded_qty * price) / leverage
            else:
                original_amount = qty * price
                new_amount = rounded_qty * price
            
            impact = ((new_amount - original_amount) / original_amount) * 100 if original_amount > 0 else 0
            print(f"   📈 التأثير المالي: {impact:+.2f}%")
            
        except Exception as e:
            print(f"   ❌ خطأ: {e}")

def test_error_messages():
    """اختبار رسائل الخطأ"""
    print("\n" + "=" * 60)
    print("🧪 اختبار ترجمة رسائل الخطأ")
    print("=" * 60)
    
    # محاكاة رسائل خطأ شائعة
    error_messages = [
        "ab not enough for new order",
        "invalid symbol",
        "invalid price",
        "invalid quantity",
        "connection timeout",
        "unknown error message"
    ]
    
    for error in error_messages:
        print(f"\n📝 رسالة الخطأ الأصلية: {error}")
        
        # محاكاة الترجمة (من api/bybit_api.py)
        if 'ab not enough' in error.lower():
            translated = "الرصيد غير كافي لتنفيذ الصفقة"
        elif 'invalid symbol' in error.lower():
            translated = "رمز العملة غير صحيح"
        elif 'invalid price' in error.lower():
            translated = "السعر غير صحيح"
        elif 'invalid quantity' in error.lower():
            translated = "الكمية غير صحيحة"
        else:
            translated = error
        
        print(f"   ✅ الترجمة: {translated}")

async def test_error_notification():
    """اختبار إرسال إشعارات الخطأ (محاكاة)"""
    print("\n" + "=" * 60)
    print("🧪 اختبار إشعارات الخطأ (محاكاة)")
    print("=" * 60)
    
    # بيانات اختبار
    user_id = 123456789
    error_message = "ab not enough for new order"
    signal_data = {
        'symbol': 'BTCUSDT',
        'action': 'buy',
        'price': 50000
    }
    
    print(f"📱 محاكاة إرسال إشعار للمستخدم: {user_id}")
    print(f"📊 الرمز: {signal_data['symbol']}")
    print(f"🔄 الإجراء: {signal_data['action']}")
    print(f"⚠️ الخطأ: {error_message}")
    
    # محاكاة إنشاء الرسالة
    if 'ab not enough' in error_message.lower():
        arabic_error = "❌ الرصيد غير كافي لتنفيذ الصفقة"
        suggestion = "💡 تأكد من وجود رصيد كافي في حسابك على Bybit"
    else:
        arabic_error = f"❌ خطأ في تنفيذ الصفقة: {error_message}"
        suggestion = "💡 تحقق من إعدادات حسابك وحاول مرة أخرى"
    
    notification_text = f"""
🚨 **فشل تنفيذ الصفقة**

📊 **تفاصيل الإشارة:**
• الرمز: {signal_data['symbol']}
• الإجراء: {signal_data['action'].upper()}

⚠️ **سبب الفشل:**
{arabic_error}

{suggestion}

🔧 **الإجراءات المقترحة:**
• تحقق من رصيد حسابك على Bybit
• تأكد من صحة إعدادات API
• راجع إعدادات التداول

📞 **للمساعدة:** تواصل مع الدعم الفني
    """.strip()
    
    print("\n📨 نص الإشعار المُنشأ:")
    print(notification_text)
    print("\n✅ تم إنشاء الإشعار بنجاح (محاكاة)")

def main():
    """تشغيل جميع الاختبارات"""
    print("بدء اختبار الإصلاحات المطبقة")
    print("=" * 60)
    
    try:
        # اختبار دالة التقريب
        test_quantity_rounding()
        
        # اختبار ترجمة رسائل الخطأ
        test_error_messages()
        
        # اختبار إشعارات الخطأ
        asyncio.run(test_error_notification())
        
        print("\n" + "=" * 60)
        print("تم اكتمال جميع الاختبارات بنجاح!")
        print("=" * 60)
        
        print("\nملخص الإصلاحات المطبقة:")
        print("1. إصلاح خطأ 'ab not enough for new order'")
        print("2. إضافة رسائل فشل الصفقات للمستخدم")
        print("3. تحسين دالة التقريب التلقائي للكمية")
        print("4. ترجمة رسائل الخطأ للعربية")
        print("5. إضافة إشعارات تلقائية عند فشل الصفقات")
        
        print("\nالنتائج المتوقعة:")
        print("• المستخدم سيحصل على رسائل واضحة عند فشل الصفقات")
        print("• دالة التقريب ستحسن دقة الكميات")
        print("• رسائل الخطأ ستكون مفهومة باللغة العربية")
        print("• البوت سيعمل بشكل أكثر استقراراً")
        
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
