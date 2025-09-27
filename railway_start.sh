#!/bin/bash
# Startup script for Railway deployment

echo "Starting Bybit Trading Bot on Railway..."

# Set the port environment variable if not already set
export PORT=${PORT:-5000}

# Start the application
python app.py