#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bybit Exchange Implementation - تطبيق منصة Bybit
"""

import logging
import hmac
import hashlib
import time
import requests
from typing import Dict, Optional, List
from urllib.parse import urlencode
import sys
import os

# إضافة المسار الجذري للمشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.exchange_base import ExchangeBase

logger = logging.getLogger(__name__)


class BybitExchange(ExchangeBase):
    """تطبيق منصة Bybit"""
    
    def __init__(self, name: str = 'bybit', api_key: str = None, api_secret: str = None):
        super().__init__(name, api_key, api_secret)
        self.base_url = "https://api.bybit.com"
        self.testnet_url = "https://api-testnet.bybit.com"
        self.use_testnet = False
        
    def _get_base_url(self) -> str:
        """الحصول على الـ URL الأساسي"""
        return self.testnet_url if self.use_testnet else self.base_url
    
    def _generate_signature(self, timestamp: str, recv_window: str, params_str: str) -> str:
        """توليد التوقيع لـ Bybit V5"""
        sign_str = timestamp + str(self.api_key) + recv_window + params_str
        
        signature = hmac.new(
            str(self.api_secret).encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب إلى Bybit API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        try:
            if method == 'GET':
                params_str = urlencode(sorted(params.items())) if params else ""
                signature = self._generate_signature(timestamp, recv_window, params_str)
                
                headers = {
                    'X-BAPI-API-KEY': str(self.api_key),
                    'X-BAPI-SIGN': signature,
                    'X-BAPI-TIMESTAMP': timestamp,
                    'X-BAPI-RECV-WINDOW': recv_window,
                    'X-BAPI-SIGN-TYPE': '2',
                    'Content-Type': 'application/json'
                }
                
                url = f"{self._get_base_url()}{endpoint}"
                if params_str:
                    url += f"?{params_str}"
                
                response = requests.get(url, headers=headers, timeout=10)
                
            elif method == 'POST':
                import json
                params_sorted = {}
                if params:
                    params_sorted = {k: params[k] for k in sorted(params.keys())}
                    params_str = json.dumps(params_sorted, separators=(',', ':'), sort_keys=True)
                else:
                    params_str = ""
                    
                signature = self._generate_signature(timestamp, recv_window, params_str)
                
                headers = {
                    'X-BAPI-API-KEY': str(self.api_key),
                    'X-BAPI-SIGN': signature,
                    'X-BAPI-TIMESTAMP': timestamp,
                    'X-BAPI-RECV-WINDOW': recv_window,
                    'X-BAPI-SIGN-TYPE': '2',
                    'Content-Type': 'application/json'
                }
                
                url = f"{self._get_base_url()}{endpoint}"
                
                if params_str:
                    response = requests.post(url, headers=headers, data=params_str, timeout=10)
                else:
                    response = requests.post(url, headers=headers, timeout=10)
            else:
                logger.error(f"نوع طلب غير مدعوم: {method}")
                return None
            
            if response.status_code == 200:
                result = response.json()
                if result.get('retCode') == 0:
                    return result.get('result')
                else:
                    error_msg = result.get('retMsg', 'Unknown error')
                    error_code = result.get('retCode', 'Unknown code')
                    logger.error(f"خطأ من Bybit API: {error_msg} (Code: {error_code})")
                    
                    # إرجاع معلومات الخطأ بدلاً من None لمعالجة أفضل
                    return {
                        'error': True,
                        'error_type': 'BYBIT_API_ERROR',
                        'retCode': error_code,
                        'retMsg': error_msg,
                        'message': error_msg
                    }
            else:
                logger.error(f"❌ Bybit API Error (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطأ في طلب Bybit: {e}")
            return None
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بـ Bybit"""
        try:
            result = self._make_request('GET', '/v5/account/wallet-balance', {
                'accountType': 'UNIFIED'
            })
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار الاتصال: {e}")
            return False
    
    def get_wallet_balance(self, market_type: str = 'unified') -> Optional[Dict]:
        """جلب رصيد المحفظة"""
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # تحديد نوع الحساب
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
            
            total_equity = safe_float(account.get('totalEquity', 0))
            available_balance = safe_float(account.get('totalAvailableBalance', 0))
            total_wallet_balance = safe_float(account.get('totalWalletBalance', 0))
            unrealized_pnl = safe_float(account.get('totalPerpUPL', 0))
            
            # معالجة العملات
            coins_data = {}
            coins_list = account.get('coin', [])
            
            for coin in coins_list:
                coin_name = coin.get('coin', 'UNKNOWN')
                coins_data[coin_name] = {
                    'equity': safe_float(coin.get('equity', 0)),
                    'available': safe_float(coin.get('availableToWithdraw', 0)),
                    'wallet_balance': safe_float(coin.get('walletBalance', 0)),
                    'unrealized_pnl': safe_float(coin.get('unrealisedPnl', 0))
                }
            
            return {
                'total_equity': total_equity,
                'available_balance': available_balance,
                'total_wallet_balance': total_wallet_balance,
                'unrealized_pnl': unrealized_pnl,
                'coins': coins_data,
                'account_type': account_type
            }
        
        return None
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   quantity: float, price: float = None, **kwargs) -> Optional[Dict]:
        """وضع أمر تداول"""
        params = {
            'category': kwargs.get('category', 'linear'),
            'symbol': symbol,
            'side': 'Buy' if side.lower() == 'buy' else 'Sell',
            'orderType': 'Market' if order_type.lower() == 'market' else 'Limit',
            'qty': str(quantity)
        }
        
        if price:
            params['price'] = str(price)
        
        # إضافة معاملات إضافية
        if 'timeInForce' in kwargs:
            params['timeInForce'] = kwargs['timeInForce']
        if 'stopLoss' in kwargs:
            params['stopLoss'] = str(kwargs['stopLoss'])
        if 'takeProfit' in kwargs:
            params['takeProfit'] = str(kwargs['takeProfit'])
        
        return self._make_request('POST', '/v5/order/create', params)
    
    def get_symbol_info(self, market_type: str, symbol: str) -> Optional[Dict]:
        """الحصول على معلومات الرمز"""
        try:
            category = 'linear' if market_type == 'futures' else 'spot'
            params = {
                'category': category,
                'symbol': symbol
            }
            
            result = self._make_request('GET', '/v5/market/instruments-info', params)
            
            if result and 'list' in result and result['list']:
                symbol_data = result['list'][0]
                return {
                    'symbol': symbol_data.get('symbol'),
                    'baseCoin': symbol_data.get('baseCoin'),
                    'quoteCoin': symbol_data.get('quoteCoin'),
                    'minOrderQty': float(symbol_data.get('lotSizeFilter', {}).get('minOrderQty', '0.001')),
                    'maxOrderQty': float(symbol_data.get('lotSizeFilter', {}).get('maxOrderQty', '1000000')),
                    'qtyStep': float(symbol_data.get('lotSizeFilter', {}).get('qtyStep', '0.001')),
                    'minNotional': float(symbol_data.get('lotSizeFilter', {}).get('minNotional', '10')),
                    'tickSize': float(symbol_data.get('priceFilter', {}).get('tickSize', '0.01'))
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الرمز {symbol}: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        params = {
            'category': 'linear',
            'symbol': symbol,
            'orderId': order_id
        }
        
        result = self._make_request('POST', '/v5/order/cancel', params)
        return result is not None
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """جلب الأوامر المفتوحة"""
        params = {
            'category': 'linear'
        }
        
        if symbol:
            params['symbol'] = symbol
        
        result = self._make_request('GET', '/v5/order/realtime', params)
        
        if result and 'list' in result:
            return result['list']
        return []
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """جلب الصفقات المفتوحة"""
        params = {
            'category': 'linear',
            'settleCoin': 'USDT'
        }
        
        if symbol:
            params['symbol'] = symbol
        
        result = self._make_request('GET', '/v5/position/list', params)
        
        if result and 'list' in result:
            return result['list']
        return []
    
    def close_position(self, symbol: str) -> bool:
        """إغلاق صفقة"""
        # الحصول على معلومات الصفقة الحالية
        positions = self.get_positions(symbol)
        
        if not positions:
            return False
        
        position = positions[0]
        size = abs(float(position.get('size', 0)))
        side = position.get('side', '')
        
        if size == 0:
            return True
        
        # إغلاق الصفقة بأمر معاكس
        close_side = 'sell' if side.lower() == 'buy' else 'buy'
        
        result = self.place_order(
            symbol=symbol,
            side=close_side,
            order_type='market',
            quantity=size,
            category='linear'
        )
        
        return result is not None
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية"""
        params = {
            'category': 'linear',
            'symbol': symbol,
            'buyLeverage': str(leverage),
            'sellLeverage': str(leverage)
        }
        
        result = self._make_request('POST', '/v5/position/set-leverage', params)
        return result is not None
    
    # معلومات المنصة
    def supports_spot(self) -> bool:
        return True
    
    def supports_futures(self) -> bool:
        return True
    
    def supports_leverage(self) -> bool:
        return True
    
    def get_max_leverage(self) -> int:
        return 100
    
    def get_supported_markets(self) -> List[str]:
        return ['spot', 'futures', 'unified']
    
    def get_referral_link(self) -> str:
        return "https://www.bybit.com/invite?ref=OLAZ2M"

