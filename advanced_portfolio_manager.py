#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المحفظة المتقدم - Advanced Portfolio Manager
يدعم إدارة المحافظ المتقدمة مع إعادة التوازن التلقائي وتحسين الأداء
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
import numpy as np
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class PortfolioStrategy(Enum):
    """استراتيجية المحفظة"""
    EQUAL_WEIGHT = "equal_weight"
    MARKET_CAP_WEIGHT = "market_cap_weight"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    MOMENTUM_BASED = "momentum_based"
    MEAN_REVERSION = "mean_reversion"
    BLACK_LITTERMAN = "black_litterman"
    RISK_PARITY = "risk_parity"

class RebalancingFrequency(Enum):
    """تكرار إعادة التوازن"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_SIGNAL = "on_signal"

class RiskModel(Enum):
    """نموذج المخاطر"""
    HISTORICAL = "historical"
    GARCH = "garch"
    EWMA = "ewma"
    MONTE_CARLO = "monte_carlo"

@dataclass
class Asset:
    """أصل مالي"""
    symbol: str
    name: str
    current_price: float
    quantity: float
    weight: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    volatility: float
    beta: float
    correlation: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class PortfolioMetrics:
    """مقاييس المحفظة"""
    total_value: float
    total_cost: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional Value at Risk 95%
    diversification_ratio: float
    concentration_ratio: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class RebalancingSignal:
    """إشارة إعادة التوازن"""
    symbol: str
    current_weight: float
    target_weight: float
    weight_difference: float
    action: str  # 'buy', 'sell', 'hold'
    quantity: float
    priority: int
    reason: str

class AdvancedPortfolioManager:
    """مدير المحفظة المتقدم"""
    
    def __init__(self, user_id: int, initial_capital: float = 10000.0):
        self.user_id = user_id
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # المحفظة
        self.assets: Dict[str, Asset] = {}
        self.cash_balance = initial_capital
        self.portfolio_strategy = PortfolioStrategy.EQUAL_WEIGHT
        self.rebalancing_frequency = RebalancingFrequency.WEEKLY
        self.risk_model = RiskModel.HISTORICAL
        
        # إعدادات إعادة التوازن
        self.rebalancing_threshold = 0.05  # 5%
        self.min_weight = 0.01  # 1%
        self.max_weight = 0.4  # 40%
        self.rebalancing_enabled = True
        
        # مقاييس الأداء
        self.portfolio_metrics = PortfolioMetrics(
            total_value=initial_capital,
            total_cost=initial_capital,
            unrealized_pnl=0.0,
            unrealized_pnl_percent=0.0,
            daily_pnl=0.0,
            weekly_pnl=0.0,
            monthly_pnl=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            var_95=0.0,
            cvar_95=0.0,
            diversification_ratio=0.0,
            concentration_ratio=0.0
        )
        
        # تاريخ المحفظة
        self.portfolio_history: List[PortfolioMetrics] = []
        self.rebalancing_history: List[RebalancingSignal] = []
        
        # إعدادات التحسين
        self.optimization_enabled = True
        self.risk_free_rate = 0.02  # 2%
        self.risk_aversion = 1.0
        self.transaction_costs = 0.001  # 0.1%
        
        logger.info(f"تم تهيئة مدير المحفظة المتقدم للمستخدم {user_id}")
    
    def add_asset(self, symbol: str, name: str, quantity: float, 
                  current_price: float, cost_basis: float = None) -> bool:
        """إضافة أصل للمحفظة"""
        try:
            if symbol in self.assets:
                logger.warning(f"الأصل {symbol} موجود بالفعل في المحفظة")
                return False
            
            if cost_basis is None:
                cost_basis = current_price
            
            market_value = quantity * current_price
            unrealized_pnl = (current_price - cost_basis) * quantity
            unrealized_pnl_percent = (current_price - cost_basis) / cost_basis * 100
            
            asset = Asset(
                symbol=symbol,
                name=name,
                current_price=current_price,
                quantity=quantity,
                weight=0.0,  # سيتم حسابها لاحقاً
                market_value=market_value,
                cost_basis=cost_basis,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_percent=unrealized_pnl_percent,
                volatility=0.02,  # افتراضي
                beta=1.0  # افتراضي
            )
            
            self.assets[symbol] = asset
            
            # تحديث رصيد النقد
            self.cash_balance -= market_value
            
            # إعادة حساب الأوزان والمقاييس
            self._update_portfolio_metrics()
            
            logger.info(f"تم إضافة الأصل {symbol} للمحفظة: {quantity} بسعر {current_price}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الأصل {symbol}: {e}")
            return False
    
    def remove_asset(self, symbol: str) -> bool:
        """إزالة أصل من المحفظة"""
        try:
            if symbol not in self.assets:
                logger.warning(f"الأصل {symbol} غير موجود في المحفظة")
                return False
            
            asset = self.assets[symbol]
            
            # إضافة القيمة السوقية إلى رصيد النقد
            self.cash_balance += asset.market_value
            
            # إزالة الأصل
            del self.assets[symbol]
            
            # إعادة حساب الأوزان والمقاييس
            self._update_portfolio_metrics()
            
            logger.info(f"تم إزالة الأصل {symbol} من المحفظة")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إزالة الأصل {symbol}: {e}")
            return False
    
    def update_asset_price(self, symbol: str, new_price: float) -> bool:
        """تحديث سعر الأصل"""
        try:
            if symbol not in self.assets:
                logger.warning(f"الأصل {symbol} غير موجود في المحفظة")
                return False
            
            asset = self.assets[symbol]
            old_price = asset.current_price
            
            # تحديث السعر والقيمة السوقية
            asset.current_price = new_price
            asset.market_value = asset.quantity * new_price
            asset.unrealized_pnl = (new_price - asset.cost_basis) * asset.quantity
            asset.unrealized_pnl_percent = (new_price - asset.cost_basis) / asset.cost_basis * 100
            asset.last_updated = datetime.now()
            
            # إعادة حساب الأوزان والمقاييس
            self._update_portfolio_metrics()
            
            logger.info(f"تم تحديث سعر {symbol} من {old_price} إلى {new_price}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث سعر الأصل {symbol}: {e}")
            return False
    
    def _update_portfolio_metrics(self):
        """تحديث مقاييس المحفظة"""
        try:
            if not self.assets:
                return
            
            # حساب القيمة الإجمالية
            total_market_value = sum(asset.market_value for asset in self.assets.values())
            total_cost = sum(asset.quantity * asset.cost_basis for asset in self.assets.values())
            
            # حساب الربح/الخسارة غير المحققة
            unrealized_pnl = total_market_value - total_cost
            unrealized_pnl_percent = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0.0
            
            # تحديث الأوزان
            for asset in self.assets.values():
                asset.weight = asset.market_value / total_market_value if total_market_value > 0 else 0.0
            
            # حساب التقلبات
            volatility = self._calculate_portfolio_volatility()
            
            # حساب نسبة شارب
            sharpe_ratio = self._calculate_sharpe_ratio()
            
            # حساب الحد الأقصى للانخفاض
            max_drawdown = self._calculate_max_drawdown()
            
            # حساب VaR و CVaR
            var_95, cvar_95 = self._calculate_var_cvar()
            
            # حساب نسبة التنويع
            diversification_ratio = self._calculate_diversification_ratio()
            
            # حساب نسبة التركيز
            concentration_ratio = self._calculate_concentration_ratio()
            
            # تحديث المقاييس
            self.portfolio_metrics = PortfolioMetrics(
                total_value=total_market_value + self.cash_balance,
                total_cost=total_cost + (self.initial_capital - self.cash_balance),
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_percent=unrealized_pnl_percent,
                daily_pnl=0.0,  # سيتم تحديثه لاحقاً
                weekly_pnl=0.0,
                monthly_pnl=0.0,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                var_95=var_95,
                cvar_95=cvar_95,
                diversification_ratio=diversification_ratio,
                concentration_ratio=concentration_ratio,
                last_updated=datetime.now()
            )
            
            # حفظ التاريخ
            self.portfolio_history.append(self.portfolio_metrics)
            
            # الاحتفاظ بآخر 1000 سجل فقط
            if len(self.portfolio_history) > 1000:
                self.portfolio_history = self.portfolio_history[-1000:]
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مقاييس المحفظة: {e}")
    
    def _calculate_portfolio_volatility(self) -> float:
        """حساب تقلبات المحفظة"""
        try:
            if len(self.assets) < 2:
                return 0.0
            
            # حساب مصفوفة التباين-التغاير
            symbols = list(self.assets.keys())
            n = len(symbols)
            cov_matrix = np.zeros((n, n))
            
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    if i == j:
                        cov_matrix[i, j] = self.assets[symbol1].volatility ** 2
                    else:
                        correlation = self.assets[symbol1].correlation.get(symbol2, 0.0)
                        cov_matrix[i, j] = (
                            self.assets[symbol1].volatility * 
                            self.assets[symbol2].volatility * 
                            correlation
                        )
            
            # حساب أوزان المحفظة
            weights = np.array([self.assets[symbol].weight for symbol in symbols])
            
            # حساب التقلبات
            portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            return portfolio_volatility
            
        except Exception as e:
            logger.error(f"خطأ في حساب تقلبات المحفظة: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self) -> float:
        """حساب نسبة شارب"""
        try:
            if self.portfolio_metrics.volatility == 0:
                return 0.0
            
            # حساب العائد المتوقع
            expected_return = sum(
                asset.weight * asset.unrealized_pnl_percent / 100 
                for asset in self.assets.values()
            )
            
            # حساب نسبة شارب
            sharpe_ratio = (expected_return - self.risk_free_rate) / self.portfolio_metrics.volatility
            
            return sharpe_ratio
            
        except Exception as e:
            logger.error(f"خطأ في حساب نسبة شارب: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self) -> float:
        """حساب الحد الأقصى للانخفاض"""
        try:
            if len(self.portfolio_history) < 2:
                return 0.0
            
            values = [metrics.total_value for metrics in self.portfolio_history]
            peak = values[0]
            max_dd = 0.0
            
            for value in values[1:]:
                if value > peak:
                    peak = value
                else:
                    drawdown = (peak - value) / peak
                    max_dd = max(max_dd, drawdown)
            
            return max_dd
            
        except Exception as e:
            logger.error(f"خطأ في حساب الحد الأقصى للانخفاض: {e}")
            return 0.0
    
    def _calculate_var_cvar(self, confidence_level: float = 0.95) -> Tuple[float, float]:
        """حساب VaR و CVaR"""
        try:
            if len(self.portfolio_history) < 30:
                return 0.0, 0.0
            
            # حساب العوائد اليومية
            returns = []
            for i in range(1, len(self.portfolio_history)):
                prev_value = self.portfolio_history[i-1].total_value
                curr_value = self.portfolio_history[i].total_value
                if prev_value > 0:
                    returns.append((curr_value - prev_value) / prev_value)
            
            if not returns:
                return 0.0, 0.0
            
            # حساب VaR
            returns_sorted = sorted(returns)
            var_index = int((1 - confidence_level) * len(returns_sorted))
            var_95 = abs(returns_sorted[var_index])
            
            # حساب CVaR
            tail_returns = returns_sorted[:var_index]
            cvar_95 = abs(np.mean(tail_returns)) if tail_returns else 0.0
            
            return var_95, cvar_95
            
        except Exception as e:
            logger.error(f"خطأ في حساب VaR و CVaR: {e}")
            return 0.0, 0.0
    
    def _calculate_diversification_ratio(self) -> float:
        """حساب نسبة التنويع"""
        try:
            if len(self.assets) < 2:
                return 0.0
            
            # حساب متوسط التقلبات المرجحة
            weighted_avg_volatility = sum(
                asset.weight * asset.volatility 
                for asset in self.assets.values()
            )
            
            # حساب تقلبات المحفظة
            portfolio_volatility = self.portfolio_metrics.volatility
            
            if portfolio_volatility == 0:
                return 0.0
            
            # حساب نسبة التنويع
            diversification_ratio = weighted_avg_volatility / portfolio_volatility
            
            return diversification_ratio
            
        except Exception as e:
            logger.error(f"خطأ في حساب نسبة التنويع: {e}")
            return 0.0
    
    def _calculate_concentration_ratio(self) -> float:
        """حساب نسبة التركيز"""
        try:
            if not self.assets:
                return 0.0
            
            # حساب نسبة التركيز (أكبر 5 أصول)
            weights = [asset.weight for asset in self.assets.values()]
            weights_sorted = sorted(weights, reverse=True)
            
            # أخذ أكبر 5 أو جميع الأصول إذا كان العدد أقل من 5
            top_weights = weights_sorted[:min(5, len(weights_sorted))]
            concentration_ratio = sum(top_weights)
            
            return concentration_ratio
            
        except Exception as e:
            logger.error(f"خطأ في حساب نسبة التركيز: {e}")
            return 0.0
    
    def optimize_portfolio(self, target_return: float = None) -> Dict[str, float]:
        """تحسين المحفظة"""
        try:
            if len(self.assets) < 2:
                return {}
            
            symbols = list(self.assets.keys())
            n = len(symbols)
            
            # حساب مصفوفة التباين-التغاير
            cov_matrix = np.zeros((n, n))
            expected_returns = np.zeros(n)
            
            for i, symbol1 in enumerate(symbols):
                expected_returns[i] = self.assets[symbol1].unrealized_pnl_percent / 100
                for j, symbol2 in enumerate(symbols):
                    if i == j:
                        cov_matrix[i, j] = self.assets[symbol1].volatility ** 2
                    else:
                        correlation = self.assets[symbol1].correlation.get(symbol2, 0.0)
                        cov_matrix[i, j] = (
                            self.assets[symbol1].volatility * 
                            self.assets[symbol2].volatility * 
                            correlation
                        )
            
            # دالة الهدف (تقليل التباين)
            def objective(weights):
                return np.dot(weights, np.dot(cov_matrix, weights))
            
            # قيود
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # مجموع الأوزان = 1
            ]
            
            if target_return is not None:
                constraints.append({
                    'type': 'eq', 
                    'fun': lambda w: np.dot(w, expected_returns) - target_return
                })
            
            # حدود
            bounds = [(self.min_weight, self.max_weight) for _ in range(n)]
            
            # نقطة البداية (أوزان متساوية)
            x0 = np.ones(n) / n
            
            # التحسين
            result = minimize(objective, x0, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                optimized_weights = {}
                for i, symbol in enumerate(symbols):
                    optimized_weights[symbol] = result.x[i]
                
                logger.info(f"تم تحسين المحفظة بنجاح")
                return optimized_weights
            else:
                logger.warning(f"فشل في تحسين المحفظة: {result.message}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في تحسين المحفظة: {e}")
            return {}
    
    def generate_rebalancing_signals(self) -> List[RebalancingSignal]:
        """توليد إشارات إعادة التوازن"""
        try:
            if not self.rebalancing_enabled:
                return []
            
            signals = []
            
            # حساب الأوزان المستهدفة
            target_weights = self._calculate_target_weights()
            
            # فحص الحاجة لإعادة التوازن
            for symbol, asset in self.assets.items():
                current_weight = asset.weight
                target_weight = target_weights.get(symbol, 0.0)
                weight_difference = abs(current_weight - target_weight)
                
                # إذا كان الفرق أكبر من العتبة
                if weight_difference > self.rebalancing_threshold:
                    # تحديد الإجراء
                    if current_weight > target_weight:
                        action = 'sell'
                        quantity = asset.quantity * (current_weight - target_weight) / current_weight
                    else:
                        action = 'buy'
                        quantity = asset.quantity * (target_weight - current_weight) / current_weight
                    
                    # تحديد الأولوية
                    priority = int(weight_difference * 100)  # الأولوية حسب حجم الفرق
                    
                    # إنشاء الإشارة
                    signal = RebalancingSignal(
                        symbol=symbol,
                        current_weight=current_weight,
                        target_weight=target_weight,
                        weight_difference=weight_difference,
                        action=action,
                        quantity=quantity,
                        priority=priority,
                        reason=f"إعادة توازن - الفرق: {weight_difference:.2%}"
                    )
                    
                    signals.append(signal)
            
            # ترتيب الإشارات حسب الأولوية
            signals.sort(key=lambda x: x.priority, reverse=True)
            
            # حفظ التاريخ
            self.rebalancing_history.extend(signals)
            
            logger.info(f"تم توليد {len(signals)} إشارة إعادة توازن")
            return signals
            
        except Exception as e:
            logger.error(f"خطأ في توليد إشارات إعادة التوازن: {e}")
            return []
    
    def _calculate_target_weights(self) -> Dict[str, float]:
        """حساب الأوزان المستهدفة"""
        try:
            if self.portfolio_strategy == PortfolioStrategy.EQUAL_WEIGHT:
                # أوزان متساوية
                n = len(self.assets)
                return {symbol: 1.0 / n for symbol in self.assets.keys()}
            
            elif self.portfolio_strategy == PortfolioStrategy.VOLATILITY_ADJUSTED:
                # أوزان معكوسة للتقلبات
                inv_volatilities = {}
                total_inv_vol = 0.0
                
                for symbol, asset in self.assets.items():
                    inv_vol = 1.0 / asset.volatility if asset.volatility > 0 else 0.0
                    inv_volatilities[symbol] = inv_vol
                    total_inv_vol += inv_vol
                
                return {
                    symbol: inv_vol / total_inv_vol 
                    for symbol, inv_vol in inv_volatilities.items()
                }
            
            elif self.portfolio_strategy == PortfolioStrategy.MOMENTUM_BASED:
                # أوزان بناءً على الزخم
                momentums = {}
                total_momentum = 0.0
                
                for symbol, asset in self.assets.items():
                    momentum = max(0.0, asset.unrealized_pnl_percent / 100)
                    momentums[symbol] = momentum
                    total_momentum += momentum
                
                if total_momentum == 0:
                    # إذا لم يكن هناك زخم، استخدام أوزان متساوية
                    n = len(self.assets)
                    return {symbol: 1.0 / n for symbol in self.assets.keys()}
                
                return {
                    symbol: momentum / total_momentum 
                    for symbol, momentum in momentums.items()
                }
            
            else:
                # افتراضي: أوزان متساوية
                n = len(self.assets)
                return {symbol: 1.0 / n for symbol in self.assets.keys()}
                
        except Exception as e:
            logger.error(f"خطأ في حساب الأوزان المستهدفة: {e}")
            n = len(self.assets)
            return {symbol: 1.0 / n for symbol in self.assets.keys()}
    
    def rebalance_portfolio(self, signals: List[RebalancingSignal] = None) -> Dict[str, Any]:
        """إعادة توازن المحفظة"""
        try:
            if signals is None:
                signals = self.generate_rebalancing_signals()
            
            if not signals:
                return {
                    'success': True,
                    'message': 'لا توجد حاجة لإعادة التوازن',
                    'trades_executed': 0,
                    'total_cost': 0.0
                }
            
            trades_executed = 0
            total_cost = 0.0
            executed_trades = []
            
            for signal in signals:
                try:
                    # تنفيذ التداول
                    if signal.action == 'sell':
                        # بيع جزء من الأصل
                        sell_quantity = signal.quantity
                        sell_price = self.assets[signal.symbol].current_price
                        sell_value = sell_quantity * sell_price
                        
                        # تحديث الكمية
                        self.assets[signal.symbol].quantity -= sell_quantity
                        
                        # إضافة إلى رصيد النقد
                        self.cash_balance += sell_value
                        
                        # حساب تكلفة المعاملة
                        transaction_cost = sell_value * self.transaction_costs
                        total_cost += transaction_cost
                        
                        executed_trades.append({
                            'symbol': signal.symbol,
                            'action': 'sell',
                            'quantity': sell_quantity,
                            'price': sell_price,
                            'value': sell_value,
                            'cost': transaction_cost
                        })
                        
                    elif signal.action == 'buy':
                        # شراء جزء من الأصل
                        buy_quantity = signal.quantity
                        buy_price = self.assets[signal.symbol].current_price
                        buy_value = buy_quantity * buy_price
                        
                        # التحقق من توفر النقد
                        if self.cash_balance >= buy_value:
                            # تحديث الكمية
                            self.assets[signal.symbol].quantity += buy_quantity
                            
                            # خصم من رصيد النقد
                            self.cash_balance -= buy_value
                            
                            # حساب تكلفة المعاملة
                            transaction_cost = buy_value * self.transaction_costs
                            total_cost += transaction_cost
                            
                            executed_trades.append({
                                'symbol': signal.symbol,
                                'action': 'buy',
                                'quantity': buy_quantity,
                                'price': buy_price,
                                'value': buy_value,
                                'cost': transaction_cost
                            })
                        
                        else:
                            logger.warning(f"رصيد النقد غير كافي لشراء {signal.symbol}")
                            continue
                    
                    trades_executed += 1
                    
                except Exception as e:
                    logger.error(f"خطأ في تنفيذ إشارة إعادة التوازن: {e}")
                    continue
            
            # إعادة حساب المقاييس
            self._update_portfolio_metrics()
            
            logger.info(f"تم تنفيذ {trades_executed} عملية إعادة توازن")
            
            return {
                'success': True,
                'message': f'تم تنفيذ {trades_executed} عملية إعادة توازن',
                'trades_executed': trades_executed,
                'total_cost': total_cost,
                'executed_trades': executed_trades
            }
            
        except Exception as e:
            logger.error(f"خطأ في إعادة توازن المحفظة: {e}")
            return {
                'success': False,
                'message': f'خطأ في إعادة توازن المحفظة: {e}',
                'trades_executed': 0,
                'total_cost': 0.0
            }
    
    def get_portfolio_report(self) -> Dict[str, Any]:
        """الحصول على تقرير المحفظة"""
        try:
            return {
                'user_id': self.user_id,
                'portfolio_metrics': {
                    'total_value': self.portfolio_metrics.total_value,
                    'total_cost': self.portfolio_metrics.total_cost,
                    'unrealized_pnl': self.portfolio_metrics.unrealized_pnl,
                    'unrealized_pnl_percent': self.portfolio_metrics.unrealized_pnl_percent,
                    'volatility': self.portfolio_metrics.volatility,
                    'sharpe_ratio': self.portfolio_metrics.sharpe_ratio,
                    'max_drawdown': self.portfolio_metrics.max_drawdown,
                    'var_95': self.portfolio_metrics.var_95,
                    'cvar_95': self.portfolio_metrics.cvar_95,
                    'diversification_ratio': self.portfolio_metrics.diversification_ratio,
                    'concentration_ratio': self.portfolio_metrics.concentration_ratio,
                    'last_updated': self.portfolio_metrics.last_updated.isoformat()
                },
                'assets': {
                    symbol: {
                        'name': asset.name,
                        'current_price': asset.current_price,
                        'quantity': asset.quantity,
                        'weight': asset.weight,
                        'market_value': asset.market_value,
                        'cost_basis': asset.cost_basis,
                        'unrealized_pnl': asset.unrealized_pnl,
                        'unrealized_pnl_percent': asset.unrealized_pnl_percent,
                        'volatility': asset.volatility,
                        'beta': asset.beta,
                        'last_updated': asset.last_updated.isoformat()
                    }
                    for symbol, asset in self.assets.items()
                },
                'cash_balance': self.cash_balance,
                'portfolio_strategy': self.portfolio_strategy.value,
                'rebalancing_frequency': self.rebalancing_frequency.value,
                'risk_model': self.risk_model.value,
                'rebalancing_enabled': self.rebalancing_enabled,
                'total_assets': len(self.assets),
                'recent_rebalancing_signals': [
                    {
                        'symbol': signal.symbol,
                        'current_weight': signal.current_weight,
                        'target_weight': signal.target_weight,
                        'weight_difference': signal.weight_difference,
                        'action': signal.action,
                        'quantity': signal.quantity,
                        'priority': signal.priority,
                        'reason': signal.reason
                    }
                    for signal in self.rebalancing_history[-10:]  # آخر 10 إشارات
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير المحفظة: {e}")
            return {'error': str(e)}
    
    def update_strategy(self, new_strategy: PortfolioStrategy) -> bool:
        """تحديث استراتيجية المحفظة"""
        try:
            self.portfolio_strategy = new_strategy
            logger.info(f"تم تحديث استراتيجية المحفظة إلى {new_strategy.value}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث استراتيجية المحفظة: {e}")
            return False
    
    def update_rebalancing_settings(self, settings: Dict[str, Any]) -> bool:
        """تحديث إعدادات إعادة التوازن"""
        try:
            for key, value in settings.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            logger.info(f"تم تحديث إعدادات إعادة التوازن للمستخدم {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات إعادة التوازن: {e}")
            return False


# مدير المحافظ العام
class GlobalPortfolioManager:
    """مدير المحافظ العام لجميع المستخدمين"""
    
    def __init__(self):
        self.user_portfolios: Dict[int, AdvancedPortfolioManager] = {}
        self.global_statistics = {
            'total_users': 0,
            'total_assets_under_management': 0.0,
            'average_portfolio_value': 0.0,
            'average_sharpe_ratio': 0.0,
            'total_rebalancing_operations': 0
        }
    
    def get_portfolio_manager(self, user_id: int, initial_capital: float = 10000.0) -> AdvancedPortfolioManager:
        """الحصول على مدير المحفظة للمستخدم"""
        if user_id not in self.user_portfolios:
            self.user_portfolios[user_id] = AdvancedPortfolioManager(user_id, initial_capital)
        return self.user_portfolios[user_id]
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        try:
            total_value = 0.0
            total_sharpe = 0.0
            total_rebalancing = 0
            
            user_stats = {}
            for user_id, portfolio in self.user_portfolios.items():
                report = portfolio.get_portfolio_report()
                user_stats[user_id] = report
                
                total_value += portfolio.portfolio_metrics.total_value
                total_sharpe += portfolio.portfolio_metrics.sharpe_ratio
                total_rebalancing += len(portfolio.rebalancing_history)
            
            # تحديث الإحصائيات العامة
            self.global_statistics['total_users'] = len(self.user_portfolios)
            self.global_statistics['total_assets_under_management'] = total_value
            self.global_statistics['average_portfolio_value'] = total_value / len(self.user_portfolios) if self.user_portfolios else 0.0
            self.global_statistics['average_sharpe_ratio'] = total_sharpe / len(self.user_portfolios) if self.user_portfolios else 0.0
            self.global_statistics['total_rebalancing_operations'] = total_rebalancing
            
            return {
                'global_statistics': self.global_statistics,
                'user_statistics': user_stats
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات العامة: {e}")
            return {'error': str(e)}


# مثيل عام لمدير المحافظ
global_portfolio_manager = GlobalPortfolioManager()
