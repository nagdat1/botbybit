#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة التحقق من صحة التداول
تحتوي على وظائف للتحقق من صحة معلمات التداول وحالة الحساب
"""

from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

def validate_trade_parameters(symbol: str, action: str, amount: float, account_info: Dict) -> Tuple[bool, str]:
    """التحقق من صحة معلمات التداول"""
    try:
        # التحقق من الرمز
        if not symbol:
            return False, "❌ الرمز غير محدد"
            
        # التحقق من نوع الأمر
        if not action or action.lower() not in ['buy', 'sell']:
            return False, f"❌ نوع الأمر غير صالح: {action}"
            
        # التحقق من المبلغ
        if amount <= 0:
            return False, f"❌ المبلغ غير صالح: {amount}"
            
        # التحقق من الرصيد
        available_balance = account_info.get('availableBalance', 0)
        if amount > available_balance:
            return False, f"""❌ الرصيد غير كافي
💰 الرصيد المتاح: {available_balance:.2f} USDT
💳 المبلغ المطلوب: {amount:.2f} USDT"""
            
        return True, "✅ معلمات التداول صحيحة"
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من معلمات التداول: {e}")
        return False, f"❌ خطأ في التحقق من المعلمات: {str(e)}"

def validate_api_status(api) -> Tuple[bool, str]:
    """التحقق من حالة API"""
    try:
        if not api:
            return False, """❌ API غير متوفر

🔍 الحلول المقترحة:
1. تحقق من إضافة مفاتيح API في الإعدادات
2. تأكد من صلاحية المفاتيح
3. تأكد من تفعيل صلاحيات التداول"""
            
        # التحقق من صلاحيات التداول
        account_info = api.get_account_info()
        if account_info.get("retCode") != 0:
            error_msg = account_info.get("retMsg", "خطأ غير معروف")
            return False, f"""❌ خطأ في الاتصال بـ API

⚠️ السبب: {error_msg}

🔍 الحلول المقترحة:
1. تحقق من صحة مفاتيح API
2. تأكد من اتصال الإنترنت
3. راجع صلاحيات API في Bybit"""
            
        return True, "✅ API متصل ويعمل"
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من API: {e}")
        return False, f"""❌ خطأ غير متوقع في API

⚠️ السبب: {str(e)}

🔍 الحلول المقترحة:
1. تأكد من اتصال الإنترنت
2. حاول إعادة تسجيل الدخول
3. راجع سجلات البوت للمزيد من التفاصيل"""

def validate_leverage(leverage: int, symbol: str, market_type: str) -> Tuple[bool, str]:
    """التحقق من صحة الرافعة المالية"""
    try:
        if market_type == 'spot':
            return True, "✅ لا تحتاج الرافعة المالية في السبوت"
            
        if leverage <= 0:
            return False, "❌ الرافعة المالية يجب أن تكون أكبر من 0"
            
        # يمكن إضافة المزيد من التحقق حسب الرمز والسوق
        return True, "✅ الرافعة المالية صحيحة"
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من الرافعة: {e}")
        return False, f"❌ خطأ في التحقق من الرافعة: {str(e)}"

def validate_symbol_price(symbol: str, price: float, market_type: str) -> Tuple[bool, str]:
    """التحقق من صحة سعر الرمز"""
    try:
        if price <= 0:
            return False, """❌ السعر غير صالح

🔍 الحلول المقترحة:
1. تأكد من توفر السعر في السوق
2. انتظر تحديث السعر
3. جرب مرة أخرى لاحقاً"""
            
        return True, "✅ السعر صالح"
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من السعر: {e}")
        return False, f"❌ خطأ في التحقق من السعر: {str(e)}"