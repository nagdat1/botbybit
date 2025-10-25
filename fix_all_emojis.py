#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إزالة الرموز التعبيرية من جميع ملفات Python
"""

import os
import re

def remove_emojis_from_file(filepath):
    """إزالة الرموز التعبيرية من ملف واحد"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إزالة الرموز التعبيرية الشائعة
        emojis_to_remove = [
            '', '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', ''
        ]
        
        original_content = content
        for emoji in emojis_to_remove:
            content = content.replace(emoji, '')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"تم إصلاح: {filepath}")
            return True
        
        return False
        
    except Exception as e:
        print(f"خطأ في {filepath}: {e}")
        return False

def fix_all_python_files():
    """إصلاح جميع ملفات Python"""
    
    python_files = []
    
    # البحث عن جميع ملفات Python
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"تم العثور على {len(python_files)} ملف Python")
    
    fixed_count = 0
    for filepath in python_files:
        if remove_emojis_from_file(filepath):
            fixed_count += 1
    
    print(f"تم إصلاح {fixed_count} ملف")

if __name__ == "__main__":
    fix_all_python_files()
