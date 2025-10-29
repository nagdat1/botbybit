# 🔄 تدفق معالجة الإشارات

## 📊 البنية الحالية

### 1. نقطة الدخول (Entry Point)
```
📥 TradingView → Webhook Endpoint
```

**الملفات المسؤولة:**
- `app.py` - `/webhook` و `/personal/<user_id>/webhook`
- `web_server.py` - `/webhook` و `/personal/<user_id>/webhook`

### 2. استقبال ومعالجة الإشارة
```python
# في app.py
from signals.signal_converter import convert_simple_signal
from signals.signal_executor import signal_executor
```

**الخطوات:**
1. استقبال JSON من TradingView
2. التحقق من صحة البيانات
3. تحويل الإشارة إلى التنسيق الداخلي
4. تنفيذ الإشارة

### 3. تحويل الإشارة (Signal Conversion)
```
signals/signal_converter.py
```

**الدوال الرئيسية:**
- `convert_simple_signal()` - تحويل الإشارة البسيطة
- `validate_simple_signal()` - التحقق من صحة الإشارة

**التحويلات:**
- `buy` → `action: 'buy'`
- `sell` → `action: 'sell'`
- `long` → `action: 'buy'`
- `close` → `action: 'close'`
- `partial_close` → `action: 'partial_close'`

### 4. تنفيذ الإشارة (Signal Execution)
```
signals/signal_executor.py
```

**الدالة الرئيسية:**
```python
signal_executor.execute_signal(user_id, signal_data, user_data)
```

**المهام:**
- فحص نوع الحساب (demo/real)
- جلب السعر من API
- حساب الكمية
- تنفيذ الأمر على Bybit
- حفظ الصفقة في قاعدة البيانات
- إرسال إشعار للمستخدم

### 5. إدارة الصفقات المرتبطة بـ ID
```
signals/signal_position_manager.py
```

**المهام:**
- ربط الصفقات بـ ID الإشارة
- تتبع الصفقات المفتوحة
- إغلاق الصفقات المرتبطة
- الإغلاق الجزئي

### 6. إدارة ID الإشارات
```
signals/signal_id_manager.py
```

**المهام:**
- توليد ID عشوائي للإشارات
- ربط ID الإشارة برقم الصفقة
- تتبع الصفقات المرتبطة بـ ID

## 🔗 تدفق العمل الكامل

```
1. TradingView يرسل إشارة
   ↓
2. app.py يستقبل الإشارة عبر webhook
   ↓
3. signal_converter يتحقق ويحول الإشارة
   ↓
4. user_manager يجلب بيانات المستخدم
   ↓
5. signal_executor ينفذ الإشارة على Bybit
   ↓
6. signal_position_manager يحفظ الصفقة
   ↓
7. إرسال إشعار للمستخدم في Telegram
```

## 📝 أمثلة الإشارات المدعومة

### إشارة شراء
```json
{
  "signal": "buy",
  "symbol": "BTCUSDT",
  "id": "STRATEGY_001"
}
```

### إشارة بيع
```json
{
  "signal": "sell",
  "symbol": "ETHUSDT",
  "id": "STRATEGY_002"
}
```

### إشارة إغلاق
```json
{
  "signal": "close",
  "symbol": "BTCUSDT",
  "id": "STRATEGY_001"
}
```

### إغلاق جزئي
```json
{
  "signal": "partial_close",
  "symbol": "BTCUSDT",
  "percentage": 50,
  "id": "STRATEGY_001"
}
```

## ⚙️ الإصلاحات المطبقة

### 1. إصلاح مسارات الاستيراد
```python
# قبل:
from signal_converter import convert_simple_signal

# بعد:
from signals.signal_converter import convert_simple_signal
```

### 2. الملفات المعدلة
- ✅ `web_server.py` - تم إصلاح الاستيرادات
- ✅ `bybit_trading_bot.py` - تم إصلاح الاستيرادات
- ✅ `app.py` - بالفعل صحيح

## 🧪 كيفية الاختبار

### اختبار يدوي
```bash
curl -X POST https://your-domain.com/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "signal": "buy",
    "symbol": "BTCUSDT",
    "id": "TEST_001"
  }'
```

### متطلبات:
1. البوت مشغل (✓)
2. المستخدم مسجل (✓)
3. المستخدم مفعّل (✓)
4. الإشارة بصيغة JSON صحيحة (✓)
5. المسارات محدثة (✓)

## 🔍 التحقق من استقبال الإشارات

### في السجلات (Logs)
```
🔔 [WEBHOOK شخصي] استقبال طلب جديد
👤 المستخدم: 123456
📊 البيانات المستلمة: {...}
✅ تم تحويل الإشارة: buy BTCUSDT
✅ نتيجة التنفيذ: {...}
```

### في Telegram
```
✅ تم تنفيذ إشارة بنجاح

🎯 الإجراء: buy
💎 الرمز: BTCUSDT
💰 المبلغ: 100.0 USDT
📊 نوع السوق: spot
🏦 نوع الحساب: real
```

## 📌 ملاحظات مهمة

1. **تأكد من أن المستخدم مسجل**: `/start` في البوت
2. **تأكد من تفعيل البوت**: اضغط ▶️ في البوت
3. **راجع السجلات**: `trading_bot.log`
4. **اختبر الإشارات**: استخدم curl أو Postman
5. **تحقق من النتائج**: راجع الصفقات في البوت

