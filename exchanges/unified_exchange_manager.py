#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المنصات الموحد - Unified Exchange Manager
دمج جميع وظائف إدارة المنصات في ملف واحد منظم
"""

import logging
import hmac
import hashlib
import time
import requests
from typing import Dict, Optional, List, Any
from urllib.parse import urlencode
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ==================== الكلاس الأساسي للمنصات ====================

class BaseExchange(ABC):
    """الكلاس الأساسي لجميع المنصات"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
    
    @abstractmethod
    def _generate_signature(self, timestamp: str, recv_window: str, params_str: str) -> str:
        """توليد التوقيع للمنصة"""
        pass
    
    @abstractmethod
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب للمنصة"""
        pass
    
    @abstractmethod
    def get_wallet_balance(self, market_type: str = 'spot') -> Optional[Dict]:
        """جلب رصيد المحفظة"""
        pass
    
    @abstractmethod
    def get_ticker_price(self, symbol: str, category: str = 'spot') -> Optional[float]:
        """جلب السعر الحالي"""
        pass
    
    @abstractmethod
    def place_order(self, **kwargs) -> Optional[Dict]:
        """وضع أمر تداول"""
        pass
    
    @abstractmethod
    def get_open_positions(self, category: str = 'linear') -> List[Dict]:
        """جلب الصفقات المفتوحة"""
        pass

# ==================== مدير Bybit الموحد ====================

class UnifiedBybitManager(BaseExchange):
    """مدير Bybit الموحد مع جميع الوظائف"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret, "https://api.bybit.com")
    
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
                logger.error(f"Method غير مدعوم: {method}")
                return None
            
            logger.info(f"Bybit API Response Status: {response.status_code}")
            logger.info(f"Bybit API Response: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"خطأ في API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في طلب API: {e}")
            return None
    
    def get_wallet_balance(self, market_type: str = 'spot') -> Optional[Dict]:
        """جلب رصيد المحفظة"""
        try:
            if market_type == 'spot':
                result = self._make_request('GET', '/v5/account/wallet-balance', {
                    'accountType': 'SPOT'
                })
            else:  # futures
                result = self._make_request('GET', '/v5/account/wallet-balance', {
                    'accountType': 'UNIFIED'
                })
            
            if result and 'result' in result:
                balance_data = result['result']
                if 'list' in balance_data and balance_data['list']:
                    account = balance_data['list'][0]
                    return {
                        'total_equity': float(account.get('totalEquity', 0)),
                        'available_balance': float(account.get('availableBalance', 0)),
                        'total_wallet_balance': float(account.get('totalWalletBalance', 0)),
                        'unrealized_pnl': float(account.get('unrealisedPnl', 0))
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب رصيد المحفظة: {e}")
            return None
    
    def get_ticker_price(self, symbol: str, category: str = 'spot') -> Optional[float]:
        """جلب السعر الحالي"""
        try:
            if category == 'spot':
                result = self._make_request('GET', '/v5/market/tickers', {
                    'category': 'spot',
                    'symbol': symbol
                })
            else:  # futures
                result = self._make_request('GET', '/v5/market/tickers', {
                    'category': 'linear',
                    'symbol': symbol
                })
            
            if result and 'result' in result and 'list' in result['result']:
                ticker_data = result['result']['list']
                if ticker_data:
                    return float(ticker_data[0].get('lastPrice', 0))
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب السعر: {e}")
            return None
    
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
            try:
                leverage_result = self.set_leverage(category, symbol, leverage)
                if leverage_result:
                    logger.info(f"تم تعيين الرافعة {leverage}x للرمز {symbol}")
                else:
                    logger.warning(f"فشل في تعيين الرافعة {leverage}x للرمز {symbol}")
            except Exception as e:
                logger.error(f"خطأ في تعيين الرافعة: {e}")
        
        result = self._make_request('POST', '/v5/order/create', params)
        
        if result:
            logger.info(f"نتيجة وضع الأمر: {result}")
            return result
        else:
            logger.error("فشل في وضع الأمر")
            return None
    
    def set_leverage(self, category: str, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية"""
        try:
            params = {
                'category': category,
                'symbol': symbol,
                'buyLeverage': str(leverage),
                'sellLeverage': str(leverage)
            }
            
            result = self._make_request('POST', '/v5/position/set-leverage', params)
            
            if result and result.get('retCode') == 0:
                logger.info(f"تم تعيين الرافعة {leverage}x للرمز {symbol}")
                return True
            else:
                logger.error(f"فشل في تعيين الرافعة: {result}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تعيين الرافعة: {e}")
            return False
    
    def get_open_positions(self, category: str = 'linear') -> List[Dict]:
        """جلب الصفقات المفتوحة"""
        try:
            result = self._make_request('GET', '/v5/position/list', {
                'category': category
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
            if result and 'result' in result and 'list' in result['result']:
                for pos in result['result']['list']:
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
            
        except Exception as e:
            logger.error(f"خطأ في جلب الصفقات المفتوحة: {e}")
            return []
    
    def close_position(self, category: str, symbol: str, side: str) -> Optional[Dict]:
        """إغلاق صفقة مفتوحة"""
        try:
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
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
            return None
    
    def get_order_history(self, category: str = 'linear', limit: int = 50) -> List[Dict]:
        """الحصول على سجل الأوامر"""
        try:
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
            if result and 'result' in result and 'list' in result['result']:
                for order in result['result']['list']:
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
            
        except Exception as e:
            logger.error(f"خطأ في جلب سجل الأوامر: {e}")
            return []
    
    def check_symbol_exists(self, symbol: str, category: str) -> bool:
        """التحقق من وجود الرمز"""
        try:
            if category == 'spot':
                result = self._make_request('GET', '/v5/market/instruments-info', {
                    'category': 'spot',
                    'symbol': symbol
                })
            else:  # futures
                result = self._make_request('GET', '/v5/market/instruments-info', {
                    'category': 'linear',
                    'symbol': symbol
                })
            
            if result and 'result' in result and 'list' in result['result']:
                return len(result['result']['list']) > 0
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من وجود الرمز: {e}")
            return False
    
    def get_spot_pairs(self) -> List[str]:
        """جلب قائمة أزواج السبوت"""
        try:
            result = self._make_request('GET', '/v5/market/instruments-info', {
                'category': 'spot'
            })
            
            pairs = []
            if result and 'result' in result and 'list' in result['result']:
                for instrument in result['result']['list']:
                    symbol = instrument.get('symbol')
                    if symbol and instrument.get('status') == 'Trading':
                        pairs.append(symbol)
            
            return pairs
            
        except Exception as e:
            logger.error(f"خطأ في جلب أزواج السبوت: {e}")
            return []
    
    def get_futures_pairs(self) -> List[str]:
        """جلب قائمة أزواج الفيوتشر"""
        try:
            result = self._make_request('GET', '/v5/market/instruments-info', {
                'category': 'linear'
            })
            
            pairs = []
            if result and 'result' in result and 'list' in result['result']:
                for instrument in result['result']['list']:
                    symbol = instrument.get('symbol')
                    if symbol and instrument.get('status') == 'Trading':
                        pairs.append(symbol)
            
            return pairs
            
        except Exception as e:
            logger.error(f"خطأ في جلب أزواج الفيوتشر: {e}")
            return []

# ==================== مدير MEXC الموحد ====================

class UnifiedMEXCManager(BaseExchange):
    """مدير MEXC الموحد مع جميع الوظائف"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret, "https://api.mexc.com")
    
    def _generate_signature(self, timestamp: str, recv_window: str, params_str: str) -> str:
        """توليد التوقيع لـ MEXC"""
        sign_str = timestamp + self.api_key + recv_window + params_str
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        logger.info(f"MEXC Signature Debug - signature: {signature}")
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب إلى MEXC API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # بناء query string
        params_str = urlencode(sorted(params.items())) if params else ""
        
        # توليد التوقيع
        signature = self._generate_signature(timestamp, recv_window, params_str)
        
        # Headers
        headers = {
            'X-MEXC-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        if params_str:
            url += f"?{params_str}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                logger.error(f"Method غير مدعوم: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"خطأ في MEXC API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في طلب MEXC API: {e}")
            return None
    
    def get_wallet_balance(self, market_type: str = 'spot') -> Optional[Dict]:
        """جلب رصيد المحفظة"""
        try:
            result = self._make_request('GET', '/api/v3/account')
            
            if result:
                total_balance = 0.0
                available_balance = 0.0
                
                for balance in result.get('balances', []):
                    asset = balance.get('asset', '')
                    free = float(balance.get('free', 0))
                    locked = float(balance.get('locked', 0))
                    
                    if asset == 'USDT':
                        total_balance += free + locked
                        available_balance += free
                
                return {
                    'total_equity': total_balance,
                    'available_balance': available_balance,
                    'total_wallet_balance': total_balance,
                    'unrealized_pnl': 0.0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب رصيد MEXC: {e}")
            return None
    
    def get_ticker_price(self, symbol: str, category: str = 'spot') -> Optional[float]:
        """جلب السعر الحالي"""
        try:
            result = self._make_request('GET', '/api/v3/ticker/price', {
                'symbol': symbol
            })
            
            if result and 'price' in result:
                return float(result['price'])
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب سعر MEXC: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'MARKET', price: float = None) -> Optional[Dict]:
        """وضع أمر تداول"""
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': str(quantity)
            }
            
            if price and order_type.upper() == 'LIMIT':
                params['price'] = str(price)
            
            result = self._make_request('POST', '/api/v3/order', params)
            
            if result:
                logger.info(f"نتيجة وضع الأمر في MEXC: {result}")
                return result
            else:
                logger.error("فشل في وضع الأمر في MEXC")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في وضع الأمر في MEXC: {e}")
            return None
    
    def get_open_positions(self, category: str = 'linear') -> List[Dict]:
        """جلب الصفقات المفتوحة (MEXC يدعم السبوت فقط)"""
        # MEXC لا يدعم الفيوتشر عبر API في هذا التطبيق
        return []
    
    def get_order_history(self, limit: int = 50) -> List[Dict]:
        """الحصول على سجل الأوامر"""
        try:
            result = self._make_request('GET', '/api/v3/allOrders', {
                'limit': limit
            })
            
            orders = []
            if result:
                for order in result:
                    orders.append({
                        'order_id': order.get('orderId'),
                        'symbol': order.get('symbol'),
                        'side': order.get('side'),
                        'type': order.get('type'),
                        'qty': float(order.get('origQty', 0)),
                        'price': float(order.get('price', 0)),
                        'avg_price': float(order.get('avgPrice', 0)),
                        'status': order.get('status'),
                        'created_time': order.get('time'),
                        'updated_time': order.get('updateTime')
                    })
            
            return orders
            
        except Exception as e:
            logger.error(f"خطأ في جلب سجل أوامر MEXC: {e}")
            return []

# ==================== مدير المنصات الموحد ====================

class UnifiedExchangeManager:
    """مدير المنصات الموحد - يدير جميع المنصات"""
    
    def __init__(self):
        self.exchanges: Dict[str, Dict[int, BaseExchange]] = {
            'bybit': {},
            'mexc': {}
        }
        logger.info("تم تهيئة مدير المنصات الموحد")
    
    def get_exchange(self, user_id: int, exchange: str) -> Optional[BaseExchange]:
        """الحصول على منصة للمستخدم"""
        try:
            if exchange in self.exchanges and user_id in self.exchanges[exchange]:
                return self.exchanges[exchange][user_id]
            return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على المنصة: {e}")
            return None
    
    def initialize_exchange(self, user_id: int, exchange: str, api_key: str, api_secret: str) -> bool:
        """تهيئة منصة للمستخدم"""
        try:
            if exchange.lower() == 'bybit':
                exchange_manager = UnifiedBybitManager(api_key, api_secret)
            elif exchange.lower() == 'mexc':
                exchange_manager = UnifiedMEXCManager(api_key, api_secret)
            else:
                logger.error(f"منصة غير مدعومة: {exchange}")
                return False
            
            self.exchanges[exchange.lower()][user_id] = exchange_manager
            logger.info(f"تم تهيئة منصة {exchange} للمستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة المنصة: {e}")
            return False
    
    def remove_exchange(self, user_id: int, exchange: str) -> bool:
        """إزالة منصة للمستخدم"""
        try:
            if exchange.lower() in self.exchanges and user_id in self.exchanges[exchange.lower()]:
                del self.exchanges[exchange.lower()][user_id]
                logger.info(f"تم إزالة منصة {exchange} للمستخدم {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في إزالة المنصة: {e}")
            return False
    
    def get_all_exchanges(self) -> Dict[str, Dict[int, BaseExchange]]:
        """الحصول على جميع المنصات"""
        return self.exchanges.copy()
    
    def get_exchange_count(self, exchange: str) -> int:
        """الحصول على عدد المستخدمين لمنصة معينة"""
        try:
            if exchange.lower() in self.exchanges:
                return len(self.exchanges[exchange.lower()])
            return 0
        except Exception as e:
            logger.error(f"خطأ في حساب عدد المنصات: {e}")
            return 0

# ==================== إنشاء مثيل مدير المنصات الموحد ====================

# إنشاء مثيل مدير المنصات الموحد
unified_exchange_manager = UnifiedExchangeManager()

# تصدير المدير للاستخدام في الملفات الأخرى
exchange_manager = unified_exchange_manager

logger.info("تم إنشاء مدير المنصات الموحد بنجاح")
