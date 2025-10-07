# 📝 ملاحظات التحديث - نظام Webhook الشخصي

## ✨ التحديثات الجديدة

تم تحديث البوت ليدعم **روابط webhook شخصية** لكل مستخدم بالإضافة إلى الرابط القديم.

---

## 🎯 ما تم إضافته

### 1. دعم الرابط القديم ✅
```
https://botbybit-production.up.railway.app/webhook
```
- يعمل كما كان سابقًا
- يستخدم الإعدادات الافتراضية

### 2. روابط شخصية لكل مستخدم ✨ جديد
```
https://botbybit-production.up.railway.app/personal/<user_id>/webhook
```
- رابط فريد لكل مستخدم
- يستخدم إعدادات المستخدم من قاعدة البيانات
- صفقات منفصلة لكل مستخدم

### 3. معالجة ذكية للإشارات 🧠
- دعم جميع أنواع الإشارات: `buy`, `sell`, `long`, `short`, `close`, `exit`, `stop`
- استخراج تلقائي لـ `user_id` من الرابط
- استخدام إعدادات المستخدم الخاصة (market_type, trade_amount, leverage)

### 4. Debug محسّن 🔍
- رسائل واضحة لكل عملية
- تتبع سهل للإشارات
- عرض إعدادات المستخدم عند كل إشارة

### 5. أمان محسّن 🔐
- التحقق من وجود المستخدم
- التحقق من تفعيل المستخدم
- رسائل خطأ واضحة

---

## 📂 الملفات المعدلة

### 1. `app.py`
- إضافة route `/personal/<user_id>/webhook`
- إضافة دالة `process_user_signal` لمعالجة إشارات المستخدمين
- إضافة رسائل debug مفصلة

### 2. `web_server.py`
- إضافة route `/personal/<user_id>/webhook`
- إضافة دالة `_process_user_signal` داخل الكلاس
- دعم WebSocket للإشارات الشخصية
- تحديث الرسوم البيانية لكل مستخدم

### 3. ملفات جديدة
- `WEBHOOK_GUIDE.md` - دليل شامل للاستخدام
- `test_webhooks.py` - ملف اختبار شامل
- `UPDATE_NOTES.md` - هذا الملف

---

## 🚀 كيفية الاستخدام

### للمستخدم الواحد (الرابط القديم):
```bash
curl -X POST https://botbybit-production.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy", "price": 50000}'
```

### للمستخدمين المتعددين (الرابط الجديد):
```bash
curl -X POST https://botbybit-production.up.railway.app/personal/123456789/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSDT", "action": "buy", "price": 3000}'
```

---

## 🧪 الاختبار

### تشغيل الاختبارات:
```bash
python test_webhooks.py
```

### قبل تشغيل الاختبارات:
1. عدّل `BASE_URL` في `test_webhooks.py`
2. عدّل `TEST_USER_ID` إلى user_id صحيح من قاعدة البيانات
3. تأكد من أن السيرفر يعمل

---

## 📊 رسائل Debug

### عند استقبال الإشارة:
```
🔔 [WEBHOOK شخصي] المستخدم: 123456789
📊 [WEBHOOK شخصي] البيانات المستلمة: {...}
✅ [WEBHOOK شخصي] المستخدم موجود ونشط
📋 [WEBHOOK شخصي] إعدادات المستخدم: market_type=futures, account_type=demo
```

### عند معالجة الصفقة:
```
🔄 [معالجة الإشارة] بدء معالجة إشارة المستخدم 123456789
📈 [معالجة الإشارة] الرمز: BTCUSDT, الإجراء: buy, السعر: 50000
⚙️ [معالجة الإشارة] الإعدادات: market=futures, account=demo, amount=100, leverage=10
✅ [معالجة الإشارة] نجح فتح الصفقة للمستخدم 123456789
```

---

## ⚙️ متطلبات قاعدة البيانات

### يجب أن يكون لكل مستخدم:
- سجل في جدول `users` مع `is_active = 1`
- سجل في جدول `user_settings` مع الإعدادات المطلوبة

### إنشاء مستخدم جديد:
```python
from database import db_manager

db_manager.create_user(user_id=123456789)
db_manager.update_user_settings(
    user_id=123456789,
    settings={
        'market_type': 'futures',
        'trade_amount': 100.0,
        'leverage': 10,
        'account_type': 'demo'
    }
)
```

---

## 🔧 استكشاف الأخطاء

### خطأ 404 - User not found:
- المستخدم غير موجود في قاعدة البيانات
- أنشئ المستخدم أولاً

### خطأ 403 - User is not active:
- المستخدم موجود لكن غير مفعّل
- فعّل المستخدم: `db_manager.toggle_user_active(user_id)`

### خطأ 400 - No data received:
- تحقق من صيغة JSON المرسلة
- تأكد من وجود `symbol` و `action`

---

## 📚 الوثائق الكاملة

راجع `WEBHOOK_GUIDE.md` للحصول على:
- شرح مفصل لكل ميزة
- أمثلة استخدام من TradingView
- دليل استكشاف الأخطاء الكامل
- أمثلة متقدمة

---

## ✅ التوافق

- ✅ متوافق مع الرابط القديم
- ✅ لا يتطلب تعديل في TradingView للمستخدم القديم
- ✅ يدعم المستخدمين الجدد بروابط شخصية
- ✅ معالجة متزامنة للإشارات
- ✅ دعم جميع أنواع الإشارات

---

## 🎉 الخلاصة

الآن البوت يدعم:
1. ✅ الرابط القديم `/webhook` (يعمل كما كان)
2. ✅ روابط شخصية `/personal/<user_id>/webhook` (جديد)
3. ✅ معالجة ذكية باستخدام إعدادات كل مستخدم
4. ✅ Debug متقدم مع رسائل واضحة
5. ✅ أمان محسّن مع التحقق من المستخدمين
6. ✅ دعم جميع أنواع الإشارات
7. ✅ إشعارات Telegram شخصية لكل مستخدم

**جاهز للاستخدام! 🚀**

---

## 📞 للمزيد من المعلومات

- راجع `WEBHOOK_GUIDE.md` للدليل الكامل
- راجع `test_webhooks.py` لأمثلة الاختبار
- تحقق من logs السيرفر لتتبع العمليات

---

**تاريخ التحديث:** 2025-10-07  
**الإصدار:** 2.0.0 - Personal Webhooks

