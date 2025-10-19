#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محسن البوت المتقدم - Advanced Trading Bot Optimizer
يدعم تحسين جميع مكونات البوت وتحسين الأداء الشامل
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

# استيراد المكونات المتقدمة
from advanced_risk_manager import global_risk_manager, AdvancedRiskManager
from advanced_signal_processor import global_signal_manager, AdvancedSignalProcessor
from advanced_trade_executor import global_trade_executor, AdvancedTradeExecutor
from advanced_portfolio_manager import global_portfolio_manager, AdvancedPortfolioManager

logger = logging.getLogger(__name__)

class OptimizationTarget(Enum):
    """هدف التحسين"""
    PERFORMANCE = "performance"
    RISK_ADJUSTED_RETURNS = "risk_adjusted_returns"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"

class OptimizationMethod(Enum):
    """طريقة التحسين"""
    GRID_SEARCH = "grid_search"
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    RANDOM_SEARCH = "random_search"
    GRADIENT_DESCENT = "gradient_descent"

@dataclass
class OptimizationResult:
    """نتيجة التحسين"""
    target: OptimizationTarget
    method: OptimizationMethod
    best_parameters: Dict[str, Any]
    best_score: float
    improvement: float
    optimization_time: float
    iterations: int
    convergence: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """مقاييس الأداء"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    volatility: float
    var_95: float
    cvar_95: float
    last_updated: datetime = field(default_factory=datetime.now)

class TradingBotOptimizer:
    """محسن البوت المتقدم"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.optimization_history: List[OptimizationResult] = []
        self.performance_metrics = PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            total_return=0.0,
            volatility=0.0,
            var_95=0.0,
            cvar_95=0.0
        )
        
        # إعدادات التحسين
        self.optimization_enabled = True
        self.auto_optimization = False
        self.optimization_frequency = timedelta(days=7)  # أسبوعياً
        self.last_optimization = None
        
        # حدود التحسين
        self.max_optimization_time = 3600  # ساعة واحدة
        self.max_iterations = 1000
        self.min_improvement_threshold = 0.01  # 1%
        
        # خيوط التحسين
        self.optimization_executor = ThreadPoolExecutor(max_workers=3)
        self.optimization_lock = threading.Lock()
        
        logger.info(f"تم تهيئة محسن البوت للمستخدم {user_id}")
    
    async def optimize_bot(self, target: OptimizationTarget, 
                          method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
                          parameters: Dict[str, Any] = None) -> OptimizationResult:
        """تحسين البوت"""
        try:
            start_time = time.time()
            
            logger.info(f"بدء تحسين البوت للمستخدم {self.user_id} - الهدف: {target.value}")
            
            # تحديد المعاملات المراد تحسينها
            if parameters is None:
                parameters = self._get_default_parameters(target)
            
            # تنفيذ التحسين حسب الطريقة
            if method == OptimizationMethod.GRID_SEARCH:
                result = await self._grid_search_optimization(target, parameters)
            elif method == OptimizationMethod.GENETIC_ALGORITHM:
                result = await self._genetic_algorithm_optimization(target, parameters)
            elif method == OptimizationMethod.BAYESIAN_OPTIMIZATION:
                result = await self._bayesian_optimization(target, parameters)
            elif method == OptimizationMethod.RANDOM_SEARCH:
                result = await self._random_search_optimization(target, parameters)
            else:
                result = await self._grid_search_optimization(target, parameters)
            
            # حساب وقت التحسين
            optimization_time = time.time() - start_time
            result.optimization_time = optimization_time
            
            # حفظ النتيجة
            self.optimization_history.append(result)
            self.last_optimization = datetime.now()
            
            # تطبيق أفضل المعاملات
            if result.improvement > self.min_improvement_threshold:
                await self._apply_optimized_parameters(result.best_parameters)
                logger.info(f"تم تطبيق المعاملات المحسنة - تحسن: {result.improvement:.2%}")
            else:
                logger.info(f"التحسن غير كافي - تم تجاهل النتيجة")
            
            logger.info(f"تم الانتهاء من تحسين البوت في {optimization_time:.2f} ثانية")
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تحسين البوت: {e}")
            import traceback
            traceback.print_exc()
            return OptimizationResult(
                target=target,
                method=method,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def _get_default_parameters(self, target: OptimizationTarget) -> Dict[str, Any]:
        """الحصول على المعاملات الافتراضية للتحسين"""
        try:
            if target == OptimizationTarget.PERFORMANCE:
                return {
                    'risk_limits': {
                        'max_daily_loss': [100, 500, 1000, 2000],
                        'max_weekly_loss': [500, 2000, 5000, 10000],
                        'max_position_size': [100, 500, 1000, 2000],
                        'max_leverage': [5, 10, 20, 50]
                    },
                    'signal_filters': {
                        'min_confidence': [0.5, 0.6, 0.7, 0.8, 0.9],
                        'min_quality_score': [0.4, 0.5, 0.6, 0.7, 0.8],
                        'max_age_seconds': [60, 300, 600, 900, 1800]
                    },
                    'execution_config': {
                        'max_retries': [1, 2, 3, 5],
                        'retry_delay': [0.5, 1.0, 2.0, 5.0],
                        'timeout': [10, 30, 60, 120],
                        'slippage_tolerance': [0.005, 0.01, 0.02, 0.05]
                    }
                }
            
            elif target == OptimizationTarget.RISK_ADJUSTED_RETURNS:
                return {
                    'risk_management': {
                        'volatility_threshold': [0.02, 0.03, 0.05, 0.08],
                        'correlation_threshold': [0.5, 0.6, 0.7, 0.8],
                        'max_drawdown': [0.05, 0.10, 0.15, 0.20],
                        'risk_aversion': [0.5, 1.0, 1.5, 2.0]
                    }
                }
            
            elif target == OptimizationTarget.SHARPE_RATIO:
                return {
                    'portfolio_strategy': ['equal_weight', 'volatility_adjusted', 'momentum_based'],
                    'rebalancing_frequency': ['daily', 'weekly', 'monthly'],
                    'rebalancing_threshold': [0.02, 0.05, 0.10, 0.15]
                }
            
            else:
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على المعاملات الافتراضية: {e}")
            return {}
    
    async def _grid_search_optimization(self, target: OptimizationTarget, 
                                      parameters: Dict[str, Any]) -> OptimizationResult:
        """تحسين باستخدام Grid Search"""
        try:
            logger.info("بدء تحسين Grid Search")
            
            best_score = float('-inf')
            best_parameters = {}
            iterations = 0
            
            # توليد جميع تركيبات المعاملات
            parameter_combinations = self._generate_parameter_combinations(parameters)
            
            for combination in parameter_combinations:
                if iterations >= self.max_iterations:
                    break
                
                try:
                    # تقييم هذه التركيبة
                    score = await self._evaluate_parameters(target, combination)
                    
                    if score > best_score:
                        best_score = score
                        best_parameters = combination.copy()
                    
                    iterations += 1
                    
                    # تحديث التقدم
                    if iterations % 10 == 0:
                        logger.info(f"Grid Search - التكرار {iterations}: أفضل نتيجة {best_score:.4f}")
                    
                except Exception as e:
                    logger.error(f"خطأ في تقييم المعاملات: {e}")
                    continue
            
            # حساب التحسن
            baseline_score = await self._get_baseline_score(target)
            improvement = (best_score - baseline_score) / abs(baseline_score) if baseline_score != 0 else 0.0
            
            logger.info(f"انتهاء Grid Search - أفضل نتيجة: {best_score:.4f}")
            
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.GRID_SEARCH,
                best_parameters=best_parameters,
                best_score=best_score,
                improvement=improvement,
                optimization_time=0.0,  # سيتم تعيينه لاحقاً
                iterations=iterations,
                convergence=True,
                metadata={'total_combinations': len(parameter_combinations)}
            )
            
        except Exception as e:
            logger.error(f"خطأ في Grid Search: {e}")
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.GRID_SEARCH,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def _generate_parameter_combinations(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """توليد جميع تركيبات المعاملات"""
        try:
            combinations = []
            
            # استخراج أسماء المعاملات وقيمها
            param_names = list(parameters.keys())
            param_values = list(parameters.values())
            
            # توليد التركيبات
            def generate_combinations(index, current_combination):
                if index == len(param_names):
                    combinations.append(current_combination.copy())
                    return
                
                param_name = param_names[index]
                param_value = param_values[index]
                
                if isinstance(param_value, list):
                    for value in param_value:
                        current_combination[param_name] = value
                        generate_combinations(index + 1, current_combination)
                else:
                    current_combination[param_name] = param_value
                    generate_combinations(index + 1, current_combination)
            
            generate_combinations(0, {})
            
            logger.info(f"تم توليد {len(combinations)} تركيبة معاملات")
            return combinations
            
        except Exception as e:
            logger.error(f"خطأ في توليد تركيبات المعاملات: {e}")
            return []
    
    async def _evaluate_parameters(self, target: OptimizationTarget, 
                                 parameters: Dict[str, Any]) -> float:
        """تقييم المعاملات"""
        try:
            # تطبيق المعاملات مؤقتاً
            await self._apply_parameters_temporarily(parameters)
            
            # تشغيل محاكاة قصيرة
            simulation_result = await self._run_simulation(duration_minutes=60)  # ساعة واحدة
            
            # حساب النتيجة حسب الهدف
            if target == OptimizationTarget.PERFORMANCE:
                score = simulation_result.get('total_return', 0.0)
            elif target == OptimizationTarget.RISK_ADJUSTED_RETURNS:
                return_val = simulation_result.get('total_return', 0.0)
                volatility = simulation_result.get('volatility', 0.01)
                score = return_val / volatility if volatility > 0 else 0.0
            elif target == OptimizationTarget.SHARPE_RATIO:
                score = simulation_result.get('sharpe_ratio', 0.0)
            elif target == OptimizationTarget.MAX_DRAWDOWN:
                score = -simulation_result.get('max_drawdown', 0.0)  # سالب لأننا نريد تقليل الانخفاض
            elif target == OptimizationTarget.WIN_RATE:
                score = simulation_result.get('win_rate', 0.0)
            elif target == OptimizationTarget.PROFIT_FACTOR:
                score = simulation_result.get('profit_factor', 0.0)
            else:
                score = 0.0
            
            # استعادة المعاملات الأصلية
            await self._restore_original_parameters()
            
            return score
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المعاملات: {e}")
            return 0.0
    
    async def _apply_parameters_temporarily(self, parameters: Dict[str, Any]):
        """تطبيق المعاملات مؤقتاً"""
        try:
            # تطبيق معاملات إدارة المخاطر
            if 'risk_limits' in parameters:
                risk_manager = global_risk_manager.get_risk_manager(self.user_id)
                risk_manager.update_risk_limits(parameters['risk_limits'])
            
            # تطبيق معاملات معالج الإشارات
            if 'signal_filters' in parameters:
                signal_processor = global_signal_manager.get_signal_processor(self.user_id)
                signal_processor.update_filters(parameters['signal_filters'])
            
            # تطبيق معاملات منفذ الصفقات
            if 'execution_config' in parameters:
                trade_executor = global_trade_executor.get_executor(self.user_id)
                trade_executor.update_execution_config(parameters['execution_config'])
            
            # تطبيق معاملات المحفظة
            if 'portfolio_strategy' in parameters:
                portfolio_manager = global_portfolio_manager.get_portfolio_manager(self.user_id)
                if 'portfolio_strategy' in parameters:
                    from advanced_portfolio_manager import PortfolioStrategy
                    strategy = PortfolioStrategy(parameters['portfolio_strategy'])
                    portfolio_manager.update_strategy(strategy)
                
                if 'rebalancing_settings' in parameters:
                    portfolio_manager.update_rebalancing_settings(parameters['rebalancing_settings'])
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق المعاملات مؤقتاً: {e}")
    
    async def _restore_original_parameters(self):
        """استعادة المعاملات الأصلية"""
        try:
            # استعادة المعاملات الافتراضية
            default_parameters = self._get_default_parameters(OptimizationTarget.PERFORMANCE)
            await self._apply_parameters_temporarily(default_parameters)
            
        except Exception as e:
            logger.error(f"خطأ في استعادة المعاملات الأصلية: {e}")
    
    async def _run_simulation(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """تشغيل محاكاة قصيرة"""
        try:
            # محاكاة بسيطة للأداء
            # في التطبيق الحقيقي، يجب تشغيل محاكاة أكثر تعقيداً
            
            simulation_start = time.time()
            simulation_duration = duration_minutes * 60  # تحويل إلى ثوان
            
            # محاكاة بعض الصفقات
            simulated_trades = []
            total_return = 0.0
            winning_trades = 0
            losing_trades = 0
            
            # محاكاة 10 صفقات عشوائية
            for i in range(10):
                # محاكاة نتيجة الصفقة
                trade_result = self._simulate_trade()
                simulated_trades.append(trade_result)
                
                total_return += trade_result['pnl_percent']
                
                if trade_result['pnl_percent'] > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
            
            # حساب المقاييس
            win_rate = winning_trades / len(simulated_trades) if simulated_trades else 0.0
            
            # محاكاة التقلبات
            volatility = 0.02 + (total_return * 0.001)  # تقلبات متغيرة
            
            # محاكاة نسبة شارب
            sharpe_ratio = total_return / volatility if volatility > 0 else 0.0
            
            # محاكاة الحد الأقصى للانخفاض
            max_drawdown = abs(min([trade['pnl_percent'] for trade in simulated_trades])) * 0.5
            
            # محاكاة Profit Factor
            total_wins = sum([trade['pnl_percent'] for trade in simulated_trades if trade['pnl_percent'] > 0])
            total_losses = abs(sum([trade['pnl_percent'] for trade in simulated_trades if trade['pnl_percent'] < 0]))
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'profit_factor': profit_factor,
                'total_trades': len(simulated_trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades
            }
            
        except Exception as e:
            logger.error(f"خطأ في تشغيل المحاكاة: {e}")
            return {
                'total_return': 0.0,
                'win_rate': 0.0,
                'volatility': 0.02,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'profit_factor': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }
    
    def _simulate_trade(self) -> Dict[str, Any]:
        """محاكاة صفقة واحدة"""
        try:
            import random
            
            # محاكاة نتيجة الصفقة
            success_probability = 0.6  # 60% احتمال النجاح
            is_successful = random.random() < success_probability
            
            if is_successful:
                # صفقة رابحة
                pnl_percent = random.uniform(0.5, 5.0)  # ربح بين 0.5% و 5%
            else:
                # صفقة خاسرة
                pnl_percent = random.uniform(-3.0, -0.5)  # خسارة بين 0.5% و 3%
            
            return {
                'pnl_percent': pnl_percent,
                'successful': is_successful,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"خطأ في محاكاة الصفقة: {e}")
            return {
                'pnl_percent': 0.0,
                'successful': False,
                'timestamp': datetime.now()
            }
    
    async def _get_baseline_score(self, target: OptimizationTarget) -> float:
        """الحصول على النتيجة الأساسية"""
        try:
            # استخدام المعاملات الافتراضية
            default_parameters = self._get_default_parameters(target)
            return await self._evaluate_parameters(target, default_parameters)
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على النتيجة الأساسية: {e}")
            return 0.0
    
    async def _apply_optimized_parameters(self, parameters: Dict[str, Any]):
        """تطبيق المعاملات المحسنة"""
        try:
            # تطبيق المعاملات بشكل دائم
            await self._apply_parameters_temporarily(parameters)
            
            logger.info(f"تم تطبيق المعاملات المحسنة للمستخدم {self.user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق المعاملات المحسنة: {e}")
    
    async def _genetic_algorithm_optimization(self, target: OptimizationTarget, 
                                           parameters: Dict[str, Any]) -> OptimizationResult:
        """تحسين باستخدام الخوارزمية الجينية"""
        try:
            logger.info("بدء تحسين الخوارزمية الجينية")
            
            # تنفيذ مبسط للخوارزمية الجينية
            # في التطبيق الحقيقي، يجب استخدام مكتبة متخصصة
            
            best_score = float('-inf')
            best_parameters = {}
            iterations = 0
            
            # إنشاء مجتمع أولي
            population_size = 20
            population = self._create_initial_population(parameters, population_size)
            
            for generation in range(50):  # 50 جيل
                if iterations >= self.max_iterations:
                    break
                
                # تقييم المجتمع
                fitness_scores = []
                for individual in population:
                    score = await self._evaluate_parameters(target, individual)
                    fitness_scores.append(score)
                    
                    if score > best_score:
                        best_score = score
                        best_parameters = individual.copy()
                    
                    iterations += 1
                
                # اختيار الأفضل للتكاثر
                selected = self._selection(population, fitness_scores, population_size // 2)
                
                # إنتاج جيل جديد
                population = self._reproduction(selected, population_size)
                
                logger.info(f"الجيل {generation + 1}: أفضل نتيجة {best_score:.4f}")
            
            # حساب التحسن
            baseline_score = await self._get_baseline_score(target)
            improvement = (best_score - baseline_score) / abs(baseline_score) if baseline_score != 0 else 0.0
            
            logger.info(f"انتهاء الخوارزمية الجينية - أفضل نتيجة: {best_score:.4f}")
            
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.GENETIC_ALGORITHM,
                best_parameters=best_parameters,
                best_score=best_score,
                improvement=improvement,
                optimization_time=0.0,
                iterations=iterations,
                convergence=True,
                metadata={'generations': 50, 'population_size': population_size}
            )
            
        except Exception as e:
            logger.error(f"خطأ في الخوارزمية الجينية: {e}")
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.GENETIC_ALGORITHM,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def _create_initial_population(self, parameters: Dict[str, Any], size: int) -> List[Dict[str, Any]]:
        """إنشاء مجتمع أولي"""
        try:
            population = []
            
            for _ in range(size):
                individual = {}
                
                for param_name, param_value in parameters.items():
                    if isinstance(param_value, list):
                        import random
                        individual[param_name] = random.choice(param_value)
                    else:
                        individual[param_name] = param_value
                
                population.append(individual)
            
            return population
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المجتمع الأولي: {e}")
            return []
    
    def _selection(self, population: List[Dict[str, Any]], 
                  fitness_scores: List[float], num_selected: int) -> List[Dict[str, Any]]:
        """اختيار الأفضل للتكاثر"""
        try:
            # اختيار الأفضل بناءً على النتائج
            combined = list(zip(population, fitness_scores))
            combined.sort(key=lambda x: x[1], reverse=True)
            
            selected = [individual for individual, score in combined[:num_selected]]
            return selected
            
        except Exception as e:
            logger.error(f"خطأ في الاختيار: {e}")
            return population[:num_selected]
    
    def _reproduction(self, selected: List[Dict[str, Any]], population_size: int) -> List[Dict[str, Any]]:
        """إنتاج جيل جديد"""
        try:
            import random
            
            new_population = []
            
            # إضافة الأفضل كما هم
            new_population.extend(selected)
            
            # إنتاج أفراد جدد
            while len(new_population) < population_size:
                # اختيار والدين عشوائيين
                parent1 = random.choice(selected)
                parent2 = random.choice(selected)
                
                # إنتاج طفل
                child = self._crossover(parent1, parent2)
                
                # تطبيق طفرات
                child = self._mutate(child)
                
                new_population.append(child)
            
            return new_population[:population_size]
            
        except Exception as e:
            logger.error(f"خطأ في الإنتاج: {e}")
            return selected
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """تقاطع بين والدين"""
        try:
            child = {}
            
            for key in parent1.keys():
                import random
                # اختيار عشوائي من أحد الوالدين
                child[key] = random.choice([parent1[key], parent2[key]])
            
            return child
            
        except Exception as e:
            logger.error(f"خطأ في التقاطع: {e}")
            return parent1
    
    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """تطبيق طفرة"""
        try:
            import random
            
            mutated = individual.copy()
            
            # تطبيق طفرة على معامل واحد عشوائياً
            if mutated:
                key = random.choice(list(mutated.keys()))
                if isinstance(mutated[key], list):
                    mutated[key] = random.choice(mutated[key])
            
            return mutated
            
        except Exception as e:
            logger.error(f"خطأ في الطفرة: {e}")
            return individual
    
    async def _bayesian_optimization(self, target: OptimizationTarget, 
                                   parameters: Dict[str, Any]) -> OptimizationResult:
        """تحسين باستخدام Bayesian Optimization"""
        try:
            logger.info("بدء تحسين Bayesian Optimization")
            
            # تنفيذ مبسط للتحسين البايزي
            # في التطبيق الحقيقي، يجب استخدام مكتبة متخصصة مثل scikit-optimize
            
            best_score = float('-inf')
            best_parameters = {}
            iterations = 0
            
            # نقاط أولية للاستكشاف
            initial_points = 10
            for i in range(initial_points):
                # توليد معاملات عشوائية
                random_params = self._generate_random_parameters(parameters)
                
                # تقييم
                score = await self._evaluate_parameters(target, random_params)
                
                if score > best_score:
                    best_score = score
                    best_parameters = random_params
                
                iterations += 1
            
            # استكشاف إضافي
            for i in range(50):
                if iterations >= self.max_iterations:
                    break
                
                # توليد معاملات جديدة بناءً على النتائج السابقة
                new_params = self._generate_smart_parameters(parameters, best_parameters)
                
                # تقييم
                score = await self._evaluate_parameters(target, new_params)
                
                if score > best_score:
                    best_score = score
                    best_parameters = new_params
                
                iterations += 1
            
            # حساب التحسن
            baseline_score = await self._get_baseline_score(target)
            improvement = (best_score - baseline_score) / abs(baseline_score) if baseline_score != 0 else 0.0
            
            logger.info(f"انتهاء Bayesian Optimization - أفضل نتيجة: {best_score:.4f}")
            
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.BAYESIAN_OPTIMIZATION,
                best_parameters=best_parameters,
                best_score=best_score,
                improvement=improvement,
                optimization_time=0.0,
                iterations=iterations,
                convergence=True,
                metadata={'initial_points': initial_points}
            )
            
        except Exception as e:
            logger.error(f"خطأ في Bayesian Optimization: {e}")
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.BAYESIAN_OPTIMIZATION,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def _generate_random_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """توليد معاملات عشوائية"""
        try:
            import random
            
            random_params = {}
            
            for param_name, param_value in parameters.items():
                if isinstance(param_value, list):
                    random_params[param_name] = random.choice(param_value)
                else:
                    random_params[param_name] = param_value
            
            return random_params
            
        except Exception as e:
            logger.error(f"خطأ في توليد المعاملات العشوائية: {e}")
            return {}
    
    def _generate_smart_parameters(self, parameters: Dict[str, Any], 
                                 best_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """توليد معاملات ذكية"""
        try:
            import random
            
            smart_params = {}
            
            for param_name, param_value in parameters.items():
                if isinstance(param_value, list):
                    # التركيز حول أفضل قيمة مع بعض العشوائية
                    if param_name in best_parameters:
                        best_value = best_parameters[param_name]
                        try:
                            best_index = param_value.index(best_value)
                            # اختيار قيمة قريبة من الأفضل
                            start = max(0, best_index - 1)
                            end = min(len(param_value), best_index + 2)
                            smart_params[param_name] = random.choice(param_value[start:end])
                        except ValueError:
                            smart_params[param_name] = random.choice(param_value)
                    else:
                        smart_params[param_name] = random.choice(param_value)
                else:
                    smart_params[param_name] = param_value
            
            return smart_params
            
        except Exception as e:
            logger.error(f"خطأ في توليد المعاملات الذكية: {e}")
            return {}
    
    async def _random_search_optimization(self, target: OptimizationTarget, 
                                        parameters: Dict[str, Any]) -> OptimizationResult:
        """تحسين باستخدام البحث العشوائي"""
        try:
            logger.info("بدء تحسين البحث العشوائي")
            
            best_score = float('-inf')
            best_parameters = {}
            iterations = 0
            
            for i in range(self.max_iterations):
                # توليد معاملات عشوائية
                random_params = self._generate_random_parameters(parameters)
                
                # تقييم
                score = await self._evaluate_parameters(target, random_params)
                
                if score > best_score:
                    best_score = score
                    best_parameters = random_params
                
                iterations += 1
                
                # تحديث التقدم
                if iterations % 50 == 0:
                    logger.info(f"البحث العشوائي - التكرار {iterations}: أفضل نتيجة {best_score:.4f}")
            
            # حساب التحسن
            baseline_score = await self._get_baseline_score(target)
            improvement = (best_score - baseline_score) / abs(baseline_score) if baseline_score != 0 else 0.0
            
            logger.info(f"انتهاء البحث العشوائي - أفضل نتيجة: {best_score:.4f}")
            
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.RANDOM_SEARCH,
                best_parameters=best_parameters,
                best_score=best_score,
                improvement=improvement,
                optimization_time=0.0,
                iterations=iterations,
                convergence=True,
                metadata={'max_iterations': self.max_iterations}
            )
            
        except Exception as e:
            logger.error(f"خطأ في البحث العشوائي: {e}")
            return OptimizationResult(
                target=target,
                method=OptimizationMethod.RANDOM_SEARCH,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """الحصول على تقرير التحسين"""
        try:
            return {
                'user_id': self.user_id,
                'optimization_enabled': self.optimization_enabled,
                'auto_optimization': self.auto_optimization,
                'optimization_frequency': self.optimization_frequency.total_seconds() / 86400,  # أيام
                'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None,
                'total_optimizations': len(self.optimization_history),
                'optimization_history': [
                    {
                        'target': result.target.value,
                        'method': result.method.value,
                        'best_score': result.best_score,
                        'improvement': result.improvement,
                        'optimization_time': result.optimization_time,
                        'iterations': result.iterations,
                        'convergence': result.convergence,
                        'timestamp': datetime.now().isoformat()
                    }
                    for result in self.optimization_history[-10:]  # آخر 10 تحسينات
                ],
                'performance_metrics': {
                    'total_trades': self.performance_metrics.total_trades,
                    'winning_trades': self.performance_metrics.winning_trades,
                    'losing_trades': self.performance_metrics.losing_trades,
                    'win_rate': self.performance_metrics.win_rate,
                    'average_win': self.performance_metrics.average_win,
                    'average_loss': self.performance_metrics.average_loss,
                    'profit_factor': self.performance_metrics.profit_factor,
                    'sharpe_ratio': self.performance_metrics.sharpe_ratio,
                    'max_drawdown': self.performance_metrics.max_drawdown,
                    'total_return': self.performance_metrics.total_return,
                    'volatility': self.performance_metrics.volatility,
                    'var_95': self.performance_metrics.var_95,
                    'cvar_95': self.performance_metrics.cvar_95,
                    'last_updated': self.performance_metrics.last_updated.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير التحسين: {e}")
            return {'error': str(e)}
    
    def update_optimization_settings(self, settings: Dict[str, Any]) -> bool:
        """تحديث إعدادات التحسين"""
        try:
            for key, value in settings.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            logger.info(f"تم تحديث إعدادات التحسين للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات التحسين: {e}")
            return False
    
    def cleanup(self):
        """تنظيف الموارد"""
        try:
            self.optimization_executor.shutdown(wait=True)
            logger.info(f"تم تنظيف موارد محسن البوت للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد: {e}")


# مدير التحسين العام
class GlobalOptimizationManager:
    """مدير التحسين العام لجميع المستخدمين"""
    
    def __init__(self):
        self.user_optimizers: Dict[int, TradingBotOptimizer] = {}
        self.global_statistics = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'average_improvement': 0.0,
            'total_optimization_time': 0.0
        }
    
    def get_optimizer(self, user_id: int) -> TradingBotOptimizer:
        """الحصول على محسن البوت للمستخدم"""
        if user_id not in self.user_optimizers:
            self.user_optimizers[user_id] = TradingBotOptimizer(user_id)
        return self.user_optimizers[user_id]
    
    async def optimize_user_bot(self, user_id: int, target: OptimizationTarget, 
                              method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
                              parameters: Dict[str, Any] = None) -> OptimizationResult:
        """تحسين بوت المستخدم"""
        try:
            optimizer = self.get_optimizer(user_id)
            result = await optimizer.optimize_bot(target, method, parameters)
            
            # تحديث الإحصائيات العامة
            if result.improvement > 0:
                self.global_statistics['successful_optimizations'] += 1
            
            self.global_statistics['total_optimizations'] += 1
            self.global_statistics['total_optimization_time'] += result.optimization_time
            
            # تحديث متوسط التحسن
            if self.global_statistics['total_optimizations'] > 0:
                total_improvement = sum(
                    opt.improvement for opt in optimizer.optimization_history
                )
                self.global_statistics['average_improvement'] = (
                    total_improvement / self.global_statistics['total_optimizations']
                )
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تحسين بوت المستخدم {user_id}: {e}")
            return OptimizationResult(
                target=target,
                method=method,
                best_parameters={},
                best_score=0.0,
                improvement=0.0,
                optimization_time=0.0,
                iterations=0,
                convergence=False,
                metadata={'error': str(e)}
            )
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        try:
            user_stats = {}
            for user_id, optimizer in self.user_optimizers.items():
                user_stats[user_id] = optimizer.get_optimization_report()
            
            return {
                'global_statistics': self.global_statistics,
                'user_statistics': user_stats,
                'total_users': len(self.user_optimizers)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات العامة: {e}")
            return {'error': str(e)}
    
    def cleanup_all(self):
        """تنظيف جميع الموارد"""
        try:
            for optimizer in self.user_optimizers.values():
                optimizer.cleanup()
            logger.info("تم تنظيف جميع موارد التحسين")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد العامة: {e}")


# مثيل عام لمدير التحسين
global_optimization_manager = GlobalOptimizationManager()
