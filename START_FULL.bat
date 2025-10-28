@echo off
REM ============================================
REM 🤖 تشغيل مشروع Bybit الكامل
REM تشغيل البوت + سيرفر الويب
REM ============================================

title 🤖 بوت Bybit - النظام الكامل
chcp 65001 > nul
cls

echo.
echo ================================================================
echo           🤖  تشغيل مشروع Bybit الكامل
echo ================================================================
echo.

REM فحص Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت!
    echo.
    echo 📥 حمّل Python من: https://www.python.org/
    echo ⚠️  تأكد من تحديد "Add Python to PATH" عند التثبيت
    echo.
    pause
    exit /b 1
)

echo [1/3] التحقق من المكتبات...
python -c "import telegram" > nul 2>&1
if errorlevel 1 (
    echo ⚠️  المكتبات غير مثبتة
    echo 📦 جاري تثبيت المكتبات...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ فشل تثبيت المكتبات!
        pause
        exit /b 1
    )
)
echo ✅ جاهز

echo.
echo [2/3] التحقق من الإعدادات...
if not exist "config.py" (
    echo ⚠️  ملف config.py مفقود!
    echo.
) else (
    echo ✅ جاهز
)

echo.
echo [3/3] تشغيل النظام الكامل...
echo.
echo ================================================================
echo           ✅  جميع الأنظمة جاهزة للتشغيل
echo ================================================================
echo.
echo 📋 المكونات النشطة:
echo    ✓ بوت Telegram (تلقائي)
echo    ✓ سيرفر الويب (Flask)
echo    ✓ استقبال Webhooks
echo    ✓ التداول الحقيقي والتجريبي
echo.
echo 📝 ملاحظات مهمة:
echo    • اترك النافذة مفتوحة
echo    • لا تغير الملفات أثناء التشغيل
echo    • Ctrl+C لإيقاف النظام
echo.
echo ================================================================
echo.

REM تشغيل التطبيق الكامل
python app.py

REM عند الخروج
echo.
echo ================================================================
echo           🛑  جميع الأنظمة متوقفة
echo ================================================================
echo.
echo 💡 للمساعدة: راجع START_HERE.txt
echo.
pause

