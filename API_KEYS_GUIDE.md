# دليل إضافة مفاتيح API لـ Bybit

## المشكلة الحالية
```
Failed to place order on Bybit: مفاتيح API غير صحيحة
```

هذا يعني أن النظام يعمل بشكل صحيح ولكن مفاتيح API مفقودة أو غير صحيحة.

## الحل: إضافة مفاتيح API صحيحة

### الخطوة 1: الحصول على مفاتيح API من Bybit

#### 1.1 تسجيل الدخول إلى Bybit
- اذهب إلى [Bybit.com](https://www.bybit.com)
- سجل الدخول إلى حسابك

#### 1.2 إنشاء مفاتيح API جديدة
- اذهب إلى **Account & Security** (الحساب والأمان)
- اضغط على **API Management** (إدارة API)
- اضغط على **Create New Key** (إنشاء مفتاح جديد)

#### 1.3 إعداد الصلاحيات
اختر الصلاحيات التالية:
- ✅ **Read** - قراءة البيانات (مطلوب)
- ✅ **Trade** - التداول (مطلوب)
- ✅ **Derivatives** - التداول على المشتقات (مطلوب للرافعة المالية)

#### 1.4 نسخ المفاتيح
- انسخ **API Key** (مفتاح API)
- انسخ **Secret Key** (المفتاح السري)
- احفظهما في مكان آمن

### الخطوة 2: إضافة المفاتيح إلى النظام

#### 2.1 تحديث إعدادات المستخدم
```python
# في ملف الإعدادات أو قاعدة البيانات
user_data = {
    'bybit_api_key': 'YOUR_API_KEY_HERE',        # ضع مفتاح API هنا
    'bybit_api_secret': 'YOUR_SECRET_KEY_HERE',  # ضع المفتاح السري هنا
    'trade_amount': 55.0,
    'leverage': 1,
    'exchange': 'bybit',
    'account_type': 'real',
    'market_type': 'futures'
}
```

#### 2.2 مثال عملي
```python
# مثال بمفاتيح وهمية (استبدلها بمفاتيحك الحقيقية)
user_data = {
    'bybit_api_key': 'ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ567',
    'bybit_api_secret': 'secret123456789abcdefghijklmnopqrstuvwxyz0123456789',
    'trade_amount': 55.0,
    'leverage': 1,
    'exchange': 'bybit',
    'account_type': 'real',
    'market_type': 'futures'
}
```

### الخطوة 3: اختبار المفاتيح

#### 3.1 اختبار بسيط
```python
from real_account_manager import real_account_manager

# تهيئة الحساب
user_id = 1  # أو معرف المستخدم الخاص بك
api_key = "YOUR_API_KEY_HERE"
api_secret = "YOUR_SECRET_KEY_HERE"

real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
account = real_account_manager.get_account(user_id)

# اختبار جلب الرصيد
balance = account.get_wallet_balance('futures')
if balance:
    print("✅ مفاتيح API صحيحة!")
    print(f"الرصيد: {balance}")
else:
    print("❌ مفاتيح API غير صحيحة!")
```

#### 3.2 اختبار تعديل الرافعة المالية
```python
# اختبار تعديل الرافعة المالية
result = account.set_leverage('linear', 'BTCUSDT', 1)
if result:
    print("✅ تم تعديل الرافعة المالية بنجاح!")
else:
    print("❌ فشل تعديل الرافعة المالية")
```

#### 3.3 اختبار وضع أمر
```python
# اختبار وضع أمر صغير
result = account.place_order(
    category='linear',
    symbol='BTCUSDT',
    side='Buy',
    order_type='Market',
    qty=0.001,  # كمية صغيرة للاختبار
    leverage=1
)

if result and result.get('success'):
    print("✅ تم وضع الأمر بنجاح!")
    print(f"Order ID: {result.get('order_id')}")
else:
    print("❌ فشل وضع الأمر")
    print(f"الخطأ: {result}")
```

## نصائح مهمة

### 🔒 الأمان
- **لا تشارك مفاتيح API** مع أي شخص
- **احفظ المفاتيح في مكان آمن**
- **استخدم IP Whitelist** إذا أمكن (قائمة IP مسموحة)

### ⚠️ تحذيرات
- **تأكد من صحة المفاتيح** قبل الاستخدام
- **تحقق من الصلاحيات** المطلوبة
- **ابدأ بكميات صغيرة** للاختبار

### 🛠️ استكشاف الأخطاء

#### إذا ظهر خطأ "Invalid API key"
- تحقق من صحة مفتاح API
- تأكد من نسخ المفتاح كاملاً
- تحقق من عدم وجود مسافات إضافية

#### إذا ظهر خطأ "Invalid signature"
- تحقق من صحة المفتاح السري
- تأكد من نسخ المفتاح السري كاملاً
- تحقق من عدم وجود مسافات إضافية

#### إذا ظهر خطأ "Permission denied"
- تحقق من صلاحيات API
- تأكد من تفعيل التداول على المشتقات
- تحقق من إعدادات الحساب

## اختبار النظام بعد إضافة المفاتيح

### تشغيل الاختبار الشامل
```bash
python simple_leverage_test.py
```

### النتيجة المتوقعة
```
اختبار تعديل الرافعة المالية
========================================
تم العثور على حساب حقيقي للمستخدم 1

اختبار تعديل الرافعة المالية:
الرمز: BTCUSDT
الرافعة: 1x
النوع: linear
نجح تعديل الرافعة المالية!

اختبار وضع أمر
==============================
تم العثور على حساب حقيقي للمستخدم 1
بيانات الأمر:
  category: linear
  symbol: BTCUSDT
  side: Buy
  order_type: Market
  qty: 0.001
  leverage: 1
نجح وضع الأمر!

ملخص النتائج:
اختبار الرافعة المالية: نجح
اختبار الأمر: نجح

جميع الاختبارات نجحت! تعديل الرافعة المالية يعمل بشكل صحيح.
```

## الخلاصة

المشكلة واضحة الآن: **مفاتيح API غير صحيحة**. بعد إضافة مفاتيح API صحيحة:

1. ✅ **تعديل الرافعة المالية سيعمل**
2. ✅ **تنفيذ الصفقات سيعمل**
3. ✅ **ستحصل على رسائل خطأ واضحة**
4. ✅ **النظام سيعمل بشكل مثالي**

**الخطوة التالية:** أضف مفاتيح API صحيحة وستجد أن كل شيء يعمل كما تريد! 🎉
