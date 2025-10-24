#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
التكامل الكامل للإشارات - Complete Signal Integration
يدمج جميع المكونات لمعالجة الإشارات الكاملة
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CompleteSignalIntegration:
    """التكامل الكامل لمعالجة الإشارات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تحميل المكونات
        self.components = {}
        self._load_components()
        
        self.logger.info("🎯 تم تهيئة التكامل الكامل للإشارات")
    
    def _load_components(self):
        """تحميل جميع المكونات"""
        try:
            # 1. معالج الإشارات النهائي
            try:
                from final_signal_processor import final_signal_processor
                self.components['signal_processor'] = final_signal_processor
                self.logger.info("✅ تم تحميل معالج الإشارات النهائي")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل معالج الإشارات: {e}")
            
            # 2. مدير الإشارات المتقدم
            try:
                from advanced_signal_manager import advanced_signal_manager
                self.components['signal_manager'] = advanced_signal_manager
                self.logger.info("✅ تم تحميل مدير الإشارات المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الإشارات: {e}")
            
            # 3. مدير الحسابات المحسن
            try:
                from enhanced_account_manager import enhanced_account_manager
                self.components['account_manager'] = enhanced_account_manager
                self.logger.info("✅ تم تحميل مدير الحسابات المحسن")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الحسابات: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل المكونات: {e}")
    
    def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة الإشارة الكاملة مع جميع المكونات"""
        try:
            self.logger.info(f"🎯 بدء معالجة الإشارة الكاملة للمستخدم {user_id}")
            
            # 1. معالجة الإشارة الأساسية
            if 'signal_processor' in self.components:
                signal_result = self.components['signal_processor'].process_signal(signal_data, user_id)
                
                if not signal_result['success']:
                    return signal_result
                
                self.logger.info("✅ تمت معالجة الإشارة الأساسية")
            else:
                signal_result = {'success': True, 'message': 'معالج الإشارات غير متاح'}
            
            # 2. إدارة الإشارة المتقدمة
            if 'signal_manager' in self.components:
                manager_result = self.components['signal_manager'].process_signal(signal_data, user_id)
                
                if not manager_result['success']:
                    self.logger.warning(f"⚠️ فشل في إدارة الإشارة: {manager_result['message']}")
                else:
                    self.logger.info("✅ تمت إدارة الإشارة المتقدمة")
                    signal_id = manager_result.get('signal_id')
            else:
                manager_result = {'success': True, 'message': 'مدير الإشارات غير متاح'}
                signal_id = signal_data.get('id')
            
            # 3. إدارة الحساب والصفحة
            position_result = None
            if 'account_manager' in self.components:
                # الحصول على إعدادات المستخدم (يمكن تحسينها لاحقاً)
                user_settings = self._get_user_settings(user_id)
                
                account_result = self.components['account_manager'].open_position(
                    user_id=user_id,
                    signal_data=signal_data,
                    account_type=user_settings.get('account_type', 'demo'),
                    market_type=user_settings.get('market_type', 'spot'),
                    exchange=user_settings.get('exchange', 'bybit')
                )
                
                if account_result['success']:
                    position_id = account_result['position_id']
                    
                    # ربط الصفقة بالإشارة
                    if 'signal_manager' in self.components and signal_id:
                        link_result = self.components['signal_manager'].link_signal_to_position(
                            signal_id, position_id
                        )
                        if link_result:
                            self.logger.info(f"🔗 تم ربط الإشارة {signal_id} بالصفقة {position_id}")
                    
                    position_result = account_result
                    self.logger.info("✅ تم إنشاء الصفقة في الحساب")
                else:
                    self.logger.warning(f"⚠️ فشل في إنشاء الصفقة: {account_result['message']}")
            
            # 4. تجميع النتائج
            final_result = {
                'success': True,
                'message': 'تم معالجة الإشارة الكاملة بنجاح',
                'signal_processing': signal_result,
                'signal_management': manager_result,
                'position_management': position_result,
                'signal_id': signal_id,
                'position_id': position_result.get('position_id') if position_result else None,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'components_used': list(self.components.keys())
            }
            
            self.logger.info(f"✅ تمت معالجة الإشارة الكاملة بنجاح للمستخدم {user_id}")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة الكاملة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة الكاملة: {str(e)}',
                'error': str(e),
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم (مؤقت - يمكن تحسينها)"""
        # هذا يمكن تحسينه لاحقاً للاتصال بقاعدة البيانات أو user_manager
        return {
            'account_type': 'demo',
            'market_type': 'spot',
            'exchange': 'bybit',
            'trade_amount': 100.0,
            'leverage': 1,
            'link_by_id': True
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        return {
            'integration_name': 'Complete Signal Integration',
            'version': '1.0.0',
            'status': 'active',
            'components': {
                'signal_processor': 'signal_processor' in self.components,
                'signal_manager': 'signal_manager' in self.components,
                'account_manager': 'account_manager' in self.components
            },
            'available_components': len(self.components),
            'total_components': 3,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_processing_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """الحصول على إحصائيات المعالجة"""
        stats = {
            'integration_status': self.get_integration_status(),
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # إضافة إحصائيات من المكونات المتاحة
        if 'signal_manager' in self.components:
            stats['signal_statistics'] = self.components['signal_manager'].get_signal_statistics(user_id)
        
        if 'account_manager' in self.components:
            if user_id:
                stats['account_statistics'] = self.components['account_manager'].get_account_statistics(user_id)
        
        return stats
    
    def close_signal_positions(self, signal_id: str) -> Dict[str, Any]:
        """إغلاق جميع الصفقات المرتبطة بإشارة"""
        try:
            results = []
            
            # إغلاق الصفقات من مدير الإشارات
            if 'signal_manager' in self.components:
                signal_result = self.components['signal_manager'].close_signal_positions(signal_id)
                results.append({
                    'component': 'signal_manager',
                    'result': signal_result
                })
            
            # إغلاق الصفقات من مدير الحسابات
            if 'account_manager' in self.components:
                positions = self.components['account_manager'].get_positions_by_signal_id(signal_id)
                
                for position in positions:
                    position_id = position['position_id']
                    close_result = self.components['account_manager'].close_position(position_id, 0.0)  # سعر مؤقت
                    results.append({
                        'component': 'account_manager',
                        'position_id': position_id,
                        'result': close_result
                    })
            
            return {
                'success': True,
                'message': f'تم إغلاق الصفقات للإشارة {signal_id}',
                'signal_id': signal_id,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إغلاق صفقات الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في إغلاق صفقات الإشارة: {str(e)}',
                'error': str(e)
            }


# مثيل عام للتكامل الكامل للإشارات
complete_signal_integration = CompleteSignalIntegration()


# دوال مساعدة للاستخدام السريع
def process_signal(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة الإشارة الكاملة"""
    return complete_signal_integration.process_signal(signal_data, user_id)


def get_integration_status() -> Dict[str, Any]:
    """الحصول على حالة التكامل"""
    return complete_signal_integration.get_integration_status()


def close_signal_positions(signal_id: str) -> Dict[str, Any]:
    """إغلاق صفقات الإشارة"""
    return complete_signal_integration.close_signal_positions(signal_id)


if __name__ == "__main__":
    # اختبار التكامل الكامل للإشارات
    print("=" * 80)
    print("اختبار التكامل الكامل للإشارات")
    print("=" * 80)
    
    # حالة التكامل
    status = get_integration_status()
    print(f"\n📊 حالة التكامل:")
    print(f"   الحالة: {status['status']}")
    print(f"   المكونات المتاحة: {status['available_components']}/{status['total_components']}")
    
    # قائمة المكونات
    print(f"\n🔧 المكونات المتاحة:")
    for component_name, is_available in status['components'].items():
        status_icon = "✅" if is_available else "❌"
        print(f"   {status_icon} {component_name}")
    
    # اختبار معالجة إشارة
    if status['available_components'] > 0:
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_INTEGRATION_001'
        }
        
        result = process_signal(test_signal, 12345)
        print(f"\n🧪 نتيجة اختبار المعالجة الكاملة: {result['success']}")
        if result['success']:
            print(f"   ID الإشارة: {result.get('signal_id', 'غير محدد')}")
            print(f"   ID الصفقة: {result.get('position_id', 'غير محدد')}")
            print(f"   المكونات المستخدمة: {result.get('components_used', [])}")
        else:
            print(f"   الخطأ: {result.get('message', 'غير محدد')}")
    else:
        print("\n⚠️ لا توجد مكونات متاحة للاختبار")
