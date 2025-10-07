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
        data = request.get_json()
        
        print(f"🔔 [WEBHOOK شخصي] المستخدم: {user_id}")
        print(f"📊 [WEBHOOK شخصي] البيانات المستلمة: {data}")
        
        if not data:
            print(f"⚠️ [WEBHOOK شخصي] لا توجد بيانات للمستخدم {user_id}")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # التحقق من وجود user_manager
        from user_manager import user_manager
        from database import db_manager
        
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
            # إنشاء الحسابات للمستخدم
            user_manager._create_user_accounts(user_id, user_data)
            print(f"✅ [WEBHOOK شخصي] تم تحميل المستخدم {user_id} بنجاح")
        
        # التحقق من تفعيل المستخدم
        if not user_data.get('is_active', False):
            print(f"⚠️ [WEBHOOK شخصي] المستخدم {user_id} غير نشط")
            return jsonify({"status": "error", "message": f"User {user_id} is not active"}), 403
        
        print(f"✅ [WEBHOOK شخصي] المستخدم {user_id} موجود ونشط")
        print(f"📋 [WEBHOOK شخصي] إعدادات المستخدم: market_type={user_data.get('market_type')}, account_type={user_data.get('account_type')}")
        
        # معالجة الإشارة للمستخدم المحدد
        def process_user_signal_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(process_user_signal(user_id, data, user_data))
            loop.close()
        
        threading.Thread(target=process_user_signal_async, daemon=True).start()
        
        print(f"✅ [WEBHOOK شخصي] تمت معالجة إشارة المستخدم {user_id} بنجاح")
        return jsonify({
            "status": "success", 
            "message": f"Signal processed for user {user_id}",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        print(f"❌ [WEBHOOK شخصي] خطأ للمستخدم {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

async def process_user_signal(user_id: int, signal_data: dict, user_data: dict):
    """معالجة الإشارة باستخدام إعدادات المستخدم الخاصة"""
    try:
        from user_manager import user_manager
        from bybit_trading_bot import BybitAPI
        
        print(f"🔄 [معالجة الإشارة] بدء معالجة إشارة المستخدم {user_id}")
        
        # استخراج بيانات الإشارة
        symbol = signal_data.get('symbol', '').upper()
        action = signal_data.get('action', '').lower()  # buy, sell, stop, close
        price = signal_data.get('price', 0.0)
        
        print(f"📈 [معالجة الإشارة] الرمز: {symbol}, الإجراء: {action}, السعر: {price}")
        
        if not symbol or not action:
            print(f"❌ [معالجة الإشارة] بيانات غير مكتملة للمستخدم {user_id}")
            return
        
        # الحصول على إعدادات المستخدم
        market_type = user_data.get('market_type', 'spot')
        account_type = user_data.get('account_type', 'demo')
        trade_amount = user_data.get('trade_amount', 100.0)
        leverage = user_data.get('leverage', 10)
        
        print(f"⚙️ [معالجة الإشارة] الإعدادات: market={market_type}, account={account_type}, amount={trade_amount}, leverage={leverage}")
        
        # معالجة أنواع الإشارات المختلفة
        if action in ['buy', 'sell', 'long', 'short']:
            # فتح صفقة جديدة
            print(f"📝 [معالجة الإشارة] فتح صفقة {action} للمستخدم {user_id}")
            
            # تحويل long/short إلى buy/sell
            if action == 'long':
                action = 'buy'
            elif action == 'short':
                action = 'sell'
            
            success, result = user_manager.execute_user_trade(
                user_id=user_id,
                symbol=symbol,
                action=action,
                price=price if price > 0 else None,  # إذا كان السعر 0، استخدم السعر الحالي
                amount=trade_amount,
                market_type=market_type
            )
            
            if success:
                print(f"✅ [معالجة الإشارة] نجح فتح الصفقة للمستخدم {user_id}: {result}")
                
                # إرسال إشعار للمستخدم
                try:
                    from telegram.ext import Application
                    from config import TELEGRAM_TOKEN
                    
                    application = Application.builder().token(TELEGRAM_TOKEN).build()
                    message = f"""
✅ تم فتح صفقة جديدة

📊 الرمز: {symbol}
📈 النوع: {action.upper()}
💰 المبلغ: {trade_amount}
🎯 السعر: {price if price > 0 else 'السعر الحالي'}
🏪 السوق: {market_type}
                    """
                    await application.bot.send_message(chat_id=user_id, text=message)
                    print(f"📨 [معالجة الإشارة] تم إرسال إشعار للمستخدم {user_id}")
                except Exception as e:
                    print(f"⚠️ [معالجة الإشارة] فشل إرسال الإشعار: {e}")
            else:
                print(f"❌ [معالجة الإشارة] فشل فتح الصفقة للمستخدم {user_id}: {result}")
                
        elif action in ['close', 'exit', 'stop']:
            # إغلاق الصفقات المفتوحة
            print(f"📝 [معالجة الإشارة] إغلاق صفقات للمستخدم {user_id}")
            
            user_positions = user_manager.get_user_positions(user_id)
            if not user_positions:
                print(f"⚠️ [معالجة الإشارة] لا توجد صفقات مفتوحة للمستخدم {user_id}")
                return
            
            # إغلاق جميع الصفقات المتعلقة بهذا الرمز
            closed_count = 0
            for position_id, position_data in list(user_positions.items()):
                if position_data['symbol'] == symbol:
                    close_price = price if price > 0 else position_data['current_price']
                    success, result = user_manager.close_user_position(
                        user_id=user_id,
                        position_id=position_id,
                        close_price=close_price
                    )
                    
                    if success:
                        closed_count += 1
                        print(f"✅ [معالجة الإشارة] تم إغلاق الصفقة {position_id} للمستخدم {user_id}")
            
            print(f"✅ [معالجة الإشارة] تم إغلاق {closed_count} صفقة للمستخدم {user_id}")
            
            # إرسال إشعار
            try:
                from telegram.ext import Application
                from config import TELEGRAM_TOKEN
                
                application = Application.builder().token(TELEGRAM_TOKEN).build()
                message = f"""
✅ تم إغلاق الصفقات

📊 الرمز: {symbol}
🔢 عدد الصفقات المغلقة: {closed_count}
                """
                await application.bot.send_message(chat_id=user_id, text=message)
                print(f"📨 [معالجة الإشارة] تم إرسال إشعار الإغلاق للمستخدم {user_id}")
            except Exception as e:
                print(f"⚠️ [معالجة الإشارة] فشل إرسال إشعار الإغلاق: {e}")
        else:
            print(f"⚠️ [معالجة الإشارة] إجراء غير معروف '{action}' للمستخدم {user_id}")
        
    except Exception as e:
        print(f"❌ [معالجة الإشارة] خطأ في معالجة إشارة المستخدم {user_id}: {e}")
        import traceback
        traceback.print_exc()

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