#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص المشاكل الأخرى المحتملة إذا كانت الصلاحيات مفعلة
"""

import sys
import os

def check_other_possible_issues():
    """فحص المشاكل الأخرى المحتملة"""
    
    print("=== فحص المشاكل الأخرى المحتملة ===")
    print()
    
    print("إذا كانت الصلاحيات كلها مفعلة، فالمشكلة قد تكون في:")
    print()
    
    print("1. نوع الحساب:")
    print("   - تأكد من أن حسابك يدعم Spot Trading")
    print("   - بعض الحسابات تدعم فقط Futures")
    print("   - تحقق من نوع حسابك في Bybit")
    print()
    
    print("2. حالة الحساب:")
    print("   - تأكد من تفعيل حسابك بالكامل")
    print("   - تأكد من إكمال التحقق من الهوية (KYC)")
    print("   - تأكد من عدم وجود قيود على الحساب")
    print()
    
    print("3. الرصيد:")
    print("   - تأكد من وجود رصيد كافٍ في Spot Wallet")
    print("   - الرصيد الحالي: $64.89 USDT")
    print("   - قد تحتاج إلى تحويل رصيد من Unified إلى Spot")
    print()
    
    print("4. قيود التداول:")
    print("   - تأكد من عدم وجود قيود على التداول")
    print("   - تأكد من عدم وجود قيود على الرموز")
    print("   - تأكد من عدم وجود قيود على المبالغ")
    print()
    
    print("5. إعدادات API Key:")
    print("   - تأكد من عدم وجود قيود IP")
    print("   - تأكد من عدم وجود قيود على الرموز")
    print("   - تأكد من عدم وجود قيود على المبالغ")
    print()
    
    print("6. مشاكل تقنية:")
    print("   - تأكد من عدم وجود مشاكل في الشبكة")
    print("   - تأكد من عدم وجود مشاكل في الخادم")
    print("   - جرب إعادة تشغيل البوت")
    print()
    
    print("الخطوات للتحقق:")
    print()
    print("الخطوة 1: تحقق من نوع الحساب")
    print("- اذهب إلى Bybit.com")
    print("- تحقق من نوع حسابك")
    print("- تأكد من دعم Spot Trading")
    print()
    
    print("الخطوة 2: تحقق من الرصيد")
    print("- اذهب إلى Wallet")
    print("- تحقق من رصيد Spot Wallet")
    print("- إذا كان فارغاً، حول رصيد من Unified")
    print()
    
    print("الخطوة 3: تحقق من إعدادات API Key")
    print("- اذهب إلى API Management")
    print("- تحقق من إعدادات API Key")
    print("- تأكد من عدم وجود قيود")
    print()
    
    print("الخطوة 4: اختبار مباشر")
    print("- جرب وضع أمر مباشرة من واجهة Bybit")
    print("- إذا نجح، المشكلة في الكود")
    print("- إذا فشل، المشكلة في الحساب")
    print()
    
    print("الخطوة 5: إنشاء API Key جديد")
    print("- احذف API Key الحالي")
    print("- أنشئ API Key جديد")
    print("- اختبره مباشرة")
    print()
    
    print("الاحتمالات الأكثر شيوعاً:")
    print("1. الحساب لا يدعم Spot Trading")
    print("2. الرصيد في Unified وليس في Spot")
    print("3. قيود على الحساب")
    print("4. مشاكل في إعدادات API Key")
    print()
    
    print("الحل الأسرع:")
    print("1. تحقق من رصيد Spot Wallet")
    print("2. حول رصيد من Unified إلى Spot")
    print("3. جرب وضع أمر مباشرة من واجهة Bybit")
    print("4. إذا نجح، المشكلة في الكود")
    print("5. إذا فشل، المشكلة في الحساب")
    print()
    
    return True

if __name__ == "__main__":
    success = check_other_possible_issues()
    if not success:
        sys.exit(1)