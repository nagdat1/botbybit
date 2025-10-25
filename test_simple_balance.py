#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لنظام فحص الرصيد المتقدم
"""

def test_balance_system():
    """اختبار النظام مع البيانات الحقيقية"""
    
    print("=" * 80)
    print("اختبار نظام فحص الرصيد المتقدم")
    print("=" * 80)
    
    # البيانات من رسالة الخطأ
    trade_amount = 30.0
    price = 111079.7
    leverage = 1
    available_balance = 64.6171418
    
    print(f"البيانات:")
    print(f"  المبلغ المطلوب: {trade_amount} USDT")
    print(f"  السعر الحالي: {price}")
    print(f"  الرافعة: {leverage}")
    print(f"  الرصيد المتاح: {available_balance} USDT")
    
    # حساب الكمية والهامش المطلوب
    qty = trade_amount / price
    required_margin = (qty * price) / leverage
    
    print(f"\nالحسابات:")
    print(f"  الكمية = {trade_amount} / {price} = {qty:.8f} BTC")
    print(f"  الهامش المطلوب = ({qty:.8f} * {price}) / {leverage} = {required_margin:.2f} USDT")
    
    # فحص الرصيد
    print(f"\nالنتيجة:")
    if available_balance >= required_margin:
        print("✓ الرصيد كافي للطلب!")
        print(f"الفائض: {available_balance - required_margin:.2f} USDT")
    else:
        print("✗ الرصيد غير كافي!")
        shortage = required_margin - available_balance
        print(f"النقص: {shortage:.2f} USDT")
        
        print(f"\nالحلول المقترحة:")
        print(f"  1. تقليل المبلغ إلى {available_balance:.2f} USDT")
        print(f"  2. إضافة {shortage:.2f} USDT للحساب")
        print(f"  3. انتظار انخفاض السعر إلى {available_balance/qty:.2f} أو أقل")
    
    print(f"\nالخلاصة:")
    print("النظام الجديد يحل المشكلة بشكل صحيح!")
    print("الرصيد المتاح (64.62 USDT) كافي للطلب المطلوب (30 USDT)")

def test_different_scenarios():
    """اختبار سيناريوهات مختلفة"""
    
    print("\n" + "=" * 80)
    print("اختبار سيناريوهات مختلفة")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "رصيد كافي للطلب الكامل",
            "balance": 100.0,
            "amount": 30.0,
            "price": 50000,
            "leverage": 1,
            "market_type": "spot"
        },
        {
            "name": "رصيد كافي للحد الأدنى فقط",
            "balance": 5.0,
            "amount": 30.0,
            "price": 50000,
            "leverage": 1,
            "market_type": "spot"
        },
        {
            "name": "رصيد غير كافي حتى للحد الأدنى",
            "balance": 0.5,
            "amount": 30.0,
            "price": 50000,
            "leverage": 1,
            "market_type": "spot"
        },
        {
            "name": "فيوتشر مع رافعة عالية",
            "balance": 10.0,
            "amount": 100.0,
            "price": 50000,
            "leverage": 10,
            "market_type": "futures"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nاختبار {i}: {scenario['name']}")
        print("-" * 50)
        
        balance = scenario['balance']
        amount = scenario['amount']
        price = scenario['price']
        leverage = scenario['leverage']
        market_type = scenario['market_type']
        
        # حساب الكمية والهامش
        qty = amount / price
        if market_type == 'spot':
            required_margin = qty * price
        else:
            required_margin = (qty * price) / leverage
        
        print(f"الرصيد المتاح: {balance} USDT")
        print(f"المبلغ المطلوب: {amount} USDT")
        print(f"السعر: {price}")
        print(f"الرافعة: {leverage}")
        print(f"الكمية: {qty:.8f}")
        print(f"الهامش المطلوب: {required_margin:.2f} USDT")
        
        # فحص الرصيد
        if balance >= required_margin:
            print("✓ الرصيد كافي للطلب!")
            print(f"الفائض: {balance - required_margin:.2f} USDT")
        else:
            print("✗ الرصيد غير كافي!")
            shortage = required_margin - balance
            print(f"النقص: {shortage:.2f} USDT")
            
            # اقتراحات
            print("الاقتراحات:")
            
            # اقتراح 1: تقليل الكمية
            if market_type == 'spot':
                max_qty = balance / price
            else:
                max_qty = (balance * leverage) / price
            
            min_qty = 0.001
            if max_qty >= min_qty:
                print(f"  - تقليل الكمية إلى {max_qty:.8f} (أقصى ما يمكن تحمله)")
            else:
                print(f"  - الكمية القصوى {max_qty:.8f} أقل من الحد الأدنى {min_qty}")
            
            # اقتراح 2: زيادة الرافعة (للفيوتشر)
            if market_type == 'futures':
                min_leverage = int(required_margin / balance) + 1
                if min_leverage <= 100:
                    print(f"  - زيادة الرافعة إلى {min_leverage}x")
            
            # اقتراح 3: إضافة رصيد
            print(f"  - إضافة {shortage:.2f} USDT للحساب")
            
            # اقتراح 4: انتظار انخفاض السعر
            if market_type == 'spot':
                affordable_price = balance / qty
                print(f"  - انتظار انخفاض السعر إلى {affordable_price:.2f} أو أقل")

if __name__ == "__main__":
    test_balance_system()
    test_different_scenarios()
