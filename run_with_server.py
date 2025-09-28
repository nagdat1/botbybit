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

def main():
    """الدالة الرئيسية لتشغيل البوت والسيرفر"""
    try:
        # استيراد الوحدات المطلوبة
        from bybit_trading_bot import trading_bot, main as bot_main
        from web_server import WebServer
        
        print("🚀 بدء تشغيل بوت التداول مع السيرفر...")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # إنشاء السيرفر وربطه بالبوت
        web_server = WebServer(trading_bot)
        trading_bot.web_server = web_server
        
        print("🌐 إعداد السيرفر المحلي...")
        
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(
            target=lambda: web_server.run(debug=False), 
            daemon=True
        )
        server_thread.start()
        
        print("✅ تم تشغيل السيرفر بنجاح")
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