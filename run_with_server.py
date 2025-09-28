#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل بوت التداول مع السيرفر المحلي والواجهة الويب
"""

import sys
import os
import threading
import asyncio
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Get PORT from environment variable (Railway will set this)
PORT = int(os.environ.get('PORT', 5000))

def send_railway_url_notification(webhook_url):
    """إرسال إشعار برابط Railway عبر تلجرام"""
    try:
        from bybit_trading_bot import TELEGRAM_TOKEN, ADMIN_USER_ID
        from telegram.ext import Application
        import asyncio
        
        async def send_message():
            try:
                application = Application.builder().token(TELEGRAM_TOKEN).build()
                message = f"🚀 بدء تشغيل بوت التداول\n\n"
                message += f"🌐 رابط استقبال الإشارات:\n{webhook_url}\n\n"
                message += f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message)
            except Exception as e:
                print(f"❌ خطأ في إرسال إشعار Railway: {e}")
        
        # تشغيل في thread منفصل
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_message())
            loop.close()
        
        threading.Thread(target=run_async, daemon=True).start()
        
    except Exception as e:
        print(f"❌ خطأ في إعداد إشعار Railway: {e}")

def main():
    """الدالة الرئيسية لتشغيل البوت والسيرفر"""
    try:
        # استيراد الوحدات المطلوبة
        from bybit_trading_bot import trading_bot, main as bot_main
        from web_server import WebServer
        from config import WEBHOOK_URL
        
        print("🚀 بدء تشغيل بوت التداول مع السيرفر...")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 المنفذ: {PORT}")
        
        # إنشاء السيرفر وربطه بالبوت
        web_server = WebServer(trading_bot)
        trading_bot.web_server = web_server
        
        print("🌐 إعداد السيرفر المحلي...")
        
        # تشغيل السيرفر في thread منفصل مع PORT من Railway
        server_thread = threading.Thread(
            target=lambda: web_server.run(debug=False, port=PORT), 
            daemon=True
        )
        server_thread.start()
        
        print("✅ تم تشغيل السيرفر بنجاح")
        
        # إعداد وإرسال إشعار برابط Webhook من Railway
        railway_url = os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            webhook_url = f"{railway_url}/webhook"
            print(f"🌐 رابط Webhook للاستقبال من Railway: {webhook_url}")
            # إرسال إشعار عبر تلجرام مع رابط Railway
            send_railway_url_notification(webhook_url)
        else:
            # استخدام الرابط من الإعدادات
            webhook_url = WEBHOOK_URL
            print(f"🌐 رابط Webhook: {webhook_url}")
            # إرسال إشعار محلي
            send_railway_url_notification(webhook_url)
        
        print("🤖 بدء تشغيل بوت التلجرام...")
        
        # تشغيل البوت الرئيسي
        # إنشاء event loop جديد للبوت
        try:
            # For Windows compatibility
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except:
            pass
            
        # تشغيل البوت في الـ event loop الرئيسي
        bot_main()
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت والسيرفر بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()