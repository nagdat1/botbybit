#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الصفقات المتقدم مع دعم TP/SL المتعدد والإغلاقات الجزئية
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """أنواع الصفقات"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class PriceType(Enum):
    """أنواع تحديد السعر"""
    PERCENTAGE = "percentage"  # نسبة مئوية
    PRICE = "price"            # سعر محدد


@dataclass
class TakeProfitLevel:
    """مستوى Take Profit"""
    level_number: int                    # رقم المستوى (1, 2, 3, ...)
    price_type: PriceType               # نوع تحديد السعر (نسبة أو سعر)
    value: float                        # القيمة (نسبة مئوية أو سعر)
    close_percentage: float             # نسبة الإغلاق من الصفقة (0-100)
    target_price: Optional[float] = None  # السعر المستهدف المحسوب
    executed: bool = False              # هل تم التنفيذ
    executed_time: Optional[datetime] = None  # وقت التنفيذ
    executed_price: Optional[float] = None    # سعر التنفيذ
    pnl: Optional[float] = None         # الربح/الخسارة المحقق
    
    def to_dict(self) -> dict:
        """تحويل إلى dict"""
        data = asdict(self)
        data['price_type'] = self.price_type.value
        if self.executed_time:
            data['executed_time'] = self.executed_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TakeProfitLevel':
        """إنشاء من dict"""
        data = data.copy()
        data['price_type'] = PriceType(data['price_type'])
        if data.get('executed_time'):
            data['executed_time'] = datetime.fromisoformat(data['executed_time'])
        return cls(**data)


@dataclass
class StopLoss:
    """Stop Loss"""
    price_type: PriceType               # نوع تحديد السعر (نسبة أو سعر)
    value: float                        # القيمة (نسبة مئوية أو سعر)
    target_price: Optional[float] = None  # السعر المستهدف المحسوب
    trailing: bool = False              # هل هو trailing stop
    trailing_distance: Optional[float] = None  # مسافة trailing (نسبة مئوية)
    trailing_activated_price: Optional[float] = None  # السعر الذي تم تفعيل trailing عنده
    executed: bool = False              # هل تم التنفيذ
    executed_time: Optional[datetime] = None  # وقت التنفيذ
    executed_price: Optional[float] = None    # سعر التنفيذ
    pnl: Optional[float] = None         # الربح/الخسارة المحقق
    
    def to_dict(self) -> dict:
        """تحويل إلى dict"""
        data = asdict(self)
        data['price_type'] = self.price_type.value
        if self.executed_time:
            data['executed_time'] = self.executed_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StopLoss':
        """إنشاء من dict"""
        data = data.copy()
        data['price_type'] = PriceType(data['price_type'])
        if data.get('executed_time'):
            data['executed_time'] = datetime.fromisoformat(data['executed_time'])
        return cls(**data)


class ManagedOrder:
    """صفقة مُدارة مع TP/SL"""
    
    def __init__(
        self,
        order_id: str,
        user_id: int,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        market_type: str = 'spot',
        leverage: int = 1
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.symbol = symbol
        self.side = side.lower()  # buy أو sell
        self.entry_price = entry_price
        self.quantity = quantity
        self.remaining_quantity = quantity
        self.market_type = market_type
        self.leverage = leverage
        
        # TP/SL
        self.take_profit_levels: List[TakeProfitLevel] = []
        self.stop_loss: Optional[StopLoss] = None
        
        # معلومات إضافية
        self.open_time = datetime.now()
        self.status = "OPEN"  # OPEN, PARTIALLY_CLOSED, CLOSED, LIQUIDATED
        self.current_price: Optional[float] = None
        self.unrealized_pnl: float = 0.0
        self.realized_pnl: float = 0.0
        
        # تاريخ الإغلاقات الجزئية
        self.partial_closes: List[Dict] = []
    
    def add_take_profit(
        self,
        level_number: int,
        price_type: PriceType,
        value: float,
        close_percentage: float
    ) -> bool:
        """إضافة مستوى Take Profit"""
        try:
            # التحقق من صحة البيانات
            if close_percentage <= 0 or close_percentage > 100:
                logger.error(f"نسبة الإغلاق غير صحيحة: {close_percentage}")
                return False
            
            # حساب السعر المستهدف
            target_price = self._calculate_target_price(price_type, value, self.entry_price, self.side)
            
            if target_price is None:
                logger.error("فشل في حساب السعر المستهدف")
                return False
            
            # إنشاء مستوى TP
            tp_level = TakeProfitLevel(
                level_number=level_number,
                price_type=price_type,
                value=value,
                close_percentage=close_percentage,
                target_price=target_price
            )
            
            self.take_profit_levels.append(tp_level)
            logger.info(f"تم إضافة TP{level_number} للصفقة {self.order_id}: السعر المستهدف={target_price:.6f}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة Take Profit: {e}")
            return False
    
    def set_stop_loss(
        self,
        price_type: PriceType,
        value: float,
        trailing: bool = False,
        trailing_distance: Optional[float] = None
    ) -> bool:
        """تعيين Stop Loss"""
        try:
            # حساب السعر المستهدف
            target_price = self._calculate_target_price(price_type, value, self.entry_price, self.side, is_stop_loss=True)
            
            if target_price is None:
                logger.error("فشل في حساب سعر Stop Loss")
                return False
            
            # إنشاء Stop Loss
            self.stop_loss = StopLoss(
                price_type=price_type,
                value=value,
                target_price=target_price,
                trailing=trailing,
                trailing_distance=trailing_distance
            )
            
            logger.info(f"تم تعيين SL للصفقة {self.order_id}: السعر المستهدف={target_price:.6f}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين Stop Loss: {e}")
            return False
    
    def _calculate_target_price(
        self,
        price_type: PriceType,
        value: float,
        base_price: float,
        side: str,
        is_stop_loss: bool = False
    ) -> Optional[float]:
        """حساب السعر المستهدف"""
        try:
            if price_type == PriceType.PRICE:
                # سعر محدد
                return value
            
            elif price_type == PriceType.PERCENTAGE:
                # نسبة مئوية
                if side == "buy":
                    if is_stop_loss:
                        # Stop Loss للشراء: أقل من سعر الدخول
                        return base_price * (1 - value / 100)
                    else:
                        # Take Profit للشراء: أعلى من سعر الدخول
                        return base_price * (1 + value / 100)
                else:  # sell
                    if is_stop_loss:
                        # Stop Loss للبيع: أعلى من سعر الدخول
                        return base_price * (1 + value / 100)
                    else:
                        # Take Profit للبيع: أقل من سعر الدخول
                        return base_price * (1 - value / 100)
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في حساب السعر المستهدف: {e}")
            return None
    
    def update_price(self, current_price: float) -> Dict:
        """تحديث السعر الحالي وفحص TP/SL"""
        self.current_price = current_price
        
        # حساب PnL غير المحقق
        self._calculate_unrealized_pnl()
        
        # فحص Stop Loss أولاً
        sl_triggered = self._check_stop_loss()
        if sl_triggered:
            return {
                'triggered': True,
                'type': 'STOP_LOSS',
                'data': sl_triggered
            }
        
        # فحص Take Profit
        tp_triggered = self._check_take_profits()
        if tp_triggered:
            return {
                'triggered': True,
                'type': 'TAKE_PROFIT',
                'data': tp_triggered
            }
        
        # تحديث Trailing Stop إذا كان مفعّلاً
        if self.stop_loss and self.stop_loss.trailing:
            self._update_trailing_stop()
        
        return {
            'triggered': False,
            'unrealized_pnl': self.unrealized_pnl
        }
    
    def _calculate_unrealized_pnl(self):
        """حساب الربح/الخسارة غير المحقق"""
        if self.current_price is None:
            return
        
        if self.side == "buy":
            self.unrealized_pnl = (self.current_price - self.entry_price) * self.remaining_quantity
        else:
            self.unrealized_pnl = (self.entry_price - self.current_price) * self.remaining_quantity
    
    def _check_stop_loss(self) -> Optional[Dict]:
        """فحص Stop Loss"""
        if not self.stop_loss or self.stop_loss.executed or self.current_price is None:
            return None
        
        triggered = False
        
        if self.side == "buy":
            # للشراء: SL يتفعل عندما يكون السعر أقل من أو يساوي SL
            if self.current_price <= self.stop_loss.target_price:
                triggered = True
        else:
            # للبيع: SL يتفعل عندما يكون السعر أعلى من أو يساوي SL
            if self.current_price >= self.stop_loss.target_price:
                triggered = True
        
        if triggered:
            self.stop_loss.executed = True
            self.stop_loss.executed_time = datetime.now()
            self.stop_loss.executed_price = self.current_price
            
            # حساب PnL
            if self.side == "buy":
                self.stop_loss.pnl = (self.current_price - self.entry_price) * self.remaining_quantity
            else:
                self.stop_loss.pnl = (self.entry_price - self.current_price) * self.remaining_quantity
            
            self.realized_pnl += self.stop_loss.pnl
            
            logger.warning(f"⚠️ Stop Loss تم تفعيله للصفقة {self.order_id} عند السعر {self.current_price:.6f}")
            
            return {
                'stop_loss': self.stop_loss,
                'close_quantity': self.remaining_quantity,
                'close_percentage': 100.0,
                'pnl': self.stop_loss.pnl
            }
        
        return None
    
    def _check_take_profits(self) -> Optional[Dict]:
        """فحص Take Profit"""
        if self.current_price is None:
            return None
        
        for tp in self.take_profit_levels:
            if tp.executed:
                continue
            
            triggered = False
            
            if self.side == "buy":
                # للشراء: TP يتفعل عندما يكون السعر أعلى من أو يساوي TP
                if self.current_price >= tp.target_price:
                    triggered = True
            else:
                # للبيع: TP يتفعل عندما يكون السعر أقل من أو يساوي TP
                if self.current_price <= tp.target_price:
                    triggered = True
            
            if triggered:
                tp.executed = True
                tp.executed_time = datetime.now()
                tp.executed_price = self.current_price
                
                # حساب الكمية المراد إغلاقها
                close_quantity = (tp.close_percentage / 100) * self.quantity
                
                # حساب PnL
                if self.side == "buy":
                    tp.pnl = (self.current_price - self.entry_price) * close_quantity
                else:
                    tp.pnl = (self.entry_price - self.current_price) * close_quantity
                
                self.realized_pnl += tp.pnl
                self.remaining_quantity -= close_quantity
                
                # حفظ الإغلاق الجزئي
                self.partial_closes.append({
                    'type': 'TAKE_PROFIT',
                    'level': tp.level_number,
                    'price': self.current_price,
                    'quantity': close_quantity,
                    'percentage': tp.close_percentage,
                    'pnl': tp.pnl,
                    'time': datetime.now().isoformat()
                })
                
                logger.info(f"✅ Take Profit {tp.level_number} تم تفعيله للصفقة {self.order_id} عند السعر {self.current_price:.6f}")
                
                # تحديث حالة الصفقة
                if self.remaining_quantity <= 0:
                    self.status = "CLOSED"
                else:
                    self.status = "PARTIALLY_CLOSED"
                
                return {
                    'take_profit': tp,
                    'close_quantity': close_quantity,
                    'close_percentage': tp.close_percentage,
                    'pnl': tp.pnl,
                    'remaining_quantity': self.remaining_quantity
                }
        
        return None
    
    def _update_trailing_stop(self):
        """تحديث Trailing Stop"""
        if not self.stop_loss or not self.stop_loss.trailing or self.current_price is None:
            return
        
        # التحقق من الاتجاه المربح
        is_profitable = False
        
        if self.side == "buy":
            # للشراء: السعر الحالي أعلى من سعر الدخول
            if self.current_price > self.entry_price:
                is_profitable = True
        else:
            # للبيع: السعر الحالي أقل من سعر الدخول
            if self.current_price < self.entry_price:
                is_profitable = True
        
        if is_profitable:
            # حساب SL الجديد بناءً على مسافة trailing
            new_sl_price = None
            
            if self.side == "buy":
                # للشراء: SL يتحرك لأعلى
                new_sl_price = self.current_price * (1 - self.stop_loss.trailing_distance / 100)
                
                # تحديث SL فقط إذا كان أعلى من القيمة الحالية
                if new_sl_price > self.stop_loss.target_price:
                    self.stop_loss.target_price = new_sl_price
                    self.stop_loss.trailing_activated_price = self.current_price
                    logger.info(f"🔄 تحديث Trailing Stop للصفقة {self.order_id}: SL الجديد={new_sl_price:.6f}")
            else:
                # للبيع: SL يتحرك لأسفل
                new_sl_price = self.current_price * (1 + self.stop_loss.trailing_distance / 100)
                
                # تحديث SL فقط إذا كان أقل من القيمة الحالية
                if new_sl_price < self.stop_loss.target_price:
                    self.stop_loss.target_price = new_sl_price
                    self.stop_loss.trailing_activated_price = self.current_price
                    logger.info(f"🔄 تحديث Trailing Stop للصفقة {self.order_id}: SL الجديد={new_sl_price:.6f}")
    
    def get_order_info(self) -> Dict:
        """الحصول على معلومات الصفقة"""
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'remaining_quantity': self.remaining_quantity,
            'market_type': self.market_type,
            'leverage': self.leverage,
            'take_profit_levels': [tp.to_dict() for tp in self.take_profit_levels],
            'stop_loss': self.stop_loss.to_dict() if self.stop_loss else None,
            'open_time': self.open_time.isoformat(),
            'status': self.status,
            'current_price': self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'partial_closes': self.partial_closes
        }
    
    def to_dict(self) -> Dict:
        """تحويل إلى dict للحفظ"""
        return self.get_order_info()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ManagedOrder':
        """إنشاء صفقة من dict"""
        order = cls(
            order_id=data['order_id'],
            user_id=data['user_id'],
            symbol=data['symbol'],
            side=data['side'],
            entry_price=data['entry_price'],
            quantity=data['quantity'],
            market_type=data.get('market_type', 'spot'),
            leverage=data.get('leverage', 1)
        )
        
        order.remaining_quantity = data.get('remaining_quantity', data['quantity'])
        order.open_time = datetime.fromisoformat(data['open_time'])
        order.status = data.get('status', 'OPEN')
        order.current_price = data.get('current_price')
        order.unrealized_pnl = data.get('unrealized_pnl', 0.0)
        order.realized_pnl = data.get('realized_pnl', 0.0)
        order.partial_closes = data.get('partial_closes', [])
        
        # تحميل TP levels
        if data.get('take_profit_levels'):
            order.take_profit_levels = [
                TakeProfitLevel.from_dict(tp) for tp in data['take_profit_levels']
            ]
        
        # تحميل SL
        if data.get('stop_loss'):
            order.stop_loss = StopLoss.from_dict(data['stop_loss'])
        
        return order


class OrderManager:
    """مدير الصفقات المتقدم"""
    
    def __init__(self):
        self.managed_orders: Dict[str, ManagedOrder] = {}  # {order_id: ManagedOrder}
        logger.info("تم تهيئة OrderManager")
    
    def create_managed_order(
        self,
        order_id: str,
        user_id: int,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        market_type: str = 'spot',
        leverage: int = 1,
        take_profits: Optional[List[Dict]] = None,
        stop_loss: Optional[Dict] = None
    ) -> Optional[ManagedOrder]:
        """إنشاء صفقة مُدارة جديدة"""
        try:
            # إنشاء الصفقة
            order = ManagedOrder(
                order_id=order_id,
                user_id=user_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                market_type=market_type,
                leverage=leverage
            )
            
            # إضافة Take Profits
            if take_profits:
                for tp in take_profits:
                    price_type = PriceType(tp['price_type'])
                    order.add_take_profit(
                        level_number=tp['level'],
                        price_type=price_type,
                        value=tp['value'],
                        close_percentage=tp['close_percentage']
                    )
            
            # إضافة Stop Loss
            if stop_loss:
                price_type = PriceType(stop_loss['price_type'])
                order.set_stop_loss(
                    price_type=price_type,
                    value=stop_loss['value'],
                    trailing=stop_loss.get('trailing', False),
                    trailing_distance=stop_loss.get('trailing_distance')
                )
            
            # حفظ الصفقة
            self.managed_orders[order_id] = order
            logger.info(f"تم إنشاء صفقة مُدارة: {order_id}")
            
            return order
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء صفقة مُدارة: {e}")
            return None
    
    def get_order(self, order_id: str) -> Optional[ManagedOrder]:
        """الحصول على صفقة"""
        return self.managed_orders.get(order_id)
    
    def update_order_price(self, order_id: str, current_price: float) -> Dict:
        """تحديث سعر الصفقة وفحص TP/SL"""
        order = self.get_order(order_id)
        if not order:
            return {'error': 'الصفقة غير موجودة'}
        
        return order.update_price(current_price)
    
    def update_all_prices(self, prices: Dict[str, float]) -> List[Dict]:
        """تحديث أسعار جميع الصفقات"""
        triggered_events = []
        
        for order_id, order in list(self.managed_orders.items()):
            if order.status in ['CLOSED', 'LIQUIDATED']:
                continue
            
            symbol = order.symbol
            if symbol in prices:
                result = order.update_price(prices[symbol])
                
                if result.get('triggered'):
                    triggered_events.append({
                        'order_id': order_id,
                        'order': order,
                        'event': result
                    })
        
        return triggered_events
    
    def close_order(self, order_id: str, reason: str = 'manual') -> bool:
        """إغلاق صفقة"""
        order = self.get_order(order_id)
        if not order:
            return False
        
        order.status = "CLOSED"
        logger.info(f"تم إغلاق الصفقة {order_id}: {reason}")
        
        return True
    
    def remove_order(self, order_id: str) -> bool:
        """حذف صفقة"""
        if order_id in self.managed_orders:
            del self.managed_orders[order_id]
            logger.info(f"تم حذف الصفقة {order_id}")
            return True
        return False
    
    def get_user_orders(self, user_id: int) -> List[ManagedOrder]:
        """الحصول على صفقات المستخدم"""
        return [order for order in self.managed_orders.values() if order.user_id == user_id]
    
    def get_active_orders(self, user_id: Optional[int] = None) -> List[ManagedOrder]:
        """الحصول على الصفقات النشطة"""
        orders = self.managed_orders.values()
        
        if user_id:
            orders = [o for o in orders if o.user_id == user_id]
        
        return [o for o in orders if o.status in ['OPEN', 'PARTIALLY_CLOSED']]
    
    def save_orders(self) -> Dict[str, Dict]:
        """حفظ جميع الصفقات"""
        return {
            order_id: order.to_dict()
            for order_id, order in self.managed_orders.items()
        }
    
    def load_orders(self, data: Dict[str, Dict]):
        """تحميل الصفقات"""
        try:
            for order_id, order_data in data.items():
                order = ManagedOrder.from_dict(order_data)
                self.managed_orders[order_id] = order
            
            logger.info(f"تم تحميل {len(data)} صفقة")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الصفقات: {e}")


# إنشاء مثيل عام
order_manager = OrderManager()

