# 📚 الدليل المفصل لبوت التداول Bybit

## 🎯 نظرة عامة

بوت Telegram متعدد المستخدمين لإدارة التداول على منصة Bybit، يدعم:
- ✅ التداول التجريبي والحقيقي
- ✅ إدارة الصفقات التفاعلية (TP/SL/Partial Close)
- ✅ دعم أسواق Spot و Futures
- ✅ نظام متعدد المستخدمين مع عزل كامل

---

## 🔧 المشكلة التي تم إصلاحها

### 🐛 المشكلة السابقة
عند تلقي إشارة صفقة والضغط على أي زر من أزرار الصفقات المفتوحة، كان يظهر خطأ:
```
❌ الصفقة غير موجودة
```

### 🔍 سبب المشكلة
كانت دوال البحث عن الصفقات تبحث فقط في `trading_bot.open_positions` ولا تغطي:
- الصفقات في الحسابات التجريبية (`demo_account_spot`)
- الصفقات في الحسابات التجريبية (`demo_account_futures`)
- الصفقات في حسابات المستخدمين الأخرى

### ✅ الحل المطبق
تم توسيع نطاق البحث في 3 ملفات رئيسية:

#### 1. **trade_button_handler.py**
- إضافة دالة `_get_position_info()` للبحث الشامل
- تحديث `_position_exists()` للبحث في جميع المصادر
- تحديث `_show_trade_message()` لاستخدام الدالة الجديدة

```python
def _get_position_info(self, position_id: str) -> dict:
    """الحصول على معلومات الصفقة من جميع المصادر"""
    # البحث في القائمة العامة
    # البحث في demo_account_spot
    # البحث في demo_account_futures
    # البحث عبر user_manager
```

#### 2. **trade_executor.py**
- إضافة نفس دالة `_get_position_info()`
- تحديث جميع الدوال: `set_take_profit()`, `set_stop_loss()`, `partial_close()`, `close_position()`

#### 3. **trade_manager.py**
- إضافة دالة `_get_position_info()` للبحث في صفقة واحدة
- إضافة دالة `_get_all_positions()` لجلب جميع الصفقات
- تحديث جميع الدوال المعتمدة على الصفقات

---

## 🏗️ البنية المعمارية

### 📁 الملفات الرئيسية

```
botbybit/
├── bybit_trading_bot.py          # البوت الرئيسي + منطق التداول
├── trade_button_handler.py       # معالجة أزرار الصفقات التفاعلية
├── trade_executor.py             # تنفيذ أوامر TP/SL/Close
├── trade_manager.py              # إدارة الصفقات
├── trade_messages.py             # رسائل وأزرار الصفقات
├── user_manager.py               # إدارة المستخدمين
├── database.py                   # قاعدة بيانات SQLite
├── web_server.py                 # واجهة ويب
├── app.py                        # تطبيق Flask الرئيسي
├── config.py                     # الإعدادات
└── run_with_server.py            # نقطة البدء
```

### 🔗 العلاقات بين المكونات

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot                          │
│                (bybit_trading_bot.py)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
┌─────▼─────┐ ┌───▼────┐ ┌────▼──────┐
│ Trade     │ │ User   │ │ Bybit     │
│ Manager   │ │ Manager│ │ API       │
└─────┬─────┘ └────────┘ └───────────┘
      │
┌─────┴──────────┬──────────────┐
│                │              │
▼                ▼              ▼
Trade Button   Trade         Trade
Handler        Executor      Messages
```

---

## 🎮 كيفية عمل نظام الصفقات

### 1️⃣ **إنشاء صفقة جديدة**

```python
# في bybit_trading_bot.py
async def execute_demo_trade():
    # 1. إنشاء صفقة في الحساب التجريبي
    account = get_current_account()
    success, position_id = account.open_futures_position(...)
    
    # 2. حفظ الصفقة في القائمة العامة
    self.open_positions[position_id] = {
        'symbol': symbol,
        'side': side,
        'entry_price': price,
        ...
    }
```

### 2️⃣ **عرض الصفقة التفاعلية**

```python
# عند الضغط على "🎯 الصفقات التفاعلية"
async def interactive_trades():
    # 1. جلب جميع الصفقات
    positions = trade_manager._get_all_positions()
    
    # 2. إرسال رسالة لكل صفقة مع أزرار تفاعلية
    for position_id, position_info in positions.items():
        message, keyboard = create_trade_message(position_info)
        await send_message(message, keyboard)
```

### 3️⃣ **معالجة الأزرار**

```python
# عند الضغط على أي زر (TP/SL/Close)
async def handle_trade_callback():
    # 1. التحقق من وجود الصفقة (البحث الشامل)
    if not _position_exists(position_id):
        return "❌ الصفقة غير موجودة"
    
    # 2. جلب معلومات الصفقة
    position_info = _get_position_info(position_id)
    
    # 3. معالجة العملية المطلوبة
    if action == "tp":
        await _handle_tp_button()
    elif action == "sl":
        await _handle_sl_button()
    elif action == "close":
        await _handle_close_button()
```

### 4️⃣ **تنفيذ الأمر**

```python
# في trade_executor.py
async def set_take_profit(position_id, percent):
    # 1. جلب معلومات الصفقة
    position_info = _get_position_info(position_id)
    
    # 2. حساب سعر TP
    tp_price = calculate_tp_price(position_info, percent)
    
    # 3. حفظ الأمر
    self.active_orders[order_id] = tp_order
    
    # 4. تنفيذ في المنصة (إذا كان حساب حقيقي)
    if account_type == 'real':
        await _place_real_tp_order(position_info, tp_price)
```

---

## 🔍 آلية البحث عن الصفقات (محدثة)

### 🔎 دالة البحث الشاملة

```python
def _get_position_info(position_id: str) -> dict:
    """
    البحث عن الصفقة بالترتيب:
    1. القائمة العامة (trading_bot.open_positions)
    2. حساب السبوت التجريبي (demo_account_spot.positions)
    3. حساب الفيوتشر التجريبي (demo_account_futures.positions)
    4. جميع حسابات المستخدمين (عبر user_manager)
    """
    
    # المرحلة 1: البحث في القائمة العامة
    if position_id in self.trading_bot.open_positions:
        return self.trading_bot.open_positions[position_id]
    
    # المرحلة 2: البحث في الحسابات التجريبية
    if position_id in demo_account_spot.positions:
        position = demo_account_spot.positions[position_id]
        return convert_position_to_dict(position)
    
    if position_id in demo_account_futures.positions:
        position = demo_account_futures.positions[position_id]
        return convert_position_to_dict(position)
    
    # المرحلة 3: البحث في جميع حسابات المستخدمين
    for user_id, user_data in user_manager.users.items():
        account = user_manager.get_user_account(user_id, market_type)
        if position_id in account.positions:
            return convert_position_to_dict(account.positions[position_id])
    
    return None
```

### 🎯 مثال عملي

```
الصفقة ID: BTCUSDT_1696234567890123

1. البحث في open_positions → ❌ غير موجودة
2. البحث في demo_account_spot → ❌ غير موجودة
3. البحث في demo_account_futures → ✅ موجودة!
   
   إرجاع:
   {
       'symbol': 'BTCUSDT',
       'side': 'buy',
       'entry_price': 43500.0,
       'current_price': 43650.0,
       'amount': 0.1,
       'margin_amount': 100.0,
       'leverage': 10,
       'position_id': 'BTCUSDT_1696234567890123',
       'account_type': 'futures'
   }
```

---

## 🎨 الأزرار التفاعلية

### 📊 رسالة الصفقة

```
🔄 صفقة مفتوحة

📊 الرمز: BTCUSDT
📈 الاتجاه: شراء (Buy)
💰 سعر الدخول: 43,500.00
💵 السعر الحالي: 43,650.00
📊 الربح/الخسارة: +0.34% (+150.00 USDT)

🔹 الهامش: 100.00 USDT
⚡ الرافعة: 10x
📦 الكمية: 0.1000

┌──────────────────┐
│  🎯 TP: 1.5%     │ ← عند الضغط → تأكيد → تنفيذ
│  🎯 TP: 3.0%     │
│  🎯 TP: 5.0%     │
│  🛑 SL: 2%       │
│  📊 إغلاق 25%    │
│  📊 إغلاق 50%    │
│  ❌ إغلاق كامل    │
│  🔄 تحديث        │
└──────────────────┘
```

### 🔘 أنواع الأزرار

| الزر | الوظيفة | البيانات المرسلة |
|------|---------|------------------|
| 🎯 TP: X% | وضع هدف ربح | `tp_{position_id}_{percent}` |
| 🛑 SL: X% | وضع وقف خسارة | `sl_{position_id}_{percent}` |
| 📊 إغلاق X% | إغلاق جزئي | `partial_{position_id}_{percent}` |
| ❌ إغلاق كامل | إغلاق الصفقة | `close_{position_id}` |
| 🔄 تحديث | تحديث المعلومات | `refresh_{position_id}` |
| ⚙️ تعديل | تعديل النسب | `edit_{position_id}_{type}` |

---

## 🔐 نظام متعدد المستخدمين

### 👥 عزل المستخدمين

```python
# كل مستخدم له:
user_data = {
    'user_id': 123456789,
    'api_key': 'encrypted_key',
    'api_secret': 'encrypted_secret',
    'balance': 10000.0,
    'is_active': True,
    'market_type': 'futures',
    'account_type': 'demo',
    'trade_amount': 100.0,
    'leverage': 10
}

# حسابات منفصلة:
- demo_account_spot[user_id]
- demo_account_futures[user_id]
- open_positions[user_id]
```

### 🔒 الأمان

- ✅ عزل كامل بين المستخدمين
- ✅ لا يمكن لمستخدم الوصول لبيانات آخر
- ✅ تشفير API Keys
- ✅ جميع العمليات مرتبطة بـ `user_id`

---

## 🚀 كيفية التشغيل

### 📦 المتطلبات

```bash
pip install -r requirements.txt
```

### 🔑 المتغيرات البيئية

```env
# .env
TELEGRAM_TOKEN=your_telegram_bot_token
BYBIT_API_KEY=your_bybit_api_key (optional)
BYBIT_API_SECRET=your_bybit_api_secret (optional)
PORT=8080
```

### ▶️ التشغيل المحلي

```bash
python run_with_server.py
```

### ☁️ التشغيل على Railway

```bash
# يتم تشغيل app.py تلقائياً
# railway.toml يحدد نقطة البدء
```

---

## 🎯 أوامر البوت

### 📝 الأوامر الأساسية

| الأمر | الوصف |
|-------|-------|
| `/start` | بدء البوت وعرض القائمة الرئيسية |
| `⚙️ الإعدادات` | فتح قائمة الإعدادات |
| `📊 حالة الحساب` | عرض معلومات الحساب |
| `🔄 الصفقات المفتوحة` | عرض الصفقات المفتوحة |
| `📈 تاريخ التداول` | عرض سجل الصفقات |
| `💰 المحفظة` | عرض الرصيد والأرباح |
| `🎯 الصفقات التفاعلية` | عرض الصفقات مع أزرار تفاعلية |

### ⚙️ الإعدادات المتاحة

```
⚙️ الإعدادات
├── 💰 مبلغ التداول (50-10000 USDT)
├── 🏪 نوع السوق (Spot / Futures)
├── 👤 نوع الحساب (تجريبي / حقيقي)
├── ⚡ الرافعة المالية (1x-125x)
├── 💳 رصيد الحساب التجريبي
├── 🔗 تحديث API Keys
└── ▶️/⏹️ تشغيل/إيقاف البوت
```

---

## 📈 سيناريو استخدام كامل

### 1️⃣ إعداد البوت

```
المستخدم: /start
البوت: مرحباً! اضغط على "🔗 ربط API"

المستخدم: يرسل API_KEY
البوت: الآن أرسل API_SECRET

المستخدم: يرسل API_SECRET
البوت: ✅ تم ربط API بنجاح!
```

### 2️⃣ تلقي إشارة

```
TradingView → Webhook → البوت

{
    "symbol": "BTCUSDT",
    "action": "buy",
    "price": 43500
}

البوت: 
✅ تم فتح صفقة جديدة
📊 BTCUSDT
📈 شراء @ 43,500.00
💰 المبلغ: 100 USDT
⚡ الرافعة: 10x
```

### 3️⃣ إدارة الصفقة

```
المستخدم: يضغط "🎯 الصفقات التفاعلية"
البوت: يرسل رسالة تفاعلية للصفقة مع أزرار

المستخدم: يضغط "🎯 TP: 1.5%"
البوت: هل تريد وضع TP عند 1.5%؟ [نعم] [لا]

المستخدم: يضغط "نعم"
البوت: ✅ تم وضع TP عند 44,152.50
```

### 4️⃣ إغلاق الصفقة

```
المستخدم: يضغط "📊 إغلاق 50%"
البوت: تأكيد إغلاق 50% من الصفقة؟

المستخدم: تأكيد
البوت: 
✅ تم الإغلاق الجزئي
💰 الربح: +75.00 USDT
📊 المتبقي: 50%
```

---

## 🐛 استكشاف الأخطاء

### ❌ "الصفقة غير موجودة"

**الحل:** تم إصلاحه! الآن يبحث في جميع المصادر.

### ❌ "API غير متصل"

```python
# التحقق من:
1. صحة API_KEY و API_SECRET
2. صلاحيات API في Bybit
3. اتصال الإنترنت
```

### ❌ "الرصيد غير كافي"

```python
# للحساب التجريبي:
الإعدادات → 💳 رصيد الحساب التجريبي → إدخال رصيد جديد

# للحساب الحقيقي:
إيداع USDT في حساب Bybit
```

---

## 📝 ملاحظات مهمة

### ⚠️ تحذيرات

1. **الحساب الحقيقي**: استخدم بحذر، الأموال حقيقية!
2. **الرافعة المالية**: رافعة عالية = مخاطر عالية
3. **API Keys**: لا تشارك مفاتيح API مع أي شخص
4. **الاختبار**: اختبر جيداً على الحساب التجريبي أولاً

### ✅ أفضل الممارسات

1. استخدم الحساب التجريبي للتجربة
2. ابدأ بمبالغ صغيرة
3. ضع دائماً Stop Loss
4. راقب الصفقات بانتظام
5. لا تستخدم رافعة عالية في البداية

---

## 🔄 التحديثات القادمة

- [ ] إضافة إشعارات Telegram عند تفعيل TP/SL
- [ ] دعم المزيد من أنواع الأوامر (Trailing Stop)
- [ ] واجهة ويب محسنة
- [ ] تحليلات وإحصائيات متقدمة
- [ ] دعم المزيد من المنصات

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- افتح Issue على GitHub
- راجع [INTEGRATION_GUIDE_AR.md](INTEGRATION_GUIDE_AR.md)
- راجع [MULTI_USER_GUIDE.md](MULTI_USER_GUIDE.md)

---

## 📜 الترخيص

هذا المشروع للاستخدام الشخصي. استخدمه على مسؤوليتك الخاصة.

---

## 🎉 شكر خاص

- مجتمع Bybit
- مطوري python-telegram-bot
- جميع المساهمين في المشروع

---

**آخر تحديث:** 2025-10-04
**الإصدار:** 2.0.0 (بعد إصلاح مشكلة البحث عن الصفقات)

