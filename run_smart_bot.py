#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل البوت الذكي الجديد
يدعم النظام المتكامل مع بيئات منفصلة لكل مستخدم
"""

import os
import sys
import asyncio
import threading
import logging
from datetime import datetime

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد البوت الذكي
from smart_trading_bot import smart_bot
from config import PORT, LOGGING_SETTINGS

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    handlers=[
        logging.FileHandler(LOGGING_SETTINGS['log_file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """طباعة شعار البوت"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🤖 بوت التداول الذكي على Bybit 🤖                  ║
║                                                              ║
║  ✨ ميزات البوت الجديد:                                      ║
║  • 🔗 ربط مفاتيح API لكل مستخدم بشكل منفصل                  ║
║  • ⚙️ إعدادات مخصصة لكل مستخدم                              ║
║  • 📊 إدارة الصفقات مع TP/SL متقدم                          ║
║  • 🛡️ نظام حماية شامل                                       ║
║  • 💰 تداول حقيقي وتجريبي                                   ║
║  • 📈 مراقبة الأسعار في الوقت الفعلي                        ║
║  • 🔄 واجهة ديناميكية مع InlineKeyboard                     ║
║                                                              ║
║  🚀 تم تطوير النظام ليكون وحدة متكاملة وذكية                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """فحص المتطلبات"""
    try:
        # فحص وجود الملفات المطلوبة
        required_files = [
            'smart_trading_bot.py',
            'database.py',
            'user_manager.py',
            'api_manager.py',
            'order_manager.py',
            'ui_manager.py',
            'commands.py',
            'bot_controller.py',
            'security_manager.py',
            'config.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"ملفات مفقودة: {', '.join(missing_files)}")
            return False
        
        # فحص متغيرات البيئة
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_telegram_token_here":
            logger.error("يجب تعيين TELEGRAM_TOKEN في ملف config.py")
            return False
        
        if not ADMIN_USER_ID or ADMIN_USER_ID == 0:
            logger.error("يجب تعيين ADMIN_USER_ID في ملف config.py")
            return False
        
        logger.info("✅ تم فحص المتطلبات بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"خطأ في فحص المتطلبات: {e}")
        return False

def setup_directories():
    """إعداد المجلدات المطلوبة"""
    try:
        # إنشاء مجلد قاعدة البيانات إذا لم يكن موجوداً
        db_dir = os.path.dirname('trading_bot.db')
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        log_file = LOGGING_SETTINGS['log_file']
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logger.info("✅ تم إعداد المجلدات بنجاح")
        
    except Exception as e:
        logger.error(f"خطأ في إعداد المجلدات: {e}")

async def run_bot():
    """تشغيل البوت"""
    try:
        logger.info("🚀 بدء تشغيل البوت الذكي...")
        logger.info(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # تشغيل البوت
        await smart_bot.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🔚 انتهاء تشغيل البوت")

def run_flask_server():
    """تشغيل سيرفر Flask للويب هوك"""
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return jsonify({
                "status": "running",
                "message": "البوت الذكي يعمل بنجاح",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            })
        
        @app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({"status": "error", "message": "No data received"}), 400
                
                # معالجة الإشارة في thread منفصل
                def process_signal_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    # يمكن إضافة معالجة الإشارات هنا لاحقاً
                    loop.close()
                
                threading.Thread(target=process_signal_async, daemon=True).start()
                
                return jsonify({"status": "success", "message": "Signal processed"}), 200
                
            except Exception as e:
                logger.error(f"خطأ في معالجة الويب هوك: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @app.route('/stats')
        def get_stats():
            try:
                bot_stats = smart_bot.get_bot_stats()
                return jsonify(bot_stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        logger.info(f"🌐 بدء تشغيل سيرفر Flask على المنفذ {PORT}")
        app.run(host='0.0.0.0', port=PORT, debug=False)
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل سيرفر Flask: {e}")

def main():
    """الدالة الرئيسية"""
    try:
        # طباعة الشعار
        print_banner()
        
        # فحص المتطلبات
        if not check_requirements():
            logger.error("❌ فشل في فحص المتطلبات")
            return
        
        # إعداد المجلدات
        setup_directories()
        
        # تشغيل سيرفر Flask في thread منفصل
        flask_thread = threading.Thread(target=run_flask_server, daemon=True)
        flask_thread.start()
        
        # انتظار قصير لبدء سيرفر Flask
        import time
        time.sleep(2)
        
        # تشغيل البوت الرئيسي
        asyncio.run(run_bot())
        
    except Exception as e:
        logger.error(f"خطأ في الدالة الرئيسية: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
