#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إصلاح سريع لمشكلة عدم وصول الإشارات
يضيف خادم ويب لاستقبال الإشارات من TradingView
"""

import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalReceiverFix:
    """إصلاح استقبال الإشارات"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.trading_bot = None
        self.webhook_port = 5000
        self.is_running = False
        
    def setup_routes(self):
        """إعداد مسارات استقبال الإشارات"""
        
        @self.app.route('/')
        def index():
            return jsonify({
                "status": "running",
                "message": "Signal Receiver is active",
                "timestamp": datetime.now().isoformat(),
                "webhook_endpoints": [
                    "/webhook - General webhook",
                    "/personal/<user_id>/webhook - Personal webhook"
                ]
            })
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """استقبال إشارات عامة"""
            try:
                data = request.get_json()
                logger.info(f"🔔 استقبال إشارة عامة: {data}")
                
                if not data:
                    return jsonify({"status": "error", "message": "No data received"}), 400
                
                # معالجة الإشارة في thread منفصل
                def process_signal():
                    try:
                        if self.trading_bot:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.trading_bot.process_signal(data))
                            loop.close()
                            logger.info("✅ تمت معالجة الإشارة العامة بنجاح")
                        else:
                            logger.error("❌ البوت غير متاح لمعالجة الإشارة")
                    except Exception as e:
                        logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
                
                threading.Thread(target=process_signal, daemon=True).start()
                
                return jsonify({"status": "success", "message": "Signal received and processing"}), 200
                
            except Exception as e:
                logger.error(f"❌ خطأ في webhook: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/personal/<int:user_id>/webhook', methods=['POST'])
        def personal_webhook(user_id):
            """استقبال إشارات شخصية لكل مستخدم"""
            try:
                data = request.get_json()
                logger.info(f"🔔 استقبال إشارة شخصية للمستخدم {user_id}: {data}")
                
                if not data:
                    return jsonify({"status": "error", "message": "No data received"}), 400
                
                # التحقق من وجود المستخدم
                try:
                    from user_manager import user_manager
                    user_data = user_manager.get_user(user_id)
                    
                    if not user_data:
                        logger.error(f"❌ المستخدم {user_id} غير موجود")
                        return jsonify({"status": "error", "message": f"User {user_id} not found"}), 404
                    
                    logger.info(f"✅ المستخدم {user_id} موجود ونشط")
                    
                except Exception as e:
                    logger.error(f"❌ خطأ في التحقق من المستخدم: {e}")
                    return jsonify({"status": "error", "message": "User verification failed"}), 500
                
                # معالجة الإشارة في thread منفصل
                def process_personal_signal():
                    try:
                        if self.trading_bot:
                            # حفظ الإعدادات الأصلية
                            original_user_id = self.trading_bot.user_id
                            original_settings = self.trading_bot.user_settings.copy()
                            
                            # تطبيق إعدادات المستخدم
                            self.trading_bot.user_id = user_id
                            self.trading_bot.user_settings.update({
                                'market_type': user_data.get('market_type', 'spot'),
                                'account_type': user_data.get('account_type', 'demo'),
                                'trade_amount': user_data.get('trade_amount', 100.0),
                                'leverage': user_data.get('leverage', 10)
                            })
                            
                            # معالجة الإشارة
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.trading_bot.process_signal(data))
                            loop.close()
                            
                            # استعادة الإعدادات الأصلية
                            self.trading_bot.user_id = original_user_id
                            self.trading_bot.user_settings.update(original_settings)
                            
                            logger.info(f"✅ تمت معالجة الإشارة الشخصية للمستخدم {user_id}")
                        else:
                            logger.error("❌ البوت غير متاح لمعالجة الإشارة")
                    except Exception as e:
                        logger.error(f"❌ خطأ في معالجة الإشارة الشخصية: {e}")
                
                threading.Thread(target=process_personal_signal, daemon=True).start()
                
                return jsonify({
                    "status": "success", 
                    "message": f"Personal signal received for user {user_id}",
                    "user_id": user_id
                }), 200
                
            except Exception as e:
                logger.error(f"❌ خطأ في personal webhook: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/health')
        def health_check():
            """فحص صحة الخادم"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "webhook_active": True
            })
    
    def set_trading_bot(self, trading_bot):
        """تعيين البوت لمعالجة الإشارات"""
        self.trading_bot = trading_bot
        logger.info("✅ تم تعيين البوت لمعالجة الإشارات")
    
    def start_server(self, port=5000):
        """بدء خادم استقبال الإشارات"""
        try:
            self.webhook_port = port
            self.setup_routes()
            
            def run_server():
                self.app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            self.is_running = True
            logger.info(f"✅ تم بدء خادم استقبال الإشارات على المنفذ {port}")
            
            # طباعة روابط Webhook
            print("\n" + "="*60)
            print("🔔 روابط استقبال الإشارات:")
            print(f"   عام: http://localhost:{port}/webhook")
            print(f"   شخصي: http://localhost:{port}/personal/<user_id>/webhook")
            print(f"   فحص الصحة: http://localhost:{port}/health")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في بدء خادم الإشارات: {e}")
            return False
    
    def stop_server(self):
        """إيقاف خادم استقبال الإشارات"""
        self.is_running = False
        logger.info("⏹️ تم إيقاف خادم استقبال الإشارات")
    
    def get_status(self):
        """الحصول على حالة الخادم"""
        return {
            'is_running': self.is_running,
            'port': self.webhook_port,
            'trading_bot_connected': self.trading_bot is not None,
            'endpoints': [
                '/webhook',
                '/personal/<user_id>/webhook',
                '/health'
            ]
        }

# إنشاء مثيل عام لإصلاح استقبال الإشارات
signal_receiver_fix = SignalReceiverFix()

# دالة بدء سريعة
def start_signal_receiver(trading_bot, port=5000):
    """بدء سريع لاستقبال الإشارات"""
    try:
        signal_receiver_fix.set_trading_bot(trading_bot)
        success = signal_receiver_fix.start_server(port)
        return success
    except Exception as e:
        logger.error(f"❌ خطأ في بدء استقبال الإشارات: {e}")
        return False

# دالة إيقاف سريعة
def stop_signal_receiver():
    """إيقاف سريع لاستقبال الإشارات"""
    try:
        signal_receiver_fix.stop_server()
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في إيقاف استقبال الإشارات: {e}")
        return False

# دالة الحالة
def get_signal_receiver_status():
    """الحصول على حالة استقبال الإشارات"""
    try:
        return signal_receiver_fix.get_status()
    except Exception as e:
        logger.error(f"❌ خطأ في جلب حالة استقبال الإشارات: {e}")
        return {'error': str(e)}

# دالة العرض
def show_signal_receiver_status():
    """عرض حالة استقبال الإشارات"""
    try:
        status = signal_receiver_fix.get_status()
        
        print("\n" + "="*60)
        print("🔔 حالة استقبال الإشارات")
        print("="*60)
        print(f"🚀 الخادم: {'✅ يعمل' if status['is_running'] else '❌ متوقف'}")
        print(f"🔌 المنفذ: {status['port']}")
        print(f"🤖 البوت: {'✅ متصل' if status['trading_bot_connected'] else '❌ غير متصل'}")
        print("\n📡 نقاط النهاية:")
        for endpoint in status['endpoints']:
            print(f"  • {endpoint}")
        print("="*60)
        
        if status['is_running']:
            print("✅ خادم استقبال الإشارات يعمل!")
            print("🎯 الإشارات ستصل بنجاح")
        else:
            print("⚠️ خادم استقبال الإشارات متوقف")
            print("🔄 يرجى بدء الخادم")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ خطأ في عرض حالة استقبال الإشارات: {e}")

# تشغيل الاختبار عند استيراد الملف
if __name__ == "__main__":
    print("🔔 اختبار استقبال الإشارات...")
    show_signal_receiver_status()
else:
    # تهيئة الخادم عند الاستيراد
    logger.info("🔔 تم تحميل إصلاح استقبال الإشارات")
