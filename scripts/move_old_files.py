#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لنقل ملفات التشخيص القديمة إلى مجلد scripts/
"""

import os
import shutil
from pathlib import Path

# الملفات المراد نقلها
files_to_move = [
    # Debug files
    "debug_project_issue.py",
    "debug_latest_signal.py",
    "debug_signal_execution.py",
    "debug_futures_trading.py",
    "debug_order_issue.py",
    "debug_mexc_order.py",
    
    # Check files
    "check_db_structure.py",
    "check_other_issues.py",
    "check_symbols_and_test.py",
    "check_users.py",
    "check_quantity_requirements.py",
    "check_mexc_symbols.py",
    "check_mexc_detailed.py",
    
    # Comprehensive files
    "comprehensive_bybit_fix.py",
    
    # Final files
    "final_system_updater.py",
    "final_system_integrator.py",
    "final_integration.py",
    "final_bybit_fix.py",
    "final_solution.py",
    "final_solution_guide.py",
    "final_diagnosis.py",
    
    # Fix files
    "fix_bybit_signature.py",
    "fix_all_emojis.py",
    "fix_emojis.py",
    
    # Clean files
    "clean_keys_simple.py",
    "clean_keys_auto.py",
    "clean_and_update_keys.py",
    
    # Other old files
    "update_market_type.py",
    "update_api_auto.py",
    "update_bybit_api_direct.py",
    "update_bybit_keys_only.py",
    "update_to_new_api.py",
    "update_user_api.py",
    "update_database.py",
    "update_user_to_real.py",
    
    # Test files
    "real_trade_fix_tester.py",
    "analyze_button_text.py",
    "quick_button_test.py",
    
    # Analysis files
    "advanced_api_diagnosis.py",
    "advanced_diagnosis.py",
    "simple_api_diagnosis.py",
    "diagnose_signal_execution.py",
    "diagnose_nfpusdt.py",
    
    # Setup/Installation files that are no longer needed
    "apply_new_api_key.py",
    "create_real_user.py",
    "demo_conversion.py",
]

def main():
    # إنشاء مجلد scripts إذا لم يكن موجوداً
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    not_found_count = 0
    error_count = 0
    
    print("Starting to move old files...\n")
    
    for filename in files_to_move:
        if os.path.exists(filename):
            try:
                destination = scripts_dir / filename
                shutil.move(filename, destination)
                print(f"[OK] Moved: {filename}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to move {filename}: {e}")
                error_count += 1
        else:
            print(f"[SKIP] File not found: {filename}")
            not_found_count += 1
    
    print("\n" + "="*50)
    print(f"Files moved: {moved_count}")
    print(f"Not found: {not_found_count}")
    print(f"Errors: {error_count}")
    print("="*50)
    
    # إنشاء ملف README في مجلد scripts
    readme_content = """# 📂 Scripts - ملفات التشخيص القديمة

هذا المجلد يحتوي على ملفات التشخيص والإصلاح القديمة التي تم نقلها من المجلد الرئيسي.

## 📝 ملاحظة
هذه الملفات محفوظة كمرجع تاريخي فقط ولا تحتاج لصيانة.

## 🗑️ يمكن حذفها
إذا كنت متأكداً، يمكنك حذف هذا المجلد بالكامل.

## 🎯 الاستخدام
يمكنك فحص هذه الملفات لفهم بعض المشاكل وحلولها القديمة، لكن يجب عدم تنفيذها على النظام الحالي.
"""
    
    readme_path = scripts_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("\n[DONE] Created scripts/README.md")
    print("\n[DONE] Cleanup completed successfully!")

if __name__ == "__main__":
    main()

