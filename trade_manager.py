#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الصفقات الرئيسي
يدمج جميع مكونات نظام إدارة الصفقات التفاعلي
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import Update
from telegram.ext import ContextTypes

from trade_messages import trade_message_manager
from trade_button_handler import trade_button_handler
from trade_executor import trade_executor

logger = logging.getLogger(__name__)

class TradeManager:
    """مدير الصفقات الرئيسي"""
    
    def __init__(self, trading_bot=None):
        self.trading_bot = trading_bot
        self.trade_messages = trade_message_manager
        self.button_handler = trade_button_handler
        self.executor = trade_executor
        
        # ربط المكونات
        self.button_handler.trading_bot = trading_bot
        self.executor.trading_bot = trading_bot
        
        # حالة التحديث التلقائي
        self.auto_update_task = None
        self.is_running = False
    
    def start_auto_updates_sync(self):
        """بدء التحديث التلقائي للصفقات (نسخة متزامنة)"""
        try:
            if self.is_running:
                return
            
            self.is_running = True
            
            def run_auto_updates():
                """تشغيل التحديث التلقائي في thread منفصل"""
                import asyncio
                import threading
                
                def update_loop():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._auto_update_loop())
                    except Exception as e:
                        logger.error(f"خطأ في حلقة التحديث التلقائي: {e}")
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=update_loop, daemon=True)
                thread.start()
            
            run_auto_updates()
            logger.info("تم بدء التحديث التلقائي للصفقات")
            
        except Exception as e:
            logger.error(f"خطأ في بدء التحديث التلقائي: {e}")
    
    async def stop_auto_updates(self):
        """إيقاف التحديث التلقائي للصفقات"""
        try:
            self.is_running = False
            if self.auto_update_task:
                self.auto_update_task.cancel()
                try:
                    await self.auto_update_task
                except asyncio.CancelledError:
                    pass
            logger.info("تم إيقاف التحديث التلقائي للصفقات")
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف التحديث التلقائي: {e}")
    
    async def _auto_update_loop(self):
        """حلقة التحديث التلقائي"""
        try:
            while self.is_running:
                # تحديث أسعار الصفقات
                await self._update_positions_prices()
                
                # فحص أوامر TP/SL
                await self._check_tp_sl_triggers()
                
                # انتظار 30 ثانية قبل التحديث التالي
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("تم إلغاء حلقة التحديث التلقائي")
        except Exception as e:
            logger.error(f"خطأ في حلقة التحديث التلقائي: {e}")
    
    async def _update_positions_prices(self):
        """تحديث أسعار الصفقات المفتوحة"""
        try:
            if self.trading_bot and hasattr(self.trading_bot, 'update_open_positions_prices'):
                await self.trading_bot.update_open_positions_prices()
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الصفقات: {e}")
    
    async def _check_tp_sl_triggers(self):
        """فحص وتحقق من أوامر TP/SL"""
        try:
            if self.executor:
                await self.executor.check_tp_sl_triggers()
        except Exception as e:
            logger.error(f"خطأ في فحص أوامر TP/SL: {e}")
    
    async def send_trade_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str):
        """إرسال رسالة تفاعلية للصفقة"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                await update.message.reply_text("❌ البوت غير متاح")
                return
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                await update.message.reply_text("❌ الصفقة غير موجودة")
                return
            
            # الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(update)
            
            # إنشاء رسالة الصفقة
            message, keyboard = self.trade_messages.create_trade_message(
                position_info, user_settings
            )
            
            await update.message.reply_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة الصفقة: {e}")
            await update.message.reply_text(f"❌ خطأ في إرسال رسالة الصفقة: {e}")
    
    async def handle_trade_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة استدعاءات أزرار الصفقات"""
        try:
            # التحقق من أن البيانات تخص نظام الصفقات
            if not self._is_trade_callback(callback_data):
                return False
            
            # توجيه المعالجة لمعالج الأزرار
            await self.button_handler.handle_trade_callback(update, context, callback_data)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في معالجة استدعاء الصفقة: {e}")
            return False
    
    async def handle_custom_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str):
        """معالجة الإدخال المخصص للمستخدم"""
        try:
            # توجيه المعالجة لمعالج الأزرار
            return await self.button_handler.handle_custom_input(update, context, user_id, text)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإدخال المخصص: {e}")
            return False
    
    def _is_trade_callback(self, callback_data: str) -> bool:
        """التحقق من أن الاستدعاء يخص نظام الصفقات"""
        try:
            trade_actions = ['tp_', 'sl_', 'partial_', 'close_', 'edit_', 'set_', 'custom_', 'confirm_', 'cancel_', 'refresh_', 'back_']
            return any(callback_data.startswith(action) for action in trade_actions)
        except:
            return False
    
    def _get_user_settings(self, update: Update) -> Dict:
        """الحصول على إعدادات المستخدم"""
        try:
            if self.trading_bot and hasattr(self.trading_bot, 'user_settings'):
                return self.trading_bot.user_settings
            return {}
        except:
            return {}
    
    async def send_all_positions_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إرسال رسائل لجميع الصفقات المفتوحة"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                await update.message.reply_text("❌ البوت غير متاح")
                return
            
            positions = self.trading_bot.open_positions
            if not positions:
                await update.message.reply_text("🔄 لا توجد صفقات مفتوحة حالياً")
                return
            
            # الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(update)
            
            # إرسال رسالة منفصلة لكل صفقة
            for position_id, position_info in positions.items():
                try:
                    message, keyboard = self.trade_messages.create_trade_message(
                        position_info, user_settings
                    )
                    await update.message.reply_text(message, reply_markup=keyboard)
                    
                    # تأخير قصير بين الرسائل لتجنب حد الخصم
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"خطأ في إرسال رسالة الصفقة {position_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"خطأ في إرسال رسائل الصفقات: {e}")
            await update.message.reply_text(f"❌ خطأ في إرسال رسائل الصفقات: {e}")
    
    async def update_position_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str):
        """تحديث رسالة صفقة موجودة"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return
            
            # الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(update)
            
            # إنشاء رسالة الصفقة المحدثة
            message, keyboard = self.trade_messages.create_trade_message(
                position_info, user_settings
            )
            
            # تحديث الرسالة إذا كانت موجودة
            if update.callback_query and update.callback_query.message:
                await update.callback_query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"خطأ في تحديث رسالة الصفقة: {e}")
    
    def get_position_summary(self, position_id: str) -> Dict:
        """الحصول على ملخص الصفقة"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {}
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return {}
            
            # حساب الربح/الخسارة
            pnl_value, pnl_percent = self._calculate_position_pnl(position_info)
            
            # الحصول على الأوامر النشطة
            active_orders = self.executor.get_active_orders(position_id)
            
            return {
                'position_info': position_info,
                'pnl_value': pnl_value,
                'pnl_percent': pnl_percent,
                'active_orders': active_orders,
                'status': 'ACTIVE'
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص الصفقة: {e}")
            return {}
    
    def _calculate_position_pnl(self, position_info: Dict) -> tuple[float, float]:
        """حساب الربح/الخسارة للصفقة"""
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
            
            # حساب القيمة المالية
            margin_amount = position_info.get('margin_amount', position_info.get('amount', 100))
            pnl_value = (pnl_percent / 100) * margin_amount
            
            return pnl_value, pnl_percent
            
        except Exception as e:
            logger.error(f"خطأ في حساب PnL للصفقة: {e}")
            return 0.0, 0.0
    
    def get_all_positions_summary(self) -> List[Dict]:
        """الحصول على ملخص جميع الصفقات"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return []
            
            positions = self.trading_bot.open_positions
            summary = []
            
            for position_id, position_info in positions.items():
                position_summary = self.get_position_summary(position_id)
                if position_summary:
                    summary.append(position_summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص الصفقات: {e}")
            return []
    
    async def notify_position_update(self, position_id: str, update_type: str, data: Dict = None):
        """إرسال إشعار بتحديث الصفقة"""
        try:
            if not self.trading_bot:
                return
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return
            
            symbol = position_info.get('symbol', 'N/A')
            
            if update_type == "tp_triggered":
                message = f"""
🔔 **إشعار: تم تفعيل TP**
🎯 الرمز: {symbol}
📊 النسبة: {data.get('percent', 0)}%
💰 السعر المستهدف: {data.get('target_price', 0):.6f}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif update_type == "sl_triggered":
                message = f"""
🔔 **إشعار: تم تفعيل SL**
🛑 الرمز: {symbol}
📊 النسبة: {data.get('percent', 0)}%
💰 السعر المستهدف: {data.get('target_price', 0):.6f}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif update_type == "partial_closed":
                message = f"""
🔔 **إشعار: تم الإغلاق الجزئي**
📊 الرمز: {symbol}
📊 النسبة: {data.get('percent', 0)}%
💰 الربح/الخسارة: {data.get('pnl', 0):.2f}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            elif update_type == "position_closed":
                message = f"""
🔔 **إشعار: تم إغلاق الصفقة**
❌ الرمز: {symbol}
💰 الربح/الخسارة النهائي: {data.get('pnl', 0):.2f}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
                """
            else:
                return
            
            # إرسال الإشعار (يمكن تخصيص هذا حسب الحاجة)
            logger.info(f"إشعار الصفقة: {message}")
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الصفقة: {e}")
    
    def set_trading_bot(self, trading_bot):
        """تعيين البوت التجاري"""
        try:
            self.trading_bot = trading_bot
            self.button_handler.trading_bot = trading_bot
            self.executor.trading_bot = trading_bot
            logger.info("تم ربط مدير الصفقات بالبوت التجاري")
        except Exception as e:
            logger.error(f"خطأ في ربط مدير الصفقات: {e}")
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات نظام الصفقات"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {}
            
            positions = self.trading_bot.open_positions
            active_orders = self.executor.get_active_orders()
            
            total_pnl = 0.0
            winning_positions = 0
            losing_positions = 0
            
            for position_id, position_info in positions.items():
                pnl_value, _ = self._calculate_position_pnl(position_info)
                total_pnl += pnl_value
                
                if pnl_value > 0:
                    winning_positions += 1
                elif pnl_value < 0:
                    losing_positions += 1
            
            return {
                'total_positions': len(positions),
                'active_orders': len(active_orders),
                'total_pnl': total_pnl,
                'winning_positions': winning_positions,
                'losing_positions': losing_positions,
                'win_rate': (winning_positions / max(len(positions), 1)) * 100,
                'is_auto_update_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات النظام: {e}")
            return {}

# إنشاء مثيل عام لمدير الصفقات
trade_manager = TradeManager()