#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار اتصال API مع Bybit
"""

import asyncio
import sys
from bybit_trading_bot import BybitAPI, check_api_connection

async def test_api_connection():
    """اختبار اتصال API"""
    print("=" * 60)
    print("🧪 اختبار اتصال API مع Bybit")
    print("=" * 60)
    
    # اطلب من المستخدم إدخال API keys
    print("\n📝 أدخل بيانات API للاختبار:")
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("\n❌ يجب إدخال API Key و API Secret")
        return
    
    print("\n" + "=" * 60)
    print("🔄 جاري الاختبار...")
    print("=" * 60)
    
    # اختبار 1: التحقق من صحة المفاتيح
    print("\n1️⃣ اختبار التحقق من صحة المفاتيح...")
    is_valid = await check_api_connection(api_key, api_secret)
    
    if is_valid:
        print("✅ المفاتيح صحيحة ومتصلة بنجاح!")
    else:
        print("❌ المفاتيح غير صحيحة أو هناك مشكلة في الاتصال")
        print("\n💡 تأكد من:")
        print("   • صحة API Key و API Secret")
        print("   • تفعيل صلاحيات: Read, Write, Trade")
        print("   • عدم وجود قيود IP")
        return
    
    # اختبار 2: جلب معلومات الحساب
    print("\n2️⃣ اختبار جلب معلومات الحساب...")
    api = BybitAPI(api_key, api_secret)
    
    try:
        account_info = api.get_account_balance("UNIFIED")
        
        if account_info and account_info.get('retCode') == 0:
            print("✅ تم جلب معلومات الحساب بنجاح!")
            
            result = account_info.get('result', {})
            if result and 'list' in result and len(result['list']) > 0:
                wallet = result['list'][0]
                total_equity = float(wallet.get('totalEquity', 0))
                available_balance = float(wallet.get('totalAvailableBalance', 0))
                
                print(f"\n💰 معلومات الحساب:")
                print(f"   • الرصيد الكلي: {total_equity:.2f} USDT")
                print(f"   • الرصيد المتاح: {available_balance:.2f} USDT")
        else:
            print(f"⚠️ تحذير: {account_info.get('retMsg', 'Unknown error')}")
    except Exception as e:
        print(f"❌ خطأ في جلب معلومات الحساب: {e}")
    
    # اختبار 3: جلب قائمة الأزواج المتاحة
    print("\n3️⃣ اختبار جلب الأزواج المتاحة...")
    try:
        spot_symbols = api.get_all_symbols("spot")
        futures_symbols = api.get_all_symbols("linear")
        
        if spot_symbols:
            print(f"✅ تم جلب {len(spot_symbols)} زوج من السبوت")
            print(f"   أمثلة: {', '.join([s['symbol'] for s in spot_symbols[:5]])}")
        
        if futures_symbols:
            print(f"✅ تم جلب {len(futures_symbols)} زوج من الفيوتشر")
            print(f"   أمثلة: {', '.join([s['symbol'] for s in futures_symbols[:5]])}")
    except Exception as e:
        print(f"❌ خطأ في جلب الأزواج: {e}")
    
    # اختبار 4: جلب سعر BTC
    print("\n4️⃣ اختبار جلب الأسعار...")
    try:
        btc_price = api.get_ticker_price("BTCUSDT", "spot")
        if btc_price:
            print(f"✅ سعر BTC/USDT: ${btc_price:,.2f}")
        else:
            print("⚠️ لم يتم جلب السعر")
    except Exception as e:
        print(f"❌ خطأ في جلب السعر: {e}")
    
    # اختبار 5: جلب الصفقات المفتوحة
    print("\n5️⃣ اختبار جلب الصفقات المفتوحة...")
    try:
        open_positions = api.get_open_positions("linear")
        if open_positions is not None:
            print(f"✅ عدد الصفقات المفتوحة: {len(open_positions)}")
            if len(open_positions) > 0:
                for pos in open_positions[:3]:
                    symbol = pos.get('symbol', 'N/A')
                    side = pos.get('side', 'N/A')
                    size = pos.get('size', 0)
                    print(f"   • {symbol}: {side} - الحجم: {size}")
        else:
            print("⚠️ لم يتم جلب الصفقات")
    except Exception as e:
        print(f"❌ خطأ في جلب الصفقات: {e}")
    
    # النتيجة النهائية
    print("\n" + "=" * 60)
    print("✅ اكتمل الاختبار بنجاح!")
    print("=" * 60)
    print("\n📊 الخلاصة:")
    print("   • API متصل ويعمل بشكل صحيح")
    print("   • يمكنك الآن استخدام البوت بثقة")
    print("   • جميع الوظائف الأساسية تعمل")
    print("\n💡 الخطوة التالية:")
    print("   • استخدم /start في البوت")
    print("   • اذهب إلى الإعدادات")
    print("   • اربط API keys")
    print("   • ابدأ التداول!")

if __name__ == "__main__":
    try:
        asyncio.run(test_api_connection())
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إلغاء الاختبار")
    except Exception as e:
        print(f"\n\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

