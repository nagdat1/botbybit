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
        # لا نضع API key في الـ headers الافتراضية
        # سيتم إضافته فقط للطلبات الموقعة
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        logger.info(f"تم تهيئة MEXC Trading Bot - Base URL: {self.base_url}")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        توليد التوقيع للطلبات - الطريقة الصحيحة لـ MEXC
        
        Args:
            params: معاملات الطلب
            
        Returns:
            التوقيع
        """
        # ترتيب المعاملات أبجدياً
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        # إنشاء التوقيع باستخدام HMAC-SHA256
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.debug(f"MEXC Signature - Query: {query_string}")
        logger.debug(f"MEXC Signature - Generated: {signature}")
        
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Optional[Dict]:
        """
        إرسال طلب إلى MEXC API - محسن للتوقيع الصحيح
        
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
            # إعداد headers حسب نوع الطلب
            headers = {}
            
            if signed:
                # إضافة API key للطلبات الموقعة
                headers['X-MEXC-APIKEY'] = self.api_key
                
                # إضافة timestamp للتوقيع
                timestamp = int(time.time() * 1000)
                params['timestamp'] = timestamp
                
                # توليد التوقيع
                signature = self._generate_signature(params)
                params['signature'] = signature
                
                logger.info(f"MEXC Request - Method: {method}, Endpoint: {endpoint} (SIGNED)")
                logger.info(f"MEXC Request - Params: {params}")
            else:
                logger.info(f"MEXC Request - Method: {method}, Endpoint: {endpoint} (PUBLIC)")
            
            # إرسال الطلب حسب النوع
            if method == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=15)
            elif method == 'POST':
                # للطلبات الموقعة، نرسل البيانات في query string
                if signed:
                    response = self.session.post(url, params=params, headers=headers, timeout=15)
                else:
                    response = self.session.post(url, json=params, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=15)
            else:
                logger.error(f"نوع طلب غير مدعوم: {method}")
                return None
            
            # تسجيل الاستجابة
            logger.info(f"MEXC Response - Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MEXC Response - Success: {result}")
                return result
            else:
                # استخدام معالج الأخطاء المحسن
                self._handle_api_error(response, f"{method} {endpoint}")
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في الطلب إلى MEXC: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"تفاصيل الخطأ: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"خطأ عام في الطلب إلى MEXC: {e}")
            return None
    
    def _handle_api_error(self, response, operation: str) -> bool:
        """
        معالجة أخطاء API بشكل مفصل
        
        Args:
            response: استجابة HTTP
            operation: العملية التي فشلت
            
        Returns:
            True إذا كان الخطأ يمكن معالجته، False خلاف ذلك
        """
        try:
            if response.status_code == 200:
                return True
            
            # محاولة تحليل رسالة الخطأ
            try:
                error_data = response.json()
                error_code = error_data.get('code', 'UNKNOWN')
                error_msg = error_data.get('msg', 'خطأ غير معروف')
                
                logger.error(f"❌ خطأ MEXC API في {operation}:")
                logger.error(f"   كود الخطأ: {error_code}")
                logger.error(f"   الرسالة: {error_msg}")
                
                # معالجة أخطاء شائعة
                if error_code == -1021:  # Invalid timestamp
                    logger.error("   السبب: timestamp غير صحيح - تحقق من تزامن الوقت")
                elif error_code == -1022:  # Invalid signature
                    logger.error("   السبب: توقيع غير صحيح - تحقق من API Secret")
                elif error_code == -2010:  # Account has insufficient balance
                    logger.error("   السبب: رصيد غير كافي")
                elif error_code == -2011:  # Order would immediately match
                    logger.error("   السبب: الأمر سيتطابق فوراً")
                elif error_code == -2013:  # Order does not exist
                    logger.error("   السبب: الأمر غير موجود")
                elif error_code == -2014:  # API-key format invalid
                    logger.error("   السبب: تنسيق API Key غير صحيح")
                elif error_code == -2015:  # Invalid API-key, IP, or permissions for action
                    logger.error("   السبب: API Key غير صحيح أو صلاحيات غير كافية")
                
            except:
                logger.error(f"❌ خطأ MEXC API في {operation}: {response.status_code}")
                logger.error(f"   النص: {response.text[:200]}...")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة خطأ API: {e}")
            return False
    
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
        الحصول على سعر الرمز الحالي - محسن للتشخيص
        
        Args:
            symbol: رمز العملة (مثل: BTCUSDT)
            
        Returns:
            السعر الحالي أو None في حالة الخطأ
        """
        try:
            logger.info(f"🔍 جلب السعر من MEXC لـ {symbol}")
            # جلب السعر لا يحتاج توقيع - طلب عام
            result = self._make_request('GET', '/api/v3/ticker/price', {'symbol': symbol}, signed=False)
            
            if result and 'price' in result:
                price = float(result['price'])
                logger.info(f"✅ السعر من MEXC لـ {symbol}: {price}")
                return price
            else:
                logger.error(f"❌ فشل جلب السعر من MEXC لـ {symbol} - النتيجة: {result}")
                return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على سعر {symbol} من MEXC: {e}")
            import traceback
            traceback.print_exc()
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
                        
                        return {
                            'symbol': sym['symbol'],
                            'status': sym['status'],
                            'base_asset': sym['baseAsset'],
                            'quote_asset': sym['quoteAsset'],
                            'filters': filters,
                            'is_spot_trading_allowed': sym.get('isSpotTradingAllowed', False),
                            'permissions': sym.get('permissions', [])
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
            lot_size_filter = symbol_info['filters'].get('LOT_SIZE', {})
            step_size = float(lot_size_filter.get('stepSize', '1'))
            
            # حساب عدد الأرقام العشرية
            step_str = f"{step_size:.10f}".rstrip('0')
            if '.' in step_str:
                decimals = len(step_str.split('.')[1])
            else:
                decimals = 0
            
            # تقريب الكمية
            quantity_decimal = Decimal(str(quantity))
            step_decimal = Decimal(str(step_size))
            
            # التأكد من أن الكمية من مضاعفات step_size
            quantity_decimal = (quantity_decimal // step_decimal) * step_decimal
            
            # تنسيق النتيجة
            return f"{float(quantity_decimal):.{decimals}f}"
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق الكمية: {e}")
            return f"{quantity:.8f}".rstrip('0').rstrip('.')
    
    def place_spot_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET', 
                        price: Optional[float] = None) -> Optional[Dict]:
        """
        وضع أمر تداول فوري (Spot) - محسن للمعالجة الصحيحة
        
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
            logger.info(f"🔄 وضع أمر MEXC: {side} {quantity} {symbol} ({order_type})")
            
            # الحصول على معلومات الرمز أولاً
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                logger.error(f"❌ فشل في الحصول على معلومات {symbol}")
                return None
            
            # التحقق من أن التداول الفوري مسموح
            if not symbol_info['is_spot_trading_allowed']:
                logger.error(f"❌ التداول الفوري غير مسموح لـ {symbol}")
                return None
            
            # تنسيق الكمية حسب متطلبات الرمز
            formatted_quantity = self._format_quantity(quantity, symbol_info)
            logger.info(f"📊 الكمية المنسقة: {formatted_quantity}")
            
            # بناء معاملات الأمر
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': formatted_quantity
            }
            
            # إضافة السعر لأوامر LIMIT
            if order_type.upper() == 'LIMIT':
                if price is None:
                    logger.error("❌ السعر مطلوب لأوامر LIMIT")
                    return None
                params['price'] = f"{price:.8f}".rstrip('0').rstrip('.')
                params['timeInForce'] = 'GTC'  # Good Till Cancel
                logger.info(f"💰 السعر المحدد: {params['price']}")
            
            # إرسال الأمر مع التوقيع
            logger.info(f"📤 إرسال الأمر إلى MEXC: {params}")
            result = self._make_request('POST', '/api/v3/order', params, signed=True)
            
            if result:
                logger.info(f"✅ تم وضع أمر {side} لـ {symbol} بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                
                # إرجاع معلومات منسقة ومفيدة
                order_info = {
                    'order_id': result.get('orderId'),
                    'symbol': result.get('symbol'),
                    'side': result.get('side'),
                    'type': result.get('type'),
                    'quantity': result.get('origQty'),
                    'price': result.get('price'),
                    'status': result.get('status'),
                    'time': result.get('transactTime'),
                    'client_order_id': result.get('clientOrderId'),
                    'executed_qty': result.get('executedQty'),
                    'cummulative_quote_qty': result.get('cummulativeQuoteQty')
                }
                
                logger.info(f"🎯 معلومات الأمر النهائية: {order_info}")
                return order_info
            else:
                logger.error(f"❌ فشل وضع الأمر - لم يتم إرجاع نتيجة صحيحة")
                return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في وضع أمر على MEXC: {e}")
            import traceback
            traceback.print_exc()
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
        اختبار الاتصال بـ MEXC API - محسن للتشخيص
        
        Returns:
            True إذا كان الاتصال ناجحاً، False خلاف ذلك
        """
        try:
            logger.info("🔄 اختبار الاتصال بـ MEXC API...")
            
            # اختبار الاتصال العام
            result = self._make_request('GET', '/api/v3/ping')
            if result is not None:
                logger.info("✅ الاتصال العام بـ MEXC API ناجح")
                
                # اختبار الاتصال المصادق عليه
                logger.info("🔄 اختبار المصادقة...")
                account = self.get_account_balance()
                if account:
                    logger.info("✅ المصادقة على MEXC API ناجحة")
                    
                    # اختبار إضافي للتوقيع
                    logger.info("🔄 اختبار التوقيع...")
                    test_result = self._test_signature()
                    if test_result:
                        logger.info("✅ اختبار التوقيع ناجح")
                        return True
                    else:
                        logger.warning("⚠️ فشل اختبار التوقيع")
                        return False
                else:
                    logger.warning("⚠️ فشلت المصادقة على MEXC API")
                    return False
            
            logger.error("❌ فشل الاتصال العام بـ MEXC API")
            return False
            
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار الاتصال بـ MEXC: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_signature(self) -> bool:
        """
        اختبار التوقيع باستخدام طلب بسيط
        
        Returns:
            True إذا كان التوقيع صحيحاً
        """
        try:
            # استخدام طلب بسيط لاختبار التوقيع
            result = self._make_request('GET', '/api/v3/account', signed=True)
            return result is not None
        except Exception as e:
            logger.error(f"❌ خطأ في اختبار التوقيع: {e}")
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

