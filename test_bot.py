"""
🧪 Test Script - اختبار سريع للبوت
اختبار المكونات الأساسية
"""
import asyncio
import sys


def test_imports():
    """اختبار استيراد المكتبات"""
    print("🔍 اختبار الاستيرادات...")
    
    try:
        import telegram
        print("  ✅ python-telegram-bot")
    except ImportError as e:
        print(f"  ❌ python-telegram-bot: {e}")
        return False
    
    try:
        import ccxt
        print("  ✅ ccxt")
    except ImportError as e:
        print(f"  ❌ ccxt: {e}")
        return False
    
    try:
        from flask import Flask
        print("  ✅ flask")
    except ImportError as e:
        print(f"  ❌ flask: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError as e:
        print(f"  ❌ python-dotenv: {e}")
        return False
    
    print()
    return True


def test_config():
    """اختبار الإعدادات"""
    print("⚙️ اختبار الإعدادات...")
    
    try:
        from config import TELEGRAM_TOKEN, ADMIN_USER_ID, EMOJIS
        
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_token_here":
            print("  ⚠️  TELEGRAM_TOKEN غير محدد!")
            print("     الرجاء تعيينه في ملف .env")
            return False
        
        print(f"  ✅ TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")
        print(f"  ✅ ADMIN_USER_ID: {ADMIN_USER_ID}")
        print(f"  ✅ EMOJIS: {len(EMOJIS)} emoji loaded")
        print()
        return True
    
    except Exception as e:
        print(f"  ❌ خطأ في config.py: {e}")
        return False


def test_database():
    """اختبار قاعدة البيانات"""
    print("💾 اختبار قاعدة البيانات...")
    
    try:
        from database import db
        
        # إنشاء مستخدم تجريبي
        test_user = db.get_user(123456789)
        if not test_user:
            test_user = db.create_user(123456789, "test_user", "Test", "User")
            print("  ✅ تم إنشاء مستخدم تجريبي")
        else:
            print("  ✅ قراءة مستخدم موجود")
        
        # اختبار الإحصائيات
        total_users = db.get_all_users_count()
        print(f"  ✅ إجمالي المستخدمين: {total_users}")
        
        print()
        return True
    
    except Exception as e:
        print(f"  ❌ خطأ في database.py: {e}")
        return False


async def test_bybit_api():
    """اختبار Bybit API"""
    print("📊 اختبار Bybit API...")
    
    try:
        from bybit_api import public_api
        
        # اختبار جلب الأسعار
        ticker = await public_api.get_ticker("BTC/USDT")
        
        if ticker:
            print(f"  ✅ BTC/USDT Price: ${ticker['price']:,.2f}")
            print(f"  ✅ Change: {ticker.get('change', 0):.2f}%")
        else:
            print("  ⚠️  فشل جلب السعر")
            return False
        
        # اختبار البحث عن الأزواج
        symbols = await public_api.search_symbols("BTC", 3)
        print(f"  ✅ وجد {len(symbols)} أزواج للبيتكوين")
        
        print()
        return True
    
    except Exception as e:
        print(f"  ❌ خطأ في bybit_api.py: {e}")
        return False


def test_handlers():
    """اختبار المعالجات"""
    print("🎯 اختبار المعالجات...")
    
    try:
        from handlers.user_handler import UserHandler
        print("  ✅ UserHandler")
        
        from handlers.admin_handler import AdminHandler
        print("  ✅ AdminHandler")
        
        from handlers.trading_handler import TradingHandler
        print("  ✅ TradingHandler")
        
        print()
        return True
    
    except Exception as e:
        print(f"  ❌ خطأ في handlers: {e}")
        return False


def test_utils():
    """اختبار الأدوات المساعدة"""
    print("🛠️ اختبار الأدوات...")
    
    try:
        from utils.keyboards import main_menu_keyboard
        keyboard = main_menu_keyboard()
        print("  ✅ keyboards.py")
        
        from utils.formatters import format_price
        price = format_price(50000.1234)
        print(f"  ✅ formatters.py: {price}")
        
        from utils.validators import validate_symbol
        is_valid, symbol = validate_symbol("BTCUSDT")
        print(f"  ✅ validators.py: {symbol}")
        
        print()
        return True
    
    except Exception as e:
        print(f"  ❌ خطأ في utils: {e}")
        return False


async def main():
    """الاختبار الرئيسي"""
    print("=" * 50)
    print("🧪 اختبار Bybit Trading Bot")
    print("=" * 50)
    print()
    
    results = []
    
    # الاختبارات
    results.append(("الاستيرادات", test_imports()))
    results.append(("الإعدادات", test_config()))
    results.append(("قاعدة البيانات", test_database()))
    results.append(("Bybit API", await test_bybit_api()))
    results.append(("المعالجات", test_handlers()))
    results.append(("الأدوات", test_utils()))
    
    # النتائج
    print("=" * 50)
    print("📊 النتائج:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"  {test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 50)
    print(f"✅ نجح: {passed}/{len(results)}")
    print(f"❌ فشل: {failed}/{len(results)}")
    print("=" * 50)
    
    if failed == 0:
        print()
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ البوت جاهز للتشغيل")
        print()
        print("لتشغيل البوت:")
        print("  python main.py")
        return True
    else:
        print()
        print("⚠️ بعض الاختبارات فشلت")
        print("الرجاء إصلاح الأخطاء قبل التشغيل")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف الاختبار")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

