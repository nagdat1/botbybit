#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة إدارة الأخطاء
تحتوي على مدير معالجة الأخطاء المتعلقة بالتداول
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TradeErrorManager:
    def __init__(self):
        self.error_history: List[Dict] = []  # سجل الأخطاء
        self.max_retries = 3  # عدد المحاولات الأقصى
        self.error_counts: Dict[str, int] = {}  # عداد الأخطاء لكل نوع

    def handle_trade_error(self, error_type: str, error_message: str, symbol: str) -> str:
        """معالجة أخطاء التداول وتقديم حلول"""
        try:
            # تسجيل الخطأ
            error_entry = {
                'timestamp': datetime.now(),
                'type': error_type,
                'message': error_message,
                'symbol': symbol
            }
            self.error_history.append(error_entry)

            # تحديث عداد الأخطاء
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

            # إنشاء رسالة خطأ مع حلول مقترحة
            error_solution = self._get_error_solution(error_type, error_message)
            formatted_message = f"""❌ فشل في تنفيذ الصفقة

الرمز: {symbol}
نوع الخطأ: {error_type}
السبب: {error_message}

{error_solution}"""

            # تسجيل في السجلات
            logger.error(f"خطأ في التداول - {error_type}: {error_message} (الرمز: {symbol})")

            return formatted_message

        except Exception as e:
            logger.error(f"خطأ في معالجة الخطأ: {e}")
            return f"❌ خطأ غير متوقع: {str(e)}"

    def _get_error_solution(self, error_type: str, error_message: str) -> str:
        """الحصول على حلول مقترحة بناءً على نوع الخطأ"""
        solutions = {
            'insufficient_balance': """
🔍 الحلول المقترحة:
1. تأكد من وجود رصيد كافٍ في حسابك
2. قم بتقليل حجم الصفقة
3. أغلق بعض الصفقات المفتوحة لتحرير الرصيد""",
            
            'invalid_symbol': """
🔍 الحلول المقترحة:
1. تأكد من كتابة الرمز بشكل صحيح
2. تحقق من توفر الرمز في السوق المحدد
3. راجع قائمة الرموز المتاحة""",
            
            'api_error': """
🔍 الحلول المقترحة:
1. تحقق من صلاحيات API
2. تأكد من صحة المفاتيح
3. راجع إعدادات API في Bybit""",
            
            'network_error': """
🔍 الحلول المقترحة:
1. تحقق من اتصال الإنترنت
2. انتظر قليلاً ثم حاول مرة أخرى
3. تأكد من عدم وجود مشاكل في خدمة Bybit""",
            
            'validation_error': """
🔍 الحلول المقترحة:
1. تأكد من صحة معلمات الصفقة
2. راجع قيمة المبلغ والسعر
3. تحقق من نوع الأمر (شراء/بيع)""",
            
            'unknown': """
🔍 الحلول المقترحة:
1. حاول مرة أخرى
2. تحقق من سجلات البوت
3. تواصل مع الدعم إذا استمرت المشكلة"""
        }

        return solutions.get(error_type, solutions['unknown'])

    def should_retry(self, error_type: str) -> bool:
        """تحديد ما إذا كان يجب إعادة المحاولة"""
        current_count = self.error_counts.get(error_type, 0)
        return current_count < self.max_retries

    def clear_error_history(self):
        """مسح سجل الأخطاء"""
        self.error_history = []
        self.error_counts = {}