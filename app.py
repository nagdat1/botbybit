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
    """استقبال إشارات TradingView (الرابط القديم - يعمل مع المستخدم الافتراضي)"""
    try:
        data = request.get_json()
        
        print("=" * 50)
        print("📥 [OLD WEBHOOK] استقبال إشارة على الرابط القديم /webhook")
        print(f"📊 البيانات المستلمة: {data}")
        print("=" * 50)
        
        if not data:
            print("❌ خطأ: لم يتم استقبال بيانات")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # معالجة الإشارة في thread منفصل
        def process_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(trading_bot.process_signal(data))
            loop.close()
        
        threading.Thread(target=process_signal_async, daemon=True).start()
        
        print("✅ تم إرسال الإشارة للمعالجة")
        return jsonify({"status": "success", "message": "Signal processed"}), 200
        
    except Exception as e:
        print(f"❌ خطأ في معالجة الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/personal/<int:user_id>/webhook', methods=['POST'])
def personal_webhook(user_id):
    """استقبال إشارات TradingView لمستخدم محدد"""
    try:
        data = request.get_json()
        
        print("=" * 50)
        print(f"📥 [PERSONAL WEBHOOK] استقبال إشارة شخصية")
        print(f"👤 معرف المستخدم: {user_id}")
        print(f"📊 البيانات المستلمة: {data}")
        print("=" * 50)
        
        if not data:
            print(f"❌ خطأ: لم يتم استقبال بيانات للمستخدم {user_id}")
            return jsonify({
                "status": "error", 
                "message": "No data received",
                "user_id": user_id
            }), 400
        
        # استيراد user_manager
        from user_manager import user_manager
        
        # التحقق من وجود المستخدم
        if not user_manager:
            print(f"❌ خطأ: مدير المستخدمين غير متاح")
            return jsonify({
                "status": "error",
                "message": "User manager not initialized",
                "user_id": user_id
            }), 500
        
        user_data = user_manager.get_user(user_id)
        if not user_data:
            print(f"⚠️ تحذير: المستخدم {user_id} غير موجود في قاعدة البيانات")
            return jsonify({
                "status": "error",
                "message": f"User {user_id} not found",
                "user_id": user_id
            }), 404
        
        # التحقق من حالة المستخدم
        if not user_manager.is_user_active(user_id):
            print(f"⚠️ تحذير: المستخدم {user_id} غير نشط")
            return jsonify({
                "status": "error",
                "message": f"User {user_id} is not active",
                "user_id": user_id
            }), 403
        
        print(f"✅ تم التحقق من المستخدم {user_id} - الحالة: نشط")
        print(f"📋 إعدادات المستخدم: market_type={user_data.get('market_type', 'spot')}, "
              f"balance={user_data.get('balance', 0)}, "
              f"notifications={user_data.get('notifications', True)}")
        
        # معالجة الإشارة للمستخدم المحدد
        def process_user_signal_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # استخدام دالة خاصة لمعالجة إشارات المستخدمين
                loop.run_until_complete(
                    process_personal_signal(user_id, data, user_manager)
                )
                
                loop.close()
            except Exception as e:
                print(f"❌ خطأ في معالجة إشارة المستخدم {user_id}: {e}")
                import traceback
                traceback.print_exc()
        
        threading.Thread(target=process_user_signal_async, daemon=True).start()
        
        print(f"✅ تم إرسال إشارة المستخدم {user_id} للمعالجة")
        return jsonify({
            "status": "success",
            "message": f"Signal processed for user {user_id}",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        print(f"❌ خطأ في معالجة إشارة المستخدم {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "user_id": user_id
        }), 500


async def process_personal_signal(user_id: int, signal_data: dict, user_manager):
    """معالجة إشارة شخصية لمستخدم محدد"""
    try:
        print(f"🔄 بدء معالجة الإشارة للمستخدم {user_id}")
        
        # استخراج بيانات الإشارة
        symbol = signal_data.get('symbol', '').upper()
        action = signal_data.get('action', '').lower()
        price = signal_data.get('price', 0)
        
        print(f"📊 تفاصيل الإشارة: symbol={symbol}, action={action}, price={price}")
        
        if not symbol or not action:
            print(f"❌ بيانات الإشارة غير مكتملة للمستخدم {user_id}")
            return
        
        # الحصول على إعدادات المستخدم
        user_data = user_manager.get_user(user_id)
        if not user_data:
            print(f"❌ فشل في الحصول على بيانات المستخدم {user_id}")
            return
        
        market_type = user_data.get('market_type', 'spot')
        trade_amount = user_data.get('trade_amount', 100.0)
        
        print(f"⚙️ إعدادات التداول: market_type={market_type}, trade_amount={trade_amount}")
        
        # معالجة الإشارة حسب نوع العملية
        if action in ['buy', 'sell']:
            print(f"📈 تنفيذ صفقة {action} للمستخدم {user_id}")
            
            # تنفيذ الصفقة
            success, result = user_manager.execute_user_trade(
                user_id=user_id,
                symbol=symbol,
                action=action,
                price=price if price > 0 else 1.0,  # استخدام سعر افتراضي إذا لم يتم توفيره
                amount=trade_amount,
                market_type=market_type
            )
            
            if success:
                print(f"✅ تم تنفيذ الصفقة بنجاح للمستخدم {user_id}: {result}")
                
                # إرسال إشعار إذا كان مفعلاً
                if user_data.get('notifications', True):
                    try:
                        await send_notification_to_user(
                            user_id,
                            f"✅ تم تنفيذ صفقة {action} على {symbol} بسعر {price}"
                        )
                    except Exception as e:
                        print(f"⚠️ فشل إرسال الإشعار: {e}")
            else:
                print(f"❌ فشل تنفيذ الصفقة للمستخدم {user_id}: {result}")
                
        elif action in ['close', 'exit', 'stop']:
            print(f"📉 إغلاق صفقة للمستخدم {user_id}")
            
            # إغلاق جميع صفقات الرمز
            user_positions = user_manager.get_user_positions(user_id)
            closed_count = 0
            
            for position_id, position_data in list(user_positions.items()):
                if position_data['symbol'] == symbol:
                    success, result = user_manager.close_user_position(
                        user_id=user_id,
                        position_id=position_id,
                        close_price=price if price > 0 else position_data.get('current_price', 1.0)
                    )
                    
                    if success:
                        closed_count += 1
                        print(f"✅ تم إغلاق الصفقة {position_id} للمستخدم {user_id}")
                        
                        # إرسال إشعار
                        if user_data.get('notifications', True):
                            try:
                                pnl = result.get('pnl', 0)
                                await send_notification_to_user(
                                    user_id,
                                    f"✅ تم إغلاق صفقة {symbol} - الربح/الخسارة: {pnl:.2f}"
                                )
                            except Exception as e:
                                print(f"⚠️ فشل إرسال الإشعار: {e}")
            
            print(f"📊 تم إغلاق {closed_count} صفقة للمستخدم {user_id}")
        
        else:
            print(f"⚠️ نوع إشارة غير معروف للمستخدم {user_id}: {action}")
            
    except Exception as e:
        print(f"❌ خطأ في معالجة الإشارة الشخصية للمستخدم {user_id}: {e}")
        import traceback
        traceback.print_exc()


async def send_notification_to_user(user_id: int, message: str):
    """إرسال إشعار للمستخدم عبر Telegram"""
    try:
        from bybit_trading_bot import application
        if application:
            await application.bot.send_message(
                chat_id=user_id,
                text=message
            )
    except Exception as e:
        print(f"خطأ في إرسال الإشعار للمستخدم {user_id}: {e}")

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