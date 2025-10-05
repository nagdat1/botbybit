#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل بوت التداول مع السيرفر المحلي والواجهة الويب
"""

import sys
import os
import threading
import asyncio
import time
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Get PORT from environment variable (Railway will set this)
PORT = int(os.environ.get('PORT', 5000))

def send_railway_url_notification(webhook_url):
    """إرسال إشعار برابط Railway عبر تلجرام"""
    try:
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        from telegram.ext import Application
        import asyncio
        
        async def send_message():
            try:
                application = Application.builder().token(TELEGRAM_TOKEN).build()
                
                # تحديد نوع البيئة
                if "railway" in webhook_url.lower() or "railway.app" in webhook_url:
                    environment = "🚂 Railway Cloud"
                elif "render" in webhook_url.lower():
                    environment = "☁️ Render Cloud"
                else:
                    environment = "💻 Local Development"
                
                message = f"🚀 بدء تشغيل بوت التداول متعدد المستخدمين\n\n"
                message += f"🌍 البيئة: {environment}\n"
                message += f"🌐 رابط استقبال الإشارات:\n`{webhook_url}`\n\n"
                message += f"📡 استخدم هذا الرابط في TradingView لإرسال الإشارات\n"
                message += f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                message += f"✅ البوت جاهز لاستقبال الإشارات من جميع المستخدمين!\n"
                message += f"👥 البوت الآن يدعم عدد غير محدود من المستخدمين"
                
                await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message, parse_mode='Markdown')
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
        
        # طباعة معلومات البيئة
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            print(f"🚂 Railway URL: {railway_url}")
        else:
            print("💻 تشغيل محلي - لم يتم العثور على Railway URL")
        
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
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            # Ensure the URL has the correct protocol
            if not railway_url.startswith('http'):
                railway_url = f"https://{railway_url}"
            webhook_url = f"{railway_url}/webhook"
            print("=" * 60)
            print("🌐 رابط Webhook للاستقبال من Railway:")
            print(f"   {webhook_url}")
            print("=" * 60)
            # إرسال إشعار عبر تلجرام مع رابط Railway
            send_railway_url_notification(webhook_url)
        else:
            # استخدام الرابط من الإعدادات
            webhook_url = WEBHOOK_URL
            print("=" * 60)
            print("🌐 رابط Webhook:")
            print(f"   {webhook_url}")
            print("=" * 60)
            # إرسال إشعار محلي
            send_railway_url_notification(webhook_url)
        
        print("🤖 بدء تشغيل بوت التلجرام...")
        
        # تشغيل البوت في thread منفصل لتجنب تضارب event loops
        def run_bot_thread():
            """تشغيل البوت في thread منفصل"""
            try:
                # إنشاء event loop جديد للبوت
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # تشغيل البوت
                bot_main()
                
            except Exception as e:
                print(f"❌ خطأ في تشغيل البوت: {e}")
                import traceback
                traceback.print_exc()
        
        # تشغيل البوت في thread منفصل
        bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
        bot_thread.start()
        
        # انتظار إلى ما لا نهاية (السيرفر سيعمل في thread منفصل)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ تم إيقاف البوت والسيرفر بواسطة المستخدم")
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت والسيرفر بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()