# -*- coding: utf-8 -*-
"""
نظام إشعارات تيليجرام للصفقات
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeNotifications:
    """فئة لإدارة إشعارات الصفقات"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send_trade_open_notification(self, position_info: Dict):
        """إرسال إشعار فتح صفقة جديدة"""
        try:
            symbol = position_info['symbol']
            side = "شراء" if position_info['side'].lower() == 'buy' else "بيع"
            
            message = f"""🔔 تم فتح صفقة جديدة

📊 الرمز: {symbol}
🔄 النوع: {side}
💰 الكمية: {position_info['initial_quantity']}
💲 سعر الدخول: {position_info['entry_price']:.6f}
⚡ الرافعة: {position_info['leverage']}x"""

            if position_info.get('take_profit'):
                message += f"\n💵 هدف الربح: {position_info['take_profit']:.6f}"
            
            if position_info.get('stop_loss'):
                message += f"\n🛑 وقف الخسارة: {position_info['stop_loss']:.6f}"
            
            if position_info.get('trailing_stop'):
                message += f"\n📈 Trailing Stop: {position_info['trailing_stop']:.6f}"
            
            # إضافة أزرار التحكم
            keyboard = [
                [
                    InlineKeyboardButton("🎯 تعديل TP/SL", 
                                       callback_data=f"modify_tp_sl_{position_info['position_id']}"),
                    InlineKeyboardButton("📊 تفاصيل", 
                                       callback_data=f"position_details_{position_info['position_id']}")
                ],
                [
                    InlineKeyboardButton("✂️ إغلاق جزئي", 
                                       callback_data=f"partial_close_{position_info['position_id']}"),
                    InlineKeyboardButton("❌ إغلاق كامل", 
                                       callback_data=f"close_position_{position_info['position_id']}")
                ],
                [
                    InlineKeyboardButton("🔄 تفعيل Trailing Stop", 
                                       callback_data=f"enable_trailing_{position_info['position_id']}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # إرسال الرسالة
            from telegram.ext import Application
            application = Application.builder().token(self.bot_token).build()
            await application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار فتح الصفقة: {e}")
    
    async def send_trade_update_notification(self, position_info: Dict, update_type: str, details: Dict):
        """إرسال إشعار تحديث الصفقة"""
        try:
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', 0)
            
            if update_type == 'partial_close':
                message = f"""✂️ تم الإغلاق الجزئي للصفقة

📊 الرمز: {symbol}
💰 الكمية المغلقة: {details['quantity']}
💲 سعر الإغلاق: {details['price']:.6f}
💵 الربح/الخسارة: {details['realized_pnl']:.2f} USDT
📊 النسبة المغلقة: {details['percent']}%
💰 الكمية المتبقية: {position_info['current_quantity']}"""

            elif update_type == 'tp_sl_update':
                message = f"""🎯 تم تحديث TP/SL

📊 الرمز: {symbol}
💲 السعر الحالي: {current_price:.6f}
💵 هدف الربح الجديد: {details.get('new_tp', 'لم يتغير')}
🛑 وقف الخسارة الجديد: {details.get('new_sl', 'لم يتغير')}"""

            elif update_type == 'trailing_stop_update':
                message = f"""📈 تحديث Trailing Stop

📊 الرمز: {symbol}
💲 السعر الحالي: {current_price:.6f}
🛑 مستوى التوقف الجديد: {details['new_stop']:.6f}"""

            # إضافة أزرار التحكم
            keyboard = [
                [
                    InlineKeyboardButton("📊 تفاصيل الصفقة", 
                                       callback_data=f"position_details_{position_info['position_id']}")
                ],
                [
                    InlineKeyboardButton("❌ إغلاق الصفقة", 
                                       callback_data=f"close_position_{position_info['position_id']}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # إرسال الرسالة
            from telegram.ext import Application
            application = Application.builder().token(self.bot_token).build()
            await application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار تحديث الصفقة: {e}")
    
    async def send_trade_close_notification(self, position_info: Dict, close_type: str):
        """إرسال إشعار إغلاق الصفقة"""
        try:
            symbol = position_info['symbol']
            side = "شراء" if position_info['side'].lower() == 'buy' else "بيع"
            pnl = position_info['realized_pnl']
            duration = position_info.get('duration', 0)  # بالساعات
            
            # تحديد نوع الإغلاق ورموزه
            close_types = {
                'take_profit': ('🎯 تم الوصول لهدف الربح', '💰'),
                'stop_loss': ('🛑 تم ضرب وقف الخسارة', '⚠️'),
                'trailing_stop': ('📈 تم ضرب Trailing Stop', '📊'),
                'manual': ('✋ تم الإغلاق يدوياً', '👋')
            }
            
            close_title, close_emoji = close_types.get(close_type, ('تم إغلاق الصفقة', '🔄'))
            
            # تحديد حالة الربح/الخسارة
            pnl_emoji = "🟢💰" if pnl > 0 else "🔴💸"
            status = "رابحة" if pnl > 0 else "خاسرة"
            
            message = f"""{close_emoji} {close_title}

📊 الرمز: {symbol}
🔄 النوع: {side}
💰 الكمية: {position_info['initial_quantity']}
💲 سعر الدخول: {position_info['entry_price']:.6f}
💲 سعر الإغلاق: {position_info['current_price']:.6f}
⚡ الرافعة: {position_info['leverage']}x
{pnl_emoji} الربح/الخسارة: {pnl:.2f} USDT - {status}
⏱ مدة الصفقة: {duration:.1f} ساعة"""

            # إضافة معلومات الإغلاق الجزئي إذا وجدت
            if position_info.get('partial_closes'):
                message += "\n\n📊 سجل الإغلاق الجزئي:"
                for idx, close in enumerate(position_info['partial_closes'], 1):
                    message += f"\n{idx}. {close['percent']}% @ {close['price']:.6f} ({close['realized_pnl']:.2f} USDT)"
            
            # إرسال الرسالة
            from telegram.ext import Application
            application = Application.builder().token(self.bot_token).build()
            await application.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار إغلاق الصفقة: {e}")
            
    async def send_position_details(self, position_info: Dict):
        """إرسال تفاصيل الصفقة"""
        try:
            symbol = position_info['symbol']
            side = "شراء" if position_info['side'].lower() == 'buy' else "بيع"
            status = position_info['status']
            
            message = f"""📊 تفاصيل الصفقة

🏷 معرف الصفقة: {position_info['position_id']}
📊 الرمز: {symbol}
🔄 النوع: {side}
📈 الحالة: {status}

💰 معلومات الكمية:
• الكمية الأولية: {position_info['initial_quantity']}
• الكمية الحالية: {position_info['current_quantity']}

💲 معلومات الأسعار:
• سعر الدخول: {position_info['entry_price']:.6f}
• السعر الحالي: {position_info['current_price']:.6f}
• هدف الربح: {position_info.get('take_profit', 'غير محدد')}
• وقف الخسارة: {position_info.get('stop_loss', 'غير محدد')}

📈 Trailing Stop:
• نشط: {'نعم' if position_info.get('trailing_activated') else 'لا'}
• المسافة: {position_info.get('trailing_stop', 'غير محدد')}
• الخطوة: {position_info.get('trailing_step', 'غير محدد')}

💰 الأرباح/الخسائر:
• غير المحققة: {position_info['unrealized_pnl']:.2f} USDT
• المحققة: {position_info['realized_pnl']:.2f} USDT

⏱ التوقيت:
• وقت الفتح: {position_info['open_time']}
• آخر تحديث: {position_info['last_update']}"""

            if position_info['partial_closes']:
                message += "\n\n✂️ سجل الإغلاق الجزئي:"
                for idx, close in enumerate(position_info['partial_closes'], 1):
                    message += f"\n{idx}. {close['percent']}% @ {close['price']:.6f} ({close['realized_pnl']:.2f} USDT)"
            
            # إضافة أزرار التحكم إذا كانت الصفقة نشطة
            keyboard = None
            if status != 'closed':
                keyboard = [
                    [
                        InlineKeyboardButton("🎯 تعديل TP/SL", 
                                           callback_data=f"modify_tp_sl_{position_info['position_id']}"),
                        InlineKeyboardButton("✂️ إغلاق جزئي", 
                                           callback_data=f"partial_close_{position_info['position_id']}")
                    ],
                    [
                        InlineKeyboardButton("❌ إغلاق كامل", 
                                           callback_data=f"close_position_{position_info['position_id']}"),
                        InlineKeyboardButton("🔄 تفعيل Trailing", 
                                           callback_data=f"enable_trailing_{position_info['position_id']}")
                    ]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # إرسال الرسالة
            from telegram.ext import Application
            application = Application.builder().token(self.bot_token).build()
            await application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال تفاصيل الصفقة: {e}")