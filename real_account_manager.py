#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الحسابات الحقيقية - تكامل كامل مع المنصات
يدير الاتصال الحقيقي مع Bybit و MEXC
"""

import logging
import hmac
import hashlib
import time
import requests
from typing import Dict, Optional, List, Any
from urllib.parse import urlencode
from datetime import datetime

logger = logging.getLogger(__name__)

class BybitRealAccount:
    """إدارة الحساب الحقيقي على Bybit"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bybit.com"
        
    def _generate_signature(self, timestamp: str, recv_window: str, params_str: str) -> str:
        """توليد التوقيع لـ Bybit V5"""
        sign_str = timestamp + self.api_key + recv_window + params_str
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        logger.info(f"Bybit Signature Debug - sign_str: {sign_str}")
        logger.info(f"Bybit Signature Debug - signature: {signature}")
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب إلى Bybit API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # بناء query string للطلبات GET
        if method == 'GET':
            params_str = urlencode(sorted(params.items())) if params else ""
        else:
            # للطلبات POST، استخدام JSON string للتوقيع (مع مسافات)
            import json
            params_str = json.dumps(params, separators=(', ', ': ')) if params else ""
        
        logger.info(f"Bybit Params Debug - params: {params}")
        logger.info(f"Bybit Params Debug - params_str: {params_str}")
        
        # توليد التوقيع
        signature = self._generate_signature(timestamp, recv_window, params_str)
        
        # Headers
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        # إضافة query string فقط للطلبات GET
        if method == 'GET' and params_str:
            url += f"?{urlencode(sorted(params.items()))}"
        
        logger.info(f"Bybit URL Debug - url: {url}")
        
        try:
            logger.info(f"Bybit API Request: {method} {url}")
            logger.info(f"Bybit API Params: {params}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                # للطلبات الموقعة، إرسال المعاملات في JSON body
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                return None
            
            logger.info(f"Bybit API Response Status: {response.status_code}")
            logger.info(f"Bybit API Response Text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Bybit API Response JSON: {result}")
                
                if result.get('retCode') == 0:
                    logger.info(f"Bybit API Success: {result.get('result')}")
                    return result.get('result')
                else:
                    error_msg = result.get('retMsg', 'Unknown error')
                    ret_code = result.get('retCode', -1)
                    logger.error(f"Bybit API Error - retCode: {ret_code}, retMsg: {error_msg}")
                    
                    # إرجاع معلومات الخطأ بدلاً من None
                    return {
                        'error': True,
                        'retCode': ret_code,
                        'retMsg': error_msg,
                        'raw_response': result
                    }
            
            logger.error(f"Bybit API HTTP Error: {response.status_code} - {response.text}")
            
            # إرجاع معلومات الخطأ HTTP
            return {
                'error': True,
                'http_status': response.status_code,
                'http_message': response.text,
                'raw_response': response.text
            }
            
        except Exception as e:
            logger.error(f"خطأ في طلب Bybit: {e}")
            
            # إرجاع معلومات الخطأ الاستثناء
            return {
                'error': True,
                'exception': str(e),
                'error_type': 'REQUEST_EXCEPTION'
            }
    
    def get_wallet_balance(self, market_type: str = 'unified') -> Optional[Dict]:
        """
        الحصول على رصيد المحفظة الحقيقي
        market_type: 'unified' للحساب الموحد، 'spot' للسبوت، 'contract' للفيوتشر
        """
        # دالة مساعدة لتحويل القيم بأمان
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # تحديد نوع الحساب حسب نوع السوق
        # ملاحظة: Bybit V5 يدعم فقط UNIFIED للحسابات الموحدة
        if market_type == 'spot':
            account_type = 'UNIFIED'  # استخدام UNIFIED للسبوت أيضاً
        elif market_type == 'futures':
            account_type = 'UNIFIED'  # استخدام UNIFIED للفيوتشر أيضاً
        else:
            account_type = 'UNIFIED'
        
        result = self._make_request('GET', '/v5/account/wallet-balance', {
            'accountType': account_type
        })
        
        if result and 'list' in result:
            account = result['list'][0] if result['list'] else {}
            coins = account.get('coin', [])
            
            balance_data = {
                'total_equity': safe_float(account.get('totalEquity', 0)),
                'available_balance': safe_float(account.get('totalAvailableBalance', 0)),
                'total_wallet_balance': safe_float(account.get('totalWalletBalance', 0)),
                'unrealized_pnl': safe_float(account.get('totalPerpUPL', 0)),
                'account_type': account_type,
                'market_type': market_type,
                'coins': {}
            }
            
            for coin in coins:
                coin_name = coin.get('coin')
                equity = safe_float(coin.get('equity', 0))
                if equity > 0:
                    balance_data['coins'][coin_name] = {
                        'equity': equity,
                        'available': safe_float(coin.get('availableToWithdraw', 0)),
                        'wallet_balance': safe_float(coin.get('walletBalance', 0)),
                        'unrealized_pnl': safe_float(coin.get('unrealisedPnl', 0))
                    }
            
            return balance_data
        
        return None
    
    def get_open_positions(self, category: str = 'linear') -> List[Dict]:
        """الحصول على الصفقات المفتوحة الحقيقية"""
        result = self._make_request('GET', '/v5/position/list', {
            'category': category,
            'settleCoin': 'USDT'
        })
        
        # دالة مساعدة لتحويل القيم بأمان
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        positions = []
        if result and 'list' in result:
            for pos in result['list']:
                size = safe_float(pos.get('size', 0))
                if size > 0:
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'side': pos.get('side'),
                        'size': size,
                        'entry_price': safe_float(pos.get('avgPrice', 0)),
                        'mark_price': safe_float(pos.get('markPrice', 0)),
                        'unrealized_pnl': safe_float(pos.get('unrealisedPnl', 0)),
                        'leverage': pos.get('leverage', '1'),
                        'liquidation_price': safe_float(pos.get('liqPrice', 0)),
                        'take_profit': safe_float(pos.get('takeProfit', 0)),
                        'stop_loss': safe_float(pos.get('stopLoss', 0)),
                        'created_time': pos.get('createdTime')
                    })
        
        return positions
    
    def place_order(self, category: str, symbol: str, side: str, order_type: str,
                   qty: float, price: float = None, leverage: int = None,
                   take_profit: float = None, stop_loss: float = None) -> Optional[Dict]:
        """وضع أمر تداول حقيقي"""
        
        logger.info(f"Bybit place_order called: {category}, {symbol}, {side}, {order_type}, qty={qty}")
        
        params = {
            'category': category,
            'symbol': symbol,
            'side': side.capitalize(),
            'orderType': order_type.capitalize(),
            'qty': str(qty)
        }
        
        if price and order_type.lower() == 'limit':
            params['price'] = str(price)
        
        if take_profit:
            params['takeProfit'] = str(take_profit)
        
        if stop_loss:
            params['stopLoss'] = str(stop_loss)
        
        # تعيين الرافعة المالية أولاً إذا كانت محددة
        if leverage and category in ['linear', 'inverse']:
            logger.info(f"Setting leverage to {leverage} for {symbol}")
            leverage_result = self.set_leverage(category, symbol, leverage)
            if not leverage_result:
                logger.error(f"Failed to set leverage for {symbol}")
        
        result = self._make_request('POST', '/v5/order/create', params)
        
        # معالجة محسنة للنتيجة
        if result is None:
            logger.error(f"Bybit order placement failed for {symbol} - No response")
            return {
                'success': False,
                'error': 'Order placement failed - No response from API',
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'error_type': 'NO_RESPONSE'
            }
        
        # فحص إذا كانت النتيجة تحتوي على خطأ
        if isinstance(result, dict) and result.get('error'):
            logger.error(f"Bybit order placement failed for {symbol} - API Error")
            
            # استخراج تفاصيل الخطأ
            error_details = {
                'success': False,
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'error_type': 'API_ERROR'
            }
            
            # إضافة تفاصيل الخطأ حسب النوع
            if 'retCode' in result:
                error_details['retCode'] = result['retCode']
                error_details['retMsg'] = result['retMsg']
                error_details['error'] = f"Bybit API Error {result['retCode']}: {result['retMsg']}"
            elif 'http_status' in result:
                error_details['http_status'] = result['http_status']
                error_details['http_message'] = result['http_message']
                error_details['error'] = f"HTTP Error {result['http_status']}: {result['http_message']}"
            elif 'exception' in result:
                error_details['exception'] = result['exception']
                error_details['error'] = f"Request Exception: {result['exception']}"
            else:
                error_details['error'] = 'Unknown API error'
            
            error_details['raw_response'] = result
            return error_details
        
        # النجاح
        if result and not result.get('error'):
            logger.info(f"Bybit order placed successfully: {result}")
            return {
                'order_id': result.get('orderId'),
                'order_link_id': result.get('orderLinkId'),
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'qty': qty,
                'price': price,
                'success': True,
                'raw_response': result
            }
        
        # حالة غير متوقعة
        logger.error(f"Bybit order placement failed for {symbol} - Unexpected response")
        return {
            'success': False,
            'error': 'Order placement failed - Unexpected response format',
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'error_type': 'UNEXPECTED_RESPONSE',
            'raw_response': result
        }
    
    def set_leverage(self, category: str, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية على المنصة"""
        params = {
            'category': category,
            'symbol': symbol,
            'buyLeverage': str(leverage),
            'sellLeverage': str(leverage)
        }
        
        logger.info(f"Setting leverage for {symbol}: {leverage}x")
        result = self._make_request('POST', '/v5/position/set-leverage', params)
        
        if result is not None:
            logger.info(f"Leverage set successfully for {symbol}: {leverage}x")
            return True
        else:
            logger.error(f"Failed to set leverage for {symbol}: {leverage}x")
            return False
    
    def set_trading_stop(self, category: str, symbol: str, position_idx: int,
                        take_profit: float = None, stop_loss: float = None) -> bool:
        """تعيين TP/SL للصفقة المفتوحة"""
        params = {
            'category': category,
            'symbol': symbol,
            'positionIdx': position_idx
        }
        
        if take_profit:
            params['takeProfit'] = str(take_profit)
        
        if stop_loss:
            params['stopLoss'] = str(stop_loss)
        
        result = self._make_request('POST', '/v5/position/trading-stop', params)
        return result is not None
    
    def close_position(self, category: str, symbol: str, side: str) -> Optional[Dict]:
        """إغلاق صفقة مفتوحة"""
        # الحصول على حجم الصفقة أولاً
        positions = self.get_open_positions(category)
        position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if not position:
            return None
        
        # عكس الجهة للإغلاق
        close_side = 'Sell' if side.lower() == 'buy' else 'Buy'
        
        return self.place_order(
            category=category,
            symbol=symbol,
            side=close_side,
            order_type='Market',
            qty=position['size']
        )
    
    def get_order_history(self, category: str = 'linear', limit: int = 50) -> List[Dict]:
        """الحصول على سجل الأوامر"""
        result = self._make_request('GET', '/v5/order/history', {
            'category': category,
            'limit': limit
        })
        
        # دالة مساعدة لتحويل القيم بأمان
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        orders = []
        if result and 'list' in result:
            for order in result['list']:
                orders.append({
                    'order_id': order.get('orderId'),
                    'symbol': order.get('symbol'),
                    'side': order.get('side'),
                    'type': order.get('orderType'),
                    'qty': safe_float(order.get('qty', 0)),
                    'price': safe_float(order.get('price', 0)),
                    'avg_price': safe_float(order.get('avgPrice', 0)),
                    'status': order.get('orderStatus'),
                    'created_time': order.get('createdTime'),
                    'updated_time': order.get('updatedTime')
                })
        
        return orders
    
    def get_ticker(self, category: str, symbol: str) -> Optional[Dict]:
        """الحصول على معلومات السعر"""
        try:
            # استخدام دالة get_ticker_price الموجودة
            price = self.get_ticker_price(symbol, category)
            if price:
                return {'lastPrice': str(price)}
            return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر: {e}")
            return None
    
    def get_ticker_price(self, symbol: str, category: str = "spot") -> Optional[float]:
        """الحصول على سعر الرمز الحالي"""
        try:
            endpoint = "/v5/market/tickers"
            # تحويل futures إلى linear للتوافق مع Bybit API
            api_category = "linear" if category == "futures" else category
            params = {"category": api_category, "symbol": symbol}
            
            result = self._make_request('GET', endpoint, params)
            
            if result and 'list' in result and result['list']:
                return float(result['list'][0].get('lastPrice', 0))
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر: {e}")
            return None


class MEXCRealAccount:
    """إدارة الحساب الحقيقي على MEXC"""
    
    def __init__(self, api_key: str, api_secret: str):
        from mexc_trading_bot import create_mexc_bot
        self.bot = create_mexc_bot(api_key, api_secret)
    
    def get_wallet_balance(self) -> Optional[Dict]:
        """الحصول على رصيد المحفظة الحقيقي"""
        balance = self.bot.get_account_balance()
        
        if balance and 'balances' in balance:
            total_usdt = 0
            coins_data = {}
            
            for asset, info in balance['balances'].items():
                if info['total'] > 0:
                    coins_data[asset] = info
                    # تقدير تقريبي بـ USDT (يمكن تحسينه)
                    if asset == 'USDT':
                        total_usdt += info['total']
            
            return {
                'total_equity': total_usdt,
                'available_balance': balance.get('balances', {}).get('USDT', {}).get('free', 0),
                'coins': coins_data
            }
        
        return None
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """الحصول على الأوامر المفتوحة"""
        orders = self.bot.get_open_orders(symbol)
        return orders if orders else []
    
    def place_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = 'MARKET', price: float = None) -> Optional[Dict]:
        """وضع أمر تداول حقيقي - محسن للمعالجة الصحيحة"""
        try:
            logger.info(f" MEXCRealAccount - وضع أمر: {side} {quantity} {symbol}")
            
            result = self.bot.place_spot_order(symbol, side, quantity, order_type, price)
            
            if result:
                logger.info(f" MEXCRealAccount - تم وضع الأمر بنجاح: {result}")
            else:
                logger.error(f" MEXCRealAccount - فشل وضع الأمر: {symbol} {side} {quantity}")
            
            return result
            
        except Exception as e:
            logger.error(f" MEXCRealAccount - خطأ في وضع الأمر: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_trade_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        """الحصول على سجل التداولات"""
        return self.bot.get_trade_history(symbol, limit)
    
    def get_ticker(self, category: str, symbol: str) -> Optional[Dict]:
        """الحصول على معلومات السعر - محسن لـ MEXC"""
        try:
            logger.info(f" MEXCRealAccount - جلب السعر لـ {symbol}")
            price = self.bot.get_ticker_price(symbol)
            if price:
                logger.info(f" MEXCRealAccount - السعر: {price}")
                return {'lastPrice': str(price)}
            else:
                logger.error(f" MEXCRealAccount - فشل جلب السعر لـ {symbol}")
                return None
        except Exception as e:
            logger.error(f" MEXCRealAccount - خطأ في جلب السعر: {e}")
            return None


class RealAccountManager:
    """مدير الحسابات الحقيقية - الواجهة الموحدة"""
    
    def __init__(self):
        self.accounts = {}  # {user_id: account_object}
    
    def initialize_account(self, user_id: int, exchange: str, api_key: str, api_secret: str):
        """تهيئة حساب حقيقي للمستخدم"""
        if exchange.lower() == 'bybit':
            self.accounts[user_id] = BybitRealAccount(api_key, api_secret)
        elif exchange.lower() == 'mexc':
            self.accounts[user_id] = MEXCRealAccount(api_key, api_secret)
        
        logger.info(f"تم تهيئة حساب {exchange} حقيقي للمستخدم {user_id}")
    
    def get_account(self, user_id: int):
        """الحصول على حساب المستخدم"""
        return self.accounts.get(user_id)
    
    def remove_account(self, user_id: int):
        """إزالة حساب المستخدم"""
        if user_id in self.accounts:
            del self.accounts[user_id]
            logger.info(f"تم إزالة الحساب الحقيقي للمستخدم {user_id}")


# مثيل عام للمدير
real_account_manager = RealAccountManager()

