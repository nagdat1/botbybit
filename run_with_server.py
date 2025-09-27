#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل بوت التداول مع السيرفر المحلي والواجهة الويب
محدث للعمل على Railway
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
        print("🚀 بدء تشغيل بوت التداول مع السيرفر...")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # طباعة متغيرات البيئة المهمة للتصحيح
        print(f"🔧 PORT environment variable: {os.environ.get('PORT', 'Not set')}")
        print(f"🔧 RAILWAY_PROJECT_ID: {os.environ.get('RAILWAY_PROJECT_ID', 'Not set')}")
        print(f"🔧 RAILWAY_PUBLIC_URL: {os.environ.get('RAILWAY_PUBLIC_URL', 'Not set')}")
        
        # استيراد الوحدات المطلوبة
        from bybit_trading_bot import trading_bot, main as bot_main
        from web_server import WebServer
        
        # إنشاء السيرفر وربطه بالبوت
        web_server = WebServer(trading_bot)
        # تعيين السيرفر للبوت باستخدام setattr لتجنب أخطاء linter
        setattr(trading_bot, 'web_server', web_server)
        
        print("🌐 إعداد السيرفر المحلي...")
        
        # الحصول على منفذ Railway أو استخدام 5000 كافتراضي
        port = int(os.environ.get('PORT', 5000))
        
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(
            target=lambda: web_server.run(host='0.0.0.0', port=port, debug=False), 
            daemon=True
        )
        server_thread.start()
        
        print(f"✅ تم تشغيل السيرفر بنجاح على المنفذ {port}")
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