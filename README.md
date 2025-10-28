# 🤖 BotByBit - Multi-User Trading Bot

بوت تداول متعدد المستخدمين يعمل مع منصتي Bybit و MEXC عبر Webhooks من TradingView.

## ⭐ الميزات الرئيسية

- 🔄 **دعم متعدد المستخدمين**: كل مستخدم له إعدادات مستقلة وحسابات منفصلة
- 💰 **حسابات Demo و Real**: تجربة آمنة مع الحسابات التجريبية أو تداول حقيقي
- 📊 **Spot & Futures**: دعم كامل للأسواق الفورية والعقود الآجلة
- 📡 **Webhooks من TradingView**: استقبال إشارات تلقائي
- 🎯 **إدارة مخاطر متقدمة**: Take Profit متعدد المستويات + Trailing Stop Loss
- 🔐 **آمن**: تشفير API Keys وإدارة صلاحيات كاملة
- 🌐 **منصات متعددة**: دعم Bybit و MEXC
- 📱 **واجهة Telegram**: سهل الاستخدام عبر البوت

## 🚀 البدء السريع

### المتطلبات

- Python 3.8+
- Telegram Bot Token
- Bybit API Keys (للحسابات الحقيقية)
- TradingView (لإرسال الإشارات)

### التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/yourusername/botbybit.git
cd botbybit

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ ملف الإعدادات
cp env.example .env

# تعديل .env بإضافة API Keys
nano .env
```

### التشغيل

```bash
# تشغيل البوت
python app.py
```

## 📖 التوثيق

- 📁 [هيكل المشروع](PROJECT_STRUCTURE.md) - شرح شامل لهيكل المشروع
- 🧹 [ملخص التنظيف](CLEANUP_SUMMARY.md) - تفاصيل تنظيف الملفات
- 📜 [ملفات التشخيص](scripts/README.md) - ملفات قديمة للرجوع

## 🏗️ البنية

```
botbybit/
├── app.py                    # Flask application + Webhooks
├── bybit_trading_bot.py     # Main trading bot
├── config.py                # Settings
├── database.py              # SQLite database
├── user_manager.py          # User management
├── developer_manager.py      # Developer system
└── real_account_manager.py  # Real account integration
```

## 💻 الاستخدام

### للمستخدمين

1. ابدأ بالبوت في Telegram: `/start`
2. أضف API Keys (للحسابات الحقيقية)
3. حدد نوع السوق (Spot/Futures)
4. حدد نوع الحساب (Demo/Real)
5. أرسل إشاراتك من TradingView

### للمطورين

1. اتبع التعليمات في [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. راجع الكود في الملفات الرئيسية
3. استخدم ملفات التشخيص في `scripts/` كمرجع

## 🔧 الإعدادات

### المتغيرات البيئية (.env)

```env
# Telegram
TELEGRAM_TOKEN=your_token
ADMIN_USER_ID=your_id

# Bybit (للحساب الافتراضي)
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret

# MEXC (اختياري)
MEXC_API_KEY=your_key
MEXC_API_SECRET=your_secret
```

## 📊 قاعدة البيانات

المشروع يستخدم SQLite لقاعدة البيانات:

- **users**: بيانات المستخدمين
- **orders**: سجل الصفقات
- **developers**: معلومات المطورين
- **developer_followers**: علاقات المتابعة
- **signal_positions**: ربط الإشارات بالصفقات

## 🔐 الأمان

- ✅ تشفير API Keys في قاعدة البيانات
- ✅ HMAC Signatures للطلبات
- ✅ عزل كامل بين حسابات المستخدمين
- ✅ التحقق من الصلاحيات
- ✅ `.gitignore` لحماية الملفات الحساسة

## 🌟 الميزات المتقدمة

- **Multi-level Take Profit**: إغلاق جزئي للصفقات (25%, 50%, 25%)
- **Trailing Stop Loss**: وقف خسارة متحرك
- **Breakeven**: رفع SL إلى نقطة التعادل بعد TP1
- **Signal Linking**: ربط الإشارات بنفس ID
- **Position Management**: إدارة متقدمة للصفقات
- **Real-time Price Updates**: تحديث الأسعار كل 30 ثانية

## 📈 الأنواع المدعومة

### الأسواق
- ✅ Spot Trading (التداول الفوري)
- ✅ Futures Trading (العقود الآجلة)

### الحسابات
- ✅ Demo Mode (حساب تجريبي)
- ✅ Real Mode (حساب حقيقي)

### المنصات
- ✅ Bybit (Spot & Futures)
- ✅ MEXC (Spot only)

## 🐛 الإبلاغ عن المشاكل

إذا واجهت مشكلة:
1. راجع ملف `trading_bot.log` للأخطاء
2. تأكد من صحة API Keys
3. تحقق من إعدادات قاعدة البيانات

## 📄 الترخيص

هذا المشروع مطور خصيصاً للاستخدام الخاص.

## 📞 الدعم

للمزيد من المعلومات أو الدعم، راجع:
- 📖 [هيكل المشروع](PROJECT_STRUCTURE.md)
- 🧹 [ملخص التنظيف](CLEANUP_SUMMARY.md)
- 📂 [ملفات التشخيص](scripts/)

---

**الإصدار**: 3.0.0  
**آخر تحديث**: 2024  
**الحالة**: ✅ جاهز للاستخدام

