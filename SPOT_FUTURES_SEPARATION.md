# 💱⚡ فصل Spot و Futures في المحفظة والإحصائيات

## ✅ التحديثات المكتملة

### 1. قاعدة البيانات - دعم Spot/Futures منفصل
**الملف:** `users/database.py`

#### 🆕 الدوال الجديدة:

##### أ) `get_portfolio_evolution()` - محسّنة
```python
get_portfolio_evolution(user_id, account_type, days, market_type=None)
```
- **market_type=None**: يعرض الرصيد الإجمالي
- **market_type='spot'**: يعرض رصيد Spot فقط
- **market_type='futures'**: يعرض رصيد Futures فقط

##### ب) `get_portfolio_evolution_by_market()` - جديدة
```python
get_portfolio_evolution_by_market(user_id, account_type, market_type, days)
```
- تجلب تطور المحفظة لسوق محدد (Spot أو Futures)
- تستخدم الحقول `spot_balance` و `futures_balance` من جدول `portfolio_snapshots`

---

### 2. نظام الإحصائيات المتقدم - دعم Spot/Futures
**الملف:** `systems/advanced_statistics.py`

#### 🔄 الدوال المحدّثة:

##### أ) `calculate_trade_statistics()` - محسّنة
```python
calculate_trade_statistics(user_id, account_type, days, market_type=None)
```
- يضيف فلتر `market_type` إلى `filters` عند الاستعلام من قاعدة البيانات
- يحسب الإحصائيات لسوق محدد أو للكل

##### ب) `format_statistics_message()` - محسّنة
```python
format_statistics_message(user_id, account_type, days, market_type=None)
```
**يعرض:**
```
🎮 حساب تجريبي | 💱 SPOT
📊 ADVANCED STATISTICS (30 يوم)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 أداء المحفظة:
• العائد الإجمالي: +234.56 USDT (+2.35%)
• أعلى رصيد: 10,234.56 USDT
...

💼 إحصائيات الصفقات:
• إجمالي الصفقات: 15 (Spot فقط)
• معدل الفوز: 66.7%
...
```

**الأزرار الجديدة:**
```
[📊 الكل] [💱 Spot] [⚡ Futures]
[📅 7د] [📅 30د] [📅 90د]
[📊 تطور المحفظة] [🔄 تحديث]
[🏠 القائمة الرئيسية]
```

##### ج) `format_portfolio_evolution_message()` - محسّنة
```python
format_portfolio_evolution_message(user_id, account_type, days, market_type=None)
```
**يعرض:**
```
🎮 حساب تجريبي | ⚡ FUTURES
📊 PORTFOLIO EVOLUTION (30 يوم)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Max: 5,234.56
●╱╱━╲╱╱━━╱╱╱╱━╲╲━━╱╱╱
📉 Min: 4,876.54

💰 الرصيد:
• البداية: 5,000.00 USDT
• الحالي: 5,234.56 USDT
• التغير: +234.56 USDT (+4.69%) 🟢

📈 الاتجاه: صاعد

📅 الفترة:
• من: 2025-01-01
• إلى: 2025-01-30
• عدد الأيام: 30

📊 آخر 5 أيام:
• 2025-01-26: 5,100.23 USDT
• 2025-01-27: 5,150.45 USDT
• 2025-01-28: 5,200.67 USDT
• 2025-01-29: 5,180.89 USDT
• 2025-01-30: 5,234.56 USDT
```

**الأزرار الجديدة:**
```
[📊 الكل] [💱 Spot] [⚡ Futures]
[📅 7د] [📅 30د] [📅 90د]
[📅 365د]
[📊 الإحصائيات] [🔄 تحديث]
[🏠 القائمة الرئيسية]
```

---

### 3. التكامل مع البوت - معالجات Callback محسّنة
**الملف:** `bybit_trading_bot.py`

#### 🔄 المعالجات المحدّثة:

##### أ) معالج `stats_` - محسّن
```python
if data.startswith("stats_"):
    parts = data.split("_")
    account_type = parts[1]
    days = int(parts[2])
    market_type = parts[3] if len(parts) >= 4 else None  # 🆕 دعم market_type
```

**أمثلة على callback_data:**
- `stats_demo_30` → إحصائيات تجريبية، 30 يوم، الكل
- `stats_demo_30_spot` → إحصائيات تجريبية، 30 يوم، Spot فقط
- `stats_real_7_futures` → إحصائيات حقيقية، 7 أيام، Futures فقط

##### ب) معالج `portfolio_evolution_` - محسّن
```python
if data.startswith("portfolio_evolution_"):
    parts = data.replace("portfolio_evolution_", "").split("_")
    account_type = parts[0]
    days = int(parts[1])
    market_type = parts[2] if len(parts) >= 3 else None  # 🆕 دعم market_type
```

**أمثلة على callback_data:**
- `portfolio_evolution_demo_30` → محفظة تجريبية، 30 يوم، الكل
- `portfolio_evolution_demo_30_spot` → محفظة تجريبية، 30 يوم، Spot فقط
- `portfolio_evolution_real_90_futures` → محفظة حقيقية، 90 يوم، Futures فقط

---

## 🎯 كيفية الاستخدام

### 1. عرض المحفظة مع فصل Spot/Futures:
```
/portfolio
```

**الخطوات:**
1. يعرض المحفظة الإجمالية (Spot + Futures)
2. اضغط على **💱 Spot** لعرض رصيد Spot فقط
3. اضغط على **⚡ Futures** لعرض رصيد Futures فقط
4. اضغط على **📊 الكل** للعودة للعرض الإجمالي

### 2. عرض الإحصائيات مع فصل Spot/Futures:
```
/statistics
```

**الخطوات:**
1. يعرض الإحصائيات الإجمالية (جميع الصفقات)
2. اضغط على **💱 Spot** لعرض إحصائيات Spot فقط
3. اضغط على **⚡ Futures** لعرض إحصائيات Futures فقط
4. اضغط على **📊 الكل** للعودة للعرض الإجمالي

### 3. التبديل بين الفترات الزمنية:
- **📅 7د**: آخر 7 أيام
- **📅 30د**: آخر 30 يوم
- **📅 90د**: آخر 90 يوم
- **📅 365د**: آخر سنة (للمحفظة فقط)

---

## 📊 الفصل بين Demo و Real

### ✅ الحسابات التجريبية (Demo):
- **مصدر البيانات:** قاعدة البيانات (`trading_bot.db`)
- **الجداول المستخدمة:**
  - `orders` - الصفقات المفتوحة والمغلقة
  - `portfolio_snapshots` - اللقطات اليومية
  - `users` - بيانات المستخدم والرصيد
- **التحديث:** يتم حفظ كل صفقة في قاعدة البيانات
- **الرصيد:** يُحفظ في `users.balance` ويُحدّث بعد كل صفقة

### ✅ الحسابات الحقيقية (Real):
- **مصدر البيانات:** API المنصة (Bybit/Binance/Bitget)
- **الجداول المستخدمة:**
  - `orders` - نسخة محلية للصفقات (للسجل)
  - `portfolio_snapshots` - اللقطات اليومية
- **التحديث:** يتم جلب البيانات مباشرة من API
- **الرصيد:** يُجلب من API المنصة

---

## 🔄 آلية الحفظ والجلب

### 1. حفظ اللقطات اليومية:
```python
# يتم استدعاؤها تلقائياً عند عرض المحفظة أو الإحصائيات
advanced_stats.save_daily_snapshot(user_id, account_type)
```

**البيانات المحفوظة:**
- `balance`: الرصيد الإجمالي
- `spot_balance`: رصيد Spot
- `futures_balance`: رصيد Futures
- `total_pnl`: إجمالي الربح/الخسارة
- `open_positions_count`: عدد الصفقات المفتوحة
- `closed_trades_count`: عدد الصفقات المغلقة
- `winning_trades`: عدد الصفقات الرابحة
- `losing_trades`: عدد الصفقات الخاسرة
- `total_volume`: حجم التداول

### 2. جلب البيانات حسب نوع الحساب:

#### أ) Demo Account:
```python
# جلب الصفقات من قاعدة البيانات
trades = db_manager.get_user_trade_history(user_id, {
    'status': 'CLOSED',
    'account_type': 'demo',
    'market_type': 'spot'  # أو 'futures' أو None للكل
})

# جلب تطور المحفظة من قاعدة البيانات
snapshots = db_manager.get_portfolio_evolution_by_market(
    user_id, 'demo', 'spot', days=30
)
```

#### ب) Real Account:
```python
# جلب الصفقات من API
from api.bybit_api import real_account_manager
api_client = real_account_manager.get_account(user_id)
positions = api_client.get_open_positions('linear')  # Futures
# أو
positions = api_client.get_open_positions('spot')  # Spot

# جلب تطور المحفظة من قاعدة البيانات (اللقطات المحفوظة)
snapshots = db_manager.get_portfolio_evolution_by_market(
    user_id, 'real', 'futures', days=30
)
```

---

## 📈 أمثلة على الاستخدام

### مثال 1: عرض محفظة Spot التجريبية لآخر 7 أيام
```
1. /portfolio
2. اضغط على [💱 Spot]
3. اضغط على [📅 7د]
```
**النتيجة:**
- يعرض رسم بياني لتطور رصيد Spot فقط
- يعرض الرصيد الحالي لـ Spot
- يعرض التغير خلال آخر 7 أيام

### مثال 2: عرض إحصائيات Futures الحقيقية لآخر 90 يوم
```
1. /statistics
2. اضغط على [⚡ Futures]
3. اضغط على [📅 90د]
```
**النتيجة:**
- يعرض إحصائيات صفقات Futures فقط
- يعرض معدل الفوز، Profit Factor، إلخ
- يعرض أفضل/أسوأ صفقة في Futures

### مثال 3: المقارنة بين Spot و Futures
```
1. /portfolio
2. اضغط على [💱 Spot] → شاهد رصيد Spot
3. اضغط على [⚡ Futures] → شاهد رصيد Futures
4. اضغط على [📊 الكل] → شاهد الرصيد الإجمالي
```

---

## 🔗 الترابط الكامل مع قاعدة البيانات

### ✅ جميع البيانات محفوظة:
1. **الصفقات** → `orders` (مع `market_type`)
2. **اللقطات اليومية** → `portfolio_snapshots` (مع `spot_balance` و `futures_balance`)
3. **إعدادات المستخدم** → `user_settings` (مع `market_type`)
4. **بيانات المستخدم** → `users` (مع `balance`)

### 🔄 التحديث التلقائي:
- يتم حفظ لقطة يومية واحدة (INSERT OR REPLACE)
- يتم تحديث `spot_balance` و `futures_balance` تلقائياً
- البيانات دائمة ولا تُفقد عند إعادة التشغيل

### 🗑️ إعادة التعيين:
- عند "إعادة تعيين كل المشروع"
- يتم حذف جميع البيانات بما فيها اللقطات
- يتم إعادة إنشاء قاعدة البيانات من الصفر

---

## 🎉 الخلاصة

تم تطوير نظام متقدم لفصل Spot و Futures يشمل:

✅ **قاعدة بيانات محسّنة** مع دعم `spot_balance` و `futures_balance`
✅ **دوال جديدة** لجلب البيانات حسب نوع السوق
✅ **إحصائيات منفصلة** لـ Spot و Futures
✅ **رسوم بيانية منفصلة** لتطور كل سوق
✅ **أزرار تفاعلية** للتبديل بين Spot/Futures/الكل
✅ **فصل كامل** بين Demo (من DB) و Real (من API)
✅ **ترابط كامل** مع قاعدة البيانات
✅ **حفظ تلقائي** للبيانات

---

## 📝 ملاحظات مهمة

1. **اللقطات اليومية** تُحفظ مع `spot_balance` و `futures_balance` منفصلين
2. **الفلاتر** تعمل على مستوى قاعدة البيانات (سريعة وفعالة)
3. **البيانات الحقيقية** تُجلب من API ولكن اللقطات تُحفظ في DB
4. **البيانات التجريبية** تُجلب بالكامل من DB
5. **التبديل** بين Spot/Futures فوري وبدون تأخير

---

**🎯 النظام جاهز للاستخدام بالكامل مع فصل تام بين Spot و Futures!**

