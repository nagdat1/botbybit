#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة الدخول الرئيسية للتطبيق - تشغيل السيرفر والبوت معاً
"""

import os
import asyncio
import threading
from run_with_server import IntegratedTradingBot, logger
from web_server_new import create_app

async def run_bot():
    try:
        # إنشاء وتهيئة البوت
        bot = IntegratedTradingBot()
        await bot.initialize()
        
        # تشغيل بوت التلجرام في خلفية
        def run_telegram_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.start_telegram_bot())
            loop.close()
        
        telegram_thread = threading.Thread(target=run_telegram_bot)
        telegram_thread.start()
        
        return bot
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        raise

def create_integrated_app():
    """إنشاء تطبيق Flask مع البوت المتكامل"""
    try:
        # تشغيل البوت
        bot = asyncio.run(run_bot())
        
        # إنشاء تطبيق Flask مع البوت
        app = create_app(bot)
        
        return app
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء التطبيق المتكامل: {e}")
        raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app = create_integrated_app()
    app.run(host='0.0.0.0', port=port)