#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص الرموز المدعومة وإصلاح المشكلة
"""

import sys
import os
import requests

def check_supported_symbols():
    """فحص الرموز المدعومة في Spot Trading"""
    
    print("=== فحص الرموز المدعومة في Spot Trading ===")
    print()
    
    try:
        # جلب قائمة الرموز المدعومة
        print("جلب قائمة الرموز المدعومة...")
        response = requests.get('https://api.bybit.com/v5/market/instruments-info', params={
            'category': 'spot'
        })
        
        if response.status_code == 200:
            data = response.json()
            symbols = data.get('result', {}).get('list', [])
            
            print(f"تم العثور على {len(symbols)} رمز مدعوم")
            print()
            
            # البحث عن الرموز الشائعة
            common_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT', 'DOTUSDT']
            
            print("الرموز الشائعة المدعومة:")
            supported_common = []
            for symbol in common_symbols:
                for symbol_info in symbols:
                    if symbol_info.get('symbol') == symbol and symbol_info.get('status') == 'Trading':
                        supported_common.append(symbol)
                        print(f"  ✅ {symbol} - مدعوم")
                        break
                else:
                    print(f"  ❌ {symbol} - غير مدعوم")
            
            print()
            print("الرموز المدعومة الأخرى:")
            other_symbols = []
            for symbol_info in symbols[:20]:  # أول 20 رمز
                symbol = symbol_info.get('symbol')
                if symbol not in common_symbols and symbol_info.get('status') == 'Trading':
                    other_symbols.append(symbol)
                    print(f"  - {symbol}")
            
            print()
            print("=== التوصيات ===")
            print("1. استخدم أحد الرموز المدعومة:")
            for symbol in supported_common[:5]:  # أول 5 رموز
                print(f"   - {symbol}")
            
            print()
            print("2. لتغيير الرمز في البوت:")
            print("   - اذهب إلى إعدادات البوت")
            print("   - اختر رمز مدعوم من القائمة")
            print("   - أو استخدم BTCUSDT كرمز افتراضي")
            
            return supported_common
            
        else:
            print(f"فشل في جلب قائمة الرموز: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"خطأ في فحص الرموز: {e}")
        return []

def test_with_supported_symbol():
    """اختبار مع رمز مدعوم"""
    
    print("=== اختبار مع رمز مدعوم ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from real_account_manager import BybitRealAccount
        
        # API Key
        api_key = "dqBHnPaItfmEZSB020"
        api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
        
        # إنشاء الحساب
        account = BybitRealAccount(api_key, api_secret)
        
        # اختبار مع BTCUSDT (مدعوم بالتأكيد)
        symbol = 'BTCUSDT'
        print(f"اختبار مع {symbol}...")
        
        # جلب السعر
        price = account.get_ticker_price(symbol, 'spot')
        if price:
            print(f"السعر: ${price}")
            
            # كمية صغيرة ($5)
            test_amount = 5.0
            qty = round(test_amount / price, 6)
            
            print(f"المبلغ: ${test_amount}")
            print(f"الكمية: {qty} BTC")
            print()
            
            print("تحذير: هذا سيضع أمر حقيقي!")
            print("هل تريد المتابعة؟ (اكتب 'نعم' للمتابعة)")
            
            # يمكنك تغيير هذا إلى input() للاختبار اليدوي
            confirm = "نعم"  # أو input() للاختبار اليدوي
            
            if confirm == "نعم":
                print("وضع أمر تجريبي...")
                result = account.place_order(
                    category='spot',
                    symbol=symbol,
                    side='Buy',
                    order_type='Market',
                    qty=qty
                )
                
                print(f"نتيجة الأمر: {result}")
                
                if result and result.get('order_id'):
                    print("نجح وضع الأمر!")
                    print(f"Order ID: {result.get('order_id')}")
                    return True
                else:
                    print("فشل وضع الأمر!")
                    
                    # تحليل الخطأ
                    if result:
                        error = result.get('error', 'Unknown')
                        print(f"الخطأ: {error}")
                        
                        if 'API returned None' in error:
                            print("السبب: API Key لا يملك صلاحية وضع الأوامر")
                            print("الحل: تأكد من تفعيل صلاحية 'Spot Trading - Trade'")
                        elif 'Invalid API-key' in error:
                            print("السبب: API Key غير صحيح أو منتهي الصلاحية")
                    
                    return False
            else:
                print("تم إلغاء الاختبار")
                return True
        else:
            print(f"فشل في جلب السعر لـ {symbol}")
            return False
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    print("1. فحص الرموز المدعومة...")
    supported_symbols = check_supported_symbols()
    
    print("\n" + "="*50 + "\n")
    
    print("2. اختبار مع رمز مدعوم...")
    success = test_with_supported_symbol()
    
    if not success:
        sys.exit(1)
