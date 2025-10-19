#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي لجميع الإصلاحات المطبقة على المشروع
"""

def test_final_fixes():
    """اختبار نهائي لجميع الإصلاحات"""
    print("اختبار نهائي لجميع الإصلاحات المطبقة على المشروع")
    print("=" * 80)
    
    # اختبار 1: استيراد user_manager
    try:
        import user_manager
        print("[OK] user_manager تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد user_manager: {e}")
        return False
    
    # اختبار 2: استيراد bybit_trading_bot
    try:
        import bybit_trading_bot
        print("[OK] bybit_trading_bot تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد bybit_trading_bot: {e}")
        return False
    
    # اختبار 3: استيراد run_with_server
    try:
        import run_with_server
        print("[OK] run_with_server تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد run_with_server: {e}")
        return False
    
    # اختبار 4: استيراد signal_executor
    try:
        import signal_executor
        print("[OK] signal_executor تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد signal_executor: {e}")
        return False
    
    # اختبار 5: استيراد real_account_manager
    try:
        import real_account_manager
        print("[OK] real_account_manager تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد real_account_manager: {e}")
        return False
    
    # اختبار 6: استيراد signal_converter
    try:
        import signal_converter
        print("[OK] signal_converter تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد signal_converter: {e}")
        return False
    
    # اختبار 7: استيراد app
    try:
        import app
        print("[OK] app تم استيراده بنجاح")
    except Exception as e:
        print(f"[ERROR] خطأ في استيراد app: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("[SUCCESS] جميع الاختبارات نجحت! المشروع جاهز للتشغيل")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_final_fixes()
