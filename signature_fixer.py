#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لطريقة التوقيع في Bybit API
"""

import hmac
import hashlib
import time
import json
import logging
from typing import Dict, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class BybitSignatureFixer:
    """إصلاح طريقة التوقيع لـ Bybit API"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bybit.com"
    
    def _generate_signature_v5(self, timestamp: str, recv_window: str, params_str: str) -> str:
        """توليد التوقيع المحسن لـ Bybit V5"""
        try:
            # بناء سلسلة التوقيع بالترتيب الصحيح
            sign_str = timestamp + self.api_key + recv_window + params_str
            
            logger.info(f"Signature Debug - timestamp: {timestamp}")
            logger.info(f"Signature Debug - api_key: {self.api_key}")
            logger.info(f"Signature Debug - recv_window: {recv_window}")
            logger.info(f"Signature Debug - params_str: {params_str}")
            logger.info(f"Signature Debug - sign_str: {sign_str}")
            
            # توليد التوقيع باستخدام HMAC-SHA256
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                sign_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            logger.info(f"Signature Debug - signature: {signature}")
            return signature
            
        except Exception as e:
            logger.error(f"خطأ في توليد التوقيع: {e}")
            raise
    
    def _prepare_params_for_signature(self, method: str, params: Dict) -> str:
        """تحضير المعاملات للتوقيع"""
        try:
            if method == 'GET':
                # للطلبات GET، استخدام query string مرتب
                if not params:
                    return ""
                
                # ترتيب المعاملات أبجدياً
                sorted_params = sorted(params.items())
                params_str = urlencode(sorted_params)
                logger.info(f"GET params_str: {params_str}")
                return params_str
                
            else:
                # للطلبات POST، استخدام JSON مرتب
                if not params:
                    return ""
                
                # ترتيب المعاملات أبجدياً
                sorted_params = dict(sorted(params.items()))
                
                # تحويل إلى JSON مع تنسيق محدد
                params_str = json.dumps(sorted_params, separators=(',', ':'), ensure_ascii=False)
                logger.info(f"POST params_str: {params_str}")
                return params_str
                
        except Exception as e:
            logger.error(f"خطأ في تحضير المعاملات: {e}")
            return ""
    
    def _make_request_fixed(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """إرسال طلب محسن إلى Bybit API"""
        if params is None:
            params = {}
        
        try:
            # إعداد الطلب
            timestamp = str(int(time.time() * 1000))
            recv_window = "5000"
            
            # تحضير المعاملات للتوقيع
            params_str = self._prepare_params_for_signature(method, params)
            
            # توليد التوقيع
            signature = self._generate_signature_v5(timestamp, recv_window, params_str)
            
            # إعداد Headers
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': recv_window,
                'Content-Type': 'application/json'
            }
            
            # إعداد URL
            url = f"{self.base_url}{endpoint}"
            
            # إضافة query string للطلبات GET
            if method == 'GET' and params_str:
                url += f"?{params_str}"
            
            logger.info(f"Request Debug - method: {method}")
            logger.info(f"Request Debug - url: {url}")
            logger.info(f"Request Debug - headers: {headers}")
            logger.info(f"Request Debug - params: {params}")
            
            # إرسال الطلب
            import requests
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                logger.error(f"Method not supported: {method}")
                return None
            
            logger.info(f"Response Debug - status: {response.status_code}")
            logger.info(f"Response Debug - text: {response.text}")
            
            # معالجة الاستجابة
            if response.status_code == 200:
                result = response.json()
                
                if result.get('retCode') == 0:
                    logger.info("Request successful")
                    return result.get('result')
                else:
                    logger.error(f"API Error - retCode: {result.get('retCode')}, retMsg: {result.get('retMsg')}")
                    return {
                        'error': True,
                        'retCode': result.get('retCode'),
                        'retMsg': result.get('retMsg'),
                        'raw_response': result
                    }
            else:
                logger.error(f"HTTP Error: {response.status_code} - {response.text}")
                return {
                    'error': True,
                    'http_status': response.status_code,
                    'http_message': response.text
                }
                
        except Exception as e:
            logger.error(f"Request exception: {e}")
            return {
                'error': True,
                'exception': str(e),
                'error_type': 'REQUEST_EXCEPTION'
            }
    
    def test_signature_with_different_params(self):
        """اختبار التوقيع مع معاملات مختلفة"""
        
        print("اختبار التوقيع مع معاملات مختلفة")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'طلب بسيط بدون معاملات',
                'method': 'GET',
                'endpoint': '/v5/account/wallet-balance',
                'params': {'accountType': 'UNIFIED'}
            },
            {
                'name': 'طلب مع معاملات متعددة',
                'method': 'POST',
                'endpoint': '/v5/order/create',
                'params': {
                    'category': 'linear',
                    'symbol': 'BTCUSDT',
                    'side': 'Buy',
                    'orderType': 'Market',
                    'qty': '0.001'
                }
            },
            {
                'name': 'طلب تعديل الرافعة المالية',
                'method': 'POST',
                'endpoint': '/v5/position/set-leverage',
                'params': {
                    'category': 'linear',
                    'symbol': 'BTCUSDT',
                    'buyLeverage': '1',
                    'sellLeverage': '1'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nاختبار {i}: {test_case['name']}")
            print("-" * 30)
            
            try:
                # تحضير المعاملات للتوقيع
                params_str = self._prepare_params_for_signature(
                    test_case['method'], 
                    test_case['params']
                )
                
                print(f"المعاملات: {test_case['params']}")
                print(f"سلسلة التوقيع: {params_str}")
                
                # توليد التوقيع
                timestamp = str(int(time.time() * 1000))
                recv_window = "5000"
                signature = self._generate_signature_v5(timestamp, recv_window, params_str)
                
                print(f"التوقيع: {signature}")
                print("تم توليد التوقيع بنجاح!")
                
            except Exception as e:
                print(f"خطأ في اختبار التوقيع: {e}")
    
    def test_api_connection(self):
        """اختبار الاتصال بـ API"""
        
        print("\nاختبار الاتصال بـ API")
        print("=" * 30)
        
        try:
            # اختبار جلب الرصيد
            result = self._make_request_fixed(
                'GET', 
                '/v5/account/wallet-balance', 
                {'accountType': 'UNIFIED'}
            )
            
            if result and not result.get('error'):
                print("نجح الاتصال بـ API!")
                return True
            else:
                print("فشل الاتصال بـ API!")
                if result:
                    print(f"تفاصيل الخطأ: {result}")
                return False
                
        except Exception as e:
            print(f"خطأ في اختبار الاتصال: {e}")
            return False

def test_signature_calculation():
    """اختبار حساب التوقيع"""
    
    print("اختبار حساب التوقيع")
    print("=" * 30)
    
    # مفاتيح وهمية للاختبار
    api_key = "test_api_key_123"
    api_secret = "test_secret_key_456"
    
    fixer = BybitSignatureFixer(api_key, api_secret)
    
    # اختبار التوقيع مع معاملات مختلفة
    fixer.test_signature_with_different_params()
    
    # اختبار الاتصال (سيفشل لأن المفاتيح وهمية)
    fixer.test_api_connection()

if __name__ == "__main__":
    print("إصلاح طريقة التوقيع لـ Bybit API")
    print("=" * 50)
    
    # اختبار حساب التوقيع
    test_signature_calculation()
    
    print("\nملخص الإصلاحات:")
    print("1. تحسين طريقة تحضير المعاملات للتوقيع")
    print("2. ترتيب المعاملات أبجدياً")
    print("3. استخدام تنسيق JSON محدد للطلبات POST")
    print("4. تحسين معالجة الأخطاء")
    print("5. إضافة تسجيل مفصل للتشخيص")
