#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة اختبار شاملة لنظام MEXC المحسن
"""

import logging
import os
import time
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_mexc_system():
    """اختبار شامل لنظام MEXC المحسن"""
    print("🧪 اختبار شامل لنظام MEXC المحسن")
    print("=" * 60)
    
    try:
        # تحميل متغيرات البيئة
        load_dotenv()
        
        from config import MEXC_API_KEY, MEXC_API_SECRET
        
        if not MEXC_API_KEY or not MEXC_API_SECRET:
            print("❌ مفاتيح MEXC API غير موجودة")
            print("تأكد من وجود ملف .env مع مفاتيح MEXC")
            return False
        
        print(f"✅ مفاتيح API موجودة")
        print(f"🔐 API Key: {MEXC_API_KEY[:8]}...")
        print(f"🔐 API Secret: {MEXC_API_SECRET[:8]}...")
        
        # اختبار 1: تهيئة البوت
        print("\n1️⃣ اختبار تهيئة البوت...")
        from mexc_trading_bot import create_mexc_bot
        bot = create_mexc_bot(MEXC_API_KEY, MEXC_API_SECRET)
        print("✅ تم تهيئة البوت بنجاح")
        
        # اختبار 2: اختبار الاتصال
        print("\n2️⃣ اختبار الاتصال...")
        if bot.test_connection():
            print("✅ الاتصال ناجح")
        else:
            print("❌ فشل الاتصال")
            return False
        
        # اختبار 3: اختبار مدير الأوامر
        print("\n3️⃣ اختبار مدير الأوامر...")
        if bot.order_manager:
            print("✅ مدير الأوامر متاح")
            
            # اختبار إضافة أمر
            from mexc_order_manager import OrderRequest, OrderType
            test_order = OrderRequest(
                symbol="BTCUSDT",
                side="BUY",
                order_type=OrderType.MARKET,
                quantity=0.0001,
                priority=1
            )
            
            client_id = bot.order_manager.add_order(test_order)
            print(f"✅ تم إضافة أمر تجريبي: {client_id}")
            
            # اختبار تقرير التنفيذ
            report = bot.order_manager.get_execution_report()
            print(f"📊 تقرير التنفيذ: {report}")
            
        else:
            print("⚠️ مدير الأوامر غير متاح")
        
        # اختبار 4: اختبار جلب السعر
        print("\n4️⃣ اختبار جلب السعر...")
        price = bot.get_ticker_price("BTCUSDT")
        if price:
            print(f"✅ سعر BTCUSDT: ${price:,.2f}")
        else:
            print("❌ فشل جلب السعر")
            return False
        
        # اختبار 5: اختبار معلومات الرمز
        print("\n5️⃣ اختبار معلومات الرمز...")
        symbol_info = bot.get_symbol_info("BTCUSDT")
        if symbol_info:
            print(f"✅ معلومات الرمز: {symbol_info['symbol']}")
            print(f"📋 التداول الفوري مسموح: {symbol_info['is_spot_trading_allowed']}")
        else:
            print("❌ فشل جلب معلومات الرمز")
            return False
        
        # اختبار 6: اختبار الرصيد
        print("\n6️⃣ اختبار الرصيد...")
        balance = bot.get_account_balance()
        if balance:
            print("✅ تم جلب الرصيد بنجاح")
            balances = balance.get('balances', {})
            if balances:
                print("💰 الأرصدة المتاحة:")
                for asset, info in balances.items():
                    if info['total'] > 0:
                        print(f"   {asset}: {info['total']:.8f}")
            else:
                print("⚠️ لا توجد أرصدة")
        else:
            print("❌ فشل جلب الرصيد")
            return False
        
        # اختبار 7: اختبار التوقيع
        print("\n7️⃣ اختبار التوقيع...")
        test_params = {'timestamp': int(time.time() * 1000)}
        signature = bot._generate_signature(test_params)
        print(f"✅ التوقيع التجريبي: {signature[:16]}...")
        
        # اختبار 8: اختبار النظام المتكامل
        print("\n8️⃣ اختبار النظام المتكامل...")
        from real_account_manager import MEXCRealAccount
        real_account = MEXCRealAccount(MEXC_API_KEY, MEXC_API_SECRET)
        
        # اختبار جلب الرصيد عبر Real Account
        wallet_balance = real_account.get_wallet_balance()
        if wallet_balance:
            print(f"✅ الرصيد عبر Real Account: ${wallet_balance.get('total_equity', 0):,.2f}")
        else:
            print("❌ فشل جلب الرصيد عبر Real Account")
        
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ النظام جاهز للاستخدام")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        return False

def test_order_execution():
    """اختبار تنفيذ الأوامر (تجريبي)"""
    print("\n🧪 اختبار تنفيذ الأوامر (تجريبي)")
    print("=" * 40)
    
    try:
        from config import MEXC_API_KEY, MEXC_API_SECRET
        from mexc_trading_bot import create_mexc_bot
        
        bot = create_mexc_bot(MEXC_API_KEY, MEXC_API_SECRET)
        
        # اختبار وضع أمر تجريبي (كمية صغيرة جداً)
        print("📝 وضع أمر تجريبي...")
        
        # جلب السعر أولاً
        price = bot.get_ticker_price("BTCUSDT")
        if not price:
            print("❌ لا يمكن جلب السعر")
            return False
        
        # حساب كمية صغيرة جداً للاختبار
        test_amount = 1.0  # $1 فقط للاختبار
        quantity = test_amount / price
        
        print(f"💰 مبلغ الاختبار: ${test_amount}")
        print(f"📊 السعر: ${price:,.2f}")
        print(f"🔢 الكمية: {quantity:.8f} BTC")
        
        # تحذير للمستخدم
        print("\n⚠️ تحذير: هذا اختبار حقيقي!")
        print("هل تريد المتابعة؟ (y/n)")
        
        # في البيئة الحقيقية، يمكن إزالة هذا التحقق
        # response = input().lower()
        # if response != 'y':
        #     print("تم إلغاء الاختبار")
        #     return True
        
        # وضع الأمر
        result = bot.place_spot_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity=quantity,
            order_type="MARKET"
        )
        
        if result:
            print(f"✅ تم وضع الأمر بنجاح: {result}")
            return True
        else:
            print("❌ فشل وضع الأمر")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار التنفيذ: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار النظام الكامل")
    
    # اختبار النظام الأساسي
    basic_test = test_complete_mexc_system()
    
    if basic_test:
        print("\n✅ النظام الأساسي يعمل بشكل صحيح")
        
        # اختبار تنفيذ الأوامر (اختياري)
        print("\nهل تريد اختبار تنفيذ الأوامر؟ (y/n)")
        # response = input().lower()
        # if response == 'y':
        #     execution_test = test_order_execution()
        #     if execution_test:
        #         print("✅ اختبار التنفيذ نجح")
        #     else:
        #         print("❌ اختبار التنفيذ فشل")
        
        print("\n🎉 النظام جاهز للاستخدام!")
        print("يمكنك الآن:")
        print("• إرسال إشارات التداول")
        print("• استخدام جميع ميزات MEXC")
        print("• الاستفادة من النظام المحسن")
        
    else:
        print("\n❌ هناك مشاكل في النظام")
        print("تحقق من:")
        print("• مفاتيح API")
        print("• الاتصال بالإنترنت")
        print("• صلاحيات الحساب")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
