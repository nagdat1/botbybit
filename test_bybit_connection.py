#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للاتصال مع Bybit API
"""

import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

def test_bybit_connection(api_key: str, api_secret: str):
    """اختبار الاتصال مع Bybit"""
    
    print("=" * 60)
    print("🔍 اختبار الاتصال مع Bybit API")
    print("=" * 60)
    
    base_url = "https://api.bybit.com"
    endpoint = "/v5/account/wallet-balance"
    
    # بناء التوقيع
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # بناء params (بدون timestamp!)
    params = {
        'accountType': 'UNIFIED'
    }
    
    params_str = urlencode(sorted(params.items()))
    
    print(f"\n📋 تفاصيل الطلب:")
    print(f"  Timestamp: {timestamp}")
    print(f"  Recv Window: {recv_window}")
    print(f"  Params: {params_str}")
    print(f"  API Key (first 8): {api_key[:8]}...")
    
    # بناء signature string
    sign_str = timestamp + str(api_key) + recv_window + params_str
    print(f"\n🔐 Sign String: {sign_str[:50]}...")
    
    # إنشاء التوقيع
    secret_bytes = str(api_secret).encode('utf-8')
    sign_bytes = sign_str.encode('utf-8')
    signature = hmac.new(secret_bytes, sign_bytes, hashlib.sha256).hexdigest()
    
    print(f"🔑 Signature (first 16): {signature[:16]}...")
    
    # Headers
    headers = {
        'X-BAPI-API-KEY': str(api_key),
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'X-BAPI-SIGN-TYPE': '2',
        'Content-Type': 'application/json'
    }
    
    # إرسال الطلب
    url = f"{base_url}{endpoint}?{params_str}"
    print(f"\n📡 إرسال الطلب إلى: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n📥 الاستجابة:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ret_code = result.get('retCode')
            ret_msg = result.get('retMsg')
            
            print(f"  retCode: {ret_code}")
            print(f"  retMsg: {ret_msg}")
            
            if ret_code == 0:
                print(f"\n✅ الاتصال ناجح!")
                
                # عرض معلومات الرصيد
                wallet_data = result.get('result', {})
                accounts = wallet_data.get('list', [])
                
                if accounts:
                    account = accounts[0]
                    print(f"\n💰 معلومات الحساب:")
                    print(f"  Account Type: {account.get('accountType')}")
                    print(f"  Total Equity: {account.get('totalEquity')}")
                    print(f"  Total Available Balance: {account.get('totalAvailableBalance')}")
                    
                    coins = account.get('coin', [])
                    if coins:
                        print(f"\n💵 العملات:")
                        for coin in coins[:5]:
                            equity = float(coin.get('equity', 0))
                            if equity > 0:
                                print(f"    • {coin.get('coin')}: {equity}")
                
                return True
            else:
                print(f"\n❌ خطأ من Bybit:")
                print(f"  الكود: {ret_code}")
                print(f"  الرسالة: {ret_msg}")
                return False
        else:
            print(f"\n❌ خطأ HTTP: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ في الاتصال: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔐 أدخل مفاتيح API الخاصة بك:")
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if api_key and api_secret:
        test_bybit_connection(api_key, api_secret)
    else:
        print("❌ يجب إدخال كلا المفتاحين")

