#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار متغيرات البيئة في Railway
"""

import os
from datetime import datetime

def test_railway_environment():
    """اختبار متغيرات البيئة في Railway"""
    print("🔍 فحص متغيرات البيئة في Railway")
    print("=" * 50)
    
    # فحص متغيرات Railway
    railway_vars = [
        'RAILWAY_PUBLIC_DOMAIN',
        'RAILWAY_STATIC_URL', 
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID',
        'RAILWAY_ENVIRONMENT',
        'PORT'
    ]
    
    print("📋 متغيرات Railway:")
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: غير موجود")
    
    print("\n" + "=" * 50)
    
    # فحص متغيرات أخرى مفيدة
    other_vars = [
        'PYTHONUNBUFFERED',
        'TELEGRAM_TOKEN',
        'ADMIN_USER_ID',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET'
    ]
    
    print("📋 متغيرات أخرى:")
    for var in other_vars:
        value = os.getenv(var)
        if value:
            # إخفاء القيم الحساسة
            if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: غير موجود")
    
    print("\n" + "=" * 50)
    
    # تحديد رابط Webhook
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    port = os.getenv('PORT', '5000')
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        webhook_url = f"{railway_url}/webhook"
        print("🌐 رابط Webhook:")
        print(f"   {webhook_url}")
    else:
        webhook_url = f"http://localhost:{port}/webhook"
        print("🌐 رابط Webhook (محلي):")
        print(f"   {webhook_url}")
    
    print("\n" + "=" * 50)
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ انتهى الفحص")

if __name__ == "__main__":
    test_railway_environment()
