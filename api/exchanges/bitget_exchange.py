#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bitget Exchange Implementation - تطبيق منصة Bitget
منصة تداول عالمية تدعم Spot و Futures مع رافعة مالية حتى 125x
"""

import logging
import hmac
import hashlib
import time
import base64
import requests
from typing import Dict, Optional, List
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.exchange_base import ExchangeBase

logger = logging.getLogger(__name__)


class BitgetExchange(ExchangeBase):
    """تطبيق منصة Bitget - كامل وجاهز للاستخدام"""
    
    def __init__(self, name: str = 'bitget', api_key: str = None, api_secret: str = None):
        super().__init__(name, api_key, api_secret)
        self.base_url = "https://api.bitget.com"
        self.passphrase = None  # Bitget تحتاج passphrase
        
    def set_passphrase(self, passphrase: str):
        """تعيين passphrase (مطلوب لـ Bitget)"""
        self.passphrase = passphrase
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """
        توليد التوقيع لـ Bitget API
        
        Signature = base64(hmac-sha256(timestamp + method + requestPath + body, secret))
        """
        if not self.api_secret:
            raise ValueError("API Secret is required")
        
        message = timestamp + method + request_path + body
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, body: Dict = None) -> Optional[Dict]:
        """إرسال طلب إلى Bitget API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        
        try:
            # بناء request_path
            request_path = endpoint
            if params and method == 'GET':
                query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
                request_path += f"?{query_string}"
            
            # بناء body للطلبات POST
            body_str = ''
            if body and method == 'POST':
                body_str = json.dumps(body, separators=(',', ':'))
            
            # توليد التوقيع
            signature = self._generate_signature(timestamp, method, request_path, body_str)
            
            # بناء Headers
            headers = {
                'ACCESS-KEY': str(self.api_key),
                'ACCESS-SIGN': signature,
                'ACCESS-TIMESTAMP': timestamp,
                'Content-Type': 'application/json',
                'locale': 'en-US'
            }
            
            # إضافة passphrase إن وجد
            if self.passphrase:
                headers['ACCESS-PASSPHRASE'] = self.passphrase
            
            # إرسال الطلب
            url = f"{self.base_url}{request_path}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=body_str, timeout=10)
            else:
                logger.error(f"❌ نوع طلب غير مدعوم: {method}")
                return None
            
            # معالجة الاستجابة
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == '00000':  # Bitget success code
                    return result.get('data')
                else:
                    logger.error(f"❌ خطأ من Bitget API: {result.get('msg')}")
                    return None
            else:
                logger.error(f"❌ Bitget API Error (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطأ في طلب Bitget: {e}")
            return None
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بـ Bitget"""
        try:
            # استخدام endpoint لجلب معلومات الحساب
            result = self._make_request('GET', '/api/spot/v1/account/assets')
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار الاتصال: {e}")
            return False
    
    def check_symbol_exists(self, symbol: str, market_type: str) -> bool:
        """التحقق من وجود رمز معين في منصة Bitget"""
        try:
            # تحديد نوع السوق
            if market_type.lower() == 'spot':
                endpoint = '/api/spot/v1/public/products'
            else:  # futures
                endpoint = '/api/mix/v1/market/contracts'
                # Bitget تستخدم صيغة مختلفة للفيوتشر (مثل BTCUSDT_UMCBL)
                if not symbol.endswith('_UMCBL'):
                    symbol = f"{symbol}_UMCBL"
            
            result = self._make_request('GET', endpoint)
            
            if result and 'data' in result:
                # البحث عن الرمز في القائمة
                for item in result['data']:
                    if market_type.lower() == 'spot':
                        if item.get('symbolName') == symbol or item.get('symbol') == symbol:
                            logger.info(f"✅ الرمز {symbol} موجود في Bitget {market_type}")
                            return True
                    else:  # futures
                        if item.get('symbol') == symbol:
                            logger.info(f"✅ الرمز {symbol} موجود في Bitget {market_type}")
                            return True
            
            logger.warning(f"⚠️ الرمز {symbol} غير موجود في Bitget {market_type}")
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من وجود الرمز {symbol}: {e}")
            # في حالة الخطأ، نعيد True لتجنب حظر الإشارات
            return True
    
    def get_wallet_balance(self, market_type: str = 'spot') -> Optional[Dict]:
        """
        جلب رصيد المحفظة
        
        Args:
            market_type: 'spot' أو 'futures'
        """
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        try:
            if market_type == 'spot':
                # جلب رصيد Spot
                result = self._make_request('GET', '/api/spot/v1/account/assets')
                
                if result:
                    total_equity = 0.0
                    available_balance = 0.0
                    coins_data = {}
                    
                    for asset in result:
                        coin_name = asset.get('coinName', 'UNKNOWN')
                        available = safe_float(asset.get('available', 0))
                        frozen = safe_float(asset.get('frozen', 0))
                        total = available + frozen
                        
                        if total > 0:
                            total_equity += total
                            available_balance += available
                            
                            coins_data[coin_name] = {
                                'equity': total,
                                'available': available,
                                'frozen': frozen,
                                'wallet_balance': total,
                                'unrealized_pnl': 0.0
                            }
                    
                    return {
                        'total_equity': total_equity,
                        'available_balance': available_balance,
                        'total_wallet_balance': total_equity,
                        'unrealized_pnl': 0.0,
                        'coins': coins_data,
                        'account_type': 'SPOT'
                    }
            
            elif market_type == 'futures':
                # جلب رصيد Futures (USDT-M)
                result = self._make_request('GET', '/api/mix/v1/account/accounts', {
                    'productType': 'umcbl'  # USDT-M Futures
                })
                
                if result:
                    total_equity = safe_float(result.get('equity', 0))
                    available = safe_float(result.get('available', 0))
                    frozen = safe_float(result.get('frozen', 0))
                    unrealized_pnl = safe_float(result.get('unrealizedPL', 0))
                    
                    return {
                        'total_equity': total_equity,
                        'available_balance': available,
                        'total_wallet_balance': total_equity - unrealized_pnl,
                        'unrealized_pnl': unrealized_pnl,
                        'coins': {
                            'USDT': {
                                'equity': total_equity,
                                'available': available,
                                'frozen': frozen,
                                'wallet_balance': total_equity - unrealized_pnl,
                                'unrealized_pnl': unrealized_pnl
                            }
                        },
                        'account_type': 'FUTURES'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الرصيد: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   quantity: float, price: float = None, **kwargs) -> Optional[Dict]:
        """
        وضع أمر تداول
        
        Args:
            symbol: رمز العملة (مثل 'BTCUSDT')
            side: 'buy' أو 'sell'
            order_type: 'market' أو 'limit'
            quantity: الكمية
            price: السعر (للأوامر المحددة)
            **kwargs: معاملات إضافية (market_type, etc.)
        """
        market_type = kwargs.get('market_type', 'spot')
        
        try:
            if market_type == 'spot':
                # Spot Order
                order_data = {
                    'symbol': symbol,
                    'side': side.lower(),
                    'orderType': 'market' if order_type.lower() == 'market' else 'limit',
                    'force': 'gtc',
                    'size': str(quantity)
                }
                
                if price and order_type.lower() == 'limit':
                    order_data['price'] = str(price)
                
                result = self._make_request('POST', '/api/spot/v1/trade/orders', body=order_data)
                return result
            
            elif market_type == 'futures':
                # Futures Order
                order_data = {
                    'symbol': symbol,
                    'marginCoin': 'USDT',
                    'side': 'open_long' if side.lower() == 'buy' else 'open_short',
                    'orderType': 'market' if order_type.lower() == 'market' else 'limit',
                    'size': str(quantity)
                }
                
                if price and order_type.lower() == 'limit':
                    order_data['price'] = str(price)
                
                result = self._make_request('POST', '/api/mix/v1/order/placeOrder', body=order_data)
                return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في وضع الأمر: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        try:
            result = self._make_request('POST', '/api/spot/v1/trade/cancel-order', body={
                'symbol': symbol,
                'orderId': order_id
            })
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في إلغاء الأمر: {e}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """جلب الأوامر المفتوحة"""
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            result = self._make_request('GET', '/api/spot/v1/trade/open-orders', params)
            
            if result:
                return result
            return []
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأوامر: {e}")
            return []
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """جلب الصفقات المفتوحة (Futures فقط)"""
        try:
            params = {
                'productType': 'umcbl',
                'marginCoin': 'USDT'
            }
            
            if symbol:
                params['symbol'] = symbol
            
            result = self._make_request('GET', '/api/mix/v1/position/allPosition', params)
            
            if result:
                return result
            return []
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الصفقات: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """إغلاق صفقة (Futures)"""
        try:
            # الحصول على معلومات الصفقة
            positions = self.get_positions(symbol)
            
            if not positions:
                return False
            
            position = positions[0]
            size = abs(float(position.get('total', 0)))
            side = position.get('holdSide', '')
            
            if size == 0:
                return True
            
            # إغلاق الصفقة
            close_side = 'close_long' if side == 'long' else 'close_short'
            
            result = self._make_request('POST', '/api/mix/v1/order/placeOrder', body={
                'symbol': symbol,
                'marginCoin': 'USDT',
                'side': close_side,
                'orderType': 'market',
                'size': str(size)
            })
            
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقة: {e}")
            return False
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية (Futures)"""
        try:
            result = self._make_request('POST', '/api/mix/v1/account/setLeverage', body={
                'symbol': symbol,
                'marginCoin': 'USDT',
                'leverage': str(leverage)
            })
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في تعيين الرافعة: {e}")
            return False
    
    # معلومات المنصة
    def supports_spot(self) -> bool:
        return True
    
    def supports_futures(self) -> bool:
        return True
    
    def supports_leverage(self) -> bool:
        return True
    
    def get_max_leverage(self) -> int:
        return 125  # Bitget تدعم حتى 125x
    
    def get_supported_markets(self) -> List[str]:
        return ['spot', 'futures', 'usdt-futures', 'coin-futures']
    
    def get_referral_link(self) -> str:
        return "https://www.bitget.com/referral/register?from=referral&clacCode=YOUR_CODE"


# ملاحظات هامة لاستخدام Bitget:
"""
📝 **متطلبات Bitget API:**

1. **Passphrase مطلوب:**
   عند إنشاء API Key في Bitget، ستحتاج إلى إنشاء passphrase
   يجب تعيينه بعد إنشاء النسخة:
   
   ```python
   bitget = BitgetExchange('bitget', api_key, api_secret)
   bitget.set_passphrase('your_passphrase')
   ```

2. **رابط API Documentation:**
   https://bitgetlimited.github.io/apidoc/en/spot/

3. **أنواع الحسابات:**
   - Spot: التداول الفوري
   - USDT-M Futures: العقود الآجلة بـ USDT
   - Coin-M Futures: العقود الآجلة بالعملات

4. **الصلاحيات المطلوبة:**
   - Read (قراءة)
   - Trade (تداول)
   - Transfer (تحويل) - اختياري

5. **حدود API:**
   - 20 طلب/ثانية للـ Spot
   - 10 طلب/ثانية للـ Futures

6. **Testnet:**
   غير متوفر حالياً، استخدم مبالغ صغيرة للاختبار

7. **رابط الإحالة:**
   احصل على عمولات من المستخدمين الجدد:
   https://www.bitget.com/referral/
"""

