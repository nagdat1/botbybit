# Bybit Trading Bot

A Telegram bot for trading on Bybit with web interface and TradingView webhook integration.

## Deployment on Railway

This project is configured to run on Railway. Follow these steps:

1. Create a new Railway project
2. Connect your GitHub repository or upload the code
3. Set the following environment variables in Railway:
   - `TELEGRAM_TOKEN` - Your Telegram bot token
   - `ADMIN_USER_ID` - Your Telegram user ID
   - `BYBIT_API_KEY` - Your Bybit API key
   - `BYBIT_API_SECRET` - Your Bybit API secret

4. Railway will automatically use the `railway.yaml` configuration file

## Running locally

To run locally, you can use:

```bash
python run_with_server.py
```

## Webhook URL

When deployed on Railway, your webhook URL will be:
`https://your-app-name.up.railway.app/webhook`

Replace `your-app-name` with your actual Railway app name.

## ✨ New Features

### 🌐 Local Server and Interactive Interface
- **Modern Web Dashboard** with interactive charts
- **Real-time Updates** via WebSocket
- **Balance Charts** and open orders tracking
- **Instant Notifications** for new signals

### 🔗 Automatic ngrok Integration
- **Automatic ngrok Setup** without manual intervention
- **Automatic URL Update** in settings file
- **Telegram Notifications** when URL changes
- **Public URL** for receiving TradingView signals

## 🚀 Quick Start

### Method 1: Auto Run
```
python start_bot.py
```

### Method 2: Run with Server
```
python run_with_server.py
```

### Traditional Method: Bot Only
```
python run_bot.py
```

## 📊 Web Interface

After running the bot, you will get:
- **Local URL**: `http://localhost:5000`
- **Public URL (ngrok)**: Will appear in Telegram automatically

### Features in the interface:
- 📈 **Balance Chart** with real-time updates
- 🔄 **Open Orders** with current P&L
- 📡 **Latest Signals** received from TradingView
- 📊 **Bot Statistics** (win rate, number of trades)
- 🎯 **Signal Chart** and trades

## ⚙️ Settings

Update `config.py`:

```
# Telegram Settings
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_USER_ID = YOUR_TELEGRAM_USER_ID

# Bybit API Settings
BYBIT_API_KEY = "YOUR_API_KEY"
BYBIT_API_SECRET = "YOUR_API_SECRET"

# Server Settings (will be updated automatically)
WEBHOOK_URL = "https://your-ngrok-url.ngrok-free.app"
WEBHOOK_PORT = 5000
```

## 📱 Bot Commands in Telegram

- **⚙️ Settings**: Customize trading settings
- **📊 Account Status**: Display balance and statistics
- **🔄 Open Orders**: Monitor current trades
- **▶️ Run Bot**: Start receiving signals
- **⏹️ Stop Bot**: Temporarily stop trading
- **📊 Signal Statistics**: Display performance statistics

## 🔔 Automatic Notifications

The bot sends Telegram notifications on:
- 📡 Receiving a new signal
- 💼 Opening a new order
- ✅ Closing an order
- 🔄 ngrok URL change
- ⚠️ Errors

## 📈 Setting Up TradingView

Use the URL sent by the bot in Telegram to set up a webhook in TradingView:

```
{
    "symbol": "{{ticker}}",
    "action": "{{strategy.order.action}}",
    "price": {{close}},
    "time": "{{time}}"
}
```

## 🔧 Requirements

`requirements.txt` includes:
```
python-telegram-bot==20.7
requests==2.31.0
flask==2.3.3
flask-socketio==5.3.6
plotly==5.17.0
dash==2.14.2
dash-bootstrap-components==1.5.0
pandas==2.1.3
pyngrok==7.0.0
```

## 🛡️ Security

- All keys are stored in `config.py`
- User authentication for Telegram commands
- Protection for sensitive endpoints
- Data encryption for transmission

## 📞 Support

If you encounter issues:
1. Verify API settings
2. Check internet connection
3. Review `trading_bot.log` for errors
4. Ensure all required libraries are installed

---

**Note**: The bot supports internal paper trading and real trading. Always start with the paper trading mode to test settings.
