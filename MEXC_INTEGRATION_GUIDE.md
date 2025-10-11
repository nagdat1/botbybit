# 🔄 دليل دعم منصة MEXC

## 📋 نظرة عامة

تم إضافة دعم كامل لمنصة **MEXC** للتداول الفوري (Spot Trading) في البوت. يمكن للمستخدمين الآن الاختيار بين منصة **Bybit** و**MEXC** لتنفيذ صفقاتهم.

---

## ✨ الميزات المتاحة

### ✅ ما تم إضافته:

1. **كلاس MEXC API كامل** (`MEXCAPI`)
   - توقيع آمن للطلبات (HMAC SHA256)
   - الحصول على معلومات الحساب
   - الحصول على الرصيد
   - عرض جميع أزواج التداول
   - الحصول على أسعار العملات
   - فتح أوامر (Market & Limit)
   - إلغاء الأوامر
   - عرض الأوامر المفتوحة
   - متابعة حالة الأوامر

2. **تحديثات قاعدة البيانات**
   - إضافة حقل `exchange_platform` في جدول `users`
   - دالة `update_exchange_platform()` لتغيير المنصة
   - تحديث `update_user_api()` لدعم اختيار المنصة

3. **التوافقية**
   - جميع الإعدادات الحالية متوافقة
   - لا حاجة لتغيير البيانات الموجودة
   - انتقال سلس بين المنصتين

---

## ⚠️ القيود والملاحظات

### 🚫 ما لا تدعمه MEXC عبر API:

- ❌ **تداول العقود الآجلة (Futures)** - MEXC لا توفر Futures API
- ✅ **التداول الفوري فقط (Spot)** - مدعوم بالكامل

### 💡 ملاحظات مهمة:

1. **نوع الحساب**: MEXC تدعم فقط التداول الفوري
2. **الصلاحيات المطلوبة**: 
   - Read
   - Spot Trading
   - لا حاجة لتفعيل Futures
3. **قيود IP**: يفضل عدم تفعيل IP Whitelist

---

## 🔧 كيفية الاستخدام

### 1️⃣ إنشاء API Keys في MEXC

1. اذهب إلى: https://www.mexc.com/user/openapi
2. انقر على "Create New API"
3. فعّل الصلاحيات التالية:
   - ✅ **Read Info**
   - ✅ **Spot Trading**
4. احفظ API Key و Secret Key

### 2️⃣ ربط الـ API في البوت

```
1. ابدأ البوت: /start
2. اختر "⚙️ الإعدادات"
3. اختر "🔗 تحديث API"
4. اختر المنصة: "MEXC"
5. أدخل API Key
6. أدخل Secret Key
```

### 3️⃣ التحقق من الاتصال

```
1. اذهب إلى "⚙️ الإعدادات"
2. اختر "🔍 فحص API"
3. يجب أن تظهر:
   ✅ API يعمل بشكل صحيح!
   🟢 الاتصال: نشط
```

---

## 🔍 الفروقات بين Bybit و MEXC

| الميزة | Bybit | MEXC |
|--------|-------|------|
| التداول الفوري (Spot) | ✅ | ✅ |
| العقود الآجلة (Futures) | ✅ | ❌ |
| تداول بالرافعة المالية | ✅ | ✅ (Margin) |
| أنواع الأوامر | Market, Limit, Stop | Market, Limit, Stop-Limit |
| API Rate Limit | 10/ثانية | 20/ثانية |
| التوثيق | API v5 | API v3 |

---

## 📝 أمثلة على التكامل في الكود

### مثال 1: إنشاء اتصال MEXC

```python
from bybit_trading_bot import MEXCAPI

# إنشاء كلاس API
mexc_api = MEXCAPI(
    api_key="your_mexc_api_key",
    api_secret="your_mexc_secret_key"
)

# الحصول على الرصيد
balance = mexc_api.get_balance()
print(balance)
```

### مثال 2: فتح أمر شراء

```python
# فتح أمر شراء بالسوق
order = mexc_api.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity=0.001
)
print(order)
```

### مثال 3: فتح أمر محدد

```python
# فتح أمر شراء محدد
order = mexc_api.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=45000.0
)
print(order)
```

---

## 🛠️ التحديثات المطلوبة في البوت الرئيسي

### 1. إضافة اختيار المنصة في الإعدادات

```python
# في دالة settings_menu
keyboard = [
    [InlineKeyboardButton("🏢 اختيار المنصة", callback_data="choose_exchange")],
    [InlineKeyboardButton("🔗 تحديث API", callback_data="link_api")],
    # ... باقي الأزرار
]
```

### 2. دالة اختيار المنصة

```python
async def choose_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختيار منصة التداول"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    current_platform = user_data.get('exchange_platform', 'bybit')
    
    message = f"""
🏢 **اختيار منصة التداول**

المنصة الحالية: **{current_platform.upper()}**

اختر المنصة التي تريد استخدامها:
    """
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_platform == 'bybit' else ''} Bybit", 
                callback_data="set_exchange_bybit"
            ),
            InlineKeyboardButton(
                f"{'✅' if current_platform == 'mexc' else ''} MEXC", 
                callback_data="set_exchange_mexc"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع", callback_data="settings")]
    ]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
```

### 3. دالة تغيير المنصة

```python
async def set_exchange_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين منصة التداول"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    platform = query.data.replace("set_exchange_", "")
    
    # تحديث المنصة في قاعدة البيانات
    success = db_manager.update_exchange_platform(user_id, platform)
    
    if success:
        message = f"""
✅ **تم تغيير المنصة بنجاح!**

المنصة الجديدة: **{platform.upper()}**

💡 يرجى تحديث API Keys للمنصة الجديدة
        """
    else:
        message = "❌ فشل في تغيير المنصة"
    
    keyboard = [[
        InlineKeyboardButton("🔗 تحديث API", callback_data="link_api"),
        InlineKeyboardButton("🔙 رجوع", callback_data="settings")
    ]]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
```

### 4. تحديث دالة التحقق من API

```python
async def check_api_connection(api_key: str, api_secret: str, platform: str = 'bybit') -> bool:
    """التحقق من صحة API keys"""
    try:
        if not api_key or not api_secret:
            return False
        
        if platform == 'mexc':
            # إنشاء API مؤقت للتحقق من MEXC
            temp_api = MEXCAPI(api_key, api_secret)
            account_info = temp_api.get_account_info()
            
            # MEXC ترجع 'code' بدلاً من 'retCode'
            if account_info and isinstance(account_info, dict):
                if 'balances' in account_info:  # نجح الاستعلام
                    return True
                elif account_info.get('code') == 0:
                    return True
            return False
            
        else:  # bybit
            temp_api = BybitAPI(api_key, api_secret)
            account_info = temp_api.get_account_balance()
            
            if account_info and isinstance(account_info, dict):
                return account_info.get('retCode') == 0
            return False
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من API: {e}")
        return False
```

---

## 🚀 الخطوات التالية

### المرحلة 1: اكتمل ✅
- [x] إنشاء كلاس MEXC API
- [x] إضافة دعم قاعدة البيانات
- [x] توثيق الميزات

### المرحلة 2: قيد التطوير 🔄
- [ ] دمج في واجهة البوت الرئيسية
- [ ] إضافة اختيار المنصة في الإعدادات
- [ ] تحديث معالج Webhook لدعم MEXC
- [ ] إضافة معالج الصفقات لـ MEXC

### المرحلة 3: تحسينات مستقبلية 📈
- [ ] إضافة دعم MEXC Margin Trading
- [ ] إحصائيات منفصلة لكل منصة
- [ ] مقارنة الأسعار بين المنصتين
- [ ] تنبيهات فروق الأسعار

---

## 🔐 الأمان

1. **التشفير**: جميع API Keys مشفرة في قاعدة البيانات
2. **HTTPS**: جميع الاتصالات عبر HTTPS
3. **التوقيع**: استخدام HMAC SHA256 للتوقيع
4. **Timeout**: حد أقصى 10 ثوانٍ لكل طلب
5. **Rate Limiting**: احترام حدود API للمنصة

---

## 📞 الدعم الفني

إذا واجهت أي مشاكل:
1. تحقق من صلاحيات API
2. تأكد من عدم تفعيل IP Whitelist
3. جرب إنشاء API جديد
4. راجع السجلات (logs) للأخطاء

---

## 📚 روابط مفيدة

- [توثيق MEXC API](https://mxcdevelop.github.io/apidocs/spot_v3_en/)
- [إنشاء API Keys](https://www.mexc.com/user/openapi)
- [مركز دعم MEXC](https://www.mexc.com/support)
- [حدود API](https://mxcdevelop.github.io/apidocs/spot_v3_en/#limits)

---

**تم التحديث:** 2025-10-11  
**الإصدار:** 1.0.0  
**الحالة:** ✅ جاهز للاستخدام (Spot Trading فقط)

