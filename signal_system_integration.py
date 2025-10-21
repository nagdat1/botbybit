#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تكامل الإشارات - Signal System Integration
يربط جميع أنظمة الإشارات الجديدة مع البوت الرئيسي
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalSystemIntegration:
    """نظام تكامل الإشارات الموحد"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تحميل جميع الأنظمة المتاحة
        self.available_systems = {}
        self._load_all_systems()
        
        self.logger.info("🎯 تم تهيئة نظام تكامل الإشارات")
    
    def _load_all_systems(self):
        """تحميل جميع أنظمة الإشارات المتاحة"""
        try:
            # 1. نظام إدارة الإشارات المتقدم
            try:
                from advanced_signal_manager import AdvancedSignalManager
                self.available_systems['advanced_manager'] = AdvancedSignalManager()
                self.logger.info("✅ تم تحميل مدير الإشارات المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الإشارات المتقدم: {e}")
            
            # 2. مدير الحسابات المحسن
            try:
                from enhanced_account_manager import EnhancedAccountManager
                self.available_systems['account_manager'] = EnhancedAccountManager()
                self.logger.info("✅ تم تحميل مدير الحسابات المحسن")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الحسابات المحسن: {e}")
            
            # 3. معالج الإشارات النهائي
            try:
                from final_signal_processor import FinalSignalProcessor
                self.available_systems['final_processor'] = FinalSignalProcessor()
                self.logger.info("✅ تم تحميل معالج الإشارات النهائي")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل معالج الإشارات النهائي: {e}")
            
            # 4. النظام المتكامل الكامل
            try:
                from complete_signal_integration import CompleteSignalIntegration
                self.available_systems['complete_integration'] = CompleteSignalIntegration()
                self.logger.info("✅ تم تحميل النظام المتكامل الكامل")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل النظام المتكامل الكامل: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل أنظمة الإشارات: {e}")
    
    def is_available(self) -> bool:
        """التحقق من توفر النظام"""
        return len(self.available_systems) > 0
    
    def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة الإشارة باستخدام أفضل نظام متاح"""
        try:
            if not self.is_available():
                return {
                    'success': False,
                    'message': 'لا توجد أنظمة إشارات متاحة',
                    'error': 'no_systems_available'
                }
            
            # اختيار أفضل نظام متاح
            best_system = self._get_best_available_system()
            
            if not best_system:
                return {
                    'success': False,
                    'message': 'لا يمكن العثور على نظام مناسب',
                    'error': 'no_suitable_system'
                }
            
            # معالجة الإشارة باستخدام النظام المختار
            result = best_system.process_signal(signal_data, user_id)
            
            self.logger.info(f"✅ تم معالجة الإشارة باستخدام {best_system.__class__.__name__}")
            
            return {
                'success': True,
                'message': 'تم معالجة الإشارة بنجاح',
                'system_used': best_system.__class__.__name__,
                'result': result
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': str(e)
            }
    
    def _get_best_available_system(self):
        """الحصول على أفضل نظام متاح"""
        # أولوية الأنظمة (من الأفضل للأقل)
        priority_order = [
            'complete_integration',
            'final_processor', 
            'advanced_manager',
            'account_manager'
        ]
        
        for system_name in priority_order:
            if system_name in self.available_systems:
                return self.available_systems[system_name]
        
        # إذا لم يتم العثور على نظام بأولوية، ارجع أول نظام متاح
        if self.available_systems:
            return list(self.available_systems.values())[0]
        
        return None
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        return {
            'integration_name': 'Signal System Integration',
            'version': '1.0.0',
            'status': 'active' if self.is_available() else 'inactive',
            'systems': {
                'advanced_manager': 'advanced_manager' in self.available_systems,
                'account_manager': 'account_manager' in self.available_systems,
                'final_processor': 'final_processor' in self.available_systems,
                'complete_integration': 'complete_integration' in self.available_systems
            },
            'available_systems': len(self.available_systems),
            'total_systems': 4,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_systems(self) -> Dict[str, Any]:
        """الحصول على قائمة الأنظمة المتاحة"""
        return self.available_systems
    
    def get_system(self, system_name: str) -> Optional[Any]:
        """الحصول على نظام محدد"""
        return self.available_systems.get(system_name)


# مثيل عام لنظام تكامل الإشارات
signal_system_integration = SignalSystemIntegration()


# دوال مساعدة للاستخدام السريع
def process_signal_integrated(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة الإشارة باستخدام النظام المتكامل"""
    return signal_system_integration.process_signal(signal_data, user_id)


def get_integration_status() -> Dict[str, Any]:
    """الحصول على حالة التكامل"""
    return signal_system_integration.get_integration_status()


def is_system_available() -> bool:
    """التحقق من توفر النظام"""
    return signal_system_integration.is_available()


if __name__ == "__main__":
    # اختبار نظام تكامل الإشارات
    print("=" * 80)
    print("اختبار نظام تكامل الإشارات")
    print("=" * 80)
    
    # حالة النظام
    status = get_integration_status()
    print(f"\nحالة النظام:")
    print(f"   الحالة: {status['status']}")
    print(f"   الأنظمة المتاحة: {status['available_systems']}/{status['total_systems']}")
    
    # قائمة الأنظمة
    print(f"\nالأنظمة المتاحة:")
    for system_name, is_available in status['systems'].items():
        status_icon = "متاح" if is_available else "غير متاح"
        print(f"   {status_icon}: {system_name}")
    
    # اختبار معالجة إشارة
    if is_system_available():
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_001'
        }
        
        result = process_signal_integrated(test_signal, 12345)
        print(f"\nنتيجة اختبار الإشارة: {result['success']}")
        if result['success']:
            print(f"   النظام المستخدم: {result.get('system_used', 'غير محدد')}")
        else:
            print(f"   الخطأ: {result.get('message', 'غير محدد')}")
    else:
        print("\nلا توجد أنظمة متاحة للاختبار")
