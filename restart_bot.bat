@echo off
chcp 65001 > nul
echo ========================================
echo 🔄 إعادة تشغيل البوت
echo ========================================
echo.

echo 🛑 إيقاف جميع نسخ Python...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak > nul

echo ✅ تم إيقاف البوت
echo.
echo 🚀 بدء تشغيل البوت الجديد...
echo.

start "" cmd /c "cd /d %~dp0 && python bybit_trading_bot.py"

echo.
echo ✅ تم تشغيل البوت بنجاح!
echo 📊 يمكنك إغلاق هذه النافذة الآن
echo.
pause
