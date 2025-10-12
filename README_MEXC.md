# دليل استخدام منصة MEXC مع البوت

## 📋 نظرة عامة

تم إضافة دعم منصة **MEXC** إلى بوت التداول. يرجى ملاحظة أن MEXC تدعم **التداول الفوري (Spot) فقط** عبر API، ولا يوجد دعم لتداول الفيوتشر.

## ⚠️ ملاحظات هامة

- ✅ **مدعوم**: التداول الفوري (Spot Trading)
- ❌ **غير مدعوم**: تداول الفيوتشر (Futures Trading)
- 🔐 **الأمان**: يتطلب API Key و Secret من حسابك على MEXC

## 🔧 الإعداد

### 1. الحصول على API Key من MEXC

1. قم بتسجيل الدخول إلى حسابك على [MEXC](https://www.mexc.com/)
2. اذهب إلى **Account** → **API Management**
3. قم بإنشاء API Key جديد
4. احفظ **API Key** و **Secret Key** في مكان آمن
5. تأكد من تفعيل صلاحية **Spot Trading** فقط

### 2. إضافة الإعدادات إلى ملف .env

قم بإضافة المفاتيح التالية إلى ملف `.env`:

```env
# إعدادات MEXC API
MEXC_API_KEY=your_mexc_api_key_here
MEXC_API_SECRET=your_mexc_api_secret_here
```

### 3. تثبيت المتطلبات

تأكد من تثبيت جميع المكتبات المطلوبة:

```bash
pip install -r requirements.txt
```

## 🚀 الاستخدام

### اختبار الاتصال بـ MEXC

يمكنك اختبار الاتصال بمنصة MEXC باستخدام:

```bash
python mexc_trading_bot.py
```

هذا السكريبت سيقوم بـ:
- اختبار الاتصال بـ MEXC API
- عرض رصيد حسابك
- عرض سعر BTC/USDT الحالي

### إرسال إشارة تداول

استخدم سكريبت الاختبار لإرسال إشارة:

```bash
python test_send_signal.py
```

عند تشغيل السكريبت:
1. أدخل User ID الخاص بك في Telegram
2. اختر نوع الإشارة (شراء/بيع)
3. **اختر المنصة**: اختر `2` لـ MEXC
4. أدخل الزوج (مثل: BTCUSDT)

### إعداد TradingView

في TradingView، قم بإضافة الحقل التالي في JSON الإشارة:

```json
{
  "action": "buy",
  "symbol": "BTCUSDT",
  "price": "{{close}}",
  "time": "{{time}}",
  "exchange": "MEXC"
}
```

**ملاحظة**: تأكد من إضافة `"exchange": "MEXC"` لتحديد المنصة.

## 📊 الميزات المدعومة في MEXC

### ✅ الميزات المتاحة

- 📈 **التداول الفوري (Spot)**: شراء وبيع العملات الرقمية
- 💰 **عرض الرصيد**: الاطلاع على رصيدك في جميع العملات
- 📊 **الحصول على الأسعار**: الحصول على الأسعار الحالية للعملات
- 📝 **الأوامر المفتوحة**: عرض وإدارة الأوامر المفتوحة
- 🔄 **أوامر السوق**: تنفيذ فوري بسعر السوق
- 📌 **أوامر محددة (Limit)**: تحديد السعر المطلوب
- 📜 **سجل التداولات**: عرض سجل تداولاتك السابقة
- ❌ **إلغاء الأوامر**: إلغاء الأوامر المفتوحة

### ❌ الميزات غير المدعومة

- 🚫 **تداول الفيوتشر**: غير متاح عبر MEXC API
- 🚫 **الرافعة المالية**: غير متاحة (خاصة بالفيوتشر)
- 🚫 **المراكز المفتوحة (Positions)**: غير متاحة (خاصة بالفيوتشر)

## 🔐 الأمان

### نصائح الأمان

1. **لا تشارك** API Keys مع أي شخص
2. **استخدم IP Whitelist** في إعدادات MEXC API
3. **فعّل صلاحية Spot Trading فقط** - لا حاجة لصلاحيات أخرى
4. **لا تفعّل صلاحية السحب (Withdrawal)** إلا إذا كنت تحتاجها
5. **احفظ Secret Key** في مكان آمن ولا تضعه في الكود

### صلاحيات API المطلوبة

- ✅ **Read**: لقراءة معلومات الحساب والأسعار
- ✅ **Spot Trading**: لتنفيذ أوامر التداول الفوري
- ❌ **Withdrawal**: غير مطلوب (يُفضل عدم تفعيله)

## 📝 أمثلة على الاستخدام

### مثال 1: شراء BTC بقيمة 100 USDT

```python
from mexc_trading_bot import create_mexc_bot

# إنشاء البوت
bot = create_mexc_bot(api_key="your_key", api_secret="your_secret")

# الحصول على السعر الحالي
price = bot.get_ticker_price("BTCUSDT")

# حساب الكمية
quantity = 100 / price  # 100 USDT

# وضع أمر شراء
order = bot.place_spot_order(
    symbol="BTCUSDT",
    side="BUY",
    quantity=quantity,
    order_type="MARKET"
)

print(f"تم تنفيذ الأمر: {order}")
```

### مثال 2: بيع BTC بسعر محدد

```python
from mexc_trading_bot import create_mexc_bot

bot = create_mexc_bot(api_key="your_key", api_secret="your_secret")

# وضع أمر بيع بسعر محدد
order = bot.place_spot_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity=0.001,  # 0.001 BTC
    order_type="LIMIT",
    price=50000  # السعر المطلوب
)

print(f"تم وضع أمر البيع: {order}")
```

### مثال 3: عرض الرصيد

```python
from mexc_trading_bot import create_mexc_bot

bot = create_mexc_bot(api_key="your_key", api_secret="your_secret")

# الحصول على الرصيد
balance = bot.get_account_balance()

# عرض الرصيد
for asset, info in balance['balances'].items():
    if info['total'] > 0:
        print(f"{asset}: {info['total']:.8f} (متاح: {info['free']:.8f})")
```

## 🆚 مقارنة بين Bybit و MEXC

| الميزة | Bybit | MEXC |
|--------|-------|------|
| التداول الفوري (Spot) | ✅ | ✅ |
| تداول الفيوتشر (Futures) | ✅ | ❌ |
| الرافعة المالية | ✅ | ❌ |
| الحساب التجريبي | ✅ | ❌ |
| API مجاني | ✅ | ✅ |
| عدد العملات | متوسط | كبير |

## 🐛 استكشاف الأخطاء

### خطأ: "User not found"

**الحل**: تأكد من بدء البوت باستخدام `/start` في Telegram أولاً.

### خطأ: "Invalid API Key"

**الحل**: 
1. تحقق من صحة API Key و Secret في ملف `.env`
2. تأكد من تفعيل API Key في حسابك على MEXC
3. تحقق من صلاحيات API Key

### خطأ: "Symbol not found"

**الحل**: 
1. تأكد من كتابة الزوج بشكل صحيح (مثل: BTCUSDT)
2. تحقق من أن الزوج متاح للتداول على MEXC
3. تأكد من عدم وجود مسافات في اسم الزوج

### خطأ: "Insufficient balance"

**الحل**: 
1. تحقق من رصيدك باستخدام `bot.get_account_balance()`
2. تأكد من وجود رصيد كافٍ في العملة المطلوبة
3. قلل من مبلغ التداول في الإعدادات

### خطأ: "Futures not supported"

**الحل**: MEXC لا تدعم تداول الفيوتشر عبر API. استخدم التداول الفوري (Spot) فقط.

## 📚 موارد إضافية

- [MEXC API Documentation](https://mexcdevelop.github.io/apidocs/spot_v3_en/)
- [MEXC Official Website](https://www.mexc.com/)
- [دليل استخدام البوت الرئيسي](README.md)

## 🤝 الدعم

إذا واجهت أي مشاكل:
1. تحقق من ملف `trading_bot.log` للحصول على تفاصيل الأخطاء
2. تأكد من صحة جميع الإعدادات في ملف `.env`
3. راجع قسم استكشاف الأخطاء أعلاه

## 📄 الترخيص

هذا المشروع مرخص تحت نفس ترخيص المشروع الأساسي.

---

**تحذير**: التداول ينطوي على مخاطر. استخدم هذا البوت على مسؤوليتك الخاصة. يُنصح بالبدء بمبالغ صغيرة واختبار البوت جيداً قبل استخدام مبالغ كبيرة.

