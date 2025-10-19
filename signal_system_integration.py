#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التكامل الموحد - ربط جميع أنظمة الإشارات مع البوت الرئيسي
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# إعداد التسجيل
logger = logging.getLogger(__name__)

class SignalSystemIntegration:
    """نظام التكامل الموحد لربط جميع الأنظمة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تحميل الأنظمة الجديدة
        self.advanced_manager = None
        self.account_manager = None
        self.final_processor = None
        self.complete_integration = None
        
        # حالة التكامل
        self.integration_status = {
            'advanced_manager': False,
            'account_manager': False,
            'final_processor': False,
            'complete_integration': False
        }
        
        # تهيئة الأنظمة
        self._initialize_systems()
        
        self.logger.info("🚀 تم تهيئة نظام التكامل الموحد")
    
    def _initialize_systems(self):
        """تهيئة جميع الأنظمة"""
        try:
            # تحميل مدير الإشارات المتقدم
            try:
                from advanced_signal_manager import advanced_signal_manager
                self.advanced_manager = advanced_signal_manager
                self.integration_status['advanced_manager'] = True
                self.logger.info("✅ تم تحميل مدير الإشارات المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الإشارات المتقدم: {e}")
            
            # تحميل مدير الحسابات المحسن
            try:
                from enhanced_account_manager import enhanced_account_manager
                self.account_manager = enhanced_account_manager
                self.integration_status['account_manager'] = True
                self.logger.info("✅ تم تحميل مدير الحسابات المحسن")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الحسابات المحسن: {e}")
            
            # تحميل معالج الإشارات النهائي
            try:
                from final_signal_processor import final_signal_processor
                self.final_processor = final_signal_processor
                self.integration_status['final_processor'] = True
                self.logger.info("✅ تم تحميل معالج الإشارات النهائي")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل معالج الإشارات النهائي: {e}")
            
            # تحميل التكامل الكامل
            try:
                from complete_signal_integration import complete_signal_integration
                self.complete_integration = complete_signal_integration
                self.integration_status['complete_integration'] = True
                self.logger.info("✅ تم تحميل التكامل الكامل")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل التكامل الكامل: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تهيئة الأنظمة: {e}")
    
    async def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        معالجة الإشارة باستخدام النظام الجديد
        
        Args:
            signal_data: بيانات الإشارة
            user_id: معرف المستخدم
            
        Returns:
            نتيجة معالجة الإشارة
        """
        try:
            self.logger.info(f"🎯 معالجة إشارة للمستخدم {user_id}: {signal_data}")
            
            # إذا كان النظام الكامل متاح، استخدمه
            if self.complete_integration:
                result = await self.complete_integration.process_signal_complete(signal_data, user_id)
                self.logger.info(f"✅ تم معالجة الإشارة بالنظام الكامل: {result}")
                return result
            
            # إذا كان معالج الإشارات النهائي متاح، استخدمه
            elif self.final_processor:
                result = await self.final_processor.process_signal(signal_data, user_id)
                self.logger.info(f"✅ تم معالجة الإشارة بالمعالج النهائي: {result}")
                return result
            
            # إذا كان مدير الإشارات المتقدم متاح، استخدمه
            elif self.advanced_manager:
                result = self.advanced_manager.process_signal(signal_data, user_id)
                self.logger.info(f"✅ تم معالجة الإشارة بالمدير المتقدم: {result}")
                return result
            
            # لا يوجد نظام متاح
            else:
                self.logger.warning("⚠️ لا يوجد نظام معالجة متاح")
                return {
                    'success': False,
                    'message': 'لا يوجد نظام معالجة متاح',
                    'error': 'NO_SYSTEM_AVAILABLE'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': 'PROCESSING_ERROR'
            }
    
    def setup_user_accounts(self, user_id: int) -> Dict[str, Any]:
        """إعداد حسابات المستخدم"""
        try:
            if self.complete_integration:
                return self.complete_integration.setup_user_accounts(user_id)
            elif self.account_manager:
                return self.account_manager.create_user_accounts(user_id)
            else:
                return {
                    'success': False,
                    'message': 'لا يوجد نظام إدارة حسابات متاح',
                    'error': 'NO_ACCOUNT_MANAGER'
                }
        except Exception as e:
            self.logger.error(f"❌ خطأ في إعداد حسابات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في إعداد الحسابات: {str(e)}',
                'error': 'ACCOUNT_SETUP_ERROR'
            }
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """تحديث إعدادات المستخدم"""
        try:
            if self.complete_integration:
                return self.complete_integration.update_user_settings(user_id, settings)
            elif self.advanced_manager:
                success = self.advanced_manager.set_user_settings(user_id, settings)
                return {
                    'success': success,
                    'message': 'تم تحديث الإعدادات' if success else 'فشل التحديث'
                }
            else:
                return {
                    'success': False,
                    'message': 'لا يوجد نظام إدارة إعدادات متاح',
                    'error': 'NO_SETTINGS_MANAGER'
                }
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث إعدادات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في تحديث الإعدادات: {str(e)}',
                'error': 'SETTINGS_UPDATE_ERROR'
            }
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """الحصول على حالة المستخدم"""
        try:
            if self.complete_integration:
                return self.complete_integration.get_user_status(user_id)
            elif self.advanced_manager:
                return self.advanced_manager.get_statistics(user_id)
            else:
                return {
                    'success': False,
                    'message': 'لا يوجد نظام حالة متاح',
                    'error': 'NO_STATUS_SYSTEM'
                }
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في الحصول على الحالة: {str(e)}',
                'error': 'STATUS_ERROR'
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        try:
            return {
                'integration_name': 'Signal System Integration',
                'version': '1.0.0',
                'status': 'active',
                'systems': self.integration_status,
                'available_systems': sum(self.integration_status.values()),
                'total_systems': len(self.integration_status),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة التكامل: {e}")
            return {
                'error': f'خطأ في الحصول على الحالة: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def is_available(self) -> bool:
        """التحقق من توفر النظام"""
        return any(self.integration_status.values())


# مثيل عام لنظام التكامل
signal_system_integration = SignalSystemIntegration()


# دوال مساعدة للاستخدام السريع
async def process_signal_integrated(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة إشارة متكاملة"""
    return await signal_system_integration.process_signal(signal_data, user_id)


def setup_user_accounts_integrated(user_id: int) -> Dict[str, Any]:
    """إعداد حسابات المستخدم المتكامل"""
    return signal_system_integration.setup_user_accounts(user_id)


def update_user_settings_integrated(user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
    """تحديث إعدادات المستخدم المتكامل"""
    return signal_system_integration.update_user_settings(user_id, settings)


def get_user_status_integrated(user_id: int) -> Dict[str, Any]:
    """الحصول على حالة المستخدم المتكاملة"""
    return signal_system_integration.get_user_status(user_id)


def get_integration_status() -> Dict[str, Any]:
    """الحصول على حالة التكامل"""
    return signal_system_integration.get_integration_status()


def is_system_available() -> bool:
    """التحقق من توفر النظام"""
    return signal_system_integration.is_available()


if __name__ == "__main__":
    # اختبار نظام التكامل
    print("=" * 80)
    print("اختبار نظام التكامل الموحد")
    print("=" * 80)
    
    # حالة التكامل
    status = get_integration_status()
    print(f"📋 حالة التكامل: {status}")
    
    # التحقق من التوفر
    available = is_system_available()
    print(f"✅ النظام متاح: {available}")
    
    if available:
        print("\n🎯 الأنظمة المتاحة:")
        for system, status in signal_system_integration.integration_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {system}")
    else:
        print("\n❌ لا توجد أنظمة متاحة")
