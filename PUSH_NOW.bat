@echo off
chcp 65001 > nul
cls
echo ========================================
echo 🚀 رفع التحديثات الآن
echo ========================================
echo.

echo 📝 إضافة التغييرات...
git add .
git add -A

echo.
echo 💾 Commit...
git commit -m "Fix: إصلاح جميع الأخطاء وتحديث ملفات النشر"

echo.
echo 🌐 Push إلى GitHub...
git push origin main

echo.
echo ========================================
echo ✅ تم!
echo ========================================
echo.
echo انتظر 2-3 دقائق ثم جرب البوت
echo.
pause

