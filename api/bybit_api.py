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
                logger.debug(f"📤 POST إلى {endpoint}")
                logger.debug(f"📋 المعاملات المرتبة: {params_str}")
                
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
                    logger.debug(f"✅ نجح الطلب: {endpoint}")
                    
                    # للأوامر، نحتاج الاستجابة الكاملة لأن orderId قد يكون في result أو في المستوى الأعلى
                    if endpoint == '/v5/order/create':
                        # إرجاع الاستجابة الكاملة للأوامر
                        logger.debug(f"📋 استجابة كاملة للأمر: {result}")
                        return result
                    else:
                        # للطلبات الأخرى، إرجاع result فقط
                        return result.get('result')
                else:
                    ret_msg = result.get('retMsg', '')
                    ret_code = result.get('retCode', 0)
                    
                    # التعامل مع الأخطاء المقبولة (مثل leverage not modified)
                    if ret_code == 110043 or 'leverage not modified' in ret_msg.lower():
                        logger.info(f"ℹ️ Bybit: {ret_msg} (retCode: {ret_code}) - يُعتبر نجاحاً")
                        return {'error': ret_msg, 'retCode': ret_code, 'acceptable': True}
                    
                    logger.error(f"❌ خطأ من Bybit API: {ret_msg}")
                    logger.error(f"   retCode: {ret_code}")
                    # إرجاع الاستجابة الكاملة لمعالجة الأخطاء بشكل أفضل
                    return {'error': ret_msg, 'retCode': ret_code}
            else:
                logger.error(f"❌ Bybit API Error (HTTP {response.status_code}): {response.text}")
                return {'error': f'HTTP {response.status_code}', 'details': response.text}
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ انتهت مهلة الاتصال بـ Bybit")
            return {'error': 'Connection timeout'}
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ فشل الاتصال بـ Bybit")
            return {'error': 'Connection failed'}
        except Exception as e:
            logger.error(f"❌ خطأ في طلب Bybit: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
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
        
        # Bybit V5 API يدعم فقط UNIFIED account type
        account_type = 'UNIFIED'
        
        logger.info(f"🔍 جلب رصيد المحفظة الموحدة من Bybit (نوع السوق: {market_type})")
        
        result = self._make_request('GET', '/v5/account/wallet-balance', {
            'accountType': account_type
        })
        
        # التحقق من وجود خطأ في الاستجابة
        if result and isinstance(result, dict) and 'error' in result:
            logger.error(f"❌ خطأ في الحصول على الرصيد: {result['error']}")
            return None
        
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
        
        # التحقق من وجود خطأ في الاستجابة
        if result and isinstance(result, dict) and 'error' in result:
            logger.error(f"❌ خطأ في الحصول على الصفقات: {result['error']}")
            return []
        
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
        
        # جلب معلومات الرمز للتحقق من الحد الأدنى
        instrument_info = self.get_instrument_info(symbol, category)
        
        if instrument_info:
            min_qty = instrument_info['min_order_qty']
            qty_step = instrument_info['qty_step']
            
            # التحقق من الحد الأدنى
            if qty < min_qty:
                logger.warning(f"⚠️ الكمية {qty} أقل من الحد الأدنى {min_qty}. سيتم رفعها للحد الأدنى.")
                qty = min_qty
            
            # تقريب الكمية حسب الخطوة المسموح بها
            qty = self.round_quantity_to_step(qty, qty_step)
            logger.info(f"✅ الكمية بعد التقريب: {qty}")
        else:
            logger.warning(f"⚠️ لم يتم جلب معلومات الرمز {symbol}. سيتم استخدام الكمية كما هي.")
        
        # تحويل الكمية لنص
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
            leverage_result = self.set_leverage(category, symbol, leverage)
            if not leverage_result:
                logger.warning(f"⚠️ فشل تعيين الرافعة المالية {leverage}x لـ {symbol} - سيتم المتابعة بالرافعة الحالية")
        
        result = self._make_request('POST', '/v5/order/create', params)
        
        # التحقق من وجود خطأ في الاستجابة
        if result and isinstance(result, dict) and 'error' in result:
            error_msg = result['error']
            logger.error(f"❌ خطأ في وضع الأمر: {error_msg}")
            
            # ترجمة رسائل الخطأ الشائعة
            if 'ab not enough' in error_msg.lower():
                error_msg = "الرصيد غير كافي لتنفيذ الصفقة"
            elif 'invalid symbol' in error_msg.lower():
                error_msg = "رمز العملة غير صحيح"
            elif 'invalid price' in error_msg.lower():
                error_msg = "السعر غير صحيح"
            elif 'invalid quantity' in error_msg.lower() or 'qty invalid' in error_msg.lower():
                error_msg = "الكمية غير صحيحة - تحقق من الحد الأدنى للكمية"
            elif 'leverage not modified' in error_msg.lower():
                error_msg = "الرافعة المالية مُعيّنة بالفعل"
            elif 'insufficient balance' in error_msg.lower():
                error_msg = "الرصيد غير كافي"
            elif 'order rejected' in error_msg.lower():
                error_msg = "تم رفض الأمر من المنصة"
            
            return {'error': error_msg, 'details': result.get('details', '')}
        
        if result:
            logger.info(f"🔍 نتيجة place_order من Bybit: {result}")
            
            # البحث عن orderId في مستويات مختلفة من الاستجابة
            order_id = None
            order_link_id = None
            
            # البحث في المستوى الأعلى
            if 'orderId' in result:
                order_id = result['orderId']
                order_link_id = result.get('orderLinkId')
            # البحث في result إذا كان موجود
            elif 'result' in result and isinstance(result['result'], dict):
                inner_result = result['result']
                order_id = inner_result.get('orderId')
                order_link_id = inner_result.get('orderLinkId')
            
            if order_id:
                logger.info(f"✅ تم الحصول على orderId: {order_id}")
                return {
                    'order_id': order_id,
                    'order_link_id': order_link_id,
                    'symbol': symbol,
                    'side': side,
                    'type': order_type,
                    'qty': qty,
                    'price': price,
                    'bybit_response': result  # للتشخيص
                }
            else:
                # تحليل مفصل لسبب عدم وجود orderId
                logger.error(f"❌ لا يوجد orderId في نتيجة Bybit")
                logger.error(f"📋 النتيجة الكاملة: {result}")
                
                # البحث عن أسباب محتملة
                error_details = []
                if 'retCode' in result:
                    error_details.append(f"retCode: {result['retCode']}")
                if 'retMsg' in result:
                    error_details.append(f"retMsg: {result['retMsg']}")
                if 'result' in result:
                    error_details.append(f"result: {result['result']}")
                
                error_summary = "; ".join(error_details) if error_details else "Unknown reason"
                
                return {
                    'error': f'No orderId in Bybit response - {error_summary}',
                    'details': result,
                    'bybit_response': result
                }
        
        logger.error(f"❌ استجابة فارغة من Bybit")
        return {'error': 'Empty result from Bybit'}
    
    def set_leverage(self, category: str, symbol: str, leverage: int) -> bool:
        """تعيين الرافعة المالية على المنصة"""
        try:
            params = {
                'category': category,
                'symbol': symbol,
                'buyLeverage': str(leverage),
                'sellLeverage': str(leverage)
            }
            
            result = self._make_request('POST', '/v5/position/set-leverage', params)
            
            # التحقق من وجود خطأ في النتيجة
            if result and isinstance(result, dict) and 'error' in result:
                error_msg = result['error']
                logger.warning(f"⚠️ تحذير من Bybit عند تعيين الرافعة: {error_msg}")
                
                # بعض الأخطاء مقبولة (مثل الرافعة مُعيّنة بالفعل)
                if 'leverage not modified' in error_msg.lower():
                    logger.info(f"✅ الرافعة المالية {leverage}x مُعيّنة بالفعل لـ {symbol}")
                    return True  # نعتبرها نجاح
                
                return False
            
            if result is not None:
                logger.info(f"✅ تم تعيين الرافعة المالية {leverage}x لـ {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في تعيين الرافعة المالية: {e}")
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
            
            # عكس الجهة للإغلاق (مهم جداً!)
            if side:
                close_side = side
            else:
                # إغلاق صفقة Buy بـ Sell والعكس
                close_side = 'Sell' if position['side'].lower() == 'buy' else 'Buy'
            
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
    
    def get_instrument_info(self, symbol: str, category: str) -> Optional[Dict]:
        """الحصول على معلومات الأداة المالية (مثل الحد الأدنى للكمية وخطوة الكمية)"""
        try:
            api_category = "linear" if category == "futures" else category
            result = self._make_request('GET', '/v5/market/instruments-info', {
                'category': api_category,
                'symbol': symbol
            })
            
            if result and 'list' in result and result['list']:
                instrument = result['list'][0]
                
                # استخراج المعلومات المطلوبة
                min_order_qty = float(instrument.get('lotSizeFilter', {}).get('minOrderQty', 0) or 0)
                qty_step = float(instrument.get('lotSizeFilter', {}).get('qtyStep', 0) or 0)
                
                logger.info(f"📋 معلومات الرمز {symbol}:")
                logger.info(f"   الحد الأدنى: {min_order_qty}")
                logger.info(f"   خطوة الكمية: {qty_step}")
                
                return {
                    'min_order_qty': min_order_qty if min_order_qty > 0 else 0.001,
                    'qty_step': qty_step if qty_step > 0 else 0.001
                }
            
            # في حالة عدم وجود معلومات، إرجاع قيم افتراضية آمنة
            logger.warning(f"⚠️ لم يتم العثور على معلومات الرمز {symbol} - استخدام القيم الافتراضية")
            return {
                'min_order_qty': 0.001,
                'qty_step': 0.001
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على معلومات الرمز {symbol}: {e}")
            return {
                'min_order_qty': 0.001,
                'qty_step': 0.001
            }
    
    def round_quantity_to_step(self, qty: float, step: float) -> float:
        """تقريب الكمية لخطوة محددة"""
        if step <= 0:
            return round(qty, 6)
        
        return round(qty / step) * step



class RealAccountManager:
    """مدير الحسابات الحقيقية - الواجهة الموحدة"""
    
    def __init__(self):
        self.accounts = {}  # {user_id: account_object}
    
    def initialize_account(self, user_id: int, exchange: str, api_key: str, api_secret: str):
        """تهيئة حساب حقيقي للمستخدم"""
        if exchange.lower() == 'bybit':
            self.accounts[user_id] = BybitRealAccount(api_key, api_secret)
        else:
            logger.error(f"Exchange غير مدعوم: {exchange}")
        
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

