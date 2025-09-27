#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the fixes for Railway deployment issues
"""

import os
import sys
import threading
import time

def test_port_configuration():
    """Test that ports are properly configured to avoid conflicts"""
    print("Testing port configuration...")
    
    # Test that PORT and WEBHOOK_PORT are properly set
    port = int(os.environ.get('PORT', 8080))
    webhook_port = int(os.environ.get('WEBHOOK_PORT', 5000))
    
    print(f"Main app port: {port}")
    print(f"Webhook port: {webhook_port}")
    
    if port == webhook_port:
        print("⚠️  Warning: Both ports are the same, which may cause conflicts")
        print("   Recommendation: Set WEBHOOK_PORT to a different value")
    else:
        print("✅ Ports are properly configured to avoid conflicts")
    
    return port, webhook_port

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'PORT',
        'WEBHOOK_PORT',
        'TELEGRAM_TOKEN',
        'ADMIN_USER_ID',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("   Please set these in your Railway dashboard")
    else:
        print("\n✅ All required environment variables are set")
    
    return len(missing_vars) == 0

def test_asyncio_fix():
    """Test that the asyncio fix is properly implemented"""
    print("\nTesting asyncio fix...")
    
    # Check if the fix is implemented in app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'asyncio.run(application.run_polling(' in content:
            print("✅ asyncio.run fix is implemented in app.py")
            return True
        else:
            print("❌ asyncio.run fix is NOT implemented in app.py")
            print("   The fix should use asyncio.run() instead of application.run_polling() directly")
            return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Railway deployment fixes...\n")
    
    port, webhook_port = test_port_configuration()
    env_ok = test_environment_variables()
    asyncio_ok = test_asyncio_fix()
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if port != webhook_port and env_ok and asyncio_ok:
        print("🎉 All fixes are properly implemented!")
        print("✅ The application should now work correctly on Railway")
    else:
        print("⚠️  Some issues need to be addressed:")
        if port == webhook_port:
            print("   - Port conflict: Set WEBHOOK_PORT to a different value than PORT")
        if not env_ok:
            print("   - Missing environment variables: Set them in Railway dashboard")
        if not asyncio_ok:
            print("   - Asyncio fix not implemented: Update app.py to use asyncio.run()")
    
    print("\n🔧 Railway Deployment Tips:")
    print("   1. In Railway dashboard, set these environment variables:")
    print("      - PORT=8080")
    print("      - WEBHOOK_PORT=5000")
    print("      - TELEGRAM_TOKEN=your_telegram_bot_token")
    print("      - ADMIN_USER_ID=your_telegram_user_id")
    print("      - BYBIT_API_KEY=your_bybit_api_key")
    print("      - BYBIT_API_SECRET=your_bybit_api_secret")

if __name__ == "__main__":
    main()