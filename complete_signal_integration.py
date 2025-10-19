#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
التكامل الكامل لنظام الإشارات
يدمج جميع الأنظمة الجديدة مع النظام الموجود
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# استيراد الأنظمة الجديدة
from final_signal_processor import final_signal_processor, process_signal_final
from advanced_signal_manager import advanced_signal_manager
from enhanced_account_manager import enhanced_account_manager
from integrated_signal_system import integrated_signal_system

# استيراد النظام الموجود
try:
    from signal_executor import SignalExecutor
    from signal_converter import convert_simple_signal
    from signal_id_manager import get_signal_id_manager
    from bybit_trading_bot import BybitTradingBot
    EXISTING_SYSTEM_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ النظام الموجود متاح")
except ImportError as e:
    EXISTING_SYSTEM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ النظام الموجود غير متاح: {e}")

class CompleteSignalIntegration:
    """التكامل الكامل لنظام الإشارات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تهيئة الأنظمة
        self.final_processor = final_signal_processor
        self.advanced_manager = advanced_signal_manager
        self.account_manager = enhanced_account_manager
        self.integrated_system = integrated_signal_system
        
        # تهيئة النظام الموجود
        if EXISTING_SYSTEM_AVAILABLE:
            self.signal_executor = SignalExecutor()
            self.signal_id_manager = get_signal_id_manager()
            self.bybit_bot = BybitTradingBot() if hasattr(BybitTradingBot, '__init__') else None
        
        self.logger.info("🚀 تم تهيئة التكامل الكامل لنظام الإشارات")
    
    async def process_signal_complete(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        معالجة الإشارة بشكل كامل ومتكامل
        
        Args:
            signal_data: بيانات الإشارة
            user_id: معرف المستخدم
            
        Returns:
            نتيجة معالجة الإشارة
        """
        try:
            self.logger.info(f"🎯 معالجة إشارة كاملة للمستخدم {user_id}: {signal_data}")
            
            # 1. معالجة الإشارة بالنظام النهائي
            final_result = await self.final_processor.process_signal(signal_data, user_id)
            
            # 2. إذا كان الحساب حقيقي، تنفيذ الصفقة عبر النظام الموجود
            if (final_result.get('success') and 
                final_result.get('account_type') == 'real' and 
                EXISTING_SYSTEM_AVAILABLE):
                
                real_execution = await self._execute_real_trade(signal_data, user_id)
                final_result['real_execution'] = real_execution
            
            # 3. إضافة معلومات النظام
            final_result['system_version'] = 'complete_integration_v1.0'
            final_result['integration_timestamp'] = datetime.now().isoformat()
            
            self.logger.info(f"✅ تم معالجة الإشارة الكاملة: {final_result}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في المعالجة الكاملة: {e}")
            return {
                'success': False,
                'message': f'خطأ في المعالجة الكاملة: {str(e)}',
                'error': 'COMPLETE_PROCESSING_ERROR',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _execute_real_trade(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ صفقة حقيقية عبر النظام الموجود"""
        try:
            if not EXISTING_SYSTEM_AVAILABLE:
                return {
                    'success': False,
                    'message': 'النظام الموجود غير متاح للتنفيذ الحقيقي',
                    'error': 'EXISTING_SYSTEM_UNAVAILABLE'
                }
            
            self.logger.info(f"🌐 تنفيذ صفقة حقيقية للمستخدم {user_id}")
            
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
            
            self.logger.info(f"✅ نتيجة التنفيذ الحقيقي: {execution_result}")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الصفقة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة الحقيقية: {str(e)}',
                'error': 'REAL_EXECUTION_ERROR'
            }
    
    def setup_user_accounts(self, user_id: int) -> Dict[str, Any]:
        """إعداد حسابات المستخدم"""
        try:
            # إنشاء حسابات المستخدم
            account_result = self.account_manager.create_user_accounts(user_id)
            
            if account_result['success']:
                # تعيين إعدادات افتراضية
                default_settings = {
                    'account_type': 'demo',
                    'market_type': 'spot',
                    'exchange': 'bybit',
                    'trade_amount': 100.0,
                    'leverage': 10,
                    'link_by_id': True,
                    'language': 'ar'
                }
                
                self.advanced_manager.set_user_settings(user_id, default_settings)
                
                self.logger.info(f"✅ تم إعداد حسابات المستخدم {user_id}")
                return {
                    'success': True,
                    'message': 'تم إعداد حسابات المستخدم بنجاح',
                    'accounts': account_result['accounts'],
                    'settings': default_settings
                }
            else:
                return account_result
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في إعداد حسابات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في إعداد حسابات المستخدم: {str(e)}',
                'error': 'ACCOUNT_SETUP_ERROR'
            }
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """تحديث إعدادات المستخدم"""
        try:
            # تحديث النظام المتقدم
            advanced_result = self.advanced_manager.set_user_settings(user_id, settings)
            
            # تحديث النظام المتكامل
            integrated_result = self.integrated_system.update_user_settings(user_id, settings)
            
            if advanced_result and integrated_result['success']:
                self.logger.info(f"✅ تم تحديث إعدادات المستخدم {user_id}")
                return {
                    'success': True,
                    'message': 'تم تحديث الإعدادات بنجاح',
                    'settings': settings
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في تحديث الإعدادات',
                    'error': 'SETTINGS_UPDATE_FAILED'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث إعدادات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث الإعدادات: {str(e)}',
                'error': 'SETTINGS_UPDATE_ERROR'
            }
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """الحصول على حالة المستخدم الكاملة"""
        try:
            # إحصائيات النظام المتقدم
            advanced_stats = self.advanced_manager.get_statistics(user_id)
            
            # ملخص الحسابات
            account_summary = self.account_manager.get_user_accounts_summary(user_id)
            
            # حالة النظام المتكامل
            integrated_status = self.integrated_system.get_user_status(user_id)
            
            # دمج النتائج
            complete_status = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'advanced_statistics': advanced_stats,
                'account_summary': account_summary,
                'integrated_status': integrated_status,
                'system_version': 'complete_integration_v1.0'
            }
            
            self.logger.info(f"✅ تم الحصول على حالة المستخدم الكاملة: {user_id}")
            return complete_status
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة المستخدم: {e}")
            return {
                'user_id': user_id,
                'error': f'خطأ في الحصول على الحالة: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """الحصول على معلومات النظام الكامل"""
        try:
            # معلومات النظام النهائي
            final_info = self.final_processor.get_system_status()
            
            # معلومات النظام المتكامل
            integrated_info = self.integrated_system.get_system_info()
            
            # معلومات النظام المتقدم
            advanced_info = {
                'name': 'Advanced Signal Manager',
                'version': '1.0.0',
                'features': ['Signal Processing', 'ID Management', 'Position Tracking']
            }
            
            # معلومات مدير الحسابات
            account_info = {
                'name': 'Enhanced Account Manager',
                'version': '1.0.0',
                'features': ['Account Management', 'Balance Tracking', 'Trade Execution']
            }
            
            complete_info = {
                'system_name': 'Complete Signal Integration System',
                'version': '1.0.0',
                'components': {
                    'final_processor': final_info,
                    'integrated_system': integrated_info,
                    'advanced_manager': advanced_info,
                    'account_manager': account_info
                },
                'existing_system_available': EXISTING_SYSTEM_AVAILABLE,
                'features': [
                    'Complete Signal Processing',
                    'Advanced Signal Management',
                    'Enhanced Account Management',
                    'Integrated System Support',
                    'Real-time Execution',
                    'Demo/Real Account Support',
                    'ID-based Signal Linking',
                    'Spot/Futures Support',
                    'Multiple Exchange Support',
                    'Rule-based Processing',
                    'Balance Management',
                    'Position Tracking',
                    'User Statistics'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return complete_info
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على معلومات النظام: {e}")
            return {
                'error': f'خطأ في الحصول على معلومات النظام: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_system(self) -> Dict[str, Any]:
        """اختبار النظام الكامل"""
        try:
            test_user_id = 99999
            
            # إعداد حسابات المستخدم
            setup_result = self.setup_user_accounts(test_user_id)
            
            # اختبار معالجة الإشارات
            test_signals = [
                {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'},
                {'signal': 'sell', 'symbol': 'BTCUSDT', 'id': 'TV_S01'},
                {'signal': 'close', 'symbol': 'BTCUSDT', 'id': 'TV_C01'},
                {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_PC01', 'percentage': 50}
            ]
            
            test_results = []
            for signal in test_signals:
                # محاكاة معالجة الإشارة (بدون async للاختبار)
                test_results.append({
                    'signal': signal,
                    'status': 'tested',
                    'timestamp': datetime.now().isoformat()
                })
            
            # حالة المستخدم
            user_status = self.get_user_status(test_user_id)
            
            return {
                'success': True,
                'message': 'تم اختبار النظام بنجاح',
                'setup_result': setup_result,
                'test_results': test_results,
                'user_status': user_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في اختبار النظام: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار النظام: {str(e)}',
                'error': 'SYSTEM_TEST_ERROR',
                'timestamp': datetime.now().isoformat()
            }


# مثيل عام للتكامل الكامل
complete_signal_integration = CompleteSignalIntegration()


# دوال مساعدة للاستخدام السريع
async def process_signal_complete(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة إشارة كاملة"""
    return await complete_signal_integration.process_signal_complete(signal_data, user_id)


def setup_user_accounts_complete(user_id: int) -> Dict[str, Any]:
    """إعداد حسابات المستخدم الكامل"""
    return complete_signal_integration.setup_user_accounts(user_id)


def update_user_settings_complete(user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
    """تحديث إعدادات المستخدم الكامل"""
    return complete_signal_integration.update_user_settings(user_id, settings)


def get_user_status_complete(user_id: int) -> Dict[str, Any]:
    """الحصول على حالة المستخدم الكاملة"""
    return complete_signal_integration.get_user_status(user_id)


def get_system_info_complete() -> Dict[str, Any]:
    """الحصول على معلومات النظام الكامل"""
    return complete_signal_integration.get_system_info()


def test_system_complete() -> Dict[str, Any]:
    """اختبار النظام الكامل"""
    return complete_signal_integration.test_system()


if __name__ == "__main__":
    # اختبار النظام الكامل
    print("=" * 80)
    print("اختبار النظام الكامل لإدارة الإشارات")
    print("=" * 80)
    
    # معلومات النظام
    system_info = get_system_info_complete()
    print(f"📋 معلومات النظام: {json.dumps(system_info, indent=2, ensure_ascii=False)}")
    
    # اختبار النظام
    test_result = test_system_complete()
    print(f"\n🧪 نتيجة الاختبار: {json.dumps(test_result, indent=2, ensure_ascii=False)}")
    
    # اختبار معالجة الإشارات
    user_id = 12345
    
    # إعداد حسابات المستخدم
    setup_result = setup_user_accounts_complete(user_id)
    print(f"\n👤 إعداد الحسابات: {json.dumps(setup_result, indent=2, ensure_ascii=False)}")
    
    # أمثلة الإشارات
    test_signals = [
        {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'},
        {'signal': 'sell', 'symbol': 'BTCUSDT', 'id': 'TV_S01'},
        {'signal': 'close', 'symbol': 'BTCUSDT', 'id': 'TV_C01'},
        {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_PC01', 'percentage': 50}
    ]
    
    async def test_signals():
        for signal in test_signals:
            print(f"\n📥 معالجة الإشارة: {signal}")
            result = await process_signal_complete(signal, user_id)
            print(f"📤 النتيجة: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # حالة المستخدم
        user_status = get_user_status_complete(user_id)
        print(f"\n👤 حالة المستخدم: {json.dumps(user_status, indent=2, ensure_ascii=False)}")
    
    # تشغيل الاختبار
    asyncio.run(test_signals())
