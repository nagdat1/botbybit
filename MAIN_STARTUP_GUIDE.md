# Main Startup File Guide

This document explains how to use the new [main.py](file:///C:/Users/nagda/OneDrive/Desktop/1/main.py) file as the primary entry point for the Bybit Trading Bot.

## Overview

The [main.py](file:///C:/Users/nagda/OneDrive/Desktop/1/main.py) file is designed to coordinate all components of the trading bot system:
1. Telegram bot (main component)
2. Web server for dashboard and webhook handling
3. Background price update tasks

## Key Features

### 1. Proper Component Management
- Starts the Telegram bot in the main thread (as required by python-telegram-bot)
- Runs the web server in a background thread
- Handles graceful shutdown with signal handlers

### 2. Environment Variable Support
- Uses `PORT` for the health check endpoint (Railway provided)
- Uses `WEBHOOK_PORT` for the web server (defaults to 5000)
- All API keys and tokens loaded from environment variables

### 3. Error Handling
- Comprehensive error handling for all components
- Graceful shutdown on interrupt signals
- Detailed logging of startup process

## How to Use

### Running Locally
```bash
# Set environment variables
export PORT=8080
export WEBHOOK_PORT=5000
export TELEGRAM_TOKEN=your_telegram_bot_token
export ADMIN_USER_ID=your_telegram_user_id
export BYBIT_API_KEY=your_bybit_api_key
export BYBIT_API_SECRET=your_bybit_api_secret

# Run the application
python main.py
```

### Running on Railway
Railway will automatically use the configuration in [railway.yaml](file:///C:/Users/nagda/OneDrive/Desktop/1/railway.yaml):
- Starts with `python main.py`
- Provides `PORT` environment variable automatically
- Uses `WEBHOOK_PORT=5000` as configured

## File Structure Updates

### Modified Files:
1. **[main.py](file:///C:/Users/nagda/OneDrive/Desktop/1/main.py)** - New main startup file
2. **[Dockerfile](file:///C:/Users/nagda/OneDrive/Desktop/1/Dockerfile)** - Updated to use `python main.py`
3. **[railway.yaml](file:///C:/Users/nagda/OneDrive/Desktop/1/railway.yaml)** - Updated to use `python main.py`
4. **[railway.toml](file:///C:/Users/nagda/OneDrive/Desktop/1/railway.toml)** - Updated to use `python main.py`

### New Files:
1. **[health_check.py](file:///C:/Users/nagda/OneDrive/Desktop/1/health_check.py)** - Simple health check endpoint
2. **[test_main.py](file:///C:/Users/nagda/OneDrive/Desktop/1/test_main.py)** - Test script for main.py
3. **[MAIN_STARTUP_GUIDE.md](file:///C:/Users/nagda/OneDrive/Desktop/1/MAIN_STARTUP_GUIDE.md)** - This guide

## Benefits

1. **Simplified Startup**: One command to start everything
2. **Proper Thread Management**: Telegram bot in main thread, web server in background
3. **No Port Conflicts**: Separate ports for main app and web server
4. **Railway Ready**: Configured for Railway deployment
5. **Graceful Shutdown**: Handles SIGINT and SIGTERM properly
6. **Error Resilience**: Continues running even if some components fail

## Expected Output

When you run `python main.py`, you should see:

```
🚀 Starting Bybit Trading Bot...
⏰ Time: 2025-09-27 00:00:00
🌐 Starting web components...
✅ Web server started on port 5000
🤖 Starting Telegram bot...
✅ Telegram bot started successfully
🔗 Bot is now listening for commands and signals...
```

## Troubleshooting

### Common Issues:

1. **Port already in use**:
   - Change `WEBHOOK_PORT` to a different value
   - Ensure no other instances are running

2. **Telegram bot not responding**:
   - Verify [TELEGRAM_TOKEN](file://c:\Users\nagda\OneDrive\Desktop\1\config.py#L13-L13) is correct
   - Check that the bot is added to your Telegram contacts

3. **Web server not accessible**:
   - Verify [WEBHOOK_PORT](file://c:\Users\nagda\OneDrive\Desktop\1\config.py#L26-L26) is not blocked by firewall
   - Check that the port is correctly forwarded (for remote access)

## Migration from Previous Setup

If you were using [run_with_server.py](file:///C:/Users/nagda/OneDrive/Desktop/1/run_with_server.py) or [app.py](file:///C:/Users/nagda/OneDrive/Desktop/1/app.py):

1. **Stop using**: `python run_with_server.py` or `python app.py`
2. **Start using**: `python main.py`
3. **Same environment variables**: No changes needed
4. **Same functionality**: All features preserved

The new [main.py](file:///C:/Users/nagda/OneDrive/Desktop/1/main.py) provides the same functionality with better error handling and Railway compatibility.