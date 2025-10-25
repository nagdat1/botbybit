#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص الرصيد المتقدم - يعمل مع أي رقم متغير
"""

import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    INVERSE = "inverse"

class ExchangeType(Enum):
    BYBIT = "bybit"
    MEXC = "mexc"
    BINANCE = "binance"

@dataclass
class BalanceInfo:
    """معلومات الرصيد"""
    available: float
    total: float
    locked: float
    currency: str = "USDT"
    
    def __str__(self):
        return f"{self.available:.8f} {self.currency} (متاح: {self.available:.2f}, محجوز: {self.locked:.2f})"

@dataclass
class OrderRequirements:
    """متطلبات الطلب"""
    quantity: float
    price: float
    leverage: int = 1
    market_type: MarketType = MarketType.SPOT
    exchange: ExchangeType = ExchangeType.BYBIT
    
    @property
    def order_value(self) -> float:
        """قيمة الطلب الإجمالية"""
        return self.quantity * self.price
    
    @property
    def required_margin(self) -> float:
        """الهامش المطلوب"""
        if self.market_type == MarketType.SPOT:
            return self.order_value
        else:
            return self.order_value / self.leverage
    
    @property
    def min_order_value(self) -> float:
        """الحد الأدنى لقيمة الطلب"""
        min_quantity = self._get_min_quantity()
        return min_quantity * self.price
    
    @property
    def min_required_margin(self) -> float:
        """الحد الأدنى للهامش المطلوب"""
        if self.market_type == MarketType.SPOT:
            return self.min_order_value
        else:
            return self.min_order_value / self.leverage
    
    def _get_min_quantity(self) -> float:
        """الحصول على الحد الأدنى للكمية حسب المنصة"""
        min_quantities = {
            ExchangeType.BYBIT: {
                MarketType.SPOT: 0.001,
                MarketType.FUTURES: 0.001,
                MarketType.INVERSE: 0.001
            },
            ExchangeType.MEXC: {
                MarketType.SPOT: 0.001
            },
            ExchangeType.BINANCE: {
                MarketType.SPOT: 0.001,
                MarketType.FUTURES: 0.001
            }
        }
        
        return min_quantities.get(self.exchange, {}).get(self.market_type, 0.001)

@dataclass
class BalanceCheckResult:
    """نتيجة فحص الرصيد"""
    success: bool
    can_execute: bool
    message: str
    available_balance: float
    required_balance: float
    shortage: float = 0.0
    suggestions: List[str] = None
    adjusted_quantity: Optional[float] = None
    adjusted_order_value: Optional[float] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        
        if not self.success:
            self.shortage = self.required_balance - self.available_balance

class AdvancedBalanceChecker:
    """فحص الرصيد المتقدم"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_balance(self, balance_info: BalanceInfo, order_req: OrderRequirements) -> BalanceCheckResult:
        """
        فحص الرصيد مع أي رقم متغير
        
        Args:
            balance_info: معلومات الرصيد المتاح
            order_req: متطلبات الطلب
            
        Returns:
            نتيجة فحص الرصيد
        """
        try:
            self.logger.info(f"فحص الرصيد: {balance_info}")
            self.logger.info(f"متطلبات الطلب: {order_req.quantity} @ {order_req.price}")
            
            # فحص الرصيد للطلب المطلوب
            if balance_info.available >= order_req.required_margin:
                return BalanceCheckResult(
                    success=True,
                    can_execute=True,
                    message=f"الرصيد كافي للطلب المطلوب",
                    available_balance=balance_info.available,
                    required_balance=order_req.required_margin,
                    suggestions=[]
                )
            
            # الرصيد غير كافي - فحص الحد الأدنى
            if order_req.quantity < order_req._get_min_quantity():
                return self._check_minimum_order(balance_info, order_req)
            
            # الرصيد غير كافي للطلب المطلوب
            return self._generate_insufficient_balance_result(balance_info, order_req)
            
        except Exception as e:
            self.logger.error(f"خطأ في فحص الرصيد: {e}")
            return BalanceCheckResult(
                success=False,
                can_execute=False,
                message=f"خطأ في فحص الرصيد: {str(e)}",
                available_balance=balance_info.available,
                required_balance=order_req.required_margin,
                suggestions=["تحقق من صحة البيانات المدخلة"]
            )
    
    def _check_minimum_order(self, balance_info: BalanceInfo, order_req: OrderRequirements) -> BalanceCheckResult:
        """فحص إمكانية تنفيذ الحد الأدنى"""
        min_margin = order_req.min_required_margin
        
        if balance_info.available >= min_margin:
            # يمكن تنفيذ الحد الأدنى
            min_quantity = order_req._get_min_quantity()
            min_order_value = min_quantity * order_req.price
            
            return BalanceCheckResult(
                success=True,
                can_execute=True,
                message=f"الرصيد كافي للحد الأدنى فقط - سيتم تعديل الكمية",
                available_balance=balance_info.available,
                required_balance=min_margin,
                adjusted_quantity=min_quantity,
                adjusted_order_value=min_order_value,
                suggestions=[
                    f"سيتم تعديل الكمية من {order_req.quantity:.8f} إلى {min_quantity:.8f}",
                    f"قيمة الطلب ستكون {min_order_value:.2f} بدلاً من {order_req.order_value:.2f}"
                ]
            )
        else:
            # لا يمكن تنفيذ حتى الحد الأدنى
            return BalanceCheckResult(
                success=False,
                can_execute=False,
                message=f"الرصيد غير كافي حتى للحد الأدنى",
                available_balance=balance_info.available,
                required_balance=min_margin,
                suggestions=self._generate_suggestions(balance_info, order_req, min_margin)
            )
    
    def _generate_insufficient_balance_result(self, balance_info: BalanceInfo, order_req: OrderRequirements) -> BalanceCheckResult:
        """إنشاء نتيجة رصيد غير كافي"""
        return BalanceCheckResult(
            success=False,
            can_execute=False,
            message=f"الرصيد غير كافي للطلب المطلوب",
            available_balance=balance_info.available,
            required_balance=order_req.required_margin,
            suggestions=self._generate_suggestions(balance_info, order_req, order_req.required_margin)
        )
    
    def _generate_suggestions(self, balance_info: BalanceInfo, order_req: OrderRequirements, required_amount: float) -> List[str]:
        """إنشاء اقتراحات لحل مشكلة الرصيد"""
        suggestions = []
        shortage = required_amount - balance_info.available
        
        # اقتراح 1: تقليل مبلغ التداول
        if order_req.market_type == MarketType.SPOT:
            max_affordable_quantity = balance_info.available / order_req.price
            suggestions.append(f"تقليل الكمية إلى {max_affordable_quantity:.8f} (أقصى ما يمكن تحمله)")
        else:
            max_affordable_quantity = (balance_info.available * order_req.leverage) / order_req.price
            suggestions.append(f"تقليل الكمية إلى {max_affordable_quantity:.8f} (أقصى ما يمكن تحمله)")
        
        # اقتراح 2: زيادة الرافعة (للفيوتشر فقط)
        if order_req.market_type != MarketType.SPOT:
            min_leverage_needed = int(order_req.order_value / balance_info.available) + 1
            if min_leverage_needed <= 100:  # حد أقصى معقول للرافعة
                suggestions.append(f"زيادة الرافعة إلى {min_leverage_needed}x لتقليل الهامش المطلوب")
        
        # اقتراح 3: إضافة رصيد
        suggestions.append(f"إضافة {shortage:.2f} {balance_info.currency} للحساب")
        
        # اقتراح 4: انتظار انخفاض السعر
        if order_req.market_type == MarketType.SPOT:
            affordable_price = balance_info.available / order_req.quantity
            suggestions.append(f"انتظار انخفاض السعر إلى {affordable_price:.2f} أو أقل")
        
        return suggestions
    
    def calculate_optimal_order(self, balance_info: BalanceInfo, order_req: OrderRequirements) -> OrderRequirements:
        """حساب الطلب الأمثل بناءً على الرصيد المتاح"""
        try:
            if order_req.market_type == MarketType.SPOT:
                # للسبوت: الكمية = الرصيد المتاح / السعر
                optimal_quantity = balance_info.available / order_req.price
            else:
                # للفيوتشر: الكمية = (الرصيد المتاح × الرافعة) / السعر
                optimal_quantity = (balance_info.available * order_req.leverage) / order_req.price
            
            # ضمان الحد الأدنى
            min_quantity = order_req._get_min_quantity()
            if optimal_quantity < min_quantity:
                optimal_quantity = min_quantity
            
            # إنشاء طلب محسن
            optimal_order = OrderRequirements(
                quantity=optimal_quantity,
                price=order_req.price,
                leverage=order_req.leverage,
                market_type=order_req.market_type,
                exchange=order_req.exchange
            )
            
            self.logger.info(f"الطلب الأمثل: {optimal_quantity:.8f} @ {order_req.price}")
            return optimal_order
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب الطلب الأمثل: {e}")
            return order_req

def test_balance_checker():
    """اختبار نظام فحص الرصيد"""
    print("=" * 80)
    print("اختبار نظام فحص الرصيد المتقدم")
    print("=" * 80)
    
    checker = AdvancedBalanceChecker()
    
    # اختبار 1: الرصيد كافي
    print("\nاختبار 1: الرصيد كافي")
    balance1 = BalanceInfo(available=100.0, total=100.0, locked=0.0)
    order1 = OrderRequirements(quantity=0.001, price=50000, leverage=1, market_type=MarketType.SPOT)
    result1 = checker.check_balance(balance1, order1)
    print(f"النتيجة: {result1.message}")
    print(f"يمكن التنفيذ: {result1.can_execute}")
    
    # اختبار 2: الرصيد غير كافي
    print("\nاختبار 2: الرصيد غير كافي")
    balance2 = BalanceInfo(available=30.0, total=30.0, locked=0.0)
    order2 = OrderRequirements(quantity=0.001, price=50000, leverage=1, market_type=MarketType.SPOT)
    result2 = checker.check_balance(balance2, order2)
    print(f"النتيجة: {result2.message}")
    print(f"يمكن التنفيذ: {result2.can_execute}")
    print("الاقتراحات:")
    for suggestion in result2.suggestions:
        print(f"  - {suggestion}")
    
    # اختبار 3: فيوتشر مع رافعة
    print("\nاختبار 3: فيوتشر مع رافعة")
    balance3 = BalanceInfo(available=50.0, total=50.0, locked=0.0)
    order3 = OrderRequirements(quantity=0.01, price=50000, leverage=10, market_type=MarketType.FUTURES)
    result3 = checker.check_balance(balance3, order3)
    print(f"النتيجة: {result3.message}")
    print(f"يمكن التنفيذ: {result3.can_execute}")
    
    # اختبار 4: حساب الطلب الأمثل
    print("\nاختبار 4: حساب الطلب الأمثل")
    optimal_order = checker.calculate_optimal_order(balance2, order2)
    print(f"الكمية الأصلية: {order2.quantity}")
    print(f"الكمية الأمثل: {optimal_order.quantity}")
    print(f"قيمة الطلب الأمثل: {optimal_order.order_value:.2f} USDT")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_balance_checker()
