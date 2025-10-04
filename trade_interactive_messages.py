# -*- coding: utf-8 -*-
"""
نظام الرسائل التفاعلية للصفقات مع الأزرار
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeInteractiveMessages:
    """فئة إدارة الرسائل التفاعلية للصفقات"""
    
    def __init__(self, trade_manager):
        self.trade_manager = trade_manager
        self.user_settings = {}  # إعدادات المستخدمين للنسب المخصصة
    
    def get_user_settings(self, user_id: int) -> Dict:
        """الحصول على إعدادات المستخدم للنسب"""
        if user_id not in self.user_settings:
            # إعدادات افتراضية
            self.user_settings[user_id] = {
                'tp_percentages': [1.0, 2.0, 5.0],
                'sl_percentages': [1.0, 2.0, 3.0],
                'partial_close_percentages': [25.0, 50.0, 75.0]
            }
        return self.user_settings[user_id]
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم"""
        try:
            self.user_settings[user_id] = settings
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم {user_id}: {e}")
            return False
    
    def create_trade_message(self, trade_id: str, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """إنشاء رسالة الصفقة مع الأزرار التفاعلية"""
        try:
            trade_info = self.trade_manager.get_trade_info(trade_id)
            if not trade_info:
                return "❌ الصفقة غير موجودة", None
            
            user_settings = self.get_user_settings(user_id)
            
            # نص الرسالة
            message_text = self._format_trade_info(trade_info)
            
            # إنشاء الأزرار
            keyboard = self._create_trade_keyboard(trade_id, user_settings)
            
            return message_text, keyboard
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الصفقة: {e}")
            return "❌ خطأ في إنشاء رسالة الصفقة", None
    
    def _format_trade_info(self, trade_info: Dict) -> str:
        """تنسيق معلومات الصفقة"""
        try:
            symbol = trade_info['symbol']
            side = trade_info['side']
            entry_price = trade_info['entry_price']
            current_price = trade_info['current_price']
            pnl = trade_info['pnl']
            pnl_percentage = trade_info['pnl_percentage']
            remaining_quantity = trade_info['remaining_quantity']
            total_quantity = trade_info['quantity']
            status = trade_info['status']
            created_at = trade_info['created_at']
            
            # تنسيق الوقت
            created_time = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M:%S")
            
            # تحديد الأيقونة واللون
            side_emoji = "📈" if side.upper() == "BUY" else "📉"
            side_text = "شراء" if side.upper() == "BUY" else "بيع"
            
            # تحديد لون الربح/الخسارة
            pnl_emoji = "💚" if pnl >= 0 else "💔"
            pnl_color = "+" if pnl >= 0 else ""
            
            # حساب نسبة الإغلاق
            closed_percentage = ((total_quantity - remaining_quantity) / total_quantity) * 100
            
            message = f"""📊 **معلومات الصفقة**

{side_emoji} **{symbol}** - {side_text}
💰 سعر الدخول: `{entry_price:.6f}`
📈 السعر الحالي: `{current_price:.6f}`
💵 الربح/الخسارة: {pnl_emoji} `{pnl_color}{pnl:.2f} USDT` ({pnl_color}{pnl_percentage:+.2f}%)

📊 الكمية الإجمالية: `{total_quantity:.6f}`
📉 الكمية المتبقية: `{remaining_quantity:.6f}`
✂️ تم الإغلاق: `{closed_percentage:.1f}%`

⏰ وقت الفتح: `{created_time}`
🔄 الحالة: {status}

---
💡 استخدم الأزرار أدناه لإدارة الصفقة"""
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق معلومات الصفقة: {e}")
            return "❌ خطأ في تنسيق معلومات الصفقة"
    
    def _create_trade_keyboard(self, trade_id: str, user_settings: Dict) -> InlineKeyboardMarkup:
        """إنشاء لوحة المفاتيح التفاعلية"""
        try:
            keyboard = []
            
            # أزرار هدف الربح (TP)
            tp_buttons = []
            for percentage in user_settings['tp_percentages']:
                tp_buttons.append(
                    InlineKeyboardButton(
                        f"🎯 TP {percentage}%",
                        callback_data=f"tp_{trade_id}_{percentage}"
                    )
                )
            if len(tp_buttons) <= 3:
                keyboard.append(tp_buttons)
            else:
                # تقسيم الأزرار على صفين
                keyboard.append(tp_buttons[:3])
                keyboard.append(tp_buttons[3:])
            
            # أزرار وقف الخسارة (SL)
            sl_buttons = []
            for percentage in user_settings['sl_percentages']:
                sl_buttons.append(
                    InlineKeyboardButton(
                        f"🛑 SL {percentage}%",
                        callback_data=f"sl_{trade_id}_{percentage}"
                    )
                )
            if len(sl_buttons) <= 3:
                keyboard.append(sl_buttons)
            else:
                keyboard.append(sl_buttons[:3])
                keyboard.append(sl_buttons[3:])
            
            # أزرار الإغلاق الجزئي
            partial_buttons = []
            for percentage in user_settings['partial_close_percentages']:
                partial_buttons.append(
                    InlineKeyboardButton(
                        f"✂️ {percentage}%",
                        callback_data=f"partial_{trade_id}_{percentage}"
                    )
                )
            if len(partial_buttons) <= 3:
                keyboard.append(partial_buttons)
            else:
                keyboard.append(partial_buttons[:3])
                keyboard.append(partial_buttons[3:])
            
            # زر الإغلاق الكامل
            keyboard.append([
                InlineKeyboardButton(
                    "🔒 إغلاق كامل",
                    callback_data=f"close_{trade_id}"
                )
            ])
            
            # أزرار الإعدادات والتحديث
            keyboard.append([
                InlineKeyboardButton(
                    "⚙️ تعديل النسب",
                    callback_data=f"settings_{trade_id}"
                ),
                InlineKeyboardButton(
                    "🔄 تحديث",
                    callback_data=f"refresh_{trade_id}"
                )
            ])
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة المفاتيح: {e}")
            return None
    
    def create_settings_message(self, trade_id: str, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """إنشاء رسالة إعدادات النسب"""
        try:
            user_settings = self.get_user_settings(user_id)
            
            message = f"""⚙️ **تعديل نسب الأزرار**

🎯 **أهداف الربح الحالية:** {', '.join([f'{p}%' for p in user_settings['tp_percentages']])}
🛑 **وقف الخسارة الحالية:** {', '.join([f'{p}%' for p in user_settings['sl_percentages']])}
✂️ **الإغلاق الجزئي الحالي:** {', '.join([f'{p}%' for p in user_settings['partial_close_percentages']])}

---
💡 **كيفية التغيير:**
1. اختر النوع المراد تعديله (TP/SL/Partial)
2. أدخل النسب الجديدة مفصولة بفواصل
3. مثال: `1, 2, 5` أو `1.5, 3, 7.5`

⚠️ **ملاحظات:**
• النسب يجب أن تكون بين 0.1% و 99%
• استخدم أرقام صحيحة أو عشرية
• الإغلاق الجزئي يجب أن يكون أقل من 100%"""
            
            keyboard = [
                [
                    InlineKeyboardButton("🎯 تعديل TP", callback_data=f"edit_tp_{trade_id}"),
                    InlineKeyboardButton("🛑 تعديل SL", callback_data=f"edit_sl_{trade_id}")
                ],
                [
                    InlineKeyboardButton("✂️ تعديل Partial", callback_data=f"edit_partial_{trade_id}")
                ],
                [
                    InlineKeyboardButton("🔄 إعادة تعيين", callback_data=f"reset_settings_{trade_id}"),
                    InlineKeyboardButton("◀️ رجوع", callback_data=f"back_{trade_id}")
                ]
            ]
            
            return message, InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الإعدادات: {e}")
            return "❌ خطأ في إنشاء رسالة الإعدادات", None
    
    def create_confirmation_message(self, action: str, trade_id: str, percentage: float = None) -> str:
        """إنشاء رسالة التأكيد"""
        try:
            trade_info = self.trade_manager.get_trade_info(trade_id)
            if not trade_info:
                return "❌ الصفقة غير موجودة"
            
            symbol = trade_info['symbol']
            current_price = trade_info['current_price']
            remaining_quantity = trade_info['remaining_quantity']
            
            if action == "tp":
                message = f"""✅ **تم تنفيذ هدف الربح!**

📊 **{symbol}**
🎯 TP: {percentage}%
💰 السعر: `{current_price:.6f}`
📊 الكمية المُغلقة: `{(percentage/100) * remaining_quantity:.6f}`

🔄 الصفقة لا تزال مفتوحة للجزء المتبقي"""
                
            elif action == "sl":
                message = f"""⚠️ **تم تنفيذ وقف الخسارة!**

📊 **{symbol}**
🛑 SL: {percentage}%
💰 السعر: `{current_price:.6f}`
📊 الكمية المُغلقة: `{remaining_quantity:.6f}`

🔒 تم إغلاق الصفقة بالكامل"""
                
            elif action == "partial":
                message = f"""✂️ **تم تنفيذ الإغلاق الجزئي!**

📊 **{symbol}**
📉 الإغلاق: {percentage}%
💰 السعر: `{current_price:.6f}`
📊 الكمية المُغلقة: `{(percentage/100) * remaining_quantity:.6f}`

🔄 الصفقة لا تزال مفتوحة للجزء المتبقي"""
                
            elif action == "close":
                message = f"""🔒 **تم إغلاق الصفقة بالكامل!**

📊 **{symbol}**
💰 السعر النهائي: `{current_price:.6f}`
📊 الكمية المُغلقة: `{remaining_quantity:.6f}`

✅ الصفقة مكتملة"""
                
            else:
                message = f"""✅ **تم تنفيذ العملية بنجاح!**

📊 **{symbol}**
💰 السعر: `{current_price:.6f}`"""
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة التأكيد: {e}")
            return "❌ خطأ في إنشاء رسالة التأكيد"
    
    def create_error_message(self, error: str) -> str:
        """إنشاء رسالة خطأ"""
        return f"""❌ **خطأ في التنفيذ**

⚠️ **السبب:** {error}

🔍 **الحلول المقترحة:**
• تحقق من أن الصفقة لا تزال مفتوحة
• تأكد من وجود كمية كافية للإغلاق
• راجع إعدادات التداول
• حاول مرة أخرى لاحقاً"""
    
    def create_settings_edit_message(self, setting_type: str, trade_id: str) -> str:
        """إنشاء رسالة تعديل الإعدادات"""
        type_names = {
            'tp': 'أهداف الربح (TP)',
            'sl': 'وقف الخسارة (SL)', 
            'partial': 'الإغلاق الجزئي'
        }
        
        return f"""✏️ **تعديل {type_names.get(setting_type, setting_type)}**

📝 **أدخل النسب الجديدة:**
• مفصولة بفواصل (مثال: `1, 2, 5`)
• بين 0.1% و 99%
• يمكن استخدام أرقام عشرية

⚠️ **لإلغاء التعديل:** أرسل `إلغاء`

💡 **مثال:** `1.5, 3, 7.5`"""
    
    def parse_percentages(self, text: str) -> List[float]:
        """تحليل النسب من النص"""
        try:
            # إزالة المسافات والفاصل
            text = text.strip().replace(' ', '')
            
            # تقسيم بالفاصلة
            parts = text.split(',')
            
            percentages = []
            for part in parts:
                part = part.strip()
                if part:
                    percentage = float(part)
                    if 0.1 <= percentage <= 99:
                        percentages.append(percentage)
                    else:
                        raise ValueError(f"النسبة {percentage} خارج النطاق المسموح (0.1-99)")
            
            if not percentages:
                raise ValueError("لم يتم العثور على نسب صحيحة")
            
            return percentages
            
        except ValueError as e:
            raise ValueError(f"خطأ في تحليل النسب: {str(e)}")
        except Exception as e:
            raise ValueError(f"خطأ غير متوقع: {str(e)}")
