#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الصفقات المتقدم مع دعم TP/SL/Partial Close
يدعم تحديد Stop Loss و Take Profit بالنسبة المئوية أو السعر المحدد
مع إمكانية الإغلاق الجزئي للصفقات
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

class PositionTarget:
    """هدف Take Profit أو Stop Loss"""
    
    def __init__(self, 
                 target_type: str,  # 'tp' أو 'sl'
                 value: float,  # السعر المستهدف
                 percentage: float = None,  # النسبة المئوية للإغلاق (للTP فقط)
                 is_percentage_based: bool = False,  # هل القيمة نسبة مئوية أم سعر
                 triggered: bool = False):
        self.target_type = target_type
        self.value = value
        self.percentage = percentage if percentage else 100.0
        self.is_percentage_based = is_percentage_based
        self.triggered = triggered
        self.trigger_time = None
    
    def check_trigger(self, current_price: float, entry_price: float, side: str) -> bool:
        """فحص ما إذا تم تفعيل الهدف"""
        if self.triggered:
            return False
        
        # حساب السعر المستهدف إذا كانت القيمة نسبة مئوية
        target_price = self.value
        if self.is_percentage_based:
            if self.target_type == 'tp':
                if side.lower() == 'buy':
                    target_price = entry_price * (1 + self.value / 100)
                else:
                    target_price = entry_price * (1 - self.value / 100)
            else:  # stop loss
                if side.lower() == 'buy':
                    target_price = entry_price * (1 - abs(self.value) / 100)
                else:
                    target_price = entry_price * (1 + abs(self.value) / 100)
        
        # فحص التفعيل
        triggered = False
        if self.target_type == 'tp':
            if side.lower() == 'buy':
                triggered = current_price >= target_price
            else:
                triggered = current_price <= target_price
        else:  # stop loss
            if side.lower() == 'buy':
                triggered = current_price <= target_price
            else:
                triggered = current_price >= target_price
        
        if triggered:
            self.triggered = True
            self.trigger_time = datetime.now()
        
        return triggered
    
    def get_target_price(self, entry_price: float, side: str) -> float:
        """الحصول على السعر المستهدف الفعلي"""
        if self.is_percentage_based:
            if self.target_type == 'tp':
                if side.lower() == 'buy':
                    return entry_price * (1 + self.value / 100)
                else:
                    return entry_price * (1 - self.value / 100)
            else:  # stop loss
                if side.lower() == 'buy':
                    return entry_price * (1 - abs(self.value) / 100)
                else:
                    return entry_price * (1 + abs(self.value) / 100)
        return self.value
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس للتخزين"""
        return {
            'target_type': self.target_type,
            'value': self.value,
            'percentage': self.percentage,
            'is_percentage_based': self.is_percentage_based,
            'triggered': self.triggered,
            'trigger_time': self.trigger_time.isoformat() if self.trigger_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """إنشاء من قاموس"""
        obj = cls(
            target_type=data['target_type'],
            value=data['value'],
            percentage=data.get('percentage', 100.0),
            is_percentage_based=data.get('is_percentage_based', False),
            triggered=data.get('triggered', False)
        )
        if data.get('trigger_time'):
            obj.trigger_time = datetime.fromisoformat(data['trigger_time'])
        return obj


class ManagedPosition:
    """صفقة مدارة مع دعم TP/SL/Partial Close"""
    
    def __init__(self,
                 position_id: str,
                 user_id: int,
                 symbol: str,
                 side: str,
                 entry_price: float,
                 quantity: float,
                 market_type: str = 'spot',
                 leverage: int = 1):
        self.position_id = position_id
        self.user_id = user_id
        self.symbol = symbol
        self.side = side.lower()
        self.entry_price = entry_price
        self.initial_quantity = quantity
        self.current_quantity = quantity
        self.market_type = market_type
        self.leverage = leverage
        self.open_time = datetime.now()
        self.status = 'OPEN'
        
        # أهداف Take Profit
        self.take_profits: List[PositionTarget] = []
        
        # Stop Loss
        self.stop_loss: Optional[PositionTarget] = None
        
        # تاريخ الإغلاقات الجزئية
        self.partial_closes: List[Dict] = []
        
        # معلومات إضافية
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
        self.notes = ""
    
    def add_take_profit(self, 
                        value: float, 
                        percentage: float = 100.0,
                        is_percentage_based: bool = False):
        """إضافة هدف Take Profit"""
        tp = PositionTarget(
            target_type='tp',
            value=value,
            percentage=percentage,
            is_percentage_based=is_percentage_based
        )
        self.take_profits.append(tp)
        self.take_profits.sort(key=lambda x: x.get_target_price(self.entry_price, self.side))
        logger.info(f"تم إضافة TP للصفقة {self.position_id}: {value}{'%' if is_percentage_based else ''}")
    
    def add_stop_loss(self, value: float, is_percentage_based: bool = False):
        """إضافة Stop Loss"""
        self.stop_loss = PositionTarget(
            target_type='sl',
            value=value,
            percentage=100.0,
            is_percentage_based=is_percentage_based
        )
        logger.info(f"تم إضافة SL للصفقة {self.position_id}: {value}{'%' if is_percentage_based else ''}")
    
    def update_take_profit(self, index: int, value: float, percentage: float = None):
        """تحديث Take Profit محدد"""
        if 0 <= index < len(self.take_profits):
            self.take_profits[index].value = value
            if percentage is not None:
                self.take_profits[index].percentage = percentage
            self.take_profits.sort(key=lambda x: x.get_target_price(self.entry_price, self.side))
            logger.info(f"تم تحديث TP{index+1} للصفقة {self.position_id}")
            return True
        return False
    
    def update_stop_loss(self, value: float):
        """تحديث Stop Loss"""
        if self.stop_loss:
            self.stop_loss.value = value
            logger.info(f"تم تحديث SL للصفقة {self.position_id}")
            return True
        return False
    
    def remove_take_profit(self, index: int):
        """حذف Take Profit محدد"""
        if 0 <= index < len(self.take_profits):
            removed_tp = self.take_profits.pop(index)
            logger.info(f"تم حذف TP{index+1} من الصفقة {self.position_id}")
            return True
        return False
    
    def remove_stop_loss(self):
        """حذف Stop Loss"""
        if self.stop_loss:
            self.stop_loss = None
            logger.info(f"تم حذف SL من الصفقة {self.position_id}")
            return True
        return False
    
    def check_targets(self, current_price: float) -> List[Tuple[str, PositionTarget]]:
        """فحص جميع الأهداف (TP/SL) وإرجاع المُفعّلة"""
        triggered = []
        
        # فحص Take Profits
        for tp in self.take_profits:
            if tp.check_trigger(current_price, self.entry_price, self.side):
                triggered.append(('tp', tp))
        
        # فحص Stop Loss
        if self.stop_loss and self.stop_loss.check_trigger(current_price, self.entry_price, self.side):
            triggered.append(('sl', self.stop_loss))
        
        return triggered
    
    def execute_partial_close(self, 
                              percentage: float, 
                              close_price: float,
                              reason: str = 'manual') -> Dict:
        """تنفيذ إغلاق جزئي"""
        if percentage <= 0 or percentage > 100:
            return {'success': False, 'error': 'نسبة غير صالحة'}
        
        if self.current_quantity <= 0:
            return {'success': False, 'error': 'الصفقة مغلقة بالكامل'}
        
        # حساب الكمية المراد إغلاقها
        close_quantity = (self.current_quantity * percentage) / 100
        
        # حساب الربح/الخسارة المحققة
        if self.side == 'buy':
            pnl = (close_price - self.entry_price) * close_quantity
        else:
            pnl = (self.entry_price - close_price) * close_quantity
        
        # تحديث البيانات
        self.current_quantity -= close_quantity
        self.realized_pnl += pnl
        
        # حفظ سجل الإغلاق الجزئي
        partial_close_record = {
            'close_time': datetime.now().isoformat(),
            'close_price': close_price,
            'close_quantity': close_quantity,
            'percentage': percentage,
            'pnl': pnl,
            'reason': reason
        }
        self.partial_closes.append(partial_close_record)
        
        # تحديث الحالة
        if self.current_quantity <= 0:
            self.status = 'CLOSED'
        
        logger.info(f"إغلاق جزئي {percentage}% من الصفقة {self.position_id}, PnL: {pnl:.2f}")
        
        return {
            'success': True,
            'close_quantity': close_quantity,
            'remaining_quantity': self.current_quantity,
            'pnl': pnl,
            'percentage_closed': percentage,
            'is_fully_closed': self.current_quantity <= 0
        }
    
    def update_unrealized_pnl(self, current_price: float):
        """تحديث الربح/الخسارة غير المحققة"""
        if self.current_quantity > 0:
            if self.side == 'buy':
                self.unrealized_pnl = (current_price - self.entry_price) * self.current_quantity
            else:
                self.unrealized_pnl = (self.entry_price - current_price) * self.current_quantity
        else:
            self.unrealized_pnl = 0.0
    
    def get_total_pnl(self) -> float:
        """الحصول على إجمالي الربح/الخسارة (المحقق + غير المحقق)"""
        return self.realized_pnl + self.unrealized_pnl
    
    def get_position_info(self, current_price: float = None) -> Dict:
        """الحصول على معلومات الصفقة الكاملة"""
        if current_price:
            self.update_unrealized_pnl(current_price)
        
        # حساب النسب
        remaining_percentage = (self.current_quantity / self.initial_quantity) * 100 if self.initial_quantity > 0 else 0
        closed_percentage = 100 - remaining_percentage
        
        info = {
            'position_id': self.position_id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'initial_quantity': self.initial_quantity,
            'current_quantity': self.current_quantity,
            'remaining_percentage': remaining_percentage,
            'closed_percentage': closed_percentage,
            'market_type': self.market_type,
            'leverage': self.leverage,
            'status': self.status,
            'open_time': self.open_time.isoformat(),
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.get_total_pnl(),
            'take_profits': [tp.to_dict() for tp in self.take_profits],
            'stop_loss': self.stop_loss.to_dict() if self.stop_loss else None,
            'partial_closes': self.partial_closes,
            'partial_closes_count': len(self.partial_closes),
            'notes': self.notes
        }
        
        return info
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس للتخزين"""
        return self.get_position_info()
    
    @classmethod
    def from_dict(cls, data: Dict):
        """إنشاء من قاموس"""
        position = cls(
            position_id=data['position_id'],
            user_id=data['user_id'],
            symbol=data['symbol'],
            side=data['side'],
            entry_price=data['entry_price'],
            quantity=data['current_quantity'],
            market_type=data.get('market_type', 'spot'),
            leverage=data.get('leverage', 1)
        )
        
        position.initial_quantity = data.get('initial_quantity', data['current_quantity'])
        position.status = data.get('status', 'OPEN')
        position.unrealized_pnl = data.get('unrealized_pnl', 0.0)
        position.realized_pnl = data.get('realized_pnl', 0.0)
        position.notes = data.get('notes', '')
        position.partial_closes = data.get('partial_closes', [])
        
        if data.get('open_time'):
            position.open_time = datetime.fromisoformat(data['open_time'])
        
        # إعادة بناء Take Profits
        if data.get('take_profits'):
            position.take_profits = [PositionTarget.from_dict(tp) for tp in data['take_profits']]
        
        # إعادة بناء Stop Loss
        if data.get('stop_loss'):
            position.stop_loss = PositionTarget.from_dict(data['stop_loss'])
        
        return position


class PositionManager:
    """مدير الصفقات المتقدم"""
    
    def __init__(self):
        self.positions: Dict[str, ManagedPosition] = {}
        self.user_positions: Dict[int, List[str]] = {}  # {user_id: [position_ids]}
    
    def create_position(self,
                        user_id: int,
                        position_id: str,
                        symbol: str,
                        side: str,
                        entry_price: float,
                        quantity: float,
                        market_type: str = 'spot',
                        leverage: int = 1) -> ManagedPosition:
        """إنشاء صفقة جديدة"""
        position = ManagedPosition(
            position_id=position_id,
            user_id=user_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            market_type=market_type,
            leverage=leverage
        )
        
        self.positions[position_id] = position
        
        if user_id not in self.user_positions:
            self.user_positions[user_id] = []
        self.user_positions[user_id].append(position_id)
        
        logger.info(f"تم إنشاء صفقة مدارة: {position_id} للمستخدم {user_id}")
        return position
    
    def get_position(self, position_id: str) -> Optional[ManagedPosition]:
        """الحصول على صفقة"""
        return self.positions.get(position_id)
    
    def get_user_positions(self, user_id: int, status: str = None) -> List[ManagedPosition]:
        """الحصول على صفقات المستخدم"""
        position_ids = self.user_positions.get(user_id, [])
        positions = [self.positions[pid] for pid in position_ids if pid in self.positions]
        
        if status:
            positions = [p for p in positions if p.status == status]
        
        return positions
    
    def remove_position(self, position_id: str):
        """حذف صفقة"""
        if position_id in self.positions:
            position = self.positions[position_id]
            user_id = position.user_id
            
            # حذف من القائمة العامة
            del self.positions[position_id]
            
            # حذف من قائمة المستخدم
            if user_id in self.user_positions and position_id in self.user_positions[user_id]:
                self.user_positions[user_id].remove(position_id)
            
            logger.info(f"تم حذف الصفقة: {position_id}")
            return True
        return False
    
    def update_prices(self, user_id: int, prices: Dict[str, float]) -> Dict[str, List[Tuple[str, PositionTarget]]]:
        """
        تحديث أسعار صفقات المستخدم وفحص الأهداف
        يُرجع: {position_id: [(target_type, target)]}
        """
        triggered_targets = {}
        
        positions = self.get_user_positions(user_id, status='OPEN')
        
        for position in positions:
            if position.symbol in prices:
                current_price = prices[position.symbol]
                
                # تحديث PnL
                position.update_unrealized_pnl(current_price)
                
                # فحص الأهداف
                triggered = position.check_targets(current_price)
                if triggered:
                    triggered_targets[position.position_id] = triggered
        
        return triggered_targets
    
    def get_all_open_positions(self) -> List[ManagedPosition]:
        """الحصول على جميع الصفقات المفتوحة"""
        return [p for p in self.positions.values() if p.status == 'OPEN']
    
    def get_positions_count(self, user_id: int) -> Dict[str, int]:
        """الحصول على عدد صفقات المستخدم"""
        positions = self.get_user_positions(user_id)
        
        return {
            'total': len(positions),
            'open': len([p for p in positions if p.status == 'OPEN']),
            'closed': len([p for p in positions if p.status == 'CLOSED'])
        }


# إنشاء مثيل عام لمدير الصفقات
position_manager = PositionManager()
