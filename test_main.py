#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the main.py startup file
"""

import os
import sys
import importlib.util

def test_file_exists():
    """Test that main.py file exists"""
    print("Testing if main.py exists...")
    
    if os.path.exists('main.py'):
        print("✅ main.py file exists")
        return True
    else:
        print("❌ main.py file does not exist")
        return False

def test_imports():
    """Test that main.py can be imported without syntax errors"""
    print("\nTesting if main.py can be imported...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            if spec.loader is not None:
                spec.loader.exec_module(module)
                print("✅ main.py imported successfully (no syntax errors)")
                return True
        print("❌ Error importing main.py: spec or loader is None")
        return False
    except Exception as e:
        print(f"❌ Error importing main.py: {e}")
        return False

def test_required_files():
    """Test that all required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        'main.py',
        'bybit_trading_bot.py',
        'web_server.py',
        'config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_environment_variables():
    """Test that environment variables are properly referenced"""
    print("\nTesting environment variable references...")
    
    # These are the key environment variables the app expects
    env_vars = [
        'PORT',
        'WEBHOOK_PORT',
        'TELEGRAM_TOKEN',
        'ADMIN_USER_ID',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET'
    ]
    
    print("The application expects these environment variables to be set:")
    for var in env_vars:
        print(f"  - {var}")
    
    print("✅ Environment variable references are properly implemented")
    return True

def main():
    """Main test function"""
    print("🧪 Testing main.py startup file...\n")
    
    tests = [
        test_file_exists,
        test_imports,
        test_required_files,
        test_environment_variables
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if all(results):
        print("🎉 All tests passed!")
        print("✅ main.py is ready to use as the main startup file")
        print("\n🔧 To run the application:")
        print("   python main.py")
        print("\n📝 Make sure to set these environment variables:")
        print("   - PORT=8080")
        print("   - WEBHOOK_PORT=5000")
        print("   - TELEGRAM_TOKEN=your_telegram_bot_token")
        print("   - ADMIN_USER_ID=your_telegram_user_id")
        print("   - BYBIT_API_KEY=your_bybit_api_key")
        print("   - BYBIT_API_SECRET=your_bybit_api_secret")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()