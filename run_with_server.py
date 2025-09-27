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
        from flask import Flask
        
        print("🚀 بدء تشغيل بوت التداول مع السيرفر...")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # تحديد المنفذ من متغيرات البيئة (Railway يوفر PORT)
        port = int(os.environ.get('PORT', 8080))
        webhook_port = int(os.environ.get('WEBHOOK_PORT', port + 1))
        
        # إنشاء تطبيق Flask للصحة
        health_app = Flask(__name__)
        
        @health_app.route('/health')
        def health_check():
            return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
        
        # إنشاء السيرفر وربطه بالبوت
        web_server = WebServer(trading_bot)
        trading_bot.web_server = web_server
        
        print(f"🌐 إعداد السيرفر على المنفذ {port}...")
        
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(
            target=lambda: web_server.run(host='0.0.0.0', port=webhook_port, debug=False), 
            daemon=True
        )
        server_thread.start()
        
        print("✅ تم تشغيل السيرفر بنجاح")
        print("🤖 بدء تشغيل بوت التلجرام...")
        
        # تشغيل البوت في thread منفصل
        bot_thread = threading.Thread(
            target=bot_main,
            daemon=True
        )
        bot_thread.start()
        
        print("✅ تم بدء تشغيل البوت في thread منفصل")
        
        # تشغيل تطبيق الصحة على المنفذ الرئيسي
        health_app.run(host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت والسيرفر بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()