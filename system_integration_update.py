#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث النظام الموجود لدمج النظام الجديد
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any

# استيراد النظام الجديد
from complete_signal_integration import complete_signal_integration, process_signal_complete

# استيراد النظام الموجود
try:
    from bybit_trading_bot import BybitTradingBot
    from signal_executor import SignalExecutor
    from signal_converter import convert_simple_signal
    EXISTING_SYSTEM_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ النظام الموجود متاح للتحديث")
except ImportError as e:
    EXISTING_SYSTEM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ النظام الموجود غير متاح: {e}")

class SystemIntegrationUpdate:
    """تحديث النظام الموجود لدمج النظام الجديد"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.complete_integration = complete_signal_integration
        
        # تهيئة النظام الموجود
        if EXISTING_SYSTEM_AVAILABLE:
            self.bybit_bot = BybitTradingBot()
            self.signal_executor = SignalExecutor()
        
        self.logger.info("🚀 تم تهيئة تحديث النظام")
    
    def update_bybit_bot(self) -> Dict[str, Any]:
        """تحديث بوت Bybit لدمج النظام الجديد"""
        try:
            if not EXISTING_SYSTEM_AVAILABLE:
                return {
                    'success': False,
                    'message': 'النظام الموجود غير متاح للتحديث',
                    'error': 'EXISTING_SYSTEM_UNAVAILABLE'
                }
            
            # إضافة دعم للنظام الجديد في بوت Bybit
            if hasattr(self.bybit_bot, 'process_signal'):
                # تحديث دالة معالجة الإشارات
                original_process_signal = self.bybit_bot.process_signal
                
                async def enhanced_process_signal(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
                    """معالجة إشارة محسنة مع النظام الجديد"""
                    try:
                        # استخدام النظام الجديد للمعالجة
                        result = await process_signal_complete(signal_data, user_id)
                        
                        # إذا كان الحساب حقيقي، تنفيذ الصفقة عبر النظام الموجود
                        if (result.get('success') and 
                            result.get('account_type') == 'real' and 
                            result.get('execution_type') == 'real'):
                            
                            # تنفيذ الصفقة عبر النظام الموجود
                            real_execution = await self._execute_via_existing_system(signal_data, user_id)
                            result['real_execution'] = real_execution
                        
                        return result
                        
                    except Exception as e:
                        self.logger.error(f"❌ خطأ في المعالجة المحسنة: {e}")
                        # العودة للنظام الأصلي في حالة الخطأ
                        return await original_process_signal(signal_data, user_id)
                
                # استبدال الدالة
                self.bybit_bot.process_signal = enhanced_process_signal
                
                self.logger.info("✅ تم تحديث بوت Bybit بنجاح")
                return {
                    'success': True,
                    'message': 'تم تحديث بوت Bybit بنجاح',
                    'enhancements': [
                        'Enhanced Signal Processing',
                        'ID-based Signal Linking',
                        'Account Type Support',
                        'Market Type Support',
                        'Real-time Execution',
                        'Demo/Real Account Support'
                    ]
                }
            else:
                return {
                    'success': False,
                    'message': 'بوت Bybit لا يحتوي على دالة process_signal',
                    'error': 'MISSING_PROCESS_SIGNAL'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث بوت Bybit: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث بوت Bybit: {str(e)}',
                'error': 'BYBIT_UPDATE_ERROR'
            }
    
    async def _execute_via_existing_system(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ الصفقة عبر النظام الموجود"""
        try:
            # تحويل الإشارة إلى التنسيق المطلوب
            converted_signal = convert_simple_signal(signal_data, {})
            
            if not converted_signal:
                return {
                    'success': False,
                    'message': 'فشل في تحويل الإشارة',
                    'error': 'SIGNAL_CONVERSION_FAILED'
                }
            
            # تنفيذ الصفقة
            execution_result = await self.signal_executor.execute_signal(user_id, converted_signal, {})
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التنفيذ عبر النظام الموجود: {e}")
            return {
                'success': False,
                'message': f'خطأ في التنفيذ: {str(e)}',
                'error': 'EXECUTION_ERROR'
            }
    
    def update_signal_executor(self) -> Dict[str, Any]:
        """تحديث منفذ الإشارات لدمج النظام الجديد"""
        try:
            if not EXISTING_SYSTEM_AVAILABLE:
                return {
                    'success': False,
                    'message': 'النظام الموجود غير متاح للتحديث',
                    'error': 'EXISTING_SYSTEM_UNAVAILABLE'
                }
            
            # إضافة دعم للنظام الجديد في منفذ الإشارات
            if hasattr(self.signal_executor, 'execute_signal'):
                # تحديث دالة تنفيذ الإشارات
                original_execute_signal = self.signal_executor.execute_signal
                
                async def enhanced_execute_signal(user_id: int, signal_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
                    """تنفيذ إشارة محسن مع النظام الجديد"""
                    try:
                        # استخدام النظام الجديد للمعالجة
                        result = await process_signal_complete(signal_data, user_id)
                        
                        # إذا كان الحساب حقيقي، تنفيذ الصفقة عبر النظام الموجود
                        if (result.get('success') and 
                            result.get('account_type') == 'real' and 
                            result.get('execution_type') == 'real'):
                            
                            # تنفيذ الصفقة عبر النظام الموجود
                            real_execution = await original_execute_signal(user_id, signal_data, user_data)
                            result['real_execution'] = real_execution
                        
                        return result
                        
                    except Exception as e:
                        self.logger.error(f"❌ خطأ في التنفيذ المحسن: {e}")
                        # العودة للنظام الأصلي في حالة الخطأ
                        return await original_execute_signal(user_id, signal_data, user_data)
                
                # استبدال الدالة
                self.signal_executor.execute_signal = enhanced_execute_signal
                
                self.logger.info("✅ تم تحديث منفذ الإشارات بنجاح")
                return {
                    'success': True,
                    'message': 'تم تحديث منفذ الإشارات بنجاح',
                    'enhancements': [
                        'Enhanced Signal Execution',
                        'ID-based Signal Processing',
                        'Account Type Support',
                        'Market Type Support',
                        'Real-time Execution',
                        'Demo/Real Account Support'
                    ]
                }
            else:
                return {
                    'success': False,
                    'message': 'منفذ الإشارات لا يحتوي على دالة execute_signal',
                    'error': 'MISSING_EXECUTE_SIGNAL'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث منفذ الإشارات: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث منفذ الإشارات: {str(e)}',
                'error': 'EXECUTOR_UPDATE_ERROR'
            }
    
    def update_signal_converter(self) -> Dict[str, Any]:
        """تحديث محول الإشارات لدمج النظام الجديد"""
        try:
            if not EXISTING_SYSTEM_AVAILABLE:
                return {
                    'success': False,
                    'message': 'النظام الموجود غير متاح للتحديث',
                    'error': 'EXISTING_SYSTEM_UNAVAILABLE'
                }
            
            # إضافة دعم للنظام الجديد في محول الإشارات
            if hasattr(convert_simple_signal, '__call__'):
                # تحديث دالة تحويل الإشارات
                original_convert_signal = convert_simple_signal
                
                def enhanced_convert_signal(signal_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
                    """تحويل إشارة محسن مع النظام الجديد"""
                    try:
                        # استخدام النظام الجديد للمعالجة
                        if not user_settings:
                            user_settings = {
                                'account_type': 'demo',
                                'market_type': 'spot',
                                'exchange': 'bybit',
                                'trade_amount': 100.0,
                                'leverage': 10,
                                'link_by_id': True
                            }
                        
                        # تحويل الإشارة بالنظام الأصلي
                        converted_signal = original_convert_signal(signal_data, user_settings)
                        
                        if converted_signal:
                            # إضافة معلومات النظام الجديد
                            converted_signal['enhanced_processing'] = True
                            converted_signal['system_version'] = 'enhanced_v1.0'
                            converted_signal['link_by_id'] = user_settings.get('link_by_id', True)
                        
                        return converted_signal
                        
                    except Exception as e:
                        self.logger.error(f"❌ خطأ في التحويل المحسن: {e}")
                        # العودة للنظام الأصلي في حالة الخطأ
                        return original_convert_signal(signal_data, user_settings)
                
                # استبدال الدالة
                convert_simple_signal = enhanced_convert_signal
                
                self.logger.info("✅ تم تحديث محول الإشارات بنجاح")
                return {
                    'success': True,
                    'message': 'تم تحديث محول الإشارات بنجاح',
                    'enhancements': [
                        'Enhanced Signal Conversion',
                        'ID-based Signal Processing',
                        'Account Type Support',
                        'Market Type Support',
                        'Real-time Conversion',
                        'Demo/Real Account Support'
                    ]
                }
            else:
                return {
                    'success': False,
                    'message': 'محول الإشارات غير متاح',
                    'error': 'CONVERTER_NOT_AVAILABLE'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث محول الإشارات: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث محول الإشارات: {str(e)}',
                'error': 'CONVERTER_UPDATE_ERROR'
            }
    
    def update_all_systems(self) -> Dict[str, Any]:
        """تحديث جميع الأنظمة"""
        try:
            update_results = {}
            
            # تحديث بوت Bybit
            bybit_result = self.update_bybit_bot()
            update_results['bybit_bot'] = bybit_result
            
            # تحديث منفذ الإشارات
            executor_result = self.update_signal_executor()
            update_results['signal_executor'] = executor_result
            
            # تحديث محول الإشارات
            converter_result = self.update_signal_converter()
            update_results['signal_converter'] = converter_result
            
            # تحديد نجاح التحديث العام
            all_successful = all(
                result.get('success', False) 
                for result in update_results.values()
            )
            
            if all_successful:
                self.logger.info("✅ تم تحديث جميع الأنظمة بنجاح")
                return {
                    'success': True,
                    'message': 'تم تحديث جميع الأنظمة بنجاح',
                    'update_results': update_results,
                    'enhancements': [
                        'Complete Signal Processing Integration',
                        'ID-based Signal Linking',
                        'Account Type Support (Demo/Real)',
                        'Market Type Support (Spot/Futures)',
                        'Exchange Support (Bybit/MEXC)',
                        'Real-time Execution',
                        'Enhanced Signal Management',
                        'Position Tracking',
                        'User Statistics',
                        'Balance Management'
                    ]
                }
            else:
                self.logger.warning("⚠️ فشل في تحديث بعض الأنظمة")
                return {
                    'success': False,
                    'message': 'فشل في تحديث بعض الأنظمة',
                    'update_results': update_results,
                    'error': 'PARTIAL_UPDATE_FAILED'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث جميع الأنظمة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث جميع الأنظمة: {str(e)}',
                'error': 'COMPLETE_UPDATE_ERROR'
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        try:
            return {
                'integration_name': 'System Integration Update',
                'version': '1.0.0',
                'status': 'active',
                'existing_system_available': EXISTING_SYSTEM_AVAILABLE,
                'complete_integration_available': True,
                'features': [
                    'Bybit Bot Enhancement',
                    'Signal Executor Enhancement',
                    'Signal Converter Enhancement',
                    'Complete System Integration',
                    'ID-based Signal Processing',
                    'Account Type Support',
                    'Market Type Support',
                    'Exchange Support',
                    'Real-time Execution',
                    'Demo/Real Account Support'
                ],
                'components': {
                    'bybit_bot': hasattr(self, 'bybit_bot') and self.bybit_bot is not None,
                    'signal_executor': hasattr(self, 'signal_executor') and self.signal_executor is not None,
                    'complete_integration': hasattr(self, 'complete_integration') and self.complete_integration is not None
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة التكامل: {e}")
            return {
                'error': f'خطأ في الحصول على حالة التكامل: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


# مثيل عام لتحديث النظام
system_integration_update = SystemIntegrationUpdate()


# دوال مساعدة للاستخدام السريع
def update_all_systems() -> Dict[str, Any]:
    """تحديث جميع الأنظمة"""
    return system_integration_update.update_all_systems()


def update_bybit_bot() -> Dict[str, Any]:
    """تحديث بوت Bybit"""
    return system_integration_update.update_bybit_bot()


def update_signal_executor() -> Dict[str, Any]:
    """تحديث منفذ الإشارات"""
    return system_integration_update.update_signal_executor()


def update_signal_converter() -> Dict[str, Any]:
    """تحديث محول الإشارات"""
    return system_integration_update.update_signal_converter()


def get_integration_status() -> Dict[str, Any]:
    """الحصول على حالة التكامل"""
    return system_integration_update.get_integration_status()


if __name__ == "__main__":
    # اختبار تحديث النظام
    print("=" * 80)
    print("اختبار تحديث النظام")
    print("=" * 80)
    
    # حالة التكامل
    integration_status = get_integration_status()
    print(f"📋 حالة التكامل: {integration_status}")
    
    # تحديث جميع الأنظمة
    update_result = update_all_systems()
    print(f"\n🔄 نتيجة التحديث: {update_result}")
    
    # اختبار النظام المحدث
    if update_result['success']:
        print("\n✅ تم تحديث النظام بنجاح!")
        print("🎯 النظام الآن يدعم:")
        for enhancement in update_result['enhancements']:
            print(f"   • {enhancement}")
    else:
        print("\n❌ فشل في تحديث النظام")
        print("🔍 تفاصيل الأخطاء:")
        for component, result in update_result['update_results'].items():
            if not result.get('success', False):
                print(f"   • {component}: {result.get('message', 'خطأ غير معروف')}")
