# 🔗 دليل استخدام Webhook للإشارات

## 📋 نظرة عامة

هذا الدليل يشرح كيفية ربط TradingView أو أي منصة إشارات مع البوت باستخدام Webhook.

---

## 🎯 ما هو Webhook؟

**Webhook** هو رابط URL خاص يستقبل الإشارات من المنصات الخارجية (مثل TradingView) ويرسلها مباشرة للبوت لتنفيذها تلقائياً.

### المميزات:
- ✅ تنفيذ تلقائي للإشارات
- ✅ سرعة عالية (أقل من ثانية)
- ✅ آمن ومشفر
- ✅ مخصص لكل مستخدم

---

## 🔗 الحصول على رابط Webhook

### في البوت:
1. افتح البوت في Telegram
2. اضغط على "🔗 رابط الإشارات"
3. انسخ الرابط الشخصي الخاص بك

### شكل الرابط:
```
https://your-domain.com/personal/YOUR_USER_ID/webhook
```

---

## 📱 الإعداد في TradingView

### الخطوة 1: إنشاء Alert

1. افتح الشارت في TradingView
2. اضغط على زر "Alert" (🔔) في الأعلى
3. أو اضغط على `Alt+A`

### الخطوة 2: إعداد الشروط

1. اختر الشرط المناسب لاستراتيجيتك:
   - Price crossing
   - Indicator condition
   - Strategy order fills
   - أو أي شرط آخر

### الخطوة 3: إضافة Webhook

1. في قسم "Notifications"
2. ضع علامة ✅ على "Webhook URL"
3. الصق رابط Webhook الخاص بك

### الخطوة 4: كتابة رسالة الإشارة

في حقل "Alert message"، استخدم صيغة JSON:

---

## 📋 صيغة الإشارات

### الصيغة الأساسية

```json
{
  "signal": "نوع_الإشارة",
  "symbol": "رمز_العملة",
  "id": "معرف_فريد"
}
```

### أمثلة عملية

#### 1. إشارة شراء (Buy)
```json
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "id": "STRATEGY_BUY_001"
}
```

#### 2. إشارة بيع (Sell)
```json
{
  "signal": "sell",
  "symbol": "ETHUSDT",
  "id": "STRATEGY_SELL_001"
}
```

#### 3. إشارة إغلاق كامل
```json
{
  "signal": "close",
  "symbol": "BTCUSDT",
  "id": "STRATEGY_CLOSE_001"
}
```

#### 4. إشارة إغلاق جزئي (50%)
```json
{
  "signal": "partial_close",
  "symbol": "BTCUSDT",
  "percentage": 50,
  "id": "STRATEGY_PC_001"
}
```

#### 5. إشارة Long (Futures)
```json
{
  "signal": "long",
  "symbol": "BTCUSDT",
  "id": "STRATEGY_LONG_001"
}
```

#### 6. إشارة Short (Futures)
```json
{
  "signal": "short",
  "symbol": "ETHUSDT",
  "id": "STRATEGY_SHORT_001"
}
```

---

## 🔤 أنواع الإشارات المدعومة

| الإشارة | الوصف | السوق |
|---------|-------|-------|
| `buy` | فتح صفقة شراء | Spot/Futures |
| `sell` | فتح صفقة بيع | Spot/Futures |
| `long` | فتح صفقة شراء | Futures |
| `short` | فتح صفقة بيع | Futures |
| `close` | إغلاق الصفقة بالكامل | Spot/Futures |
| `partial_close` | إغلاق جزئي (مع percentage) | Spot/Futures |

---

## 🎲 استخدام المتغيرات في TradingView

يمكنك استخدام متغيرات TradingView الديناميكية:

```json
{
  "signal": "buy",
  "symbol": "{{ticker}}",
  "price": "{{close}}",
  "id": "STRATEGY_{{time}}"
}
```

### المتغيرات المتاحة:
- `{{ticker}}` - رمز العملة الحالي
- `{{close}}` - سعر الإغلاق
- `{{open}}` - سعر الافتتاح
- `{{high}}` - أعلى سعر
- `{{low}}` - أدنى سعر
- `{{time}}` - الوقت الحالي
- `{{exchange}}` - المنصة

---

## 🆔 أهمية معرف ID

### لماذا نستخدم ID؟

معرف `id` يربط عدة إشارات معاً للصفقة الواحدة:

```json
// فتح صفقة
{"signal": "buy", "symbol": "BTCUSDT", "id": "STRAT_001"}

// إضافة لنفس الصفقة
{"signal": "buy", "symbol": "BTCUSDT", "id": "STRAT_001"}

// إغلاق جزئي لنفس الصفقة
{"signal": "partial_close", "symbol": "BTCUSDT", "percentage": 50, "id": "STRAT_001"}

// إغلاق كامل لنفس الصفقة
{"signal": "close", "symbol": "BTCUSDT", "id": "STRAT_001"}
```

### بدون ID:
كل إشارة تُعتبر صفقة منفصلة.

---

## ⚙️ الإعدادات التلقائية

عند استقبال الإشارة، يستخدم البوت إعداداتك تلقائياً:

### المبلغ:
يُحدد من إعدادات "💰 مبلغ التداول"

### نوع السوق:
يُحدد من "🏪 نوع السوق" (Spot/Futures)

### الرافعة المالية:
تُطبق تلقائياً للـ Futures

### نوع الحساب:
Demo أو Real حسب إعداداتك

---

## 🔍 اختبار الإشارات

### اختبار يدوي

استخدم `curl` أو Postman:

```bash
curl -X POST https://your-domain.com/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "signal": "buy",
    "symbol": "BTCUSDT",
    "id": "TEST_001"
  }'
```

### التحقق من الاستجابة

**نجاح:**
```json
{
  "status": "success",
  "message": "Signal processing started for user YOUR_USER_ID",
  "user_id": YOUR_USER_ID
}
```

**فشل:**
```json
{
  "status": "error",
  "message": "وصف الخطأ"
}
```

---

## ⚠️ الأخطاء الشائعة وحلولها

### 1. "User not found"
**السبب:** المستخدم غير مسجل في البوت  
**الحل:** أرسل `/start` في البوت أولاً

### 2. "User not active"
**السبب:** البوت متوقف  
**الحل:** فعّل البوت من "▶️/⏹️ تشغيل/إيقاف البوت"

### 3. "No data received"
**السبب:** صيغة JSON خاطئة  
**الحل:** تأكد من صحة صيغة JSON (استخدم JSON validator)

### 4. "Invalid signal type"
**السبب:** نوع إشارة غير مدعوم  
**الحل:** استخدم أحد الأنواع المدعومة (buy, sell, close, ...)

### 5. الإشارة لا تصل
**الحلول:**
- تحقق من رابط Webhook
- تأكد من تفعيل البوت
- راجع سجلات TradingView
- اختبر الرابط يدوياً

---

## 🔒 الأمان

### نصائح الأمان:

1. **لا تشارك رابط Webhook**
   - الرابط خاص بك فقط
   - أي شخص لديه الرابط يمكنه إرسال إشارات

2. **استخدم HTTPS**
   - تأكد أن الرابط يبدأ بـ `https://`
   - للحماية من التنصت

3. **راقب النشاط**
   - راجع الصفقات بانتظام
   - تحقق من السجلات (`trading_bot.log`)

4. **ابدأ بالحساب التجريبي**
   - اختبر الإشارات أولاً
   - تأكد من صحة التنفيذ
   - ثم انتقل للحساب الحقيقي

---

## 📊 مثال استراتيجية كاملة

### في TradingView:

```javascript
//@version=5
strategy("My Strategy", overlay=true)

// شروط الدخول
longCondition = ta.crossover(ta.sma(close, 10), ta.sma(close, 20))
shortCondition = ta.crossunder(ta.sma(close, 10), ta.sma(close, 20))

// تنفيذ
if (longCondition)
    strategy.entry("Long", strategy.long, alert_message='{"signal":"buy","symbol":"BTCUSDT","id":"STRAT_MAIN"}')

if (shortCondition)
    strategy.entry("Short", strategy.short, alert_message='{"signal":"sell","symbol":"BTCUSDT","id":"STRAT_MAIN"}')

// إغلاق عند الربح
if (strategy.position_size > 0 and close > strategy.position_avg_price * 1.02)
    strategy.close("Long", alert_message='{"signal":"close","symbol":"BTCUSDT","id":"STRAT_MAIN"}')
```

---

## 🎓 نصائح متقدمة

### 1. استخدام إشارات متعددة
```json
// إشارة 1: فتح صفقة
{"signal": "buy", "symbol": "BTCUSDT", "id": "MAIN"}

// إشارة 2: إضافة للصفقة (DCA)
{"signal": "buy", "symbol": "BTCUSDT", "id": "MAIN"}

// إشارة 3: إغلاق جزئي عند هدف
{"signal": "partial_close", "symbol": "BTCUSDT", "percentage": 50, "id": "MAIN"}
```

### 2. صفقات منفصلة
استخدم IDs مختلفة:
```json
{"signal": "buy", "symbol": "BTCUSDT", "id": "STRATEGY_A"}
{"signal": "buy", "symbol": "ETHUSDT", "id": "STRATEGY_B"}
```

### 3. إدارة المخاطر
- حدد Stop Loss في إعدادات البوت
- استخدم إغلاق جزئي للتأمين
- راقب الخسائر اليومية

---

## 📞 الدعم

### في حالة وجود مشاكل:

1. راجع `trading_bot.log` للأخطاء
2. اختبر الرابط يدوياً
3. تحقق من الإعدادات
4. استخدم `/help` في البوت

---

## ✅ نقاط التحقق النهائية

قبل البدء، تأكد من:

- [ ] تم نسخ رابط Webhook الصحيح
- [ ] تم إضافة الرابط في TradingView
- [ ] صيغة JSON صحيحة
- [ ] البوت مفعّل (▶️)
- [ ] تم اختبار إشارة تجريبية
- [ ] الإعدادات صحيحة (المبلغ، السوق، الحساب)
- [ ] تم تفعيل Stop Loss (موصى به)

---

**🎉 الآن أنت جاهز للتداول الآلي!**

**ملاحظة أخيرة:** ابدأ دائماً بمبالغ صغيرة والحساب التجريبي.

---

**آخر تحديث**: 2025-10-28  
**الإصدار**: 3.0.0

