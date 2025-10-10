#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة إدارة أدوات الصفقات المتقدمة
Take Profit, Stop Loss, Partial Close, Trailing Stop
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TakeProfitLevel:
    """مستوى هدف الربح"""
    price: float  # السعر المستهدف
    percentage: float  # نسبة الإغلاق (مثال: 50 = 50%)
    hit: bool = False  # تم تحقيق الهدف؟
    hit_time: Optional[datetime] = None  # وقت تحقيق الهدف
    
    def __post_init__(self):
        """التحقق من صحة البيانات"""
        if self.percentage <= 0 or self.percentage > 100:
            raise ValueError(f"نسبة الإغلاق يجب أن تكون بين 0 و 100، القيمة: {self.percentage}")


@dataclass
class StopLoss:
    """وقف الخسارة"""
    price: float  # سعر وقف الخسارة
    initial_price: float  # السعر الأصلي
    is_trailing: bool = False  # هل هو trailing stop؟
    trailing_distance: float = 0.0  # المسافة بالنسبة المئوية
    moved_to_breakeven: bool = False  # تم نقله للتعادل؟
    last_update: Optional[datetime] = None  # آخر تحديث
    
    def update_trailing(self, current_price: float, side: str):
        """تحديث trailing stop"""
        if not self.is_trailing or self.trailing_distance <= 0:
            return False
        
        try:
            if side.lower() == "buy":
                # في صفقة الشراء، الـ stop يرتفع مع السعر
                new_stop = current_price * (1 - self.trailing_distance / 100)
                if new_stop > self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"✅ تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
            else:  # sell
                # في صفقة البيع، الـ stop ينخفض مع السعر
                new_stop = current_price * (1 + self.trailing_distance / 100)
                if new_stop < self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"✅ تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
        except Exception as e:
            logger.error(f"خطأ في تحديث trailing stop: {e}")
        
        return False
    
    def move_to_breakeven(self, entry_price: float):
        """نقل وقف الخسارة إلى نقطة التعادل"""
        if not self.moved_to_breakeven:
            self.price = entry_price
            self.moved_to_breakeven = True
            self.last_update = datetime.now()
            logger.info(f"🔒 تم نقل Stop Loss إلى نقطة التعادل: {entry_price:.6f}")
            return True
        return False


@dataclass
class PositionManagement:
    """إدارة متقدمة للصفقة"""
    position_id: str
    symbol: str
    side: str  # buy or sell
    entry_price: float
    quantity: float  # الكمية الأصلية
    remaining_quantity: float  # الكمية المتبقية
    market_type: str  # spot or futures
    leverage: int = 1
    
    # أدوات الإدارة
    take_profits: List[TakeProfitLevel] = field(default_factory=list)
    stop_loss: Optional[StopLoss] = None
    
    # حالة الصفقة
    total_closed_percentage: float = 0.0
    realized_pnl: float = 0.0
    closed_parts: List[Dict] = field(default_factory=list)
    
    def add_take_profit(self, price: float, percentage: float) -> bool:
        """إضافة مستوى هدف ربح"""
        try:
            # التحقق من أن السعر في الاتجاه الصحيح
            if self.side.lower() == "buy" and price <= self.entry_price:
                logger.error(f"سعر TP يجب أن يكون أعلى من سعر الدخول في صفقة الشراء")
                return False
            elif self.side.lower() == "sell" and price >= self.entry_price:
                logger.error(f"سعر TP يجب أن يكون أقل من سعر الدخول في صفقة البيع")
                return False
            
            # التحقق من أن مجموع النسب لا يتجاوز 100%
            total_percentage = sum(tp.percentage for tp in self.take_profits if not tp.hit) + percentage
            if total_percentage > 100:
                logger.error(f"مجموع نسب TP يتجاوز 100% ({total_percentage}%)")
                return False
            
            tp = TakeProfitLevel(price=price, percentage=percentage)
            self.take_profits.append(tp)
            # ترتيب حسب السعر
            self.take_profits.sort(key=lambda x: x.price if self.side.lower() == "buy" else -x.price)
            logger.info(f"✅ تم إضافة TP: {price:.6f} ({percentage}%)")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة take profit: {e}")
            return False
    
    def set_stop_loss(self, price: float, is_trailing: bool = False, 
                     trailing_distance: float = 0.0) -> bool:
        """تعيين وقف الخسارة"""
        try:
            # التحقق من أن السعر في الاتجاه الصحيح
            if self.side.lower() == "buy" and price >= self.entry_price:
                logger.error(f"سعر SL يجب أن يكون أقل من سعر الدخول في صفقة الشراء")
                return False
            elif self.side.lower() == "sell" and price <= self.entry_price:
                logger.error(f"سعر SL يجب أن يكون أعلى من سعر الدخول في صفقة البيع")
                return False
            
            self.stop_loss = StopLoss(
                price=price,
                initial_price=price,
                is_trailing=is_trailing,
                trailing_distance=trailing_distance,
                last_update=datetime.now()
            )
            logger.info(f"✅ تم تعيين SL: {price:.6f} {'(Trailing)' if is_trailing else ''}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين stop loss: {e}")
            return False
    
    def check_and_execute_tp(self, current_price: float) -> List[Dict]:
        """التحقق من تحقيق أهداف الربح وتنفيذها"""
        executed = []
        
        for tp in self.take_profits:
            if tp.hit:
                continue
            
            # التحقق من تحقيق الهدف
            hit = False
            if self.side.lower() == "buy":
                hit = current_price >= tp.price
            else:  # sell
                hit = current_price <= tp.price
            
            if hit:
                # حساب الكمية المغلقة
                close_qty = (self.quantity * tp.percentage / 100)
                
                # حساب الربح
                if self.side.lower() == "buy":
                    pnl = (current_price - self.entry_price) * close_qty
                else:
                    pnl = (self.entry_price - current_price) * close_qty
                
                # تسجيل الإغلاق
                tp.hit = True
                tp.hit_time = datetime.now()
                self.total_closed_percentage += tp.percentage
                self.remaining_quantity -= close_qty
                self.realized_pnl += pnl
                
                close_info = {
                    'type': 'take_profit',
                    'price': current_price,
                    'tp_target': tp.price,
                    'percentage': tp.percentage,
                    'quantity': close_qty,
                    'pnl': pnl,
                    'time': tp.hit_time
                }
                self.closed_parts.append(close_info)
                executed.append(close_info)
                
                logger.info(f"🎯 تم تحقيق TP عند {current_price:.6f}: إغلاق {tp.percentage}% بربح {pnl:.2f}")
                
                # نقل SL للتعادل بعد أول هدف
                if len(executed) == 1 and self.stop_loss and not self.stop_loss.moved_to_breakeven:
                    self.stop_loss.move_to_breakeven(self.entry_price)
        
        return executed
    
    def check_stop_loss(self, current_price: float) -> Optional[Dict]:
        """التحقق من تفعيل وقف الخسارة"""
        if not self.stop_loss:
            return None
        
        # تحديث trailing stop إذا كان مفعلاً
        if self.stop_loss.is_trailing:
            self.stop_loss.update_trailing(current_price, self.side)
        
        # التحقق من تفعيل Stop Loss
        hit = False
        if self.side.lower() == "buy":
            hit = current_price <= self.stop_loss.price
        else:  # sell
            hit = current_price >= self.stop_loss.price
        
        if hit:
            # حساب الخسارة
            if self.side.lower() == "buy":
                pnl = (current_price - self.entry_price) * self.remaining_quantity
            else:
                pnl = (self.entry_price - current_price) * self.remaining_quantity
            
            self.realized_pnl += pnl
            
            sl_info = {
                'type': 'stop_loss',
                'price': current_price,
                'sl_target': self.stop_loss.price,
                'percentage': 100 - self.total_closed_percentage,
                'quantity': self.remaining_quantity,
                'pnl': pnl,
                'time': datetime.now(),
                'was_breakeven': self.stop_loss.moved_to_breakeven
            }
            
            logger.warning(f"🛑 تم تفعيل SL عند {current_price:.6f}: {pnl:.2f}")
            
            return sl_info
        
        return None
    
    def get_status_message(self, current_price: float) -> str:
        """الحصول على رسالة حالة الصفقة"""
        try:
            unrealized_pnl = 0.0
            if self.side.lower() == "buy":
                unrealized_pnl = (current_price - self.entry_price) * self.remaining_quantity
            else:
                unrealized_pnl = (self.entry_price - current_price) * self.remaining_quantity
            
            total_pnl = self.realized_pnl + unrealized_pnl
            
            message = f"📊 **إدارة الصفقة: {self.symbol}**\n\n"
            message += f"🔄 النوع: {self.side.upper()}\n"
            message += f"💲 سعر الدخول: {self.entry_price:.6f}\n"
            message += f"💲 السعر الحالي: {current_price:.6f}\n"
            message += f"📈 الكمية الأصلية: {self.quantity:.6f}\n"
            message += f"📉 المتبقي: {self.remaining_quantity:.6f} ({100 - self.total_closed_percentage:.1f}%)\n\n"
            
            # الأهداف
            message += "🎯 **أهداف الربح:**\n"
            for i, tp in enumerate(self.take_profits, 1):
                status = "✅" if tp.hit else "⏳"
                distance = ((tp.price - current_price) / current_price) * 100
                message += f"  {status} TP{i}: {tp.price:.6f} ({tp.percentage}%) - "
                message += f"{'تم تحقيقه' if tp.hit else f'{abs(distance):.2f}% متبقي'}\n"
            
            # وقف الخسارة
            if self.stop_loss:
                distance = ((current_price - self.stop_loss.price) / current_price) * 100
                sl_type = ""
                if self.stop_loss.is_trailing:
                    sl_type = " (Trailing)"
                if self.stop_loss.moved_to_breakeven:
                    sl_type += " [BE]"
                
                message += f"\n🛑 **Stop Loss:** {self.stop_loss.price:.6f}{sl_type}\n"
                message += f"   المسافة: {abs(distance):.2f}%\n"
            
            # الأرباح/الخسائر
            message += f"\n💰 **النتائج:**\n"
            message += f"  الربح المحقق: {self.realized_pnl:.2f}\n"
            message += f"  الربح غير المحقق: {unrealized_pnl:.2f}\n"
            message += f"  الإجمالي: {total_pnl:.2f}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الحالة: {e}")
            return "❌ خطأ في عرض حالة الصفقة"
    
    def calculate_risk_reward_ratio(self) -> float:
        """حساب نسبة المخاطرة إلى العائد"""
        if not self.stop_loss or not self.take_profits:
            return 0.0
        
        try:
            # حساب المخاطرة
            if self.side.lower() == "buy":
                risk = self.entry_price - self.stop_loss.initial_price
            else:
                risk = self.stop_loss.initial_price - self.entry_price
            
            # حساب العائد المتوقع (متوسط جميع الأهداف)
            total_reward = 0.0
            for tp in self.take_profits:
                if self.side.lower() == "buy":
                    reward = tp.price - self.entry_price
                else:
                    reward = self.entry_price - tp.price
                total_reward += reward * (tp.percentage / 100)
            
            if risk > 0:
                rr_ratio = total_reward / risk
                return rr_ratio
            
        except Exception as e:
            logger.error(f"خطأ في حساب R:R: {e}")
        
        return 0.0


class TradeToolsManager:
    """مدير أدوات التداول"""
    
    def __init__(self):
        self.managed_positions: Dict[str, PositionManagement] = {}
        logger.info("✅ تم تهيئة TradeToolsManager")
    
    def create_managed_position(self, position_id: str, symbol: str, side: str,
                               entry_price: float, quantity: float, market_type: str,
                               leverage: int = 1) -> Optional[PositionManagement]:
        """إنشاء صفقة مدارة"""
        try:
            if position_id in self.managed_positions:
                logger.warning(f"الصفقة {position_id} موجودة بالفعل")
                return self.managed_positions[position_id]
            
            pm = PositionManagement(
                position_id=position_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                remaining_quantity=quantity,
                market_type=market_type,
                leverage=leverage
            )
            
            self.managed_positions[position_id] = pm
            logger.info(f"✅ تم إنشاء إدارة للصفقة {position_id}")
            return pm
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء صفقة مدارة: {e}")
            return None
    
    def get_managed_position(self, position_id: str) -> Optional[PositionManagement]:
        """الحصول على صفقة مدارة"""
        return self.managed_positions.get(position_id)
    
    def remove_managed_position(self, position_id: str) -> bool:
        """إزالة صفقة مدارة"""
        if position_id in self.managed_positions:
            del self.managed_positions[position_id]
            logger.info(f"✅ تم إزالة إدارة الصفقة {position_id}")
            return True
        return False
    
    def update_all_positions(self, prices: Dict[str, float]) -> Dict[str, List[Dict]]:
        """تحديث جميع الصفقات المدارة"""
        results = {}
        
        for position_id, pm in list(self.managed_positions.items()):
            if pm.symbol in prices:
                current_price = prices[pm.symbol]
                
                # التحقق من الأهداف
                tp_executions = pm.check_and_execute_tp(current_price)
                
                # التحقق من وقف الخسارة
                sl_execution = pm.check_stop_loss(current_price)
                
                if tp_executions or sl_execution:
                    results[position_id] = {
                        'take_profits': tp_executions,
                        'stop_loss': sl_execution
                    }
                
                # إزالة الصفقة إذا تم إغلاقها بالكامل
                if pm.remaining_quantity <= 0 or sl_execution:
                    self.remove_managed_position(position_id)
        
        return results
    
    def set_default_levels(self, position_id: str, tp_percentages: List[float] = None,
                          sl_percentage: float = 2.0, trailing: bool = False) -> bool:
        """تعيين مستويات افتراضية ذكية"""
        pm = self.get_managed_position(position_id)
        if not pm:
            return False
        
        try:
            # مستويات TP افتراضية
            if tp_percentages is None:
                tp_percentages = [1.5, 3.0, 5.0]  # أهداف بنسب متزايدة
            
            partial_percentages = [50, 30, 20]  # نسب الإغلاق
            
            for i, tp_pct in enumerate(tp_percentages):
                if i >= len(partial_percentages):
                    break
                
                if pm.side.lower() == "buy":
                    tp_price = pm.entry_price * (1 + tp_pct / 100)
                else:
                    tp_price = pm.entry_price * (1 - tp_pct / 100)
                
                pm.add_take_profit(tp_price, partial_percentages[i])
            
            # Stop Loss افتراضي
            if pm.side.lower() == "buy":
                sl_price = pm.entry_price * (1 - sl_percentage / 100)
            else:
                sl_price = pm.entry_price * (1 + sl_percentage / 100)
            
            pm.set_stop_loss(sl_price, is_trailing=trailing, trailing_distance=sl_percentage)
            
            logger.info(f"✅ تم تعيين مستويات افتراضية للصفقة {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين المستويات الافتراضية: {e}")
            return False


# إنشاء مثيل عام
trade_tools_manager = TradeToolsManager()

