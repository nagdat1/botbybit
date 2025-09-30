#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير تهيئة النظام المتكامل
"""

import os
import logging
from datetime import datetime
from system_config import get_system_config

logger = logging.getLogger(__name__)

class SystemInitializer:
    """فئة تهيئة النظام"""
    
    def __init__(self):
        """تهيئة المُهيئ"""
        self.config = get_system_config()
        self.components = {}
        self.is_initialized = False
        self.start_time = None
    
    async def initialize_system(self):
        """تهيئة النظام بالكامل"""
        try:
            logger.info("🚀 بدء تهيئة النظام المتكامل...")
            
            # تهيئة النظام بالترتيب الصحيح
            initialization_steps = [
                self._init_logging,
                self._init_database,
                self._init_security,
                self._init_api,
                self._init_user_management,
                self._init_trading,
                self._init_monitoring,
                self._init_web_server,
                self._init_telegram_bot
            ]
            
            for step in initialization_steps:
                await step()
            
            self.is_initialized = True
            self.start_time = datetime.now()
            
            logger.info("✅ تم تهيئة النظام المتكامل بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة النظام: {e}")
            self.is_initialized = False
            return False
    
    async def _init_logging(self):
        """تهيئة نظام التسجيل"""
        try:
            log_config = self.config['logging']
            
            # إعداد التسجيل
            logging.basicConfig(
                level=getattr(logging, log_config['level']),
                format=log_config['format'],
                handlers=[
                    logging.FileHandler(log_config['file'], encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
            self.components['logging'] = True
            logger.info("✅ تم تهيئة نظام التسجيل")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة نظام التسجيل: {e}")
            raise
    
    async def _init_database(self):
        """تهيئة قاعدة البيانات"""
        try:
            from database import db_manager

            # معلومات تشخيصية
            logger.info(f"تهيئة قاعدة البيانات - الكائن: {db_manager}")
            logger.info(f"نوع الكائن: {type(db_manager)}")
            logger.info(f"الإعدادات: {self.config['database']}")

            # التحقق من وجود الطريقة
            if not hasattr(db_manager, 'init_database'):
                error_msg = f"الكائن {db_manager} لا يحتوي على طريقة init_database"
                logger.error(error_msg)
                raise AttributeError(error_msg)

            # التحقق من توقيع الطريقة
            import inspect
            try:
                sig = inspect.signature(db_manager.init_database)
                logger.info(f"توقيع الطريقة: {sig}")
            except Exception as sig_error:
                logger.error(f"خطأ في الحصول على توقيع الطريقة: {sig_error}")

            # تهيئة قاعدة البيانات مع الإعدادات
            logger.info("بدء استدعاء init_database...")
            db_manager.init_database(
                url=self.config['database']['url'],
                pool_size=self.config['database']['pool_size'],
                max_overflow=self.config['database']['max_overflow']
            )
            logger.info("انتهى استدعاء init_database بنجاح")

            self.components['database'] = db_manager
            logger.info("✅ تم تهيئة قاعدة البيانات")

        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
            import traceback
            logger.error(f"تتبع الخطأ: {traceback.format_exc()}")
            raise
    
    async def _init_security(self):
        """تهيئة نظام الأمان"""
        try:
            from security_manager import security_manager
            
            # تكوين نظام الأمان
            security_manager.configure(
                max_attempts=self.config['security']['max_login_attempts'],
                timeout=self.config['security']['login_timeout'],
                rate_limit=self.config['security']['api_rate_limit'],
                allowed_ips=self.config['security']['allowed_ips']
            )
            
            # بدء المراقبة
            security_manager.start_security_monitoring()
            
            self.components['security'] = security_manager
            logger.info("✅ تم تهيئة نظام الأمان")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة نظام الأمان: {e}")
            raise
    
    async def _init_api(self):
        """تهيئة مدير API"""
        try:
            from api_manager import api_manager
            
            # تكوين مدير API
            api_manager.configure(
                version=self.config['new_system']['api_version'],
                timeout=self.config['performance']['request_timeout']
            )
            
            self.components['api'] = api_manager
            logger.info("✅ تم تهيئة مدير API")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة مدير API: {e}")
            raise
    
    async def _init_user_management(self):
        """تهيئة إدارة المستخدمين"""
        try:
            from user_manager import user_manager
            
            # تكوين إدارة المستخدمين
            user_manager.configure(
                require_verification=self.config['user_management']['require_verification'],
                session_timeout=self.config['user_management']['session_timeout'],
                max_accounts=self.config['user_management']['max_accounts'],
                demo_balance=self.config['user_management']['demo_balance']
            )
            
            self.components['user_manager'] = user_manager
            logger.info("✅ تم تهيئة إدارة المستخدمين")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة إدارة المستخدمين: {e}")
            raise
    
    async def _init_trading(self):
        """تهيئة نظام التداول"""
        try:
            from smart_trading_bot import SmartTradingBot
            
            # إنشاء وتكوين نظام التداول الذكي
            trading_bot = SmartTradingBot()
            trading_bot.configure(
                market_type=self.config['trading']['default_market_type'],
                leverage=self.config['trading']['default_leverage'],
                trade_amount=self.config['trading']['default_trade_amount'],
                risk_config=self.config['risk_management']
            )
            
            # بدء نظام التداول
            await trading_bot.start()
            
            self.components['trading'] = trading_bot
            logger.info("✅ تم تهيئة نظام التداول")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة نظام التداول: {e}")
            raise
    
    async def _init_monitoring(self):
        """تهيئة نظام المراقبة"""
        try:
            from bot_controller import bot_controller
            
            # تكوين نظام المراقبة
            bot_controller.configure(
                update_interval=self.config['monitoring']['interval'],
                price_interval=self.config['monitoring']['price_update_interval'],
                balance_interval=self.config['monitoring']['balance_update_interval']
            )
            
            # بدء المراقبة
            bot_controller.start_monitoring()
            
            self.components['monitor'] = bot_controller
            logger.info("✅ تم تهيئة نظام المراقبة")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة نظام المراقبة: {e}")
            raise
    
    async def _init_web_server(self):
        """تهيئة خادم الويب"""
        try:
            from web_server import WebServer
            
            # إنشاء وتكوين خادم الويب
            web_server = WebServer(self)
            web_server.configure(
                host=self.config['server']['host'],
                port=self.config['server']['port'],
                webhook_path=self.config['server']['webhook_path']
            )
            
            self.components['web_server'] = web_server
            logger.info("✅ تم تهيئة خادم الويب")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة خادم الويب: {e}")
            raise
    
    async def _init_telegram_bot(self):
        """تهيئة بوت التلجرام"""
        try:
            from telegram.ext import Application
            from config import TELEGRAM_TOKEN
            
            # إنشاء تطبيق التلجرام
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # تكوين التطبيق
            if self.config['telegram']['webhook_url']:
                await application.bot.set_webhook(self.config['telegram']['webhook_url'])
            
            self.components['telegram'] = application
            logger.info("✅ تم تهيئة بوت التلجرام")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة بوت التلجرام: {e}")
            raise
    
    def get_component(self, name):
        """الحصول على مكون معين"""
        return self.components.get(name)
    
    def get_status(self):
        """الحصول على حالة النظام"""
        status = {
            'is_initialized': self.is_initialized,
            'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'components': {}
        }
        
        # جمع حالة كل المكونات
        for name, component in self.components.items():
            if hasattr(component, 'get_status'):
                status['components'][name] = component.get_status()
            else:
                status['components'][name] = {'running': bool(component)}
        
        return status