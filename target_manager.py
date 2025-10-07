#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الأهداف ووقف الخسارة والإغلاق الجزئي للصفقات
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import db_manager

logger = logging.getLogger(__name__)

class TargetManager:
    """مدير الأهداف ووقف الخسارة والإغلاق الجزئي"""
    
    def __init__(self, trading_bot):
        self.trading_bot = trading_bot
        self.db = db_manager
        
    async def check_targets_and_stops(self):
        """فحص الأهداف ووقف الخسارة للصفقات المفتوحة"""
        try:
            # الحصول على جميع الصفقات التي لها أهداف أو وقف خسارة
            orders = self.db.get_orders_with_targets()
            
            for order in orders:
                await self._check_order_targets(order)
                await self._check_stop_loss(order)
                await self._check_trailing_stop(order)
                
        except Exception as e:
            logger.error(f"خطأ في فحص الأهداف ووقف الخسارة: {e}")
    
    async def _check_order_targets(self, order: Dict):
        """فحص أهداف صفقة محددة"""
        try:
            symbol = order['symbol']
            side = order['side']
            entry_price = order['entry_price']
            targets = order.get('targets', [])
            
            if not targets:
                return
            
            # الحصول على السعر الحالي
            current_price = await self._get_current_price(symbol)
            if not current_price:
                return
            
            # فحص كل هدف
            for i, target in enumerate(targets):
                if target.get('achieved', False):
                    continue
                
                target_price = target['price']
                target_percentage = target['percentage']
                
                # فحص ما إذا تم الوصول للهدف
                if self._is_target_reached(side, current_price, target_price):
                    await self._execute_target(order, target, i, current_price)
                    
        except Exception as e:
            logger.error(f"خطأ في فحص أهداف الصفقة {order['order_id']}: {e}")
    
    def _is_target_reached(self, side: str, current_price: float, target_price: float) -> bool:
        """فحص ما إذا تم الوصول للهدف"""
        if side.lower() == 'buy':
            return current_price >= target_price
        else:
            return current_price <= target_price
    
    async def _execute_target(self, order: Dict, target: Dict, target_index: int, current_price: float):
        """تنفيذ هدف محقق"""
        try:
            order_id = order['order_id']
            user_id = order['user_id']
            symbol = order['symbol']
            side = order['side']
            quantity = order['quantity']
            entry_price = order['entry_price']
            
            target_percentage = target['percentage']
            target_price = target['price']
            
            # حساب الكمية المراد إغلاقها
            close_quantity = quantity * (target_percentage / 100)
            
            # حساب الربح/الخسارة المحققة
            if side.lower() == 'buy':
                realized_pnl = (current_price - entry_price) * close_quantity
            else:
                realized_pnl = (entry_price - current_price) * close_quantity
            
            # تنفيذ الإغلاق الجزئي
            success = await self._execute_partial_close(
                order_id, user_id, symbol, side, close_quantity, current_price
            )
            
            if success:
                # تحديث الهدف كمحقق
                targets = order['targets']
                targets[target_index]['achieved'] = True
                targets[target_index]['achieved_price'] = current_price
                targets[target_index]['achieved_time'] = datetime.now().isoformat()
                
                # حفظ التحديث في قاعدة البيانات
                self.db.update_order_targets(order_id, targets)
                
                # إضافة سجل الهدف المحقق
                self.db.add_target_achievement(
                    order_id, user_id, target_price, target_percentage,
                    current_price, close_quantity, realized_pnl
                )
                
                # تحديث المحفظة
                self.db.update_portfolio(user_id, symbol, -close_quantity, current_price, realized_pnl)
                
                # إرسال إشعار
                await self._send_target_notification(order, target, current_price, realized_pnl)
                
                logger.info(f"تم تحقيق الهدف للصفقة {order_id}: {target_percentage}% بسعر {current_price}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الهدف: {e}")
    
    async def _check_stop_loss(self, order: Dict):
        """فحص وقف الخسارة"""
        try:
            stop_loss = order.get('stop_loss', 0)
            if stop_loss <= 0:
                return
            
            symbol = order['symbol']
            side = order['side']
            
            # الحصول على السعر الحالي
            current_price = await self._get_current_price(symbol)
            if not current_price:
                return
            
            # فحص ما إذا تم الوصول لوقف الخسارة
            if self._is_stop_loss_triggered(side, current_price, stop_loss):
                await self._execute_stop_loss(order, current_price)
                
        except Exception as e:
            logger.error(f"خطأ في فحص وقف الخسارة للصفقة {order['order_id']}: {e}")
    
    def _is_stop_loss_triggered(self, side: str, current_price: float, stop_loss: float) -> bool:
        """فحص ما إذا تم تفعيل وقف الخسارة"""
        if side.lower() == 'buy':
            return current_price <= stop_loss
        else:
            return current_price >= stop_loss
    
    async def _execute_stop_loss(self, order: Dict, current_price: float):
        """تنفيذ وقف الخسارة"""
        try:
            order_id = order['order_id']
            user_id = order['user_id']
            symbol = order['symbol']
            side = order['side']
            quantity = order['quantity']
            entry_price = order['entry_price']
            
            # حساب الربح/الخسارة المحققة
            if side.lower() == 'buy':
                realized_pnl = (current_price - entry_price) * quantity
            else:
                realized_pnl = (entry_price - current_price) * quantity
            
            # إغلاق الصفقة بالكامل
            success = await self._execute_full_close(
                order_id, user_id, symbol, side, quantity, current_price
            )
            
            if success:
                # تحديث حالة الصفقة
                self.db.close_order(order_id, current_price, realized_pnl)
                
                # تحديث المحفظة
                self.db.update_portfolio(user_id, symbol, -quantity, current_price, realized_pnl)
                
                # إرسال إشعار
                await self._send_stop_loss_notification(order, current_price, realized_pnl)
                
                logger.info(f"تم تفعيل وقف الخسارة للصفقة {order_id}: {current_price}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ وقف الخسارة: {e}")
    
    async def _check_trailing_stop(self, order: Dict):
        """فحص وقف الخسارة المتحرك"""
        try:
            if not order.get('trailing_stop', False):
                return
            
            trailing_distance = order.get('trailing_stop_distance', 0)
            if trailing_distance <= 0:
                return
            
            symbol = order['symbol']
            side = order['side']
            entry_price = order['entry_price']
            
            # الحصول على السعر الحالي
            current_price = await self._get_current_price(symbol)
            if not current_price:
                return
            
            # حساب وقف الخسارة المتحرك الجديد
            new_stop_loss = self._calculate_trailing_stop(side, current_price, trailing_distance)
            
            # تحديث وقف الخسارة إذا كان أفضل
            current_stop_loss = order.get('stop_loss', 0)
            if self._should_update_trailing_stop(side, new_stop_loss, current_stop_loss):
                self.db.update_order_stop_loss(order['order_id'], new_stop_loss)
                
                logger.info(f"تم تحديث وقف الخسارة المتحرك للصفقة {order['order_id']}: {new_stop_loss}")
                
        except Exception as e:
            logger.error(f"خطأ في فحص وقف الخسارة المتحرك للصفقة {order['order_id']}: {e}")
    
    def _calculate_trailing_stop(self, side: str, current_price: float, distance: float) -> float:
        """حساب وقف الخسارة المتحرك"""
        if side.lower() == 'buy':
            return current_price * (1 - distance / 100)
        else:
            return current_price * (1 + distance / 100)
    
    def _should_update_trailing_stop(self, side: str, new_stop: float, current_stop: float) -> bool:
        """فحص ما إذا كان يجب تحديث وقف الخسارة المتحرك"""
        if current_stop <= 0:
            return True
        
        if side.lower() == 'buy':
            return new_stop > current_stop
        else:
            return new_stop < current_stop
    
    async def _execute_partial_close(self, order_id: str, user_id: int, symbol: str, 
                                   side: str, quantity: float, price: float) -> bool:
        """تنفيذ إغلاق جزئي"""
        try:
            # تنفيذ الإغلاق الجزئي في البوت
            if hasattr(self.trading_bot, 'execute_partial_close'):
                return await self.trading_bot.execute_partial_close(
                    order_id, user_id, symbol, side, quantity, price
                )
            else:
                # تنفيذ افتراضي
                logger.warning("البوت لا يدعم الإغلاق الجزئي المباشر")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي: {e}")
            return False
    
    async def _execute_full_close(self, order_id: str, user_id: int, symbol: str, 
                                side: str, quantity: float, price: float) -> bool:
        """تنفيذ إغلاق كامل"""
        try:
            # تنفيذ الإغلاق الكامل في البوت
            if hasattr(self.trading_bot, 'execute_full_close'):
                return await self.trading_bot.execute_full_close(
                    order_id, user_id, symbol, side, quantity, price
                )
            else:
                # تنفيذ افتراضي
                logger.warning("البوت لا يدعم الإغلاق الكامل المباشر")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الكامل: {e}")
            return False
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """الحصول على السعر الحالي"""
        try:
            if hasattr(self.trading_bot, 'bybit_api'):
                return self.trading_bot.bybit_api.get_ticker_price(symbol, 'spot')
            else:
                logger.warning("لا يمكن الحصول على السعر الحالي")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر الحالي: {e}")
            return None
    
    async def _send_target_notification(self, order: Dict, target: Dict, 
                                      current_price: float, realized_pnl: float):
        """إرسال إشعار تحقيق الهدف"""
        try:
            message = f"🎯 تم تحقيق الهدف!\n\n"
            message += f"الرمز: {order['symbol']}\n"
            message += f"الهدف: {target['percentage']}%\n"
            message += f"السعر المحقق: {current_price}\n"
            message += f"الربح/الخسارة: {realized_pnl:.2f}\n"
            message += f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # إرسال الإشعار للمستخدم
            if hasattr(self.trading_bot, 'send_notification'):
                await self.trading_bot.send_notification(order['user_id'], message)
                
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الهدف: {e}")
    
    async def _send_stop_loss_notification(self, order: Dict, current_price: float, 
                                        realized_pnl: float):
        """إرسال إشعار وقف الخسارة"""
        try:
            message = f"🛑 تم تفعيل وقف الخسارة!\n\n"
            message += f"الرمز: {order['symbol']}\n"
            message += f"سعر الإغلاق: {current_price}\n"
            message += f"الربح/الخسارة: {realized_pnl:.2f}\n"
            message += f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # إرسال الإشعار للمستخدم
            if hasattr(self.trading_bot, 'send_notification'):
                await self.trading_bot.send_notification(order['user_id'], message)
                
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار وقف الخسارة: {e}")
    
    def add_targets_to_order(self, order_id: str, targets: List[Dict]) -> bool:
        """إضافة أهداف لصفقة"""
        try:
            return self.db.update_order_targets(order_id, targets)
        except Exception as e:
            logger.error(f"خطأ في إضافة الأهداف: {e}")
            return False
    
    def add_stop_loss_to_order(self, order_id: str, stop_loss: float) -> bool:
        """إضافة وقف خسارة لصفقة"""
        try:
            return self.db.update_order_stop_loss(order_id, stop_loss)
        except Exception as e:
            logger.error(f"خطأ في إضافة وقف الخسارة: {e}")
            return False
    
    def add_trailing_stop_to_order(self, order_id: str, enabled: bool, distance: float) -> bool:
        """إضافة وقف خسارة متحرك لصفقة"""
        try:
            return self.db.update_trailing_stop(order_id, enabled, distance)
        except Exception as e:
            logger.error(f"خطأ في إضافة وقف الخسارة المتحرك: {e}")
            return False
    
    def get_order_targets(self, order_id: str) -> List[Dict]:
        """الحصول على أهداف صفقة"""
        try:
            order = self.db.get_order(order_id)
            if order:
                return order.get('targets', [])
            return []
        except Exception as e:
            logger.error(f"خطأ في الحصول على أهداف الصفقة: {e}")
            return []
    
    def get_order_stop_loss(self, order_id: str) -> float:
        """الحصول على وقف خسارة صفقة"""
        try:
            order = self.db.get_order(order_id)
            if order:
                return order.get('stop_loss', 0)
            return 0
        except Exception as e:
            logger.error(f"خطأ في الحصول على وقف الخسارة: {e}")
            return 0
    
    def get_partial_closes(self, order_id: str) -> List[Dict]:
        """الحصول على الإغلاقات الجزئية لصفقة"""
        try:
            return self.db.get_partial_closes(order_id)
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإغلاقات الجزئية: {e}")
            return []
    
    def get_target_achievements(self, order_id: str) -> List[Dict]:
        """الحصول على الأهداف المحققة لصفقة"""
        try:
            return self.db.get_target_achievements(order_id)
        except Exception as e:
            logger.error(f"خطأ في الحصول على الأهداف المحققة: {e}")
            return []
    
    def get_user_portfolio(self, user_id: int) -> List[Dict]:
        """الحصول على محفظة المستخدم"""
        try:
            return self.db.get_user_portfolio(user_id)
        except Exception as e:
            logger.error(f"خطأ في الحصول على محفظة المستخدم: {e}")
            return []
