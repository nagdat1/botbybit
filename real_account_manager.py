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
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب إلى Bybit API - محسّن مع توقيع صحيح"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        try:
            # بناء التوقيع بطريقة مختلفة حسب نوع الطلب
            if method == 'GET':
                # للطلبات GET: استخدام query string
                params_str = urlencode(sorted(params.items())) if params else ""
                signature = self._generate_signature(timestamp, recv_window, params_str)
                
                headers = {
                    'X-BAPI-API-KEY': self.api_key,
                    'X-BAPI-SIGN': signature,
                    'X-BAPI-TIMESTAMP': timestamp,
                    'X-BAPI-RECV-WINDOW': recv_window,
                    'X-BAPI-SIGN-TYPE': '2',
                    'Content-Type': 'application/json'
                }
                
                url = f"{self.base_url}{endpoint}"
                if params_str:
                    url += f"?{params_str}"
                
                response = requests.get(url, headers=headers, timeout=10)
                
            elif method == 'POST':
                # للطلبات POST: استخدام JSON body
                import json
                # ترتيب المعاملات أبجدياً لضمان توافق التوقيع
                params_sorted = {}
                if params:
                    params_sorted = {k: params[k] for k in sorted(params.keys())}
                    # استخدام json.dumps بدون مسافات
                    params_str = json.dumps(params_sorted, separators=(',', ':'), sort_keys=True)
                else:
                    params_str = ""
                signature = self._generate_signature(timestamp, recv_window, params_str)
                
                headers = {
                    'X-BAPI-API-KEY': self.api_key,
                    'X-BAPI-SIGN': signature,
                    'X-BAPI-TIMESTAMP': timestamp,
                    'X-BAPI-RECV-WINDOW': recv_window,
                    'X-BAPI-SIGN-TYPE': '2',
                    'Content-Type': 'application/json'
                }
                
                url = f"{self.base_url}{endpoint}"
                logger.info(f"📤 POST إلى {endpoint}")
                logger.info(f"📋 المعاملات المرتبة: {params_str}")
                logger.debug(f"المعاملات الأصلية: {params}")
                
                # إرسال المعاملات كنص JSON لضمان التطابق التام مع التوقيع
                if params_str:
                    response = requests.post(url, headers=headers, data=params_str, timeout=10)
                else:
                    response = requests.post(url, headers=headers, timeout=10)
            else:
                logger.error(f"❌ نوع طلب غير مدعوم: {method}")
                return None
            
            # معالجة الاستجابة
            if response.status_code == 200:
                result = response.json()
                if result.get('retCode') == 0:
                    logger.info(f"✅ نجح الطلب: {endpoint}")
                    return result.get('result')
                else:
                    logger.error(f"❌ خطأ من Bybit API: {result.get('retMsg')}")
                    logger.error(f"   retCode: {result.get('retCode')}")
                    return None
            else:
                logger.error(f"❌ Bybit API Error (HTTP {response.status_code}): {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في طلب Bybit: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
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
        if market_type == 'spot':
            account_type = 'SPOT'
        elif market_type == 'futures':
            account_type = 'CONTRACT'
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
                   take_profit: float = None, stop_loss: float = None,
                   reduce_only: bool = False) -> Optional[Dict]:
        """وضع أمر تداول حقيقي"""
        
        # إرسال الكمية كما هي بدون تقريب - المنصة ستقوم بالتقريب
        # فقط نضمن أن الكمية رقم صحيح
        qty_str = str(float(qty))
        
        params = {
            'category': category,
            'symbol': symbol,
            'side': side.capitalize(),
            'orderType': order_type.capitalize(),
            'qty': qty_str
        }
        
        if price and order_type.lower() == 'limit':
            params['price'] = str(price)
        
        # reduce_only للأوامر Futures فقط
        if reduce_only and category in ['linear', 'inverse']:
            params['reduceOnly'] = True
        
        if take_profit:
            params['takeProfit'] = str(take_profit)
        
        if stop_loss:
            params['stopLoss'] = str(stop_loss)
        
        # تعيين الرافعة المالية أولاً إذا كانت محددة
        if leverage and category in ['linear', 'inverse']:
            self.set_leverage(category, symbol, leverage)
        
        result = self._make_request('POST', '/v5/order/create', params)
        
        if result:
            logger.info(f"🔍 نتيجة place_order من Bybit: {result}")
            order_id = result.get('orderId')
            if order_id:
                return {
                    'order_id': order_id,
                    'order_link_id': result.get('orderLinkId'),
                    'symbol': symbol,
                    'side': side,
                    'type': order_type,
                    'qty': qty,
                    'price': price
                }
            else:
                logger.error(f"❌ لا يوجد orderId في نتيجة Bybit: {result}")
                return {'error': 'No orderId in result', 'details': result}
        
        return {'error': 'Empty result from Bybit'}
    
    def set_leverage(self, category: str, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية على المنصة"""
        params = {
            'category': category,
            'symbol': symbol,
            'buyLeverage': str(leverage),
            'sellLeverage': str(leverage)
        }
        
        result = self._make_request('POST', '/v5/position/set-leverage', params)
        return result is not None
    
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
    
    def close_position(self, category: str, symbol: str, side: str = None, reduce_only: bool = False) -> Optional[Dict]:
        """إغلاق صفقة مفتوحة"""
        # للـ Spot، نحتاج فقط لإرسال أمر بيع/شراء عكسي
        if category == 'spot':
            # الحصول على معلومات الصفقة
            positions = self.get_open_positions(category)
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                return None
            
            # عكس الجهة للإغلاق
            close_side = 'Sell' if position['side'].lower() == 'buy' else 'Buy'
            
            return self.place_order(
                category=category,
                symbol=symbol,
                side=close_side,
                order_type='Market',
                qty=position['size'],
                reduce_only=False  # Spot لا يدعم reduce_only
            )
        else:
            # للـ Futures/Linear
            positions = self.get_open_positions(category)
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                return None
            
            # عكس الجهة للإغلاق
            close_side = side if side else ('Sell' if position['side'].lower() == 'buy' else 'Buy')
            
            return self.place_order(
                category=category,
                symbol=symbol,
                side=close_side,
                order_type='Market',
                qty=position['size'],
                reduce_only=True
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
            logger.info(f"🔄 MEXCRealAccount - وضع أمر: {side} {quantity} {symbol}")
            
            result = self.bot.place_spot_order(symbol, side, quantity, order_type, price)
            
            if result:
                logger.info(f"✅ MEXCRealAccount - تم وضع الأمر بنجاح: {result}")
            else:
                logger.error(f"❌ MEXCRealAccount - فشل وضع الأمر: {symbol} {side} {quantity}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MEXCRealAccount - خطأ في وضع الأمر: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_trade_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        """الحصول على سجل التداولات"""
        return self.bot.get_trade_history(symbol, limit)
    
    def get_ticker(self, category: str, symbol: str) -> Optional[Dict]:
        """الحصول على معلومات السعر - محسن لـ MEXC"""
        try:
            logger.info(f"🔍 MEXCRealAccount - جلب السعر لـ {symbol}")
            price = self.bot.get_ticker_price(symbol)
            if price:
                logger.info(f"✅ MEXCRealAccount - السعر: {price}")
                return {'lastPrice': str(price)}
            else:
                logger.error(f"❌ MEXCRealAccount - فشل جلب السعر لـ {symbol}")
                return None
        except Exception as e:
            logger.error(f"❌ MEXCRealAccount - خطأ في جلب السعر: {e}")
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

