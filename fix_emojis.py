#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إزالة الرموز التعبيرية من bybit_trading_bot.py
"""

import re

def remove_emojis():
    """إزالة الرموز التعبيرية من الملف"""
    
    # قراءة الملف
    with open('bybit_trading_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة الرموز التعبيرية الشائعة
    emojis_to_remove = [
        '', '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', ''
    ]
    
    for emoji in emojis_to_remove:
        content = content.replace(emoji, '')
    
    # كتابة الملف المحدث
    with open('bybit_trading_bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("تم إزالة الرموز التعبيرية من bybit_trading_bot.py")

if __name__ == "__main__":
    remove_emojis()
