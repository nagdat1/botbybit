#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الصفقات مع تنفيذ فوري وتأكيدات
يدعم TP, SL, Partial Close, و Full Close
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class TradeExecutor:
    """منفذ الصفقات مع التنفيذ الفوري"""
    
    def __init__(self, trading_bot, trade_manager):
        self.trading_bot = trading_bot
        self.trade_manager = trade_manager
        self.pending_orders = {}  # {order_id: order_info}
        
    async def execute_take_profit(self, position_id: str, percent: float, query: CallbackQuery) -> bool:
        """تنفيذ Take Profit مع التأكيد الفوري"""
        try:
            if position_id not in self.trading_bot.open_positions:
                await query.edit_message_text("❌ الصفقة غير موجودة")
                return False
            
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            entry_price = position_info['entry_price']
            side = position_info['side']
            current_price = position_info.get('current_price', entry_price)
            market_type = position_info.get('account_type', 'spot')
            
            # حساب سعر TP
            if side.lower() == "buy":
                tp_price = entry_price * (1 + percent / 100)
            else:
                tp_price = entry_price * (1 - percent / 100)
            
            # التحقق من صحة سعر TP
            if not self.validate_tp_price(tp_price, current_price, side):
                await query.edit_message_text(
                    f"❌ سعر TP غير صحيح\n"
                    f"سعر TP: {tp_price:.6f}\n"
                    f"السعر الحالي: {current_price:.6f}\n"
                    f"يجب أن يكون TP أعلى من السعر الحالي للشراء وأقل للبيع"
                )
                return False
            
            # تنفيذ TP
            success = await self.execute_tp_order(position_id, tp_price, percent)
            
            if success:
                # رسالة تأكيد النجاح
                confirmation_text = f"""
✅ **تم تنفيذ Take Profit بنجاح**
📊 الرمز: {symbol}
💲 سعر الدخول: {entry_price:.6f}
🎯 سعر TP: {tp_price:.6f}
📈 النسبة: {percent}%
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

🔄 سيتم إغلاق الصفقة عند الوصول للسعر المحدد
📱 ستتلقى إشعاراً عند التنفيذ
                """
                
                await query.edit_message_text(confirmation_text, parse_mode='Markdown')
                
                # إضافة إلى قائمة الأوامر المعلقة
                order_id = f"tp_{position_id}_{int(datetime.now().timestamp())}"
                self.pending_orders[order_id] = {
                    'type': 'tp',
                    'position_id': position_id,
                    'target_price': tp_price,
                    'percent': percent,
                    'created_at': datetime.now(),
                    'status': 'pending'
                }
                
                logger.info(f"تم تنفيذ TP للصفقة {position_id} بسعر {tp_price}")
                return True
            else:
                await query.edit_message_text("❌ فشل في تنفيذ Take Profit")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ TP: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ Take Profit")
            return False
    
    async def execute_stop_loss(self, position_id: str, percent: float, query: CallbackQuery) -> bool:
        """تنفيذ Stop Loss مع التأكيد الفوري"""
        try:
            if position_id not in self.trading_bot.open_positions:
                await query.edit_message_text("❌ الصفقة غير موجودة")
                return False
            
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            entry_price = position_info['entry_price']
            side = position_info['side']
            current_price = position_info.get('current_price', entry_price)
            market_type = position_info.get('account_type', 'spot')
            
            # حساب سعر SL
            if side.lower() == "buy":
                sl_price = entry_price * (1 - percent / 100)
            else:
                sl_price = entry_price * (1 + percent / 100)
            
            # التحقق من صحة سعر SL
            if not self.validate_sl_price(sl_price, current_price, side):
                await query.edit_message_text(
                    f"❌ سعر SL غير صحيح\n"
                    f"سعر SL: {sl_price:.6f}\n"
                    f"السعر الحالي: {current_price:.6f}\n"
                    f"يجب أن يكون SL أقل من السعر الحالي للشراء وأعلى للبيع"
                )
                return False
            
            # تنفيذ SL
            success = await self.execute_sl_order(position_id, sl_price, percent)
            
            if success:
                # رسالة تأكيد النجاح
                confirmation_text = f"""
⚠️ **تم تنفيذ Stop Loss بنجاح**
📊 الرمز: {symbol}
💲 سعر الدخول: {entry_price:.6f}
🛑 سعر SL: {sl_price:.6f}
📉 النسبة: {percent}%
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

🔄 سيتم إغلاق الصفقة عند الوصول للسعر المحدد
📱 ستتلقى إشعاراً عند التنفيذ
                """
                
                await query.edit_message_text(confirmation_text, parse_mode='Markdown')
                
                # إضافة إلى قائمة الأوامر المعلقة
                order_id = f"sl_{position_id}_{int(datetime.now().timestamp())}"
                self.pending_orders[order_id] = {
                    'type': 'sl',
                    'position_id': position_id,
                    'target_price': sl_price,
                    'percent': percent,
                    'created_at': datetime.now(),
                    'status': 'pending'
                }
                
                logger.info(f"تم تنفيذ SL للصفقة {position_id} بسعر {sl_price}")
                return True
            else:
                await query.edit_message_text("❌ فشل في تنفيذ Stop Loss")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ SL: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ Stop Loss")
            return False
    
    async def execute_partial_close(self, position_id: str, percent: float, query: CallbackQuery) -> bool:
        """تنفيذ الإغلاق الجزئي مع التأكيد الفوري"""
        try:
            if position_id not in self.trading_bot.open_positions:
                await query.edit_message_text("❌ الصفقة غير موجودة")
                return False
            
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', position_info['entry_price'])
            market_type = position_info.get('account_type', 'spot')
            
            # تنفيذ الإغلاق الجزئي
            success = await self.execute_partial_close_order(position_id, percent, current_price)
            
            if success:
                # حساب الربح/الخسارة الجزئية
                pnl_info = await self.calculate_partial_pnl(position_id, percent, current_price)
                
                # رسالة تأكيد النجاح
                confirmation_text = f"""
🔄 **تم تنفيذ الإغلاق الجزئي بنجاح**
📊 الرمز: {symbol}
💲 سعر الإغلاق: {current_price:.6f}
📊 النسبة المغلقة: {percent}%
💰 الربح/الخسارة: {pnl_info['pnl']:.2f} ({pnl_info['pnl_percent']:.2f}%)
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

✅ تم إغلاق {percent}% من الصفقة بنجاح
🔄 باقي الصفقة: {100-percent}%
                """
                
                await query.edit_message_text(confirmation_text, parse_mode='Markdown')
                
                # تحديث معلومات الصفقة
                await self.update_position_after_partial_close(position_id, percent, pnl_info)
                
                logger.info(f"تم تنفيذ الإغلاق الجزئي للصفقة {position_id} بنسبة {percent}%")
                return True
            else:
                await query.edit_message_text("❌ فشل في تنفيذ الإغلاق الجزئي")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ الإغلاق الجزئي")
            return False
    
    async def execute_full_close(self, position_id: str, query: CallbackQuery) -> bool:
        """تنفيذ الإغلاق الكامل مع التأكيد الفوري"""
        try:
            if position_id not in self.trading_bot.open_positions:
                await query.edit_message_text("❌ الصفقة غير موجودة")
                return False
            
            position_info = self.trading_bot.open_positions[position_id]
            symbol = position_info['symbol']
            current_price = position_info.get('current_price', position_info['entry_price'])
            market_type = position_info.get('account_type', 'spot')
            
            # تنفيذ الإغلاق الكامل
            success = await self.execute_full_close_order(position_id, current_price)
            
            if success:
                # حساب الربح/الخسارة النهائية
                pnl_info = await self.calculate_final_pnl(position_id, current_price)
                
                # رسالة تأكيد النجاح
                pnl_emoji = "🟢💰" if pnl_info['pnl'] >= 0 else "🔴💸"
                pnl_status = "رابحة" if pnl_info['pnl'] >= 0 else "خاسرة"
                
                confirmation_text = f"""
❌ **تم تنفيذ الإغلاق الكامل بنجاح**
{pnl_emoji} {symbol}
💲 سعر الإغلاق: {current_price:.6f}
💰 الربح/الخسارة النهائية: {pnl_info['pnl']:.2f} ({pnl_info['pnl_percent']:.2f}%) - {pnl_status}
⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}

✅ تم إغلاق الصفقة بالكامل بنجاح
                """
                
                await query.edit_message_text(confirmation_text, parse_mode='Markdown')
                
                # حذف الصفقة من القائمة المفتوحة
                if position_id in self.trading_bot.open_positions:
                    del self.trading_bot.open_positions[position_id]
                
                # حذف رسالة الصفقة
                if position_id in self.trade_manager.trade_messages:
                    del self.trade_manager.trade_messages[position_id]
                
                logger.info(f"تم تنفيذ الإغلاق الكامل للصفقة {position_id}")
                return True
            else:
                await query.edit_message_text("❌ فشل في تنفيذ الإغلاق الكامل")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الكامل: {e}")
            await query.edit_message_text("❌ خطأ في تنفيذ الإغلاق الكامل")
            return False
    
    async def execute_tp_order(self, position_id: str, tp_price: float, percent: float) -> bool:
        """تنفيذ أمر TP فعلي"""
        try:
            # هنا يمكن إضافة منطق تنفيذ TP الفعلي على المنصة
            # حالياً نعيد True للمحاكاة
            await asyncio.sleep(0.5)  # محاكاة التنفيذ
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ أمر TP: {e}")
            return False
    
    async def execute_sl_order(self, position_id: str, sl_price: float, percent: float) -> bool:
        """تنفيذ أمر SL فعلي"""
        try:
            # هنا يمكن إضافة منطق تنفيذ SL الفعلي على المنصة
            # حالياً نعيد True للمحاكاة
            await asyncio.sleep(0.5)  # محاكاة التنفيذ
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ أمر SL: {e}")
            return False
    
    async def execute_partial_close_order(self, position_id: str, percent: float, close_price: float) -> bool:
        """تنفيذ أمر الإغلاق الجزئي فعلي"""
        try:
            # هنا يمكن إضافة منطق تنفيذ الإغلاق الجزئي الفعلي على المنصة
            # حالياً نعيد True للمحاكاة
            await asyncio.sleep(0.5)  # محاكاة التنفيذ
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ أمر الإغلاق الجزئي: {e}")
            return False
    
    async def execute_full_close_order(self, position_id: str, close_price: float) -> bool:
        """تنفيذ أمر الإغلاق الكامل فعلي"""
        try:
            # استخدام دالة إغلاق الصفقة الموجودة في البوت الرئيسي
            if position_id in self.trading_bot.open_positions:
                position_info = self.trading_bot.open_positions[position_id]
                market_type = position_info.get('account_type', 'spot')
                
                if market_type == 'spot':
                    account = self.trading_bot.demo_account_spot
                    success, result = account.close_spot_position(position_id, close_price)
                else:
                    account = self.trading_bot.demo_account_futures
                    success, result = account.close_futures_position(position_id, close_price)
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ أمر الإغلاق الكامل: {e}")
            return False
    
    async def calculate_partial_pnl(self, position_id: str, percent: float, close_price: float) -> Dict:
        """حساب الربح/الخسارة الجزئية"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            entry_price = position_info['entry_price']
            side = position_info['side']
            market_type = position_info.get('account_type', 'spot')
            
            if market_type == 'futures':
                margin_amount = position_info.get('margin_amount', 0)
                position_size = position_info.get('position_size', 0)
                partial_size = position_size * (percent / 100)
                partial_contracts = partial_size / entry_price
                
                if side.lower() == "buy":
                    pnl = (close_price - entry_price) * partial_contracts
                else:
                    pnl = (entry_price - close_price) * partial_contracts
                
                pnl_percent = (pnl / margin_amount) * 100 if margin_amount > 0 else 0
            else:
                amount = position_info.get('amount', 0)
                partial_amount = amount * (percent / 100)
                partial_contracts = partial_amount / entry_price
                
                if side.lower() == "buy":
                    pnl = (close_price - entry_price) * partial_contracts
                else:
                    pnl = (entry_price - close_price) * partial_contracts
                
                pnl_percent = (pnl / partial_amount) * 100 if partial_amount > 0 else 0
            
            return {
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب PnL الجزئي: {e}")
            return {'pnl': 0, 'pnl_percent': 0}
    
    async def calculate_final_pnl(self, position_id: str, close_price: float) -> Dict:
        """حساب الربح/الخسارة النهائية"""
        try:
            position_info = self.trading_bot.open_positions[position_id]
            entry_price = position_info['entry_price']
            side = position_info['side']
            market_type = position_info.get('account_type', 'spot')
            
            if market_type == 'futures':
                margin_amount = position_info.get('margin_amount', 0)
                position_size = position_info.get('position_size', 0)
                contracts = position_size / entry_price
                
                if side.lower() == "buy":
                    pnl = (close_price - entry_price) * contracts
                else:
                    pnl = (entry_price - close_price) * contracts
                
                pnl_percent = (pnl / margin_amount) * 100 if margin_amount > 0 else 0
            else:
                amount = position_info.get('amount', 0)
                contracts = amount / entry_price
                
                if side.lower() == "buy":
                    pnl = (close_price - entry_price) * contracts
                else:
                    pnl = (entry_price - close_price) * contracts
                
                pnl_percent = (pnl / amount) * 100 if amount > 0 else 0
            
            return {
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب PnL النهائي: {e}")
            return {'pnl': 0, 'pnl_percent': 0}
    
    async def update_position_after_partial_close(self, position_id: str, closed_percent: float, pnl_info: Dict):
        """تحديث معلومات الصفقة بعد الإغلاق الجزئي"""
        try:
            if position_id in self.trading_bot.open_positions:
                position_info = self.trading_bot.open_positions[position_id]
                
                # تحديث حجم الصفقة
                if 'position_size' in position_info:
                    position_info['position_size'] *= (1 - closed_percent / 100)
                
                if 'amount' in position_info:
                    position_info['amount'] *= (1 - closed_percent / 100)
                
                # تحديث عدد العقود
                if 'contracts' in position_info:
                    position_info['contracts'] *= (1 - closed_percent / 100)
                
                # إضافة الربح/الخسارة المحققة
                if 'realized_pnl' not in position_info:
                    position_info['realized_pnl'] = 0
                position_info['realized_pnl'] += pnl_info['pnl']
                
                logger.info(f"تم تحديث الصفقة {position_id} بعد الإغلاق الجزئي")
                
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقة بعد الإغلاق الجزئي: {e}")
    
    def validate_tp_price(self, tp_price: float, current_price: float, side: str) -> bool:
        """التحقق من صحة سعر TP"""
        try:
            if side.lower() == "buy":
                return tp_price > current_price  # TP يجب أن يكون أعلى من السعر الحالي للشراء
            else:
                return tp_price < current_price  # TP يجب أن يكون أقل من السعر الحالي للبيع
        except:
            return False
    
    def validate_sl_price(self, sl_price: float, current_price: float, side: str) -> bool:
        """التحقق من صحة سعر SL"""
        try:
            if side.lower() == "buy":
                return sl_price < current_price  # SL يجب أن يكون أقل من السعر الحالي للشراء
            else:
                return sl_price > current_price  # SL يجب أن يكون أعلى من السعر الحالي للبيع
        except:
            return False
    
    async def monitor_pending_orders(self):
        """مراقبة الأوامر المعلقة وتنفيذها عند الوصول للسعر المطلوب"""
        try:
            while True:
                await asyncio.sleep(5)  # فحص كل 5 ثوان
                
                for order_id, order_info in list(self.pending_orders.items()):
                    if order_info['status'] == 'pending':
                        position_id = order_info['position_id']
                        
                        if position_id in self.trading_bot.open_positions:
                            position_info = self.trading_bot.open_positions[position_id]
                            current_price = position_info.get('current_price', 0)
                            target_price = order_info['target_price']
                            
                            # التحقق من الوصول للسعر المطلوب
                            if self.should_execute_order(current_price, target_price, order_info['type']):
                                await self.execute_pending_order(order_id, order_info, current_price)
                
        except Exception as e:
            logger.error(f"خطأ في مراقبة الأوامر المعلقة: {e}")
    
    def should_execute_order(self, current_price: float, target_price: float, order_type: str) -> bool:
        """التحقق من وجوب تنفيذ الأمر"""
        try:
            if order_type == 'tp':
                return abs(current_price - target_price) <= target_price * 0.001  # تحمل 0.1%
            elif order_type == 'sl':
                return abs(current_price - target_price) <= target_price * 0.001  # تحمل 0.1%
            return False
        except:
            return False
    
    async def execute_pending_order(self, order_id: str, order_info: Dict, current_price: float):
        """تنفيذ الأمر المعلق"""
        try:
            position_id = order_info['position_id']
            order_type = order_info['type']
            
            # تحديث حالة الأمر
            self.pending_orders[order_id]['status'] = 'executing'
            
            # تنفيذ الإغلاق الكامل
            if position_id in self.trading_bot.open_positions:
                position_info = self.trading_bot.open_positions[position_id]
                symbol = position_info['symbol']
                
                # تنفيذ الإغلاق
                success = await self.execute_full_close_order(position_id, current_price)
                
                if success:
                    # تحديث حالة الأمر
                    self.pending_orders[order_id]['status'] = 'executed'
                    self.pending_orders[order_id]['executed_at'] = datetime.now()
                    self.pending_orders[order_id]['executed_price'] = current_price
                    
                    logger.info(f"تم تنفيذ الأمر المعلق {order_id} للصفقة {position_id}")
                    
                    # إرسال إشعار للمستخدم (يمكن إضافته لاحقاً)
                    
                else:
                    self.pending_orders[order_id]['status'] = 'failed'
                    
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر المعلق {order_id}: {e}")
            if order_id in self.pending_orders:
                self.pending_orders[order_id]['status'] = 'failed'
