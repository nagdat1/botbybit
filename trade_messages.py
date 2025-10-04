#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الرسائل التفاعلية للصفقات
يدعم عرض معلومات الصفقة مع أزرار TP, SL, الإغلاق الجزئي والكامل
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeMessageManager:
    """مدير الرسائل التفاعلية للصفقات"""
    
    def __init__(self):
        # إعدادات افتراضية للنسب
        self.default_tp_percents = [1, 2, 5]  # نسب TP الافتراضية
        self.default_sl_percents = [1, 2, 3]  # نسب SL الافتراضية  
        self.default_partial_percents = [25, 50, 75]  # نسب الإغلاق الجزئي الافتراضية
    
    def create_trade_message(self, position_info: Dict, user_settings: Dict = None) -> tuple[str, InlineKeyboardMarkup]:
        """
        إنشاء رسالة تفاعلية للصفقة مع الأزرار
        
        Args:
            position_info: معلومات الصفقة
            user_settings: إعدادات المستخدم للنسب المخصصة
            
        Returns:
            tuple: (رسالة النص, لوحة الأزرار)
        """
        try:
            # الحصول على معلومات الصفقة
            symbol = position_info.get('symbol', 'N/A')
            side = position_info.get('side', 'N/A')
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', entry_price)
            position_id = position_info.get('position_id', 'N/A')
            market_type = position_info.get('account_type', 'spot')
            
            # حساب الربح/الخسارة
            pnl_value, pnl_percent = self._calculate_pnl(position_info)
            
            # تحديد مؤشرات بصرية
            pnl_emoji = "🟢💰" if pnl_value >= 0 else "🔴💸"
            pnl_status = "رابح" if pnl_value >= 0 else "خاسر"
            arrow = "⬆️" if pnl_value >= 0 else "⬇️"
            
            # بناء رسالة الصفقة
            message = f"""
{pnl_emoji} **{symbol}** - {side.upper()}
{arrow} **الربح/الخسارة:** {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}

📊 **معلومات الصفقة:**
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
🏪 نوع السوق: {market_type.upper()}
🆔 رقم الصفقة: {position_id}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # إضافة معلومات إضافية للفيوتشر
            if market_type == 'futures':
                leverage = position_info.get('leverage', 1)
                margin_amount = position_info.get('margin_amount', 0)
                liquidation_price = position_info.get('liquidation_price', 0)
                
                message += f"""
⚡ الرافعة: {leverage}x
💰 الهامش المحجوز: {margin_amount:.2f}
⚠️ سعر التصفية: {liquidation_price:.6f}
                """
            
            # إنشاء لوحة الأزرار
            keyboard = self._create_trade_keyboard(position_id, user_settings)
            
            return message.strip(), keyboard
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الصفقة: {e}")
            error_message = f"❌ خطأ في عرض معلومات الصفقة: {e}"
            return error_message, InlineKeyboardMarkup([])
    
    def _calculate_pnl(self, position_info: Dict) -> tuple[float, float]:
        """حساب الربح/الخسارة"""
        try:
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', entry_price)
            side = position_info.get('side', 'buy')
            
            if entry_price == 0:
                return 0.0, 0.0
            
            # حساب النسبة المئوية
            if side.lower() == "buy":
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            # حساب القيمة المالية (تقريبي)
            margin_amount = position_info.get('margin_amount', position_info.get('amount', 100))
            pnl_value = (pnl_percent / 100) * margin_amount
            
            return pnl_value, pnl_percent
            
        except Exception as e:
            logger.error(f"خطأ في حساب PnL: {e}")
            return 0.0, 0.0
    
    def _create_trade_keyboard(self, position_id: str, user_settings: Dict = None) -> InlineKeyboardMarkup:
        """إنشاء لوحة أزرار الصفقة"""
        try:
            keyboard = []
            
            # الحصول على النسب من إعدادات المستخدم أو استخدام الافتراضية
            if user_settings:
                tp_percents = user_settings.get('tps_percents', self.default_tp_percents)
                sl_percents = user_settings.get('sl_percents', self.default_sl_percents)
                partial_percents = user_settings.get('partial_percents', self.default_partial_percents)
            else:
                tp_percents = self.default_tp_percents
                sl_percents = self.default_sl_percents
                partial_percents = self.default_partial_percents
            
            # أزرار TP (Take Profit)
            tp_row = []
            for percent in tp_percents:
                tp_row.append(InlineKeyboardButton(
                    f"🎯 TP {percent}%", 
                    callback_data=f"tp_{position_id}_{percent}"
                ))
            keyboard.append(tp_row)
            
            # أزرار SL (Stop Loss)
            sl_row = []
            for percent in sl_percents:
                sl_row.append(InlineKeyboardButton(
                    f"🛑 SL {percent}%", 
                    callback_data=f"sl_{position_id}_{percent}"
                ))
            keyboard.append(sl_row)
            
            # أزرار الإغلاق الجزئي
            partial_row = []
            for percent in partial_percents:
                partial_row.append(InlineKeyboardButton(
                    f"📊 {percent}%", 
                    callback_data=f"partial_{position_id}_{percent}"
                ))
            keyboard.append(partial_row)
            
            # زر الإغلاق الكامل
            keyboard.append([InlineKeyboardButton(
                "❌ إغلاق كامل", 
                callback_data=f"close_{position_id}"
            )])
            
            # أزرار إضافية
            keyboard.append([
                InlineKeyboardButton("⚙️ تعديل النسب", callback_data=f"edit_{position_id}_percents"),
                InlineKeyboardButton("🔄 تحديث", callback_data=f"refresh_{position_id}")
            ])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة الأزرار: {e}")
            return InlineKeyboardMarkup([])
    
    def create_percent_edit_keyboard(self, position_id: str, current_settings: Dict = None) -> InlineKeyboardMarkup:
        """إنشاء لوحة تعديل النسب"""
        try:
            keyboard = []
            
            # أزرار تعديل نسب TP
            keyboard.append([InlineKeyboardButton(
                "🎯 تعديل نسب TP", 
                callback_data=f"edit_{position_id}_tp"
            )])
            
            # أزرار تعديل نسب SL
            keyboard.append([InlineKeyboardButton(
                "🛑 تعديل نسب SL", 
                callback_data=f"edit_{position_id}_sl"
            )])
            
            # أزرار تعديل نسب الإغلاق الجزئي
            keyboard.append([InlineKeyboardButton(
                "📊 تعديل نسب الإغلاق الجزئي", 
                callback_data=f"edit_{position_id}_partial"
            )])
            
            # زر العودة
            keyboard.append([InlineKeyboardButton(
                "🔙 العودة", 
                callback_data=f"back_to_trade_{position_id}"
            )])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة تعديل النسب: {e}")
            return InlineKeyboardMarkup([])
    
    def create_tp_edit_keyboard(self, position_id: str) -> InlineKeyboardMarkup:
        """إنشاء لوحة تعديل نسب TP"""
        try:
            keyboard = []
            
            # النسب المقترحة
            suggested_tps = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
            
            # تنظيم الأزرار في صفوف
            for i in range(0, len(suggested_tps), 3):
                row = []
                for j in range(i, min(i + 3, len(suggested_tps))):
                    percent = suggested_tps[j]
                    row.append(InlineKeyboardButton(
                        f"{percent}%", 
                        callback_data=f"set_tp_{position_id}_{percent}"
                    ))
                keyboard.append(row)
            
            # زر إدخال مخصص
            keyboard.append([InlineKeyboardButton(
                "✏️ إدخال مخصص", 
                callback_data=f"custom_tp_{position_id}"
            )])
            
            # زر العودة
            keyboard.append([InlineKeyboardButton(
                "🔙 العودة", 
                callback_data=f"edit_{position_id}_percents"
            )])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة تعديل TP: {e}")
            return InlineKeyboardMarkup([])
    
    def create_sl_edit_keyboard(self, position_id: str) -> InlineKeyboardMarkup:
        """إنشاء لوحة تعديل نسب SL"""
        try:
            keyboard = []
            
            # النسب المقترحة لـ SL (أصغر من TP عادة)
            suggested_sls = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
            
            # تنظيم الأزرار في صفوف
            for i in range(0, len(suggested_sls), 3):
                row = []
                for j in range(i, min(i + 3, len(suggested_sls))):
                    percent = suggested_sls[j]
                    row.append(InlineKeyboardButton(
                        f"{percent}%", 
                        callback_data=f"set_sl_{position_id}_{percent}"
                    ))
                keyboard.append(row)
            
            # زر إدخال مخصص
            keyboard.append([InlineKeyboardButton(
                "✏️ إدخال مخصص", 
                callback_data=f"custom_sl_{position_id}"
            )])
            
            # زر العودة
            keyboard.append([InlineKeyboardButton(
                "🔙 العودة", 
                callback_data=f"edit_{position_id}_percents"
            )])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة تعديل SL: {e}")
            return InlineKeyboardMarkup([])
    
    def create_partial_edit_keyboard(self, position_id: str) -> InlineKeyboardMarkup:
        """إنشاء لوحة تعديل نسب الإغلاق الجزئي"""
        try:
            keyboard = []
            
            # النسب المقترحة للإغلاق الجزئي
            suggested_partials = [10, 15, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90]
            
            # تنظيم الأزرار في صفوف
            for i in range(0, len(suggested_partials), 3):
                row = []
                for j in range(i, min(i + 3, len(suggested_partials))):
                    percent = suggested_partials[j]
                    row.append(InlineKeyboardButton(
                        f"{percent}%", 
                        callback_data=f"set_partial_{position_id}_{percent}"
                    ))
                keyboard.append(row)
            
            # زر إدخال مخصص
            keyboard.append([InlineKeyboardButton(
                "✏️ إدخال مخصص", 
                callback_data=f"custom_partial_{position_id}"
            )])
            
            # زر العودة
            keyboard.append([InlineKeyboardButton(
                "🔙 العودة", 
                callback_data=f"edit_{position_id}_percents"
            )])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة تعديل الإغلاق الجزئي: {e}")
            return InlineKeyboardMarkup([])
    
    def create_confirmation_message(self, action: str, position_id: str, percent: float = None) -> tuple[str, InlineKeyboardMarkup]:
        """إنشاء رسالة تأكيد العملية"""
        try:
            symbol = position_id.split('_')[0] if '_' in position_id else 'N/A'
            
            if action == "tp":
                message = f"""
✅ **تأكيد وضع هدف الربح**
🎯 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⚠️ سيتم وضع أمر TP عند الوصول لهذه النسبة
                """
            elif action == "sl":
                message = f"""
✅ **تأكيد وضع وقف الخسارة**
🛑 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⚠️ سيتم إغلاق الصفقة عند الوصول لهذه النسبة
                """
            elif action == "partial":
                message = f"""
✅ **تأكيد الإغلاق الجزئي**
📊 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⚠️ سيتم إغلاق {percent}% من الصفقة
                """
            elif action == "close":
                message = f"""
✅ **تأكيد الإغلاق الكامل**
❌ الرمز: {symbol}
🆔 رقم الصفقة: {position_id}

⚠️ سيتم إغلاق الصفقة بالكامل
                """
            else:
                message = f"""
✅ **تأكيد العملية**
🆔 رقم الصفقة: {position_id}
                """
            
            # لوحة أزرار التأكيد
            keyboard = [
                [
                    InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_{action}_{position_id}_{percent if percent is not None else ''}"),
                    InlineKeyboardButton("❌ إلغاء", callback_data=f"cancel_{position_id}")
                ]
            ]
            
            return message.strip(), InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة التأكيد: {e}")
            error_message = f"❌ خطأ في إنشاء رسالة التأكيد: {e}"
            return error_message, InlineKeyboardMarkup([])
    
    def create_success_message(self, action: str, position_id: str, percent: float = None, result: Dict = None) -> str:
        """إنشاء رسالة نجاح العملية"""
        try:
            symbol = position_id.split('_')[0] if '_' in position_id else 'N/A'
            
            if action == "tp":
                message = f"""
✅ **تم وضع هدف الربح بنجاح**
🎯 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif action == "sl":
                message = f"""
✅ **تم وضع وقف الخسارة بنجاح**
🛑 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif action == "partial":
                message = f"""
✅ **تم الإغلاق الجزئي بنجاح**
📊 الرمز: {symbol}
📊 النسبة: {percent}%
🆔 رقم الصفقة: {position_id}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif action == "close":
                pnl_info = ""
                if result and 'pnl' in result:
                    pnl = result['pnl']
                    pnl_emoji = "🟢💰" if pnl >= 0 else "🔴💸"
                    pnl_status = "رابحة" if pnl >= 0 else "خاسرة"
                    pnl_info = f"\n{pnl_emoji} النتيجة: {pnl:.2f} - {pnl_status}"
                
                message = f"""
✅ **تم إغلاق الصفقة بنجاح**
❌ الرمز: {symbol}
🆔 رقم الصفقة: {position_id}
{pnl_info}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            else:
                message = f"""
✅ **تم تنفيذ العملية بنجاح**
🆔 رقم الصفقة: {position_id}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة النجاح: {e}")
            return f"✅ تم تنفيذ العملية بنجاح\n⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}"
    
    def create_error_message(self, error: str, position_id: str = None) -> str:
        """إنشاء رسالة خطأ"""
        try:
            symbol_info = ""
            if position_id and '_' in position_id:
                symbol = position_id.split('_')[0]
                symbol_info = f"\n📊 الرمز: {symbol}"
            
            message = f"""
❌ **خطأ في تنفيذ العملية**
{symbol_info}
🆔 رقم الصفقة: {position_id or 'N/A'}

⚠️ الخطأ: {error}

⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الخطأ: {e}")
            return f"❌ خطأ في تنفيذ العملية: {error}"

# إنشاء مثيل عام لمدير الرسائل
trade_message_manager = TradeMessageManager()
