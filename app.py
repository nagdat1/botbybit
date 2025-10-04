#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق Flask الرئيسي لبوت التداول على Railway
"""

import os
import sys
import threading
import asyncio
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد الوحدات المطلوبة
from bybit_trading_bot import trading_bot
from web_server import WebServer
from config import PORT

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعدادات التطبيق
app.config['SECRET_KEY'] = 'trading_bot_secret_key_2024'

# متغيرات عامة
web_server = None
bot_thread = None

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

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال إشارات TradingView"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # معالجة الإشارة في thread منفصل
        def process_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(trading_bot.process_signal(data))
            loop.close()
        
        threading.Thread(target=process_signal_async, daemon=True).start()
        
        return jsonify({"status": "success", "message": "Signal processed"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def start_bot():
    """بدء تشغيل البوت"""
    global bot_thread
    
    def run_bot():
        """تشغيل البوت في thread منفصل"""
        try:
            # إعداد Telegram bot
            from telegram.ext import Application
            from bybit_trading_bot import (
                start, settings_menu, account_status, open_positions,
                trade_history, wallet_overview, handle_callback, 
                handle_text_input, error_handler, TELEGRAM_TOKEN
            )
            
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # إضافة المعالجات
            from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
            application.add_handler(CallbackQueryHandler(handle_callback))
            application.add_error_handler(error_handler)
            
            # تحديث الأزواج عند البدء
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(trading_bot.update_available_pairs())
                loop.close()
            except Exception as e:
                print(f"خطأ في تحديث الأزواج: {e}")
            
            # بدء التحديث الدوري للأسعار
            def start_price_updates():
                """بدء التحديث الدوري للأسعار"""
                def update_prices():
                    while True:
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(trading_bot.update_open_positions_prices())
                            loop.close()
                            threading.Event().wait(30)  # انتظار 30 ثانية
                        except Exception as e:
                            print(f"خطأ في التحديث الدوري: {e}")
                            threading.Event().wait(60)  # انتظار دقيقة في حالة الخطأ
                
                threading.Thread(target=update_prices, daemon=True).start()
            
            # بدء التحديث الدوري
            start_price_updates()
            
            # تشغيل البوت
            print("بدء تشغيل البوت...")
            application.run_polling(allowed_updates=['message', 'callback_query'])
            
        except Exception as e:
            print(f"خطأ في تشغيل البوت: {e}")
            import traceback
            traceback.print_exc()
    
    # تشغيل البوت في thread منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ تم بدء تشغيل البوت في thread منفصل")

def start_web_server():
    """بدء تشغيل السيرفر الويب"""
    global web_server
    
    try:
        # إنشاء السيرفر وربطه بالبوت
        web_server = WebServer(trading_bot)
        trading_bot.web_server = web_server
        
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(
            target=lambda: web_server.run(debug=False, port=PORT), 
            daemon=True
        )
        server_thread.start()
        
        print("✅ تم تشغيل السيرفر الويب بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل السيرفر الويب: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت التداول على Railway...")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 المنفذ: {PORT}")
    
    # بدء البوت
    start_bot()
    
    # بدء السيرفر الويب
    start_web_server()
    
    # تشغيل تطبيق Flask
    app.run(host='0.0.0.0', port=PORT, debug=False)