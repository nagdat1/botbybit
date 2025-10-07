#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سيرفر ويب محلي لعرض بيانات التداول والرسوم البيانية
مع دعم التحديثات المباشرة عبر WebSocket
"""

import os
import time
import json
import threading
import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
import pandas as pd
import requests

# استيراد إعدادات البوت
from config import *

class WebServer:
    def __init__(self, trading_bot):
        self.trading_bot = trading_bot
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'trading_bot_secret_key_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # بيانات للرسوم البيانية
        self.chart_data = {
            'prices': [],
            'timestamps': [],
            'signals': [],
            'trades': [],
            'balance_history': []
        }
        
        self.setup_routes()
        self.setup_socketio_events()
        
    def setup_routes(self):
        """إعداد المسارات"""
        
        @self.app.route('/')
        def dashboard():
            """الصفحة الرئيسية - لوحة التحكم"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/bot_status')
        def bot_status():
            """الحصول على حالة البوت"""
            account = self.trading_bot.get_current_account()
            account_info = account.get_account_info()
            
            return jsonify({
                'is_running': self.trading_bot.is_running,
                'signals_received': self.trading_bot.signals_received,
                'open_positions': len(self.trading_bot.open_positions),
                'account_type': self.trading_bot.user_settings['account_type'],
                'market_type': self.trading_bot.user_settings['market_type'],
                'balance': account_info['balance'],
                'total_trades': account_info['total_trades'],
                'win_rate': account_info['win_rate'],
                'winning_trades': account_info['winning_trades'],
                'losing_trades': account_info['losing_trades']
            })
        
        @self.app.route('/api/chart_data')
        def get_chart_data():
            """الحصول على بيانات الرسم البياني"""
            return jsonify(self.chart_data)
        
        @self.app.route('/api/positions')
        def get_positions():
            """الحصول على الصفقات المفتوحة"""
            positions = []
            for pos_id, pos_info in self.trading_bot.open_positions.items():
                # الحصول على السعر الحالي
                current_price = self.trading_bot.bybit_api.get_ticker_price(
                    pos_info['symbol'], 
                    self.trading_bot.user_settings['market_type']
                )
                
                if current_price:
                    entry_price = pos_info['entry_price']
                    side = pos_info['side']
                    
                    if side == "buy":
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                    else:
                        pnl_percent = ((entry_price - current_price) / entry_price) * 100
                    
                    positions.append({
                        'id': pos_id,
                        'symbol': pos_info['symbol'],
                        'side': side,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'pnl_percent': round(pnl_percent, 2)
                    })
            
            return jsonify(positions)
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """استقبال إشارات TradingView (الرابط القديم - يستخدم الإعدادات الافتراضية)"""
            try:
                data = request.get_json()
                
                print(f"🔔 [WEB SERVER - WEBHOOK القديم] استقبال إشارة: {data}")
                
                if not data:
                    print("⚠️ [WEB SERVER - WEBHOOK القديم] لا توجد بيانات")
                    return jsonify({"status": "error", "message": "No data received"}), 400
                
                # تسجيل الإشارة
                self.add_signal_to_chart(data)
                
                # إرسال تحديث مباشر للعملاء
                self.socketio.emit('new_signal', data)
                
                # معالجة الإشارة في البوت
                def process_signal_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.trading_bot.process_signal(data))
                    loop.close()
                
                threading.Thread(target=process_signal_async, daemon=True).start()
                
                # إرسال إشعار تلجرام
                self.send_telegram_notification("📡 تم استقبال إشارة جديدة", data)
                
                print(f"✅ [WEB SERVER - WEBHOOK القديم] تمت معالجة الإشارة بنجاح")
                return jsonify({"status": "success"}), 200
                
            except Exception as e:
                print(f"❌ [WEB SERVER - WEBHOOK القديم] خطأ: {e}")
                return jsonify({"status": "error", "message": str(e)}), 400
        
        @self.app.route('/personal/<int:user_id>/webhook', methods=['POST'])
        def personal_webhook(user_id):
            """استقبال إشارات TradingView الشخصية لكل مستخدم"""
            try:
                data = request.get_json()
                
                print(f"🔔 [WEB SERVER - WEBHOOK شخصي] المستخدم: {user_id}")
                print(f"📊 [WEB SERVER - WEBHOOK شخصي] البيانات المستلمة: {data}")
                
                if not data:
                    print(f"⚠️ [WEB SERVER - WEBHOOK شخصي] لا توجد بيانات للمستخدم {user_id}")
                    return jsonify({"status": "error", "message": "No data received"}), 400
                
                # التحقق من وجود user_manager
                from user_manager import user_manager
                from database import db_manager
                
                if not user_manager:
                    print(f"❌ [WEB SERVER - WEBHOOK شخصي] user_manager غير متاح للمستخدم {user_id}")
                    return jsonify({"status": "error", "message": "User manager not initialized"}), 500
                
                # التحقق من وجود المستخدم في الذاكرة
                user_data = user_manager.get_user(user_id)
                
                # إذا لم يكن موجودًا في الذاكرة، تحقق من قاعدة البيانات مباشرة
                if not user_data:
                    print(f"⚠️ [WEB SERVER - WEBHOOK شخصي] المستخدم {user_id} غير موجود في الذاكرة، جاري التحقق من قاعدة البيانات...")
                    user_data = db_manager.get_user(user_id)
                    
                    if not user_data:
                        print(f"❌ [WEB SERVER - WEBHOOK شخصي] المستخدم {user_id} غير موجود في قاعدة البيانات")
                        return jsonify({"status": "error", "message": f"User {user_id} not found. Please start the bot first with /start"}), 404
                    
                    # إعادة تحميل المستخدم في الذاكرة
                    print(f"✅ [WEB SERVER - WEBHOOK شخصي] تم العثور على المستخدم {user_id} في قاعدة البيانات، جاري التحميل...")
                    user_manager.reload_user_data(user_id)
                    # إنشاء الحسابات للمستخدم
                    user_manager._create_user_accounts(user_id, user_data)
                    print(f"✅ [WEB SERVER - WEBHOOK شخصي] تم تحميل المستخدم {user_id} بنجاح")
                
                # التحقق من تفعيل المستخدم
                if not user_data.get('is_active', False):
                    print(f"⚠️ [WEB SERVER - WEBHOOK شخصي] المستخدم {user_id} غير نشط")
                    return jsonify({"status": "error", "message": f"User {user_id} is not active"}), 403
                
                print(f"✅ [WEB SERVER - WEBHOOK شخصي] المستخدم {user_id} موجود ونشط")
                print(f"📋 [WEB SERVER - WEBHOOK شخصي] إعدادات المستخدم: market_type={user_data.get('market_type')}, account_type={user_data.get('account_type')}")
                
                # تسجيل الإشارة في الرسم البياني
                self.add_signal_to_chart(data)
                
                # إرسال تحديث مباشر للعملاء
                self.socketio.emit('new_signal', {
                    'user_id': user_id,
                    'data': data
                })
                
                # معالجة الإشارة للمستخدم المحدد
                def process_user_signal_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._process_user_signal(user_id, data, user_data))
                    loop.close()
                
                threading.Thread(target=process_user_signal_async, daemon=True).start()
                
                print(f"✅ [WEB SERVER - WEBHOOK شخصي] تمت معالجة إشارة المستخدم {user_id} بنجاح")
                return jsonify({
                    "status": "success", 
                    "message": f"Signal processed for user {user_id}",
                    "user_id": user_id
                }), 200
                
            except Exception as e:
                print(f"❌ [WEB SERVER - WEBHOOK شخصي] خطأ للمستخدم {user_id}: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"status": "error", "message": str(e)}), 500
    
    async def _process_user_signal(self, user_id: int, signal_data: dict, user_data: dict):
        """معالجة الإشارة باستخدام إعدادات المستخدم الخاصة"""
        try:
            from user_manager import user_manager
            
            print(f"🔄 [WEB SERVER - معالجة الإشارة] بدء معالجة إشارة المستخدم {user_id}")
            
            # استخراج بيانات الإشارة
            symbol = signal_data.get('symbol', '').upper()
            action = signal_data.get('action', '').lower()  # buy, sell, stop, close
            price = signal_data.get('price', 0.0)
            
            print(f"📈 [WEB SERVER - معالجة الإشارة] الرمز: {symbol}, الإجراء: {action}, السعر: {price}")
            
            if not symbol or not action:
                print(f"❌ [WEB SERVER - معالجة الإشارة] بيانات غير مكتملة للمستخدم {user_id}")
                return
            
            # الحصول على إعدادات المستخدم
            market_type = user_data.get('market_type', 'spot')
            account_type = user_data.get('account_type', 'demo')
            trade_amount = user_data.get('trade_amount', 100.0)
            leverage = user_data.get('leverage', 10)
            
            print(f"⚙️ [WEB SERVER - معالجة الإشارة] الإعدادات: market={market_type}, account={account_type}, amount={trade_amount}, leverage={leverage}")
            
            # معالجة أنواع الإشارات المختلفة
            if action in ['buy', 'sell', 'long', 'short']:
                # فتح صفقة جديدة
                print(f"📝 [WEB SERVER - معالجة الإشارة] فتح صفقة {action} للمستخدم {user_id}")
                
                # تحويل long/short إلى buy/sell
                if action == 'long':
                    action = 'buy'
                elif action == 'short':
                    action = 'sell'
                
                success, result = user_manager.execute_user_trade(
                    user_id=user_id,
                    symbol=symbol,
                    action=action,
                    price=price if price > 0 else None,
                    amount=trade_amount,
                    market_type=market_type
                )
                
                if success:
                    print(f"✅ [WEB SERVER - معالجة الإشارة] نجح فتح الصفقة للمستخدم {user_id}: {result}")
                    
                    # تحديث الرسوم البيانية
                    self.add_trade_to_chart({
                        'symbol': symbol,
                        'side': action,
                        'price': price,
                        'amount': trade_amount,
                        'pnl': 0
                    })
                    
                    # إرسال إشعار للمستخدم
                    message_data = {
                        "رسالة": "تم فتح صفقة جديدة ✅",
                        "الرمز": symbol,
                        "النوع": action.upper(),
                        "المبلغ": trade_amount,
                        "السعر": price if price > 0 else 'السعر الحالي',
                        "السوق": market_type
                    }
                    self.send_telegram_notification(f"📊 صفقة جديدة للمستخدم {user_id}", message_data)
                else:
                    print(f"❌ [WEB SERVER - معالجة الإشارة] فشل فتح الصفقة للمستخدم {user_id}: {result}")
                    
            elif action in ['close', 'exit', 'stop']:
                # إغلاق الصفقات المفتوحة
                print(f"📝 [WEB SERVER - معالجة الإشارة] إغلاق صفقات للمستخدم {user_id}")
                
                user_positions = user_manager.get_user_positions(user_id)
                if not user_positions:
                    print(f"⚠️ [WEB SERVER - معالجة الإشارة] لا توجد صفقات مفتوحة للمستخدم {user_id}")
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
                            print(f"✅ [WEB SERVER - معالجة الإشارة] تم إغلاق الصفقة {position_id} للمستخدم {user_id}")
                            
                            # تحديث الرسوم البيانية
                            self.add_trade_to_chart({
                                'symbol': symbol,
                                'side': 'close',
                                'price': close_price,
                                'amount': position_data.get('quantity', 0),
                                'pnl': result.get('pnl', 0)
                            })
                
                print(f"✅ [WEB SERVER - معالجة الإشارة] تم إغلاق {closed_count} صفقة للمستخدم {user_id}")
                
                # إرسال إشعار
                message_data = {
                    "رسالة": "تم إغلاق الصفقات ✅",
                    "الرمز": symbol,
                    "عدد الصفقات المغلقة": closed_count
                }
                self.send_telegram_notification(f"🔒 إغلاق صفقات المستخدم {user_id}", message_data)
            else:
                print(f"⚠️ [WEB SERVER - معالجة الإشارة] إجراء غير معروف '{action}' للمستخدم {user_id}")
            
        except Exception as e:
            print(f"❌ [WEB SERVER - معالجة الإشارة] خطأ في معالجة إشارة المستخدم {user_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_socketio_events(self):
        """إعداد أحداث WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """عند اتصال عميل جديد"""
            print(f"عميل جديد متصل: {request.environ.get('REMOTE_ADDR')}")
            # إرسال البيانات الحالية للعميل الجديد
            emit('chart_update', self.chart_data)
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """عند قطع الاتصال"""
            print(f"تم قطع الاتصال: {request.environ.get('REMOTE_ADDR')}")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """طلب تحديث البيانات"""
            emit('chart_update', self.chart_data)
    
    def add_signal_to_chart(self, signal_data):
        """إضافة إشارة جديدة للرسم البياني"""
        timestamp = datetime.now().isoformat()
        
        self.chart_data['signals'].append({
            'timestamp': timestamp,
            'symbol': signal_data.get('symbol', ''),
            'action': signal_data.get('action', ''),
            'price': signal_data.get('price', 0)
        })
        
        # الاحتفاظ بآخر 100 إشارة فقط
        if len(self.chart_data['signals']) > 100:
            self.chart_data['signals'] = self.chart_data['signals'][-100:]
    
    def update_balance_chart(self):
        """تحديث رسم البياني للرصيد"""
        account = self.trading_bot.get_current_account()
        account_info = account.get_account_info()
        
        timestamp = datetime.now().isoformat()
        self.chart_data['balance_history'].append({
            'timestamp': timestamp,
            'balance': account_info['balance'],
            'unrealized_pnl': account_info['unrealized_pnl']
        })
        
        # الاحتفاظ بآخر 200 نقطة
        if len(self.chart_data['balance_history']) > 200:
            self.chart_data['balance_history'] = self.chart_data['balance_history'][-200:]
        
        # إرسال التحديث للعملاء
        self.socketio.emit('balance_update', {
            'timestamp': timestamp,
            'balance': account_info['balance'],
            'unrealized_pnl': account_info['unrealized_pnl']
        })
    
    def add_trade_to_chart(self, trade_data):
        """إضافة صفقة جديدة للرسم البياني"""
        timestamp = datetime.now().isoformat()
        
        self.chart_data['trades'].append({
            'timestamp': timestamp,
            'symbol': trade_data.get('symbol', ''),
            'side': trade_data.get('side', ''),
            'price': trade_data.get('price', 0),
            'amount': trade_data.get('amount', 0),
            'pnl': trade_data.get('pnl', 0)
        })
        
        # الاحتفاظ بآخر 50 صفقة
        if len(self.chart_data['trades']) > 50:
            self.chart_data['trades'] = self.chart_data['trades'][-50:]
        
        # إرسال التحديث للعملاء
        self.socketio.emit('trade_update', trade_data)
    
    def setup_webhook_url(self):
        """إعداد رابط Webhook (على Railway سيتم استخدام الرابط المقدم)"""
        try:
            # Check for Railway URL first, then Render, then fallback to localhost
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            render_url = os.getenv('RENDER_EXTERNAL_URL')
            
            if railway_url:
                # Ensure the URL has the correct protocol
                if not railway_url.startswith('http'):
                    railway_url = f"https://{railway_url}"
                self.current_url = f"{railway_url}/webhook"
            elif render_url:
                self.current_url = f"{render_url}/webhook"
            else:
                # استخدام المنفذ المحدد من Railway أو القيمة الافتراضية
                port = PORT
                self.current_url = f"http://localhost:{port}/webhook"
            
            print(f"🌐 تم إعداد رابط Webhook: {self.current_url}")
            
            # إرسال إشعار بدء التشغيل
            self.send_startup_notification(self.current_url)
            
            return self.current_url
            
        except Exception as e:
            print(f"❌ خطأ في إعداد رابط Webhook: {e}")
            port = PORT
            local_url = f"http://localhost:{port}/webhook"
            self.send_startup_notification(local_url)
            return local_url

    def send_startup_notification(self, current_url):
        """إرسال إشعار بدء التشغيل"""
        try:
            # التحقق مما إذا كان عنوان Railway متوفرًا
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            if railway_url:
                # Ensure the URL has the correct protocol
                if not railway_url.startswith('http'):
                    railway_url = f"https://{railway_url}"
                # استخدام عنوان Railway للإشعارات
                display_url = f"{railway_url}/webhook"
            else:
                # استخدام العنوان المحلي
                display_url = current_url
                
            notification_data = {
                "رابط استقبال الإشارات": display_url,
                "الوقت": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "الحالة": "السيرفر قيد التشغيل ✅"
            }
            
            self.send_telegram_notification(
                "🚀 بدء تشغيل السيرفر",
                notification_data
            )
            
        except Exception as e:
            print(f"❌ خطأ في إرسال إشعار بدء التشغيل: {e}")
    
    def send_detailed_startup_notification(self, current_url, old_url=None):
        """إرسال إشعار بدء التشغيل المفصل مع تفاصيل URL"""
        try:
            # If old_url is not provided, use the one from config
            if old_url is None:
                old_url = WEBHOOK_URL
                
            # Always send detailed notification when ngrok is involved
            if "ngrok-free.app" in current_url:
                # إرسال إشعار تلجرام مفصل
                notification_data = {
                    "الرابط القديم": old_url,
                    "الرابط الجديد": current_url,
                    "الوقت": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "الحالة": "تم التحديث بنجاح ✅"
                }
                
                self.send_telegram_notification(
                    "🔄 تم تحديث رابط السيرفر تلقائياً",
                    notification_data
                )
            elif "localhost" in current_url:
                # Send notification for localhost with old URL info
                notification_data = {
                    "الرابط القديم": old_url,
                    "الرابط الحالي": current_url,
                    "الوقت": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "الحالة": "فشل في إنشاء نفق ngrok ❌"
                }
                
                self.send_telegram_notification(
                    "❌ فشل في إنشاء نفق ngrok",
                    notification_data
                )
            else:
                # Send notification for all other URLs
                notification_data = {
                    "الرابط الحالي": current_url,
                    "الوقت": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "الحالة": "السيرفر قيد التشغيل ✅"
                }
                
                self.send_telegram_notification(
                    "🚀 بدء تشغيل السيرفر",
                    notification_data
                )
            
        except Exception as e:
            print(f"❌ خطأ في إرسال إشعار بدء التشغيل المفصل: {e}")

    def send_telegram_notification(self, title, data):
        """إرسال إشعار تلجرام"""
        try:
            message = f"{title}\n\n"
            
            if isinstance(data, dict):
                for key, value in data.items():
                    message += f"🔹 {key}: {value}\n"
            else:
                message += str(data)
            
            # إرسال الرسالة (سيتم تنفيذها من خلال البوت)
            import asyncio
            from telegram.ext import Application
            
            async def send_message():
                try:
                    application = Application.builder().token(TELEGRAM_TOKEN).build()
                    await application.bot.send_message(chat_id=ADMIN_USER_ID, text=message)
                except Exception as e:
                    print(f"خطأ في إرسال الرسالة: {e}")
            
            # تشغيل في thread منفصل
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_message())
                loop.close()
            
            threading.Thread(target=run_async, daemon=True).start()
            
        except Exception as e:
            print(f"❌ خطأ في إرسال إشعار تلجرام: {e}")
    
    def start_background_tasks(self):
        """بدء المهام الخلفية"""
        def update_charts_periodically():
            """تحديث الرسوم البيانية دورياً"""
            while True:
                try:
                    # تحديث رسم الرصيد كل 30 ثانية
                    self.update_balance_chart()
                    time.sleep(30)
                except Exception as e:
                    print(f"خطأ في تحديث الرسوم البيانية: {e}")
                    time.sleep(30)
        
        # تشغيل المهمة في thread منفصل
        threading.Thread(target=update_charts_periodically, daemon=True).start()
    
    def run(self, host='0.0.0.0', port=None, debug=False):
        """ تشغيل السيرفر"""
        if port is None:
            port = PORT
        
        # إعداد رابط Webhook
        webhook_url = self.setup_webhook_url()
        
        # بدء المهام الخلفية
        self.start_background_tasks()
        
        print(f"🚀 تشغيل السيرفر على http://{host}:{port}")
        if webhook_url:
            print(f"🌐 رابط Webhook: {webhook_url}")
        
        # تشغيل السيرفر
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)