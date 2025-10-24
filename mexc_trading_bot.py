#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت التداول على منصة MEXC
يدعم التداول الفوري (Spot) فقط - لا يدعم الفيوتشر
"""

import logging
import hashlib
import hmac
import time
import requests
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

class MEXCTradingBot:
    """فئة للتداول على منصة MEXC - Spot فقط"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        تهيئة بوت MEXC
        
        Args:
            api_key: مفتاح API من MEXC
            api_secret: السر الخاص بـ API
            testnet: استخدام الشبكة التجريبية (غير مدعوم حالياً في MEXC)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        # MEXC لا تدعم testnet، فقط الحساب الحقيقي
        self.base_url = "https://api.mexc.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MEXC-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
        
        # Rate Limiting: حسب ملف السياق - حتى 5 طلبات/ثانية
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms بين الطلبات (5 طلبات/ثانية)
        
        logger.info(f"تم تهيئة MEXC Trading Bot - Base URL: {self.base_url}")
        logger.info(f"⚙️ Rate Limit: {1/self.min_request_interval} طلبات/ثانية")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        توليد التوقيع للطلبات وفقاً للوثائق الرسمية لـ MEXC
        الصيغة الصحيحة: access_key + timestamp + query_string
        
        Args:
            params: معاملات الطلب (بدون signature)
            
        Returns:
            التوقيع
        """
        # إزالة signature إذا كانت موجودة (لتجنب التوقيع الذاتي)
        params_copy = {k: v for k, v in params.items() if k != 'signature'}
        
        # استخراج timestamp قبل إزالته من المعاملات
        timestamp = str(params_copy.get('timestamp', ''))
        
        # إزالة timestamp من المعاملات لأنه يُضاف منفصلاً في signature_string
        params_copy.pop('timestamp', None)
        
        # ترتيب أبجدي صارم كما هو مطلوب من MEXC
        sorted_items = sorted(params_copy.items())
        
        # بناء query string يدوياً للتأكد من التنسيق الصحيح
        query_parts = []
        for key, value in sorted_items:
            query_parts.append(f"{key}={value}")
        
        query_string = '&'.join(query_parts)
        
        # الصيغة الصحيحة حسب الوثائق الرسمية: access_key + timestamp + query_string
        signature_string = self.api_key + timestamp + query_string
        
        logger.info(f"🔑 Query string: {query_string}")
        logger.info(f"🔐 API Key: {self.api_key}")
        logger.info(f"⏰ Timestamp: {timestamp}")
        logger.info(f"📝 Signature String: {signature_string}")
        logger.info(f"🔐 API Secret (أول 8 أحرف): {self.api_secret[:8]}...")
        
        # توليد التوقيع باستخدام HMAC-SHA256 حسب الوثائق الرسمية
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.info(f"✅ التوقيع المُولد: {signature}")
        
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Optional[Dict]:
        """
        إرسال طلب إلى MEXC API
        
        Args:
            method: نوع الطلب (GET, POST, DELETE)
            endpoint: نقطة النهاية
            params: معاملات الطلب
            signed: هل يحتاج الطلب إلى توقيع
            
        Returns:
            استجابة API أو None في حالة الخطأ
        """
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Rate Limiting: التحكم في معدل الطلبات (5 طلبات/ثانية)
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                logger.info(f"⏳ Rate Limit: انتظار {sleep_time:.3f} ثانية...")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
            
            if signed:
                # إضافة timestamp بـ UTC بالميلي ثانية (مطلوب من MEXC)
                timestamp = int(time.time() * 1000)
                params['timestamp'] = timestamp
                
                logger.info(f"⏰ Timestamp: {timestamp}")
                logger.info(f"📅 الوقت الحالي: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
                
                # توليد التوقيع (بدون signature في المعاملات)
                signature = self._generate_signature(params)
                
                # إضافة التوقيع إلى المعاملات
                params['signature'] = signature
                
                logger.info(f"🔐 التوقيع المُولد: {signature}")
                logger.info(f"📋 المعاملات النهائية: {params}")
            
            # MEXC Spot API: إرسال البيانات في query string للطلبات الموقعة
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                # للطلبات الموقعة: إرسال جميع المعاملات في query string
                if signed:
                    response = self.session.post(url, params=params, timeout=10)
                else:
                    # للطلبات غير الموقعة: إرسال في body
                    response = self.session.post(url, json=params, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                logger.error(f"نوع طلب غير مدعوم: {method}")
                return None
            
            # تسجيل تفاصيل الطلب للمساعدة في التشخيص
            logger.info(f"📤 طلب MEXC: {method} {endpoint}")
            logger.info(f"🔗 الرابط الكامل: {url}")
            logger.info(f"📋 المعاملات المرسلة: {params}")
            
            # تسجيل URL النهائي للطلبات الموقعة
            if signed and method == 'POST':
                query_string = urlencode(params)
                full_url = f"{url}?{query_string}"
                logger.info(f"🌐 الرابط النهائي: {full_url}")
                
                # تسجيل مفصل للتأكد من صحة الطلب
                logger.info(f"📋 تفاصيل الطلب النهائي:")
                logger.info(f"   - Method: {method}")
                logger.info(f"   - URL: {url}")
                logger.info(f"   - Headers: {dict(self.session.headers)}")
                logger.info(f"   - Params: {params}")
            
            # التحقق من حالة الاستجابة
            if response.status_code != 200:
                logger.error(f"خطأ في استجابة MEXC: {response.status_code}")
                logger.error(f"محتوى الخطأ: {response.text}")
                
                # معالجة أخطاء محددة حسب ملف السياق
                if response.status_code == 429:
                    logger.warning("⚠️ Rate Limit تم تجاوزه (429) - توقف مؤقت...")
                    time.sleep(2)  # توقف مؤقت (backoff)
                    return None
                elif response.status_code >= 500:
                    logger.error("❌ خطأ في خادم MEXC (5xx) - يُنصح بالاستعلام عن حالة الطلب")
                
                # محاولة تحليل الخطأ
                try:
                    error_data = response.json()
                    if 'msg' in error_data:
                        logger.error(f"رسالة الخطأ من MEXC: {error_data['msg']}")
                    if 'code' in error_data:
                        logger.error(f"كود الخطأ من MEXC: {error_data['code']}")
                except:
                    pass
                
                return None
            
            response_data = response.json()
            
            # التحقق من وجود خطأ في الاستجابة
            if 'code' in response_data and response_data['code'] != 0:
                logger.error(f"خطأ من MEXC API: {response_data}")
                if 'msg' in response_data:
                    logger.error(f"رسالة الخطأ: {response_data['msg']}")
                return None
            
            logger.info(f"استجابة MEXC ناجحة: {response_data}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في الطلب إلى MEXC: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"تفاصيل الخطأ: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"خطأ غير متوقع في MEXC: {e}")
            return None
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        الحصول على رصيد الحساب
        
        Returns:
            معلومات الرصيد أو None في حالة الخطأ
        """
        try:
            result = self._make_request('GET', '/api/v3/account', signed=True)
            
            if result and 'balances' in result:
                # تنسيق البيانات
                balances = {}
                for balance in result['balances']:
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    
                    if free > 0 or locked > 0:
                        balances[asset] = {
                            'free': free,
                            'locked': locked,
                            'total': free + locked
                        }
                
                return {
                    'balances': balances,
                    'can_trade': result.get('canTrade', False),
                    'can_withdraw': result.get('canWithdraw', False),
                    'can_deposit': result.get('canDeposit', False)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على رصيد MEXC: {e}")
            return None
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """
        الحصول على سعر الرمز الحالي
        
        Args:
            symbol: رمز العملة (مثل: BTCUSDT)
            
        Returns:
            السعر الحالي أو None في حالة الخطأ
        """
        try:
            result = self._make_request('GET', '/api/v3/ticker/price', {'symbol': symbol})
            
            if result and 'price' in result:
                return float(result['price'])
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على سعر {symbol} من MEXC: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        الحصول على معلومات الرمز
        
        Args:
            symbol: رمز العملة
            
        Returns:
            معلومات الرمز أو None في حالة الخطأ
        """
        try:
            result = self._make_request('GET', '/api/v3/exchangeInfo')
            
            if result and 'symbols' in result:
                for sym in result['symbols']:
                    if sym['symbol'] == symbol:
                        # استخراج معلومات الفلاتر
                        filters = {}
                        for f in sym.get('filters', []):
                            filters[f['filterType']] = f
                        
                        # تحديد ما إذا كان التداول الفوري مسموح
                        permissions = sym.get('permissions', [])
                        status = sym['status']
                        is_spot_allowed = 'SPOT' in permissions and status == '1'
                        
                        logger.info(f"🔍 تحليل معلومات الرمز {symbol}:")
                        logger.info(f"   - الحالة: {status}")
                        logger.info(f"   - الصلاحيات: {permissions}")
                        logger.info(f"   - التداول الفوري مسموح: {is_spot_allowed}")
                        
                        return {
                            'symbol': sym['symbol'],
                            'status': sym['status'],
                            'base_asset': sym['baseAsset'],
                            'quote_asset': sym['quoteAsset'],
                            'filters': filters,
                            'is_spot_trading_allowed': is_spot_allowed,
                            'permissions': permissions
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات {symbol} من MEXC: {e}")
            return None
    
    def _format_quantity(self, quantity: float, symbol_info: Dict) -> str:
        """
        تنسيق الكمية حسب متطلبات الرمز
        
        Args:
            quantity: الكمية
            symbol_info: معلومات الرمز
            
        Returns:
            الكمية المنسقة
        """
        try:
            # الحصول على فلاتر الرمز
            filters = symbol_info.get('filters', {})
            lot_size_filter = filters.get('LOT_SIZE')
            
            if not lot_size_filter:
                logger.warning("لم يتم العثور على فلتر LOT_SIZE، استخدام القيم الافتراضية")
                return f"{quantity:.6f}".rstrip('0').rstrip('.')
            
            step_size = float(lot_size_filter.get('stepSize', '1'))
            min_qty = float(lot_size_filter.get('minQty', '0'))
            max_qty = float(lot_size_filter.get('maxQty', '0'))
            
            logger.info(f"فلاتر الكمية - Step: {step_size}, Min: {min_qty}, Max: {max_qty}")
            
            # التحقق من الحد الأدنى
            if quantity < min_qty:
                logger.error(f"الكمية أقل من الحد الأدنى: {quantity} < {min_qty}")
                return f"{min_qty:.6f}".rstrip('0').rstrip('.')
            
            # التحقق من الحد الأقصى
            if max_qty > 0 and quantity > max_qty:
                logger.error(f"الكمية أكبر من الحد الأقصى: {quantity} > {max_qty}")
                return f"{max_qty:.6f}".rstrip('0').rstrip('.')
            
            # حساب عدد الأرقام العشرية من step_size
            step_str = f"{step_size:.10f}".rstrip('0')
            if '.' in step_str:
                decimals = len(step_str.split('.')[1])
            else:
                decimals = 0
            
            # تقريب الكمية إلى مضاعف step_size
            quantity_decimal = Decimal(str(quantity))
            step_decimal = Decimal(str(step_size))
            
            # التأكد من أن الكمية من مضاعفات step_size
            quantity_decimal = (quantity_decimal // step_decimal) * step_decimal
            
            # تنسيق النتيجة
            if decimals > 0:
                formatted = f"{float(quantity_decimal):.{decimals}f}"
            else:
                formatted = f"{int(quantity_decimal)}"
            
            logger.info(f"الكمية المنسقة: {formatted}")
            return formatted
                
        except Exception as e:
            logger.error(f"خطأ في تنسيق الكمية: {e}")
            # في حالة الخطأ، نعيد الكمية بتنسيق آمن
            return f"{quantity:.6f}".rstrip('0').rstrip('.')
    
    def place_spot_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET', 
                        price: Optional[float] = None) -> Optional[Dict]:
        """
        وضع أمر تداول فوري (Spot)
        
        Args:
            symbol: رمز العملة (مثل: BTCUSDT)
            side: نوع الأمر (BUY أو SELL)
            quantity: الكمية
            order_type: نوع الأمر (MARKET أو LIMIT)
            price: السعر (مطلوب لأوامر LIMIT)
            
        Returns:
            معلومات الأمر أو None في حالة الخطأ
        """
        try:
            logger.info(f"محاولة وضع أمر {side} {quantity} {symbol} على MEXC")
            
            # الحصول على معلومات الرمز
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                logger.error(f"فشل في الحصول على معلومات {symbol}")
                return None
            
            logger.info(f"معلومات الرمز: {symbol_info}")
            
            # التحقق من أن التداول الفوري مسموح
            if not symbol_info['is_spot_trading_allowed']:
                logger.error(f"التداول الفوري غير مسموح لـ {symbol}")
                return None
            
            # تنسيق الكمية بناءً على متطلبات الرمز
            formatted_quantity = self._format_quantity(quantity, symbol_info)
            logger.info(f"الكمية المنسقة: {formatted_quantity}")
            
            # التحقق من أن الكمية المنسقة ليست صفر
            if float(formatted_quantity) <= 0:
                logger.error(f"الكمية المنسقة صفر أو سالبة: {formatted_quantity}")
                return None
            
            # بناء معاملات الأمر حسب نوع الأمر
            import uuid
            client_order_id = f"bot-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
            
            # للأوامر MARKET: فقط الحقول الأساسية
            if order_type.upper() == 'MARKET':
                params = {
                    'symbol': symbol,
                    'side': side.upper(),
                    'type': order_type.upper(),
                    'quantity': formatted_quantity,
                    'newClientOrderId': client_order_id
                }
            else:
                # للأوامر LIMIT: إضافة السعر
                params = {
                    'symbol': symbol,
                    'side': side.upper(),
                    'type': order_type.upper(),
                    'quantity': formatted_quantity,
                    'price': f"{price:.8f}".rstrip('0').rstrip('.'),
                    'newClientOrderId': client_order_id
                }
            
            logger.info(f"🆔 Client Order ID: {client_order_id}")
            logger.info(f"📋 نوع الأمر: {order_type.upper()}")
            logger.info(f"📋 الحقول المرسلة: {list(params.keys())}")
            
            logger.info(f"معاملات الأمر: {params}")
            
            # إرسال الأمر
            logger.info(f"📤 إرسال الأمر إلى MEXC API...")
            logger.info(f"🔗 الرابط: {self.base_url}/api/v3/order")
            logger.info(f"📋 المعاملات النهائية: {params}")
            
            result = self._make_request('POST', '/api/v3/order', params, signed=True)
            
            logger.info(f"📥 استجابة MEXC API: {result}")
            
            if result:
                logger.info(f"✅ تم وضع أمر {side} لـ {symbol} بنجاح: {result}")
                return {
                    'orderId': result.get('orderId'),
                    'symbol': result.get('symbol'),
                    'side': result.get('side'),
                    'type': result.get('type'),
                    'origQty': result.get('origQty'),
                    'price': result.get('price'),
                    'status': result.get('status'),
                    'transactTime': result.get('transactTime')
                }
            
            logger.error(f"❌ فشل في وضع الأمر - لم يتم إرجاع نتيجة من MEXC")
            logger.error(f"🔍 السبب: _make_request عاد None")
            return None
            
        except Exception as e:
            logger.error(f"خطأ في وضع أمر على MEXC: {e}")
            import traceback
            logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
            return None
    
    def get_order_status(self, symbol: str, order_id: str) -> Optional[Dict]:
        """
        الحصول على حالة الأمر
        
        Args:
            symbol: رمز العملة
            order_id: معرف الأمر
            
        Returns:
            معلومات الأمر أو None في حالة الخطأ
        """
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            result = self._make_request('GET', '/api/v3/order', params, signed=True)
            
            if result:
                return {
                    'order_id': result.get('orderId'),
                    'symbol': result.get('symbol'),
                    'side': result.get('side'),
                    'type': result.get('type'),
                    'quantity': result.get('origQty'),
                    'executed_qty': result.get('executedQty'),
                    'price': result.get('price'),
                    'status': result.get('status'),
                    'time': result.get('time')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة الأمر: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        إلغاء أمر
        
        Args:
            symbol: رمز العملة
            order_id: معرف الأمر
            
        Returns:
            True إذا تم الإلغاء بنجاح، False خلاف ذلك
        """
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            result = self._make_request('DELETE', '/api/v3/order', params, signed=True)
            
            if result:
                logger.info(f"تم إلغاء الأمر {order_id} لـ {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إلغاء الأمر: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> Optional[list]:
        """
        الحصول على الأوامر المفتوحة
        
        Args:
            symbol: رمز العملة (اختياري - إذا لم يتم تحديده، يتم جلب جميع الأوامر)
            
        Returns:
            قائمة الأوامر المفتوحة أو None في حالة الخطأ
        """
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            result = self._make_request('GET', '/api/v3/openOrders', params, signed=True)
            
            if result:
                orders = []
                for order in result:
                    orders.append({
                        'order_id': order.get('orderId'),
                        'symbol': order.get('symbol'),
                        'side': order.get('side'),
                        'type': order.get('type'),
                        'quantity': order.get('origQty'),
                        'executed_qty': order.get('executedQty'),
                        'price': order.get('price'),
                        'status': order.get('status'),
                        'time': order.get('time')
                    })
                return orders
            
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الأوامر المفتوحة: {e}")
            return None
    
    def get_trade_history(self, symbol: str, limit: int = 100) -> Optional[list]:
        """
        الحصول على سجل التداولات
        
        Args:
            symbol: رمز العملة
            limit: عدد التداولات (الحد الأقصى 1000)
            
        Returns:
            قائمة التداولات أو None في حالة الخطأ
        """
        try:
            params = {
                'symbol': symbol,
                'limit': min(limit, 1000)
            }
            
            result = self._make_request('GET', '/api/v3/myTrades', params, signed=True)
            
            if result:
                trades = []
                for trade in result:
                    trades.append({
                        'id': trade.get('id'),
                        'order_id': trade.get('orderId'),
                        'symbol': trade.get('symbol'),
                        'side': 'BUY' if trade.get('isBuyer') else 'SELL',
                        'price': float(trade.get('price', 0)),
                        'quantity': float(trade.get('qty', 0)),
                        'commission': float(trade.get('commission', 0)),
                        'commission_asset': trade.get('commissionAsset'),
                        'time': trade.get('time')
                    })
                return trades
            
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على سجل التداولات: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        اختبار الاتصال بـ MEXC API
        
        Returns:
            True إذا كان الاتصال ناجحاً، False خلاف ذلك
        """
        try:
            # اختبار الاتصال العام
            result = self._make_request('GET', '/api/v3/ping')
            if result is not None:
                logger.info("✅ الاتصال بـ MEXC API ناجح")
                
                # اختبار الاتصال المصادق عليه
                account = self.get_account_balance()
                if account:
                    logger.info("✅ المصادقة على MEXC API ناجحة")
                    return True
                else:
                    logger.warning("⚠️ فشلت المصادقة على MEXC API")
                    return False
            
            logger.error("❌ فشل الاتصال بـ MEXC API")
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار الاتصال بـ MEXC: {e}")
            return False


# دالة مساعدة لإنشاء بوت MEXC
def create_mexc_bot(api_key: str, api_secret: str, testnet: bool = False) -> MEXCTradingBot:
    """
    إنشاء بوت MEXC
    
    Args:
        api_key: مفتاح API
        api_secret: السر الخاص
        testnet: استخدام الشبكة التجريبية (غير مدعوم في MEXC)
        
    Returns:
        كائن MEXCTradingBot
    """
    return MEXCTradingBot(api_key, api_secret, testnet)


if __name__ == "__main__":
    # مثال على الاستخدام
    print("=" * 60)
    print("🧪 اختبار MEXC Trading Bot")
    print("=" * 60)
    print("\n⚠️ تحذير: MEXC تدعم التداول الفوري (Spot) فقط عبر API")
    print("⚠️ لا يوجد دعم لتداول الفيوتشر في MEXC API\n")
    
    # يجب تعيين API Key و Secret من متغيرات البيئة أو ملف الإعدادات
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('MEXC_API_KEY', '')
    api_secret = os.getenv('MEXC_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ يرجى تعيين MEXC_API_KEY و MEXC_API_SECRET في ملف .env")
        exit(1)
    
    # إنشاء البوت
    bot = create_mexc_bot(api_key, api_secret)
    
    # اختبار الاتصال
    print("\n🔌 اختبار الاتصال...")
    if bot.test_connection():
        print("✅ الاتصال ناجح!")
        
        # عرض الرصيد
        print("\n💰 الرصيد:")
        balance = bot.get_account_balance()
        if balance:
            for asset, info in balance['balances'].items():
                if info['total'] > 0:
                    print(f"   {asset}: {info['total']:.8f} (متاح: {info['free']:.8f})")
        
        # اختبار الحصول على السعر
        print("\n📊 اختبار الحصول على السعر:")
        price = bot.get_ticker_price('BTCUSDT')
        if price:
            print(f"   سعر BTC/USDT: ${price:,.2f}")
    else:
        print("❌ فشل الاتصال!")
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار")
    print("=" * 60)

