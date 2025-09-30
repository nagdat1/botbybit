#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة البداية الرئيسية للمشروع المتكامل
يقوم هذا الملف بتشغيل وإدارة جميع مكونات المشروع
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
import signal
import threading

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد المكونات الأساسية
from system_initializer import SystemInitializer
from config import (
    TELEGRAM_TOKEN,
    ADMIN_USER_ID,
    WEBHOOK_URL
)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemManager:
    """مدير النظام المتكامل"""
    
    def __init__(self):
        """تهيئة مدير النظام"""
        self.initializer = None
        self.components = {}
        self.stopping = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """إعداد معالجات إشارات النظام"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """معالجة إيقاف النظام"""
        if self.stopping:
            return
        
        self.stopping = True
        logger.info("⏹️ جاري إيقاف النظام بأمان...")
        
        try:
            # إيقاف المكونات بالترتيب العكسي
            if 'web_server' in self.components:
                self.components['web_server'].stop()
            
            if 'telegram' in self.components:
                self.components['telegram'].stop()
            
            if 'trading' in self.components:
                self.components['trading'].stop()
            
            logger.info("✅ تم إيقاف النظام بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إيقاف النظام: {e}")
        
        sys.exit(0)
    
    async def start(self):
        """بدء تشغيل النظام"""
        try:
            print("🚀 بدء تشغيل النظام المتكامل للتداول على Bybit...")
            print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # إنشاء وتهيئة النظام
            self.initializer = SystemInitializer()
            if not await self.initializer.initialize_system():
                raise Exception("فشل في تهيئة النظام")
            
            # حفظ المكونات الأساسية
            self.components = self.initializer.components
            
            # إعداد وتشغيل الخادم
            await self.setup_server()
            
            # تشغيل بوت التلجرام
            await self.setup_telegram()
            
            # تشغيل نظام التداول
            await self.setup_trading()
            
            logger.info("✅ تم بدء تشغيل النظام المتكامل بنجاح")
            
            # المحافظة على تشغيل النظام
            while not self.stopping:
                await asyncio.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("تم إيقاف النظام بواسطة المستخدم")
            self.handle_shutdown(None, None)
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل النظام: {e}")
            raise
    
    async def setup_server(self):
        """إعداد وتشغيل الخادم"""
        try:
            web_server = self.components.get('web_server')
            if not web_server:
                raise Exception("خادم الويب غير متاح")
            
            # تشغيل الخادم في thread منفصل
            server_thread = threading.Thread(
                target=web_server.run,
                daemon=True
            )
            server_thread.start()
            
            print("✅ تم تشغيل خادم الويب بنجاح")
            
            # إعداد وطباعة روابط Webhook
            await self.setup_webhooks()
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد الخادم: {e}")
            raise
    
    async def setup_webhooks(self):
        """إعداد روابط Webhook"""
        try:
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            if railway_url:
                if not railway_url.startswith('http'):
                    railway_url = f"https://{railway_url}"
                webhook_url = f"{railway_url}/webhook"
                environment = "🚂 Railway Cloud"
            else:
                port = self.components['web_server'].port
                webhook_url = f"http://localhost:{port}/webhook"
                environment = "💻 Local Development"
            
            print("=" * 60)
            print(f"🌐 رابط Webhook ({environment}):")
            print(f"   {webhook_url}")
            print("=" * 60)
            
            # إرسال إشعار تلجرام
            await self.send_startup_notification(webhook_url, environment)
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد Webhook: {e}")
    
    async def setup_telegram(self):
        """إعداد وتشغيل بوت التلجرام"""
        try:
            telegram = self.components.get('telegram')
            if not telegram:
                raise Exception("بوت التلجرام غير متاح")
            
            print("🤖 بدء تشغيل بوت التلجرام المتكامل...")
            
            # تشغيل البوت في نفس الـ event loop
            asyncio.create_task(
                telegram.run_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True
                )
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد بوت التلجرام: {e}")
            raise
    
    async def setup_trading(self):
        """إعداد وتشغيل نظام التداول"""
        try:
            trading = self.components.get('trading')
            if not trading:
                raise Exception("نظام التداول غير متاح")
            
            # تشغيل نظام التداول
            await trading.start()
            
            print("📈 تم بدء نظام التداول بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد نظام التداول: {e}")
            raise
    
    async def send_startup_notification(self, webhook_url, environment):
        """إرسال إشعار بدء التشغيل"""
        try:
            telegram = self.components.get('telegram')
            if not telegram or not ADMIN_USER_ID:
                return
            
            message = f"""
🚀 بدء تشغيل النظام المتكامل

🌍 البيئة: {environment}
🌐 رابط استقبال الإشارات:
`{webhook_url}`

📋 كيفية الاستخدام:
1. انسخ الرابط أعلاه
2. اذهب إلى TradingView
3. أضف الرابط في إعدادات Webhook
4. أرسل الإشارات بالصيغة:
   {{"symbol": "BTCUSDT", "action": "buy"}}

⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ النظام المتكامل جاهز للعمل!
            """
            
            await telegram.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال إشعار بدء التشغيل: {e}")

async def main():
    """نقطة البداية الرئيسية"""
    try:
        # إنشاء وتشغيل مدير النظام
        manager = SystemManager()
        await manager.start()
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل النظام: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # لتوافق Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # تشغيل النظام
    asyncio.run(main())