#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الصفقات مع دعم TP/SL والإغلاق الجزئي
يدعم إدارة الصفقات لكل مستخدم بشكل منفصل
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_DOWN
import threading

from database import db_manager
from api_manager import api_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class OrderManager:
    """مدير الصفقات مع دعم متقدم للـ TP/SL"""
    
    def __init__(self):
        self.active_orders: Dict[str, Dict] = {}
        self.order_locks: Dict[str, threading.Lock] = {}
        self.price_update_thread = None
        self.is_running = False
        
        # إعدادات التحديث
        self.price_update_interval = 30  # ثانية
        self.max_price_age = 300  # 5 دقائق
        
    def start_price_monitoring(self):
        """بدء مراقبة الأسعار"""
        if not self.is_running:
            self.is_running = True
            self.price_update_thread = threading.Thread(target=self._price_update_loop, daemon=True)
            self.price_update_thread.start()
            logger.info("تم بدء مراقبة الأسعار")
    
    def stop_price_monitoring(self):
        """إيقاف مراقبة الأسعار"""
        self.is_running = False
        if self.price_update_thread:
            self.price_update_thread.join(timeout=5)
        logger.info("تم إيقاف مراقبة الأسعار")
    
    def _price_update_loop(self):
        """حلقة تحديث الأسعار"""
        while self.is_running:
            try:
                self.update_all_order_prices()
                time.sleep(self.price_update_interval)
            except Exception as e:
                logger.error(f"خطأ في حلقة تحديث الأسعار: {e}")
                time.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    def create_order(self, user_id: int, symbol: str, side: str, quantity: float, 
                    price: float, leverage: int = 1, margin_amount: float = 0) -> Tuple[bool, str]:
        """إنشاء صفقة جديدة"""
        try:
            # التحقق من نشاط المستخدم
            if not user_manager.is_user_active(user_id):
                return False, "البوت متوقف لهذا المستخدم"
            
            # التحقق من وجود مفاتيح API
            if not api_manager.has_user_api(user_id):
                return False, "مفاتيح API غير مرتبطة"
            
            # إنشاء معرف فريد للصفقة
            order_id = f"{user_id}_{symbol}_{int(time.time() * 1000000)}"
            
            # حساب سعر التصفية للفيوتشر
            liquidation_price = 0
            if leverage > 1:
                liquidation_price = self._calculate_liquidation_price(price, side, leverage)
            
            # حفظ الصفقة في قاعدة البيانات
            success = db_manager.add_order(
                order_id=order_id,
                user_id=user_id,
                symbol=symbol,
                side=side,
                entry_price=price,
                quantity=quantity,
                leverage=leverage,
                margin_amount=margin_amount,
                liquidation_price=liquidation_price
            )
            
            if success:
                # إضافة الصفقة إلى القائمة النشطة
                self.active_orders[order_id] = {
                    'order_id': order_id,
                    'user_id': user_id,
                    'symbol': symbol,
                    'side': side,
                    'entry_price': price,
                    'quantity': quantity,
                    'leverage': leverage,
                    'margin_amount': margin_amount,
                    'liquidation_price': liquidation_price,
                    'current_price': price,
                    'unrealized_pnl': 0,
                    'tps': [],
                    'sl': 0,
                    'partial_close': [],
                    'status': 'open',
                    'open_time': datetime.now(),
                    'last_price_update': datetime.now()
                }
                
                # إنشاء قفل للصفقة
                self.order_locks[order_id] = threading.Lock()
                
                # تحديث بيئة المستخدم
                user_manager.refresh_user_environment(user_id)
                
                logger.info(f"تم إنشاء صفقة جديدة: {order_id} للمستخدم: {user_id}")
                return True, order_id
            
            return False, "فشل في حفظ الصفقة"
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الصفقة للمستخدم {user_id}: {e}")
            return False, str(e)
    
    def _calculate_liquidation_price(self, entry_price: float, side: str, leverage: int) -> float:
        """حساب سعر التصفية"""
        try:
            maintenance_margin_rate = 0.005  # 0.5%
            
            if side.lower() == "buy":
                # للصفقات الشرائية (Long)
                liquidation_price = entry_price * (1 - (1/leverage) + maintenance_margin_rate)
            else:
                # للصفقات البيعية (Short)
                liquidation_price = entry_price * (1 + (1/leverage) - maintenance_margin_rate)
            
            return max(liquidation_price, 0.000001)
            
        except Exception as e:
            logger.error(f"خطأ في حساب سعر التصفية: {e}")
            return 0
    
    def update_all_order_prices(self):
        """تحديث أسعار جميع الصفقات النشطة"""
        try:
            # جمع الرموز الفريدة
            symbols_to_update = {}
            for order_id, order_data in self.active_orders.items():
                symbol = order_data['symbol']
                user_id = order_data['user_id']
                if user_id not in symbols_to_update:
                    symbols_to_update[user_id] = set()
                symbols_to_update[user_id].add(symbol)
            
            # تحديث الأسعار لكل مستخدم
            for user_id, symbols in symbols_to_update.items():
                if api_manager.has_user_api(user_id):
                    for symbol in symbols:
                        # تحديد نوع السوق بناءً على الرافعة
                        category = "linear" if any(
                            order['leverage'] > 1 for order in self.active_orders.values() 
                            if order['symbol'] == symbol and order['user_id'] == user_id
                        ) else "spot"
                        
                        current_price = api_manager.get_user_price(user_id, symbol, category)
                        if current_price:
                            self._update_symbol_prices(user_id, symbol, current_price)
            
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الصفقات: {e}")
    
    def _update_symbol_prices(self, user_id: int, symbol: str, current_price: float):
        """تحديث أسعار رمز معين لجميع صفقات المستخدم"""
        try:
            for order_id, order_data in self.active_orders.items():
                if (order_data['user_id'] == user_id and 
                    order_data['symbol'] == symbol and 
                    order_data['status'] == 'open'):
                    
                    with self.order_locks.get(order_id, threading.Lock()):
                        # تحديث السعر والربح/الخسارة
                        order_data['current_price'] = current_price
                        order_data['last_price_update'] = datetime.now()
                        
                        # حساب الربح/الخسارة غير المحققة
                        unrealized_pnl = self._calculate_unrealized_pnl(order_data)
                        order_data['unrealized_pnl'] = unrealized_pnl
                        
                        # تحديث قاعدة البيانات
                        db_manager.update_order_price(order_id, current_price, unrealized_pnl)
                        
                        # فحص أهداف الأرباح ووقف الخسارة
                        self._check_tp_sl(order_id, order_data)
                        
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الرمز {symbol} للمستخدم {user_id}: {e}")
    
    def _calculate_unrealized_pnl(self, order_data: Dict) -> float:
        """حساب الربح/الخسارة غير المحققة"""
        try:
            entry_price = order_data['entry_price']
            current_price = order_data['current_price']
            quantity = order_data['quantity']
            side = order_data['side']
            leverage = order_data.get('leverage', 1)
            
            if side.lower() == "buy":
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity
            
            # تطبيق الرافعة المالية
            if leverage > 1:
                pnl = pnl * leverage
            
            return pnl
            
        except Exception as e:
            logger.error(f"خطأ في حساب الربح/الخسارة: {e}")
            return 0
    
    def _check_tp_sl(self, order_id: str, order_data: Dict):
        """فحص أهداف الأرباح ووقف الخسارة"""
        try:
            current_price = order_data['current_price']
            entry_price = order_data['entry_price']
            side = order_data['side']
            unrealized_pnl = order_data['unrealized_pnl']
            
            # فحص وقف الخسارة
            if order_data['sl'] > 0:
                sl_price = self._calculate_sl_price(entry_price, side, order_data['sl'])
                if self._should_trigger_sl(current_price, sl_price, side):
                    self._trigger_stop_loss(order_id, order_data)
                    return
            
            # فحص أهداف الأرباح
            for tp in order_data['tps']:
                if not tp.get('triggered', False):
                    tp_price = self._calculate_tp_price(entry_price, side, tp['percentage'])
                    if self._should_trigger_tp(current_price, tp_price, side):
                        self._trigger_take_profit(order_id, order_data, tp)
                        return
            
            # فحص التصفية للفيوتشر
            if order_data['leverage'] > 1:
                liquidation_price = order_data['liquidation_price']
                if self._should_trigger_liquidation(current_price, liquidation_price, side):
                    self._trigger_liquidation(order_id, order_data)
                    
        except Exception as e:
            logger.error(f"خطأ في فحص TP/SL للصفقة {order_id}: {e}")
    
    def _calculate_sl_price(self, entry_price: float, side: str, sl_percentage: float) -> float:
        """حساب سعر وقف الخسارة"""
        try:
            if side.lower() == "buy":
                return entry_price * (1 - sl_percentage / 100)
            else:
                return entry_price * (1 + sl_percentage / 100)
        except Exception as e:
            logger.error(f"خطأ في حساب سعر وقف الخسارة: {e}")
            return 0
    
    def _calculate_tp_price(self, entry_price: float, side: str, tp_percentage: float) -> float:
        """حساب سعر هدف الربح"""
        try:
            if side.lower() == "buy":
                return entry_price * (1 + tp_percentage / 100)
            else:
                return entry_price * (1 - tp_percentage / 100)
        except Exception as e:
            logger.error(f"خطأ في حساب سعر هدف الربح: {e}")
            return 0
    
    def _should_trigger_sl(self, current_price: float, sl_price: float, side: str) -> bool:
        """فحص ما إذا كان يجب تفعيل وقف الخسارة"""
        if side.lower() == "buy":
            return current_price <= sl_price
        else:
            return current_price >= sl_price
    
    def _should_trigger_tp(self, current_price: float, tp_price: float, side: str) -> bool:
        """فحص ما إذا كان يجب تفعيل هدف الربح"""
        if side.lower() == "buy":
            return current_price >= tp_price
        else:
            return current_price <= tp_price
    
    def _should_trigger_liquidation(self, current_price: float, liquidation_price: float, side: str) -> bool:
        """فحص ما إذا كان يجب تفعيل التصفية"""
        if side.lower() == "buy":
            return current_price <= liquidation_price
        else:
            return current_price >= liquidation_price
    
    def _trigger_stop_loss(self, order_id: str, order_data: Dict):
        """تفعيل وقف الخسارة"""
        try:
            logger.warning(f"تم تفعيل وقف الخسارة للصفقة: {order_id}")
            self.close_order(order_id, "stop_loss")
        except Exception as e:
            logger.error(f"خطأ في تفعيل وقف الخسارة: {e}")
    
    def _trigger_take_profit(self, order_id: str, order_data: Dict, tp: Dict):
        """تفعيل هدف الربح"""
        try:
            logger.info(f"تم تفعيل هدف الربح للصفقة: {order_id}")
            
            # تحديد النسبة للإغلاق الجزئي
            close_percentage = tp.get('close_percentage', 100)
            
            if close_percentage >= 100:
                # إغلاق كامل
                self.close_order(order_id, "take_profit")
            else:
                # إغلاق جزئي
                self.partial_close_order(order_id, close_percentage, "take_profit")
            
            # تحديد TP كمفعل
            tp['triggered'] = True
            tp['triggered_at'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"خطأ في تفعيل هدف الربح: {e}")
    
    def _trigger_liquidation(self, order_id: str, order_data: Dict):
        """تفعيل التصفية"""
        try:
            logger.error(f"تم تفعيل التصفية للصفقة: {order_id}")
            self.close_order(order_id, "liquidation")
        except Exception as e:
            logger.error(f"خطأ في تفعيل التصفية: {e}")
    
    def add_take_profit(self, order_id: str, percentage: float, close_percentage: float = 100) -> bool:
        """إضافة هدف ربح"""
        try:
            if order_id not in self.active_orders:
                return False
            
            with self.order_locks.get(order_id, threading.Lock()):
                order_data = self.active_orders[order_id]
                
                tp = {
                    'percentage': percentage,
                    'close_percentage': close_percentage,
                    'triggered': False,
                    'created_at': datetime.now().isoformat()
                }
                
                order_data['tps'].append(tp)
                
                # تحديث قاعدة البيانات
                db_manager.update_order_tps(order_id, order_data['tps'])
                
                logger.info(f"تم إضافة هدف ربح للصفقة {order_id}: {percentage}%")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إضافة هدف ربح: {e}")
            return False
    
    def set_stop_loss(self, order_id: str, percentage: float) -> bool:
        """تعيين وقف خسارة"""
        try:
            if order_id not in self.active_orders:
                return False
            
            with self.order_locks.get(order_id, threading.Lock()):
                order_data = self.active_orders[order_id]
                order_data['sl'] = percentage
                
                # تحديث قاعدة البيانات
                db_manager.update_order_sl(order_id, percentage)
                
                logger.info(f"تم تعيين وقف خسارة للصفقة {order_id}: {percentage}%")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في تعيين وقف خسارة: {e}")
            return False
    
    def partial_close_order(self, order_id: str, percentage: float, reason: str = "manual") -> bool:
        """إغلاق جزئي للصفقة"""
        try:
            if order_id not in self.active_orders:
                return False
            
            with self.order_locks.get(order_id, threading.Lock()):
                order_data = self.active_orders[order_id]
                
                # حساب الربح/الخسارة للإغلاق الجزئي
                partial_pnl = order_data['unrealized_pnl'] * (percentage / 100)
                
                # تسجيل الإغلاق الجزئي
                partial_close_record = {
                    'percentage': percentage,
                    'pnl': partial_pnl,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
                
                order_data['partial_close'].append(partial_close_record)
                
                # تحديث قاعدة البيانات
                db_manager.partial_close_order(order_id, percentage, partial_pnl)
                
                # تحديث إحصائيات المستخدم
                user_id = order_data['user_id']
                user_manager.refresh_user_environment(user_id)
                
                logger.info(f"تم إغلاق جزئي للصفقة {order_id}: {percentage}%")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في الإغلاق الجزئي: {e}")
            return False
    
    def close_order(self, order_id: str, reason: str = "manual") -> bool:
        """إغلاق الصفقة نهائياً"""
        try:
            if order_id not in self.active_orders:
                return False
            
            with self.order_locks.get(order_id, threading.Lock()):
                order_data = self.active_orders[order_id]
                
                # حساب الربح/الخسارة النهائي
                final_pnl = order_data['unrealized_pnl']
                exit_price = order_data['current_price']
                
                # إغلاق الصفقة في قاعدة البيانات
                db_manager.close_order(order_id, exit_price, final_pnl)
                
                # تحديث إحصائيات المستخدم
                user_id = order_data['user_id']
                user_manager.refresh_user_environment(user_id)
                
                # إزالة الصفقة من القائمة النشطة
                del self.active_orders[order_id]
                if order_id in self.order_locks:
                    del self.order_locks[order_id]
                
                logger.info(f"تم إغلاق الصفقة {order_id} بسبب: {reason}")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
            return False
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        """الحصول على صفقات المستخدم"""
        try:
            user_orders = []
            for order_id, order_data in self.active_orders.items():
                if order_data['user_id'] == user_id:
                    user_orders.append(order_data.copy())
            
            return user_orders
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على صفقات المستخدم {user_id}: {e}")
            return []
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """الحصول على صفقة محددة"""
        return self.active_orders.get(order_id)
    
    def get_all_orders(self) -> Dict[str, Dict]:
        """الحصول على جميع الصفقات النشطة"""
        return self.active_orders.copy()
    
    def get_order_count(self) -> int:
        """الحصول على عدد الصفقات النشطة"""
        return len(self.active_orders)
    
    def get_user_order_count(self, user_id: int) -> int:
        """الحصول على عدد صفقات المستخدم"""
        count = 0
        for order_data in self.active_orders.values():
            if order_data['user_id'] == user_id:
                count += 1
        return count

# إنشاء مثيل عام لمدير الصفقات
order_manager = OrderManager()
