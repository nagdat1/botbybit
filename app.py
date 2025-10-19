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

# استيراد النظام المحسن
try:
    from integrated_trading_system import IntegratedTradingSystem
    ENHANCED_SYSTEM_AVAILABLE = True
    print("✅ النظام المحسن الكامل متاح")
except ImportError as e:
    try:
        from simple_enhanced_system import SimpleEnhancedSystem
        ENHANCED_SYSTEM_AVAILABLE = True
        print("✅ النظام المحسن المبسط متاح")
    except ImportError as e2:
        ENHANCED_SYSTEM_AVAILABLE = False
        print(f"⚠️ النظام المحسن غير متاح: {e2}")
        print("📝 سيتم استخدام النظام العادي")

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
    system_status = "enhanced" if ENHANCED_SYSTEM_AVAILABLE and enhanced_system else "normal"
    
    return jsonify({
        "status": "running",
        "message": f"بوت التداول على Bybit يعمل بنجاح - النظام: {system_status}",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0" if ENHANCED_SYSTEM_AVAILABLE else "1.0.0",
        "system_type": system_status,
        "enhanced_features": ENHANCED_SYSTEM_AVAILABLE,
        "features": {
            "advanced_risk_management": ENHANCED_SYSTEM_AVAILABLE,
            "smart_signal_processing": ENHANCED_SYSTEM_AVAILABLE,
            "optimized_trade_execution": ENHANCED_SYSTEM_AVAILABLE,
            "portfolio_management": ENHANCED_SYSTEM_AVAILABLE,
            "automatic_optimization": ENHANCED_SYSTEM_AVAILABLE
        } if ENHANCED_SYSTEM_AVAILABLE else {}
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
    """استقبال إشارات TradingView (الرابط القديم - يستخدم الإعدادات الافتراضية)"""
    try:
        data = request.get_json()
        
        print(f"🔔 [WEBHOOK القديم] استقبال إشارة: {data}")
        
        if not data:
            print("⚠️ [WEBHOOK القديم] لا توجد بيانات")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # معالجة الإشارة في thread منفصل
        def process_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(trading_bot.process_signal(data))
            loop.close()
        
        threading.Thread(target=process_signal_async, daemon=True).start()
        
        print(f"✅ [WEBHOOK القديم] تمت معالجة الإشارة بنجاح")
        return jsonify({"status": "success", "message": "Signal processed"}), 200
        
    except Exception as e:
        print(f"❌ [WEBHOOK القديم] خطأ: {e}")
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
        print(f"📋 نوع البيانات: {type(data)}")
        print(f"{'='*60}\n")
        
        if not data:
            print(f"⚠️ [WEBHOOK شخصي] لا توجد بيانات للمستخدم {user_id}")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # التحقق من وجود user_manager
        from user_manager import user_manager
        from database import db_manager
        
        # التأكد من تهيئة user_manager
        if user_manager is None:
            print(f"❌ [WEBHOOK شخصي] user_manager غير مهيأ")
            return jsonify({"status": "error", "message": "User manager not initialized"}), 500
        
        if not user_manager:
            print(f"❌ [WEBHOOK شخصي] user_manager غير متاح للمستخدم {user_id}")
            return jsonify({"status": "error", "message": "User manager not initialized"}), 500
        
        # التحقق من وجود المستخدم في الذاكرة
        user_data = user_manager.get_user(user_id)
        
        # إذا لم يكن موجودًا في الذاكرة، تحقق من قاعدة البيانات مباشرة
        if not user_data:
            print(f"⚠️ [WEBHOOK شخصي] المستخدم {user_id} غير موجود في الذاكرة، جاري التحقق من قاعدة البيانات...")
            user_data = db_manager.get_user(user_id)
            
            if not user_data:
                print(f"❌ [WEBHOOK شخصي] المستخدم {user_id} غير موجود في قاعدة البيانات")
                return jsonify({"status": "error", "message": f"User {user_id} not found. Please start the bot first with /start"}), 404
            
            # إعادة تحميل المستخدم في الذاكرة
            print(f"✅ [WEBHOOK شخصي] تم العثور على المستخدم {user_id} في قاعدة البيانات، جاري التحميل...")
            user_manager.reload_user_data(user_id)
            # إنشاء الحسابات للمستخدم (استخدام البيانات المُعاد تحميلها)
            user_data = user_manager.get_user(user_id)  # الحصول على البيانات المُحدثة
            user_manager._create_user_accounts(user_id, user_data)
            print(f"✅ [WEBHOOK شخصي] تم تحميل المستخدم {user_id} بنجاح")
        
        # التحقق من تفعيل المستخدم
        if not user_data.get('is_active', False):
            print(f"⚠️ [WEBHOOK شخصي] المستخدم {user_id} غير نشط")
            return jsonify({"status": "error", "message": f"User {user_id} is not active"}), 403
        
        print(f"✅ [WEBHOOK شخصي] المستخدم {user_id} موجود ونشط")
        print(f"📋 [WEBHOOK شخصي] إعدادات المستخدم: market_type={user_data.get('market_type')}, account_type={user_data.get('account_type')}")
        
        # استيراد trading_bot
        from bybit_trading_bot import trading_bot
        
        # نسخ بيانات المستخدم للاستخدام في الـ thread
        user_settings_copy = {
            'user_id': user_id,
            'market_type': user_data.get('market_type', 'spot'),
            'account_type': user_data.get('account_type', 'demo'),
            'trade_amount': user_data.get('trade_amount', 100.0),
            'leverage': user_data.get('leverage', 10)
        }
        
        # معالجة الإشارة في thread منفصل مع إعدادات المستخدم
        def process_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # حفظ الإعدادات الأصلية داخل الـ thread
            original_settings = trading_bot.user_settings.copy()
            original_user_id = trading_bot.user_id
            
            try:
                # تطبيق إعدادات المستخدم المحدد
                trading_bot.user_id = user_settings_copy['user_id']
                trading_bot.user_settings['market_type'] = user_settings_copy['market_type']
                trading_bot.user_settings['account_type'] = user_settings_copy['account_type']
                trading_bot.user_settings['trade_amount'] = user_settings_copy['trade_amount']
                trading_bot.user_settings['leverage'] = user_settings_copy['leverage']
                
                print(f"✅ [WEBHOOK شخصي - Thread] تم تطبيق إعدادات المستخدم {user_settings_copy['user_id']}")
                
                # معالجة الإشارة باستخدام النظام المحسن أو النظام العادي
                if ENHANCED_SYSTEM_AVAILABLE and enhanced_system:
                    print("🚀 معالجة الإشارة باستخدام النظام المحسن...")
                    result = enhanced_system.process_signal(user_settings_copy['user_id'], data)
                    print(f"✅ [WEBHOOK محسن - Thread] تمت معالجة الإشارة للمستخدم {user_settings_copy['user_id']}: {result}")
                else:
                    print("📝 معالجة الإشارة باستخدام النظام العادي...")
                    loop.run_until_complete(trading_bot.process_signal(data))
                    print(f"✅ [WEBHOOK عادي - Thread] تمت معالجة الإشارة للمستخدم {user_settings_copy['user_id']}")
            except Exception as e:
                print(f"❌ [WEBHOOK شخصي - Thread] خطأ في معالجة الإشارة: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # استعادة الإعدادات الأصلية
                trading_bot.user_settings.update(original_settings)
                trading_bot.user_id = original_user_id
                loop.close()
                print(f"✅ [WEBHOOK شخصي - Thread] تم استعادة الإعدادات الأصلية")
        
        threading.Thread(target=process_signal_async, daemon=True).start()
        
        print(f"✅ [WEBHOOK شخصي] تم بدء معالجة إشارة المستخدم {user_id}")
        
        return jsonify({
            "status": "success", 
            "message": f"Signal processing started for user {user_id}",
            "user_id": user_id,
            "system_type": "enhanced" if ENHANCED_SYSTEM_AVAILABLE and enhanced_system else "normal",
            "enhanced_features": ENHANCED_SYSTEM_AVAILABLE
        }), 200
        
    except Exception as e:
        print(f"❌ [WEBHOOK شخصي] خطأ للمستخدم {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# تم حذف دالة process_user_signal القديمة - الآن نستخدم trading_bot.process_signal مباشرة

def start_bot():
    """بدء تشغيل البوت"""
    global bot_thread, enhanced_system
    
    def run_bot():
        """تشغيل البوت في thread منفصل"""
        try:
            # تهيئة النظام المحسن إذا كان متاحاً
            if ENHANCED_SYSTEM_AVAILABLE:
                try:
                    print("🚀 تهيئة النظام المحسن الكامل...")
                    enhanced_system = IntegratedTradingSystem()
                    print("✅ تم تهيئة النظام المحسن الكامل بنجاح")
                except Exception as e:
                    try:
                        print("🚀 تهيئة النظام المحسن المبسط...")
                        enhanced_system = SimpleEnhancedSystem()
                        print("✅ تم تهيئة النظام المحسن المبسط بنجاح")
                    except Exception as e2:
                        print(f"⚠️ فشل في تهيئة النظام المحسن: {e2}")
                        enhanced_system = None
            else:
                print("📝 استخدام النظام العادي")
            
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
            
            # إضافة معالجات أوامر المنصات (Bybit & MEXC)
            try:
                from exchange_commands import register_exchange_handlers
                register_exchange_handlers(application)
                print("✅ تم تسجيل معالجات أوامر المنصات")
            except Exception as e:
                print(f"⚠️ خطأ في تسجيل معالجات المنصات: {e}")
            
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
    """بدء تشغيل السيرفر الويب - لن يتم استخدامه في app.py"""
    pass

if __name__ == "__main__":
    # إرسال رسالة الترحيب
    def send_startup_notification():
        """إرسال رسالة الترحيب عبر تلجرام"""
        try:
            from config import TELEGRAM_TOKEN, ADMIN_USER_ID
            from telegram.ext import Application
            import os
            
            async def send_message():
                try:
                    application = Application.builder().token(TELEGRAM_TOKEN).build()
                    
                    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
                    if railway_url:
                        if not railway_url.startswith('http'):
                            railway_url = f"https://{railway_url}"
                        webhook_url = railway_url
                        environment = "🚂 Railway Cloud"
                    else:
                        webhook_url = f"http://localhost:{PORT}"
                        environment = "💻 Local Development"
                    
                    message = f"مرحبا ايها القائد\n⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message, parse_mode='Markdown')
                except Exception as e:
                    pass
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_message())
            loop.close()
            
        except Exception as e:
            pass
    
    # بدء البوت
    start_bot()
    
    # إرسال رسالة الترحيب
    threading.Thread(target=send_startup_notification, daemon=True).start()
    
    # عرض معلومات النظام
    print("\n" + "="*60)
    if ENHANCED_SYSTEM_AVAILABLE:
        print("🚀 النظام المحسن متاح!")
        print("✨ الميزات المتقدمة:")
        print("   • إدارة مخاطر متقدمة")
        print("   • معالجة إشارات ذكية")
        print("   • تنفيذ صفقات محسن")
        print("   • إدارة محفظة متقدمة")
        print("   • تحسين تلقائي")
    else:
        print("📝 النظام العادي يعمل")
        print("⚠️ النظام المحسن غير متاح")
    print("="*60 + "\n")
    
    # تشغيل تطبيق Flask الرئيسي
    app.run(host='0.0.0.0', port=PORT, debug=False)