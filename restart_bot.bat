@echo off
chcp 65001 > nul
echo ========================================
echo    إعادة تشغيل بوت Bybit
echo ========================================
echo.

echo [1/3] إيقاف البوت الحالي...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py*" 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] تنظيف الذاكرة...
timeout /t 1 /nobreak >nul

echo [3/3] تشغيل البوت...
echo.
echo ✅ البوت يعمل الآن!
echo.
echo 📝 ملاحظة: اترك هذه النافذة مفتوحة
echo 🛑 لإيقاف البوت: اضغط Ctrl+C أو أغلق النافذة
echo.
echo ========================================

python app.py

pause

