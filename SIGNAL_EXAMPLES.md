# 📡 أمثلة على صيغة الإشارات

## ✅ الصيغة البسيطة (الموصى بها)

### مثال 1: شراء BTC
```json
{
  "symbol": "BTCUSDT",
  "action": "buy"
}
```

### مثال 2: بيع ETH
```json
{
  "symbol": "ETHUSDT",
  "action": "sell"
}
```

### مثال 3: فتح صفقة Long (شراء)
```json
{
  "symbol": "BNBUSDT",
  "action": "long"
}
```

### مثال 4: فتح صفقة Short (بيع)
```json
{
  "symbol": "ADAUSDT",
  "action": "short"
}
```

### مثال 5: إغلاق صفقة BTC
```json
{
  "symbol": "BTCUSDT",
  "action": "close"
}
```

### مثال 6: إغلاق جميع صفقات ETH
```json
{
  "symbol": "ETHUSDT",
  "action": "exit"
}
```

---

## 📋 الصيغة مع السعر (اختياري)

إذا أردت تحديد السعر بنفسك:

### مثال 1: شراء BTC بسعر محدد
```json
{
  "symbol": "BTCUSDT",
  "action": "buy",
  "price": 50000
}
```

### مثال 2: بيع ETH بسعر محدد
```json
{
  "symbol": "ETHUSDT",
  "action": "sell",
  "price": 3000
}
```

### مثال 3: إغلاق بسعر محدد
```json
{
  "symbol": "BTCUSDT",
  "action": "close",
  "price": 51000
}
```

---

## 🔧 إعداد TradingView

### الصيغة البسيطة (بدون سعر):
```
URL: https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook

Message:
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}"
}
```

### الصيغة مع السعر:
```
URL: https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook

Message:
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "price": {{close}}
}
```

---

## 🎯 الإجراءات المدعومة

| الإجراء | الوصف | مثال |
|---------|--------|------|
| `buy` | شراء / فتح صفقة Long | `{"symbol": "BTCUSDT", "action": "buy"}` |
| `sell` | بيع / فتح صفقة Short | `{"symbol": "BTCUSDT", "action": "sell"}` |
| `long` | مثل buy - فتح صفقة شراء | `{"symbol": "ETHUSDT", "action": "long"}` |
| `short` | مثل sell - فتح صفقة بيع | `{"symbol": "ETHUSDT", "action": "short"}` |
| `close` | إغلاق الصفقة | `{"symbol": "BTCUSDT", "action": "close"}` |
| `exit` | مثل close - إغلاق | `{"symbol": "BTCUSDT", "action": "exit"}` |
| `stop` | مثل close - إغلاق | `{"symbol": "BTCUSDT", "action": "stop"}` |

---

## 💡 ملاحظات مهمة

### حول السعر:
- ✅ **إذا لم تحدد السعر**: البوت سيستخدم السعر الحالي من السوق تلقائيًا
- ✅ **إذا حددت السعر**: سيتم استخدام السعر الذي حددته
- ✅ **السعر = 0 أو null**: سيُعامل كأنك لم تحدد السعر ويستخدم السعر الحالي

### حول الرمز (Symbol):
- يجب أن يكون بصيغة مثل: `BTCUSDT`, `ETHUSDT`, `BNBUSDT`
- يمكنك استخدام أي زوج متداول على Bybit

### حول الإجراء (Action):
- غير حساس لحالة الأحرف (buy = BUY = Buy)
- `long` و `buy` لهما نفس التأثير
- `short` و `sell` لهما نفس التأثير
- `close`, `exit`, `stop` كلها تغلق الصفقة

---

## 🧪 اختبار الإشارة

### اختبار عبر Curl:

**صيغة بسيطة:**
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

**صيغة مع السعر:**
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy", "price": 50000}'
```

### النتيجة المتوقعة:
```json
{
  "status": "success",
  "message": "Signal processed for user YOUR_USER_ID",
  "user_id": YOUR_USER_ID
}
```

---

## ✅ الخلاصة

**الصيغة الموصى بها:**
```json
{
  "symbol": "BTCUSDT",
  "action": "buy"
}
```

**بسيطة، واضحة، وتعمل بشكل مثالي! 🚀**

- لا حاجة لتحديد السعر
- البوت يستخدم السعر الحالي تلقائيًا
- أقل احتمالية للأخطاء
- سهلة الإعداد في TradingView

