# 🧪 دليل الاختبار السريع

## اختبار عزل حسابات المستخدمين

### 1️⃣ اختبار مستخدمين مختلفين

قم بإرسال إشارات من مستخدمين مختلفين:

```bash
# المستخدم الأول (ID: 111)
curl -X POST http://localhost:5000/personal/111/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'

# المستخدم الثاني (ID: 222)
curl -X POST http://localhost:5000/personal/222/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSDT", "action": "buy"}'
```

**✅ النتيجة المتوقعة:**
- المستخدم 111 يستقبل رسالة عن صفقة BTCUSDT
- المستخدم 222 يستقبل رسالة عن صفقة ETHUSDT
- كل رسالة تحتوي على معرّف المستخدم الخاص بها

### 2️⃣ اختبار نفس المستخدم، عدة إشارات

```bash
# الإشارة الأولى
curl -X POST http://localhost:5000/personal/123/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'

# الإشارة الثانية
curl -X POST http://localhost:5000/personal/123/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSDT", "action": "buy"}'
```

**✅ النتيجة المتوقعة:**
- المستخدم 123 يستقبل رسالتين
- كلا الصفقتين على حساب المستخدم 123
- الرصيد يُخصم من حساب واحد فقط

### 3️⃣ التحقق من الرسائل

كل رسالة يجب أن تحتوي على:
```
📈 تم فتح صفقة ... تجريبية
👤 المستخدم: 123456789  ← معرّف المستخدم
📊 الرمز: BTCUSDT
🔄 النوع: BUY
💰 المبلغ: 100.0
...
```

### 4️⃣ فحص السجلات (Logs)

ابحث عن:
```
✅ استخدام حساب المستخدم 123 لنوع السوق spot
✅ تم فتح صفقة سبوت: ID=xxx, الرمز=BTCUSDT, user_id=123
```

## اختبار على Railway

```bash
# استبدل YOUR_USER_ID بمعرّفك من تلجرام
curl -X POST https://your-app.railway.app/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

## إعداد TradingView

في إعدادات Alert في TradingView:

**Webhook URL:**
```
https://your-app.railway.app/personal/YOUR_USER_ID/webhook
```

**Message:**
```json
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}"
}
```

## التحقق من العزل

1. **افتح تلجرام** وتحقق من الرسائل
2. **تأكد** أن كل مستخدم يستقبل رسائله فقط
3. **راقب** الأرصدة: كل مستخدم له رصيده المنفصل
4. **تحقق** من الصفقات: لا تداخل بين المستخدمين

## ✅ علامات النجاح

- ✅ كل مستخدم يستقبل رسالة بمعرّفه
- ✅ الرسائل تصل للمستخدم الصحيح فقط
- ✅ لا يوجد تداخل في الصفقات
- ✅ كل مستخدم له رصيد منفصل

## ❌ علامات الفشل

- ❌ المستخدم A يستقبل رسائل المستخدم B
- ❌ الرصيد مشترك بين عدة مستخدمين
- ❌ الصفقات تختلط بين المستخدمين
- ❌ رسالة بدون معرّف مستخدم

## 🆘 في حالة وجود مشاكل

1. **تحقق من السجلات** في Railway
2. **ابحث عن** رسائل الخطأ
3. **تأكد من** أن المستخدم موجود في قاعدة البيانات (`/start` في تلجرام)
4. **تأكد من** أن المستخدم نشط (`is_active = True`)

## 📞 الحصول على معرّف المستخدم

في تلجرام، أرسل `/start` للبوت، سترى رسالة مثل:
```
مرحباً! معرّفك: 123456789
```

استخدم هذا الرقم في URL الـ webhook.

