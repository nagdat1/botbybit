#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الصفقات المتقدم - Advanced Trade Executor
يدعم تنفيذ الصفقات المتقدم مع إدارة مخاطر ذكية وتحسين الأداء
"""

import logging
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """حالة التنفيذ"""
    PENDING = "pending"
    PROCESSING = "processing"
    EXECUTED = "executed"
    PARTIALLY_EXECUTED = "partially_executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ExecutionStrategy(Enum):
    """استراتيجية التنفيذ"""
    IMMEDIATE = "immediate"
    TWAP = "twap"  # Time Weighted Average Price
    VWAP = "vwap"  # Volume Weighted Average Price
    ICEBERG = "iceberg"
    ADAPTIVE = "adaptive"

class OrderType(Enum):
    """نوع الأمر"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

@dataclass
class ExecutionConfig:
    """إعدادات التنفيذ"""
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    slippage_tolerance: float = 0.01  # 1%
    min_order_size: float = 10.0
    max_order_size: float = 10000.0
    execution_strategy: ExecutionStrategy = ExecutionStrategy.IMMEDIATE
    order_type: OrderType = OrderType.MARKET
    price_improvement: bool = True
    smart_routing: bool = True

@dataclass
class ExecutionResult:
    """نتيجة التنفيذ"""
    success: bool
    order_id: Optional[str]
    executed_price: Optional[float]
    executed_quantity: Optional[float]
    remaining_quantity: Optional[float]
    fees: Optional[float]
    slippage: Optional[float]
    execution_time: Optional[float]
    status: ExecutionStatus
    error_message: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketConditions:
    """ظروف السوق"""
    volatility: float
    volume: float
    spread: float
    liquidity: float
    trend: str  # 'bullish', 'bearish', 'sideways'
    momentum: float
    last_updated: datetime = field(default_factory=datetime.now)

class AdvancedTradeExecutor:
    """منفذ الصفقات المتقدم"""
    
    def __init__(self, user_id: int, exchange: str = 'bybit'):
        self.user_id = user_id
        self.exchange = exchange
        self.execution_config = ExecutionConfig()
        self.execution_history: List[ExecutionResult] = []
        self.active_orders: Dict[str, Dict] = {}
        self.market_conditions: Dict[str, MarketConditions] = {}
        self.performance_metrics = {
            'total_orders': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'average_execution_time': 0.0,
            'average_slippage': 0.0,
            'total_fees': 0.0,
            'success_rate': 0.0
        }
        
        # إعدادات التحسين
        self.adaptive_sizing = True
        self.dynamic_pricing = True
        self.smart_timing = True
        self.risk_aware_execution = True
        
        # خيوط التنفيذ
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.execution_lock = threading.Lock()
        
        logger.info(f"تم تهيئة منفذ الصفقات المتقدم للمستخدم {user_id} على {exchange}")
    
    async def execute_trade(self, trade_data: Dict[str, Any], 
                          market_data: Dict[str, Any] = None) -> ExecutionResult:
        """تنفيذ الصفقة المتقدم"""
        try:
            start_time = time.time()
            order_id = self._generate_order_id(trade_data)
            
            logger.info(f"بدء تنفيذ الصفقة {order_id} للمستخدم {self.user_id}")
            
            # التحقق من صحة البيانات
            validation_result = self._validate_trade_data(trade_data)
            if not validation_result['valid']:
                return ExecutionResult(
                    success=False,
                    order_id=order_id,
                    executed_price=None,
                    executed_quantity=None,
                    remaining_quantity=None,
                    fees=None,
                    slippage=None,
                    execution_time=time.time() - start_time,
                    status=ExecutionStatus.FAILED,
                    error_message=validation_result['error']
                )
            
            # تحليل ظروف السوق
            market_conditions = self._analyze_market_conditions(trade_data.get('symbol'), market_data)
            
            # تحسين إعدادات التنفيذ
            optimized_config = self._optimize_execution_config(trade_data, market_conditions)
            
            # تنفيذ الصفقة
            execution_result = await self._execute_order(trade_data, optimized_config, market_conditions)
            
            # تحديث الإحصائيات
            self._update_performance_metrics(execution_result)
            
            # حفظ النتيجة
            self.execution_history.append(execution_result)
            
            execution_time = time.time() - start_time
            execution_result.execution_time = execution_time
            
            logger.info(f"تم تنفيذ الصفقة {order_id} في {execution_time:.2f} ثانية")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة: {e}")
            import traceback
            traceback.print_exc()
            return ExecutionResult(
                success=False,
                order_id=order_id if 'order_id' in locals() else None,
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=time.time() - start_time if 'start_time' in locals() else 0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    def _generate_order_id(self, trade_data: Dict[str, Any]) -> str:
        """توليد معرف فريد للأمر"""
        try:
            timestamp = int(time.time() * 1000)
            symbol = trade_data.get('symbol', 'UNKNOWN')
            action = trade_data.get('action', 'UNKNOWN')
            
            return f"{self.exchange}_{self.user_id}_{symbol}_{action}_{timestamp}"
            
        except Exception as e:
            logger.error(f"خطأ في توليد معرف الأمر: {e}")
            return f"{self.exchange}_{self.user_id}_{int(time.time())}"
    
    def _validate_trade_data(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة بيانات الصفقة"""
        try:
            # فحص الحقول المطلوبة
            required_fields = ['symbol', 'action', 'quantity']
            for field in required_fields:
                if field not in trade_data or not trade_data[field]:
                    return {
                        'valid': False,
                        'error': f'الحقل المطلوب {field} مفقود أو فارغ'
                    }
            
            # فحص صحة الرمز
            symbol = trade_data.get('symbol', '')
            if len(symbol) < 6 or not symbol.isupper():
                return {
                    'valid': False,
                    'error': f'رمز العملة غير صحيح: {symbol}'
                }
            
            # فحص صحة الإجراء
            action = trade_data.get('action', '').lower()
            valid_actions = ['buy', 'sell', 'close', 'long', 'short']
            if action not in valid_actions:
                return {
                    'valid': False,
                    'error': f'إجراء غير صحيح: {action}'
                }
            
            # فحص صحة الكمية
            quantity = float(trade_data.get('quantity', 0))
            if quantity <= 0:
                return {
                    'valid': False,
                    'error': f'الكمية يجب أن تكون أكبر من صفر: {quantity}'
                }
            
            if quantity < self.execution_config.min_order_size:
                return {
                    'valid': False,
                    'error': f'الكمية {quantity} أقل من الحد الأدنى {self.execution_config.min_order_size}'
                }
            
            if quantity > self.execution_config.max_order_size:
                return {
                    'valid': False,
                    'error': f'الكمية {quantity} أكبر من الحد الأقصى {self.execution_config.max_order_size}'
                }
            
            # فحص صحة السعر (إذا كان محدداً)
            if 'price' in trade_data and trade_data['price']:
                price = float(trade_data['price'])
                if price <= 0:
                    return {
                        'valid': False,
                        'error': f'السعر يجب أن يكون أكبر من صفر: {price}'
                    }
            
            # فحص صحة الرافعة المالية (إذا كانت محددة)
            if 'leverage' in trade_data and trade_data['leverage']:
                leverage = float(trade_data['leverage'])
                if leverage < 1 or leverage > 100:
                    return {
                        'valid': False,
                        'error': f'الرافعة المالية يجب أن تكون بين 1 و 100: {leverage}'
                    }
            
            return {
                'valid': True,
                'message': 'بيانات الصفقة صحيحة'
            }
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صحة البيانات: {e}")
            return {
                'valid': False,
                'error': f'خطأ في التحقق من صحة البيانات: {e}'
            }
    
    def _analyze_market_conditions(self, symbol: str, market_data: Dict[str, Any] = None) -> MarketConditions:
        """تحليل ظروف السوق"""
        try:
            if not market_data or symbol not in market_data:
                # بيانات افتراضية
                return MarketConditions(
                    volatility=0.02,
                    volume=1000000.0,
                    spread=0.001,
                    liquidity=0.8,
                    trend='sideways',
                    momentum=0.0
                )
            
            symbol_data = market_data[symbol]
            
            # حساب التقلبات
            volatility = symbol_data.get('volatility', 0.02)
            
            # حساب الحجم
            volume = symbol_data.get('volume', 1000000.0)
            
            # حساب السبريد
            bid = symbol_data.get('bid', 0)
            ask = symbol_data.get('ask', 0)
            spread = (ask - bid) / bid if bid > 0 else 0.001
            
            # حساب السيولة
            liquidity = min(volume / 10000000.0, 1.0)  # تطبيع الحجم
            
            # تحديد الاتجاه
            price_change = symbol_data.get('price_change_24h', 0)
            if price_change > 0.02:
                trend = 'bullish'
            elif price_change < -0.02:
                trend = 'bearish'
            else:
                trend = 'sideways'
            
            # حساب الزخم
            momentum = symbol_data.get('momentum', 0.0)
            
            conditions = MarketConditions(
                volatility=volatility,
                volume=volume,
                spread=spread,
                liquidity=liquidity,
                trend=trend,
                momentum=momentum
            )
            
            # حفظ ظروف السوق
            self.market_conditions[symbol] = conditions
            
            return conditions
            
        except Exception as e:
            logger.error(f"خطأ في تحليل ظروف السوق: {e}")
            return MarketConditions(
                volatility=0.02,
                volume=1000000.0,
                spread=0.001,
                liquidity=0.8,
                trend='sideways',
                momentum=0.0
            )
    
    def _optimize_execution_config(self, trade_data: Dict[str, Any], 
                                 market_conditions: MarketConditions) -> ExecutionConfig:
        """تحسين إعدادات التنفيذ"""
        try:
            optimized_config = ExecutionConfig()
            
            # نسخ الإعدادات الأساسية
            optimized_config.max_retries = self.execution_config.max_retries
            optimized_config.retry_delay = self.execution_config.retry_delay
            optimized_config.timeout = self.execution_config.timeout
            optimized_config.min_order_size = self.execution_config.min_order_size
            optimized_config.max_order_size = self.execution_config.max_order_size
            
            # تحسين استراتيجية التنفيذ بناءً على ظروف السوق
            if market_conditions.volatility > 0.05:  # تقلبات عالية
                optimized_config.execution_strategy = ExecutionStrategy.IMMEDIATE
                optimized_config.slippage_tolerance = 0.02  # زيادة التسامح
            elif market_conditions.liquidity < 0.3:  # سيولة منخفضة
                optimized_config.execution_strategy = ExecutionStrategy.TWAP
                optimized_config.slippage_tolerance = 0.015
            elif market_conditions.spread > 0.005:  # سبريد عالي
                optimized_config.execution_strategy = ExecutionStrategy.LIMIT
                optimized_config.order_type = OrderType.LIMIT
            else:
                optimized_config.execution_strategy = ExecutionStrategy.IMMEDIATE
            
            # تحسين نوع الأمر
            if market_conditions.trend == 'bullish' and trade_data.get('action') == 'buy':
                optimized_config.order_type = OrderType.MARKET
            elif market_conditions.trend == 'bearish' and trade_data.get('action') == 'sell':
                optimized_config.order_type = OrderType.MARKET
            else:
                optimized_config.order_type = OrderType.LIMIT
            
            # تحسين التسامح مع الانزلاق
            if market_conditions.volatility > 0.03:
                optimized_config.slippage_tolerance = min(0.03, optimized_config.slippage_tolerance * 1.5)
            
            logger.info(f"تم تحسين إعدادات التنفيذ: {optimized_config.execution_strategy.value}")
            
            return optimized_config
            
        except Exception as e:
            logger.error(f"خطأ في تحسين إعدادات التنفيذ: {e}")
            return self.execution_config
    
    async def _execute_order(self, trade_data: Dict[str, Any], 
                           config: ExecutionConfig, 
                           market_conditions: MarketConditions) -> ExecutionResult:
        """تنفيذ الأمر"""
        try:
            order_id = self._generate_order_id(trade_data)
            symbol = trade_data.get('symbol')
            action = trade_data.get('action')
            quantity = float(trade_data.get('quantity'))
            price = trade_data.get('price')
            
            logger.info(f"تنفيذ الأمر {order_id}: {action} {quantity} {symbol}")
            
            # تنفيذ الأمر حسب الاستراتيجية
            if config.execution_strategy == ExecutionStrategy.IMMEDIATE:
                result = await self._execute_immediate_order(trade_data, config, market_conditions)
            elif config.execution_strategy == ExecutionStrategy.TWAP:
                result = await self._execute_twap_order(trade_data, config, market_conditions)
            elif config.execution_strategy == ExecutionStrategy.VWAP:
                result = await self._execute_vwap_order(trade_data, config, market_conditions)
            elif config.execution_strategy == ExecutionStrategy.ICEBERG:
                result = await self._execute_iceberg_order(trade_data, config, market_conditions)
            else:
                result = await self._execute_immediate_order(trade_data, config, market_conditions)
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر: {e}")
            return ExecutionResult(
                success=False,
                order_id=order_id if 'order_id' in locals() else None,
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _execute_immediate_order(self, trade_data: Dict[str, Any], 
                                     config: ExecutionConfig, 
                                     market_conditions: MarketConditions) -> ExecutionResult:
        """تنفيذ الأمر الفوري"""
        try:
            start_time = time.time()
            
            # محاكاة تنفيذ الأمر (يجب استبدالها بالتنفيذ الفعلي)
            await asyncio.sleep(0.1)  # محاكاة زمن التنفيذ
            
            # حساب النتائج
            symbol = trade_data.get('symbol')
            action = trade_data.get('action')
            quantity = float(trade_data.get('quantity'))
            
            # محاكاة السعر المنفذ
            if config.order_type == OrderType.MARKET:
                # سعر السوق مع انزلاق
                base_price = 50000.0  # سعر افتراضي
                slippage = market_conditions.volatility * 0.5
                if action.lower() == 'buy':
                    executed_price = base_price * (1 + slippage)
                else:
                    executed_price = base_price * (1 - slippage)
            else:
                # سعر محدد
                executed_price = float(trade_data.get('price', 50000.0))
            
            # محاكاة التنفيذ الكامل
            executed_quantity = quantity
            remaining_quantity = 0.0
            
            # حساب الرسوم
            fees = executed_quantity * executed_price * 0.001  # 0.1% رسوم
            
            # حساب الانزلاق
            slippage = abs(executed_price - 50000.0) / 50000.0 if executed_price != 50000.0 else 0.0
            
            execution_time = time.time() - start_time
            
            logger.info(f"تم تنفيذ الأمر الفوري: {executed_quantity} بسعر {executed_price}")
            
            return ExecutionResult(
                success=True,
                order_id=self._generate_order_id(trade_data),
                executed_price=executed_price,
                executed_quantity=executed_quantity,
                remaining_quantity=remaining_quantity,
                fees=fees,
                slippage=slippage,
                execution_time=execution_time,
                status=ExecutionStatus.EXECUTED,
                error_message=None,
                metadata={
                    'execution_strategy': config.execution_strategy.value,
                    'order_type': config.order_type.value,
                    'market_conditions': {
                        'volatility': market_conditions.volatility,
                        'liquidity': market_conditions.liquidity,
                        'trend': market_conditions.trend
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر الفوري: {e}")
            return ExecutionResult(
                success=False,
                order_id=self._generate_order_id(trade_data),
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _execute_twap_order(self, trade_data: Dict[str, Any], 
                                config: ExecutionConfig, 
                                market_conditions: MarketConditions) -> ExecutionResult:
        """تنفيذ الأمر TWAP (Time Weighted Average Price)"""
        try:
            start_time = time.time()
            
            symbol = trade_data.get('symbol')
            action = trade_data.get('action')
            total_quantity = float(trade_data.get('quantity'))
            
            # تقسيم الكمية على فترات زمنية
            num_periods = 5  # 5 فترات
            period_quantity = total_quantity / num_periods
            period_delay = 2.0  # ثانيتين بين كل فترة
            
            executed_quantity = 0.0
            total_fees = 0.0
            weighted_price = 0.0
            
            for i in range(num_periods):
                # تنفيذ جزء من الأمر
                await asyncio.sleep(period_delay)
                
                # محاكاة تنفيذ الجزء
                base_price = 50000.0 + (i * 10)  # تغيير طفيف في السعر
                slippage = market_conditions.volatility * 0.3
                
                if action.lower() == 'buy':
                    period_price = base_price * (1 + slippage)
                else:
                    period_price = base_price * (1 - bipage)
                
                period_executed = period_quantity
                period_fees = period_executed * period_price * 0.001
                
                executed_quantity += period_executed
                total_fees += period_fees
                weighted_price += period_price * period_executed
                
                logger.info(f"TWAP الجزء {i+1}/{num_periods}: {period_executed} بسعر {period_price}")
            
            # حساب السعر المرجح
            if executed_quantity > 0:
                weighted_price /= executed_quantity
            else:
                weighted_price = 0.0
            
            execution_time = time.time() - start_time
            
            logger.info(f"تم تنفيذ الأمر TWAP: {executed_quantity} بسعر متوسط {weighted_price}")
            
            return ExecutionResult(
                success=True,
                order_id=self._generate_order_id(trade_data),
                executed_price=weighted_price,
                executed_quantity=executed_quantity,
                remaining_quantity=total_quantity - executed_quantity,
                fees=total_fees,
                slippage=abs(weighted_price - 50000.0) / 50000.0,
                execution_time=execution_time,
                status=ExecutionStatus.EXECUTED,
                error_message=None,
                metadata={
                    'execution_strategy': config.execution_strategy.value,
                    'num_periods': num_periods,
                    'period_delay': period_delay
                }
            )
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر TWAP: {e}")
            return ExecutionResult(
                success=False,
                order_id=self._generate_order_id(trade_data),
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _execute_vwap_order(self, trade_data: Dict[str, Any], 
                                config: ExecutionConfig, 
                                market_conditions: MarketConditions) -> ExecutionResult:
        """تنفيذ الأمر VWAP (Volume Weighted Average Price)"""
        try:
            # تنفيذ مشابه لـ TWAP لكن مع مراعاة الحجم
            return await self._execute_twap_order(trade_data, config, market_conditions)
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر VWAP: {e}")
            return ExecutionResult(
                success=False,
                order_id=self._generate_order_id(trade_data),
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _execute_iceberg_order(self, trade_data: Dict[str, Any], 
                                   config: ExecutionConfig, 
                                   market_conditions: MarketConditions) -> ExecutionResult:
        """تنفيذ الأمر Iceberg (أمر مخفي)"""
        try:
            # تنفيذ مشابه لـ TWAP لكن مع إخفاء الحجم
            return await self._execute_twap_order(trade_data, config, market_conditions)
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر Iceberg: {e}")
            return ExecutionResult(
                success=False,
                order_id=self._generate_order_id(trade_data),
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    def _update_performance_metrics(self, execution_result: ExecutionResult):
        """تحديث مقاييس الأداء"""
        try:
            self.performance_metrics['total_orders'] += 1
            
            if execution_result.success:
                self.performance_metrics['successful_orders'] += 1
                if execution_result.execution_time:
                    # تحديث متوسط زمن التنفيذ
                    total_time = self.performance_metrics['average_execution_time'] * (self.performance_metrics['successful_orders'] - 1)
                    self.performance_metrics['average_execution_time'] = (total_time + execution_result.execution_time) / self.performance_metrics['successful_orders']
                
                if execution_result.slippage:
                    # تحديث متوسط الانزلاق
                    total_slippage = self.performance_metrics['average_slippage'] * (self.performance_metrics['successful_orders'] - 1)
                    self.performance_metrics['average_slippage'] = (total_slippage + execution_result.slippage) / self.performance_metrics['successful_orders']
                
                if execution_result.fees:
                    self.performance_metrics['total_fees'] += execution_result.fees
            else:
                self.performance_metrics['failed_orders'] += 1
            
            # تحديث معدل النجاح
            if self.performance_metrics['total_orders'] > 0:
                self.performance_metrics['success_rate'] = self.performance_metrics['successful_orders'] / self.performance_metrics['total_orders']
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مقاييس الأداء: {e}")
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التنفيذ"""
        try:
            return {
                'user_id': self.user_id,
                'exchange': self.exchange,
                'performance_metrics': self.performance_metrics,
                'total_executions': len(self.execution_history),
                'recent_executions': [
                    {
                        'order_id': result.order_id,
                        'success': result.success,
                        'executed_price': result.executed_price,
                        'executed_quantity': result.executed_quantity,
                        'execution_time': result.execution_time,
                        'status': result.status.value
                    }
                    for result in self.execution_history[-10:]  # آخر 10 تنفيذات
                ],
                'market_conditions': {
                    symbol: {
                        'volatility': conditions.volatility,
                        'volume': conditions.volume,
                        'spread': conditions.spread,
                        'liquidity': conditions.liquidity,
                        'trend': conditions.trend,
                        'last_updated': conditions.last_updated.isoformat()
                    }
                    for symbol, conditions in self.market_conditions.items()
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات التنفيذ: {e}")
            return {'error': str(e)}
    
    def update_execution_config(self, new_config: Dict[str, Any]) -> bool:
        """تحديث إعدادات التنفيذ"""
        try:
            for key, value in new_config.items():
                if hasattr(self.execution_config, key):
                    setattr(self.execution_config, key, value)
            
            logger.info(f"تم تحديث إعدادات التنفيذ للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات التنفيذ: {e}")
            return False
    
    def cancel_order(self, order_id: str) -> bool:
        """إلغاء الأمر"""
        try:
            if order_id in self.active_orders:
                del self.active_orders[order_id]
                logger.info(f"تم إلغاء الأمر {order_id}")
                return True
            else:
                logger.warning(f"الأمر {order_id} غير موجود")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في إلغاء الأمر: {e}")
            return False
    
    def get_active_orders(self) -> Dict[str, Dict]:
        """الحصول على الأوامر النشطة"""
        return self.active_orders.copy()
    
    def cleanup(self):
        """تنظيف الموارد"""
        try:
            self.executor.shutdown(wait=True)
            logger.info(f"تم تنظيف موارد منفذ الصفقات للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد: {e}")


# مدير التنفيذ العام
class GlobalTradeExecutor:
    """مدير التنفيذ العام لجميع المستخدمين"""
    
    def __init__(self):
        self.user_executors: Dict[int, AdvancedTradeExecutor] = {}
        self.global_statistics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'global_success_rate': 0.0
        }
    
    def get_executor(self, user_id: int, exchange: str = 'bybit') -> AdvancedTradeExecutor:
        """الحصول على منفذ الصفقات للمستخدم"""
        key = f"{user_id}_{exchange}"
        if key not in self.user_executors:
            self.user_executors[key] = AdvancedTradeExecutor(user_id, exchange)
        return self.user_executors[key]
    
    async def execute_trade_for_user(self, user_id: int, trade_data: Dict[str, Any], 
                                   market_data: Dict[str, Any] = None, 
                                   exchange: str = 'bybit') -> ExecutionResult:
        """تنفيذ الصفقة للمستخدم"""
        try:
            executor = self.get_executor(user_id, exchange)
            result = await executor.execute_trade(trade_data, market_data)
            
            # تحديث الإحصائيات العامة
            if result.success:
                self.global_statistics['successful_executions'] += 1
            else:
                self.global_statistics['failed_executions'] += 1
            
            self.global_statistics['total_executions'] += 1
            
            # تحديث معدل النجاح
            if self.global_statistics['total_executions'] > 0:
                self.global_statistics['global_success_rate'] = (
                    self.global_statistics['successful_executions'] / 
                    self.global_statistics['total_executions']
                )
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة للمستخدم {user_id}: {e}")
            return ExecutionResult(
                success=False,
                order_id=None,
                executed_price=None,
                executed_quantity=None,
                remaining_quantity=None,
                fees=None,
                slippage=None,
                execution_time=0.0,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        try:
            user_stats = {}
            for key, executor in self.user_executors.items():
                user_stats[key] = executor.get_execution_statistics()
            
            return {
                'global_statistics': self.global_statistics,
                'user_statistics': user_stats,
                'total_users': len(self.user_executors)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات العامة: {e}")
            return {'error': str(e)}
    
    def cleanup_all(self):
        """تنظيف جميع الموارد"""
        try:
            for executor in self.user_executors.values():
                executor.cleanup()
            logger.info("تم تنظيف جميع موارد التنفيذ")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد العامة: {e}")


# مثيل عام لمدير التنفيذ
global_trade_executor = GlobalTradeExecutor()
