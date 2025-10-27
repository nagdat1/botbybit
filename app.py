#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق Flask الرئيسي لبوت التداول على Railway
يحتوي على Webhooks لإستقبال الإشارات ويدعم تعدد المستخدمين
"""

import os
import sys
import threading
import asyncio
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد الوحدات المطلوبة
from bybit_trading_bot import trading_bot
from web_server import WebServer
from config import PORT

# استيراد النظام المحسن والنظام الجديد
try:
    from signal_system_integration import signal_system_integration, process_signal_integrated
    NEW_SYSTEM_AVAILABLE = signal_system_integration.is_available()
except ImportError as e:
    NEW_SYSTEM_AVAILABLE = False

try:
    from integrated_trading_system import IntegratedTradingSystem
    ENHANCED_SYSTEM_AVAILABLE = True
except ImportError as e:
    try:
        from systems.simple_enhanced_system import SimpleEnhancedSystem
        ENHANCED_SYSTEM_AVAILABLE = True
    except ImportError as e2:
        ENHANCED_SYSTEM_AVAILABLE = False

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعدادات التطبيق
app.config['SECRET_KEY'] = 'trading_bot_secret_key_2024'

# متغيرات عامة
web_server = None
bot_thread = None
enhanced_system = None

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    system_status = "new" if NEW_SYSTEM_AVAILABLE else ("enhanced" if ENHANCED_SYSTEM_AVAILABLE and enhanced_system else "normal")
    
    features = {}
    if NEW_SYSTEM_AVAILABLE:
        features = {
            "advanced_signal_management": True,
            "id_based_signal_linking": True,
            "account_type_support": True,
            "market_type_support": True,
            "demo_real_accounts": True,
            "spot_futures_support": True,
            "enhanced_account_manager": True,
            "complete_integration": True
        }
    elif ENHANCED_SYSTEM_AVAILABLE:
        features = {
            "advanced_risk_management": True,
            "smart_signal_processing": True,
            "optimized_trade_execution": True,
            "portfolio_management": True,
            "automatic_optimization": True
        }
    
    return jsonify({
        "status": "running",
        "message": f"بوت التداول على Bybit يعمل بنجاح - النظام: {system_status}",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0" if NEW_SYSTEM_AVAILABLE else ("2.0.0" if ENHANCED_SYSTEM_AVAILABLE else "1.0.0"),
        "system_type": system_status,
        "new_system_available": NEW_SYSTEM_AVAILABLE,
        "enhanced_features": ENHANCED_SYSTEM_AVAILABLE or NEW_SYSTEM_AVAILABLE,
        "features": features
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
    """استقبال إشارات TradingView (رابط عام)"""
    try:
        data = request.get_json()
        print(f"[WEBHOOK] Received signal: {data}")
        
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
        print(f"[WEBHOOK] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/personal/<int:user_id>/webhook', methods=['POST'])
def personal_webhook(user_id):
    """استقبال إشارات TradingView الشخصية لكل مستخدم"""
    try:
        print(f"\n{'='*60}")
        print(f"🔔 [WEBHOOK شخصي] استقبال طلب جديد")
        print(f"👤 المستخدم: {user_id}")
        print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data = request.get_json()
        print(f"📊 البيانات المستلمة: {data}")
        
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # التحقق من وجود user_manager
        from users.user_manager import user_manager
        from users.database import db_manager
        
        if user_manager is None:
            return jsonify({"status": "error", "message": "User manager not initialized"}), 500
        
        # التحقق من وجود المستخدم
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            # محاولة التحميل من قاعدة البيانات
            user_data = db_manager.get_user(user_id)
            if user_data:
                user_manager.reload_user_data(user_id)
                user_data = user_manager.get_user(user_id)
                user_manager._create_user_accounts(user_id, user_data)
        
        if not user_data:
            return jsonify({"status": "error", "message": f"User {user_id} not found"}), 404
        
        if not user_data.get('is_active', False):
            return jsonify({"status": "error", "message": f"User {user_id} is not active"}), 403
        
        # إعدادات المستخدم
        user_settings_copy = {
            'user_id': user_id,
            'market_type': user_data.get('market_type', 'spot'),
            'account_type': user_data.get('account_type', 'demo'),
            'trade_amount': user_data.get('trade_amount', 100.0),
            'leverage': user_data.get('leverage', 10)
        }
        
        # معالجة الإشارة في thread منفصل
        def process_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # تطبيق إعدادات المستخدم
                original_settings = trading_bot.user_settings.copy()
                original_user_id = trading_bot.user_id
                
                trading_bot.user_id = user_settings_copy['user_id']
                trading_bot.user_settings['market_type'] = user_settings_copy['market_type']
                trading_bot.user_settings['account_type'] = user_settings_copy['account_type']
                trading_bot.user_settings['trade_amount'] = user_settings_copy['trade_amount']
                trading_bot.user_settings['leverage'] = user_settings_copy['leverage']
                
                # معالجة الإشارة
                if NEW_SYSTEM_AVAILABLE:
                    loop.run_until_complete(process_signal_integrated(data, user_settings_copy['user_id']))
                elif ENHANCED_SYSTEM_AVAILABLE and enhanced_system:
                    enhanced_system.process_signal(user_settings_copy['user_id'], data)
                else:
                    loop.run_until_complete(trading_bot.process_signal(data))
                
                # استعادة الإعدادات
                trading_bot.user_settings.update(original_settings)
                trading_bot.user_id = original_user_id
            except Exception as e:
                print(f"❌ خطأ: {e}")
            finally:
                loop.close()
        
        threading.Thread(target=process_signal_async, daemon=True).start()
        
        return jsonify({
            "status": "success",
            "message": f"Signal processing started for user {user_id}",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

def setup_telegram_bot():
    """إعداد Telegram Bot بدون تشغيله"""
    global enhanced_system
    
    # تهيئة النظام المحسن إذا كان متاحاً
    if ENHANCED_SYSTEM_AVAILABLE:
        try:
            print("🚀 تهيئة النظام المحسن الكامل...")
            enhanced_system = IntegratedTradingSystem()
            print("✅ تم تهيئة النظام المحسن")
        except Exception as e:
            try:
                print("🚀 تهيئة النظام المحسن المبسط...")
                enhanced_system = SimpleEnhancedSystem()
                print("✅ تم تهيئة النظام المحسن")
            except Exception as e2:
                print(f"⚠️ فشل في تهيئة النظام المحسن: {e2}")
                enhanced_system = None
    else:
        print("📝 استخدام النظام العادي")
    
    # إعداد Telegram bot
    from telegram.ext import Application
    from telegram import Update
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
    
    # إضافة معالجات أوامر المنصات
    try:
        from exchange_commands import register_exchange_handlers
        register_exchange_handlers(application)
        print("✅ تم تسجيل معالجات أوامر المنصات")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
    
    return application

def send_telegram_notification(title, message_text):
    """إرسال إشعار تلجرام"""
    try:
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID
        from telegram.ext import Application
        
        def run_send():
            async def send():
                try:
                    application = Application.builder().token(TELEGRAM_TOKEN).build()
                    await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message_text)
                except Exception as e:
                    print(f"❌ خطأ في إرسال الرسالة: {e}")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send())
            loop.close()
        
        threading.Thread(target=run_send, daemon=True).start()
    except Exception as e:
        print(f"❌ خطأ: {e}")

def run_flask_in_thread():
    """تشغيل Flask في thread منفصل"""
    print("🌐 بدء تشغيل Flask server...")
    
    # إرسال رسالة عند بدء Flask Server
    message = f"""مرحبا ايها القائد

🌐 بدء سيرفر الويب
🔹 الأداة: Flask Web Server
🔹 الوظيفة: استقبال webhooks من TradingView
🔹 المنفذ: {PORT}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_telegram_notification("🌐 بدء سيرفر الويب", message)
    
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)

if __name__ == "__main__":
    # عرض معلومات النظام
    print("\n" + "="*60)
    if NEW_SYSTEM_AVAILABLE:
        print("🎯 النظام الجديد متاح!")
    elif ENHANCED_SYSTEM_AVAILABLE:
        print("🚀 النظام المحسن متاح!")
    else:
        print("📝 النظام العادي يعمل")
    print("="*60 + "\n")
    
    # إعداد وإعداد البوت
    bot_application = setup_telegram_bot()
    print("✅ تم إعداد البوت")
    
    # تشغيل Flask في thread منفصل
    flask_thread = threading.Thread(target=run_flask_in_thread, daemon=True)
    flask_thread.start()
    
    # إعطاء Flask وقت لبدء التشغيل
    time.sleep(3)
    
    # إرسال رسالة عند بدء Telegram Bot
    system_type = "Normal" if not ENHANCED_SYSTEM_AVAILABLE else ("Enhanced" if not NEW_SYSTEM_AVAILABLE else "New System")
    message = f"""مرحبا ايها القائد

🤖 بدء بوت التلجرام
🔹 الأداة: Telegram Bot
🔹 الوظيفة: استقبال الأوامر من المستخدمين
🔹 النظام: {system_type}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_telegram_notification("🤖 بدء بوت التلجرام", message)
    
    # تشغيل البوت في الـ main thread
    print("🤖 بدء تشغيل البوت...")
    bot_application.run_polling(allowed_updates=['message', 'callback_query'], drop_pending_updates=False)
