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
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
import pandas as pd
import requests

# استيراد إعدادات البوت
from config import *

def create_app(trading_bot=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'trading_bot_secret_key_2024'
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    if trading_bot is None:
        # إذا لم يتم تمرير trading_bot، قم بإنشاء نسخة فارغة
        class EmptyBot:
            def get_current_account(self):
                return None
        trading_bot = EmptyBot()
    
    # إعداد المسارات
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/bot_status')
    def bot_status():
        try:
            account = trading_bot.get_current_account()
            if account:
                account_info = account.get_account_info()
                return jsonify({
                    'status': 'running',
                    'account_info': account_info
                })
        except:
            pass
        
        return jsonify({
            'status': 'not_connected',
            'account_info': None
        })
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        try:
            data = request.get_json()
            # معالجة الإشارة في البوت
            def process_signal_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(trading_bot.process_signal(data))
                loop.close()
            
            threading.Thread(target=process_signal_async, daemon=True).start()
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    
    return app

# للتشغيل المباشر باستخدام flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port)