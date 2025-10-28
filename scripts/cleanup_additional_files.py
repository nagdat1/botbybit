#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تنظيف الملفات الإضافية
"""

import os
import shutil
from pathlib import Path

# ملفات إضافية للتنظيف
additional_files = [
    "launch_ultimate_system.py",
    "run_ultimate_system.py",
    "run_enhanced_system.py",
    "run_with_server.py",
    "run_enhanced_bot.py",
    "system_updater.py",
    "system_integration_update.py",
    "ultimate_system_updater.py",
    "cleanup_final.py",
    "cleanup_temp_files.py",
]

def main():
    scripts_dir = Path("scripts")
    
    if not scripts_dir.exists():
        scripts_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    not_found_count = 0
    
    print("Starting to move additional old files...\n")
    
    for filename in additional_files:
        if os.path.exists(filename):
            try:
                destination = scripts_dir / filename
                shutil.move(filename, destination)
                print(f"[OK] Moved: {filename}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to move {filename}: {e}")
                not_found_count += 1
        else:
            print(f"[SKIP] File not found: {filename}")
            not_found_count += 1
    
    print("\n" + "="*50)
    print(f"Files moved: {moved_count}")
    print(f"Not found: {not_found_count}")
    print("="*50)
    
    if moved_count > 0:
        print("\n[DONE] Additional cleanup completed successfully!")
    
    # لا نحتاج نقل السكريبت نفسه

if __name__ == "__main__":
    main()

