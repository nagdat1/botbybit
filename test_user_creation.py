#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام إنشاء المستخدمين وحفظ API Keys
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from users.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_creation():
    """اختبار إنشاء مستخدم جديد"""
    # استخدم ID تجريبي
    test_user_id = 999999999
    
    print("="*60)
    print("🧪 اختبار نظام إنشاء المستخدمين")
    print("="*60)
    
    # الخطوة 1: حذف المستخدم إذا كان موجوداً (للاختبار)
    print(f"\n1️⃣ التحقق من المستخدم {test_user_id}...")
    user = db_manager.get_user(test_user_id)
    if user:
        print(f"   ✅ المستخدم موجود: {user.get('user_id')}")
    else:
        print(f"   ⚪ المستخدم غير موجود")
    
    # الخطوة 2: إنشاء المستخدم
    print(f"\n2️⃣ إنشاء المستخدم {test_user_id}...")
    result = db_manager.create_user(test_user_id)
    if result:
        print(f"   ✅ تم إنشاء المستخدم بنجاح")
    else:
        print(f"   ❌ فشل في إنشاء المستخدم")
        return False
    
    # الخطوة 3: التحقق من الإنشاء
    print(f"\n3️⃣ التحقق من إنشاء المستخدم...")
    user = db_manager.get_user(test_user_id)
    if user:
        print(f"   ✅ المستخدم موجود في قاعدة البيانات")
        print(f"      - user_id: {user.get('user_id')}")
        print(f"      - exchange: {user.get('exchange', 'غير محدد')}")
        print(f"      - is_active: {user.get('is_active')}")
    else:
        print(f"   ❌ فشل في التحقق من المستخدم")
        return False
    
    # الخطوة 4: تحديث بيانات المستخدم (محاكاة حفظ API Keys)
    print(f"\n4️⃣ محاكاة حفظ API Keys...")
    test_data = {
        'bybit_api_key': 'TEST_API_KEY_123456',
        'bybit_api_secret': 'TEST_API_SECRET_789',
        'exchange': 'bybit',
        'is_active': True
    }
    
    result = db_manager.update_user_data(test_user_id, test_data)
    if result:
        print(f"   ✅ تم حفظ البيانات بنجاح")
    else:
        print(f"   ❌ فشل في حفظ البيانات")
        return False
    
    # الخطوة 5: التحقق من الحفظ
    print(f"\n5️⃣ التحقق من حفظ البيانات...")
    user = db_manager.get_user(test_user_id)
    if user:
        print(f"   ✅ تم التحقق من البيانات المحفوظة:")
        print(f"      - bybit_api_key: {user.get('bybit_api_key', 'غير موجود')}")
        print(f"      - bybit_api_secret: {'موجود' if user.get('bybit_api_secret') else 'غير موجود'}")
        print(f"      - exchange: {user.get('exchange')}")
        print(f"      - is_active: {user.get('is_active')}")
        
        # التحقق من القيم
        if user.get('bybit_api_key') == test_data['bybit_api_key']:
            print(f"   ✅ API Key محفوظ بشكل صحيح")
        else:
            print(f"   ❌ API Key غير صحيح")
            return False
            
        if user.get('exchange') == 'bybit':
            print(f"   ✅ Exchange محفوظ بشكل صحيح")
        else:
            print(f"   ❌ Exchange غير صحيح")
            return False
    else:
        print(f"   ❌ فشل في جلب البيانات المحفوظة")
        return False
    
    print("\n" + "="*60)
    print("🎉 نجح الاختبار! النظام يعمل بشكل صحيح")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = test_user_creation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

