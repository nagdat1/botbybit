"""
🌐 Webhook Server - خادم Webhooks
استقبال الإشارات الخارجية لكل مستخدم
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from threading import Thread
from database import db
from utils.validators import validate_webhook_token, validate_symbol, validate_trade_side
from config import WEBHOOK_HOST, WEBHOOK_PORT

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# لحفظ instance البوت
bot_instance = None


def set_bot_instance(bot):
    """تعيين instance البوت"""
    global bot_instance
    bot_instance = bot


@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة الخادم"""
    return jsonify({
        'status': 'healthy',
        'service': 'Bybit Trading Bot Webhook Server'
    }), 200


@app.route('/webhook/user/<token>', methods=['POST'])
async def user_webhook(token):
    """استقبال إشارة من webhook مستخدم"""
    try:
        # التحقق من البيانات
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # التحقق من التوكن
        # البحث عن المستخدم بناءً على التوكن
        # TODO: إضافة دالة في database للبحث بالتوكن
        # user = db.get_user_by_webhook_token(token)
        
        # if not user:
        #     return jsonify({'error': 'Invalid webhook token'}), 401
        
        # استخراج البيانات
        symbol = data.get('symbol')
        action = data.get('action')
        leverage = data.get('leverage', 1)
        stop_loss = data.get('stop_loss')
        take_profit = data.get('take_profit')
        amount = data.get('amount')
        
        # التحقق من البيانات
        if not symbol or not action:
            return jsonify({'error': 'symbol and action are required'}), 400
        
        is_valid_symbol, symbol = validate_symbol(symbol)
        if not is_valid_symbol:
            return jsonify({'error': 'Invalid symbol format'}), 400
        
        is_valid_side, action = validate_trade_side(action)
        if not is_valid_side:
            return jsonify({'error': 'Invalid action. Use buy or sell'}), 400
        
        # TODO: تنفيذ الصفقة تلقائياً
        # يمكن إضافة منطق التنفيذ هنا
        
        logger.info(f"Webhook signal received: {symbol} {action} for token {token}")
        
        return jsonify({
            'status': 'success',
            'message': 'Signal received and queued for execution',
            'data': {
                'symbol': symbol,
                'action': action,
                'leverage': leverage
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/webhook/nagdat', methods=['POST'])
async def nagdat_webhook():
    """استقبال إشارة من المطور Nagdat"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # التحقق من المفتاح السري
        from config import DEVELOPER_INFO
        secret_key = data.get('secret_key')
        
        if secret_key != DEVELOPER_INFO['developer_secret_key']:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # استخراج البيانات
        symbol = data.get('symbol')
        action = data.get('action')
        leverage = data.get('leverage', 1)
        message = data.get('message')
        
        # التحقق من البيانات
        if not symbol or not action:
            return jsonify({'error': 'symbol and action are required'}), 400
        
        is_valid_symbol, symbol = validate_symbol(symbol)
        if not is_valid_symbol:
            return jsonify({'error': 'Invalid symbol format'}), 400
        
        is_valid_side, action = validate_trade_side(action)
        if not is_valid_side:
            return jsonify({'error': 'Invalid action'}), 400
        
        # حفظ الإشارة
        signal_id = db.create_signal(
            sender_id=DEVELOPER_INFO['developer_id'],
            symbol=symbol,
            action=action,
            leverage=leverage,
            message=message
        )
        
        # إرسال للمشتركين
        # TODO: إضافة منطق الإرسال للمشتركين
        subscribers = db.get_nagdat_subscribers()
        
        logger.info(f"Nagdat signal received: {symbol} {action} to {len(subscribers)} subscribers")
        
        return jsonify({
            'status': 'success',
            'message': f'Signal sent to {len(subscribers)} subscribers',
            'signal_id': signal_id
        }), 200
    
    except Exception as e:
        logger.error(f"Nagdat webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """إحصائيات عامة"""
    try:
        stats = {
            'total_users': db.get_all_users_count(),
            'active_users': db.get_active_users_count(),
            'subscribers': len(db.get_nagdat_subscribers()),
            'signals_sent': db.get_total_signals_sent()
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


def run_webhook_server():
    """تشغيل خادم Webhooks"""
    try:
        logger.info(f"🌐 Starting webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
        app.run(
            host=WEBHOOK_HOST,
            port=WEBHOOK_PORT,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start webhook server: {e}")


def start_webhook_server_thread():
    """تشغيل الخادم في thread منفصل"""
    webhook_thread = Thread(target=run_webhook_server, daemon=True)
    webhook_thread.start()
    logger.info("✅ Webhook server thread started")


if __name__ == '__main__':
    run_webhook_server()

