#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الإشارات المتكامل - Integrated Signal System
يدمج النظام الجديد مع الموجود لمعالجة الإشارات المتكاملة
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class IntegratedSignalSystem:
    """نظام الإشارات المتكامل"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تحميل الأنظمة
        self.systems = {}
        self._load_systems()
        
        self.logger.info("🎯 تم تهيئة نظام الإشارات المتكامل")
    
    def _load_systems(self):
        """تحميل جميع الأنظمة المتاحة"""
        try:
            # 1. النظام الجديد (الأولوية الأولى)
            try:
                from complete_signal_integration import complete_signal_integration
                self.systems['new_system'] = complete_signal_integration
                self.logger.info("✅ تم تحميل النظام الجديد")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل النظام الجديد: {e}")
            
            # 2. النظام المحسن الموجود
            try:
                from systems.simple_enhanced_system import SimpleEnhancedSystem
                self.systems['enhanced_system'] = SimpleEnhancedSystem()
                self.logger.info("✅ تم تحميل النظام المحسن")
            except Exception as e:
                self.logger.warning(f"⚠️ فشل تحميل النظام المحسن: {e}")
            
            # 3. النظام المحسن المبسط
            try:
                from systems.simple_enhanced_system import SimpleEnhancedSystem
                self.systems['simple_enhanced'] = SimpleEnhancedSystem()
                self.logger.info("✅ تم تحميل النظام المحسن المبسط")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل النظام المحسن المبسط: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل الأنظمة: {e}")
    
    def process_signal(self, user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة الإشارة باستخدام أفضل نظام متاح"""
        try:
            if not self.systems:
                return {
                    'status': 'error',
                    'message': 'لا توجد أنظمة متاحة',
                    'error': 'no_systems_available'
                }
            
            # اختيار أفضل نظام متاح
            best_system = self._get_best_available_system()
            
            if not best_system:
                return {
                    'status': 'error',
                    'message': 'لا يمكن العثور على نظام مناسب',
                    'error': 'no_suitable_system'
                }
            
            # معالجة الإشارة
            system_name = best_system.__class__.__name__
            self.logger.info(f"🎯 معالجة الإشارة باستخدام {system_name}")
            
            # معالجة الإشارة حسب نوع النظام
            if hasattr(best_system, 'process_signal'):
                result = best_system.process_signal(signal_data, user_id)
            else:
                # للنظام المحسن الموجود
                result = best_system.process_signal(user_id, signal_data)
            
            # تنسيق النتيجة
            if isinstance(result, dict) and 'success' in result:
                # النظام الجديد
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result.get('message', 'تمت معالجة الإشارة'),
                    'system_used': system_name,
                    'details': result
                }
            else:
                # النظام المحسن الموجود
                return {
                    'status': 'success',
                    'message': 'تمت معالجة الإشارة بنجاح',
                    'system_used': system_name,
                    'details': result
                }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            return {
                'status': 'error',
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': str(e),
                'system_used': 'error'
            }
    
    def _get_best_available_system(self):
        """الحصول على أفضل نظام متاح"""
        # أولوية الأنظمة (من الأفضل للأقل)
        priority_order = [
            'new_system',
            'enhanced_system',
            'simple_enhanced'
        ]
        
        for system_name in priority_order:
            if system_name in self.systems:
                return self.systems[system_name]
        
        # إذا لم يتم العثور على نظام بأولوية، ارجع أول نظام متاح
        if self.systems:
            return list(self.systems.values())[0]
        
        return None
    
    def get_available_systems(self) -> Dict[str, Any]:
        """الحصول على قائمة الأنظمة المتاحة"""
        return self.systems
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة الأنظمة"""
        return {
            'new_system': 'new_system' in self.systems,
            'enhanced_system': 'enhanced_system' in self.systems,
            'simple_enhanced': 'simple_enhanced' in self.systems,
            'total_available': len(self.systems),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_integration_info(self) -> Dict[str, Any]:
        """الحصول على معلومات التكامل"""
        status = self.get_system_status()
        
        return {
            'integration_name': 'Integrated Signal System',
            'version': '1.0.0',
            'status': 'active' if self.systems else 'inactive',
            'systems': status,
            'best_system': self._get_best_available_system().__class__.__name__ if self.systems else None,
            'timestamp': datetime.now().isoformat()
        }


# مثيل عام لنظام الإشارات المتكامل
integrated_signal_system = IntegratedSignalSystem()


# دوال مساعدة للاستخدام السريع
def process_signal(user_id: int, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """معالجة الإشارة"""
    return integrated_signal_system.process_signal(user_id, signal_data)


def get_system_status() -> Dict[str, Any]:
    """الحصول على حالة الأنظمة"""
    return integrated_signal_system.get_system_status()


def get_integration_info() -> Dict[str, Any]:
    """الحصول على معلومات التكامل"""
    return integrated_signal_system.get_integration_info()


if __name__ == "__main__":
    # اختبار نظام الإشارات المتكامل
    print("=" * 80)
    print("اختبار نظام الإشارات المتكامل")
    print("=" * 80)
    
    # حالة الأنظمة
    status = get_system_status()
    print(f"\n📊 حالة الأنظمة:")
    print(f"   إجمالي الأنظمة المتاحة: {status['total_available']}")
    
    # قائمة الأنظمة
    print(f"\n🔧 الأنظمة المتاحة:")
    for system_name, is_available in status.items():
        if system_name != 'total_available' and system_name != 'timestamp':
            status_icon = "✅" if is_available else "❌"
            print(f"   {status_icon} {system_name}")
    
    # معلومات التكامل
    info = get_integration_info()
    print(f"\n🎯 معلومات التكامل:")
    print(f"   الحالة: {info['status']}")
    print(f"   أفضل نظام: {info.get('best_system', 'غير متاح')}")
    
    # اختبار معالجة إشارة
    if status['total_available'] > 0:
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TV_INTEGRATION_001'
        }
        
        result = process_signal(12345, test_signal)
        print(f"\n🧪 نتيجة اختبار المعالجة: {result['status']}")
        print(f"   النظام المستخدم: {result.get('system_used', 'غير محدد')}")
        print(f"   الرسالة: {result.get('message', 'غير محدد')}")
    else:
        print("\n⚠️ لا توجد أنظمة متاحة للاختبار")
