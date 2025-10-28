#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث تكامل النظام - System Integration Update
يوضح كيفية ربط الملفات الجديدة مع النظام الحالي
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemIntegrationUpdate:
    """تحديث تكامل النظام"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # قائمة الملفات الجديدة
        self.new_files = [
            'signal_system_integration.py',
            'advanced_signal_manager.py',
            'enhanced_account_manager.py',
            'final_signal_processor.py',
            'complete_signal_integration.py',
            'integrated_signal_system.py'
        ]
        
        # قائمة الملفات الموجودة التي تحتاج تحديث
        self.existing_files = [
            'app.py',
            'bybit_trading_bot.py'
        ]
        
        self.logger.info(" تم تهيئة تحديث تكامل النظام")
    
    def get_integration_plan(self) -> Dict[str, Any]:
        """الحصول على خطة التكامل"""
        return {
            'integration_name': 'System Integration Update',
            'version': '1.0.0',
            'new_files': self.new_files,
            'existing_files': self.existing_files,
            'integration_steps': [
                '1. تحميل النظام الجديد في app.py',
                '2. تحديث معالجة الإشارات في app.py',
                '3. إضافة أزرار النظام الجديد في bybit_trading_bot.py',
                '4. تحديث معالجة الإشارات في bybit_trading_bot.py',
                '5. ربط النظام الجديد مع الموجود',
                '6. اختبار التكامل'
            ],
            'features_added': [
                'نظام ID للإشارات',
                'ربط الإشارات بنفس ID (اختياري)',
                'إدارة حسابات محسنة',
                'معالجة إشارات متقدمة',
                'تكامل كامل مع النظام الموجود'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def check_file_availability(self) -> Dict[str, bool]:
        """فحص توفر الملفات الجديدة"""
        import os
        
        availability = {}
        
        for file_name in self.new_files:
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            availability[file_name] = os.path.exists(file_path)
        
        return availability
    
    def get_integration_status(self) -> Dict[str, Any]:
        """الحصول على حالة التكامل"""
        file_availability = self.check_file_availability()
        
        available_files = sum(1 for available in file_availability.values() if available)
        total_files = len(self.new_files)
        
        return {
            'integration_name': 'System Integration Update',
            'version': '1.0.0',
            'status': 'ready' if available_files == total_files else 'partial',
            'files_status': file_availability,
            'available_files': available_files,
            'total_files': total_files,
            'completion_percentage': (available_files / total_files) * 100,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_app_py_updates(self) -> Dict[str, str]:
        """الحصول على التحديثات المطلوبة لـ app.py"""
        return {
            'imports': '''
# استيراد النظام الجديد
try:
    from signal_system_integration import signal_system_integration, process_signal_integrated
    NEW_SYSTEM_AVAILABLE = signal_system_integration.is_available()
    print(f" نظام الإشارات الجديد متاح: {NEW_SYSTEM_AVAILABLE}")
except ImportError as e:
    NEW_SYSTEM_AVAILABLE = False
    print(f" نظام الإشارات الجديد غير متاح: {e}")
''',
            'webhook_processing': '''
# معالجة الإشارة باستخدام النظام الجديد أو المحسن أو العادي
if NEW_SYSTEM_AVAILABLE:
    print(" معالجة الإشارة باستخدام النظام الجديد...")
    result = loop.run_until_complete(process_signal_integrated(data, user_settings_copy['user_id']))
    print(f" [WEBHOOK جديد - Thread] تمت معالجة الإشارة للمستخدم {user_settings_copy['user_id']}: {result}")
elif ENHANCED_SYSTEM_AVAILABLE and enhanced_system:
    print(" معالجة الإشارة باستخدام النظام المحسن...")
    result = enhanced_system.process_signal(user_settings_copy['user_id'], data)
    print(f" [WEBHOOK محسن - Thread] تمت معالجة الإشارة للمستخدم {user_settings_copy['user_id']}: {result}")
else:
    print(" معالجة الإشارة باستخدام النظام العادي...")
    loop.run_until_complete(trading_bot.process_signal(data))
    print(f" [WEBHOOK عادي - Thread] تمت معالجة الإشارة للمستخدم {user_settings_copy['user_id']}")
''',
            'index_page': '''
# تحديد نوع النظام المستخدم
system_status = "new" if NEW_SYSTEM_AVAILABLE else ("enhanced" if ENHANCED_SYSTEM_AVAILABLE and enhanced_system else "normal")

return jsonify({
    "status": "running",
    "message": f"بوت التداول على Bybit يعمل بنجاح - النظام: {system_status}",
    "timestamp": datetime.now().isoformat(),
    "version": "3.0.0" if NEW_SYSTEM_AVAILABLE else ("2.0.0" if ENHANCED_SYSTEM_AVAILABLE else "1.0.0"),
    "system_type": system_status,
    "new_system_available": NEW_SYSTEM_AVAILABLE,
    "enhanced_features": ENHANCED_SYSTEM_AVAILABLE or NEW_SYSTEM_AVAILABLE
})
'''
        }
    
    def get_bot_updates(self) -> Dict[str, str]:
        """الحصول على التحديثات المطلوبة لـ bybit_trading_bot.py"""
        return {
            'keyboard_buttons': '''
# إضافة أزرار النظام الجديد
keyboard = [
    [KeyboardButton(" الإعدادات"), KeyboardButton(" حالة الحساب")],
    [KeyboardButton(" الصفقات المفتوحة"), KeyboardButton(" تاريخ التداول")],
    [KeyboardButton(" المحفظة"), KeyboardButton(" إحصائيات")],
    [KeyboardButton(" الأدوات المتقدمة"), KeyboardButton(" نظام الإشارات")],  # أزرار جديدة
    [KeyboardButton("🔙 الرجوع لحساب المطور")]
]
''',
            'signal_processing': '''
# استخراج ID الإشارة لاستخدامه كمعرف للصفقة
signal_id = signal_data.get('signal_id') or signal_data.get('id') or signal_data.get('original_signal', {}).get('id')
if signal_id:
    logger.info(f" تم استخراج ID الإشارة: {signal_id}")
    self._current_signal_id = signal_id
else:
    logger.info(" لا يوجد ID في الإشارة - سيتم توليد ID عشوائي")
    self._current_signal_id = None
''',
            'position_creation': '''
# استخدام ID الإشارة كمعرف للصفقة إذا كان متاحاً
custom_position_id = None
if hasattr(self, '_current_signal_id') and self._current_signal_id:
    custom_position_id = self._current_signal_id
    logger.info(f" استخدام ID الإشارة كمعرف للصفقة: {custom_position_id}")

success, result = account.open_futures_position(
    symbol=symbol,
    side=action,
    margin_amount=margin_amount,
    price=price,
    leverage=leverage,
    position_id=custom_position_id  # استخدام ID المخصص
)
'''
        }
    
    def get_usage_examples(self) -> Dict[str, List[str]]:
        """الحصول على أمثلة الاستخدام"""
        return {
            'signal_with_id': [
                '# إشارة مع ID محدد',
                'signal_data = {',
                '    "signal": "buy",',
                '    "symbol": "BTCUSDT",',
                '    "id": "TV_B01"',
                '}',
                '# النتيجة: سيتم استخدام "TV_B01" كمعرف للصفقة'
            ],
            'signal_without_id': [
                '# إشارة بدون ID',
                'signal_data = {',
                '    "signal": "sell",',
                '    "symbol": "ETHUSDT"',
                '}',
                '# النتيجة: سيتم توليد ID عشوائي مثل "ETHUSDT_sell_ABC12345"'
            ],
            'close_signal': [
                '# إشارة إغلاق',
                'signal_data = {',
                '    "signal": "close",',
                '    "symbol": "BTCUSDT",',
                '    "id": "TV_B01"',
                '}',
                '# النتيجة: سيتم إغلاق الصفقة التي لها ID "TV_B01"'
            ],
            'partial_close': [
                '# إشارة إغلاق جزئي',
                'signal_data = {',
                '    "signal": "partial_close",',
                '    "symbol": "BTCUSDT",',
                '    "id": "TV_B01",',
                '    "percentage": 50',
                '}',
                '# النتيجة: سيتم إغلاق 50% من الصفقة التي لها ID "TV_B01"'
            ]
        }
    
    def get_testing_guide(self) -> Dict[str, Any]:
        """الحصول على دليل الاختبار"""
        return {
            'testing_steps': [
                '1. تشغيل البوت والتأكد من عدم وجود أخطاء',
                '2. إرسال إشارة مع ID والتحقق من استخدام ID كمعرف للصفقة',
                '3. إرسال إشارة بدون ID والتحقق من توليد ID عشوائي',
                '4. إرسال إشارة إغلاق والتحقق من إغلاق الصفقة الصحيحة',
                '5. إرسال إشارة إغلاق جزئي والتحقق من الإغلاق الجزئي',
                '6. اختبار النظام مع حسابات Demo و Real',
                '7. اختبار النظام مع أسواق Spot و Futures'
            ],
            'test_signals': [
                {
                    'name': 'إشارة شراء مع ID',
                    'data': {
                        'signal': 'buy',
                        'symbol': 'BTCUSDT',
                        'id': 'TEST_BUY_001'
                    },
                    'expected': 'يجب أن تفتح صفقة بمعرف "TEST_BUY_001"'
                },
                {
                    'name': 'إشارة بيع بدون ID',
                    'data': {
                        'signal': 'sell',
                        'symbol': 'ETHUSDT'
                    },
                    'expected': 'يجب أن تفتح صفقة بمعرف عشوائي'
                },
                {
                    'name': 'إشارة إغلاق',
                    'data': {
                        'signal': 'close',
                        'symbol': 'BTCUSDT',
                        'id': 'TEST_BUY_001'
                    },
                    'expected': 'يجب أن تغلق الصفقة التي لها معرف "TEST_BUY_001"'
                }
            ]
        }


# مثيل عام لتحديث تكامل النظام
system_integration_update = SystemIntegrationUpdate()


# دوال مساعدة للاستخدام السريع
def get_integration_plan() -> Dict[str, Any]:
    """الحصول على خطة التكامل"""
    return system_integration_update.get_integration_plan()


def get_integration_status() -> Dict[str, Any]:
    """الحصول على حالة التكامل"""
    return system_integration_update.get_integration_status()


def get_app_py_updates() -> Dict[str, str]:
    """الحصول على تحديثات app.py"""
    return system_integration_update.get_app_py_updates()


def get_bot_updates() -> Dict[str, str]:
    """الحصول على تحديثات bybit_trading_bot.py"""
    return system_integration_update.get_bot_updates()


if __name__ == "__main__":
    # اختبار تحديث تكامل النظام
    print("=" * 80)
    print("اختبار تحديث تكامل النظام")
    print("=" * 80)
    
    # خطة التكامل
    plan = get_integration_plan()
    print(f"\n خطة التكامل:")
    print(f"   الاسم: {plan['integration_name']}")
    print(f"   الإصدار: {plan['version']}")
    print(f"   الملفات الجديدة: {len(plan['new_files'])}")
    print(f"   الملفات الموجودة: {len(plan['existing_files'])}")
    
    # حالة التكامل
    status = get_integration_status()
    print(f"\n حالة التكامل:")
    print(f"   الحالة: {status['status']}")
    print(f"   الملفات المتاحة: {status['available_files']}/{status['total_files']}")
    print(f"   نسبة الإكمال: {status['completion_percentage']:.1f}%")
    
    # قائمة الملفات
    print(f"\n📁 حالة الملفات:")
    for file_name, is_available in status['files_status'].items():
        status_icon = "" if is_available else ""
        print(f"   {status_icon} {file_name}")
    
    # خطوات التكامل
    print(f"\n خطوات التكامل:")
    for i, step in enumerate(plan['integration_steps'], 1):
        print(f"   {i}. {step}")
    
    # الميزات المضافة
    print(f"\n الميزات المضافة:")
    for feature in plan['features_added']:
        print(f"   • {feature}")
    
    # أمثلة الاستخدام
    examples = system_integration_update.get_usage_examples()
    print(f"\n🧪 أمثلة الاستخدام:")
    for example_name, code_lines in examples.items():
        print(f"\n    {example_name}:")
        for line in code_lines:
            print(f"      {line}")
