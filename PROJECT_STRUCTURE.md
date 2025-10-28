# 📊 هيكل المشروع - BotByBit

## 📁 نظرة عامة

مشروع بوت تداول متعدد المستخدمين يدعم Bybit و MEXC مع واجهة Telegram و Webhooks من TradingView.

## 🗂️ البنية التنظيمية

### 📂 الملفات الرئيسية

```
botbybit/
├── app.py                          # تطبيق Flask الرئيسي مع Webhooks
├── bybit_trading_bot.py           # البوت الرئيسي (للقراءة فقط - كبير جداً)
├── config.py                      # الإعدادات الرئيسية
├── database.py                    # إدارة قاعدة البيانات SQLite
├── user_manager.py                # إدارة المستخدمين المتعددة
├── developer_manager.py           # إدارة المطورين
├── real_account_manager.py        # إدارة الحسابات الحقيقية
│
├── core/                          # الوحدات الأساسية
│   └── unified_trading_bot.py    # البوت الموحد (غير مستخدم حالياً)
│
├── exchanges/                     # وحدات المنصات
│   └── unified_exchange_manager.py
│
├── enhanced/                      # أنظمة محسنة (تجريبية)
│   └── unified_enhanced_system.py
│
├── trading_bot.db                # قاعدة البيانات (إنتاج)
└── requirements.txt               # التبعيات
```

## 🎯 الميزات الرئيسية

### 1️⃣ نظام المستخدمين المتعددين
- ✅ دعم غير محدود للمستخدمين
- ✅ عزل كامل للحسابات
- ✅ إعدادات مستقلة لكل مستخدم
- ✅ Webhooks شخصية لكل مستخدم

### 2️⃣ أنظمة التداول
#### Demo Mode
- حساب افتراضي ب 10,000 USDT
- تسجيل جميع العمليات
- لا تأثير على المال الحقيقي

#### Real Mode  
- اتصال مباشر مع Bybit API
- صفقات حقيقية على المنصة
- إدارة كاملة للمخاطر

### 3️⃣ أنواع الأسواق
- **Spot**: التداول الفوري
- **Futures**: العقود الآجلة مع رافعة مالية

### 4️⃣ إدارة الإشارات
- استقبال من TradingView Webhooks
- معالجة إشارات Buy/Sell
- ربط الإشارات بنفس ID (لدعم الإغلاق الذكي)
- Exit signals للخروج من الصفقات

### 5️⃣ إدارة المخاطر
- ✅ Take Profit متعدد المستويات
- ✅ Stop Loss مع Trailing
- ✅ إغلاق جزئي (25%, 50%, 25%)
- ✅ رفع SL إلى Breakeven بعد تحقيق TP1

### 6️⃣ نظام المطورين
- مطورون يرسلون إشارات لتابعيهم
- صلاحيات خاصة
- توزيع إشارات تلقائي

## 🔄 سير العمل

### تسجيل مستخدم جديد
1. المستخدم يضغط `/start` في Telegram
2. يتم إنشاء حساب demo افتراضي
3. يمكن إضافة API Keys للحساب الحقيقي

### معالجة إشارة
1. TradingView يرسل Webhook
2. النظام يتحقق من وجود الرمز
3. قراءة إعدادات المستخدم
4. تنفيذ الصفقة (Demo/Real)
5. إنشاء تذكيرات TP/SL
6. تحديث الأسعار كل 30 ثانية

### إدارة الإشارات
- كل إشارة لها **signal_id** فريد
- إشارات متعددة لنفس الرمز تفتح صفقات منفصلة
- إشارة Exit تغلق الصفقة المرتبطة بنفس ID
- دعم الإغلاق الجزئي

## 🗄️ قاعدة البيانات

### جدول users
```sql
- user_id (PRIMARY KEY)
- is_active (BOOLEAN)
- balance (REAL)
- bybit_api_key (TEXT)
- bybit_api_secret (TEXT)
- mexc_api_key (TEXT)
- mexc_api_secret (TEXT)
- account_type (demo/real)
- market_type (spot/futures)
- trade_amount (REAL)
- leverage (INTEGER)
- partial_percents (JSON)
- tps_percents (JSON)
- risk_management (JSON)
```

### جدول orders
```sql
- order_id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- symbol (TEXT)
- side (buy/sell)
- entry_price (REAL)
- quantity (REAL)
- status (OPEN/CLOSED)
- open_time, close_time
- tps (JSON array)
- sl (REAL)
- partial_close (JSON array)
```

### جدول developers
```sql
- developer_id (PRIMARY KEY)
- developer_name (TEXT)
- webhook_url (TEXT)
- is_active (BOOLEAN)
- can_broadcast (BOOLEAN)
- auto_broadcast (BOOLEAN)
```

### جدول developer_followers
```sql
- developer_id (FOREIGN KEY)
- user_id (FOREIGN KEY)
- UNIQUE(developer_id, user_id)
```

### جدول signal_positions
```sql
- signal_id (TEXT)        # للربط بين الإشارات والصفقات
- user_id (FOREIGN KEY)
- symbol (TEXT)
- side (buy/sell)
- entry_price (REAL)
- status (OPEN/CLOSED)
- exchange, market_type
```

## 🔧 الوحدات الرئيسية

### app.py
- Flask application
- Route: `/webhook` - استقبال عام
- Route: `/personal/<user_id>/webhook` - استقبال شخصي
- بدء البوت Telegram
- إدارة النظام العام

### bybit_trading_bot.py
- المعالج الرئيسي للإشارات
- تنفيذ الصفقات Demo/Real
- إدارة PositionManager
- تحديث الأسعار
- حساب TP/SL

### user_manager.py
- تحميل بيانات المستخدمين
- إنشاء حسابات demo لكل مستخدم
- إدارة API Keys
- عزل بيانات كل مستخدم

### database.py
- إدارة SQLite
- CRUD operations
- إدارة الصفقات والتاريخ
- إحصائيات المستخدمين

## 🔐 الأمان

### API Keys
- يتم تخزينها في قاعدة البيانات
- استخدام HMAC للتوقيع
- حماية من أخطاء API

### التحقق
- التحقق من المستخدم قبل تنفيذ الصفقة
- التحقق من الرصيد
- التحقق من صلاحية الرمز

## 📈 الإحصائيات

### للمستخدم
- عدد الصفقات المفتوحة
- إجمالي الربح/الخسارة
- تاريخ الصفقات
- رصيد الحساب

### للنظام
- عدد المستخدمين النشطين
- الصفقات المنفذة
- الإشارات المستلمة
- معدل النجاح

## 🚀 النشر

### Railway
- `railway.yaml` - إعدادات النشر
- `railway_start.sh` - سكريبت البدء

### Render
- `render.yaml` - إعدادات النشر

## ⚠️ ملاحظات

### ملفات مكررة أو قديمة
- `core/unified_trading_bot.py` - غير مستخدم
- `enhanced/unified_enhanced_system.py` - تجريبي
- عدة ملفات debug/check يمكن حذفها

### تحسينات مستقبلية
1. إعادة هيكلة الكود
2. إضافة نظام permissions متقدم
3. دعم منصات إضافية
4. واجهة web dashboard
5. نظام notifications متقدم

## 📞 الدعم

- Telegram Bot: `@YourBot`
- Email: support@example.com
- Documentation: [Link]

