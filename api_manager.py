#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة مفاتيح API مع دعم متعدد المستخدمين
يدعم ربط مفاتيح Bybit لكل مستخدم بشكل منفصل
"""

import logging
import hashlib
import hmac
import requests
import time
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class BybitAPI:
    """فئة للتعامل مع Bybit API مع دعم متعدد المستخدمين"""
    
    def __init__(self, api_key: str, api_secret: str, user_id: int = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        self.base_url = "https://api.bybit.com"
        self.lock = threading.Lock()
        
        # إحصائيات الاستخدام
        self.request_count = 0
        self.last_request_time = None
        self.error_count = 0
    
    def _generate_signature(self, params: dict, timestamp: str) -> str:
        """إنشاء التوقيع للطلبات"""
        try:
            param_str = timestamp + self.api_key + "5000" + urlencode(sorted(params.items()))
            return hmac.new(
                self.api_secret.encode('utf-8'),
                param_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            logger.error(f"خطأ في إنشاء التوقيع للمستخدم {self.user_id}: {e}")
            return ""
    
    def _make_request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        """إرسال طلب إلى API مع حماية من التكرار"""
        try:
            with self.lock:
                # حماية من الطلبات المتكررة
                current_time = time.time()
                if self.last_request_time and (current_time - self.last_request_time) < 0.1:
                    time.sleep(0.1)
                
                url = f"{self.base_url}{endpoint}"
                timestamp = str(int(current_time * 1000))
                
                if params is None:
                    params = {}
                
                signature = self._generate_signature(params, timestamp)
                
                headers = {
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-SIGN-TYPE": "2",
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-RECV-WINDOW": "5000",
                    "Content-Type": "application/json"
                }
                
                self.request_count += 1
                self.last_request_time = current_time
                
                if method.upper() == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=params, headers=headers, timeout=10)
                
                response.raise_for_status()
                result = response.json()
                
                # تسجيل الطلب الناجح
                logger.debug(f"طلب API ناجح للمستخدم {self.user_id}: {endpoint}")
                return result
                
        except requests.RequestException as e:
            self.error_count += 1
            logger.error(f"خطأ في طلب API للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
        except Exception as e:
            self.error_count += 1
            logger.error(f"خطأ غير متوقع في API للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بـ API"""
        try:
            response = self._make_request("GET", "/v5/account/wallet-balance", {"accountType": "UNIFIED"})
            return response.get("retCode") == 0
        except Exception as e:
            logger.error(f"خطأ في اختبار الاتصال للمستخدم {self.user_id}: {e}")
            return False
    
    def get_all_symbols(self, category: str = "spot") -> List[dict]:
        """الحصول على جميع الرموز المتاحة"""
        try:
            endpoint = "/v5/market/instruments-info"
            # تحويل futures إلى linear للتوافق مع Bybit API
            api_category = "linear" if category == "futures" else category
            params = {"category": api_category}
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                result = response.get("result", {})
                symbols = result.get("list", [])
                return symbols
            
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الرموز للمستخدم {self.user_id}: {e}")
            return []
    
    def get_ticker_price(self, symbol: str, category: str = "spot") -> Optional[float]:
        """الحصول على سعر الرمز الحالي"""
        try:
            endpoint = "/v5/market/tickers"
            # تحويل futures إلى linear للتوافق مع Bybit API
            api_category = "linear" if category == "futures" else "spot"
            params = {"category": api_category, "symbol": symbol}
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                result = response.get("result", {})
                ticker_list = result.get("list", [])
                if ticker_list:
                    return float(ticker_list[0].get("lastPrice", 0))
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر للمستخدم {self.user_id}: {e}")
            return None
    
    def check_symbol_exists(self, symbol: str, category: str = "spot") -> bool:
        """التحقق من وجود الرمز في المنصة"""
        try:
            price = self.get_ticker_price(symbol, category)
            return price is not None and price > 0
        except Exception as e:
            logger.error(f"خطأ في التحقق من الرمز للمستخدم {self.user_id}: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, 
                   price: Optional[str] = None, category: str = "spot") -> dict:
        """وضع أمر تداول"""
        try:
            endpoint = "/v5/order/create"
            
            params = {
                "category": category,
                "symbol": symbol,
                "side": side.capitalize(),
                "orderType": order_type,
                "qty": qty
            }
            
            if price and order_type.lower() == "limit":
                params["price"] = price
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في وضع الأمر للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_account_balance(self, account_type: str = "UNIFIED") -> dict:
        """الحصول على رصيد الحساب"""
        try:
            endpoint = "/v5/account/wallet-balance"
            params = {"accountType": account_type}
            
            response = self._make_request("GET", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الرصيد للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_open_positions(self, category: str = "linear") -> dict:
        """الحصول على الصفقات المفتوحة"""
        try:
            endpoint = "/v5/position/list"
            params = {"category": category}
            
            response = self._make_request("GET", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصفقات المفتوحة للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def close_position(self, symbol: str, side: str, category: str = "linear") -> dict:
        """إغلاق صفقة"""
        try:
            endpoint = "/v5/order/create"
            
            params = {
                "category": category,
                "symbol": symbol,
                "side": "Sell" if side.lower() == "buy" else "Buy",
                "orderType": "Market",
                "qty": "0",  # إغلاق كامل
                "reduceOnly": True
            }
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة للمستخدم {self.user_id}: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_api_stats(self) -> Dict:
        """الحصول على إحصائيات API"""
        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'last_request_time': self.last_request_time,
            'success_rate': ((self.request_count - self.error_count) / max(self.request_count, 1)) * 100
        }

class APIManager:
    """مدير مفاتيح API مع دعم متعدد المستخدمين"""
    
    def __init__(self):
        self.user_apis: Dict[int, BybitAPI] = {}
        self.lock = threading.Lock()
    
    def add_user_api(self, user_id: int, api_key: str, api_secret: str) -> bool:
        """إضافة مفاتيح API للمستخدم"""
        try:
            with self.lock:
                # إنشاء مثيل API جديد للمستخدم
                api_instance = BybitAPI(api_key, api_secret, user_id)
                
                # اختبار الاتصال
                if api_instance.test_connection():
                    self.user_apis[user_id] = api_instance
                    logger.info(f"تم ربط مفاتيح API للمستخدم: {user_id}")
                    return True
                else:
                    logger.error(f"فشل في اختبار مفاتيح API للمستخدم: {user_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"خطأ في إضافة مفاتيح API للمستخدم {user_id}: {e}")
            return False
    
    def remove_user_api(self, user_id: int) -> bool:
        """إزالة مفاتيح API للمستخدم"""
        try:
            with self.lock:
                if user_id in self.user_apis:
                    del self.user_apis[user_id]
                    logger.info(f"تم إزالة مفاتيح API للمستخدم: {user_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"خطأ في إزالة مفاتيح API للمستخدم {user_id}: {e}")
            return False
    
    def get_user_api(self, user_id: int) -> Optional[BybitAPI]:
        """الحصول على مثيل API للمستخدم"""
        return self.user_apis.get(user_id)
    
    def has_user_api(self, user_id: int) -> bool:
        """التحقق من وجود مفاتيح API للمستخدم"""
        return user_id in self.user_apis
    
    def test_user_api(self, user_id: int) -> bool:
        """اختبار مفاتيح API للمستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.test_connection()
        return False
    
    def get_user_symbols(self, user_id: int, category: str = "spot") -> List[dict]:
        """الحصول على الرموز المتاحة للمستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.get_all_symbols(category)
        return []
    
    def get_user_price(self, user_id: int, symbol: str, category: str = "spot") -> Optional[float]:
        """الحصول على سعر الرمز للمستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.get_ticker_price(symbol, category)
        return None
    
    def place_user_order(self, user_id: int, symbol: str, side: str, order_type: str, 
                        qty: str, price: Optional[str] = None, category: str = "spot") -> dict:
        """وضع أمر تداول للمستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.place_order(symbol, side, order_type, qty, price, category)
        return {"retCode": -1, "retMsg": "مفاتيح API غير متاحة"}
    
    def get_user_balance(self, user_id: int, account_type: str = "UNIFIED") -> dict:
        """الحصول على رصيد المستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.get_account_balance(account_type)
        return {"retCode": -1, "retMsg": "مفاتيح API غير متاحة"}
    
    def get_user_positions(self, user_id: int, category: str = "linear") -> dict:
        """الحصول على صفقات المستخدم المفتوحة"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.get_open_positions(category)
        return {"retCode": -1, "retMsg": "مفاتيح API غير متاحة"}
    
    def close_user_position(self, user_id: int, symbol: str, side: str, category: str = "linear") -> dict:
        """إغلاق صفقة المستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.close_position(symbol, side, category)
        return {"retCode": -1, "retMsg": "مفاتيح API غير متاحة"}
    
    def get_all_user_apis(self) -> Dict[int, BybitAPI]:
        """الحصول على جميع مثيلات API"""
        return self.user_apis.copy()
    
    def get_user_count(self) -> int:
        """الحصول على عدد المستخدمين المرتبطين"""
        return len(self.user_apis)
    
    def cleanup_inactive_apis(self, max_age_hours: int = 24):
        """تنظيف مفاتيح API غير النشطة"""
        try:
            current_time = time.time()
            users_to_remove = []
            
            for user_id, api_instance in self.user_apis.items():
                if api_instance.last_request_time:
                    age_hours = (current_time - api_instance.last_request_time) / 3600
                    if age_hours > max_age_hours:
                        users_to_remove.append(user_id)
            
            for user_id in users_to_remove:
                self.remove_user_api(user_id)
                logger.info(f"تم تنظيف مفاتيح API غير النشطة للمستخدم: {user_id}")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف مفاتيح API غير النشطة: {e}")
    
    def get_api_stats(self, user_id: int) -> Optional[Dict]:
        """الحصول على إحصائيات API للمستخدم"""
        api_instance = self.get_user_api(user_id)
        if api_instance:
            return api_instance.get_api_stats()
        return None
    
    def validate_api_keys(self, api_key: str, api_secret: str) -> bool:
        """التحقق من صحة مفاتيح API"""
        try:
            # إنشاء مثيل مؤقت للاختبار
            temp_api = BybitAPI(api_key, api_secret)
            return temp_api.test_connection()
        except Exception as e:
            logger.error(f"خطأ في التحقق من مفاتيح API: {e}")
            return False

# إنشاء مثيل عام لمدير API
api_manager = APIManager()
