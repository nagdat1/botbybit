#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تنظيف الملفات المؤقتة والاختبارية
"""

import os
import sys

def cleanup_temp_files():
    """حذف الملفات المؤقتة والاختبارية"""
    
    print("=== تنظيف الملفات المؤقتة ===")
    print()
    
    # قائمة الملفات المؤقتة للحذف
    temp_files = [
        # ملفات الاختبار القديمة
        'debug_project_issue.py',
        'test_signature_issue.py',
        'fix_bybit_signature.py',
        'test_bybit_api_direct.py',
        'comprehensive_bybit_fix.py',
        'final_bybit_fix.py',
        'test_new_keys.py',
        'test_fixed_signature.py',
        'test_direct_order_final.py',
        
        # ملفات الاختبار الأخرى
        'test_bybit_api.py',
        'test_mexc_fix.py',
        'test_mexc_price.py',
        'test_mexc_order.py',
        'test_real_mexc.py',
        'test_mexc_keys.py',
        'test_order_simple.py',
        'test_mexc_debug.py',
        'test_signature_debug.py',
        'test_other_pairs.py',
        'test_improvements.py',
        'test_mexc_debug_simple.py',
        'test_bybit_fix.py',
        'test_mexc_simple.py',
        'test_signature_methods.py',
        'test_correct_symbol.py',
        'test_order_types.py',
        'test_button_fix.py',
        'test_final_button_fix.py',
        'test_integrated_linking.py',
        'test_direct_api.py',
        'test_order_debug.py',
        'test_final_fix.py',
        
        # ملفات التوثيق المؤقتة
        'MEXC_SIGNATURE_FIX.md',
        'MEXC_PRICE_FETCH_FIX.md',
        'FIXES_SUMMARY.md',
        'FINAL_BUTTON_FIX.md',
        'RESTART_INSTRUCTIONS.md',
        'ORDER_DEBUGGING_GUIDE.md',
        'FINAL_SOLUTION.md',
        'BYBIT_API_FIX.md',
        
        # ملفات أخرى
        'update_market_type.py',
        'test_direct_order.py',
        'debug_latest_signal.py',
        'final_solution.py',
        'cleanup_temp_files.py'
    ]
    
    deleted_count = 0
    not_found_count = 0
    
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ تم حذف: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ خطأ في حذف {file}: {e}")
        else:
            print(f"📭 الملف غير موجود: {file}")
            not_found_count += 1
    
    print()
    print("=" * 50)
    print("نتيجة التنظيف")
    print("=" * 50)
    print(f"✅ تم حذف: {deleted_count} ملف")
    print(f"📭 غير موجود: {not_found_count} ملف")
    print(f"📊 إجمالي الملفات: {len(temp_files)} ملف")
    print()
    
    if deleted_count > 0:
        print("🎉 تم تنظيف الملفات المؤقتة بنجاح!")
    else:
        print("✨ لا توجد ملفات مؤقتة للحذف")

def show_remaining_files():
    """عرض الملفات المتبقية المهمة"""
    
    print("=" * 50)
    print("الملفات المهمة المتبقية")
    print("=" * 50)
    print()
    
    important_files = [
        # ملفات النظام الأساسية
        'bybit_trading_bot.py',
        'real_account_manager.py',
        'signal_executor.py',
        'database.py',
        'user_manager.py',
        'position_manager.py',
        
        # ملفات الإعدادات
        'config.py',
        'config_updated.py',
        'env.example',
        
        # ملفات النظام المحسن
        'simple_enhanced_system.py',
        'integrated_signal_system.py',
        'integrated_trading_system.py',
        'enhanced_trading_bot.py',
        'enhanced_portfolio_manager.py',
        
        # ملفات إدارة الإشارات
        'signal_converter.py',
        'signal_id_manager.py',
        'signal_position_manager.py',
        
        # ملفات المنصات
        'mexc_trading_bot.py',
        'exchange_commands.py',
        
        # ملفات الإدارة
        'developer_manager.py',
        'developer_config.py',
        'developer_example.py',
        'init_developers.py',
        
        # ملفات التشغيل
        'run_enhanced_bot.py',
        'run_with_server.py',
        'web_server.py',
        'health.py',
        
        # ملفات الإعداد
        'setup_mexc.py',
        'railway_start.sh',
        'railway.toml',
        'railway.yaml',
        'render.yaml',
        'Dockerfile',
        'requirements.txt',
        
        # ملفات الاختبار المحدثة
        'test_complete_system.py',
        'update_database.py',
        
        # ملفات التوثيق المهمة
        'COMPLETE_GUIDE.md',
        'README_POSITIONS.md',
        'USER_GUIDE_AR.md',
        'FINAL_SUMMARY_AR.md',
        
        # ملفات قاعدة البيانات والسجلات
        'trading_bot.db',
        'trading_bot.log',
        
        # ملفات البيانات
        'spot_pairs.json',
        'futures_pairs.json',
        'popular_pairs.json'
    ]
    
    existing_files = []
    missing_files = []
    
    for file in important_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"✅ الملفات الموجودة ({len(existing_files)}):")
    for file in existing_files:
        print(f"   • {file}")
    
    if missing_files:
        print()
        print(f"❌ الملفات المفقودة ({len(missing_files)}):")
        for file in missing_files:
            print(f"   • {file}")
    
    print()
    print(f"📊 إجمالي الملفات المهمة: {len(important_files)}")
    print(f"✅ موجودة: {len(existing_files)}")
    print(f"❌ مفقودة: {len(missing_files)}")

if __name__ == "__main__":
    print("اختيار العملية:")
    print("1. تنظيف الملفات المؤقتة")
    print("2. عرض الملفات المهمة المتبقية")
    print("3. تنظيف + عرض")
    
    choice = input("اختر (1 أو 2 أو 3): ").strip()
    
    if choice == "1":
        cleanup_temp_files()
    elif choice == "2":
        show_remaining_files()
    elif choice == "3":
        cleanup_temp_files()
        print()
        show_remaining_files()
    else:
        print("اختيار غير صحيح")
        sys.exit(1)
    
    print()
    print("🎉 تم الانتهاء!")
