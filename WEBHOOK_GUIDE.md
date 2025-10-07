# 🔗 دليل استخدام روابط الإشارات الشخصية

## 📋 نظرة عامة

بعد التحديث الأخير، أصبح لكل مستخدم رابط webhook خاص به لاستقبال الإشارات من TradingView.

---

## 🎯 الروابط المتاحة

### 1️⃣ **الرابط الأساسي (للجميع)**
```
https://botbybit-production.up.railway.app/webhook
```
- يستخدم للإشارات العامة
- يعمل مع الإعدادات الافتراضية للبوت

### 2️⃣ **الرابط الشخصي (لكل مستخدم)**
```
https://botbybit-production.up.railway.app/personal/<user_id>/webhook
```

**مثال:**
```
https://botbybit-production.up.railway.app/personal/8169000394/webhook
```

---

## 🔧 كيفية الحصول على رابطك الشخصي

### من خلال البوت على Telegram:

1. افتح البوت على Telegram
2. اضغط على **"⚙️ الإعدادات"**
3. اختر **"🔗 رابط الإشارة الشخصي"**
4. سيرسل لك البوت رابطك الخاص

---

## 📡 كيفية استخدام الرابط في TradingView

### الخطوات:

1. **افتح TradingView**
2. **اذهب إلى Alert Settings**
3. **في حقل Webhook URL، ضع رابطك الشخصي:**
   ```
   https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook
   ```

4. **في حقل Message، استخدم هذا الشكل:**
   ```json
   {
     "symbol": "{{ticker}}",
     "action": "{{strategy.order.action}}"
   }
   ```

   أو بشكل يدوي:
   ```json
   {
     "symbol": "BTCUSDT",
     "action": "buy"
   }
   ```

---

## ✅ التحقق من عمل الرابط

### 1. اختبار بسيط (GET):
```bash
curl https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/test
```

**النتيجة المتوقعة:**
```json
{
  "status": "success",
  "message": "Personal webhook endpoint is working for user YOUR_USER_ID",
  "user_id": YOUR_USER_ID,
  "webhook_url": "/personal/YOUR_USER_ID/webhook"
}
```

### 2. اختبار إشارة (POST):
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

**النتيجة المتوقعة:**
```json
{
  "status": "success",
  "message": "Personal signal received for user YOUR_USER_ID",
  "user_id": YOUR_USER_ID,
  "data": {
    "symbol": "BTCUSDT",
    "action": "buy",
    "user_id": YOUR_USER_ID,
    "source": "personal_webhook"
  }
}
```

---

## 🔍 كيفية التحقق من الـ Logs

### على Railway:

1. اذهب إلى **Railway Dashboard**
2. افتح مشروع **botbybit**
3. اضغط على **Deployments**
4. اختر آخر deployment
5. اضغط على **View Logs**

### ما يجب أن تراه عند إرسال إشارة:

```
🔍 تم استقبال طلب webhook للمستخدم: 8169000394
🔍 البيانات المستلمة: {'symbol': 'BTCUSDT', 'action': 'buy'}
🔍 البيانات بعد الإضافة: {'symbol': 'BTCUSDT', 'action': 'buy', 'user_id': 8169000394, 'source': 'personal_webhook'}
🔍 بدء معالجة الإشارة الشخصية
✅ تم بدء thread معالجة الإشارة للمستخدم 8169000394
🚀 بدء معالجة الإشارة للمستخدم 8169000394
🔍 البيانات: {'symbol': 'BTCUSDT', 'action': 'buy', 'user_id': 8169000394, 'source': 'personal_webhook'}
🔍 معالجة الإشارة للمستخدم 8169000394 بنفس طريقة الرابط الأساسي
🔍 معالجة إشارة للمستخدم 8169000394
إنشاء مستخدم جديد 8169000394  (إذا كان جديد)
تفعيل المستخدم 8169000394  (إذا كان غير نشط)
✅ انتهت معالجة الإشارة للمستخدم 8169000394
```

---

## ❌ حل المشاكل الشائعة

### المشكلة 1: الإشارة لا تصل
**الحل:**
- تحقق من الرابط في TradingView
- تأكد من استخدام `POST` وليس `GET`
- تأكد من `Content-Type: application/json`

### المشكلة 2: الإشارة تصل لكن لا يتم تنفيذ الصفقة
**الحل:**
- تحقق من الـ logs في Railway
- تأكد من أن المستخدم نشط (active)
- تأكد من إعدادات المستخدم (account_type, market_type, trade_amount)

### المشكلة 3: خطأ "Trading bot not available"
**الحل:**
- انتظر قليلاً (البوت قد يكون في طور التشغيل)
- أعد تشغيل الـ deployment على Railway
- تحقق من الـ logs للأخطاء

---

## 📊 الفرق بين الرابط الأساسي والشخصي

| الميزة | الرابط الأساسي | الرابط الشخصي |
|--------|----------------|---------------|
| **الاستخدام** | عام للجميع | خاص بكل مستخدم |
| **الإعدادات** | افتراضية | حسب إعدادات المستخدم |
| **التتبع** | صعب | سهل (كل مستخدم له logs خاصة) |
| **الأمان** | أقل | أعلى (كل مستخدم له رابط فريد) |
| **التخصيص** | محدود | كامل |

---

## 🎯 أفضل الممارسات

1. **استخدم رابطك الشخصي دائماً** لضمان تطبيق إعداداتك الخاصة
2. **لا تشارك رابطك الشخصي** مع أي شخص آخر
3. **راقب الـ logs** بانتظام للتأكد من عمل الإشارات
4. **اختبر الرابط** قبل استخدامه في TradingView
5. **احفظ رابطك** في مكان آمن

---

## 🔐 الأمان

- كل رابط شخصي مرتبط بـ `user_id` فريد
- لا يمكن لمستخدم الوصول إلى إشارات مستخدم آخر
- جميع الإشارات تُسجل في الـ logs مع `user_id`
- يمكنك تتبع جميع إشاراتك من خلال البوت

---

## 📞 الدعم

إذا واجهت أي مشكلة:
1. تحقق من الـ logs في Railway
2. اختبر الرابط باستخدام `curl`
3. تواصل مع الدعم عبر البوت على Telegram

---

## 🚀 مثال كامل

### 1. احصل على رابطك:
```
https://botbybit-production.up.railway.app/personal/8169000394/webhook
```

### 2. اختبره:
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/8169000394/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

### 3. استخدمه في TradingView:
- **Webhook URL:** `https://botbybit-production.up.railway.app/personal/8169000394/webhook`
- **Message:** `{"symbol": "{{ticker}}", "action": "{{strategy.order.action}}"}`

### 4. راقب النتيجة:
- افتح Telegram
- ستصلك رسالة تأكيد تنفيذ الصفقة

---

✅ **تم! الآن لديك رابط webhook شخصي يعمل بكفاءة!**
