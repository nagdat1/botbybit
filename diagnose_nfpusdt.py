#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشخيص مشكلة NFPUSDT
"""

import sys
import os

def diagnose_nfpusdt_issue():
    """تشخيص مشكلة NFPUSDT"""
    
    print("=== تشخيص مشكلة NFPUSDT ===")
    print()
    
    try:
        # استيراد المكونات المطلوبة
        from real_account_manager import BybitRealAccount
        
        print("تم استيراد المكونات بنجاح")
        print()
        
        # API Key
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
        
        # اختبار 1: فحص الرمز NFPUSDT
        print("اختبار 1: فحص الرمز NFPUSDT...")
        try:
            price = account.get_ticker_price('NFPUSDT', 'spot')
            if price:
                print(f"نجح: السعر = ${price}")
            else:
                print("فشل: لم يتم العثور على الرمز NFPUSDT")
                print("السبب المحتمل: الرمز غير مدعوم في Spot Trading")
                return False
        except Exception as e:
            print(f"خطأ: {e}")
            return False
        print()
        
        # اختبار 2: فحص الرموز المدعومة
        print("اختبار 2: فحص الرموز المدعومة...")
        try:
            import requests
            
            # جلب قائمة الرموز المدعومة
            response = requests.get('https://api.bybit.com/v5/market/instruments-info', params={
                'category': 'spot'
            })
            
            if response.status_code == 200:
                data = response.json()
                symbols = data.get('result', {}).get('list', [])
                
                # البحث عن NFPUSDT
                nfpusdt_found = False
                for symbol_info in symbols:
                    if symbol_info.get('symbol') == 'NFPUSDT':
                        nfpusdt_found = True
                        print(f"تم العثور على NFPUSDT: {symbol_info}")
                        break
                
                if not nfpusdt_found:
                    print("NFPUSDT غير مدعوم في Spot Trading")
                    print("الرموز المدعومة تشمل:")
                    for symbol_info in symbols[:10]:  # أول 10 رموز
                        print(f"  - {symbol_info.get('symbol')}")
                    return False
                else:
                    print("NFPUSDT مدعوم في Spot Trading")
            else:
                print(f"فشل في جلب قائمة الرموز: {response.status_code}")
        except Exception as e:
            print(f"خطأ في فحص الرموز: {e}")
        print()
        
        # اختبار 3: أمر تجريبي مع NFPUSDT
        print("اختبار 3: أمر تجريبي مع NFPUSDT...")
        try:
            # كمية صغيرة ($5)
            test_amount = 5.0
            qty = round(test_amount / price, 6)
            
            print(f"المبلغ: ${test_amount}")
            print(f"السعر: ${price}")
            print(f"الكمية: {qty} NFP")
            print()
            
            print("تحذير: هذا سيضع أمر حقيقي!")
            print("هل تريد المتابعة؟ (اكتب 'نعم' للمتابعة)")
            
            # يمكنك تغيير هذا إلى input() للاختبار اليدوي
            confirm = "نعم"  # أو input() للاختبار اليدوي
            
            if confirm == "نعم":
                print("وضع أمر تجريبي...")
                result = account.place_order(
                    category='spot',
                    symbol='NFPUSDT',
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
                
        except Exception as e:
            print(f"خطأ في وضع الأمر: {e}")
            return False
        
    except Exception as e:
        print(f"خطأ في التشخيص: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_nfpusdt_issue()
    if not success:
        sys.exit(1)
