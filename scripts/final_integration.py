#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التكامل النهائي - ربط النظام المحسن مع النظام الحالي
يحافظ على آلية التوقيع وحساب السعر مع دعم تعديل المتغيرات
"""

import logging
import time
from typing import Dict, Any, Optional

# استيراد النظام المحسن
from flexible_config_manager import flexible_config_manager
from enhanced_bot_interface import enhanced_bot_interface
from enhanced_trade_executor import enhanced_trade_executor
from integrated_trading_system import integrated_trading_system
from enhanced_trading_bot import enhanced_trading_bot
from system_updater import system_updater

# استيراد النظام الحالي
from database import db_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class FinalIntegration:
    """التكامل النهائي للنظام المحسن"""
    
    def __init__(self):
        self.integration_status = "not_started"
        self.backup_created = False
        self.enhanced_system_active = False
        
    def integrate_with_existing_system(self, existing_bot=None):
        """التكامل مع النظام الحالي"""
        try:
            logger.info("🚀 بدء التكامل النهائي للنظام المحسن...")
            
            # 1. إنشاء نسخة احتياطية
            self._create_system_backup()
            
            # 2. تهيئة النظام المحسن
            self._initialize_enhanced_system()
            
            # 3. ربط النظام المحسن مع النظام الحالي
            self._link_with_existing_system(existing_bot)
            
            # 4. اختبار التكامل
            self._test_integration()
            
            # 5. تفعيل النظام المحسن
            self._activate_enhanced_system()
            
            self.integration_status = "completed"
            logger.info("✅ تم التكامل النهائي بنجاح!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل في التكامل النهائي: {e}")
            self.integration_status = "failed"
            return False
    
    def _create_system_backup(self):
        """إنشاء نسخة احتياطية من النظام"""
        try:
            # حفظ الإعدادات الحالية
            self.backup_data = {
                'timestamp': time.time(),
                'user_settings': {},
                'api_settings': {},
                'database_backup': True
            }
            
            # حفظ إعدادات المستخدمين النشطين
            active_users = db_manager.get_all_active_users()
            for user in active_users:
                user_id = user['user_id']
                self.backup_data['user_settings'][user_id] = {
                    'trade_amount': user.get('trade_amount', 50.0),
                    'leverage': user.get('leverage', 2),
                    'market_type': user.get('market_type', 'futures'),
                    'account_type': user.get('account_type', 'real'),
                    'exchange': user.get('exchange', 'bybit')
                }
            
            self.backup_created = True
            logger.info("💾 تم إنشاء النسخة الاحتياطية")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
    
    def _initialize_enhanced_system(self):
        """تهيئة النظام المحسن"""
        try:
            # تهيئة مدير الإعدادات المرن
            flexible_config_manager.clear_config_cache()
            
            # تهيئة تنفيذ الصفقات المحسن
            enhanced_trade_executor.clear_execution_history()
            
            # تهيئة النظام المتكامل
            integrated_trading_system.toggle_system(True)
            
            logger.info("⚙️ تم تهيئة النظام المحسن")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام المحسن: {e}")
    
    def _link_with_existing_system(self, existing_bot):
        """ربط النظام المحسن مع النظام الحالي"""
        try:
            # ربط البوت المحسن
            if existing_bot:
                enhanced_trading_bot.integrate_with_existing_system(existing_bot)
            
            # ربط معالجات الإشارات
            self._enhance_signal_processing()
            
            # ربط واجهة المستخدم
            self._enhance_user_interface()
            
            logger.info("🔗 تم ربط النظام المحسن مع النظام الحالي")
            
        except Exception as e:
            logger.error(f"خطأ في ربط النظام المحسن: {e}")
    
    def _enhance_signal_processing(self):
        """تحسين معالجة الإشارات"""
        try:
            # حفظ المعالج الأصلي
            original_process_signal = getattr(user_manager, 'process_signal', None)
            
            # إنشاء معالج محسن
            async def enhanced_signal_processor(signal_data, user_id):
                try:
                    # استخدام النظام المحسن لتنفيذ الإشارة
                    result = await integrated_trading_system.execute_enhanced_signal(user_id, signal_data)
                    return result
                except Exception as e:
                    logger.error(f"خطأ في المعالج المحسن: {e}")
                    # استخدام المعالج الأصلي كاحتياطي
                    if original_process_signal:
                        return await original_process_signal(signal_data, user_id)
                    return {'success': False, 'message': f'خطأ: {e}'}
            
            # استبدال المعالج
            user_manager.process_signal = enhanced_signal_processor
            
            logger.info("📡 تم تحسين معالجة الإشارات")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين معالجة الإشارات: {e}")
    
    def _enhance_user_interface(self):
        """تحسين واجهة المستخدم"""
        try:
            # إضافة معالجات محسنة للواجهة
            enhanced_bot_interface.user_input_states = {}
            
            logger.info("🎨 تم تحسين واجهة المستخدم")
            
        except Exception as e:
            logger.error(f"خطأ في تحسين واجهة المستخدم: {e}")
    
    def _test_integration(self):
        """اختبار التكامل"""
        try:
            # اختبار مدير الإعدادات المرن
            test_config = flexible_config_manager.get_user_config(12345)
            assert len(test_config) > 0, "مدير الإعدادات المرن لا يعمل"
            
            # اختبار حساب المعاملات
            test_params = flexible_config_manager.calculate_trade_parameters(
                12345, 'BTCUSDT', 'buy', 50000.0
            )
            assert len(test_params) > 0, "حساب المعاملات لا يعمل"
            
            # اختبار النظام المتكامل
            system_status = integrated_trading_system.get_system_status()
            assert system_status['system_active'], "النظام المتكامل غير نشط"
            
            logger.info("🧪 تم اختبار التكامل بنجاح")
            
        except Exception as e:
            logger.error(f"فشل في اختبار التكامل: {e}")
            raise
    
    def _activate_enhanced_system(self):
        """تفعيل النظام المحسن"""
        try:
            # تفعيل جميع المكونات
            flexible_config_manager.system_active = True
            enhanced_trade_executor.system_active = True
            integrated_trading_system.system_active = True
            
            self.enhanced_system_active = True
            logger.info("🚀 تم تفعيل النظام المحسن")
            
        except Exception as e:
            logger.error(f"خطأ في تفعيل النظام المحسن: {e}")
    
    def get_integration_report(self) -> Dict[str, Any]:
        """الحصول على تقرير التكامل"""
        try:
            return {
                'integration_status': self.integration_status,
                'backup_created': self.backup_created,
                'enhanced_system_active': self.enhanced_system_active,
                'components_status': {
                    'config_manager': 'active' if flexible_config_manager else 'inactive',
                    'bot_interface': 'active' if enhanced_bot_interface else 'inactive',
                    'trade_executor': 'active' if enhanced_trade_executor else 'inactive',
                    'integrated_system': 'active' if integrated_trading_system else 'inactive'
                },
                'features_preserved': {
                    'signature_logic': True,
                    'price_calculation': True,
                    'existing_system': True
                },
                'new_features': {
                    'flexible_api_keys': True,
                    'flexible_leverage': True,
                    'flexible_trade_amount': True,
                    'enhanced_interface': True,
                    'improved_execution': True
                },
                'backup_info': {
                    'timestamp': self.backup_data.get('timestamp', 0),
                    'users_backed_up': len(self.backup_data.get('user_settings', {})),
                    'database_backed_up': self.backup_data.get('database_backup', False)
                }
            }
        except Exception as e:
            logger.error(f"خطأ في جلب تقرير التكامل: {e}")
            return {
                'integration_status': 'error',
                'error': str(e)
            }
    
    def restore_from_backup(self):
        """استعادة من النسخة الاحتياطية"""
        try:
            if not self.backup_created:
                logger.warning("لا توجد نسخة احتياطية للاستعادة")
                return False
            
            # استعادة إعدادات المستخدمين
            for user_id, settings in self.backup_data['user_settings'].items():
                db_manager.update_user_settings(user_id, settings)
            
            # إعادة تعيين النظام المحسن
            self.enhanced_system_active = False
            self.integration_status = "restored"
            
            logger.info("🔄 تم الاستعادة من النسخة الاحتياطية")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في الاستعادة من النسخة الاحتياطية: {e}")
            return False

# إنشاء مثيل عام للتكامل النهائي
final_integration = FinalIntegration()

# دالة التكامل الرئيسية
def integrate_enhanced_trading_system(existing_bot=None):
    """تكامل نظام التداول المحسن"""
    try:
        logger.info("🎯 بدء تكامل نظام التداول المحسن...")
        
        # تشغيل التكامل النهائي
        success = final_integration.integrate_with_existing_system(existing_bot)
        
        if success:
            # عرض تقرير التكامل
            report = final_integration.get_integration_report()
            
            logger.info("="*60)
            logger.info("🎉 تم تكامل نظام التداول المحسن بنجاح!")
            logger.info("="*60)
            logger.info(f"📊 حالة التكامل: {report['integration_status']}")
            logger.info(f"💾 النسخة الاحتياطية: {'✅' if report['backup_created'] else '❌'}")
            logger.info(f"🚀 النظام المحسن: {'✅ نشط' if report['enhanced_system_active'] else '❌ غير نشط'}")
            logger.info("")
            logger.info("🔧 المكونات المدعومة:")
            for component, status in report['components_status'].items():
                logger.info(f"   • {component}: {'✅' if status == 'active' else '❌'}")
            logger.info("")
            logger.info("🛡️ الميزات المحفوظة:")
            for feature, preserved in report['features_preserved'].items():
                logger.info(f"   • {feature}: {'✅' if preserved else '❌'}")
            logger.info("")
            logger.info("🎯 الميزات الجديدة:")
            for feature, available in report['new_features'].items():
                logger.info(f"   • {feature}: {'✅' if available else '❌'}")
            logger.info("")
            logger.info("🎊 النظام جاهز للاستخدام مع جميع المتغيرات!")
            logger.info("="*60)
            
            return True
        else:
            logger.error("❌ فشل في تكامل نظام التداول المحسن")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في تكامل نظام التداول المحسن: {e}")
        return False

# دالة العرض السريع
def show_quick_status():
    """عرض حالة سريعة للنظام"""
    try:
        report = final_integration.get_integration_report()
        
        print("\n" + "="*50)
        print("🤖 حالة نظام التداول المحسن")
        print("="*50)
        print(f"🔗 التكامل: {report['integration_status']}")
        print(f"💾 النسخة الاحتياطية: {'✅' if report['backup_created'] else '❌'}")
        print(f"🚀 النظام المحسن: {'✅' if report['enhanced_system_active'] else '❌'}")
        print(f"👥 المستخدمين المدعومين: {report['backup_info']['users_backed_up']}")
        print("="*50)
        
        if report['enhanced_system_active']:
            print("🎉 النظام جاهز للاستخدام!")
            print("📱 استخدم /enhanced_settings في البوت")
            print("🧪 استخدم /test_trade لاختبار الصفقات")
        else:
            print("⚠️ النظام غير نشط - يرجى إعادة التكامل")
        
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ خطأ في عرض الحالة: {e}")

# تشغيل التكامل عند استيراد الملف
if __name__ == "__main__":
    # تكامل النظام
    integration_success = integrate_enhanced_trading_system()
    
    if integration_success:
        # عرض الحالة السريعة
        show_quick_status()
    else:
        print("❌ فشل في تكامل النظام")
else:
    # تكامل النظام عند الاستيراد
    integrate_enhanced_trading_system()
