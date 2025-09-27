#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple health check endpoint for the trading bot
"""

import os
from flask import Flask, jsonify
from datetime import datetime

# Create Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Bybit Trading Bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Bybit Trading Bot Health Check"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)