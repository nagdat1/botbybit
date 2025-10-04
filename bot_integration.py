#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف الربط بين البوت الحالي ونظام TP/SL الجديد
"""

import logging
import asyncio
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from order_manager import order_manager, PriceType
from trade_interface import trade_interface
from database import db_manager

logger = logging.getLogger(__name__)


class BotIntegration:
    """ربط نظام TP/SL مع البوت"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_task = None
    
    async def handle_new_position_with_tpsl(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        position_id: str,
        user_id: int,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        market_type: str = 'spot',
        leverage: int = 1
    ):
        """معالجة صفقة جديدة مع خيارات TP/SL"""
        try:
            # عرض واجهة تحديد TP/SL
            await trade_interface.show_new_trade_menu(
                update, context,
                symbol, side, entry_price, quantity,
                market_type, leverage
            )
            
            # حفظ position_id للربط لاحقاً
            if hasattr(context, 'user_data') and context.user_data:
                context.user_data['pending_position_id'] = position_id
            
        except Exception as e:
            logger.error(f"خطأ في معالجة صفقة جديدة مع TP/SL: {e}")
    
    async def confirm_position_with_tpsl(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        position_id: str
    ) -> bool:
        """تأكيد فتح الصفقة مع TP/SL"""
        try:
            # الحصول على بيانات الصفقة من trade_interface
            trade_state = trade_interface.get_trade_state(user_id)
            
            if not trade_state:
                logger.error(f"لا توجد بيانات صفقة للمستخدم {user_id}")
                return False
            
            # إنشاء صفقة مُدارة في order_manager
            managed_order = order_manager.create_managed_order(
                order_id=position_id,
                user_id=user_id,
                symbol=trade_state['symbol'],
                side=trade_state['side'],
                entry_price=trade_state['entry_price'],
                quantity=trade_state['quantity'],
                market_type=trade_state['market_type'],
                leverage=trade_state.get('leverage', 1),
                take_profits=trade_state.get('take_profits'),
                stop_loss=trade_state.get('stop_loss')
            )
            
            if not managed_order:
                logger.error(f"فشل في إنشاء صفقة مُدارة: {position_id}")
                return False
            
            # حفظ TP/SL في قاعدة البيانات
            for tp in managed_order.take_profit_levels:
                tp_data = {
                    'level_number': tp.level_number,
                    'price_type': tp.price_type.value,
                    'value': tp.value,
                    'close_percentage': tp.close_percentage,
                    'target_price': tp.target_price
                }
                db_manager.add_take_profit(position_id, tp_data)
            
            if managed_order.stop_loss:
                sl = managed_order.stop_loss
                sl_data = {
                    'price_type': sl.price_type.value,
                    'value': sl.value,
                    'target_price': sl.target_price,
                    'trailing': sl.trailing,
                    'trailing_distance': sl.trailing_distance
                }
                db_manager.add_stop_loss(position_id, sl_data)
            
            # مسح حالة الصفقة
            trade_interface.clear_trade_state(user_id)
            
            logger.info(f"تم تأكيد صفقة مع TP/SL: {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تأكيد صفقة مع TP/SL: {e}")
            return False
    
    async def start_price_monitoring(self, bybit_api=None):
        """بدء مراقبة الأسعار وتفعيل TP/SL"""
        if self.monitoring_active:
            logger.warning("مراقبة الأسعار نشطة بالفعل")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(
            self._price_monitoring_loop(bybit_api)
        )
        logger.info("✅ تم بدء مراقبة الأسعار لتفعيل TP/SL")
    
    async def stop_price_monitoring(self):
        """إيقاف مراقبة الأسعار"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ تم إيقاف مراقبة الأسعار")
    
    async def _price_monitoring_loop(self, bybit_api):
        """حلقة مراقبة الأسعار"""
        while self.monitoring_active:
            try:
                # الحصول على جميع الصفقات النشطة
                active_orders = order_manager.get_active_orders()
                
                if not active_orders:
                    await asyncio.sleep(30)  # انتظار 30 ثانية إذا لم توجد صفقات
                    continue
                
                # جمع الرموز الفريدة
                symbols = list(set(order.symbol for order in active_orders))
                
                # الحصول على الأسعار الحالية
                prices = {}
                for symbol in symbols:
                    if bybit_api:
                        # تحديد نوع السوق من أول صفقة بنفس الرمز
                        market_type = 'spot'
                        for order in active_orders:
                            if order.symbol == symbol:
                                market_type = order.market_type
                                break
                        
                        category = "linear" if market_type == "futures" else "spot"
                        price = bybit_api.get_ticker_price(symbol, category)
                        if price:
                            prices[symbol] = price
                
                if not prices:
                    await asyncio.sleep(30)
                    continue
                
                # تحديث أسعار جميع الصفقات وفحص TP/SL
                triggered_events = order_manager.update_all_prices(prices)
                
                # معالجة الأحداث المُفعّلة
                for event in triggered_events:
                    await self._handle_triggered_event(event)
                
                # انتظار 10 ثوانٍ قبل التحديث التالي
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"خطأ في حلقة مراقبة الأسعار: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    async def _handle_triggered_event(self, event: Dict):
        """معالجة حدث تفعيل TP/SL"""
        try:
            order = event['order']
            event_data = event['event']
            event_type = event_data['type']
            
            logger.info(f"⚡ تم تفعيل {event_type} للصفقة {order.order_id}")
            
            if event_type == 'STOP_LOSS':
                # معالجة Stop Loss
                await self._handle_stop_loss_trigger(order, event_data)
            
            elif event_type == 'TAKE_PROFIT':
                # معالجة Take Profit
                await self._handle_take_profit_trigger(order, event_data)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة حدث مُفعّل: {e}")
    
    async def _handle_stop_loss_trigger(self, order, event_data):
        """معالجة تفعيل Stop Loss"""
        try:
            sl_data = event_data['data']
            
            # حفظ الإغلاق الجزئي في قاعدة البيانات
            partial_close_data = {
                'order_id': order.order_id,
                'close_type': 'STOP_LOSS',
                'price': sl_data['stop_loss'].executed_price,
                'quantity': sl_data['close_quantity'],
                'percentage': sl_data['close_percentage'],
                'pnl': sl_data['pnl']
            }
            db_manager.add_partial_close(partial_close_data)
            
            # تحديث حالة الصفقة في قاعدة البيانات
            db_manager.update_order(order.order_id, {
                'status': 'CLOSED',
                'remaining_quantity': 0,
                'realized_pnl': order.realized_pnl
            })
            
            # إرسال إشعار للمستخدم
            message = f"""
⚠️ Stop Loss مُفعّل!

📊 الصفقة: {order.symbol}
🔄 النوع: {order.side.upper()}
💲 سعر الدخول: {order.entry_price:.6f}
💲 سعر التنفيذ: {sl_data['stop_loss'].executed_price:.6f}
💰 الكمية: {sl_data['close_quantity']}
{"🔴" if sl_data['pnl'] < 0 else "🟢"} PnL: {sl_data['pnl']:.2f}

تم إغلاق الصفقة بالكامل.
            """
            
            await self._send_notification_to_user(order.user_id, message)
            
            logger.info(f"✅ تم معالجة Stop Loss للصفقة {order.order_id}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة Stop Loss: {e}")
    
    async def _handle_take_profit_trigger(self, order, event_data):
        """معالجة تفعيل Take Profit"""
        try:
            tp_data = event_data['data']
            tp = tp_data['take_profit']
            
            # حفظ الإغلاق الجزئي في قاعدة البيانات
            partial_close_data = {
                'order_id': order.order_id,
                'close_type': 'TAKE_PROFIT',
                'level': tp.level_number,
                'price': tp.executed_price,
                'quantity': tp_data['close_quantity'],
                'percentage': tp_data['close_percentage'],
                'pnl': tp_data['pnl']
            }
            db_manager.add_partial_close(partial_close_data)
            
            # تحديث حالة الصفقة في قاعدة البيانات
            updates = {
                'remaining_quantity': tp_data['remaining_quantity'],
                'realized_pnl': order.realized_pnl
            }
            
            if order.status == 'CLOSED':
                updates['status'] = 'CLOSED'
            elif order.status == 'PARTIALLY_CLOSED':
                updates['status'] = 'PARTIALLY_CLOSED'
            
            db_manager.update_order(order.order_id, updates)
            
            # إرسال إشعار للمستخدم
            message = f"""
✅ Take Profit {tp.level_number} مُفعّل!

📊 الصفقة: {order.symbol}
🔄 النوع: {order.side.upper()}
💲 سعر الدخول: {order.entry_price:.6f}
💲 سعر التنفيذ: {tp.executed_price:.6f}
💰 الكمية المُغلقة: {tp_data['close_quantity']} ({tp_data['close_percentage']}%)
🟢 PnL: {tp_data['pnl']:.2f}

الكمية المتبقية: {tp_data['remaining_quantity']}
            """
            
            if order.status == 'CLOSED':
                message += "\n\n✅ تم إغلاق الصفقة بالكامل."
            
            await self._send_notification_to_user(order.user_id, message)
            
            logger.info(f"✅ تم معالجة Take Profit {tp.level_number} للصفقة {order.order_id}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة Take Profit: {e}")
    
    async def _send_notification_to_user(self, user_id: int, message: str):
        """إرسال إشعار للمستخدم"""
        try:
            # هنا نحتاج إلى الوصول إلى application للإرسال
            # سيتم تنفيذ ذلك من خلال البوت الرئيسي
            logger.info(f"إرسال إشعار للمستخدم {user_id}: {message}")
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار: {e}")
    
    async def load_managed_orders_from_db(self):
        """تحميل الصفقات المُدارة من قاعدة البيانات"""
        try:
            # الحصول على جميع الصفقات المفتوحة
            all_users = db_manager.get_all_active_users()
            
            loaded_count = 0
            
            for user_data in all_users:
                user_id = user_data['user_id']
                
                # الحصول على صفقات المستخدم المفتوحة
                orders = db_manager.get_user_orders(user_id, status='OPEN')
                orders += db_manager.get_user_orders(user_id, status='PARTIALLY_CLOSED')
                
                for order_data in orders:
                    order_id = order_data['order_id']
                    
                    # الحصول على تفاصيل الصفقة الكاملة
                    full_order = db_manager.get_full_order_details(order_id)
                    
                    if not full_order:
                        continue
                    
                    # تحويل TP/SL إلى الصيغة المطلوبة
                    take_profits = []
                    for tp_db in full_order.get('take_profits', []):
                        if not tp_db.get('executed'):
                            take_profits.append({
                                'level': tp_db['level_number'],
                                'price_type': tp_db['price_type'],
                                'value': tp_db['value'],
                                'close_percentage': tp_db['close_percentage']
                            })
                    
                    stop_loss = None
                    sl_db = full_order.get('stop_loss')
                    if sl_db and not sl_db.get('executed'):
                        stop_loss = {
                            'price_type': sl_db['price_type'],
                            'value': sl_db['value'],
                            'trailing': sl_db.get('trailing', False),
                            'trailing_distance': sl_db.get('trailing_distance')
                        }
                    
                    # إنشاء صفقة مُدارة
                    managed_order = order_manager.create_managed_order(
                        order_id=order_id,
                        user_id=user_id,
                        symbol=order_data['symbol'],
                        side=order_data['side'],
                        entry_price=order_data['entry_price'],
                        quantity=order_data['quantity'],
                        market_type='spot',  # يمكن تحسينه لاحقاً
                        leverage=1,
                        take_profits=take_profits if take_profits else None,
                        stop_loss=stop_loss
                    )
                    
                    if managed_order:
                        loaded_count += 1
            
            logger.info(f"✅ تم تحميل {loaded_count} صفقة مُدارة من قاعدة البيانات")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الصفقات المُدارة: {e}")


# إنشاء مثيل عام
bot_integration = BotIntegration()

