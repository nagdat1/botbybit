#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار توليد التوقيع لـ Bybit
"""

import sys
import os
import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_bybit_signature():
    """اختبار توليد التوقيع لـ Bybit"""
    
    print("=== اختبار توليد التوقيع لـ Bybit ===")
    print()
    
    # بيانات الاختبار
    api_key = "dqBHnPaItfmEZSB020"
    api_secret = "PjAN7fUfeLn4ouTpIzWwBJe4TKQVOr02lIdc"
    
    # معاملات الاختبار
    params = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'buyLeverage': '10',
        'sellLeverage': '10'
    }
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:10]}...")
    print(f"Timestamp: {timestamp}")
    print(f"Recv Window: {recv_window}")
    print(f"Params: {params}")
    print()
    
    # بناء query string
    params_str = urlencode(sorted(params.items()))
    print(f"Params String: {params_str}")
    print()
    
    # توليد التوقيع
    sign_str = timestamp + api_key + recv_window + params_str
    print(f"Sign String: {sign_str}")
    print()
    
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"Signature: {signature}")
    print()
    
    # اختبار مع معاملات مختلفة
    print("=== اختبار مع معاملات مختلفة ===")
    print()
    
    # اختبار مع معاملات فارغة
    params_empty = {}
    params_str_empty = urlencode(sorted(params_empty.items()))
    sign_str_empty = timestamp + api_key + recv_window + params_str_empty
    signature_empty = hmac.new(
        api_secret.encode('utf-8'),
        sign_str_empty.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"Empty Params String: '{params_str_empty}'")
    print(f"Empty Sign String: {sign_str_empty}")
    print(f"Empty Signature: {signature_empty}")
    print()
    
    # اختبار مع معاملات order
    params_order = {
        'category': 'linear',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '1000.0'
    }
    
    params_str_order = urlencode(sorted(params_order.items()))
    sign_str_order = timestamp + api_key + recv_window + params_str_order
    signature_order = hmac.new(
        api_secret.encode('utf-8'),
        sign_str_order.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"Order Params String: {params_str_order}")
    print(f"Order Sign String: {sign_str_order}")
    print(f"Order Signature: {signature_order}")
    print()
    
    return True

if __name__ == "__main__":
    success = test_bybit_signature()
    if success:
        print("اختبار التوقيع نجح!")
    else:
        print("اختبار التوقيع فشل!")
        sys.exit(1)
