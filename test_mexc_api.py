#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لـ MEXC API
استخدم هذا الملف لاختبار API Keys الخاصة بك
"""

import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

class MEXCTester:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.mexc.com"
    
    def _generate_signature(self, params: dict) -> str:
        """إنشاء التوقيع"""
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        print(f"🔐 Query String: {query_string}")
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"🔐 Signature: {signature}")
        
        return signature
    
    def test_account_info(self):
        """اختبار الحصول على معلومات الحساب"""
        print("\n" + "="*60)
        print("🧪 اختبار MEXC API - معلومات الحساب")
        print("="*60)
        
        try:
            endpoint = "/api/v3/account"
            url = f"{self.base_url}{endpoint}"
            
            params = {
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            signature = self._generate_signature(params)
            params['signature'] = signature
            
            headers = {
                "X-MEXC-APIKEY": self.api_key
            }
            
            print(f"\n📤 URL: {url}")
            print(f"📋 Parameters: {params}")
            print(f"🔑 API Key: {self.api_key[:10]}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"\n📥 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body:\n{response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"\n✅ نجح! JSON Response:")
                    print(result)
                    
                    if 'balances' in result:
                        print(f"\n💰 عدد العملات: {len(result['balances'])}")
                        # عرض العملات التي لديها رصيد
                        non_zero = [b for b in result['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
                        if non_zero:
                            print("\n💵 العملات بأرصدة:")
                            for b in non_zero[:5]:  # أول 5 فقط
                                print(f"  • {b['asset']}: Free={b['free']}, Locked={b['locked']}")
                    
                    return True
                except Exception as e:
                    print(f"\n❌ خطأ في تحليل JSON: {e}")
                    return False
            else:
                print(f"\n❌ فشل - Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            import traceback
            print(traceback.format_exc())
            return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🧪 برنامج اختبار MEXC API                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("📝 الرجاء إدخال بيانات API الخاصة بك:\n")
    
    api_key = input("🔑 API Key: ").strip()
    api_secret = input("🔐 API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("\n❌ يجب إدخال API Key و Secret!")
        return
    
    print(f"\n✅ تم استلام:")
    print(f"   • API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   • Secret: {api_secret[:10]}...{api_secret[-4:]}")
    
    tester = MEXCTester(api_key, api_secret)
    success = tester.test_account_info()
    
    if success:
        print("\n" + "="*60)
        print("✅ الاختبار نجح! API Keys صحيحة")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ الاختبار فشل! تحقق من:")
        print("   1. API Key و Secret صحيحة")
        print("   2. الصلاحيات (Read-Write + Spot Trading)")
        print("   3. IP Whitelist معطلة أو IP مضاف")
        print("="*60)

if __name__ == "__main__":
    main()

