# 🚀 البداية السريعة - نظام TP/SL

## ⚡ 5 دقائق للبدء

### 1️⃣ اختبر النظام (30 ثانية)
```bash
python examples_tpsl.py
```

سترى الأمثلة التالية تعمل:
- ✅ صفقة بسيطة مع TP/SL
- ✅ صفقة مع TP متعدد
- ✅ صفقة بأسعار محددة
- ✅ محاكاة تحديثات الأسعار
- ✅ صفقة بيع (Short)
- ✅ Futures مع رافعة

---

### 2️⃣ اقرأ المثال الأساسي (1 دقيقة)

```python
from order_manager import order_manager

# صفقة شراء BTC
order = order_manager.create_managed_order(
    order_id="BTC_001",
    user_id=123456,
    symbol="BTCUSDT",
    side="buy",
    entry_price=50000.0,
    quantity=0.1,
    
    # Take Profit: +5% (إغلاق 100%)
    take_profits=[{
        'level': 1,
        'price_type': 'percentage',
        'value': 5.0,
        'close_percentage': 100.0
    }],
    
    # Stop Loss: -2%
    stop_loss={
        'price_type': 'percentage',
        'value': 2.0,
        'trailing': False
    }
)

# تحديث السعر
result = order.update_price(52500.0)  # سيتم تفعيل TP!
```

---

### 3️⃣ افهم الأنواع (1 دقيقة)

#### النوع 1: نسبة مئوية
```python
'price_type': 'percentage'
'value': 5.0  # يعني +5% من سعر الدخول
```

#### النوع 2: سعر محدد
```python
'price_type': 'price'
'value': 52500.0  # سعر محدد بالضبط
```

---

### 4️⃣ TP متعدد (1 دقيقة)

```python
take_profits=[
    # TP1: +2% (إغلاق 33%)
    {
        'level': 1,
        'price_type': 'percentage',
        'value': 2.0,
        'close_percentage': 33.33
    },
    # TP2: +5% (إغلاق 33%)
    {
        'level': 2,
        'price_type': 'percentage',
        'value': 5.0,
        'close_percentage': 33.33
    },
    # TP3: +10% (إغلاق الباقي)
    {
        'level': 3,
        'price_type': 'percentage',
        'value': 10.0,
        'close_percentage': 33.34
    }
]
```

---

### 5️⃣ الربط مع البوت (2 دقيقة)

أضف في `bybit_trading_bot.py`:

```python
# في بداية الملف
from order_manager import order_manager
from trade_interface import trade_interface
from bot_integration import bot_integration

# في دالة main()
async def start_monitoring():
    await bot_integration.load_managed_orders_from_db()
    await bot_integration.start_price_monitoring(trading_bot.bybit_api)

application.post_init = start_monitoring
```

---

## 📖 الخطوات التالية

### للاستخدام الأساسي:
✅ أنت جاهز الآن! ابدأ بفتح صفقات

### للاستخدام المتقدم:
📚 اقرأ `TP_SL_GUIDE.md` للتفاصيل الكاملة

### للتخصيص:
🔧 راجع `order_manager.py` للتعديلات

---

## 💡 نصائح سريعة

### ✅ افعل:
- استخدم SL دائماً
- اختبر بصفقات صغيرة
- راقب logs البوت

### ❌ لا تفعل:
- لا تضع SL بعيد جداً
- لا تستخدم رافعة عالية بدون خبرة
- لا تتجاهل التحذيرات

---

## 🆘 حل المشاكل

### المشكلة: "الصفقة غير موجودة"
```python
# تأكد من إنشاء الصفقة أولاً
order = order_manager.create_managed_order(...)
```

### المشكلة: "خطأ في قاعدة البيانات"
```bash
# احذف قاعدة البيانات وأعد المحاولة
rm trading_bot.db
python bybit_trading_bot.py
```

### المشكلة: "TP/SL لم يتفعل"
```python
# تأكد من تشغيل المراقبة
await bot_integration.start_price_monitoring(bybit_api)
```

---

## 📊 استراتيجية للمبتدئين

```python
# استراتيجية بسيطة وآمنة
take_profits=[
    {'level': 1, 'price_type': 'percentage', 'value': 2.0, 'close_percentage': 50.0},
    {'level': 2, 'price_type': 'percentage', 'value': 5.0, 'close_percentage': 50.0}
]

stop_loss = {'price_type': 'percentage', 'value': 1.5, 'trailing': False}
```

**شرح**:
- TP1 عند +2%: نأخذ نصف الربح مبكراً ✅
- TP2 عند +5%: نترك النصف يرتفع أكثر 📈
- SL عند -1.5%: حماية من خسارة كبيرة 🛡️

---

## ✨ ميزة إضافية: Trailing Stop

```python
stop_loss = {
    'price_type': 'percentage',
    'value': 2.0,
    'trailing': True,
    'trailing_distance': 1.0  # يتحرك 1% خلف السعر
}
```

**كيف يعمل**:
- السعر يرتفع → SL يرتفع معه
- السعر ينخفض → SL يبقى ثابت
- النتيجة: حماية الأرباح تلقائياً 🎯

---

## 🎓 تعلم المزيد

| الموضوع | الملف |
|---------|------|
| الدليل الشامل | `TP_SL_GUIDE.md` |
| أمثلة عملية | `examples_tpsl.py` |
| تفاصيل التنفيذ | `IMPLEMENTATION_SUMMARY.md` |
| البداية السريعة | `README_TP_SL.md` |

---

## 🏁 جاهز للبدء؟

```bash
# اختبر الآن
python examples_tpsl.py

# ثم ابدأ التداول! 🚀
```

---

**مدة القراءة**: 5 دقائق  
**مستوى الصعوبة**: مبتدئ  
**الحالة**: ✅ جاهز للاستخدام

---

**تذكر**: التداول ينطوي على مخاطر. استخدم النظام بحكمة! 🧠

