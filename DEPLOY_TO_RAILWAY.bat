@echo off
chcp 65001 > nul
cls
echo ========================================
echo 🚀 نشر التحديثات على Railway
echo ========================================
echo.

echo 🔍 التحقق من حالة Git...
git status
echo.

echo 📝 إضافة جميع التغييرات...
git add .
git add -A
echo ✅ تم إضافة التغييرات
echo.

echo 💾 حفظ التغييرات (Commit)...
git commit -m "Fix: إصلاح استيراد signal_position_manager وتحسين نظام إعادة التعيين"
if errorlevel 1 (
    echo ⚠️ لا توجد تغييرات جديدة للحفظ
    echo.
) else (
    echo ✅ تم حفظ التغييرات
    echo.
)

echo 🌐 رفع التغييرات إلى GitHub...
git push origin main
if errorlevel 1 (
    echo ❌ فشل الرفع! تحقق من الاتصال بالإنترنت
    echo.
    pause
    exit /b 1
)
echo ✅ تم رفع التغييرات بنجاح
echo.

echo ========================================
echo ✅ اكتمل النشر!
echo ========================================
echo.
echo 📊 Railway سيقوم بإعادة النشر تلقائياً الآن
echo 🌐 راقب التقدم على: https://railway.app
echo.
echo ⏳ الخطوات التالية:
echo    1. افتح Railway Dashboard
echo    2. راقب عملية Build و Deploy
echo    3. انتظر 2-3 دقائق
echo    4. تحقق من اللوغ للتأكد من عدم وجود أخطاء
echo    5. جرب البوت في Telegram
echo.
echo 🎯 التحديثات المنشورة:
echo    ✅ إصلاح استيراد signal_position_manager
echo    ✅ تحسين نظام إعادة التعيين
echo    ✅ حذف الذاكرة والكاش
echo    ✅ تحديث الأزرار والمعالجات
echo.
pause

