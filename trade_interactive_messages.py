#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الرسائل التفاعلية للصفقات
يدعم التحديث التلقائي والإشعارات
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeInteractiveMessages:
    """نظام الرسائل التفاعلية للصفقات"""
    
    def __init__(self, trading_bot, trade_manager, trade_executor):
        self.trading_bot = trading_bot
        self.trade_manager = trade_manager
        self.trade_executor = trade_executor
        self.update_interval = 30  # تحديث كل 30 ثانية
        self.is_updating = False
        
    async def start_auto_updates(self):
        """بدء التحديث التلقائي للرسائل"""
        try:
            if not self.is_updating:
                self.is_updating = True
                asyncio.create_task(self.auto_update_loop())
                logger.info("تم بدء التحديث التلقائي للرسائل")
        except Exception as e:
            logger.error(f"خطأ في بدء التحديث التلقائي: {e}")
    
    async def stop_auto_updates(self):
        """إيقاف التحديث التلقائي للرسائل"""
        try:
            self.is_updating = False
            logger.info("تم إيقاف التحديث التلقائي للرسائل")
        except Exception as e:
            logger.error(f"خطأ في إيقاف التحديث التلقائي: {e}")
    
    async def auto_update_loop(self):
        """حلقة التحديث التلقائي"""
        try:
            while self.is_updating:
                await self.update_all_trade_messages()
                await asyncio.sleep(self.update_interval)
        except Exception as e:
            logger.error(f"خطأ في حلقة التحديث التلقائي: {e}")
        finally:
            self.is_updating = False
    
    async def update_all_trade_messages(self):
        """تحديث جميع رسائل الصفقات"""
        try:
            if not self.trade_manager.trade_messages:
                return
            
            # تحديث أسعار الصفقات المفتوحة أولاً
            await self.trading_bot.update_open_positions_prices()
            
            # تحديث كل رسالة صفقة
            for position_id in list(self.trade_manager.trade_messages.keys()):
                try:
                    await self.trade_manager.update_trade_message(position_id, None)
                except Exception as e:
                    logger.error(f"خطأ في تحديث رسالة الصفقة {position_id}: {e}")
                    
        except Exception as e:
            logger.error(f"خطأ في تحديث جميع رسائل الصفقات: {e}")
    
    async def send_trade_notification(self, position_id: str, notification_type: str, data: Dict = None):
        """إرسال إشعار للصفقة"""
        try:
            if position_id not in self.trade_manager.trade_messages:
                return
            
            message_info = self.trade_manager.trade_messages[position_id]
            position_info = message_info['position_info']
            
            # إنشاء نص الإشعار
            notification_text = await self.create_notification_text(
                position_id, notification_type, data
            )
            
            # إرسال الإشعار كرسالة منفصلة
            try:
                # هنا يمكن إضافة منطق إرسال الإشعار للمستخدم
                logger.info(f"إشعار للصفقة {position_id}: {notification_text}")
            except Exception as e:
                logger.error(f"خطأ في إرسال الإشعار: {e}")
                
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الصفقة: {e}")
    
    async def create_notification_text(self, position_id: str, notification_type: str, data: Dict = None) -> str:
        """إنشاء نص الإشعار"""
        try:
            position_info = self.trade_manager.trade_messages[position_id]['position_info']
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', 0)
            pnl_percent = position_info.get('pnl_percent', 0)
            
            if notification_type == "tp_hit":
                return f"""
🎯 **تم الوصول لهدف الربح!**
📊 {symbol}
💲 السعر الحالي: {current_price:.6f}
💰 الربح: {pnl_percent:.2f}%
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            elif notification_type == "sl_hit":
                return f"""
🛑 **تم تفعيل وقف الخسارة!**
📊 {symbol}
💲 السعر الحالي: {current_price:.6f}
📉 الخسارة: {pnl_percent:.2f}%
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            elif notification_type == "partial_executed":
                percent = data.get('percent', 0) if data else 0
                pnl = data.get('pnl', 0) if data else 0
                return f"""
🔄 **تم تنفيذ الإغلاق الجزئي**
📊 {symbol}
📊 النسبة: {percent}%
💰 الربح/الخسارة: {pnl:.2f}
💲 السعر: {current_price:.6f}
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            elif notification_type == "full_executed":
                pnl = data.get('pnl', 0) if data else 0
                return f"""
✅ **تم إغلاق الصفقة بالكامل**
📊 {symbol}
💰 الربح/الخسارة النهائية: {pnl:.2f}
💲 السعر النهائي: {current_price:.6f}
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            elif notification_type == "liquidation_warning":
                return f"""
🚨 **تحذير: قريب من التصفية!**
📊 {symbol}
💲 السعر الحالي: {current_price:.6f}
📉 الخسارة: {pnl_percent:.2f}%
⚠️ انتبه! الصفقة قريبة من سعر التصفية
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            elif notification_type == "price_update":
                return f"""
📈 **تحديث السعر**
📊 {symbol}
💲 السعر الجديد: {current_price:.6f}
💰 الربح/الخسارة: {pnl_percent:.2f}%
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
            
            else:
                return f"""
📢 **إشعار عام**
📊 {symbol}
💲 السعر: {current_price:.6f}
💰 الربح/الخسارة: {pnl_percent:.2f}%
⏰ {datetime.now().strftime('%H:%M:%S')}
                """
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء نص الإشعار: {e}")
            return "❌ خطأ في إنشاء الإشعار"
    
    async def create_trade_summary_message(self, position_id: str) -> str:
        """إنشاء رسالة ملخص الصفقة"""
        try:
            if position_id not in self.trade_manager.trade_messages:
                return "❌ الصفقة غير موجودة"
            
            message_info = self.trade_manager.trade_messages[position_id]
            position_info = message_info['position_info']
            
            symbol = position_info['symbol']
            side = position_info['side']
            entry_price = position_info['entry_price']
            current_price = position_info.get('current_price', entry_price)
            market_type = position_info.get('account_type', 'spot')
            pnl_percent = position_info.get('pnl_percent', 0)
            
            # حساب معلومات إضافية
            duration = datetime.now() - message_info['last_update']
            duration_str = self.format_duration(duration)
            
            # تحديد حالة الصفقة
            if pnl_percent > 0:
                status_emoji = "🟢💰"
                status_text = "رابحة"
            elif pnl_percent < 0:
                status_emoji = "🔴💸"
                status_text = "خاسرة"
            else:
                status_emoji = "⚪"
                status_text = "متعادلة"
            
            if market_type == 'futures':
                margin_amount = position_info.get('margin_amount', 0)
                leverage = position_info.get('leverage', 1)
                position_size = position_info.get('position_size', 0)
                liquidation_price = position_info.get('liquidation_price', 0)
                
                summary_text = f"""
📊 **ملخص الصفقة - فيوتشر**
{status_emoji} {symbol} - {status_text}

🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الهامش: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {liquidation_price:.6f}

📊 الأداء:
💰 الربح/الخسارة: {pnl_percent:.2f}%
⏰ المدة: {duration_str}
🆔 رقم الصفقة: {position_id}
                """
            else:
                amount = position_info.get('amount', 0)
                
                summary_text = f"""
📊 **ملخص الصفقة - سبوت**
{status_emoji} {symbol} - {status_text}

🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 المبلغ: {amount:.2f}

📊 الأداء:
💰 الربح/الخسارة: {pnl_percent:.2f}%
⏰ المدة: {duration_str}
🆔 رقم الصفقة: {position_id}
                """
            
            return summary_text
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملخص الصفقة: {e}")
            return "❌ خطأ في إنشاء ملخص الصفقة"
    
    def format_duration(self, duration: timedelta) -> str:
        """تنسيق مدة الصفقة"""
        try:
            total_seconds = int(duration.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds} ثانية"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"{minutes} دقيقة"
            elif total_seconds < 86400:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours} ساعة و {minutes} دقيقة"
            else:
                days = total_seconds // 86400
                hours = (total_seconds % 86400) // 3600
                return f"{days} يوم و {hours} ساعة"
                
        except Exception as e:
            logger.error(f"خطأ في تنسيق المدة: {e}")
            return "غير محدد"
    
    async def send_performance_summary(self, context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
        """إرسال ملخص الأداء"""
        try:
            if not self.trade_manager.trade_messages:
                return
            
            # حساب إحصائيات الأداء
            total_trades = len(self.trade_manager.trade_messages)
            profitable_trades = 0
            losing_trades = 0
            total_pnl = 0
            
            for position_id, message_info in self.trade_manager.trade_messages.items():
                position_info = message_info['position_info']
                pnl_percent = position_info.get('pnl_percent', 0)
                
                if pnl_percent > 0:
                    profitable_trades += 1
                elif pnl_percent < 0:
                    losing_trades += 1
                
                # حساب PnL الفعلي
                market_type = position_info.get('account_type', 'spot')
                if market_type == 'futures':
                    margin_amount = position_info.get('margin_amount', 0)
                    pnl_value = (pnl_percent / 100) * margin_amount
                else:
                    amount = position_info.get('amount', 0)
                    pnl_value = (pnl_percent / 100) * amount
                
                total_pnl += pnl_value
            
            # حساب معدل النجاح
            win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # إنشاء نص الملخص
            summary_text = f"""
📊 **ملخص الأداء العام**

📈 إجمالي الصفقات: {total_trades}
✅ الصفقات الرابحة: {profitable_trades}
❌ الصفقات الخاسرة: {losing_trades}
🎯 معدل النجاح: {win_rate:.1f}%

💰 الربح/الخسارة الإجمالي: {total_pnl:.2f}
📊 متوسط الربح لكل صفقة: {total_pnl/total_trades:.2f}

⏰ آخر تحديث: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # إرسال الملخص
            if user_id and context.bot:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=summary_text,
                    parse_mode='Markdown'
                )
            else:
                logger.info(f"ملخص الأداء: {summary_text}")
                
        except Exception as e:
            logger.error(f"خطأ في إرسال ملخص الأداء: {e}")
    
    async def cleanup_old_messages(self):
        """تنظيف الرسائل القديمة"""
        try:
            current_time = datetime.now()
            old_messages = []
            
            for position_id, message_info in self.trade_manager.trade_messages.items():
                # إذا كانت الرسالة أقدم من 24 ساعة والصفقة مغلقة
                if (current_time - message_info['last_update']).total_seconds() > 86400:
                    if position_id not in self.trading_bot.open_positions:
                        old_messages.append(position_id)
            
            # حذف الرسائل القديمة
            for position_id in old_messages:
                del self.trade_manager.trade_messages[position_id]
            
            if old_messages:
                logger.info(f"تم تنظيف {len(old_messages)} رسالة قديمة")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف الرسائل القديمة: {e}")
    
    async def handle_emergency_close_all(self, context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
        """معالجة إغلاق جميع الصفقات في حالات الطوارئ"""
        try:
            if not self.trade_manager.trade_messages:
                return
            
            emergency_text = """
🚨 **إغلاق طارئ لجميع الصفقات**

⚠️ تحذير: سيتم إغلاق جميع الصفقات المفتوحة فوراً
هذا الإجراء لا يمكن التراجع عنه

هل أنت متأكد؟
            """
            
            # إنشاء أزرار التأكيد
            keyboard = [
                [InlineKeyboardButton("✅ تأكيد الإغلاق", callback_data="emergency_close_confirm")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="emergency_close_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if user_id and context.bot:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=emergency_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                logger.warning("طلب إغلاق طارئ - لا يمكن إرسال الرسالة")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الطارئ: {e}")
