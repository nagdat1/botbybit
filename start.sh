#!/bin/bash

# ============================================
# Bybit Trading Bot - Start Script
# ============================================

echo "🚀 Starting Bybit Trading Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/Update requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
    exit 1
fi

# Start the bot
echo "✅ Starting bot..."
python main.py

