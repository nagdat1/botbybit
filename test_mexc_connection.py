#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار الاتصال بمنصة MEXC
"""

import os
import sys
from dotenv import load_dotenv
from mexc_trading_bot import create_mexc_bot

def test_mexc_connection():
    """اختبار الاتصال بـ MEXC"""
    print("=" * 70)
    print("🧪 اختبار الاتصال بمنصة MEXC")
    print("=" * 70)
    
    # تحميل المتغيرات البيئية
    load_dotenv()
    
    # الحصول على المفاتيح
    api_key = os.getenv('MEXC_API_KEY', '')
    api_secret = os.getenv('MEXC_API_SECRET', '')
    
    print("\n📋 التحقق من الإعدادات...")
    
    if not api_key or not api_secret:
        print("❌ خطأ: لم يتم العثور على MEXC_API_KEY أو MEXC_API_SECRET")
        print("\n💡 الحل:")
        print("   1. أنشئ ملف .env في مجلد المشروع")
        print("   2. أضف السطور التالية:")
        print("      MEXC_API_KEY=your_api_key_here")
        print("      MEXC_API_SECRET=your_api_secret_here")
        print("\n📚 للمزيد من المعلومات، راجع README_MEXC.md")
        return False
    
    print(f"✅ تم العثور على API Key: {api_key[:10]}...")
    print(f"✅ تم العثور على API Secret: {api_secret[:10]}...")
    
    # إنشاء البوت
    print("\n🔧 إنشاء بوت MEXC...")
    try:
        bot = create_mexc_bot(api_key, api_secret)
        print("✅ تم إنشاء البوت بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إنشاء البوت: {e}")
        return False
    
    # اختبار الاتصال
    print("\n🔌 اختبار الاتصال بـ MEXC API...")
    if not bot.test_connection():
        print("❌ فشل الاتصال بـ MEXC API")
        print("\n💡 تحقق من:")
        print("   • صحة API Key و Secret")
        print("   • تفعيل API Key في حسابك على MEXC")
        print("   • صلاحيات API Key (يجب تفعيل Spot Trading)")
        print("   • الاتصال بالإنترنت")
        return False
    
    print("✅ الاتصال بـ MEXC API ناجح!")
    
    # عرض معلومات الحساب
    print("\n" + "=" * 70)
    print("💰 معلومات الحساب")
    print("=" * 70)
    
    balance = bot.get_account_balance()
    if balance:
        print(f"\n📊 الرصيد:")
        print(f"   • يمكن التداول: {'نعم' if balance['can_trade'] else 'لا'}")
        print(f"   • يمكن السحب: {'نعم' if balance['can_withdraw'] else 'لا'}")
        print(f"   • يمكن الإيداع: {'نعم' if balance['can_deposit'] else 'لا'}")
        
        print(f"\n💵 الأرصدة المتاحة:")
        has_balance = False
        for asset, info in balance['balances'].items():
            if info['total'] > 0:
                has_balance = True
                print(f"   • {asset}:")
                print(f"      - الإجمالي: {info['total']:.8f}")
                print(f"      - المتاح: {info['free']:.8f}")
                print(f"      - المحجوز: {info['locked']:.8f}")
        
        if not has_balance:
            print("   ⚠️ لا يوجد رصيد في الحساب")
    else:
        print("❌ فشل في الحصول على معلومات الحساب")
    
    # اختبار الحصول على الأسعار
    print("\n" + "=" * 70)
    print("📊 اختبار الحصول على الأسعار")
    print("=" * 70)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    for symbol in test_symbols:
        price = bot.get_ticker_price(symbol)
        if price:
            print(f"✅ {symbol}: ${price:,.2f}")
        else:
            print(f"❌ فشل في الحصول على سعر {symbol}")
    
    # اختبار معلومات الرمز
    print("\n" + "=" * 70)
    print("🔍 اختبار معلومات الرمز")
    print("=" * 70)
    
    symbol_info = bot.get_symbol_info('BTCUSDT')
    if symbol_info:
        print(f"\n📋 معلومات BTCUSDT:")
        print(f"   • الحالة: {symbol_info['status']}")
        print(f"   • العملة الأساسية: {symbol_info['base_asset']}")
        print(f"   • عملة التسعير: {symbol_info['quote_asset']}")
        print(f"   • التداول الفوري مسموح: {'نعم' if symbol_info['is_spot_trading_allowed'] else 'لا'}")
        print(f"   • الصلاحيات: {', '.join(symbol_info['permissions'])}")
    else:
        print("❌ فشل في الحصول على معلومات الرمز")
    
    # اختبار الأوامر المفتوحة
    print("\n" + "=" * 70)
    print("📝 الأوامر المفتوحة")
    print("=" * 70)
    
    open_orders = bot.get_open_orders()
    if open_orders is not None:
        if len(open_orders) > 0:
            print(f"\n✅ عدد الأوامر المفتوحة: {len(open_orders)}")
            for order in open_orders[:5]:  # عرض أول 5 أوامر فقط
                print(f"\n   📌 أمر {order['order_id']}:")
                print(f"      • الزوج: {order['symbol']}")
                print(f"      • النوع: {order['side']} {order['type']}")
                print(f"      • الكمية: {order['quantity']}")
                print(f"      • السعر: {order['price']}")
                print(f"      • الحالة: {order['status']}")
        else:
            print("✅ لا توجد أوامر مفتوحة")
    else:
        print("❌ فشل في الحصول على الأوامر المفتوحة")
    
    # ملخص النتائج
    print("\n" + "=" * 70)
    print("✅ اكتمل الاختبار بنجاح!")
    print("=" * 70)
    print("\n📝 ملاحظات:")
    print("   • MEXC تدعم التداول الفوري (Spot) فقط")
    print("   • لا يوجد دعم لتداول الفيوتشر عبر API")
    print("   • تأكد من تفعيل صلاحية Spot Trading في API Key")
    print("\n📚 للمزيد من المعلومات، راجع README_MEXC.md")
    
    return True


if __name__ == "__main__":
    try:
        success = test_mexc_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إلغاء الاختبار")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

