# 🏗️ هيكل المشروع - Project Structure

## 📁 الهيكل الكامل

```
botbybit/
├── 📄 main.py                    # البوت الرئيسي - نقطة البداية
├── 📄 config.py                  # الإعدادات والثوابت
├── 📄 database.py                # إدارة قاعدة البيانات SQLite
├── 📄 bybit_api.py               # التكامل مع Bybit API
├── 📄 webhook_server.py          # خادم Webhooks (Flask)
│
├── 📂 handlers/                  # معالجات الأوامر والتفاعلات
│   ├── __init__.py
│   ├── user_handler.py           # معالجات المستخدمين العاديين
│   ├── admin_handler.py          # معالجات المطور/الأدمن
│   └── trading_handler.py        # معالجات التداول والصفقات
│
├── 📂 utils/                     # أدوات مساعدة
│   ├── __init__.py
│   ├── keyboards.py              # أزرار Telegram
│   ├── formatters.py             # تنسيق الرسائل
│   └── validators.py             # التحقق من المدخلات
│
├── 📂 docs/                      # التوثيق
│   ├── README.md                 # الدليل الرئيسي
│   ├── INSTALLATION.md           # دليل التثبيت
│   ├── FEATURES.md               # شرح المميزات
│   ├── FAQ.md                    # الأسئلة الشائعة
│   ├── QUICKSTART.md             # البدء السريع
│   ├── CHANGELOG.md              # سجل التغييرات
│   └── PROJECT_STRUCTURE.md      # هذا الملف
│
├── 📄 requirements.txt           # المكتبات المطلوبة
├── 📄 .gitignore                 # ملفات يتم تجاهلها من Git
├── 📄 env_example.txt            # مثال للمتغيرات البيئية
├── 📄 LICENSE                    # الترخيص (MIT)
│
├── 📄 start.sh                   # سكريبت تشغيل (Linux/Mac)
├── 📄 start.bat                  # سكريبت تشغيل (Windows)
├── 📄 test_bot.py                # اختبارات سريعة
│
├── 📄 Procfile                   # للنشر على Railway/Heroku
├── 📄 runtime.txt                # إصدار Python
│
├── 📄 context.txt                # ملف السياق الأصلي
├── 💾 botbybit.db                # قاعدة البيانات (يتم إنشاؤها تلقائياً)
└── 📝 bot.log                    # ملف السجلات (يتم إنشاؤه تلقائياً)
```

---

## 📋 شرح الملفات

### 🎯 الملفات الرئيسية

#### `main.py`
**الوظيفة:** نقطة البداية الرئيسية للبوت
```python
# يحتوي على:
- إعداد البوت
- ربط المعالجات (handlers)
- إدارة دورة حياة البوت
- تشغيل خادم Webhooks

# كيفية التشغيل:
python main.py
```

#### `config.py`
**الوظيفة:** جميع الإعدادات والثوابت
```python
# يحتوي على:
- معلومات Telegram (TOKEN, ADMIN_ID)
- إعدادات التداول (الحدود، الرافعة)
- ألوان ورموز الواجهة
- رسائل النظام
- إعدادات Bybit API

# مثال:
TELEGRAM_TOKEN = "..."
ADMIN_USER_ID = 8169000394
TRADING_CONFIG = {...}
```

#### `database.py`
**الوظيفة:** إدارة كاملة لقاعدة البيانات
```python
# الجداول:
- users: معلومات المستخدمين
- trades: الصفقات
- signals: الإشارات
- nagdat_subscribers: المشتركين
- statistics: الإحصائيات

# الوظائف الرئيسية:
- get_user() / create_user()
- create_trade() / get_open_trades()
- subscribe_to_nagdat()
- update_statistics()
```

#### `bybit_api.py`
**الوظيفة:** التكامل مع Bybit
```python
# المميزات:
- جلب الأسعار والأزواج
- تنفيذ صفقات Spot
- تنفيذ صفقات Futures
- إدارة الرافعة المالية
- Stop Loss / Take Profit
- الحصول على الرصيد والصفقات

# استخدام:
api = BybitAPI(api_key, api_secret)
ticker = await api.get_ticker("BTC/USDT")
order = await api.create_spot_order(...)
```

#### `webhook_server.py`
**الوظيفة:** خادم لاستقبال الإشارات الخارجية
```python
# Endpoints:
- /health                  → فحص الصحة
- /webhook/user/<token>    → webhook المستخدم
- /webhook/nagdat          → webhook المطور
- /api/stats               → الإحصائيات

# يعمل على Flask في thread منفصل
```

---

### 📂 مجلد handlers/

#### `user_handler.py`
**المعالجات:**
- `/start` - بدء البوت
- `/help` - المساعدة
- `/setapi` - إضافة API Keys
- عرض المحفظة
- الإعدادات
- التبديل بين الحسابات

#### `admin_handler.py`
**المعالجات:**
- لوحة المطور
- إرسال إشارات Nagdat
- إدارة المشتركين
- الإحصائيات
- الرسائل الجماعية

#### `trading_handler.py`
**المعالجات:**
- فتح صفقات (Buy/Sell)
- اختيار نوع الصفقة (Spot/Futures)
- اختيار الزوج والمبلغ
- عرض الصفقات المفتوحة
- إغلاق كامل/جزئي
- إدارة المخاطر
- إشارات Nagdat

---

### 📂 مجلد utils/

#### `keyboards.py`
**الوظيفة:** جميع أزرار Telegram
```python
# أنواع الأزرار:
- القائمة الرئيسية
- أزرار التداول
- أزرار الصفقات
- أزرار الإعدادات
- لوحة المطور

# مثال:
keyboard = main_menu_keyboard(is_admin=False)
```

#### `formatters.py`
**الوظيفة:** تنسيق الرسائل بشكل احترافي
```python
# الوظائف:
- format_price() → تنسيق الأسعار
- format_profit_loss() → الربح/الخسارة مع الألوان
- format_trade_info() → معلومات الصفقة
- format_ticker_info() → معلومات السعر
- format_nagdat_signal() → تنسيق الإشارة

# مثال:
msg = format_trade_info(trade, current_price)
```

#### `validators.py`
**الوظيفة:** التحقق من صحة المدخلات
```python
# الوظائف:
- validate_symbol() → رمز الزوج
- validate_amount() → المبلغ
- validate_leverage() → الرافعة
- validate_price() → السعر
- validate_api_key() → API Key
- calculate_stop_loss_price()
- calculate_take_profit_price()

# مثال:
is_valid, amount, msg = validate_amount("100")
```

---

## 🔄 تدفق العمل

### 1️⃣ بدء البوت
```
main.py
  ↓
تحميل config.py
  ↓
تهيئة database.py
  ↓
بدء webhook_server.py
  ↓
ربط handlers
  ↓
البوت جاهز! ✅
```

### 2️⃣ معالجة أمر المستخدم
```
مستخدم يضغط زر
  ↓
Telegram يرسل Update
  ↓
main.py يستقبل
  ↓
يوجه إلى المعالج المناسب
  ↓
user_handler أو trading_handler
  ↓
يتفاعل مع database و bybit_api
  ↓
يستخدم keyboards و formatters
  ↓
يرسل الرد للمستخدم
```

### 3️⃣ تنفيذ صفقة
```
مستخدم يختار "شراء"
  ↓
trading_handler.trade_buy()
  ↓
يطلب النوع (Spot/Futures)
  ↓
يطلب الزوج
  ↓
يطلب المبلغ
  ↓
validators.validate_amount()
  ↓
bybit_api.get_ticker() → السعر الحالي
  ↓
عرض ملخص للتأكيد
  ↓
المستخدم يؤكد
  ↓
تنفيذ حسب نوع الحساب:
  • Demo → تحديث database فقط
  • Real → bybit_api.create_order()
  ↓
حفظ في database.create_trade()
  ↓
إرسال تأكيد للمستخدم ✅
```

---

## 🗄️ قاعدة البيانات

### الجداول

#### `users`
```sql
- user_id (PK)
- username
- mode (demo/real)
- demo_balance
- activated_nagdat
- webhook_url
- webhook_token
- api_key (encrypted)
- api_secret (encrypted)
- leverage
- created_at
```

#### `trades`
```sql
- trade_id (PK)
- user_id (FK)
- symbol
- trade_type (spot/futures)
- side (buy/sell)
- leverage
- entry_price
- current_price
- quantity
- stop_loss
- take_profit
- trailing_stop_percent
- status (open/closed)
- profit_loss
- mode (demo/real)
- opened_at
- closed_at
```

#### `signals`
```sql
- signal_id (PK)
- sender_id (FK)
- symbol
- action (buy/sell)
- leverage
- message
- created_at
- executed_count
```

---

## 🌐 API Endpoints (Webhook Server)

### Public Endpoints

#### `GET /health`
```json
Response: {
  "status": "healthy",
  "service": "Bybit Trading Bot"
}
```

#### `POST /webhook/user/<token>`
```json
Request: {
  "token": "user_webhook_token",
  "symbol": "BTC/USDT",
  "action": "buy",
  "leverage": 10,
  "amount": 100
}

Response: {
  "status": "success",
  "message": "Signal received"
}
```

#### `POST /webhook/nagdat`
```json
Request: {
  "secret_key": "NAGDAT-KEY-XXXX",
  "symbol": "BTC/USDT",
  "action": "buy",
  "leverage": 10,
  "message": "Strong signal"
}

Response: {
  "status": "success",
  "signal_id": "uuid",
  "subscribers": 123
}
```

#### `GET /api/stats`
```json
Response: {
  "total_users": 1234,
  "active_users": 567,
  "subscribers": 890,
  "signals_sent": 45
}
```

---

## 🔐 الأمان

### تشفير البيانات
- API Keys مشفرة في قاعدة البيانات
- Webhook tokens فريدة لكل مستخدم (UUID)
- التحقق من صلاحيات المطور

### فصل الصلاحيات
```
المستخدم العادي:
  ✅ التداول (حسابه فقط)
  ✅ الاشتراك في الإشارات
  ✅ Webhook خاص
  ❌ إرسال إشارات عامة
  ❌ إدارة مستخدمين

المطور (Nagdat):
  ✅ كل صلاحيات المستخدم
  ✅ إرسال إشارات لجميع المشتركين
  ✅ عرض إحصائيات كاملة
  ✅ إدارة البوت
  ✅ رسائل جماعية
```

---

## 📊 الأداء

### معدلات التحديث
- **الأسعار**: كل 3 ثواني
- **الصفقات**: لحظي عند التغيير
- **Cache**: 60 ثانية

### الموثوقية
- معالجة أخطاء شاملة
- إعادة محاولة تلقائية
- سجلات مفصلة (logs)
- استعادة من الأخطاء

---

## 🚀 التطوير

### إضافة ميزة جديدة

#### 1. إضافة handler جديد
```python
# في handlers/new_handler.py
class NewHandler:
    @staticmethod
    async def new_feature(update, context):
        # منطق الميزة
        pass
```

#### 2. ربطه في main.py
```python
# في main.py → setup_handlers()
app.add_handler(
    CallbackQueryHandler(
        NewHandler.new_feature,
        pattern="^new_feature$"
    )
)
```

#### 3. إضافة زر في keyboards.py
```python
# في keyboards.py
InlineKeyboardButton(
    "ميزة جديدة",
    callback_data="new_feature"
)
```

### إضافة جدول في قاعدة البيانات
```python
# في database.py → init_database()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY,
        ...
    )
""")
```

---

## 📦 المتطلبات

### المكتبات الأساسية
```
python-telegram-bot==20.7  → Telegram Bot API
ccxt==4.2.25                → Bybit API
flask==3.0.0                → Webhook Server
python-dotenv==1.0.0        → Environment Variables
loguru==0.7.2               → Logging
```

### المتطلبات النظامية
```
Python: 3.9+
RAM: 512 MB (minimum)
Storage: 100 MB
Internet: Always-on connection
```

---

## 🎯 الخلاصة

هيكل المشروع مصمم ليكون:
- ✅ **منظم**: كل شيء في مكانه
- ✅ **قابل للتوسع**: سهل إضافة ميزات
- ✅ **قابل للصيانة**: كود واضح ومفهوم
- ✅ **آمن**: فصل صلاحيات وتشفير
- ✅ **موثوق**: معالجة أخطاء شاملة

---

صُنع بـ ❤️ بواسطة Nagdat

