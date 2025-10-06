# 🚀 Bybit Trading Bot - بوت تداول احترافي

## 📋 نظرة عامة
بوت تيليجرام احترافي متكامل للتداول على منصة Bybit مع دعم كامل لـ Spot & Futures، أدوات إدارة المخاطر المتقدمة، ونظام إشارات احترافي.

## ✨ المميزات الرئيسية

### 🎯 أنواع الحسابات
- **حساب تجريبي (Demo)**: محاكاة كاملة للسوق بدون مخاطر
- **حساب حقيقي (Real)**: تداول فعلي عبر Bybit API

### 📊 أنواع التداول
- **Spot Trading**: التداول الفوري
- **Futures Trading**: العقود الآجلة مع رافعة مالية (1x - 20x)

### 🛡️ أدوات إدارة المخاطر
- **Stop Loss**: إيقاف الخسارة
- **Take Profit**: جني الأرباح
- **Trailing Stop**: إيقاف متحرك
- **إغلاقات جزئية**: إغلاق 25%، 50%، أو 75% من الصفقة

### ⚡ نظام الإشارات
- **إشارات Nagdat**: إشارات احترافية من المطور
- **Webhook شخصي**: استقبال إشارات خاصة لكل مستخدم
- **تنفيذ تلقائي**: تطبيق الإشارات فوراً

### 📈 مراقبة الصفقات
- عرض الصفقات المفتوحة
- تحديث الأسعار لحظياً
- حساب الأرباح والخسائر
- ألوان توضيحية (🟢 أخضر للربح، 🔴 أحمر للخسارة)

### 👨‍💻 لوحة المطور
- إرسال إشارات لجميع المشتركين
- إدارة المستخدمين
- إحصائيات البوت
- محاكاة الأوامر

## 🔧 التثبيت

### المتطلبات
- Python 3.9 أو أحدث
- حساب Telegram Bot Token
- حساب Bybit API (للتداول الحقيقي)

### الخطوات

1. **استنساخ المشروع**
```bash
git clone https://github.com/nagdat/botbybit.git
cd botbybit
```

2. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

3. **إعداد المتغيرات البيئية**
أنشئ ملف `.env` في المجلد الرئيسي:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_USER_ID=8169000394
DEVELOPER_SECRET_KEY=your_secret_key
BASE_WEBHOOK_URL=https://your-app.railway.app
```

4. **تشغيل البوت**
```bash
python main.py
```

## 📱 كيفية الاستخدام

### للمستخدمين
1. ابدأ محادثة مع البوت: `/start`
2. اختر نوع الحساب (تجريبي/حقيقي)
3. للحساب الحقيقي: أدخل API Key وSecret من Bybit
4. ابدأ التداول باستخدام الأزرار التفاعلية
5. اشترك في إشارات Nagdat للحصول على توصيات

### للمطور (Nagdat)
1. افتح البوت لتظهر لوحة المطور تلقائياً
2. أرسل إشارات لجميع المشتركين
3. راقب إحصائيات البوت
4. أدر المستخدمين

## 🏗️ هيكل المشروع

```
botbybit/
├── main.py                 # البوت الرئيسي
├── config.py              # الإعدادات
├── database.py            # قاعدة البيانات
├── bybit_api.py          # وحدة Bybit API
├── webhook_server.py      # خادم Webhooks
├── handlers/
│   ├── user_handler.py    # معالجات المستخدمين
│   ├── admin_handler.py   # معالجات المطور
│   └── trading_handler.py # معالجات التداول
├── utils/
│   ├── keyboards.py       # الأزرار التفاعلية
│   ├── formatters.py      # تنسيق الرسائل
│   └── validators.py      # التحقق من المدخلات
├── requirements.txt       # المتطلبات
└── README.md             # هذا الملف
```

## 🔐 الأمان
- تشفير بيانات API Keys
- توكنات UUID فريدة لكل Webhook
- فصل صلاحيات المستخدمين والمطور
- التحقق من الهوية في كل عملية

## 🌐 النشر على Railway

### نشر سريع في 5 دقائق! ⚡

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/nagdat/botbybit)

**أو يدوياً:**

1. **رفع على GitHub**
```bash
git init && git add . && git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

2. **النشر على Railway**
   - اذهب إلى [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub"
   - اختر repository

3. **إضافة المتغيرات**
   - Variables → Add:
     - `TELEGRAM_TOKEN`
     - `ADMIN_USER_ID` 
     - `BASE_WEBHOOK_URL` (بعد Generate Domain)

4. **تفعيل Domain**
   - Settings → Generate Domain
   - انسخ الرابط وضعه في `BASE_WEBHOOK_URL`
   - Redeploy

**✅ جاهز!** البوت يعمل الآن 24/7

📖 [دليل النشر الكامل](DEPLOY_RAILWAY.md) | [دليل تفصيلي](RAILWAY_DEPLOYMENT.md)

## 📞 الدعم والتواصل
- **المطور**: Nagdat
- **Telegram**: @Nagdat
- **User ID**: 8169000394

## 📄 الترخيص
هذا المشروع ملك خاص لـ Nagdat. جميع الحقوق محفوظة © 2024

## ⚠️ تنويه
التداول في العملات المشفرة يحمل مخاطر عالية. استخدم الحساب التجريبي أولاً لفهم كيفية عمل البوت.

---

صُنع بـ ❤️ بواسطة Nagdat

