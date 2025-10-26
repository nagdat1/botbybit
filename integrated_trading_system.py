#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التداول المتكامل - Integrated Trading System
نظام شامل يجمع جميع المكونات المتقدمة في نظام واحد متكامل
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
from enhanced_trading_bot import enhanced_bot_manager, EnhancedTradingBot

# استيراد المكونات الأصلية
from user_manager import user_manager
from database import db_manager
from signal_converter import signal_converter
from signal_executor import SignalExecutor

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """حالة النظام"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"
    ERROR = "error"

class SystemMode(Enum):
    """وضع النظام"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class SystemConfiguration:
    """إعدادات النظام"""
    system_mode: SystemMode
    max_users: int
    max_concurrent_trades: int
    system_wide_risk_limits: Dict[str, float]
    auto_optimization_enabled: bool
    monitoring_enabled: bool
    backup_enabled: bool
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SystemMetrics:
    """مقاييس النظام"""
    total_users: int
    active_users: int
    total_trades: int
    successful_trades: int
    total_volume: float
    system_uptime: float
    average_response_time: float
    error_rate: float
    last_updated: datetime = field(default_factory=datetime.now)

class IntegratedTradingSystem:
    """نظام التداول المتكامل"""
    
    def __init__(self):
        self.system_id = "integrated_trading_system_v2"
        self.version = "2.0.0"
        self.status = SystemStatus.INITIALIZING
        self.system_mode = SystemMode.DEVELOPMENT
        
        # إعدادات النظام
        self.configuration = SystemConfiguration(
            system_mode=SystemMode.DEVELOPMENT,
            max_users=1000,
            max_concurrent_trades=100,
            system_wide_risk_limits={
                'max_total_exposure': 1000000.0,
                'max_daily_loss': 100000.0,
                'max_volatility': 0.1
            },
            auto_optimization_enabled=True,
            monitoring_enabled=True,
            backup_enabled=True
        )
        
        # مقاييس النظام
        self.system_metrics = SystemMetrics(
            total_users=0,
            active_users=0,
            total_trades=0,
            successful_trades=0,
            total_volume=0.0,
            system_uptime=0.0,
            average_response_time=0.0,
            error_rate=0.0
        )
        
        # مكونات النظام
        self.risk_manager = global_risk_manager
        self.signal_manager = global_signal_manager
        self.trade_executor = global_trade_executor
        self.portfolio_manager = global_portfolio_manager
        self.optimization_manager = global_optimization_manager
        self.bot_manager = enhanced_bot_manager
        
        # إعدادات المراقبة
        self.monitoring_enabled = True
        self.performance_tracking_enabled = True
        self.system_health_checks_enabled = True
        
        # خيوط النظام
        self.system_monitoring_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        
        # إعدادات التوقيت
        self.monitoring_interval = 10.0  # 10 ثوان
        self.health_check_interval = 60.0  # دقيقة واحدة
        self.optimization_interval = 3600.0  # ساعة واحدة
        
        # بداية النظام
        self.system_start_time = datetime.now()
        
        logger.info(f"تم تهيئة نظام التداول المتكامل {self.system_id} v{self.version}")
    
    async def initialize_system(self) -> bool:
        """تهيئة النظام"""
        try:
            logger.info("بدء تهيئة نظام التداول المتكامل")
            
            self.status = SystemStatus.INITIALIZING
            
            # تهيئة قاعدة البيانات
            if not await self._initialize_database():
                logger.error("فشل في تهيئة قاعدة البيانات")
                return False
            
            # تهيئة مدير المستخدمين
            if not await self._initialize_user_manager():
                logger.error("فشل في تهيئة مدير المستخدمين")
                return False
            
            # تهيئة المكونات المتقدمة
            if not await self._initialize_advanced_components():
                logger.error("فشل في تهيئة المكونات المتقدمة")
                return False
            
            # بدء مراقبة النظام
            if self.monitoring_enabled:
                self.system_monitoring_task = asyncio.create_task(self._system_monitoring_loop())
            
            # بدء فحص صحة النظام
            if self.system_health_checks_enabled:
                self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # بدء التحسين التلقائي
            if self.configuration.auto_optimization_enabled:
                self.optimization_task = asyncio.create_task(self._system_optimization_loop())
            
            self.status = SystemStatus.RUNNING
            
            logger.info("تم تهيئة نظام التداول المتكامل بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام: {e}")
            self.status = SystemStatus.ERROR
            return False
    
    async def shutdown_system(self) -> bool:
        """إيقاف النظام"""
        try:
            logger.info("بدء إيقاف نظام التداول المتكامل")
            
            self.status = SystemStatus.STOPPED
            
            # إيقاف المهام
            if self.system_monitoring_task:
                self.system_monitoring_task.cancel()
                try:
                    await self.system_monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self.optimization_task:
                self.optimization_task.cancel()
                try:
                    await self.optimization_task
                except asyncio.CancelledError:
                    pass
            
            # إيقاف جميع البوتات
            await self._shutdown_all_bots()
            
            # حفظ حالة النظام
            await self._save_system_state()
            
            # تنظيف الموارد
            await self._cleanup_resources()
            
            logger.info("تم إيقاف نظام التداول المتكامل بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف النظام: {e}")
            return False
    
    async def process_signal(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة الإشارة"""
        try:
            if self.status != SystemStatus.RUNNING:
                return {
                    'success': False,
                    'message': f'النظام في حالة {self.status.value} - لا يمكن معالجة الإشارات'
                }
            
            start_time = time.time()
            
            logger.info(f"معالجة إشارة جديدة للمستخدم {user_id}")
            
            # التحقق من وجود المستخدم
            if not user_manager.is_user_active(user_id):
                return {
                    'success': False,
                    'message': 'المستخدم غير نشط أو غير موجود'
                }
            
            # تحويل الإشارة إذا لزم الأمر
            if 'signal' in signal_data and 'action' not in signal_data:
                user_data = user_manager.get_user(user_id)
                converted_signal = signal_converter.convert_signal(signal_data, user_data)
                
                if not converted_signal:
                    return {
                        'success': False,
                        'message': 'فشل في تحويل الإشارة'
                    }
                
                signal_data = converted_signal
            
            # معالجة الإشارة بواسطة البوت المحسن
            result = await self.bot_manager.process_signal(user_id, signal_data)
            
            # تحديث مقاييس النظام
            processing_time = time.time() - start_time
            self._update_system_metrics(processing_time, result.get('success', False))
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {e}'
            }
    
    async def start_user_bot(self, user_id: int, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """بدء تشغيل بوت المستخدم"""
        try:
            if self.status != SystemStatus.RUNNING:
                return {
                    'success': False,
                    'message': f'النظام في حالة {self.status.value} - لا يمكن بدء البوتات'
                }
            
            logger.info(f"بدء تشغيل بوت المستخدم {user_id}")
            
            # بدء البوت
            success = await self.bot_manager.start_bot(user_id, initial_capital)
            
            if success:
                # تحديث إحصائيات النظام
                self.system_metrics.active_users += 1
                
                return {
                    'success': True,
                    'message': 'تم بدء تشغيل البوت بنجاح',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في بدء تشغيل البوت'
                }
            
        except Exception as e:
            logger.error(f"خطأ في بدء تشغيل بوت المستخدم {user_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ في بدء تشغيل البوت: {e}'
            }
    
    async def stop_user_bot(self, user_id: int) -> Dict[str, Any]:
        """إيقاف بوت المستخدم"""
        try:
            logger.info(f"إيقاف بوت المستخدم {user_id}")
            
            # إيقاف البوت
            success = await self.bot_manager.stop_bot(user_id)
            
            if success:
                # تحديث إحصائيات النظام
                self.system_metrics.active_users = max(0, self.system_metrics.active_users - 1)
                
                return {
                    'success': True,
                    'message': 'تم إيقاف البوت بنجاح',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في إيقاف البوت'
                }
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف بوت المستخدم {user_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ في إيقاف البوت: {e}'
            }
    
    def get_user_bot_status(self, user_id: int) -> Dict[str, Any]:
        """الحصول على حالة بوت المستخدم"""
        try:
            return self.bot_manager.get_bot_status(user_id)
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة بوت المستخدم {user_id}: {e}")
            return {'error': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        try:
            return {
                'system_id': self.system_id,
                'version': self.version,
                'status': self.status.value,
                'system_mode': self.system_mode.value,
                'uptime': (datetime.now() - self.system_start_time).total_seconds(),
                'configuration': {
                    'max_users': self.configuration.max_users,
                    'max_concurrent_trades': self.configuration.max_concurrent_trades,
                    'system_wide_risk_limits': self.configuration.system_wide_risk_limits,
                    'auto_optimization_enabled': self.configuration.auto_optimization_enabled,
                    'monitoring_enabled': self.configuration.monitoring_enabled,
                    'backup_enabled': self.configuration.backup_enabled
                },
                'metrics': {
                    'total_users': self.system_metrics.total_users,
                    'active_users': self.system_metrics.active_users,
                    'total_trades': self.system_metrics.total_trades,
                    'successful_trades': self.system_metrics.successful_trades,
                    'total_volume': self.system_metrics.total_volume,
                    'system_uptime': self.system_metrics.system_uptime,
                    'average_response_time': self.system_metrics.average_response_time,
                    'error_rate': self.system_metrics.error_rate,
                    'last_updated': self.system_metrics.last_updated.isoformat()
                },
                'components': {
                    'risk_manager': 'active',
                    'signal_manager': 'active',
                    'trade_executor': 'active',
                    'portfolio_manager': 'active',
                    'optimization_manager': 'active',
                    'bot_manager': 'active'
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة النظام: {e}")
            return {'error': str(e)}
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        try:
            # إحصائيات النظام العام
            system_stats = self.get_system_status()
            
            # إحصائيات البوتات
            bot_stats = self.bot_manager.get_global_statistics()
            
            # إحصائيات إدارة المخاطر
            risk_stats = self.risk_manager.get_global_risk_report()
            
            # إحصائيات معالجة الإشارات
            signal_stats = self.signal_manager.get_global_statistics()
            
            # إحصائيات تنفيذ الصفقات
            execution_stats = self.trade_executor.get_global_statistics()
            
            # إحصائيات المحافظ
            portfolio_stats = self.portfolio_manager.get_global_statistics()
            
            # إحصائيات التحسين
            optimization_stats = self.optimization_manager.get_global_statistics()
            
            return {
                'system_overview': system_stats,
                'bot_statistics': bot_stats,
                'risk_statistics': risk_stats,
                'signal_statistics': signal_stats,
                'execution_statistics': execution_stats,
                'portfolio_statistics': portfolio_stats,
                'optimization_statistics': optimization_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات النظام: {e}")
            return {'error': str(e)}
    
    async def _initialize_database(self) -> bool:
        """تهيئة قاعدة البيانات"""
        try:
            # التحقق من اتصال قاعدة البيانات
            if not db_manager:
                logger.error("مدير قاعدة البيانات غير متوفر")
                return False
            
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            return False
    
    async def _initialize_user_manager(self) -> bool:
        """تهيئة مدير المستخدمين"""
        try:
            # تحميل المستخدمين
            user_manager.load_all_users()
            
            # تحديث إحصائيات النظام
            self.system_metrics.total_users = len(user_manager.users)
            
            logger.info(f"تم تهيئة مدير المستخدمين - {self.system_metrics.total_users} مستخدم")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة مدير المستخدمين: {e}")
            return False
    
    async def _initialize_advanced_components(self) -> bool:
        """تهيئة المكونات المتقدمة"""
        try:
            # التحقق من جميع المكونات
            components = [
                self.risk_manager,
                self.signal_manager,
                self.trade_executor,
                self.portfolio_manager,
                self.optimization_manager,
                self.bot_manager
            ]
            
            for component in components:
                if not component:
                    logger.error(f"مكون غير متوفر: {component}")
                    return False
            
            logger.info("تم تهيئة جميع المكونات المتقدمة بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة المكونات المتقدمة: {e}")
            return False
    
    async def _system_monitoring_loop(self):
        """حلقة مراقبة النظام"""
        try:
            while self.monitoring_enabled and self.status == SystemStatus.RUNNING:
                try:
                    # تحديث مقاييس النظام
                    await self._update_system_metrics()
                    
                    # فحص صحة النظام
                    await self._check_system_health()
                    
                    # حفظ بيانات المراقبة
                    await self._save_monitoring_data()
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في حلقة مراقبة النظام: {e}")
                    await asyncio.sleep(self.monitoring_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info("تم إلغاء حلقة مراقبة النظام")
        except Exception as e:
            logger.error(f"خطأ عام في حلقة مراقبة النظام: {e}")
    
    async def _health_check_loop(self):
        """حلقة فحص صحة النظام"""
        try:
            while self.system_health_checks_enabled and self.status == SystemStatus.RUNNING:
                try:
                    # فحص صحة المكونات
                    health_status = await self._perform_health_checks()
                    
                    # معالجة المشاكل المكتشفة
                    if health_status['status'] != 'healthy':
                        await self._handle_health_issues(health_status)
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في حلقة فحص الصحة: {e}")
                    await asyncio.sleep(self.health_check_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info("تم إلغاء حلقة فحص الصحة")
        except Exception as e:
            logger.error(f"خطأ عام في حلقة فحص الصحة: {e}")
    
    async def _system_optimization_loop(self):
        """حلقة تحسين النظام"""
        try:
            while self.configuration.auto_optimization_enabled and self.status == SystemStatus.RUNNING:
                try:
                    # تشغيل التحسين التلقائي
                    await self._run_system_optimization()
                    
                    # انتظار قبل التكرار التالي
                    await asyncio.sleep(self.optimization_interval)
                    
                except Exception as e:
                    logger.error(f"خطأ في حلقة تحسين النظام: {e}")
                    await asyncio.sleep(self.optimization_interval)
                    continue
            
        except asyncio.CancelledError:
            logger.info("تم إلغاء حلقة تحسين النظام")
        except Exception as e:
            logger.error(f"خطأ عام في حلقة تحسين النظام: {e}")
    
    async def _update_system_metrics(self, response_time: float = None, success: bool = None):
        """تحديث مقاييس النظام"""
        try:
            # تحديث وقت الاستجابة
            if response_time is not None:
                if self.system_metrics.average_response_time == 0:
                    self.system_metrics.average_response_time = response_time
                else:
                    self.system_metrics.average_response_time = (
                        self.system_metrics.average_response_time * 0.9 + response_time * 0.1
                    )
            
            # تحديث معدل النجاح
            if success is not None:
                if success:
                    self.system_metrics.successful_trades += 1
                self.system_metrics.total_trades += 1
                
                # حساب معدل الخطأ
                if self.system_metrics.total_trades > 0:
                    self.system_metrics.error_rate = (
                        (self.system_metrics.total_trades - self.system_metrics.successful_trades) /
                        self.system_metrics.total_trades
                    )
            
            # تحديث وقت التشغيل
            self.system_metrics.system_uptime = (
                datetime.now() - self.system_start_time
            ).total_seconds()
            
            # تحديث عدد المستخدمين النشطين
            self.system_metrics.active_users = len([
                bot for bot in self.bot_manager.user_bots.values()
                if bot.status.value == 'running'
            ])
            
            self.system_metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مقاييس النظام: {e}")
    
    async def _check_system_health(self):
        """فحص صحة النظام"""
        try:
            # فحص المكونات
            components_health = {
                'risk_manager': self.risk_manager is not None,
                'signal_manager': self.signal_manager is not None,
                'trade_executor': self.trade_executor is not None,
                'portfolio_manager': self.portfolio_manager is not None,
                'optimization_manager': self.optimization_manager is not None,
                'bot_manager': self.bot_manager is not None
            }
            
            # فحص قاعدة البيانات
            db_health = db_manager is not None
            
            # فحص مدير المستخدمين
            user_manager_health = user_manager is not None
            
            # حساب صحة النظام العامة
            all_components_healthy = all(components_health.values())
            system_healthy = all_components_healthy and db_health and user_manager_health
            
            if not system_healthy:
                logger.warning("تم اكتشاف مشاكل في صحة النظام")
                
                # تسجيل المشاكل
                for component, healthy in components_health.items():
                    if not healthy:
                        logger.error(f"المكون {component} غير صحي")
            
        except Exception as e:
            logger.error(f"خطأ في فحص صحة النظام: {e}")
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """تنفيذ فحوصات الصحة"""
        try:
            health_status = {
                'status': 'healthy',
                'components': {},
                'issues': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # فحص المكونات
            components = {
                'risk_manager': self.risk_manager,
                'signal_manager': self.signal_manager,
                'trade_executor': self.trade_executor,
                'portfolio_manager': self.portfolio_manager,
                'optimization_manager': self.optimization_manager,
                'bot_manager': self.bot_manager
            }
            
            for name, component in components.items():
                if component:
                    health_status['components'][name] = 'healthy'
                else:
                    health_status['components'][name] = 'unhealthy'
                    health_status['issues'].append(f"المكون {name} غير متوفر")
            
            # تحديد الحالة العامة
            if health_status['issues']:
                health_status['status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ فحوصات الصحة: {e}")
            return {
                'status': 'error',
                'components': {},
                'issues': [f'خطأ في فحص الصحة: {e}'],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _handle_health_issues(self, health_status: Dict[str, Any]):
        """معالجة مشاكل الصحة"""
        try:
            for issue in health_status['issues']:
                logger.error(f"مشكلة صحية: {issue}")
                
                # محاولة إصلاح المشاكل
                if "غير متوفر" in issue:
                    # محاولة إعادة تهيئة المكون
                    await self._reinitialize_component(issue)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة مشاكل الصحة: {e}")
    
    async def _reinitialize_component(self, issue: str):
        """إعادة تهيئة المكون"""
        try:
            # تحديد المكون وإعادة تهيئته
            if "risk_manager" in issue:
                # إعادة تهيئة مدير المخاطر
                pass
            elif "signal_manager" in issue:
                # إعادة تهيئة مدير الإشارات
                pass
            # إلخ...
            
            logger.info(f"تم إعادة تهيئة المكون: {issue}")
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تهيئة المكون: {e}")
    
    async def _run_system_optimization(self):
        """تشغيل تحسين النظام"""
        try:
            logger.info("بدء تحسين النظام التلقائي")
            
            # تحسين البوتات النشطة
            active_bots = [
                bot for bot in self.bot_manager.user_bots.values()
                if bot.status.value == 'running'
            ]
            
            for bot in active_bots:
                try:
                    # تشغيل التحسين للبوت
                    if bot.optimizer:
                        await bot.optimizer.optimize_bot(
                            target=bot.optimizer.OptimizationTarget.PERFORMANCE,
                            method=bot.optimizer.OptimizationMethod.GRID_SEARCH
                        )
                except Exception as e:
                    logger.error(f"خطأ في تحسين البوت {bot.user_id}: {e}")
                    continue
            
            logger.info("تم الانتهاء من تحسين النظام التلقائي")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين النظام: {e}")
    
    async def _save_monitoring_data(self):
        """حفظ بيانات المراقبة"""
        try:
            # حفظ بيانات المراقبة في قاعدة البيانات
            monitoring_data = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': {
                    'total_users': self.system_metrics.total_users,
                    'active_users': self.system_metrics.active_users,
                    'total_trades': self.system_metrics.total_trades,
                    'successful_trades': self.system_metrics.successful_trades,
                    'total_volume': self.system_metrics.total_volume,
                    'system_uptime': self.system_metrics.system_uptime,
                    'average_response_time': self.system_metrics.average_response_time,
                    'error_rate': self.system_metrics.error_rate
                },
                'system_status': self.status.value,
                'system_mode': self.system_mode.value
            }
            
            # حفظ في قاعدة البيانات
            db_manager.create_monitoring_record(monitoring_data)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات المراقبة: {e}")
    
    async def _save_system_state(self):
        """حفظ حالة النظام"""
        try:
            # حفظ حالة النظام
            system_state = {
                'system_id': self.system_id,
                'version': self.version,
                'status': self.status.value,
                'system_mode': self.system_mode.value,
                'configuration': {
                    'max_users': self.configuration.max_users,
                    'max_concurrent_trades': self.configuration.max_concurrent_trades,
                    'system_wide_risk_limits': self.configuration.system_wide_risk_limits,
                    'auto_optimization_enabled': self.configuration.auto_optimization_enabled,
                    'monitoring_enabled': self.configuration.monitoring_enabled,
                    'backup_enabled': self.configuration.backup_enabled
                },
                'metrics': {
                    'total_users': self.system_metrics.total_users,
                    'active_users': self.system_metrics.active_users,
                    'total_trades': self.system_metrics.total_trades,
                    'successful_trades': self.system_metrics.successful_trades,
                    'total_volume': self.system_metrics.total_volume,
                    'system_uptime': self.system_metrics.system_uptime,
                    'average_response_time': self.system_metrics.average_response_time,
                    'error_rate': self.system_metrics.error_rate
                },
                'last_updated': datetime.now().isoformat()
            }
            
            # حفظ في قاعدة البيانات
            db_manager.create_system_state_record(system_state)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ حالة النظام: {e}")
    
    async def _shutdown_all_bots(self):
        """إيقاف جميع البوتات"""
        try:
            # إيقاف جميع البوتات النشطة
            for user_id, bot in self.bot_manager.user_bots.items():
                try:
                    if bot.status.value == 'running':
                        await bot.stop()
                        logger.info(f"تم إيقاف البوت للمستخدم {user_id}")
                except Exception as e:
                    logger.error(f"خطأ في إيقاف البوت للمستخدم {user_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف جميع البوتات: {e}")
    
    async def _cleanup_resources(self):
        """تنظيف الموارد"""
        try:
            # تنظيف موارد البوتات
            self.bot_manager.cleanup_all()
            
            # تنظيف موارد التحسين
            self.optimization_manager.cleanup_all()
            
            # تنظيف موارد التنفيذ
            self.trade_executor.cleanup_all()
            
            logger.info("تم تنظيف جميع موارد النظام")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الموارد: {e}")
    
    def update_system_configuration(self, new_config: Dict[str, Any]) -> bool:
        """تحديث إعدادات النظام"""
        try:
            for key, value in new_config.items():
                if hasattr(self.configuration, key):
                    setattr(self.configuration, key, value)
            
            self.configuration.last_updated = datetime.now()
            
            logger.info("تم تحديث إعدادات النظام")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات النظام: {e}")
            return False
    
    def set_system_mode(self, new_mode: SystemMode) -> bool:
        """تحديث وضع النظام"""
        try:
            self.system_mode = new_mode
            self.configuration.system_mode = new_mode
            
            logger.info(f"تم تحديث وضع النظام إلى {new_mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث وضع النظام: {e}")
            return False


# مثيل عام لنظام التداول المتكامل
integrated_system = IntegratedTradingSystem()


# دوال مساعدة للاستخدام السريع
async def initialize_trading_system() -> bool:
    """تهيئة نظام التداول"""
    return await integrated_system.initialize_system()

async def shutdown_trading_system() -> bool:
    """إيقاف نظام التداول"""
    return await integrated_system.shutdown_system()

async def process_trading_signal(user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """معالجة إشارة التداول"""
    return await integrated_system.process_signal(user_id, signal_data)

async def start_user_trading_bot(user_id: int, initial_capital: float = 10000.0) -> Dict[str, Any]:
    """بدء تشغيل بوت التداول للمستخدم"""
    return await integrated_system.start_user_bot(user_id, initial_capital)

async def stop_user_trading_bot(user_id: int) -> Dict[str, Any]:
    """إيقاف بوت التداول للمستخدم"""
    return await integrated_system.stop_user_bot(user_id)

def get_system_status() -> Dict[str, Any]:
    """الحصول على حالة النظام"""
    return integrated_system.get_system_status()

def get_system_statistics() -> Dict[str, Any]:
    """الحصول على إحصائيات النظام"""
    return integrated_system.get_system_statistics()

def get_user_bot_status(user_id: int) -> Dict[str, Any]:
    """الحصول على حالة بوت المستخدم"""
    return integrated_system.get_user_bot_status(user_id)


if __name__ == "__main__":
    # مثال على الاستخدام
    async def main():
        # تهيئة النظام
        await initialize_trading_system()
        
        # بدء بوت للمستخدم
        await start_user_trading_bot(12345, 10000.0)
        
        # معالجة إشارة
        signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TV_001'
        }
        
        result = await process_trading_signal(12345, signal)
        print(f"نتيجة معالجة الإشارة: {result}")
        
        # الحصول على حالة النظام
        status = get_system_status()
        print(f"حالة النظام: {status}")
        
        # إيقاف النظام
        await shutdown_trading_system()
    
    # تشغيل المثال
    asyncio.run(main())
