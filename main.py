#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main startup file for the Bybit Trading Bot
This file coordinates all components of the trading bot system.
"""

import os
import sys
import threading
import asyncio
import signal
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from bybit_trading_bot import trading_bot
from web_server import WebServer
from config import *

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Received shutdown signal. Stopping bot and server...")
    sys.exit(0)

def start_telegram_bot():
    """Start the Telegram bot in the main thread"""
    try:
        print("🤖 Starting Telegram bot...")
        
        # Import required modules
        from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
        from bybit_trading_bot import (
            start, settings_menu, account_status, open_positions,
            trade_history, wallet_overview, handle_callback, 
            handle_text_input, error_handler, TELEGRAM_TOKEN
        )
        
        # Create application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_error_handler(error_handler)
        
        # Update available pairs
        try:
            asyncio.run(trading_bot.update_available_pairs())
        except Exception as e:
            print(f"⚠️ Error updating pairs: {e}")
        
        # Start price updates in background thread
        def start_price_updates():
            """Start periodic price updates"""
            def update_prices():
                while True:
                    try:
                        asyncio.run(trading_bot.update_open_positions_prices())
                        threading.Event().wait(30)  # Wait 30 seconds
                    except Exception as e:
                        print(f"⚠️ Error in price update: {e}")
                        threading.Event().wait(60)  # Wait 1 minute on error
            
            threading.Thread(target=update_prices, daemon=True).start()
        
        # Start periodic updates
        start_price_updates()
        
        # Start the bot
        print("✅ Telegram bot started successfully")
        print("🔗 Bot is now listening for commands and signals...")
        
        # Run the bot (this will block)
        application.run_polling(allowed_updates=['message', 'callback_query'])
        
    except Exception as e:
        print(f"❌ Error starting Telegram bot: {e}")
        import traceback
        traceback.print_exc()

def start_web_components():
    """Start web server components in background threads"""
    try:
        print("🌐 Starting web components...")
        
        # Create and configure web server
        web_server = WebServer(trading_bot)
        trading_bot.web_server = web_server
        
        # Start web server in background thread
        server_port = int(os.environ.get('WEBHOOK_PORT', 5000))
        server_thread = threading.Thread(
            target=lambda: web_server.run(debug=False, port=server_port),
            daemon=True
        )
        server_thread.start()
        print(f"✅ Web server started on port {server_port}")
        
    except Exception as e:
        print(f"❌ Error starting web components: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to start all components"""
    print("🚀 Starting Bybit Trading Bot...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start web components in background
        start_web_components()
        
        # Small delay to ensure web server starts
        threading.Event().wait(2)
        
        # Start Telegram bot in main thread (blocking)
        start_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()