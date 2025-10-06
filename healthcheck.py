"""
❤️ Health Check Endpoint
للتحقق من صحة البوت
"""
import requests
import sys
import os

def check_health():
    """فحص صحة البوت"""
    try:
        port = os.getenv('PORT', os.getenv('WEBHOOK_PORT', '5000'))
        url = f"http://localhost:{port}/health"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Bot is healthy!")
                return True
        
        print(f"❌ Bot is unhealthy: {response.status_code}")
        return False
    
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = check_health()
    sys.exit(0 if result else 1)

