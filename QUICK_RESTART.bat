@echo off
echo 🔄 إعادة تشغيل سريعة...
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak > nul
start "" cmd /c "cd /d %~dp0 && python bybit_trading_bot.py"
echo ✅ تم!
timeout /t 2 /nobreak > nul
exit

