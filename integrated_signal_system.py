#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النظام المتكامل لإدارة الإشارات
يدمج النظام الجديد مع النظام الموجود
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# استيراد النظام الجديد
from advanced_signal_manager import advanced_signal_manager, process_signal, set_user_settings

# استيراد النظام الموجود
try:
    from signal_executor import SignalExecutor
    from signal_converter import convert_simple_signal
    from signal_id_manager import get_signal_id_manager
    EXISTING_SYSTEM_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ النظام الموجود متاح")
except ImportError as e:
    EXISTING_SYSTEM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ النظام الموجود غير متاح: {e}")

# استيراد إدارة المستخدمين
try:
    from user_manager import user_manager
    USER_MANAGER_AVAILABLE = True
except ImportError as e:
    USER_MANAGER_AVAILABLE = False
    logger.warning(f"⚠️ مدير المستخدمين غير متاح: {e}")

class IntegratedSignalSystem:
    """النظام المتكامل لإدارة الإشارات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.signal_executor = SignalExecutor() if EXISTING_SYSTEM_AVAILABLE else None
        self.signal_id_manager = get_signal_id_manager() if EXISTING_SYSTEM_AVAILABLE else None
        
        self.logger.info("🚀 تم تهيئة النظام المتكامل لإدارة الإشارات")
    
    async def process_signal_complete(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        معالجة الإشارة بشكل متكامل
        
        Args:
            signal_data: بيانات الإشارة
            user_id: معرف المستخدم
            
        Returns:
            نتيجة معالجة الإشارة
        """
        try:
            self.logger.info(f"🔄 معالجة إشارة متكاملة للمستخدم {user_id}: {signal_data}")
            
            # 1. التحقق من صحة الإشارة
            if not self._validate_signal_format(signal_data):
                return {
                    'success': False,
                    'message': 'تنسيق الإشارة غير صحيح',
                    'error': 'INVALID_FORMAT'
                }
            
            # 2. الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(user_id)
            
            # 3. تطبيق إعدادات المستخدم على النظام الجديد
            advanced_settings = self._convert_to_advanced_settings(user_settings)
            set_user_settings(user_id, advanced_settings)
            
            # 4. معالجة الإشارة بالنظام الجديد
            advanced_result = process_signal(signal_data, user_id)
            
            # 5. إذا كان الحساب حقيقي، تنفيذ الصفقة عبر النظام الموجود
            if user_settings.get('account_type') == 'real' and advanced_result.get('success'):
                execution_result = await self._execute_real_trade(signal_data, user_settings, user_id)
                
                # دمج النتائج
                advanced_result['execution_result'] = execution_result
                
                if not execution_result.get('success'):
                    advanced_result['success'] = False
                    advanced_result['message'] = f"فشل في التنفيذ: {execution_result.get('message', '')}"
            
            # 6. إضافة معلومات إضافية
            advanced_result['user_id'] = user_id
            advanced_result['timestamp'] = datetime.now().isoformat()
            advanced_result['system_version'] = 'integrated_v1.0'
            
            self.logger.info(f"✅ تم معالجة الإشارة بنجاح: {advanced_result}")
            return advanced_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في المعالجة المتكاملة: {e}")
            return {
                'success': False,
                'message': f'خطأ في المعالجة المتكاملة: {str(e)}',
                'error': 'INTEGRATION_ERROR',
                'user_id': user_id
            }
    
    def _validate_signal_format(self, signal_data: Dict[str, Any]) -> bool:
        """التحقق من صحة تنسيق الإشارة"""
        try:
            required_fields = ['signal', 'symbol', 'id']
            for field in required_fields:
                if field not in signal_data or not signal_data[field]:
                    self.logger.error(f"❌ الحقل المطلوب '{field}' مفقود")
                    return False
            
            # التحقق من نوع الإشارة
            signal_type = signal_data['signal'].lower()
            valid_signals = ['buy', 'sell', 'close', 'partial_close']
            if signal_type not in valid_signals:
                self.logger.error(f"❌ نوع إشارة غير مدعوم: {signal_type}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحقق من تنسيق الإشارة: {e}")
            return False
    
    def _get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم"""
        try:
            if USER_MANAGER_AVAILABLE:
                # الحصول على إعدادات المستخدم من النظام الموجود
                user_data = user_manager.get_user_data(user_id)
                if user_data:
                    return user_data.get('settings', {})
            
            # إعدادات افتراضية
            return {
                'account_type': 'demo',
                'market_type': 'spot',
                'exchange': 'bybit',
                'trade_amount': 100.0,
                'leverage': 10,
                'link_by_id': True
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على إعدادات المستخدم: {e}")
            return {
                'account_type': 'demo',
                'market_type': 'spot',
                'exchange': 'bybit',
                'trade_amount': 100.0,
                'leverage': 10,
                'link_by_id': True
            }
    
    def _convert_to_advanced_settings(self, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل إعدادات المستخدم إلى تنسيق النظام المتقدم"""
        try:
            advanced_settings = {
                'account_type': user_settings.get('account_type', 'demo'),
                'market_type': user_settings.get('market_type', 'spot'),
                'exchange': user_settings.get('exchange', 'bybit'),
                'trade_amount': float(user_settings.get('trade_amount', 100.0)),
                'leverage': int(user_settings.get('leverage', 10)),
                'link_by_id': bool(user_settings.get('link_by_id', True)),
                'language': user_settings.get('language', 'ar')
            }
            
            self.logger.info(f"✅ تم تحويل إعدادات المستخدم: {advanced_settings}")
            return advanced_settings
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحويل الإعدادات: {e}")
            return {
                'account_type': 'demo',
                'market_type': 'spot',
                'exchange': 'bybit',
                'trade_amount': 100.0,
                'leverage': 10,
                'link_by_id': True,
                'language': 'ar'
            }
    
    async def _execute_real_trade(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ صفقة حقيقية عبر النظام الموجود"""
        try:
            if not EXISTING_SYSTEM_AVAILABLE or not self.signal_executor:
                return {
                    'success': False,
                    'message': 'النظام الموجود غير متاح للتنفيذ الحقيقي',
                    'error': 'EXISTING_SYSTEM_UNAVAILABLE'
                }
            
            self.logger.info(f"🌐 تنفيذ صفقة حقيقية للمستخدم {user_id}")
            
            # تحويل الإشارة إلى التنسيق المطلوب
            converted_signal = convert_simple_signal(signal_data, user_settings)
            
            if not converted_signal:
                return {
                    'success': False,
                    'message': 'فشل في تحويل الإشارة',
                    'error': 'SIGNAL_CONVERSION_FAILED'
                }
            
            # تنفيذ الصفقة
            execution_result = await self.signal_executor.execute_signal(user_id, converted_signal, user_settings)
            
            self.logger.info(f"✅ نتيجة التنفيذ الحقيقي: {execution_result}")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الصفقة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة الحقيقية: {str(e)}',
                'error': 'REAL_EXECUTION_ERROR'
            }
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """الحصول على حالة المستخدم"""
        try:
            # إعدادات المستخدم
            user_settings = self._get_user_settings(user_id)
            
            # إحصائيات النظام المتقدم
            from advanced_signal_manager import get_user_statistics
            stats = get_user_statistics(user_id)
            
            # صفقات المستخدم
            from advanced_signal_manager import get_user_positions
            positions = get_user_positions(user_id)
            
            return {
                'user_id': user_id,
                'settings': user_settings,
                'statistics': stats,
                'positions': positions,
                'system_status': 'active',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة المستخدم: {e}")
            return {
                'user_id': user_id,
                'error': f'خطأ في الحصول على الحالة: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def update_user_settings(self, user_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تحديث إعدادات المستخدم"""
        try:
            # تحديث النظام المتقدم
            advanced_settings = self._convert_to_advanced_settings(new_settings)
            success = set_user_settings(user_id, advanced_settings)
            
            if success:
                self.logger.info(f"✅ تم تحديث إعدادات المستخدم {user_id}")
                return {
                    'success': True,
                    'message': 'تم تحديث الإعدادات بنجاح',
                    'settings': advanced_settings
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في تحديث الإعدادات',
                    'error': 'UPDATE_FAILED'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث إعدادات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث الإعدادات: {str(e)}',
                'error': 'UPDATE_ERROR'
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """الحصول على معلومات النظام"""
        try:
            return {
                'system_name': 'Integrated Signal System',
                'version': '1.0.0',
                'features': [
                    'Advanced Signal Management',
                    'ID-based Signal Linking',
                    'Account Type Support (Demo/Real)',
                    'Market Type Support (Spot/Futures)',
                    'Optional Signal Linking',
                    'Real-time Execution',
                    'Position Tracking',
                    'User Statistics'
                ],
                'supported_signals': ['buy', 'sell', 'close', 'partial_close'],
                'supported_exchanges': ['bybit', 'mexc'],
                'supported_markets': ['spot', 'futures'],
                'supported_accounts': ['demo', 'real'],
                'existing_system_available': EXISTING_SYSTEM_AVAILABLE,
                'user_manager_available': USER_MANAGER_AVAILABLE,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على معلومات النظام: {e}")
            return {
                'error': f'خطأ في الحصول على معلومات النظام: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


# مثيل عام للنظام المتكامل
integrated_signal_system = IntegratedSignalSystem()


# دوال مساعدة للاستخدام السريع
async def process_signal_integrated(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة إشارة متكاملة"""
    return await integrated_signal_system.process_signal_complete(signal_data, user_id)


def get_user_status_integrated(user_id: int) -> Dict[str, Any]:
    """الحصول على حالة المستخدم المتكاملة"""
    return integrated_signal_system.get_user_status(user_id)


def update_user_settings_integrated(user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
    """تحديث إعدادات المستخدم المتكاملة"""
    return integrated_signal_system.update_user_settings(user_id, settings)


def get_system_info_integrated() -> Dict[str, Any]:
    """الحصول على معلومات النظام المتكامل"""
    return integrated_signal_system.get_system_info()


if __name__ == "__main__":
    # اختبار النظام المتكامل
    print("=" * 80)
    print("اختبار النظام المتكامل لإدارة الإشارات")
    print("=" * 80)
    
    # معلومات النظام
    system_info = get_system_info_integrated()
    print(f"📋 معلومات النظام: {system_info}")
    
    # اختبار معالجة الإشارات
    user_id = 12345
    
    # إعدادات المستخدم
    settings = {
        'account_type': 'demo',
        'market_type': 'spot',
        'exchange': 'bybit',
        'trade_amount': 100.0,
        'leverage': 10,
        'link_by_id': True
    }
    
    # تحديث الإعدادات
    update_result = update_user_settings_integrated(user_id, settings)
    print(f"✅ تحديث الإعدادات: {update_result}")
    
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
            result = await process_signal_integrated(signal, user_id)
            print(f"📤 النتيجة: {result}")
        
        # حالة المستخدم
        user_status = get_user_status_integrated(user_id)
        print(f"\n👤 حالة المستخدم: {user_status}")
    
    # تشغيل الاختبار
    asyncio.run(test_signals())
