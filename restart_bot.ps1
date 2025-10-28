# -*- coding: utf-8 -*-
# Restart Bybit Trading Bot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   إعادة تشغيل بوت Bybit" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# الحصول على المسار الحالي
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "[1/3] إيقاف البوت الحالي..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "  - إيقاف عملية Python (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✅ تم إيقاف العمليات" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  لا توجد عمليات Python قيد التشغيل" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/3] انتظار 2 ثانية..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Write-Host "  ✅ جاهز" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] تشغيل البوت..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ البوت يعمل الآن!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 ملاحظات:" -ForegroundColor Yellow
Write-Host "  • اترك هذه النافذة مفتوحة" -ForegroundColor White
Write-Host "  • لإيقاف البوت: اضغط Ctrl+C" -ForegroundColor White
Write-Host "  • السجلات في: trading_bot.log" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تشغيل البوت
python app.py

Write-Host ""
Write-Host "⚠️ البوت توقف!" -ForegroundColor Red
Write-Host ""
pause

