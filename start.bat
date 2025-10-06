@echo off
REM ============================================
REM Bybit Trading Bot - Start Script (Windows)
REM ============================================

echo 🚀 Starting Bybit Trading Bot...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Update requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 📝 Creating .env from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your credentials
    pause
    exit
)

REM Start the bot
echo ✅ Starting bot...
python main.py

pause

