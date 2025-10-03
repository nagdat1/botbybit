# -*- coding: utf-8 -*-
"""
نظام إدارة الصفقات المتقدم مع دعم TP/SL وTrailing Stop
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

class TradePosition:
    """فئة تمثل صفقة مع إدارة متقدمة"""
    
    def __init__(self, 
                 position_id: str,
                 symbol: str,
                 side: str,
                 entry_price: float,
                 quantity: float,
                 leverage: int = 1,
                 take_profit: Optional[float] = None,
                 stop_loss: Optional[float] = None,
                 trailing_stop: Optional[float] = None,
                 trailing_step: Optional[float] = None):
        
        self.position_id = position_id
        self.symbol = symbol
        self.side = side.lower()
        self.entry_price = entry_price
        self.initial_quantity = quantity
        self.current_quantity = quantity
        self.leverage = leverage
        
        # أهداف الربح والخسارة
        self.take_profits = [] # قائمة بأهداف الربح المتعددة
        if take_profit:
            if isinstance(take_profit, (list, tuple)):
                self.take_profits = sorted(take_profit)
            else:
                self.take_profits = [take_profit]
        
        self.stop_losses = [] # قائمة بمستويات وقف الخسارة
        if stop_loss:
            if isinstance(stop_loss, (list, tuple)):
                self.stop_losses = sorted(stop_loss, reverse=True)
            else:
                self.stop_losses = [stop_loss]
        
        self.initial_stop_losses = self.stop_losses.copy()
        
        # إعدادات Trailing Stop
        self.trailing_stop = trailing_stop
        self.trailing_step = trailing_step
        self.trailing_activated = False
        self.highest_price = entry_price if side == 'buy' else float('-inf')
        self.lowest_price = entry_price if side == 'sell' else float('inf')
        
        # سجل الإغلاق الجزئي
        self.partial_closes: List[Dict] = []
        
        # معلومات الصفقة
        self.open_time = datetime.now()
        self.last_update = self.open_time
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
        self.current_price = entry_price
        self.status = 'open'  # open, partially_closed, closed
        
        # نسب الإغلاق الجزئي
        self.partial_close_levels = [
            {'percent': 25, 'price': None, 'executed': False},
            {'percent': 50, 'price': None, 'executed': False},
            {'percent': 75, 'price': None, 'executed': False}
        ]
    
    def update_price(self, current_price: float) -> Dict:
        """تحديث السعر الحالي وحساب PnL والتحقق من TP/SL"""
        self.current_price = current_price
        self.last_update = datetime.now()
        
        # تحديث أعلى/أقل سعر للـ Trailing Stop
        if self.side == 'buy':
            self.highest_price = max(self.highest_price, current_price)
        else:
            self.lowest_price = min(self.lowest_price, current_price)
        
        # حساب PnL
        if self.side == 'buy':
            self.unrealized_pnl = (current_price - self.entry_price) * self.current_quantity * self.leverage
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.current_quantity * self.leverage
        
        events = []
        
        # التحقق من TP
        if self.take_profit and self.should_take_profit(current_price):
            events.append({
                'type': 'take_profit',
                'price': current_price,
                'quantity': self.current_quantity,
                'pnl': self.unrealized_pnl
            })
        
        # التحقق من SL
        if self.stop_loss and self.should_stop_loss(current_price):
            events.append({
                'type': 'stop_loss',
                'price': current_price,
                'quantity': self.current_quantity,
                'pnl': self.unrealized_pnl
            })
        
        # تحديث Trailing Stop
        if self.trailing_stop and self.should_update_trailing_stop(current_price):
            self.update_trailing_stop(current_price)
            events.append({
                'type': 'trailing_stop_update',
                'price': current_price,
                'new_stop': self.stop_loss
            })
        
        # التحقق من مستويات الإغلاق الجزئي
        for level in self.partial_close_levels:
            if not level['executed'] and self.should_partial_close(current_price, level['percent']):
                events.append({
                    'type': 'partial_close',
                    'price': current_price,
                    'percent': level['percent'],
                    'quantity': self.current_quantity * (level['percent'] / 100)
                })
                level['executed'] = True
        
        return {
            'position_id': self.position_id,
            'current_price': current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'events': events
        }
    
    def should_take_profit(self, price: float) -> bool:
        """التحقق من تحقق هدف الربح"""
        if not self.take_profit:
            return False
            
        if self.side == 'buy':
            return price >= self.take_profit
        else:
            return price <= self.take_profit
    
    def should_stop_loss(self, price: float) -> bool:
        """التحقق من ضرب وقف الخسارة"""
        if not self.stop_loss:
            return False
            
        if self.side == 'buy':
            return price <= self.stop_loss
        else:
            return price >= self.stop_loss
    
    def should_update_trailing_stop(self, price: float) -> bool:
        """التحقق من تحديث Trailing Stop"""
        if not (self.trailing_stop and self.trailing_step):
            return False
        
        if self.side == 'buy':
            price_move = price - self.highest_price
            return price_move >= self.trailing_step
        else:
            price_move = self.lowest_price - price
            return price_move >= self.trailing_step
    
    def update_trailing_stop(self, current_price: float):
        """تحديث مستوى Trailing Stop"""
        if not (self.trailing_stop and self.trailing_step):
            return
            
        if self.side == 'buy':
            new_stop = current_price - self.trailing_stop
            if not self.stop_loss or new_stop > self.stop_loss:
                self.stop_loss = new_stop
                self.trailing_activated = True
        else:
            new_stop = current_price + self.trailing_stop
            if not self.stop_loss or new_stop < self.stop_loss:
                self.stop_loss = new_stop
                self.trailing_activated = True
    
    def should_partial_close(self, price: float, percent: float) -> bool:
        """التحقق من تحقق شروط الإغلاق الجزئي"""
        if self.status == 'closed':
            return False
            
        profit_percent = ((price - self.entry_price) / self.entry_price * 100) if self.side == 'buy' else \
                        ((self.entry_price - price) / self.entry_price * 100)
                        
        return profit_percent >= percent
    
    def execute_partial_close(self, price: float, close_percent: float) -> Dict:
        """تنفيذ إغلاق جزئي للصفقة"""
        if self.status == 'closed' or close_percent >= 100:
            return {'success': False, 'error': 'Invalid close percent'}
        
        close_quantity = self.current_quantity * (close_percent / 100)
        if self.side == 'buy':
            realized_pnl = (price - self.entry_price) * close_quantity * self.leverage
        else:
            realized_pnl = (self.entry_price - price) * close_quantity * self.leverage
        
        self.current_quantity -= close_quantity
        self.realized_pnl += realized_pnl
        
        if self.current_quantity <= 0:
            self.status = 'closed'
        else:
            self.status = 'partially_closed'
        
        close_record = {
            'time': datetime.now(),
            'price': price,
            'quantity': close_quantity,
            'percent': close_percent,
            'realized_pnl': realized_pnl
        }
        
        self.partial_closes.append(close_record)
        
        return {
            'success': True,
            'close_record': close_record,
            'remaining_quantity': self.current_quantity,
            'total_realized_pnl': self.realized_pnl
        }
    
    def close_position(self, price: float) -> Dict:
        """إغلاق الصفقة بالكامل"""
        if self.status == 'closed':
            return {'success': False, 'error': 'Position already closed'}
        
        final_pnl = self.realized_pnl
        if self.current_quantity > 0:
            if self.side == 'buy':
                final_pnl += (price - self.entry_price) * self.current_quantity * self.leverage
            else:
                final_pnl += (self.entry_price - price) * self.current_quantity * self.leverage
        
        self.current_quantity = 0
        self.status = 'closed'
        self.realized_pnl = final_pnl
        
        close_record = {
            'time': datetime.now(),
            'price': price,
            'quantity': self.initial_quantity,
            'realized_pnl': final_pnl,
            'duration': (datetime.now() - self.open_time).total_seconds() / 3600  # بالساعات
        }
        
        return {
            'success': True,
            'close_record': close_record,
            'final_pnl': final_pnl
        }
    
    def update_tp_sl(self, new_tp: Optional[float] = None, new_sl: Optional[float] = None) -> Dict:
        """تحديث مستويات TP/SL"""
        if self.status == 'closed':
            return {'success': False, 'error': 'Position closed'}
        
        if new_tp is not None:
            self.take_profit = new_tp
        
        if new_sl is not None:
            self.stop_loss = new_sl
            # إعادة ضبط Trailing Stop عند تغيير SL يدوياً
            self.trailing_activated = False
        
        return {
            'success': True,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss
        }
    
    def get_position_info(self) -> Dict:
        """الحصول على معلومات الصفقة كاملة"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'initial_quantity': self.initial_quantity,
            'current_quantity': self.current_quantity,
            'leverage': self.leverage,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'trailing_stop': self.trailing_stop,
            'trailing_step': self.trailing_step,
            'trailing_activated': self.trailing_activated,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'status': self.status,
            'open_time': self.open_time.isoformat(),
            'last_update': self.last_update.isoformat(),
            'partial_closes': self.partial_closes
        }

class TradeManager:
    """فئة لإدارة جميع الصفقات النشطة"""
    
    def __init__(self):
        self.active_positions: Dict[str, TradePosition] = {}
        self.closed_positions: Dict[str, Dict] = {}
        self.last_update = datetime.now()
    
    def create_position(self, 
                       position_id: str,
                       symbol: str,
                       side: str,
                       entry_price: float,
                       quantity: float,
                       leverage: int = 1,
                       take_profit: Optional[float] = None,
                       stop_loss: Optional[float] = None,
                       trailing_stop: Optional[float] = None,
                       trailing_step: Optional[float] = None) -> TradePosition:
        """إنشاء صفقة جديدة"""
        position = TradePosition(
            position_id=position_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss,
            trailing_stop=trailing_stop,
            trailing_step=trailing_step
        )
        
        self.active_positions[position_id] = position
        logger.info(f"تم إنشاء صفقة جديدة: {position_id} {symbol} {side}")
        return position
    
    def update_prices(self, prices: Dict[str, float]) -> List[Dict]:
        """تحديث أسعار جميع الصفقات النشطة"""
        events = []
        self.last_update = datetime.now()
        
        for position_id, position in list(self.active_positions.items()):
            if position.symbol in prices:
                update_result = position.update_price(prices[position.symbol])
                
                if update_result['events']:
                    events.extend([{
                        'position_id': position_id,
                        **event
                    } for event in update_result['events']])
                    
                    # إغلاق الصفقة إذا تم ضرب TP أو SL
                    if any(e['type'] in ['take_profit', 'stop_loss'] for e in update_result['events']):
                        close_result = position.close_position(prices[position.symbol])
                        if close_result['success']:
                            self.closed_positions[position_id] = position.get_position_info()
                            del self.active_positions[position_id]
        
        return events
    
    def close_position(self, position_id: str, price: float) -> Dict:
        """إغلاق صفقة محددة"""
        if position_id not in self.active_positions:
            return {'success': False, 'error': 'Position not found'}
        
        position = self.active_positions[position_id]
        result = position.close_position(price)
        
        if result['success']:
            self.closed_positions[position_id] = position.get_position_info()
            del self.active_positions[position_id]
        
        return result
    
    def partial_close(self, position_id: str, price: float, close_percent: float) -> Dict:
        """تنفيذ إغلاق جزئي لصفقة محددة"""
        if position_id not in self.active_positions:
            return {'success': False, 'error': 'Position not found'}
        
        position = self.active_positions[position_id]
        result = position.execute_partial_close(price, close_percent)
        
        if result['success'] and position.status == 'closed':
            self.closed_positions[position_id] = position.get_position_info()
            del self.active_positions[position_id]
        
        return result
    
    def update_position_tp_sl(self, 
                            position_id: str, 
                            new_tp: Optional[float] = None, 
                            new_sl: Optional[float] = None) -> Dict:
        """تحديث TP/SL لصفقة محددة"""
        if position_id not in self.active_positions:
            return {'success': False, 'error': 'Position not found'}
            
        position = self.active_positions[position_id]
        return position.update_tp_sl(new_tp, new_sl)
    
    def get_active_positions(self) -> Dict[str, Dict]:
        """الحصول على جميع الصفقات النشطة"""
        return {
            position_id: position.get_position_info()
            for position_id, position in self.active_positions.items()
        }
    
    def get_closed_positions(self) -> Dict[str, Dict]:
        """الحصول على الصفقات المغلقة"""
        return self.closed_positions
    
    def get_position_status(self, position_id: str) -> Optional[Dict]:
        """الحصول على حالة صفقة محددة"""
        if position_id in self.active_positions:
            return self.active_positions[position_id].get_position_info()
        elif position_id in self.closed_positions:
            return self.closed_positions[position_id]
        return None