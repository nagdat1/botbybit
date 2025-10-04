#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة تنفيذ التداول
تحتوي على منطق تنفيذ وإدارة الصفقات مع معالجة أفضل للأخطاء
"""

import logging
from typing import Dict, Tuple, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, api, account_type: str = 'spot'):
        self.api = api
        self.account_type = account_type

    async def validate_account_status(self) -> Tuple[bool, str]:
        """التحقق من حالة الحساب قبل التداول"""
        try:
            if not self.api:
                return False, """❌ لا يمكن تنفيذ الصفقة

السبب: API غير متوفر

🔍 الحلول المقترحة:
1. تحقق من إضافة مفاتيح API في الإعدادات
2. تأكد من صلاحية المفاتيح
3. تأكد من تفعيل صلاحيات التداول"""

            # التحقق من الرصيد
            balance_info = self.api.get_account_balance()
            if balance_info.get("retCode") != 0:
                error_msg = balance_info.get("retMsg", "خطأ غير معروف")
                return False, f"""❌ لا يمكن تنفيذ الصفقة

السبب: فشل في التحقق من الرصيد - {error_msg}

🔍 الحلول المقترحة:
1. تحقق من صلاحيات API
2. تأكد من اتصال الإنترنت
3. حاول مرة أخرى لاحقاً"""

            return True, "✅ الحساب جاهز للتداول"

        except Exception as e:
            logger.error(f"خطأ في التحقق من حالة الحساب: {e}")
            return False, f"""❌ خطأ في التحقق من حالة الحساب

⚠️ نوع الخطأ: {type(e).__name__}
📝 التفاصيل: {str(e)}

🔍 الحلول المقترحة:
1. تأكد من اتصال الإنترنت
2. تحقق من صحة مفاتيح API
3. راجع سجلات البوت للمزيد من التفاصيل"""

    async def validate_trade_parameters(self, symbol: str, action: str, amount: float, price: float) -> Tuple[bool, str]:
        """التحقق من معلمات الصفقة"""
        try:
            if not symbol:
                return False, """❌ لا يمكن تنفيذ الصفقة

السبب: الرمز غير محدد

🔍 الحل:
- تأكد من تحديد رمز التداول بشكل صحيح"""

            if not action or action.lower() not in ['buy', 'sell']:
                return False, f"""❌ لا يمكن تنفيذ الصفقة

السبب: نوع الأمر غير صالح ({action})

🔍 الحل:
- نوع الأمر يجب أن يكون buy أو sell"""

            if amount <= 0:
                return False, f"""❌ لا يمكن تنفيذ الصفقة

السبب: المبلغ غير صالح ({amount})

🔍 الحل:
- يجب أن يكون المبلغ أكبر من 0"""

            if price <= 0:
                return False, f"""❌ لا يمكن تنفيذ الصفقة

السبب: السعر غير صالح ({price})

🔍 الحل:
- تأكد من توفر سعر صالح للرمز"""

            return True, "✅ معلمات الصفقة صحيحة"

        except Exception as e:
            logger.error(f"خطأ في التحقق من معلمات الصفقة: {e}")
            return False, f"""❌ خطأ في التحقق من معلمات الصفقة

⚠️ نوع الخطأ: {type(e).__name__}
📝 التفاصيل: {str(e)}

🔍 الحلول المقترحة:
1. تأكد من صحة المعلمات المدخلة
2. حاول مرة أخرى
3. راجع سجلات البوت للمزيد من التفاصيل"""

    async def execute_trade(self, symbol: str, action: str, amount: float, price: float) -> Dict[str, Any]:
        """تنفيذ الصفقة مع معالجة محسنة للأخطاء"""
        try:
            # التحقق من حالة الحساب
            account_valid, account_error = await self.validate_account_status()
            if not account_valid:
                return {
                    "success": False,
                    "error": account_error,
                    "error_type": "account_status"
                }

            # التحقق من معلمات الصفقة
            params_valid, params_error = await self.validate_trade_parameters(symbol, action, amount, price)
            if not params_valid:
                return {
                    "success": False,
                    "error": params_error,
                    "error_type": "parameters"
                }

            # تنفيذ الصفقة
            side = "Buy" if action.lower() == "buy" else "Sell"
            category = "spot" if self.account_type == "spot" else "linear"

            response = self.api.place_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=str(amount),
                category=category
            )

            if response.get("retCode") == 0:
                order_id = response.get("result", {}).get("orderId", "")
                return {
                    "success": True,
                    "order_id": order_id,
                    "message": f"""✅ تم تنفيذ الصفقة بنجاح

📊 {symbol}
🔄 {side}
💰 المبلغ: {amount}
💲 السعر: {price:.6f}
🏪 السوق: {category.upper()}
🆔 رقم الأمر: {order_id}"""
                }
            else:
                error_msg = response.get("retMsg", "خطأ غير معروف")
                error_code = response.get("retCode")
                return {
                    "success": False,
                    "error": f"""❌ فشل في تنفيذ الصفقة

السبب: {error_msg}
رمز الخطأ: {error_code}

🔍 الحلول المقترحة:
1. تأكد من وجود رصيد كافٍ
2. تحقق من صلاحيات API
3. تأكد من صحة معلمات الصفقة
4. حاول مرة أخرى لاحقاً""",
                    "error_type": "api_error",
                    "error_code": error_code
                }

        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة: {e}")
            return {
                "success": False,
                "error": f"""❌ خطأ غير متوقع في تنفيذ الصفقة

⚠️ نوع الخطأ: {type(e).__name__}
📝 التفاصيل: {str(e)}

🔍 الحلول المقترحة:
1. تأكد من اتصال الإنترنت
2. تحقق من صحة إعدادات API
3. راجع سجلات البوت للمزيد من التفاصيل""",
                "error_type": "execution_error"
            }