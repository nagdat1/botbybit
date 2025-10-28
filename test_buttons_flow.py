#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تدفق الأزرار
فحص جميع الأزرار والتأكد من ربطها بالدوال الصحيحة
"""

import re
from pathlib import Path

def extract_callbacks_from_file(file_path):
    """استخراج جميع callback_data من الملف"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع callback_data
    pattern = r'callback_data=["\']([^"\']+)["\']'
    callbacks = re.findall(pattern, content)
    
    return set(callbacks)

def extract_handlers_from_file(file_path):
    """استخراج جميع معالجات الأزرار من handle_callback"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع معالجات if data ==
    pattern = r'if data == ["\']([^"\']+)["\']'
    handlers = re.findall(pattern, content)
    
    # البحث عن جميع معالجات elif data ==
    pattern2 = r'elif data == ["\']([^"\']+)["\']'
    handlers.extend(re.findall(pattern2, content))
    
    # البحث عن جميع معالجات startswith
    pattern3 = r'if data\.startswith\(["\']([^"\']+)["\']'
    handlers.extend(re.findall(pattern3, content))
    
    pattern4 = r'elif data\.startswith\(["\']([^"\']+)["\']'
    handlers.extend(re.findall(pattern4, content))
    
    # البحث عن معالجات "or data ==" في نفس السطر
    pattern5 = r'or data == ["\']([^"\']+)["\']'
    handlers.extend(re.findall(pattern5, content))
    
    return set(handlers)

def main():
    import sys
    import io
    # إصلاح encoding لـ Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("🔍 فحص الأزرار في المشروع")
    print("=" * 60)
    
    # 1. استخراج جميع callback_data المُعرّفة
    print("\n1️⃣ استخراج جميع callback_data من الملفات...")
    
    callbacks_from_main = extract_callbacks_from_file('bybit_trading_bot.py')
    callbacks_from_builders = extract_callbacks_from_file('buttons/keyboard_builders.py')
    
    all_callbacks = callbacks_from_main.union(callbacks_from_builders)
    
    print(f"   ✅ عدد الأزرار في bybit_trading_bot.py: {len(callbacks_from_main)}")
    print(f"   ✅ عدد الأزرار في keyboard_builders.py: {len(callbacks_from_builders)}")
    print(f"   📊 إجمالي الأزرار الفريدة: {len(all_callbacks)}")
    
    # 2. استخراج جميع المعالجات من handle_callback
    print("\n2️⃣ استخراج جميع المعالجات من handle_callback...")
    
    handlers = extract_handlers_from_file('bybit_trading_bot.py')
    
    print(f"   ✅ عدد المعالجات: {len(handlers)}")
    
    # 3. مقارنة الأزرار بالمعالجات
    print("\n3️⃣ فحص الأزرار المفقودة...")
    
    # أزرار بدون معالجات
    missing_handlers = []
    for callback in all_callbacks:
        # التحقق من المعالج المباشر
        if callback not in handlers:
            # التحقق من المعالجات التي تستخدم startswith
            found_prefix = False
            for handler_prefix in handlers:
                if callback.startswith(handler_prefix):
                    found_prefix = True
                    break
            
            if not found_prefix:
                missing_handlers.append(callback)
    
    if missing_handlers:
        print(f"   ❌ أزرار بدون معالجات ({len(missing_handlers)}):")
        for callback in sorted(missing_handlers)[:20]:  # عرض أول 20 فقط
            print(f"      • {callback}")
        if len(missing_handlers) > 20:
            print(f"      ... و {len(missing_handlers) - 20} أزرار أخرى")
    else:
        print("   ✅ جميع الأزرار لديها معالجات!")
    
    # 4. فحص الأزرار الأساسية
    print("\n4️⃣ فحص الأزرار الأساسية...")
    
    essential_buttons = {
        'settings': 'قائمة الإعدادات',
        'select_exchange': 'اختيار المنصة',
        'set_amount': 'تعيين مبلغ التداول',
        'set_market': 'تعيين نوع السوق',
        'set_account': 'تعيين نوع الحساب',
        'set_leverage': 'تعيين الرافعة المالية',
        'set_demo_balance': 'تعيين رصيد الحساب التجريبي',
        'auto_apply_menu': 'قائمة التطبيق التلقائي',
        'risk_management_menu': 'قائمة إدارة المخاطر',
        'webhook_url': 'عرض رابط webhook',
        'market_spot': 'تفعيل Spot',
        'market_futures': 'تفعيل Futures',
        'account_real': 'تفعيل الحساب الحقيقي',
        'account_demo': 'تفعيل الحساب التجريبي'
    }
    
    for callback, description in essential_buttons.items():
        if callback in all_callbacks:
            if callback in handlers or any(callback.startswith(h) for h in handlers):
                print(f"   ✅ {description}: موجود ومرتبط")
            else:
                print(f"   ❌ {description}: موجود لكن غير مرتبط")
        else:
            print(f"   ⚠️ {description}: غير موجود!")
    
    # 5. التقرير النهائي
    print("\n" + "=" * 60)
    print("📋 التقرير النهائي")
    print("=" * 60)
    print(f"✅ إجمالي الأزرار: {len(all_callbacks)}")
    print(f"✅ إجمالي المعالجات: {len(handlers)}")
    print(f"❌ أزرار بدون معالجات: {len(missing_handlers)}")
    
    if len(missing_handlers) == 0:
        print("\n🎉 رائع! جميع الأزرار مترابطة بشكل صحيح!")
    else:
        print(f"\n⚠️ يوجد {len(missing_handlers)} أزرار تحتاج معالجات")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

