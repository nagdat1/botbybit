#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق Flask الرئيسي لبوت التداول على Railway
"""

import os
import sys
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد الوحدات المطلوبة
from bybit_trading_bot import (
    trading_bot,
    start,
    handle_text_input,
    handle_callback,
    error_handler,
    TELEGRAM_TOKEN
)

# متغيرات عامة
application = None
bot = None

def create_app():
    """إنشاء وإعداد تطبيق Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'trading_bot_secret_key_2024'
    
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        return jsonify({
            "status": "running",
            "message": "بوت التداول على Bybit يعمل بنجاح",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

    @app.route('/health')
    def health_check():
        """فحص صحة التطبيق"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/telegram', methods=['POST'])
    def telegram_webhook():
        """معالجة تحديثات Telegram webhook"""
        if request.method == 'POST' and application:
            try:
                update = Update.de_json(request.get_json(force=True), application.bot)
                asyncio.run(application.update_queue.put(update))
                return 'OK'
            except Exception as e:
                print(f"خطأ في معالجة تحديث Telegram: {e}")
                return str(e), 500
        return 'Failed', 400

    @app.route('/webhook', methods=['POST'])
    def tradingview_webhook():
        """استقبال إشارات TradingView"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"status": "error", "message": "No data received"}), 400
            
            # معالجة الإشارة بشكل غير متزامن
            async def process_signal():
                try:
                    await trading_bot.process_signal(data)
                    return {"status": "success", "message": "Signal processed"}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
            
            result = asyncio.run(process_signal())
            return jsonify(result), 200 if result["status"] == "success" else 500
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return app

async def init_bot():
    """تهيئة وبدء تشغيل بوت Telegram"""
    global application
    
    try:
        # الحصول على عنوان الويب هوك من متغيرات البيئة
        DOMAIN = os.environ.get('RAILWAY_STATIC_URL')
        if not DOMAIN:
            raise ValueError("RAILWAY_STATIC_URL environment variable is not set")
        
        WEBHOOK_URL = f"https://{DOMAIN}"
        PORT = int(os.environ.get("PORT", 8080))
        
        # إعداد التطبيق
        application = (
            Application.builder()
            .token(TELEGRAM_TOKEN)
            .webhook(
                webhook_url=f"{WEBHOOK_URL}/telegram",
                allowed_updates=['message', 'callback_query']
            )
            .build()
        )
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_error_handler(error_handler)
        
        # تحديث الأزواج المتاحة
        await trading_bot.update_available_pairs()
        
        # بدء التحديث الدوري للأسعار
        async def price_update_loop():
            while True:
                try:
                    await trading_bot.update_open_positions_prices()
                    await asyncio.sleep(30)
                except Exception as e:
                    print(f"خطأ في التحديث الدوري: {e}")
                    await asyncio.sleep(60)
        
        # تشغيل التحديث الدوري في مهمة منفصلة
        asyncio.create_task(price_update_loop())
        
        # بدء الويب هوك
        await application.initialize()
        await application.start()
        print(f"✅ تم بدء تشغيل البوت")
        
        # إعداد الويب هوك
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")
        print(f"✅ تم إعداد الويب هوك على: {WEBHOOK_URL}/telegram")
        
    except Exception as e:
        print(f"❌ خطأ في تهيئة البوت: {e}")
        raise

def main():
    """الدالة الرئيسية"""
    try:
        # تهيئة البوت
        asyncio.run(init_bot())
        
        # إنشاء تطبيق Flask
        app = create_app()
        
        # الحصول على المنفذ من متغيرات البيئة
        port = int(os.environ.get("PORT", 8080))
        
        # تشغيل التطبيق
        app.run(host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()