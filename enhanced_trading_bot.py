#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
البوت المحسن - Enhanced Trading Bot
نظام متكامل يجمع جميع المكونات المتقدمة في بوت واحد محسن
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
from trading_bot_optimizer import global_optimization_manager, TradingBotOptimizer

# استيراد المكونات الأصلية
from user_manager import user_manager
from database import db_manager

logger = logging.getLogger(__name__)

class BotStatus(Enum):
    """حالة البوت"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"

class TradingMode(Enum):
    """وضع التداول"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

@dataclass
class BotConfiguration:
    """إعدادات البوت"""
    user_id: int
    trading_mode: TradingMode
    risk_tolerance: float
    max_positions: int
    auto_rebalancing: bool
    signal_filtering: bool
    risk_management: bool
    portfolio_optimization: bool
    performance_tracking: bool
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class BotPerformance:
    """أداء البوت"""
    total_trades: int
    successful_trades: int
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    average_trade_duration: float
    last_updated: datetime = field(default_factory=datetime.now)

class EnhancedTradingBot:
    """البوت المحسن المتكامل"""
    
    def __init__(self, user_id: int, initial_capital: float = 10000.0):
        self.user_id = user_id
        self.initial_capital = initial_capital
        
        # حالة البوت
        self.status = BotStatus.STOPPED
        self.trading_mode = TradingMode.MODERATE
        self.configuration = BotConfiguration(
            user_id=user_id,
            trading_mode=TradingMode.MODERATE,
            risk_tolerance=0.5,
            max_positions=10,
            auto_rebalancing=True,
            signal_filtering=True,
            risk_management=True,
            portfolio_optimization=True,
            performance_tracking=True
        )
        
        # المكونات المتقدمة
        self.risk_manager: Optional[AdvancedRiskManager] = None
        self.signal_processor: Optional[AdvancedSignalProcessor] = None
        self.trade_executor: Optional[AdvancedTradeExecutor] = None
        self.portfolio_manager: Optional[AdvancedPortfolioManager] = None
        self.optimizer: Optional[TradingBotOptimizer] = None
        
        # أداء البوت
        self.performance = BotPerformance(
            total_trades=0,
            successful_trades=0,
            total_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            average_trade_duration=0.0
        )
        
        # إعدادات التداول
        self.active_positions: Dict[str, Dict] = {}
        self.pending_orders: Dict[str, Dict] = {}
        self.signal_queue: List[Dict] = []
        self.market_data: Dict[str, Dict] = {}
        
        # إعدادات المراقبة
        self.monitoring_enabled = True
        self.performance_tracking_enabled = True
        self.auto_optimization_enabled = False
        
        # خيوط العمل
        self.main_loop_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        
        # إعدادات التوقيت
        self.main_loop_interval = 1.0  # ثانية واحدة
        self.monitoring_interval = 5.0  # 5 ثوان
        self.optimization_interval = 3600.0  # ساعة واحدة
        
        logger.info(f"تم تهيئة البوت المحسن للمستخدم {user_id}")
    
    async def initialize(self) -> bool:
        """تهيئة البوت"""
        try:
            logger.info(f"بدء تهيئة البوت المحسن للمستخدم {self.user_id}")
            
            # تهيئة المكونات المتقدمة
            self.risk_manager = global_risk_manager.get_risk_manager(self.user_id)
            self.signal_processor = global_signal_manager.get_signal_processor(self.user_id)
            self.trade_executor = global_trade_executor.get_executor(self.user_id)
            self.portfolio_manager = global_portfolio_manager.get_portfolio_manager(self.user_id, self.initial_capital)
            self.optimizer = global_optimization_manager.get_optimizer(self.user_id)
            
            # تحميل إعدادات المستخدم
            user_data = user_manager.get_user(self.user_id)
            if user_data:
                await self._load_user_settings(user_data)
            
            # تطبيق إعدادات التداول
            await self._apply_trading_mode_settings()
            
            # تهيئة المحفظة
            await self._initialize_portfolio()
            
            logger.info(f"تم تهيئة البوت المحسن بنجاح للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة البوت: {e}")
            self.status = BotStatus.ERROR
            return False
    
    async def start(self) -> bool:
        """بدء تشغيل البوت"""
        try:
            if self.status != BotStatus.STOPPED:
                logger.warning(f"البوت في حالة {self.status.value} - لا يمكن البدء")
                return False
            
            logger.info(f"بدء تشغيل البوت المحسن للمستخدم {self.user_id}")
            
            self.status = BotStatus.STARTING
            
            # تهيئة البوت
            if not await self.initialize():
                self.status = BotStatus.ERROR
                return False
            
            # بدء الحلقة الرئيسية
            self.main_loop_task = asyncio.create_task(self._main_loop())
            
            # بدء مراقبة الأداء
            if self.monitoring_enabled:
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # بدء التحسين التلقائي
            if self.auto_optimization_enabled:
                self.optimization_task = asyncio.create_task(self._optimization_loop())
            
            self.status = BotStatus.RUNNING
            
            logger.info(f"تم بدء تشغيل البوت المحسن بنجاح للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في بدء تشغيل البوت: {e}")
            self.status = BotStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """إيقاف البوت"""
        try:
            if self.status != BotStatus.RUNNING:
                logger.warning(f"البوت في حالة {self.status.value} - لا يمكن الإيقاف")
                return False
            
            logger.info(f"إيقاف البوت المحسن للمستخدم {self.user_id}")
            
            self.status = BotStatus.STOPPING
            
            # إيقاف المهام
            if self.main_loop_task:
                self.main_loop_task.cancel()
                try:
                    await self.main_loop_task
                except asyncio.CancelledError:
                    pass
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self.optimization_task:
                self.optimization_task.cancel()
                try:
                    await self.optimization_task
                except asyncio.CancelledError:
                    pass
            
            # حفظ الحالة
            await self._save_bot_state()
            
            self.status = BotStatus.STOPPED
            
            logger.info(f"تم إيقاف البوت المحسن بنجاح للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت: {e}")
            self.status = BotStatus.ERROR
            return False
    
    async def pause(self) -> bool:
        """إيقاف مؤقت للبوت"""
        try:
            if self.status != BotStatus.RUNNING:
                logger.warning(f"البوت في حالة {self.status.value} - لا يمكن الإيقاف المؤقت")
                return False
            
            logger.info(f"إيقاف مؤقت للبوت المحسن للمستخدم {self.user_id}")
            
            self.status = BotStatus.PAUSED
            
            # إيقاف المهام مؤقتاً
            if self.main_loop_task:
                self.main_loop_task.cancel()
            
            logger.info(f"تم إيقاف البوت مؤقتاً للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في الإيقاف المؤقت: {e}")
            return False
    
    async def resume(self) -> bool:
        """استئناف البوت"""
        try:
            if self.status != BotStatus.PAUSED:
                logger.warning(f"البوت في حالة {self.status.value} - لا يمكن الاستئناف")
                return False
            
            logger.info(f"استئناف البوت المحسن للمستخدم {self.user_id}")
            
            self.status = BotStatus.RUNNING
            
            # استئناف الحلقة الرئيسية
            self.main_loop_task = asyncio.create_task(self._main_loop())
            
            logger.info(f"تم استئناف البوت المحسن للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في الاستئناف: {e}")
            return False
    
    async def _main_loop(self):
        """الحلقة الرئيسية للبوت"""
        try:
            while self.status == BotStatus.RUNNING:
                try:
                    # معالجة الإشارات في الطابور
                    await self._process_signal_queue()
                    
                    # تحديث بيانات السوق
                    await self._update_market_data()
                    
                    # تحديث الصفقات المفتوحة
                    await self._update_open_positions()
                    
                    # فحص إعادة التوازن
                    if self.configuration.auto_rebalancing:
                        await self._check_rebalancing()
                    
                    # فحص المخاطر
                    if self.configuration.risk_management:
                        await self._check_risk_limits()
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.main_loop_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في الحلقة الرئيسية: {e}")
                    await asyncio.sleep(self.main_loop_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info(f"تم إلغاء الحلقة الرئيسية للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ عام في الحلقة الرئيسية: {e}")
            self.status = BotStatus.ERROR
    
    async def _monitoring_loop(self):
        """حلقة مراقبة الأداء"""
        try:
            while self.monitoring_enabled and self.status in [BotStatus.RUNNING, BotStatus.PAUSED]:
                try:
                    # تحديث مقاييس الأداء
                    await self._update_performance_metrics()
                    
                    # حفظ البيانات
                    await self._save_performance_data()
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في حلقة المراقبة: {e}")
                    await asyncio.sleep(self.monitoring_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info(f"تم إلغاء حلقة المراقبة للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ عام في حلقة المراقبة: {e}")
    
    async def _optimization_loop(self):
        """حلقة التحسين التلقائي"""
        try:
            while self.auto_optimization_enabled and self.status == BotStatus.RUNNING:
                try:
                    # التحقق من الحاجة للتحسين
                    if self._should_optimize():
                        # تشغيل التحسين
                        await self._run_auto_optimization()
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.optimization_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في حلقة التحسين: {e}")
                    await asyncio.sleep(self.optimization_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info(f"تم إلغاء حلقة التحسين للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ عام في حلقة التحسين: {e}")
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة الإشارة"""
        try:
            if self.status != BotStatus.RUNNING:
                return {
                    'success': False,
                    'message': f'البوت في حالة {self.status.value} - لا يمكن معالجة الإشارات'
                }
            
            logger.info(f"معالجة إشارة جديدة للمستخدم {self.user_id}")
            
            # معالجة الإشارة المتقدمة
            if self.configuration.signal_filtering and self.signal_processor:
                processed_signal = self.signal_processor.process_signal(signal_data, self.market_data)
                
                if not processed_signal.get('success', False):
                    return {
                        'success': False,
                        'message': 'تم رفض الإشارة بواسطة الفلاتر',
                        'details': processed_signal
                    }
                
                signal_data = processed_signal.get('enhanced_signal', signal_data)
            
            # فحص المخاطر
            if self.configuration.risk_management and self.risk_manager:
                risk_check = self.risk_manager.check_risk_limits(signal_data)
                
                if not risk_check.get('allowed', False):
                    return {
                        'success': False,
                        'message': 'تم رفض الإشارة بواسطة إدارة المخاطر',
                        'details': risk_check
                    }
            
            # إضافة الإشارة إلى الطابور
            self.signal_queue.append({
                'signal': signal_data,
                'timestamp': datetime.now(),
                'processed': False
            })
            
            return {
                'success': True,
                'message': 'تم قبول الإشارة وإضافتها إلى الطابور',
                'queue_position': len(self.signal_queue)
            }
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {e}'
            }
    
    async def _process_signal_queue(self):
        """معالجة طابور الإشارات"""
        try:
            if not self.signal_queue:
                return
            
            # معالجة الإشارات حسب الأولوية
            signals_to_process = [
                signal for signal in self.signal_queue 
                if not signal['processed']
            ]
            
            for signal_item in signals_to_process:
                try:
                    signal_data = signal_item['signal']
                    
                    # تنفيذ الصفقة
                    if self.trade_executor:
                        execution_result = await self.trade_executor.execute_trade(
                            signal_data, self.market_data
                        )
                        
                        if execution_result.success:
                            # تحديث المحفظة
                            if self.portfolio_manager:
                                await self._update_portfolio_with_trade(execution_result)
                            
                            # تحديث الأداء
                            await self._update_trade_performance(execution_result)
                            
                            logger.info(f"تم تنفيذ الصفقة بنجاح: {execution_result.order_id}")
                        else:
                            logger.warning(f"فشل في تنفيذ الصفقة: {execution_result.error_message}")
                    
                    # وضع علامة على الإشارة كمعالجة
                    signal_item['processed'] = True
                    
                except Exception as e:
                    logger.error(f"خطأ في معالجة إشارة: {e}")
                    continue
            
            # إزالة الإشارات المعالجة
            self.signal_queue = [
                signal for signal in self.signal_queue 
                if not signal['processed']
            ]
            
        except Exception as e:
            logger.error(f"خطأ في معالجة طابور الإشارات: {e}")
    
    async def _update_market_data(self):
        """تحديث بيانات السوق"""
        try:
            # محاكاة تحديث بيانات السوق
            # في التطبيق الحقيقي، يجب الحصول على البيانات من مصادر حقيقية
            
            for symbol in ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']:
                if symbol not in self.market_data:
                    self.market_data[symbol] = {}
                
                # محاكاة تحديث السعر
                base_price = 50000.0 if symbol == 'BTCUSDT' else 3000.0 if symbol == 'ETHUSDT' else 0.5
                price_change = (time.time() % 100 - 50) / 1000  # تغيير طفيف
                current_price = base_price * (1 + price_change)
                
                self.market_data[symbol].update({
                    'price': current_price,
                    'volume': 1000000.0,
                    'volatility': 0.02,
                    'last_updated': datetime.now()
                })
                
                # تحديث المحفظة
                if self.portfolio_manager and symbol in self.portfolio_manager.assets:
                    self.portfolio_manager.update_asset_price(symbol, current_price)
                
                # تحديث مدير المخاطر
                if self.risk_manager:
                    self.risk_manager.update_market_data(symbol, current_price, 0.02)
            
        except Exception as e:
            logger.error(f"خطأ في تحديث بيانات السوق: {e}")
    
    async def _update_open_positions(self):
        """تحديث الصفقات المفتوحة"""
        try:
            # تحديث الصفقات المفتوحة
            if self.trade_executor:
                active_orders = self.trade_executor.get_active_orders()
                
                for order_id, order_info in active_orders.items():
                    # تحديث حالة الأمر
                    # في التطبيق الحقيقي، يجب فحص حالة الأمر من المنصة
                    
                    if order_id not in self.active_positions:
                        self.active_positions[order_id] = {
                            'order_info': order_info,
                            'created_at': datetime.now(),
                            'status': 'open'
                        }
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقات المفتوحة: {e}")
    
    async def _check_rebalancing(self):
        """فحص إعادة التوازن"""
        try:
            if self.portfolio_manager:
                # توليد إشارات إعادة التوازن
                rebalancing_signals = self.portfolio_manager.generate_rebalancing_signals()
                
                if rebalancing_signals:
                    logger.info(f"تم اكتشاف {len(rebalancing_signals)} إشارة إعادة توازن")
                    
                    # تنفيذ إعادة التوازن
                    rebalancing_result = self.portfolio_manager.rebalance_portfolio(rebalancing_signals)
                    
                    if rebalancing_result['success']:
                        logger.info(f"تم تنفيذ {rebalancing_result['trades_executed']} عملية إعادة توازن")
                    else:
                        logger.warning(f"فشل في إعادة التوازن: {rebalancing_result['message']}")
            
        except Exception as e:
            logger.error(f"خطأ في فحص إعادة التوازن: {e}")
    
    async def _check_risk_limits(self):
        """فحص حدود المخاطر"""
        try:
            if self.risk_manager:
                # فحص المخاطر العامة
                risk_report = self.risk_manager.get_risk_report()
                
                # التحقق من المخاطر الحرجة
                if risk_report.get('portfolio_risk', {}).get('risk_level') == 'critical':
                    logger.warning("تم اكتشاف مخاطر حرجة - إيقاف التداول مؤقتاً")
                    await self.pause()
                
                # التحقق من الخسائر اليومية
                daily_pnl = risk_report.get('risk_metrics', {}).get('daily_pnl', 0)
                max_daily_loss = risk_report.get('risk_limits', {}).get('max_daily_loss', 1000)
                
                if daily_pnl < -max_daily_loss * 0.8:  # 80% من الحد الأقصى
                    logger.warning(f"الخسارة اليومية تقترب من الحد الأقصى: {daily_pnl}")
                
        except Exception as e:
            logger.error(f"خطأ في فحص حدود المخاطر: {e}")
    
    async def _update_portfolio_with_trade(self, execution_result):
        """تحديث المحفظة مع الصفقة"""
        try:
            if self.portfolio_manager and execution_result.success:
                # إضافة الصفقة إلى المحفظة
                # هذا تبسيط - يجب تنفيذ منطق أكثر تعقيداً
                
                symbol = execution_result.metadata.get('symbol', 'UNKNOWN')
                quantity = execution_result.executed_quantity or 0
                price = execution_result.executed_price or 0
                
                if symbol != 'UNKNOWN' and quantity > 0 and price > 0:
                    # إضافة أو تحديث الأصل في المحفظة
                    if symbol in self.portfolio_manager.assets:
                        # تحديث الكمية الموجودة
                        existing_asset = self.portfolio_manager.assets[symbol]
                        existing_asset.quantity += quantity
                        existing_asset.market_value = existing_asset.quantity * price
                    else:
                        # إضافة أصل جديد
                        self.portfolio_manager.add_asset(
                            symbol=symbol,
                            name=symbol,
                            quantity=quantity,
                            current_price=price,
                            cost_basis=price
                        )
                
        except Exception as e:
            logger.error(f"خطأ في تحديث المحفظة: {e}")
    
    async def _update_trade_performance(self, execution_result):
        """تحديث أداء التداول"""
        try:
            if execution_result.success:
                self.performance.total_trades += 1
                self.performance.successful_trades += 1
                
                # حساب معدل الفوز
                if self.performance.total_trades > 0:
                    self.performance.win_rate = (
                        self.performance.successful_trades / self.performance.total_trades
                    )
                
                # تحديث العائد الإجمالي
                if execution_result.executed_price and execution_result.executed_quantity:
                    trade_value = execution_result.executed_price * execution_result.executed_quantity
                    self.performance.total_return += trade_value * 0.001  # محاكاة ربح 0.1%
                
                self.performance.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"خطأ في تحديث أداء التداول: {e}")
    
    async def _update_performance_metrics(self):
        """تحديث مقاييس الأداء"""
        try:
            # تحديث مقاييس المحفظة
            if self.portfolio_manager:
                portfolio_metrics = self.portfolio_manager.portfolio_metrics
                
                self.performance.total_return = portfolio_metrics.unrealized_pnl_percent
                self.performance.sharpe_ratio = portfolio_metrics.sharpe_ratio
                self.performance.max_drawdown = portfolio_metrics.max_drawdown
            
            # تحديث مقاييس التنفيذ
            if self.trade_executor:
                execution_stats = self.trade_executor.get_execution_statistics()
                
                if execution_stats.get('performance_metrics'):
                    metrics = execution_stats['performance_metrics']
                    self.performance.total_trades = metrics.get('total_orders', 0)
                    self.performance.successful_trades = metrics.get('successful_orders', 0)
                    
                    if self.performance.total_trades > 0:
                        self.performance.win_rate = (
                            self.performance.successful_trades / self.performance.total_trades
                        )
            
            self.performance.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مقاييس الأداء: {e}")
    
    async def _load_user_settings(self, user_data: Dict[str, Any]):
        """تحميل إعدادات المستخدم"""
        try:
            # تحميل وضع التداول
            trading_mode = user_data.get('trading_mode', 'moderate')
            if trading_mode in ['conservative', 'moderate', 'aggressive']:
                self.trading_mode = TradingMode(trading_mode)
            
            # تحميل إعدادات المخاطر
            risk_tolerance = user_data.get('risk_tolerance', 0.5)
            self.configuration.risk_tolerance = risk_tolerance
            
            # تحميل إعدادات المحفظة
            max_positions = user_data.get('max_positions', 10)
            self.configuration.max_positions = max_positions
            
            logger.info(f"تم تحميل إعدادات المستخدم للمستخدم {self.user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل إعدادات المستخدم: {e}")
    
    async def _apply_trading_mode_settings(self):
        """تطبيق إعدادات وضع التداول"""
        try:
            if self.trading_mode == TradingMode.CONSERVATIVE:
                # إعدادات محافظة
                if self.risk_manager:
                    self.risk_manager.update_risk_limits({
                        'max_daily_loss': 100,
                        'max_weekly_loss': 500,
                        'max_position_size': 500,
                        'max_leverage': 5
                    })
                
                if self.signal_processor:
                    self.signal_processor.update_filters({
                        'min_confidence': 0.8,
                        'min_quality_score': 0.7,
                        'max_age_seconds': 300
                    })
            
            elif self.trading_mode == TradingMode.AGGRESSIVE:
                # إعدادات عدوانية
                if self.risk_manager:
                    self.risk_manager.update_risk_limits({
                        'max_daily_loss': 2000,
                        'max_weekly_loss': 10000,
                        'max_position_size': 5000,
                        'max_leverage': 20
                    })
                
                if self.signal_processor:
                    self.signal_processor.update_filters({
                        'min_confidence': 0.6,
                        'min_quality_score': 0.5,
                        'max_age_seconds': 900
                    })
            
            # الوضع المعتدل هو الافتراضي
            
            logger.info(f"تم تطبيق إعدادات وضع التداول: {self.trading_mode.value}")
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق إعدادات وضع التداول: {e}")
    
    async def _initialize_portfolio(self):
        """تهيئة المحفظة"""
        try:
            if self.portfolio_manager:
                # إضافة رصيد نقدي أولي
                self.portfolio_manager.cash_balance = self.initial_capital
                
                logger.info(f"تم تهيئة المحفظة برصيد أولي: {self.initial_capital}")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة المحفظة: {e}")
    
    def _should_optimize(self) -> bool:
        """فحص الحاجة للتحسين"""
        try:
            if not self.optimizer:
                return False
            
            # التحسين كل أسبوع
            if self.optimizer.last_optimization:
                time_since_last = datetime.now() - self.optimizer.last_optimization
                return time_since_last >= timedelta(days=7)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في فحص الحاجة للتحسين: {e}")
            return False
    
    async def _run_auto_optimization(self):
        """تشغيل التحسين التلقائي"""
        try:
            if self.optimizer:
                logger.info(f"بدء التحسين التلقائي للمستخدم {self.user_id}")
                
                # تحسين الأداء
                result = await self.optimizer.optimize_bot(
                    target=OptimizationTarget.PERFORMANCE,
                    method=OptimizationMethod.GRID_SEARCH
                )
                
                if result.improvement > 0.01:  # تحسن أكثر من 1%
                    logger.info(f"تم تحسين الأداء بنسبة {result.improvement:.2%}")
                else:
                    logger.info("لم يتم اكتشاف تحسن ملحوظ")
            
        except Exception as e:
            logger.error(f"خطأ في التحسين التلقائي: {e}")
    
    async def _save_bot_state(self):
        """حفظ حالة البوت"""
        try:
            # حفظ حالة البوت في قاعدة البيانات
            bot_state = {
                'user_id': self.user_id,
                'status': self.status.value,
                'trading_mode': self.trading_mode.value,
                'configuration': {
                    'risk_tolerance': self.configuration.risk_tolerance,
                    'max_positions': self.configuration.max_positions,
                    'auto_rebalancing': self.configuration.auto_rebalancing,
                    'signal_filtering': self.configuration.signal_filtering,
                    'risk_management': self.configuration.risk_management,
                    'portfolio_optimization': self.configuration.portfolio_optimization,
                    'performance_tracking': self.configuration.performance_tracking
                },
                'performance': {
                    'total_trades': self.performance.total_trades,
                    'successful_trades': self.performance.successful_trades,
                    'total_return': self.performance.total_return,
                    'sharpe_ratio': self.performance.sharpe_ratio,
                    'max_drawdown': self.performance.max_drawdown,
                    'win_rate': self.performance.win_rate,
                    'profit_factor': self.performance.profit_factor
                },
                'active_positions': self.active_positions,
                'last_updated': datetime.now().isoformat()
            }
            
            # حفظ في قاعدة البيانات
            db_manager.update_user(self.user_id, {'bot_state': json.dumps(bot_state)})
            
            logger.info(f"تم حفظ حالة البوت للمستخدم {self.user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ حالة البوت: {e}")
    
    async def _save_performance_data(self):
        """حفظ بيانات الأداء"""
        try:
            # حفظ بيانات الأداء
            performance_data = {
                'user_id': self.user_id,
                'timestamp': datetime.now().isoformat(),
                'performance': {
                    'total_trades': self.performance.total_trades,
                    'successful_trades': self.performance.successful_trades,
                    'total_return': self.performance.total_return,
                    'sharpe_ratio': self.performance.sharpe_ratio,
                    'max_drawdown': self.performance.max_drawdown,
                    'win_rate': self.performance.win_rate,
                    'profit_factor': self.performance.profit_factor
                }
            }
            
            # حفظ في قاعدة البيانات
            db_manager.create_performance_record(performance_data)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات الأداء: {e}")
    
    def get_bot_status(self) -> Dict[str, Any]:
        """الحصول على حالة البوت"""
        try:
            return {
                'user_id': self.user_id,
                'status': self.status.value,
                'trading_mode': self.trading_mode.value,
                'configuration': {
                    'risk_tolerance': self.configuration.risk_tolerance,
                    'max_positions': self.configuration.max_positions,
                    'auto_rebalancing': self.configuration.auto_rebalancing,
                    'signal_filtering': self.configuration.signal_filtering,
                    'risk_management': self.configuration.risk_management,
                    'portfolio_optimization': self.configuration.portfolio_optimization,
                    'performance_tracking': self.configuration.performance_tracking
                },
                'performance': {
                    'total_trades': self.performance.total_trades,
                    'successful_trades': self.performance.successful_trades,
                    'total_return': self.performance.total_return,
                    'sharpe_ratio': self.performance.sharpe_ratio,
                    'max_drawdown': self.performance.max_drawdown,
                    'win_rate': self.performance.win_rate,
                    'profit_factor': self.performance.profit_factor,
                    'last_updated': self.performance.last_updated.isoformat()
                },
                'active_positions': len(self.active_positions),
                'pending_orders': len(self.pending_orders),
                'signal_queue': len(self.signal_queue),
                'market_data_symbols': len(self.market_data),
                'monitoring_enabled': self.monitoring_enabled,
                'auto_optimization_enabled': self.auto_optimization_enabled
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة البوت: {e}")
            return {'error': str(e)}
    
    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """تحديث إعدادات البوت"""
        try:
            for key, value in new_config.items():
                if hasattr(self.configuration, key):
                    setattr(self.configuration, key, value)
            
            self.configuration.last_updated = datetime.now()
            
            logger.info(f"تم تحديث إعدادات البوت للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات البوت: {e}")
            return False
    
    def update_trading_mode(self, new_mode: TradingMode) -> bool:
        """تحديث وضع التداول"""
        try:
            self.trading_mode = new_mode
            self.configuration.trading_mode = new_mode
            
            # تطبيق الإعدادات الجديدة
            asyncio.create_task(self._apply_trading_mode_settings())
            
            logger.info(f"تم تحديث وضع التداول إلى {new_mode.value} للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث وضع التداول: {e}")
            return False
    
    def cleanup(self):
        """تنظيف الموارد"""
        try:
            # إيقاف البوت
            if self.status == BotStatus.RUNNING:
                asyncio.create_task(self.stop())
            
            # تنظيف المكونات
            if self.optimizer:
                self.optimizer.cleanup()
            
            if self.trade_executor:
                self.trade_executor.cleanup()
            
            logger.info(f"تم تنظيف موارد البوت المحسن للمستخدم {self.user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد: {e}")


# مدير البوتات المحسن
class EnhancedTradingBotManager:
    """مدير البوتات المحسن لجميع المستخدمين"""
    
    def __init__(self):
        self.user_bots: Dict[int, EnhancedTradingBot] = {}
        self.global_statistics = {
            'total_bots': 0,
            'active_bots': 0,
            'total_trades': 0,
            'total_return': 0.0,
            'average_performance': 0.0
        }
    
    def get_bot(self, user_id: int, initial_capital: float = 10000.0) -> EnhancedTradingBot:
        """الحصول على البوت المحسن للمستخدم"""
        if user_id not in self.user_bots:
            self.user_bots[user_id] = EnhancedTradingBot(user_id, initial_capital)
        return self.user_bots[user_id]
    
    async def start_bot(self, user_id: int, initial_capital: float = 10000.0) -> bool:
        """بدء تشغيل البوت"""
        try:
            bot = self.get_bot(user_id, initial_capital)
            return await bot.start()
            
        except Exception as e:
            logger.error(f"خطأ في بدء تشغيل البوت للمستخدم {user_id}: {e}")
            return False
    
    async def stop_bot(self, user_id: int) -> bool:
        """إيقاف البوت"""
        try:
            if user_id in self.user_bots:
                bot = self.user_bots[user_id]
                return await bot.stop()
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت للمستخدم {user_id}: {e}")
            return False
    
    async def pause_bot(self, user_id: int) -> bool:
        """إيقاف البوت مؤقتاً"""
        try:
            if user_id in self.user_bots:
                bot = self.user_bots[user_id]
                return await bot.pause()
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت مؤقتاً للمستخدم {user_id}: {e}")
            return False
    
    async def resume_bot(self, user_id: int) -> bool:
        """استئناف البوت"""
        try:
            if user_id in self.user_bots:
                bot = self.user_bots[user_id]
                return await bot.resume()
            return False
            
        except Exception as e:
            logger.error(f"خطأ في استئناف البوت للمستخدم {user_id}: {e}")
            return False
    
    async def process_signal(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة إشارة للمستخدم"""
        try:
            if user_id in self.user_bots:
                bot = self.user_bots[user_id]
                return await bot.process_signal(signal_data)
            else:
                return {
                    'success': False,
                    'message': 'البوت غير موجود أو غير نشط'
                }
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة للمستخدم {user_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {e}'
            }
    
    def get_bot_status(self, user_id: int) -> Dict[str, Any]:
        """الحصول على حالة البوت"""
        try:
            if user_id in self.user_bots:
                bot = self.user_bots[user_id]
                return bot.get_bot_status()
            else:
                return {
                    'user_id': user_id,
                    'status': 'not_found',
                    'message': 'البوت غير موجود'
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة البوت للمستخدم {user_id}: {e}")
            return {'error': str(e)}
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        try:
            total_bots = len(self.user_bots)
            active_bots = sum(1 for bot in self.user_bots.values() if bot.status == BotStatus.RUNNING)
            
            total_trades = 0
            total_return = 0.0
            
            user_stats = {}
            for user_id, bot in self.user_bots.items():
                status = bot.get_bot_status()
                user_stats[user_id] = status
                
                total_trades += status['performance']['total_trades']
                total_return += status['performance']['total_return']
            
            average_performance = total_return / total_bots if total_bots > 0 else 0.0
            
            return {
                'global_statistics': {
                    'total_bots': total_bots,
                    'active_bots': active_bots,
                    'total_trades': total_trades,
                    'total_return': total_return,
                    'average_performance': average_performance
                },
                'user_statistics': user_stats
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات العامة: {e}")
            return {'error': str(e)}
    
    def cleanup_all(self):
        """تنظيف جميع الموارد"""
        try:
            for bot in self.user_bots.values():
                bot.cleanup()
            logger.info("تم تنظيف جميع موارد البوتات المحسنة")
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد العامة: {e}")


# مثيل عام لمدير البوتات المحسن
enhanced_bot_manager = EnhancedTradingBotManager()
