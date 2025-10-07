# 🚀 دليل البدء السريع - روابط الإشارات الشخصية

## 📌 ما الجديد؟

الآن كل مستخدم لديه **رابط webhook خاص به** لاستقبال إشارات TradingView!

---

## ⚡ البدء السريع (3 خطوات)

### 1️⃣ **احصل على رابطك الشخصي**

افتح البوت على Telegram واكتب:
```
/start
```

ثم اضغط على:
```
⚙️ الإعدادات → 🔗 رابط الإشارة الشخصي
```

سيرسل لك البوت رابطك:
```
https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook
```

---

### 2️⃣ **استخدم الرابط في TradingView**

1. افتح **TradingView**
2. اذهب إلى **Alert Settings**
3. في **Webhook URL**، ضع رابطك:
   ```
   https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook
   ```
4. في **Message**، استخدم:
   ```json
   {"symbol": "{{ticker}}", "action": "{{strategy.order.action}}"}
   ```

---

### 3️⃣ **اختبر الرابط**

#### أ. اختبار بسيط:
```bash
curl https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/test
```

#### ب. إرسال إشارة اختبار:
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/YOUR_USER_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

#### ج. استخدام السكريبت:
```bash
python test_complete_webhook.py
```

---

## ✅ التحقق من النجاح

بعد إرسال إشارة، يجب أن:

1. **تصلك رسالة في Telegram** تؤكد استلام الإشارة
2. **تظهر الصفقة** في "📊 الصفقات المفتوحة"
3. **تتغير المحفظة** في "💼 المحفظة"

---

## 🔍 إذا لم يعمل

### تحقق من الـ Logs:
```bash
railway logs
```

### يجب أن ترى:
```
🔍 تم استقبال طلب webhook للمستخدم: YOUR_USER_ID
🔍 البيانات المستلمة: {'symbol': 'BTCUSDT', 'action': 'buy'}
✅ تم بدء thread معالجة الإشارة للمستخدم YOUR_USER_ID
```

### إذا لم ترى شيء:
- تحقق من الرابط
- تأكد من استخدام `POST` وليس `GET`
- تأكد من `Content-Type: application/json`

---

## 📚 مزيد من المعلومات

- **دليل كامل:** اقرأ `WEBHOOK_GUIDE.md`
- **حل المشاكل:** اقرأ `TROUBLESHOOTING.md`
- **اختبار شامل:** استخدم `test_complete_webhook.py`

---

## 🎯 مثال كامل

### 1. الحصول على الرابط:
```
https://botbybit-production.up.railway.app/personal/8169000394/webhook
```

### 2. الاختبار:
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/8169000394/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

### 3. النتيجة:
```json
{
  "status": "success",
  "message": "Personal signal received for user 8169000394",
  "user_id": 8169000394,
  "data": {
    "symbol": "BTCUSDT",
    "action": "buy",
    "user_id": 8169000394,
    "source": "personal_webhook"
  }
}
```

### 4. في Telegram:
```
🚀 تم استقبال إشارة شخصية لك!

👋 مرحباً! تم تفعيل بوت التداول على Bybit لك

📡 تم استقبال إشارة التداول:
🔹 الرمز: BTCUSDT
🔹 الإجراء: buy

✅ المشروع يعمل الآن بشكل كامل لك!
```

---

## 💡 نصائح

1. **احفظ رابطك** في مكان آمن
2. **لا تشاركه** مع أي شخص
3. **اختبره** قبل استخدامه في TradingView
4. **راقب الـ logs** أثناء الاختبار

---

## 🔐 الأمان

- كل رابط فريد لكل مستخدم
- لا يمكن لمستخدم الوصول إلى إشارات مستخدم آخر
- جميع الإشارات مسجلة في الـ logs

---

## 📞 الدعم

إذا واجهت مشكلة:
1. اقرأ `TROUBLESHOOTING.md`
2. استخدم `test_complete_webhook.py`
3. تواصل عبر Telegram

---

✅ **الآن أنت جاهز للبدء!**

🎉 **استمتع بالتداول الآلي!**
