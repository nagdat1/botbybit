#!/bin/bash
# Railway Startup Script

echo "🚀 بدء تشغيل بوت التداول على Railway..."

# تعيين المنفذ
export PORT=${PORT:-5000}

# تشغيل التطبيق
echo "✅ جاري التشغيل على المنفذ: $PORT"
python app.py