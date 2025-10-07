# دليل الروابط الشخصية - نظام الإشارات الفردية

## 🎯 نظرة عامة

النظام الآن يدعم **روابط شخصية لكل مستخدم** تعمل بنفس طريقة الرابط الأساسي، لكن كل مستخدم له رابط خاص به.

## 🔗 الروابط المتاحة

### 1. الرابط الأساسي (للجميع)
```
POST https://botbybit-production.up.railway.app/webhook
```
- يستقبل إشارات عامة
- يرسل للجميع

### 2. الروابط الشخصية (لكل مستخدم)
```
POST https://botbybit-production.up.railway.app/personal/{USER_ID}/webhook
```
- يستقبل إشارات شخصية
- يرسل للمستخدم المحدد فقط

### 3. رابط بدء المشروع (بدون إشارة)
```
POST https://botbybit-production.up.railway.app/personal/{USER_ID}/start
```
- يبدأ المشروع للمستخدم
- بدون إشارة تداول

### 4. رابط اختبار الرابط
```
GET https://botbybit-production.up.railway.app/personal/{USER_ID}/test
```
- يختبر حالة الرابط

## 📡 صيغة الإشارات

### الإشارة البسيطة (مطلوبة)
```json
{
    "symbol": "BTCUSDT",
    "action": "buy"
}
```

### الإشارة مع السعر (اختيارية)
```json
{
    "symbol": "BTCUSDT",
    "action": "buy",
    "price": 45000.50
}
```

## 🚀 كيفية الاستخدام

### للمستخدم العادي:

1. **احصل على رابطك الشخصي:**
   ```
   https://botbybit-production.up.railway.app/personal/8169000394/webhook
   ```

2. **أرسل إشارة:**
   ```bash
   curl -X POST https://botbybit-production.up.railway.app/personal/8169000394/webhook \
   -H "Content-Type: application/json" \
   -d '{"symbol": "BTCUSDT", "action": "buy"}'
   ```

3. **ستحصل على:**
   - رسالة ترحيب في البوت
   - تنفيذ الصفقة تلقائياً
   - رسالة تأكيد الصفقة

### للمطورين:

1. **إنشاء رابط لكل مستخدم:**
   ```python
   user_id = 123456789
   webhook_url = f"https://botbybit-production.up.railway.app/personal/{user_id}/webhook"
   ```

2. **إرسال إشارة:**
   ```python
   import requests
   
   signal_data = {
       "symbol": "ETHUSDT",
       "action": "sell"
   }
   
   response = requests.post(webhook_url, json=signal_data)
   print(response.json())
   ```

## 🔧 الميزات

### ✅ ما يحدث عند إرسال إشارة:

1. **إنشاء المستخدم تلقائياً** (إذا لم يكن موجود)
2. **تفعيل المستخدم تلقائياً**
3. **إنشاء الحسابات** (Spot/Futures)
4. **إعداد API** للمستخدم
5. **إرسال رسالة ترحيب**
6. **تنفيذ الصفقة** (حقيقي أو تجريبي)
7. **إرسال رسالة تأكيد**

### 🎯 الفوائد:

- **كل مستخدم له رابط خاص**
- **يعمل بنفس طريقة الرابط الأساسي**
- **إنشاء تلقائي للمستخدمين**
- **تفعيل تلقائي**
- **دعم كامل لجميع الميزات**

## 📊 أمثلة عملية

### مثال 1: مستخدم جديد
```bash
# إرسال إشارة لمستخدم جديد
curl -X POST https://botbybit-production.up.railway.app/personal/999999999/webhook \
-H "Content-Type: application/json" \
-d '{"symbol": "ADAUSDT", "action": "buy"}'
```

**النتيجة:**
- إنشاء المستخدم 999999999
- تفعيله تلقائياً
- تنفيذ صفقة ADAUSDT
- إرسال رسائل تأكيد

### مثال 2: مستخدم موجود
```bash
# إرسال إشارة لمستخدم موجود
curl -X POST https://botbybit-production.up.railway.app/personal/8169000394/webhook \
-H "Content-Type: application/json" \
-d '{"symbol": "SOLUSDT", "action": "sell"}'
```

**النتيجة:**
- تنفيذ صفقة SOLUSDT فوراً
- إرسال رسائل تأكيد

## 🔍 اختبار النظام

### اختبار سريع:
```python
import requests

# اختبار الرابط
user_id = 8169000394
webhook_url = f"https://botbybit-production.up.railway.app/personal/{user_id}/webhook"

# إرسال إشارة اختبار
signal = {"symbol": "BTCUSDT", "action": "buy"}
response = requests.post(webhook_url, json=signal)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### اختبار شامل:
```bash
python test_full_project.py
```

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة:

1. **"Trading bot not available"**
   - تأكد من تشغيل السيرفر
   - تحقق من logs

2. **"No data received"**
   - تأكد من إرسال JSON صحيح
   - تحقق من Content-Type

3. **"User not found"**
   - سيتم إنشاء المستخدم تلقائياً
   - لا تقلق!

### التحقق من الحالة:
```bash
# فحص حالة السيرفر
curl https://botbybit-production.up.railway.app/health

# اختبار رابط شخصي
curl https://botbybit-production.up.railway.app/personal/8169000394/test
```

## 📈 الإحصائيات

- **عدد المستخدمين:** غير محدود
- **عدد الإشارات:** غير محدود
- **الاستجابة:** فورية
- **الدعم:** Spot + Futures
- **الحسابات:** حقيقي + تجريبي

## 🎉 الخلاصة

الآن كل مستخدم لديه:
- ✅ رابط شخصي فريد
- ✅ يعمل بنفس طريقة الرابط الأساسي
- ✅ إنشاء تلقائي للحساب
- ✅ تفعيل تلقائي
- ✅ دعم كامل لجميع الميزات

**النتيجة:** نظام إشارات شخصي كامل ومتطور! 🚀
