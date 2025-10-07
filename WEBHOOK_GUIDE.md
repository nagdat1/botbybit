# 📡 دليل استخدام Webhook - نظام الروابط الشخصية

## 🎯 نظرة عامة

تم تحديث البوت ليدعم نوعين من روابط Webhook:

### 1️⃣ الرابط القديم (Global Webhook)
يستخدم الإعدادات الافتراضية للبوت
```
https://botbybit-production.up.railway.app/webhook
```

### 2️⃣ الروابط الشخصية (Personal Webhooks) ✨ جديد
لكل مستخدم رابط خاص يستخدم إعداداته الشخصية
```
https://botbybit-production.up.railway.app/personal/<user_id>/webhook
```

---

## 📊 كيفية الاستخدام

### الرابط القديم `/webhook`
- يعمل كما كان سابقًا
- يستخدم الإعدادات الافتراضية من `config.py`
- مناسب للمستخدم الأساسي أو للاختبار

**مثال:**
```bash
curl -X POST https://botbybit-production.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "action": "buy",
    "price": 50000
  }'
```

### الرابط الشخصي `/personal/<user_id>/webhook`
- يستخدم إعدادات المستخدم المحددة من قاعدة البيانات
- يدعم تعدد المستخدمين
- كل مستخدم لديه:
  - إعدادات خاصة (market_type, account_type, trade_amount, leverage)
  - صفقات مستقلة
  - رصيد منفصل

**مثال للمستخدم 123456789:**
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ETHUSDT",
    "action": "buy",
    "price": 3000
  }'
```

---

## 📝 صيغة الإشارات المدعومة

### إشارات الشراء/البيع
```json
{
  "symbol": "BTCUSDT",
  "action": "buy",      // أو "sell", "long", "short"
  "price": 50000        // اختياري - إذا لم يحدد، يستخدم السعر الحالي
}
```

### إشارات الإغلاق
```json
{
  "symbol": "BTCUSDT",
  "action": "close",    // أو "exit", "stop"
  "price": 51000        // اختياري
}
```

---

## ⚙️ إعدادات المستخدم في قاعدة البيانات

كل مستخدم يحتاج إلى السجل التالي في قاعدة البيانات:

```sql
-- جدول users
user_id              INTEGER    -- معرف المستخدم في Telegram
api_key              TEXT       -- مفتاح API من Bybit (اختياري)
api_secret           TEXT       -- سر API من Bybit (اختياري)
balance              REAL       -- الرصيد الحالي
is_active            BOOLEAN    -- حالة التفعيل
notifications        BOOLEAN    -- تفعيل الإشعارات

-- جدول user_settings
market_type          TEXT       -- "spot" أو "futures"
trade_amount         REAL       -- مبلغ التداول الافتراضي
leverage             INTEGER    -- الرافعة المالية (للفيوتشر)
account_type         TEXT       -- "demo" أو "real"
```

---

## 🔍 Debug Logs

تم إضافة رسائل debug مفصلة لتتبع كل عملية:

### عند استقبال الإشارة:
```
🔔 [WEBHOOK شخصي] المستخدم: 123456789
📊 [WEBHOOK شخصي] البيانات المستلمة: {"symbol": "BTCUSDT", "action": "buy"}
✅ [WEBHOOK شخصي] المستخدم 123456789 موجود ونشط
📋 [WEBHOOK شخصي] إعدادات المستخدم: market_type=futures, account_type=demo
```

### عند معالجة الصفقة:
```
🔄 [معالجة الإشارة] بدء معالجة إشارة المستخدم 123456789
📈 [معالجة الإشارة] الرمز: BTCUSDT, الإجراء: buy, السعر: 50000
⚙️ [معالجة الإشارة] الإعدادات: market=futures, account=demo, amount=100.0, leverage=10
📝 [معالجة الإشارة] فتح صفقة buy للمستخدم 123456789
✅ [معالجة الإشارة] نجح فتح الصفقة للمستخدم 123456789
```

### عند وجود خطأ:
```
⚠️ [WEBHOOK شخصي] المستخدم 123456789 غير موجود في قاعدة البيانات
⚠️ [WEBHOOK شخصي] المستخدم 123456789 غير نشط
❌ [معالجة الإشارة] بيانات غير مكتملة للمستخدم 123456789
```

---

## 🔐 التحقق من الأمان

### التحقق من وجود المستخدم:
```python
user_data = user_manager.get_user(user_id)
if not user_data:
    return {"status": "error", "message": "User not found"}, 404
```

### التحقق من تفعيل المستخدم:
```python
if not user_data.get('is_active', False):
    return {"status": "error", "message": "User is not active"}, 403
```

---

## 🛠️ إعداد المستخدمين

### إنشاء مستخدم جديد عبر Telegram:
1. المستخدم يرسل `/start` للبوت
2. البوت يقوم بإنشاء سجل جديد في قاعدة البيانات تلقائيًا
3. يتم تخصيص إعدادات افتراضية للمستخدم

### إنشاء مستخدم يدويًا في قاعدة البيانات:
```python
from database import db_manager

# إنشاء مستخدم جديد
db_manager.create_user(
    user_id=123456789,
    api_key="YOUR_API_KEY",      # اختياري
    api_secret="YOUR_API_SECRET"  # اختياري
)

# تحديث إعدادات المستخدم
db_manager.update_user_settings(
    user_id=123456789,
    settings={
        'market_type': 'futures',
        'trade_amount': 100.0,
        'leverage': 10,
        'account_type': 'demo',
        'partial_percents': [25, 50, 25],
        'tps_percents': [1.5, 3.0, 5.0],
        'notifications': True
    }
)
```

---

## 📈 أمثلة استخدام من TradingView

### إعداد Webhook في TradingView:

**للرابط القديم:**
```
URL: https://botbybit-production.up.railway.app/webhook
Message:
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "price": {{close}}
}
```

**للرابط الشخصي:**
```
URL: https://botbybit-production.up.railway.app/personal/123456789/webhook
Message:
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "price": {{close}}
}
```

---

## 🎯 الميزات الجديدة

✅ **دعم المستخدمين المتعددين**: كل مستخدم لديه إعدادات وصفقات مستقلة  
✅ **روابط شخصية**: رابط فريد لكل مستخدم  
✅ **Debug متقدم**: رسائل واضحة لتتبع كل عملية  
✅ **إشعارات Telegram**: يتلقى كل مستخدم إشعارات خاصة به  
✅ **الحماية**: التحقق من وجود وتفعيل المستخدم  
✅ **دعم جميع أنواع الإشارات**: buy, sell, long, short, close, exit, stop  
✅ **معالجة متزامنة**: يمكن استقبال عدة إشارات في نفس الوقت  

---

## 🔧 استكشاف الأخطاء

### إذا لم يعمل الرابط الشخصي:

1. **تحقق من وجود المستخدم:**
   ```python
   from database import db_manager
   user = db_manager.get_user(123456789)
   print(user)
   ```

2. **تحقق من تفعيل المستخدم:**
   ```python
   if user and user.get('is_active'):
       print("المستخدم نشط ✅")
   else:
       print("المستخدم غير نشط ❌")
   ```

3. **تحقق من logs السيرفر:**
   - ابحث عن رسائل تبدأ بـ `[WEBHOOK شخصي]`
   - تحقق من وجود أخطاء

4. **اختبر الرابط:**
   ```bash
   curl -X POST https://botbybit-production.up.railway.app/personal/<user_id>/webhook \
     -H "Content-Type: application/json" \
     -d '{"symbol": "BTCUSDT", "action": "buy", "price": 50000}'
   ```

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. راجع logs السيرفر
2. تحقق من إعدادات المستخدم في قاعدة البيانات
3. تأكد من صحة صيغة JSON المرسلة
4. تحقق من أن user_manager تم تهيئته بشكل صحيح

---

## 🎉 خلاصة

الآن لديك نظام webhook متقدم يدعم:
- ✅ الرابط القديم للتوافق مع الإصدار السابق
- ✅ روابط شخصية لكل مستخدم
- ✅ إعدادات منفصلة لكل مستخدم
- ✅ debug متقدم لسهولة التتبع
- ✅ أمان محسّن مع التحقق من المستخدمين

**استمتع بالتداول! 🚀**

