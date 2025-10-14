# 📡 نظام الإشارات المتقدم - دليل شامل

## 🎯 نظرة عامة

نظام إدارة إشارات التداول المتقدم الذي يدعم جميع أنواع الصفقات (Spot & Futures) مع تتبع كامل للإشارات والصفقات باستخدام معرفات فريدة (Signal IDs).

---

## 📋 أنواع الإشارات المدعومة

### 1️⃣ **BUY** - شراء في السوق الفوري (Spot)

**الوصف:** فتح صفقة شراء في السوق الفوري (Spot Market)

**مثال الإشارة:**
```json
{
  "signal": "buy",
  "symbol": "BTCUSDT"
}
```

**مثال مع TP/SL (اختياري):**
```json
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "take_profit": 46000,
  "stop_loss": 44000
}
```

**ماذا يحدث:**
- ✅ يفتح البوت صفقة شراء Spot
- 💾 يحفظ الصفقة مع `signal_id = "TV_20240115_001"`
- 🔔 يرسل إشعار تيليجرام بتفاصيل الصفقة
- 📊 يربط الصفقة بمعرف الإشارة للمتابعة

**إشعار تيليجرام:**
```
🟢 تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_20240115_001
📊 النوع: BUY
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: SPOT
📋 رقم الأمر: ORD_123456789

✅ الحالة: Order placed: buy BTCUSDT
```

---

### 2️⃣ **SELL** - بيع/إغلاق في السوق الفوري (Spot)

**الوصف:** إغلاق صفقة الشراء المفتوحة في السوق الفوري

**مثال الإشارة:**
```json
{
  "signal": "sell",
  "symbol": "BTCUSDT"
}
```

**ماذا يحدث:**
- 🔍 يبحث البوت عن صفقة Spot مفتوحة لـ BTCUSDT
- ✅ يغلق الصفقة المفتوحة
- 💾 يحدث حالة الصفقة إلى "CLOSED"
- 🔔 يرسل إشعار بالإغلاق

**إشعار تيليجرام:**
```
🔴 تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_20240115_002
📊 النوع: SELL
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: SPOT
📋 رقم الأمر: ORD_123456790

✅ الحالة: Position closed: BTCUSDT
```

---

### 3️⃣ **LONG** - صفقة شراء في العقود المستقبلية (Futures)

**الوصف:** فتح صفقة شراء (LONG) في سوق العقود المستقبلية

**مثال الإشارة:**
```json
{
  "signal": "long",
  "symbol": "BTCUSDT"
}
```

**مثال مع TP/SL (اختياري):**
```json
{
  "signal": "long",
  "symbol": "BTCUSDT",
  "take_profit": 47000,
  "stop_loss": 44000
}
```

**ماذا يحدث:**
- ✅ يفتح البوت صفقة LONG في Futures
- 📈 يستخدم الرافعة المالية المحددة في الإعدادات
- 💾 يحفظ الصفقة مع `signal_id = "TV_LONG_20240115_001"`
- 🔔 يرسل إشعار بتفاصيل الصفقة والرافعة

**إشعار تيليجرام:**
```
📈 تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_LONG_20240115_001
📊 النوع: LONG
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر: FUT_987654321

✅ الحالة: Order placed: long BTCUSDT
```

---

### 4️⃣ **CLOSE_LONG** - إغلاق صفقة LONG

**الوصف:** إغلاق صفقة LONG المفتوحة للرمز المحدد

**مثال الإشارة:**
```json
{
  "signal": "close_long",
  "symbol": "BTCUSDT"
}
```

**ماذا يحدث:**
- 🔍 يبحث البوت عن صفقة LONG مفتوحة بـ `signal_id = "TV_LONG_20240115_001"`
- ✅ يغلق الصفقة المحددة فقط
- 💾 يحدث حالة الصفقة
- 🔔 يرسل إشعار بالإغلاق مع الأرباح/الخسائر

**إذا لم توجد صفقة مفتوحة:**
```
❌ فشل تنفيذ الإشارة

🆔 معرف الإشارة: TV_CLOSE_20240115_001
📊 النوع: CLOSE_LONG
💱 الرمز: BTCUSDT
⚠️ السبب: No open position found for signal: TV_LONG_20240115_001
```

**إشعار نجاح الإغلاق:**
```
✅ تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_CLOSE_20240115_001
📊 النوع: CLOSE_LONG
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر: FUT_987654321
🔒 الأمر المغلق: FUT_987654321

✅ الحالة: Position closed: BTCUSDT
```

---

### 5️⃣ **SHORT** - صفقة بيع في العقود المستقبلية (Futures)

**الوصف:** فتح صفقة بيع (SHORT) في سوق العقود المستقبلية

**مثال الإشارة:**
```json
{
  "signal": "short",
  "symbol": "ETHUSDT"
}
```

**مثال مع TP/SL (اختياري):**
```json
{
  "signal": "short",
  "symbol": "ETHUSDT",
  "take_profit": 2400,
  "stop_loss": 2550
}
```

**ماذا يحدث:**
- ✅ يفتح البوت صفقة SHORT في Futures
- 📉 يستخدم الرافعة المالية المحددة
- 💾 يحفظ الصفقة مع `signal_id = "TV_SHORT_20240115_001"`
- 🔔 يرسل إشعار بتفاصيل الصفقة

**إشعار تيليجرام:**
```
📉 تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_SHORT_20240115_001
📊 النوع: SHORT
💱 الرمز: ETHUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر: FUT_111222333

✅ الحالة: Order placed: short ETHUSDT
```

---

### 6️⃣ **CLOSE_SHORT** - إغلاق صفقة SHORT

**الوصف:** إغلاق صفقة SHORT المفتوحة للرمز المحدد

**مثال الإشارة:**
```json
{
  "signal": "close_short",
  "symbol": "ETHUSDT"
}
```

**ماذا يحدث:**
- 🔍 يبحث البوت عن صفقة SHORT مفتوحة بـ `signal_id = "TV_SHORT_20240115_001"`
- ✅ يغلق الصفقة المحددة فقط
- 💾 يحدث حالة الصفقة
- 🔔 يرسل إشعار بالإغلاق

**إشعار تيليجرام:**
```
✅ تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_CLOSE_20240115_002
📊 النوع: CLOSE_SHORT
💱 الرمز: ETHUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر: FUT_111222333
🔒 الأمر المغلق: FUT_111222333

✅ الحالة: Position closed: ETHUSDT
```

---

## 🔄 سيناريوهات عملية كاملة

### سيناريو 1: تداول Spot كامل

```json
// الخطوة 1: فتح صفقة شراء Spot
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "price": 45000,
  "id": "SPOT_BTC_001"
}

// ✅ يفتح البوت صفقة شراء ويحفظها بـ signal_id = "SPOT_BTC_001"
// 📋 Order ID: ORD_SPOT_123

// الخطوة 2: إغلاق الصفقة
{
  "signal": "sell",
  "symbol": "BTCUSDT",
  "price": 46500,
  "id": "SPOT_BTC_002"
}

// ✅ يغلق البوت صفقة BTCUSDT المفتوحة
// 💰 الربح: +1500 USDT (3.33%)
```

---

### سيناريو 2: تداول Futures LONG كامل

```json
// الخطوة 1: فتح صفقة LONG
{
  "signal": "long",
  "symbol": "ETHUSDT",
  "take_profit": 2600,
  "stop_loss": 2450
}

// ✅ يفتح البوت صفقة LONG بسعر السوق مع رافعة x10
// 📋 Order ID: FUT_LONG_456
// 💰 تم التنفيذ بسعر: 2500 USDT

// الخطوة 2: إغلاق صفقة LONG
{
  "signal": "close_long",
  "symbol": "ETHUSDT"
}

// ✅ يغلق البوت صفقة ETHUSDT LONG المفتوحة بسعر السوق
// 💰 تم التنفيذ بسعر: 2580 USDT
// 💰 الربح: +80 USDT × 10 = +800 USDT (3.2% × 10 = 32%)
```

---

### سيناريو 3: تداول Futures SHORT كامل

```json
// الخطوة 1: فتح صفقة SHORT
{
  "signal": "short",
  "symbol": "BTCUSDT",
  "price": 46000,
  "id": "FUT_BTC_SHORT_001",
  "take_profit": 45000,
  "stop_loss": 46500
}

// ✅ يفتح البوت صفقة SHORT مع رافعة x10
// 📋 Order ID: FUT_SHORT_789

// الخطوة 2: إغلاق صفقة SHORT
{
  "signal": "close_short",
  "symbol": "BTCUSDT",
  "price": 45200,
  "id": "FUT_BTC_CLOSE_001",
  "original_id": "FUT_BTC_SHORT_001"
}

// ✅ يغلق البوت الصفقة المحددة
// 💰 الربح: +800 USDT × 10 = +8000 USDT (1.74% × 10 = 17.4%)
```

---

### سيناريو 4: صفقات متعددة في نفس الوقت

```json
// يمكن فتح عدة صفقات بمعرفات مختلفة
{
  "signal": "long",
  "symbol": "BTCUSDT",
  "price": 45000,
  "id": "MULTI_BTC_001"
}

{
  "signal": "long",
  "symbol": "ETHUSDT",
  "price": 2500,
  "id": "MULTI_ETH_001"
}

{
  "signal": "short",
  "symbol": "BNBUSDT",
  "price": 300,
  "id": "MULTI_BNB_001"
}

// ✅ جميع الصفقات مفتوحة ومتتبعة بمعرفات فريدة

// إغلاق صفقة واحدة فقط
{
  "signal": "close_long",
  "symbol": "ETHUSDT",
  "price": 2580,
  "id": "MULTI_ETH_CLOSE",
  "original_id": "MULTI_ETH_001"
}

// ✅ يغلق صفقة ETH فقط، وتبقى صفقات BTC و BNB مفتوحة
```

---

## ⚠️ حالات خاصة وسلوك النظام

### ❌ إشارة مكررة

```json
// إشارة 1
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "price": 45000,
  "id": "DUP_001"
}
// ✅ تم التنفيذ

// إشارة 2 - نفس الـ ID
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "price": 45100,
  "id": "DUP_001"
}
// ❌ تم التجاهل - إشارة مكررة
```

**إشعار التجاهل:**
```
⚠️ تم تجاهل الإشارة

🆔 معرف الإشارة: DUP_001
السبب: إشارة مكررة (تم استلامها مسبقاً)
```

---

### ❌ إغلاق بدون صفقة مفتوحة

```json
{
  "signal": "close_long",
  "symbol": "BTCUSDT",
  "price": 46000,
  "id": "CLOSE_NO_OPEN",
  "original_id": "NONEXISTENT_ID"
}
// ❌ فشل - لا توجد صفقة بهذا المعرف
```

**إشعار الفشل:**
```
❌ فشل تنفيذ الإشارة

🆔 معرف الإشارة: CLOSE_NO_OPEN
📊 النوع: CLOSE_LONG
💱 الرمز: BTCUSDT
⚠️ السبب: No open position found for signal: NONEXISTENT_ID
```

---

### ⚠️ إشارة بدون ID

```json
// إذا لم يتم إرسال ID
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "price": 45000
}

// ✅ يقوم النظام بتوليد ID تلقائي
// مثال: "20240115123045_buy_BTCUSDT_a1b2c3d4"
```

---

## 🔧 إعداد TradingView

### مثال كود Pine Script لإرسال الإشارات

```pine
//@version=5
strategy("Signal System Example", overlay=true)

// استراتيجية بسيطة
sma20 = ta.sma(close, 20)
sma50 = ta.sma(close, 50)

// شروط الدخول والخروج
longCondition = ta.crossover(sma20, sma50)
shortCondition = ta.crossunder(sma20, sma50)

// متغير لتتبع ID الإشارة
var string currentSignalId = ""

// إشارة LONG
if (longCondition)
    currentSignalId := str.tostring(timestamp)
    alert_message = '{"signal": "long", "symbol": "{{ticker}}", "price": ' + str.tostring(close) + ', "id": "' + currentSignalId + '"}'
    strategy.entry("Long", strategy.long, alert_message=alert_message)

// إشارة CLOSE_LONG
if (shortCondition and strategy.position_size > 0)
    alert_message = '{"signal": "close_long", "symbol": "{{ticker}}", "price": ' + str.tostring(close) + ', "id": "CLOSE_' + currentSignalId + '", "original_id": "' + currentSignalId + '"}'
    strategy.close("Long", alert_message=alert_message)

plot(sma20, "SMA 20", color=color.blue)
plot(sma50, "SMA 50", color=color.red)
```

---

## 📊 هيكل قاعدة البيانات

### جدول الإشارات (signals)

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    signal_id TEXT NOT NULL,           -- معرف الإشارة الفريد
    user_id INTEGER NOT NULL,          -- معرف المستخدم
    signal_type TEXT NOT NULL,         -- buy, sell, long, short, etc.
    symbol TEXT NOT NULL,              -- الرمز (BTCUSDT)
    price REAL,                        -- السعر
    market_type TEXT DEFAULT 'spot',   -- spot أو futures
    status TEXT DEFAULT 'received',    -- received, executed, closed, failed
    received_at TIMESTAMP,             -- وقت الاستلام
    processed_at TIMESTAMP,            -- وقت المعالجة
    order_id TEXT,                     -- معرف الأمر المنفذ
    UNIQUE(signal_id, user_id)         -- منع التكرار
)
```

### جدول الصفقات (orders)

```sql
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    status TEXT DEFAULT 'OPEN',
    signal_id TEXT,                    -- ربط مع الإشارة
    signal_type TEXT,                  -- نوع الإشارة
    market_type TEXT DEFAULT 'spot',   -- نوع السوق
    open_time TIMESTAMP,
    close_time TIMESTAMP
)
```

---

## 🔌 API Endpoints

### استقبال الإشارات

```
POST /personal/{user_id}/webhook
```

**مثال Request:**
```bash
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "signal": "long",
    "symbol": "BTCUSDT",
    "price": 45000,
    "id": "TV_001",
    "take_profit": 46000,
    "stop_loss": 44000
  }'
```

**مثال Response (نجاح):**
```json
{
  "status": "success",
  "message": "Signal processed for user 123456789",
  "user_id": 123456789
}
```

**مثال Response (إشارة مكررة):**
```json
{
  "status": "error",
  "message": "Duplicate signal ignored: TV_001"
}
```

---

## 📱 أمثلة الإشعارات الكاملة

### إشعار فتح صفقة ناجح

```
📈 تم تنفيذ الإشارة بنجاح

🆔 معرف الإشارة: TV_LONG_20240115_001
📊 النوع: LONG
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر: 1234567890
🔢 الكمية: 0.05 BTC
💵 السعر: 45000 USDT
⚖️ الرافعة: 10x
💰 حجم الصفقة: 2250 USDT

✅ الحالة: Order placed: long BTCUSDT
```

### إشعار إغلاق صفقة ناجح

```
✅ تم إغلاق الصفقة بنجاح

🆔 معرف الإشارة: TV_CLOSE_20240115_001
📊 النوع: CLOSE_LONG
💱 الرمز: BTCUSDT
🏦 المنصة: BYBIT
💰 السوق: FUTURES
📋 رقم الأمر الأصلي: 1234567890
🔒 رقم أمر الإغلاق: 1234567891

💵 سعر الدخول: 45000 USDT
💵 سعر الخروج: 46500 USDT
📊 الربح: +1500 USDT (+3.33%)
⚖️ مع الرافعة x10: +15000 USDT (+33.3%)

✅ الحالة: Position closed successfully
```

### إشعار فشل

```
❌ فشل تنفيذ الإشارة

🆔 معرف الإشارة: TV_ERROR_001
📊 النوع: CLOSE_LONG
💱 الرمز: BTCUSDT
⚠️ السبب: No open position found for signal: TV_NONEXIST

ℹ️ تأكد من:
- وجود صفقة مفتوحة بنفس المعرف
- صحة original_id المرسل
- أن الصفقة لم يتم إغلاقها مسبقاً
```

---

## 🧪 اختبار النظام

### اختبار 1: صفقة Spot كاملة

```bash
# 1. فتح صفقة
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"buy","symbol":"BTCUSDT","price":45000,"id":"TEST_SPOT_001"}'

# انتظر الإشعار...

# 2. إغلاق صفقة
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"sell","symbol":"BTCUSDT","price":46000,"id":"TEST_SPOT_002"}'
```

### اختبار 2: صفقة Futures كاملة

```bash
# 1. فتح LONG
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"long","symbol":"ETHUSDT","price":2500,"id":"TEST_LONG_001"}'

# 2. إغلاق LONG
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"close_long","symbol":"ETHUSDT","price":2600,"id":"TEST_CLOSE_001","original_id":"TEST_LONG_001"}'
```

### اختبار 3: إشارة مكررة

```bash
# 1. إشارة أولى
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"buy","symbol":"BTCUSDT","price":45000,"id":"DUP_TEST_001"}'

# 2. إشارة مكررة (سيتم تجاهلها)
curl -X POST https://your-bot.com/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"buy","symbol":"BTCUSDT","price":45100,"id":"DUP_TEST_001"}'

# ستتلقى إشعار بالتجاهل
```

---

## 🔒 الأمان والموثوقية

### ✅ ميزات الأمان

1. **منع التكرار**: كل `signal_id` يتم معالجته مرة واحدة فقط
2. **ربط الصفقات**: كل صفقة مربوطة بإشارة محددة
3. **تتبع كامل**: سجل كامل لجميع الإشارات والصفقات
4. **معالجة الأخطاء**: إشعارات فورية بأي مشاكل
5. **توليد ID تلقائي**: في حال عدم إرسال معرف

### ⚡ معالجة الأخطاء

- ❌ إشارة غير صالحة → تجاهل + إشعار
- ❌ إشارة مكررة → تجاهل + تسجيل
- ❌ صفقة غير موجودة → تجاهل + إشعار
- ❌ فشل التنفيذ → إعادة محاولة + إشعار

---

## 📞 الدعم والمساعدة

### الأخطاء الشائعة

#### 1. "No open position found"
**الحل:** تأكد من:
- وجود صفقة مفتوحة بنفس `original_id`
- أن الرمز (symbol) صحيح
- أن الصفقة لم يتم إغلاقها مسبقاً

#### 2. "Duplicate signal ignored"
**الحل:** استخدم معرف فريد لكل إشارة جديدة

#### 3. "Invalid signal type"
**الحل:** استخدم أحد الأنواع المدعومة:
- buy, sell, long, short, close_long, close_short

---

## 📈 الإحصائيات والتقارير

يمكنك الاستعلام عن إحصائيات الإشارات من خلال:

```python
from database import db_manager

# إحصائيات المستخدم
stats = db_manager.get_signal_stats(user_id=123456789)
print(stats)
# {
#   'total': 150,
#   'by_type': {
#     'buy': 30,
#     'sell': 28,
#     'long': 45,
#     'close_long': 42,
#     'short': 3,
#     'close_short': 2
#   },
#   'by_status': {
#     'executed': 145,
#     'failed': 3,
#     'ignored': 2
#   }
# }
```

---

## 🎓 خلاصة

### ✅ ما تم تنفيذه:

1. ✅ نظام إشارات متقدم يدعم 6 أنواع من الإشارات
2. ✅ تتبع كامل بمعرفات فريدة (Signal IDs)
3. ✅ منع الإشارات المكررة تلقائياً
4. ✅ ربط الصفقات بالإشارات
5. ✅ إشعارات تيليجرام مفصلة لكل عملية
6. ✅ معالجة أخطاء شاملة
7. ✅ دعم Spot و Futures
8. ✅ قاعدة بيانات متقدمة للتتبع

### 🚀 البدء السريع:

1. أرسل إشارة `buy` لفتح صفقة Spot
2. أرسل إشارة `sell` لإغلاقها
3. أرسل إشارة `long` لفتح صفقة Futures
4. أرسل إشارة `close_long` مع `original_id` لإغلاقها

**جميع الإشارات تعمل بنفس المنطق البسيط والواضح! 🎉**

---

**تم إنشاء هذا النظام بواسطة:** Bybit Trading Bot v2.0  
**التحديث الأخير:** يناير 2024  
**الحالة:** ✅ جاهز للإنتاج

