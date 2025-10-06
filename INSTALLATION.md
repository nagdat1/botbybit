# 📖 دليل التثبيت والإعداد - Bybit Trading Bot

## 📋 المتطلبات الأساسية

- Python 3.9 أو أحدث
- حساب Telegram Bot Token
- حساب Bybit (للتداول الحقيقي - اختياري)

## 🚀 خطوات التثبيت

### 1. تحميل المشروع

```bash
git clone https://github.com/nagdat/botbybit.git
cd botbybit
```

### 2. إنشاء البيئة الافتراضية

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 4. إعداد المتغيرات البيئية

انسخ ملف `env_example.txt` إلى `.env`:

```bash
cp env_example.txt .env
```

افتح `.env` وأضف بياناتك:

```env
TELEGRAM_TOKEN=7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw
ADMIN_USER_ID=8169000394
DEVELOPER_SECRET_KEY=your_secret_key_here
BASE_WEBHOOK_URL=https://your-app.railway.app
```

### 5. الحصول على Telegram Bot Token

1. افتح [@BotFather](https://t.me/BotFather) في Telegram
2. أرسل `/newbot`
3. اتبع التعليمات لإنشاء البوت
4. انسخ التوكن وضعه في `.env`

### 6. الحصول على User ID الخاص بك

1. افتح [@userinfobot](https://t.me/userinfobot) في Telegram
2. سيرسل لك ID الخاص بك
3. ضعه في `ADMIN_USER_ID` في `.env`

### 7. تشغيل البوت

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

أو مباشرة:
```bash
python main.py
```

## 🌐 النشر على Railway

### 1. إنشاء مشروع جديد

1. اذهب إلى [Railway.app](https://railway.app)
2. اضغط "New Project"
3. اختر "Deploy from GitHub repo"

### 2. ربط المشروع

1. اختر repository الخاص بك
2. انتظر حتى يتم رفع المشروع

### 3. إضافة المتغيرات البيئية

في لوحة Railway، اذهب إلى Variables وأضف:

```
TELEGRAM_TOKEN=your_token_here
ADMIN_USER_ID=8169000394
DEVELOPER_SECRET_KEY=your_secret
BASE_WEBHOOK_URL=https://your-app.railway.app
```

### 4. الحصول على رابط التطبيق

1. اذهب إلى Settings
2. اضغط "Generate Domain"
3. انسخ الرابط وضعه في `BASE_WEBHOOK_URL`
4. أعد نشر التطبيق

## 🔑 إعداد Bybit API (للتداول الحقيقي)

### 1. إنشاء API Key

1. اذهب إلى [Bybit](https://www.bybit.com)
2. سجل دخول
3. اذهب إلى Account → API Management
4. اضغط "Create New Key"

### 2. الصلاحيات المطلوبة

اختر الصلاحيات التالية:
- ✅ Read-Write
- ✅ Spot Trading
- ✅ Derivatives Trading
- ❌ Withdrawal (غير مطلوب)

### 3. إضافة API في البوت

في البوت، أرسل:
```
/setapi YOUR_API_KEY YOUR_API_SECRET
```

⚠️ **تحذير:** لا تشارك API Keys مع أي شخص!

## ✅ التحقق من التثبيت

بعد التشغيل، يجب أن ترى:

```
🚀 Starting Bybit Trading Bot...
✅ Handlers setup completed
✅ Bot initialized successfully
🌐 Starting webhook server...
🚀 Starting bot polling...
```

افتح البوت في Telegram وأرسل `/start`

## 🐛 حل المشاكل

### مشكلة: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### مشكلة: "Database locked"
```bash
rm botbybit.db
python main.py
```

### مشكلة: "Invalid token"
تأكد من أن TELEGRAM_TOKEN صحيح في `.env`

### مشكلة: "Permission denied" على start.sh
```bash
chmod +x start.sh
```

## 📞 الدعم

للمساعدة:
- Telegram: @Nagdat
- GitHub Issues: [Create Issue](https://github.com/nagdat/botbybit/issues)

## 🎉 تم التثبيت بنجاح!

يمكنك الآن:
1. اختيار نوع الحساب (تجريبي/حقيقي)
2. البدء بالتداول
3. الاشتراك في إشارات Nagdat
4. متابعة صفقاتك

---

صُنع بـ ❤️ بواسطة Nagdat

