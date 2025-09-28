# 🤖 بوت التداول الذكي على Bybit

بوت تداول متقدم لمنصة Bybit يدعم التداول الحقيقي والتجريبي مع واجهة ويب تفاعلية وإشعارات تلجرام.

## ✨ الميزات الجديدة

### 🌐 السيرفر المحلي والواجهة التفاعلية
- **لوحة تحكم ويب حديثة** مع رسوم بيانية تفاعلية
- **تحديثات مباشرة** عبر WebSocket
- **رسوم بيانية لتتبع الرصيد** والصفقات المفتوحة
- **إشعارات فورية** للإشارات الجديدة

### 🔗 تكامل ngrok التلقائي
- **إعداد تلقائي لـ ngrok** بدون تدخل يدوي
- **تحديث تلقائي للرابط** في ملف الإعدادات
- **إشعارات تلجرام** عند تغيير الرابط
- **رابط عام** لاستقبال إشارات TradingView

## 🚀 التشغيل السريع

### الطريقة الأولى: التشغيل التلقائي
```bash
python start_bot.py
```

### الطريقة الثانية: التشغيل مع السيرفر
```bash
python run_with_server.py
```

### الطريقة التقليدية: البوت فقط
```bash
python run_bot.py
```

## 📊 الواجهة الويب

بعد تشغيل البوت، ستحصل على:
- **رابط محلي**: `http://localhost:5000`
- **رابط عام (ngrok)**: سيظهر في التلجرام تلقائياً

### المميزات في الواجهة:
- 📈 **رسم بياني للرصيد** مع التحديثات المباشرة
- 🔄 **الصفقات المفتوحة** مع الأرباح/الخسائر الحالية
- 📡 **آخر الإشارات** المستقبلة من TradingView
- 📊 **إحصائيات البوت** (معدل النجاح، عدد الصفقات)
- 🎯 **رسم بياني للإشارات** والصفقات

## ⚙️ الإعدادات

قم بتحديث ملف `config.py`:

```python
# إعدادات تلغرام
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_USER_ID = YOUR_TELEGRAM_USER_ID

# إعدادات Bybit API
BYBIT_API_KEY = "YOUR_API_KEY"
BYBIT_API_SECRET = "YOUR_API_SECRET"

# إعدادات السيرفر (سيتم تحديثها تلقائياً)
WEBHOOK_URL = "https://your-ngrok-url.ngrok-free.app"
WEBHOOK_PORT = 5000
```

## 📱 أوامر البوت في تلجرام

- **⚙️ الإعدادات**: تخصيص إعدادات التداول
- **📊 حالة الحساب**: عرض الرصيد والإحصائيات
- **🔄 الصفقات المفتوحة**: متابعة الصفقات الحالية
- **▶️ تشغيل البوت**: بدء استقبال الإشارات
- **⏹️ إيقاف البوت**: إيقاف التداول مؤقتاً
- **📊 إحصائيات الإشارات**: عرض إحصائيات الأداء

## 🔔 الإشعارات التلقائية

البوت يرسل إشعارات تلجرام عند:
- 📡 استقبال إشارة جديدة
- 💼 فتح صفقة جديدة
- ✅ إغلاق صفقة
- 🔄 تغيير رابط ngrok
- ⚠️ حدوث أخطاء

## 📈 إعداد TradingView

استخدم الرابط الذي يرسله البوت في تلجرام لإعداد webhook في TradingView:

```
{
    "symbol": "{{ticker}}",
    "action": "{{strategy.order.action}}",
    "price": {{close}},
    "time": "{{time}}"
}
```

## 🔧 المتطلبات

تم تحديث `requirements.txt` ليشمل:
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

## 🛡️ الأمان

- جميع المفاتيح محفوظة في ملف `config.py`
- التحقق من هوية المستخدم لأوامر تلجرام
- حماية endpoints الحساسة
- تشفير البيانات المرسلة

## 📞 الدعم

إذا واجهت مشاكل:
1. تأكد من صحة إعدادات API
2. تحقق من اتصال الإنترنت
3. راجع ملف `trading_bot.log` للأخطاء
4. تأكد من تثبيت جميع المكتبات المطلوبة

---

**ملاحظة**: البوت يدعم التداول التجريبي الداخلي والتداول الحقيقي. ابدأ دائماً بالوضع التجريبي لاختبار الإعدادات. 

# Bybit Trading Bot

A comprehensive trading bot for Bybit with Telegram integration, web dashboard, and TradingView webhook support.

## Features

- Spot and Futures trading on Bybit
- Telegram bot interface for control and notifications
- Web dashboard with real-time data and charts
- TradingView webhook integration
- Demo trading mode
- Advanced profit taking strategies
- Risk management features

## Deployment to Railway

This project is ready for deployment to Railway. Follow these steps:

1. Fork this repository to your GitHub account
2. Go to [Railway.app](https://railway.app) and create an account
3. Create a new project and select "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will automatically detect this is a Python project and use the `railway.yaml` configuration

### Environment Variables

Set these environment variables in your Railway project:

- `TELEGRAM_TOKEN`: Your Telegram bot token
- `ADMIN_USER_ID`: Your Telegram user ID (for admin access)
- `BYBIT_API_KEY`: Your Bybit API key
- `BYBIT_API_SECRET`: Your Bybit API secret

### Configuration

The bot will automatically use Railway's provided URL for webhooks. No additional configuration is needed.

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your credentials:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   ADMIN_USER_ID=your_telegram_user_id
   BYBIT_API_KEY=your_bybit_api_key
   BYBIT_API_SECRET=your_bybit_api_secret
   ```

3. Run the bot:
   ```
   python app.py
   ```

## Usage

Once deployed, the bot will be accessible via:
- Telegram bot interface
- Web dashboard at your Railway URL
- TradingView webhook at `/webhook`

## Support

For issues or questions, please open an issue on GitHub.

## Railway-Specific Notes

This project includes Railway-specific configuration files:
- `railway.yaml`: Main Railway configuration
- `railway.toml`: Additional Railway settings
- `.railway/build.toml`: Build configuration
- `.railway/deploy.toml`: Deployment configuration

The application will automatically bind to the PORT environment variable provided by Railway.
Health checks are performed on the `/health` endpoint.
