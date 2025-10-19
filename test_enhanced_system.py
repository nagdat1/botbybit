#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النظام المحسن - Enhanced System Test
اختبار شامل لجميع المكونات المحسنة في النظام
"""

import logging
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union

# استيراد المكونات المحسنة
from advanced_risk_manager import global_risk_manager, AdvancedRiskManager
from advanced_signal_processor import global_signal_manager, AdvancedSignalProcessor
from advanced_trade_executor import global_trade_executor, AdvancedTradeExecutor
from advanced_portfolio_manager import global_portfolio_manager, AdvancedPortfolioManager
from trading_bot_optimizer import global_optimization_manager, TradingBotOptimizer
from enhanced_trading_bot import enhanced_bot_manager, EnhancedTradingBot
from integrated_trading_system import integrated_system, initialize_trading_system, shutdown_trading_system

logger = logging.getLogger(__name__)

class EnhancedSystemTester:
    """اختبار النظام المحسن"""
    
    def __init__(self):
        self.test_results = {}
        self.test_start_time = None
        self.test_end_time = None
        
        # إعدادات الاختبار
        self.test_user_id = 99999
        self.test_initial_capital = 10000.0
        self.test_signals = [
            {
                'signal': 'buy',
                'symbol': 'BTCUSDT',
                'id': 'TV_TEST_001'
            },
            {
                'signal': 'sell',
                'symbol': 'ETHUSDT',
                'id': 'TV_TEST_002'
            },
            {
                'signal': 'close',
                'symbol': 'BTCUSDT',
                'id': 'TV_TEST_003'
            }
        ]
        
        logger.info("تم تهيئة اختبار النظام المحسن")
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """تشغيل اختبار شامل"""
        try:
            self.test_start_time = datetime.now()
            logger.info("بدء الاختبار الشامل للنظام المحسن")
            
            # تشغيل جميع الاختبارات
            test_results = {
                'system_initialization': await self._test_system_initialization(),
                'risk_manager': await self._test_risk_manager(),
                'signal_processor': await self._test_signal_processor(),
                'trade_executor': await self._test_trade_executor(),
                'portfolio_manager': await self._test_portfolio_manager(),
                'optimizer': await self._test_optimizer(),
                'enhanced_bot': await self._test_enhanced_bot(),
                'integrated_system': await self._test_integrated_system(),
                'signal_processing': await self._test_signal_processing(),
                'performance_analysis': await self._test_performance_analysis()
            }
            
            self.test_end_time = datetime.now()
            
            # حساب النتائج الإجمالية
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results.values() if result.get('success', False))
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # إنشاء التقرير النهائي
            final_report = {
                'test_summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': success_rate,
                    'test_duration': (self.test_end_time - self.test_start_time).total_seconds()
                },
                'test_results': test_results,
                'recommendations': self._generate_recommendations(test_results),
                'timestamp': self.test_end_time.isoformat()
            }
            
            self.test_results = final_report
            
            logger.info(f"انتهاء الاختبار الشامل - معدل النجاح: {success_rate:.2f}%")
            
            return final_report
            
        except Exception as e:
            logger.error(f"خطأ في الاختبار الشامل: {e}")
            return {
                'test_summary': {
                    'total_tests': 0,
                    'passed_tests': 0,
                    'failed_tests': 0,
                    'success_rate': 0,
                    'test_duration': 0,
                    'error': str(e)
                },
                'test_results': {},
                'recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _test_system_initialization(self) -> Dict[str, Any]:
        """اختبار تهيئة النظام"""
        try:
            logger.info("اختبار تهيئة النظام")
            
            # تهيئة النظام
            init_result = await initialize_trading_system()
            
            if init_result:
                # التحقق من حالة النظام
                system_status = integrated_system.get_system_status()
                
                if system_status.get('status') == 'running':
                    return {
                        'success': True,
                        'message': 'تم تهيئة النظام بنجاح',
                        'details': {
                            'system_status': system_status,
                            'initialization_time': time.time()
                        }
                    }
                else:
                    return {
                        'success': False,
                        'message': f'النظام في حالة {system_status.get("status")}',
                        'details': system_status
                    }
            else:
                return {
                    'success': False,
                    'message': 'فشل في تهيئة النظام',
                    'details': {}
                }
                
        except Exception as e:
            logger.error(f"خطأ في اختبار تهيئة النظام: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار تهيئة النظام: {e}',
                'details': {}
            }
    
    async def _test_risk_manager(self) -> Dict[str, Any]:
        """اختبار مدير المخاطر"""
        try:
            logger.info("اختبار مدير المخاطر")
            
            # الحصول على مدير المخاطر
            risk_manager = global_risk_manager.get_risk_manager(self.test_user_id)
            
            if not risk_manager:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على مدير المخاطر',
                    'details': {}
                }
            
            # اختبار تحديث حدود المخاطر
            risk_limits = {
                'max_daily_loss': 500.0,
                'max_weekly_loss': 2000.0,
                'max_position_size': 1000.0,
                'max_leverage': 10.0
            }
            
            update_result = risk_manager.update_risk_limits(risk_limits)
            
            if not update_result:
                return {
                    'success': False,
                    'message': 'فشل في تحديث حدود المخاطر',
                    'details': {}
                }
            
            # اختبار فحص المخاطر
            test_trade = {
                'symbol': 'BTCUSDT',
                'size': 100.0,
                'leverage': 5.0
            }
            
            risk_check = risk_manager.check_risk_limits(test_trade)
            
            # اختبار تقرير المخاطر
            risk_report = risk_manager.get_risk_report()
            
            return {
                'success': True,
                'message': 'تم اختبار مدير المخاطر بنجاح',
                'details': {
                    'risk_limits_updated': update_result,
                    'risk_check_result': risk_check,
                    'risk_report': risk_report
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار مدير المخاطر: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار مدير المخاطر: {e}',
                'details': {}
            }
    
    async def _test_signal_processor(self) -> Dict[str, Any]:
        """اختبار معالج الإشارات"""
        try:
            logger.info("اختبار معالج الإشارات")
            
            # الحصول على معالج الإشارات
            signal_processor = global_signal_manager.get_signal_processor(self.test_user_id)
            
            if not signal_processor:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على معالج الإشارات',
                    'details': {}
                }
            
            # اختبار معالجة الإشارات
            processed_signals = []
            
            for signal in self.test_signals:
                processed_signal = signal_processor.process_signal(signal)
                processed_signals.append(processed_signal)
            
            # اختبار إحصائيات الإشارات
            signal_stats = signal_processor.get_signal_statistics()
            
            # اختبار تحديث الفلاتر
            new_filters = {
                'min_confidence': 0.7,
                'min_quality_score': 0.6,
                'max_age_seconds': 300
            }
            
            filter_update_result = signal_processor.update_filters(new_filters)
            
            return {
                'success': True,
                'message': 'تم اختبار معالج الإشارات بنجاح',
                'details': {
                    'processed_signals': len(processed_signals),
                    'signal_statistics': signal_stats,
                    'filter_update_result': filter_update_result
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار معالج الإشارات: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار معالج الإشارات: {e}',
                'details': {}
            }
    
    async def _test_trade_executor(self) -> Dict[str, Any]:
        """اختبار منفذ الصفقات"""
        try:
            logger.info("اختبار منفذ الصفقات")
            
            # الحصول على منفذ الصفقات
            trade_executor = global_trade_executor.get_executor(self.test_user_id)
            
            if not trade_executor:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على منفذ الصفقات',
                    'details': {}
                }
            
            # اختبار تنفيذ الصفقات
            test_trade = {
                'symbol': 'BTCUSDT',
                'action': 'buy',
                'quantity': 0.001,
                'price': 50000.0
            }
            
            execution_result = await trade_executor.execute_trade(test_trade)
            
            # اختبار إحصائيات التنفيذ
            execution_stats = trade_executor.get_execution_statistics()
            
            # اختبار تحديث إعدادات التنفيذ
            new_config = {
                'max_retries': 3,
                'retry_delay': 1.0,
                'timeout': 30.0
            }
            
            config_update_result = trade_executor.update_execution_config(new_config)
            
            return {
                'success': True,
                'message': 'تم اختبار منفذ الصفقات بنجاح',
                'details': {
                    'execution_result': execution_result,
                    'execution_statistics': execution_stats,
                    'config_update_result': config_update_result
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار منفذ الصفقات: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار منفذ الصفقات: {e}',
                'details': {}
            }
    
    async def _test_portfolio_manager(self) -> Dict[str, Any]:
        """اختبار مدير المحفظة"""
        try:
            logger.info("اختبار مدير المحفظة")
            
            # الحصول على مدير المحفظة
            portfolio_manager = global_portfolio_manager.get_portfolio_manager(
                self.test_user_id, self.test_initial_capital
            )
            
            if not portfolio_manager:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على مدير المحفظة',
                    'details': {}
                }
            
            # اختبار إضافة أصول
            test_assets = [
                {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'quantity': 0.001, 'price': 50000.0},
                {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'quantity': 0.01, 'price': 3000.0}
            ]
            
            added_assets = []
            for asset in test_assets:
                add_result = portfolio_manager.add_asset(
                    asset['symbol'], asset['name'], asset['quantity'], 
                    asset['price'], asset['price']
                )
                added_assets.append(add_result)
            
            # اختبار تحديث أسعار الأصول
            price_updates = [
                {'symbol': 'BTCUSDT', 'new_price': 51000.0},
                {'symbol': 'ETHUSDT', 'new_price': 3100.0}
            ]
            
            price_update_results = []
            for update in price_updates:
                update_result = portfolio_manager.update_asset_price(
                    update['symbol'], update['new_price']
                )
                price_update_results.append(update_result)
            
            # اختبار إعادة التوازن
            rebalancing_signals = portfolio_manager.generate_rebalancing_signals()
            rebalancing_result = portfolio_manager.rebalance_portfolio(rebalancing_signals)
            
            # اختبار تقرير المحفظة
            portfolio_report = portfolio_manager.get_portfolio_report()
            
            return {
                'success': True,
                'message': 'تم اختبار مدير المحفظة بنجاح',
                'details': {
                    'added_assets': added_assets,
                    'price_update_results': price_update_results,
                    'rebalancing_signals': len(rebalancing_signals),
                    'rebalancing_result': rebalancing_result,
                    'portfolio_report': portfolio_report
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار مدير المحفظة: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار مدير المحفظة: {e}',
                'details': {}
            }
    
    async def _test_optimizer(self) -> Dict[str, Any]:
        """اختبار المحسن"""
        try:
            logger.info("اختبار المحسن")
            
            # الحصول على المحسن
            optimizer = global_optimization_manager.get_optimizer(self.test_user_id)
            
            if not optimizer:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على المحسن',
                    'details': {}
                }
            
            # اختبار التحسين
            optimization_result = await optimizer.optimize_bot(
                target=optimizer.OptimizationTarget.PERFORMANCE,
                method=optimizer.OptimizationMethod.GRID_SEARCH
            )
            
            # اختبار تقرير التحسين
            optimization_report = optimizer.get_optimization_report()
            
            # اختبار تحديث إعدادات التحسين
            new_settings = {
                'optimization_enabled': True,
                'auto_optimization': False,
                'optimization_frequency': timedelta(days=7)
            }
            
            settings_update_result = optimizer.update_optimization_settings(new_settings)
            
            return {
                'success': True,
                'message': 'تم اختبار المحسن بنجاح',
                'details': {
                    'optimization_result': optimization_result,
                    'optimization_report': optimization_report,
                    'settings_update_result': settings_update_result
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار المحسن: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار المحسن: {e}',
                'details': {}
            }
    
    async def _test_enhanced_bot(self) -> Dict[str, Any]:
        """اختبار البوت المحسن"""
        try:
            logger.info("اختبار البوت المحسن")
            
            # الحصول على البوت المحسن
            enhanced_bot = enhanced_bot_manager.get_bot(self.test_user_id, self.test_initial_capital)
            
            if not enhanced_bot:
                return {
                    'success': False,
                    'message': 'فشل في الحصول على البوت المحسن',
                    'details': {}
                }
            
            # اختبار بدء البوت
            start_result = await enhanced_bot.start()
            
            if not start_result:
                return {
                    'success': False,
                    'message': 'فشل في بدء البوت المحسن',
                    'details': {}
                }
            
            # اختبار معالجة الإشارات
            signal_results = []
            for signal in self.test_signals:
                signal_result = await enhanced_bot.process_signal(signal)
                signal_results.append(signal_result)
            
            # اختبار حالة البوت
            bot_status = enhanced_bot.get_bot_status()
            
            # اختبار تحديث الإعدادات
            new_config = {
                'risk_tolerance': 0.7,
                'max_positions': 15,
                'auto_rebalancing': True
            }
            
            config_update_result = enhanced_bot.update_configuration(new_config)
            
            # اختبار إيقاف البوت
            stop_result = await enhanced_bot.stop()
            
            return {
                'success': True,
                'message': 'تم اختبار البوت المحسن بنجاح',
                'details': {
                    'start_result': start_result,
                    'signal_results': signal_results,
                    'bot_status': bot_status,
                    'config_update_result': config_update_result,
                    'stop_result': stop_result
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار البوت المحسن: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار البوت المحسن: {e}',
                'details': {}
            }
    
    async def _test_integrated_system(self) -> Dict[str, Any]:
        """اختبار النظام المتكامل"""
        try:
            logger.info("اختبار النظام المتكامل")
            
            # اختبار حالة النظام
            system_status = integrated_system.get_system_status()
            
            # اختبار إحصائيات النظام
            system_statistics = integrated_system.get_system_statistics()
            
            # اختبار بدء بوت المستخدم
            start_bot_result = await integrated_system.start_user_bot(
                self.test_user_id, self.test_initial_capital
            )
            
            # اختبار معالجة الإشارات
            signal_processing_results = []
            for signal in self.test_signals:
                signal_result = await integrated_system.process_signal(self.test_user_id, signal)
                signal_processing_results.append(signal_result)
            
            # اختبار حالة بوت المستخدم
            user_bot_status = integrated_system.get_user_bot_status(self.test_user_id)
            
            # اختبار إيقاف بوت المستخدم
            stop_bot_result = await integrated_system.stop_user_bot(self.test_user_id)
            
            return {
                'success': True,
                'message': 'تم اختبار النظام المتكامل بنجاح',
                'details': {
                    'system_status': system_status,
                    'system_statistics': system_statistics,
                    'start_bot_result': start_bot_result,
                    'signal_processing_results': signal_processing_results,
                    'user_bot_status': user_bot_status,
                    'stop_bot_result': stop_bot_result
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار النظام المتكامل: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار النظام المتكامل: {e}',
                'details': {}
            }
    
    async def _test_signal_processing(self) -> Dict[str, Any]:
        """اختبار معالجة الإشارات"""
        try:
            logger.info("اختبار معالجة الإشارات")
            
            # اختبار معالجة الإشارات المختلفة
            test_signals = [
                {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_001'},
                {'signal': 'sell', 'symbol': 'ETHUSDT', 'id': 'TV_002'},
                {'signal': 'close', 'symbol': 'ADAUSDT', 'id': 'TV_003'},
                {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_004', 'percentage': 50}
            ]
            
            processing_results = []
            
            for signal in test_signals:
                # معالجة الإشارة
                result = await integrated_system.process_signal(self.test_user_id, signal)
                processing_results.append(result)
                
                # انتظار قصير بين الإشارات
                await asyncio.sleep(0.1)
            
            # تحليل النتائج
            successful_signals = sum(1 for result in processing_results if result.get('success', False))
            total_signals = len(processing_results)
            success_rate = (successful_signals / total_signals) * 100 if total_signals > 0 else 0
            
            return {
                'success': True,
                'message': 'تم اختبار معالجة الإشارات بنجاح',
                'details': {
                    'total_signals': total_signals,
                    'successful_signals': successful_signals,
                    'success_rate': success_rate,
                    'processing_results': processing_results
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار معالجة الإشارات: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار معالجة الإشارات: {e}',
                'details': {}
            }
    
    async def _test_performance_analysis(self) -> Dict[str, Any]:
        """اختبار تحليل الأداء"""
        try:
            logger.info("اختبار تحليل الأداء")
            
            # جمع مقاييس الأداء من جميع المكونات
            performance_metrics = {
                'risk_manager': global_risk_manager.get_global_statistics(),
                'signal_manager': global_signal_manager.get_global_statistics(),
                'trade_executor': global_trade_executor.get_global_statistics(),
                'portfolio_manager': global_portfolio_manager.get_global_statistics(),
                'optimization_manager': global_optimization_manager.get_global_statistics(),
                'bot_manager': enhanced_bot_manager.get_global_statistics(),
                'integrated_system': integrated_system.get_system_statistics()
            }
            
            # تحليل الأداء
            performance_analysis = {
                'total_users': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('total_users', 0),
                'active_users': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('active_users', 0),
                'total_trades': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('total_trades', 0),
                'successful_trades': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('successful_trades', 0),
                'average_response_time': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('average_response_time', 0.0),
                'error_rate': performance_metrics['integrated_system'].get('system_overview', {}).get('metrics', {}).get('error_rate', 0.0)
            }
            
            # حساب معدل النجاح
            if performance_analysis['total_trades'] > 0:
                performance_analysis['success_rate'] = (
                    performance_analysis['successful_trades'] / performance_analysis['total_trades']
                ) * 100
            else:
                performance_analysis['success_rate'] = 0.0
            
            return {
                'success': True,
                'message': 'تم اختبار تحليل الأداء بنجاح',
                'details': {
                    'performance_metrics': performance_metrics,
                    'performance_analysis': performance_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في اختبار تحليل الأداء: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار تحليل الأداء: {e}',
                'details': {}
            }
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """توليد التوصيات"""
        try:
            recommendations = []
            
            # تحليل النتائج وتوليد التوصيات
            for test_name, result in test_results.items():
                if not result.get('success', False):
                    recommendations.append(f"تحسين {test_name}: {result.get('message', '')}")
            
            # توصيات عامة
            if not recommendations:
                recommendations.append("جميع الاختبارات نجحت - النظام يعمل بشكل ممتاز")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"خطأ في توليد التوصيات: {e}")
            return ["خطأ في توليد التوصيات"]
    
    def save_test_report(self, filename: str = None) -> str:
        """حفظ تقرير الاختبار"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"enhanced_system_test_report_{timestamp}.json"
            
            # حفظ التقرير
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"تم حفظ تقرير الاختبار في {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"خطأ في حفظ تقرير الاختبار: {e}")
            return ""
    
    def print_test_summary(self):
        """طباعة ملخص الاختبار"""
        try:
            if not self.test_results:
                print("لا توجد نتائج اختبار متاحة")
                return
            
            summary = self.test_results.get('test_summary', {})
            recommendations = self.test_results.get('recommendations', [])
            
            print("=" * 80)
            print("ملخص اختبار النظام المحسن")
            print("=" * 80)
            print(f"إجمالي الاختبارات: {summary.get('total_tests', 0)}")
            print(f"الاختبارات الناجحة: {summary.get('passed_tests', 0)}")
            print(f"الاختبارات الفاشلة: {summary.get('failed_tests', 0)}")
            print(f"معدل النجاح: {summary.get('success_rate', 0):.2f}%")
            print(f"مدة الاختبار: {summary.get('test_duration', 0):.2f} ثانية")
            print("=" * 80)
            
            if recommendations:
                print("التوصيات:")
                for i, recommendation in enumerate(recommendations, 1):
                    print(f"{i}. {recommendation}")
            
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"خطأ في طباعة ملخص الاختبار: {e}")


# دالة الاختبار الرئيسية
async def run_enhanced_system_test() -> Dict[str, Any]:
    """تشغيل اختبار النظام المحسن"""
    try:
        # إنشاء اختبار النظام المحسن
        tester = EnhancedSystemTester()
        
        # تشغيل الاختبار الشامل
        test_report = await tester.run_comprehensive_test()
        
        # طباعة ملخص الاختبار
        tester.print_test_summary()
        
        # حفظ تقرير الاختبار
        report_filename = tester.save_test_report()
        
        print(f"تم حفظ تقرير الاختبار في: {report_filename}")
        
        return test_report
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل اختبار النظام المحسن: {e}")
        return {
            'test_summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0,
                'test_duration': 0,
                'error': str(e)
            },
            'test_results': {},
            'recommendations': [f'خطأ في تشغيل الاختبار: {e}'],
            'timestamp': datetime.now().isoformat()
        }


# تشغيل الاختبار إذا تم تنفيذ الملف مباشرة
if __name__ == "__main__":
    # تشغيل الاختبار
    asyncio.run(run_enhanced_system_test())
