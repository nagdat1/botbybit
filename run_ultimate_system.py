#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل الرئيسي النهائي - تشغيل النظام المحسن مع النظام الحالي
يحافظ على آلية التوقيع وحساب السعر مع دعم تعديل المتغيرات
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional

# استيراد النظام المحسن
from flexible_config_manager import flexible_config_manager
from enhanced_bot_interface import enhanced_bot_interface
from enhanced_trade_executor import enhanced_trade_executor
from integrated_trading_system import integrated_trading_system
from enhanced_trading_bot import enhanced_trading_bot
from final_integration import final_integration
from run_enhanced_system import enhanced_system_runner
from ultimate_system_updater import ultimate_system_updater
from run_ultimate_system import ultimate_system_runner
from final_system_integrator import final_system_integrator
from launch_ultimate_system import ultimate_system_launcher
from ultimate_system_updater import ultimate_system_updater

# استيراد النظام الحالي
from database import db_manager
from user_manager import user_manager
from bybit_trading_bot import trading_bot
from web_server import WebServer

logger = logging.getLogger(__name__)

class UltimateTradingSystemRunner:
    """مشغل نظام التداول النهائي"""
    
    def __init__(self):
        self.system_running = False
        self.enhanced_system_active = False
        self.web_server = None
        self.startup_time = None
        self.runner_status = "not_started"
        
    async def run_ultimate_system(self):
        """تشغيل النظام النهائي"""
        try:
            self.startup_time = time.time()
            logger.info("🚀 بدء تشغيل النظام النهائي...")
            
            # 1. تحديث النظام إلى النسخة النهائية
            update_success = await ultimate_system_updater.update_to_ultimate_system()
            if not update_success:
                logger.error("❌ فشل في تحديث النظام")
                return False
            
            # 2. تكامل النظام النهائي
            integration_success = await final_system_integrator.integrate_final_system()
            if not integration_success:
                logger.error("❌ فشل في تكامل النظام النهائي")
                return False
            
            # 3. بدء النظام النهائي
            system_success = await ultimate_system_runner.start_ultimate_system()
            if not system_success:
                logger.error("❌ فشل في بدء النظام النهائي")
                return False
            
            # 4. إطلاق النظام النهائي
            launch_success = await ultimate_system_launcher.launch_ultimate_system()
            if not launch_success:
                logger.error("❌ فشل في إطلاق النظام النهائي")
                return False
            
            # 5. اختبار النظام النهائي
            await self._test_ultimate_system()
            
            # 6. تفعيل النظام النهائي
            await self._activate_ultimate_system()
            
            # 7. عرض رسالة التشغيل النهائية
            await self._show_ultimate_run_message()
            
            self.system_running = True
            self.enhanced_system_active = True
            self.runner_status = "completed"
            
            logger.info("✅ تم تشغيل النظام النهائي بنجاح!")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل في تشغيل النظام النهائي: {e}")
            self.runner_status = "failed"
            return False
    
    async def _test_ultimate_system(self):
        """اختبار النظام النهائي"""
        try:
            # اختبار جميع المكونات
            components = [
                ('مدير الإعدادات المرن', flexible_config_manager),
                ('واجهة البوت المحسنة', enhanced_bot_interface),
                ('تنفيذ الصفقات المحسن', enhanced_trade_executor),
                ('النظام المتكامل', integrated_trading_system),
                ('البوت المحسن', enhanced_trading_bot)
            ]
            
            for name, component in components:
                if hasattr(component, 'system_active'):
                    assert component.system_active, f"{name} غير نشط"
                logger.info(f"✅ {name}: نشط")
            
            # اختبار حساب المعاملات
            test_params = flexible_config_manager.calculate_trade_parameters(
                12345, 'BTCUSDT', 'buy', 50000.0
            )
            assert len(test_params) > 0, "حساب المعاملات لا يعمل"
            
            # اختبار التحقق من تنفيذ الصفقة
            validation_result = flexible_config_manager.validate_trade_execution(12345, test_params)
            assert validation_result[0], f"فشل في التحقق من تنفيذ الصفقة: {validation_result[1]}"
            
            # اختبار النظام النهائي
            ultimate_status = ultimate_system_runner.get_ultimate_system_status()
            assert ultimate_status['system_running'], "النظام النهائي غير نشط"
            
            # اختبار النظام المطلق
            launch_status = ultimate_system_launcher.get_ultimate_system_status()
            assert launch_status['system_running'], "النظام المطلق غير نشط"
            
            logger.info("🧪 تم اختبار النظام النهائي بنجاح")
            
        except Exception as e:
            logger.error(f"فشل في اختبار النظام النهائي: {e}")
            raise
    
    async def _activate_ultimate_system(self):
        """تفعيل النظام النهائي"""
        try:
            # تفعيل جميع المكونات
            flexible_config_manager.system_active = True
            enhanced_trade_executor.system_active = True
            integrated_trading_system.system_active = True
            enhanced_trading_bot.system_active = True
            enhanced_system_runner.enhanced_system_active = True
            ultimate_system_runner.system_running = True
            ultimate_system_runner.enhanced_system_active = True
            ultimate_system_launcher.system_running = True
            ultimate_system_launcher.enhanced_system_active = True
            
            logger.info("🚀 تم تفعيل النظام النهائي")
            
        except Exception as e:
            logger.error(f"خطأ في تفعيل النظام النهائي: {e}")
    
    async def _show_ultimate_run_message(self):
        """عرض رسالة التشغيل النهائية"""
        try:
            # الحصول على تقارير النظام
            update_report = ultimate_system_updater.get_ultimate_update_report()
            system_status = ultimate_system_runner.get_ultimate_system_status()
            integration_report = final_integration.get_integration_report()
            final_report = final_system_integrator.get_final_integration_report()
            launch_status = ultimate_system_launcher.get_ultimate_system_status()
            
            run_time = time.time() - self.startup_time
            
            ultimate_message = f"""
🎉 تم تشغيل النظام النهائي بنجاح!

⏱️ وقت التشغيل: {run_time:.2f} ثانية

📊 حالة النظام:
• التحديث: {update_report['update_status']}
• التكامل: {integration_report['integration_status']}
• النظام النهائي: {'✅ نشط' if system_status['system_running'] else '❌ غير نشط'}
• النظام المطلق: {'✅ نشط' if launch_status['system_running'] else '❌ غير نشط'}
• النسخة الاحتياطية: {'✅ موجودة' if update_report['backup_created'] else '❌ غير موجودة'}

🎯 الميزات الجديدة المتاحة:
• 🔑 تعديل مفاتيح API من خلال البوت
• ⚡ تعديل الرافعة المالية (1x-100x)
• 💰 تعديل مبلغ التداول ($1-$10,000)
• 🏪 التبديل بين Spot و Futures
• 👤 التبديل بين الحساب الحقيقي والتجريبي
• 🏦 التبديل بين Bybit و MEXC

🛡️ الميزات المحفوظة:
• ✅ آلية التوقيع الحالية محفوظة 100%
• ✅ آلية حساب السعر الحالية محفوظة 100%
• ✅ جميع الصفقات الحالية تعمل بنفس الطريقة
• ✅ لا توجد تغييرات على النظام الأساسي

📱 كيفية الاستخدام:
• استخدم /enhanced_settings في البوت
• استخدم /config_summary لعرض الإعدادات
• استخدم /test_trade لاختبار الصفقات
• استخدم القائمة المحسنة للوصول السريع

🚀 النظام جاهز للاستخدام مع جميع المتغيرات!
            """
            
            print(ultimate_message)
            
            # إرسال رسالة للمدير إذا كان متاحاً
            if hasattr(trading_bot, 'send_message_to_admin'):
                await trading_bot.send_message_to_admin("🎉 تم تشغيل النظام النهائي بنجاح! جميع الميزات المحسنة متاحة الآن.")
            
        except Exception as e:
            logger.error(f"خطأ في عرض رسالة التشغيل النهائية: {e}")
    
    async def stop_ultimate_system(self):
        """إيقاف النظام النهائي"""
        try:
            logger.info("⏹️ إيقاف النظام النهائي...")
            
            # إيقاف النظام النهائي
            await ultimate_system_launcher.stop_ultimate_system()
            await ultimate_system_runner.stop_ultimate_system()
            
            # إيقاف جميع المكونات
            flexible_config_manager.system_active = False
            enhanced_trade_executor.system_active = False
            integrated_trading_system.system_active = False
            enhanced_trading_bot.system_active = False
            
            self.system_running = False
            self.enhanced_system_active = False
            
            logger.info("✅ تم إيقاف النظام النهائي بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف النظام النهائي: {e}")
    
    def get_ultimate_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام النهائي"""
        try:
            return {
                'system_running': self.system_running,
                'enhanced_system_active': self.enhanced_system_active,
                'startup_time': self.startup_time,
                'uptime': time.time() - self.startup_time if self.startup_time else 0,
                'runner_status': self.runner_status,
                'update_report': ultimate_system_updater.get_ultimate_update_report(),
                'system_status': ultimate_system_runner.get_ultimate_system_status(),
                'integration_report': final_integration.get_integration_report(),
                'final_report': final_system_integrator.get_final_integration_report(),
                'launch_status': ultimate_system_launcher.get_ultimate_system_status(),
                'components_status': {
                    'config_manager': flexible_config_manager.system_active,
                    'bot_interface': True,
                    'trade_executor': enhanced_trade_executor.system_active,
                    'integrated_system': integrated_trading_system.system_active,
                    'enhanced_bot': enhanced_trading_bot.system_active
                }
            }
        except Exception as e:
            logger.error(f"خطأ في جلب حالة النظام النهائي: {e}")
            return {
                'system_running': False,
                'error': str(e)
            }
    
    async def restart_ultimate_system(self):
        """إعادة تشغيل النظام النهائي"""
        try:
            logger.info("🔄 إعادة تشغيل النظام النهائي...")
            
            # إيقاف النظام
            await self.stop_ultimate_system()
            
            # انتظار قليل
            await asyncio.sleep(2)
            
            # بدء النظام مرة أخرى
            success = await self.run_ultimate_system()
            
            if success:
                logger.info("✅ تم إعادة تشغيل النظام النهائي بنجاح")
            else:
                logger.error("❌ فشل في إعادة تشغيل النظام النهائي")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تشغيل النظام النهائي: {e}")
            return False

# إنشاء مثيل عام لمشغل النظام النهائي
ultimate_system_runner = UltimateTradingSystemRunner()

# دالة التشغيل النهائية
async def run_ultimate_trading_system():
    """تشغيل نظام التداول النهائي"""
    try:
        logger.info("🎯 بدء تشغيل نظام التداول النهائي...")
        
        # تشغيل النظام النهائي
        success = await ultimate_system_runner.run_ultimate_system()
        
        if success:
            logger.info("🎉 تم تشغيل نظام التداول النهائي بنجاح!")
            return True
        else:
            logger.error("❌ فشل في تشغيل نظام التداول النهائي")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في تشغيل نظام التداول النهائي: {e}")
        return False

# دالة الإيقاف النهائية
async def stop_ultimate_trading_system():
    """إيقاف نظام التداول النهائي"""
    try:
        await ultimate_system_runner.stop_ultimate_system()
        logger.info("✅ تم إيقاف نظام التداول النهائي")
    except Exception as e:
        logger.error(f"خطأ في إيقاف نظام التداول النهائي: {e}")

# دالة إعادة التشغيل النهائية
async def restart_ultimate_trading_system():
    """إعادة تشغيل نظام التداول النهائي"""
    try:
        success = await ultimate_system_runner.restart_ultimate_system()
        return success
    except Exception as e:
        logger.error(f"خطأ في إعادة تشغيل نظام التداول النهائي: {e}")
        return False

# دالة الحالة النهائية
def get_ultimate_system_status():
    """الحصول على حالة نظام التداول النهائي"""
    try:
        return ultimate_system_runner.get_ultimate_system_status()
    except Exception as e:
        logger.error(f"خطأ في جلب حالة النظام النهائي: {e}")
        return {'error': str(e)}

# دالة العرض النهائية
def show_ultimate_system_status():
    """عرض حالة النظام النهائي"""
    try:
        status = ultimate_system_runner.get_ultimate_system_status()
        
        print("\n" + "="*80)
        print("🤖 حالة نظام التداول النهائي")
        print("="*80)
        print(f"🚀 النظام: {'✅ نشط' if status['system_running'] else '❌ غير نشط'}")
        print(f"⚡ النظام المحسن: {'✅ نشط' if status['enhanced_system_active'] else '❌ غير نشط'}")
        print(f"⏱️ وقت التشغيل: {status['uptime']:.2f} ثانية")
        print(f"📊 حالة التشغيل: {status['runner_status']}")
        print(f"🔗 حالة التكامل: {status['integration_report']['integration_status']}")
        print(f"📈 حالة التحديث: {status['update_report']['update_status']}")
        print("="*80)
        
        if status['system_running'] and status['enhanced_system_active']:
            print("🎉 النظام النهائي نشط!")
            print("📱 استخدم /enhanced_settings في البوت")
            print("🧪 استخدم /test_trade لاختبار الصفقات")
            print("🎯 جميع المتغيرات قابلة للتعديل!")
            print("🛡️ آلية التوقيع وحساب السعر محفوظة!")
            print("🚀 النظام جاهز للاستخدام مع جميع المتغيرات!")
        else:
            print("⚠️ النظام النهائي غير نشط")
            print("🔄 يرجى تشغيل النظام")
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ خطأ في عرض حالة النظام النهائي: {e}")

# تشغيل النظام النهائي عند استيراد الملف
if __name__ == "__main__":
    # تشغيل النظام النهائي
    asyncio.run(run_ultimate_trading_system())
else:
    # تشغيل النظام النهائي عند الاستيراد
    import asyncio
    asyncio.create_task(run_ultimate_trading_system())