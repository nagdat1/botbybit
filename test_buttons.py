"""
اختبار بسيط للأزرار
"""

import sys
import os

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("فحص معالجات الأزرار في bybit_trading_bot.py")
print("=" * 60)

try:
    # استيراد الملف
    import bybit_trading_bot
    print("✅ تم استيراد bybit_trading_bot بنجاح")
    
    # فحص وجود الدوال المهمة
    functions_to_check = [
        'handle_callback',
        'handle_text_input',
        'start',
        'settings_menu',
        'portfolio_handler',
        'open_positions',
        'trade_history',
        'account_status'
    ]
    
    print("\nفحص الدوال:")
    for func_name in functions_to_check:
        if hasattr(bybit_trading_bot, func_name):
            print(f"  ✅ {func_name} موجودة")
        else:
            print(f"  ❌ {func_name} مفقودة")
    
    # فحص دالة main
    if hasattr(bybit_trading_bot, 'main'):
        print("\n✅ دالة main موجودة")
    else:
        print("\n❌ دالة main مفقودة")
    
    print("\n" + "=" * 60)
    print("✅ الفحص انتهى بنجاح")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ خطأ في الاستيراد: {e}")
    import traceback
    traceback.print_exc()

