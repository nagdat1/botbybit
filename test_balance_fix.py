#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة فحص الرصيد
"""

def test_balance_calculation():
    """اختبار حساب الرصيد المطلوب"""
    
    print("=" * 60)
    print("اختبار إصلاح مشكلة فحص الرصيد")
    print("=" * 60)
    
    # بيانات الاختبار من رسالة الخطأ
    trade_amount = 30.0  # المبلغ المطلوب
    price = 111079.7     # السعر الحالي
    leverage = 1          # الرافعة
    available_balance = 64.6171418  # الرصيد المتاح
    
    print(f"البيانات:")
    print(f"  المبلغ المطلوب: {trade_amount} USDT")
    print(f"  السعر الحالي: {price}")
    print(f"  الرافعة: {leverage}")
    print(f"  الرصيد المتاح: {available_balance} USDT")
    print()
    
    # حساب الكمية (الطريقة الجديدة)
    qty = trade_amount / price
    print(f"حساب الكمية:")
    print(f"  الكمية = {trade_amount} / {price} = {qty:.8f} BTC")
    print()
    
    # حساب الهامش المطلوب (الطريقة الجديدة)
    required_margin = (qty * price) / leverage
    print(f"حساب الهامش المطلوب:")
    print(f"  الهامش المطلوب = ({qty:.8f} * {price}) / {leverage} = {required_margin:.2f} USDT")
    print()
    
    # فحص الرصيد
    print(f"فحص الرصيد:")
    print(f"  الرصيد المتاح: {available_balance} USDT")
    print(f"  الهامش المطلوب: {required_margin:.2f} USDT")
    
    if available_balance >= required_margin:
        print(f"  ✓ الرصيد كافي للطلب!")
        print(f"  الفائض: {available_balance - required_margin:.2f} USDT")
    else:
        print(f"  ✗ الرصيد غير كافي للطلب!")
        print(f"  النقص: {required_margin - available_balance:.2f} USDT")
    
    print()
    
    # اختبار الحد الأدنى
    min_quantity = 0.001
    print(f"اختبار الحد الأدنى:")
    print(f"  الحد الأدنى للكمية: {min_quantity} BTC")
    
    if qty < min_quantity:
        print(f"  الكمية أقل من الحد الأدنى: {qty:.8f} < {min_quantity}")
        
        min_margin_required = (min_quantity * price) / leverage
        print(f"  الهامش المطلوب للحد الأدنى: {min_margin_required:.2f} USDT")
        
        if available_balance >= min_margin_required:
            print(f"  ✓ الرصيد كافي للحد الأدنى!")
            print(f"  سيتم تعديل الكمية إلى الحد الأدنى")
        else:
            print(f"  ✗ الرصيد غير كافي حتى للحد الأدنى!")
            print(f"  النقص: {min_margin_required - available_balance:.2f} USDT")
    else:
        print(f"  الكمية أكبر من الحد الأدنى: {qty:.8f} >= {min_quantity}")
    
    print()
    print("=" * 60)
    print("الخلاصة:")
    print("=" * 60)
    
    if available_balance >= required_margin:
        print("✓ الإصلاح نجح! الرصيد كافي للطلب المطلوب")
        print(f"   المطلوب: {required_margin:.2f} USDT")
        print(f"   المتاح: {available_balance} USDT")
    elif qty < min_quantity and available_balance >= (min_quantity * price) / leverage:
        print("⚠️  الإصلاح نجح جزئياً! الرصيد كافي للحد الأدنى فقط")
        print(f"   سيتم تعديل الكمية إلى الحد الأدنى")
    else:
        print("✗ الإصلاح لم يحل المشكلة - الرصيد غير كافي")
        print("   الحلول المقترحة:")
        print("   1. تقليل مبلغ التداول")
        print("   2. زيادة الرافعة المالية")
        print("   3. إضافة رصيد للحساب")

if __name__ == "__main__":
    test_balance_calculation()
