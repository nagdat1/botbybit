#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Railway deployment readiness
"""

import os
import sys

def check_railway_readiness():
    """Check if the project is ready for Railway deployment"""
    
    print("Checking Railway deployment readiness...")
    
    # Check required files
    required_files = [
        'app.py',
        'requirements.txt',
        'Dockerfile',
        'railway.yaml',
        'railway.toml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
    
    # Check environment variables
    env_vars = [
        'PORT',
        'TELEGRAM_TOKEN',
        'ADMIN_USER_ID',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET'
    ]
    
    print("📝 Note: Environment variables will be set in Railway dashboard:")
    for var in env_vars:
        print(f"   - {var}")
    
    # Check Python version compatibility
    if sys.version_info < (3, 8):
        print("❌ Python version too old. Railway supports Python 3.8+")
        return False
    else:
        print("✅ Python version compatible")
    
    print("\n🎉 Project is ready for Railway deployment!")
    print("\nNext steps:")
    print("1. Push to GitHub")
    print("2. Connect Railway to your repository")
    print("3. Set environment variables in Railway dashboard")
    print("4. Deploy!")
    
    return True

if __name__ == "__main__":
    check_railway_readiness()