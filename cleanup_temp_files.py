#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تنظيف الملفات المؤقتة
"""

import os
import sys

def cleanup_temp_files():
    """حذف الملفات المؤقتة"""
    
    print("=== تنظيف الملفات المؤقتة ===")
    print()
    
    temp_files = [
        'debug_project_issue.py',
        'test_signature_issue.py',
        'fix_bybit_signature.py',
        'test_bybit_api_direct.py',
        'comprehensive_bybit_fix.py',
        'final_bybit_fix.py'
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"تم حذف: {file}")
            except Exception as e:
                print(f"خطأ في حذف {file}: {e}")
        else:
            print(f"الملف غير موجود: {file}")
    
    print()
    print("تم تنظيف الملفات المؤقتة!")

if __name__ == "__main__":
    cleanup_temp_files()
