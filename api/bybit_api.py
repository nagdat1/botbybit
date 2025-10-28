#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bybit API - إدارة الحساب الحقيقي على Bybit
يدير جميع الاتصالات مع Bybit API
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
    
    def round_quantity(self, qty: float, category: str, symbol: str) -> float:
        """
        تقريب الكمية - المنطق القديم البسيط الذي كان يعمل
        """
        try:
            # تحويل إلى float إذا كان string
            if isinstance(qty, str):
                qty = float(qty)
            
            # ضمان الحد الأدنى للكمية (منطق النسخة القديمة)
            min_quantity = 0.001  # الحد الأدنى لـ Bybit
            
            if qty < min_quantity:
                logger.warning(f"الكمية صغيرة جداً: {qty}, تم تعديلها إلى الحد الأدنى: {min_quantity}")
                qty = min_quantity
            
            # تقريب الكمية حسب دقة الرمز (منطق النسخة القديمة)
            rounded_qty = round(qty, 6)
            
            # التأكد من أن الكمية ليست صفر
            if rounded_qty <= 0:
                logger.warning(f"الكمية أصبحت صفر بعد التقريب، استخدام الحد الأدنى: {min_quantity}")
                rounded_qty = min_quantity
            
            logger.info(f"تم تقريب الكمية: {qty} → {rounded_qty}")
            return rounded_qty
            
        except Exception as e:
            logger.error(f"خطأ في تقريب الكمية: {e}")
            # في حالة الخطأ، استخدم الحد الأدنى الآمن
            return 0.001
        
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
                    # 🔧 إصلاح: إرجاع معلومات الخطأ الكاملة بدلاً من None
                    ret_code = result.get('retCode')
                    ret_msg = result.get('retMsg', 'Unknown error')
                    ret_ext_info = result.get('retExtInfo', {})
                    
                    logger.error(f"❌ فشل طلب Bybit API:")
                    logger.error(f"   Endpoint: {endpoint}")
                    logger.error(f"   Error Code: {ret_code}")
                    logger.error(f"   Error Message: {ret_msg}")
                    logger.error(f"   Extra Info: {ret_ext_info}")
                    
                    # إرجاع معلومات الخطأ بدلاً من None
                    return {
                        'error': True,
                        'retCode': ret_code,
                        'retMsg': ret_msg,
                        'retExtInfo': ret_ext_info
                    }
            else:
                error_text = response.text[:500] if len(response.text) > 500 else response.text
                logger.error(f"❌ Bybit API HTTP Error:")
                logger.error(f"   Status Code: {response.status_code}")
                logger.error(f"   Endpoint: {endpoint}")
                logger.error(f"   Response: {error_text}")
                return {
                    'error': True,
                    'http_status': response.status_code,
                    'message': error_text
                }
            
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
        
        try:
            # 🔧 إصلاح: تأكد أن qty هو float
            if isinstance(qty, str):
                logger.warning(f"⚠️ qty هو string، تم تحويله إلى float")
                qty = float(qty)
            
            # 🔧 إصلاح: تقريب الكمية بناءً على قواعد الرمز
            logger.info(f"🔢 تقريب الكمية للرمز {symbol}...")
            
            # استخدام دالة التقريب من ExchangeBase
            rounded_qty = self.round_quantity(qty, category, symbol)
            
            # استخدام الكمية المقربة
            qty_str = str(rounded_qty)
            logger.info(f"✅ الكمية بعد التقريب: {qty_str}")
            
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
            
            logger.info(f"📤 وضع أمر جديد:")
            logger.info(f"   Category: {category}")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Side: {side}")
            logger.info(f"   Order Type: {order_type}")
            logger.info(f"   Quantity: {qty_str}")
            if price:
                logger.info(f"   Price: {price}")
            
            result = self._make_request('POST', '/v5/order/create', params)
            
            # 🔧 معالجة محسّنة للنتائج
            if result is None:
                logger.error(f"❌ لم يتم إرجاع نتيجة من Bybit API")
                return {
                    'error': True,
                    'message': 'Empty result from Bybit API',
                    'error_type': 'EMPTY_RESPONSE'
                }
            
            # التحقق من وجود خطأ في النتيجة
            if isinstance(result, dict) and result.get('error'):
                logger.error(f"❌ خطأ من Bybit API في place_order:")
                logger.error(f"   Details: {result}")
                return result
            
            logger.info(f"🔍 نتيجة place_order من Bybit: {result}")
            
            # استخراج orderId من النتيجة
            order_id = result.get('orderId')
            if order_id:
                logger.info(f"✅ تم إنشاء أمر بنجاح: {order_id}")
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
                # البحث في مكان آخر
                logger.warning(f"⚠️ لا يوجد orderId في المكان المتوقع، البحث في النتيجة الكاملة...")
                logger.warning(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # محاولة الحصول من النتيجة الكاملة
                if isinstance(result, dict):
                    for key in ['orderId', 'order_id', 'order-link-id', 'orderLinkId']:
                        if key in result:
                            order_id = result[key]
                            logger.info(f"✅ تم العثور على orderId في '{key}': {order_id}")
                            return {
                                'order_id': order_id,
                                'order_link_id': result.get('order_link_id', result.get('orderLinkId')),
                                'symbol': symbol,
                                'side': side,
                                'type': order_type,
                                'qty': qty,
                                'price': price
                            }
                
                logger.error(f"❌ لا يوجد orderId في النتيجة: {result}")
                return {
                    'error': True,
                    'message': 'No orderId in result',
                    'details': result,
                    'error_type': 'NO_ORDER_ID'
                }
        
        except Exception as e:
            logger.error(f"❌ خطأ في place_order: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': True,
                'message': str(e),
                'error_type': 'EXCEPTION'
            }
    
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
    
    def get_symbol_info(self, category: str, symbol: str) -> Optional[Dict]:
        """
        الحصول على معلومات الرمز (precision, min/max qty, etc.)
        🔧 يعمل بالتوافق مع ExchangeBase interface
        """
        try:
            endpoint = "/v5/market/instruments-info"
            params = {"category": category, "symbol": symbol}
            
            result = self._make_request('GET', endpoint, params)
            
            if result and 'list' in result and result['list']:
                symbol_info = result['list'][0]
                lot_size = symbol_info.get('lotSizeFilter', {})
                price_filter = symbol_info.get('priceFilter', {})
                
                qty_step = lot_size.get('qtyStep', '0.001')
                qty_precision = len(qty_step.split('.')[-1]) if '.' in str(qty_step) else 0
                
                return {
                    'symbol': symbol_info.get('symbol'),
                    'qty_step': qty_step,
                    'min_qty': float(lot_size.get('minQty', '0')),
                    'max_qty': float(lot_size.get('maxQty', '0')),
                    'qty_precision': qty_precision,
                    'price_precision': int(price_filter.get('tickSize', '0.01').count('0') - 1),
                    'min_price': float(price_filter.get('minPrice', '0')),
                    'max_price': float(price_filter.get('maxPrice', '0')),
                    # معلومات إضافية للمنصات الأخرى
                    'lot_size_filter': lot_size,
                    'price_filter': price_filter,
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الرمز: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None



class RealAccountManager:
    """مدير الحسابات الحقيقية - الواجهة الموحدة"""
    
    def __init__(self):
        self.accounts = {}  # {user_id: account_object}
    
    def initialize_account(self, user_id: int, exchange: str, api_key: str, api_secret: str):
        """تهيئة حساب حقيقي للمستخدم"""
        exchange_lower = exchange.lower()
        
        if exchange_lower == 'bybit':
            self.accounts[user_id] = BybitRealAccount(api_key, api_secret)
            logger.info(f"✅ تم تهيئة حساب Bybit للمستخدم {user_id}")
        elif exchange_lower == 'bitget':
            try:
                from api.exchanges.bitget_exchange import BitgetExchange
                self.accounts[user_id] = BitgetExchange('bitget', api_key, api_secret)
                logger.info(f"✅ تم تهيئة حساب Bitget للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ فشل تهيئة Bitget: {e}")
        elif exchange_lower == 'binance':
            try:
                from api.exchanges.binance_exchange import BinanceExchange
                self.accounts[user_id] = BinanceExchange('binance', api_key, api_secret)
                logger.info(f"✅ تم تهيئة حساب Binance للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ فشل تهيئة Binance: {e}")
        elif exchange_lower == 'okx':
            try:
                from api.exchanges.okx_exchange import OKXExchange
                self.accounts[user_id] = OKXExchange('okx', api_key, api_secret)
                logger.info(f"✅ تم تهيئة حساب OKX للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ فشل تهيئة OKX: {e}")
        else:
            logger.error(f"❌ Exchange غير مدعوم: {exchange}")
            logger.info(f"💡 المنصات المدعومة: bybit, bitget, binance, okx")
        
        logger.info(f"📊 تم تهيئة حساب {exchange} حقيقي للمستخدم {user_id}")
    
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

