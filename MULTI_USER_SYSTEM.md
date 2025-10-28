# نظام المستخدم المتعدد - العزل الكامل

## ✅ الميزات المنجزة

### 1. 🔐 **عزل مفاتيح API**
كل مستخدم له مفاتيح API الخاصة به منفصلة تماماً:

```python
- bybit_api_key / bybit_api_secret
- bitget_api_key / bitget_api_secret  
- binance_api_key / binance_api_secret
- okx_api_key / okx_api_secret
```

### 2. 🏦 **عزل الحسابات**
- كل مستخدم له حسابات تجريبية منفصلة (Spot + Futures)
- كل مستخدم له اتصال API خاص بمنصته المفضلة
- البيانات منفصلة تماماً في الذاكرة

### 3. ⚙️ **عزل الإعدادات**
كل مستخدم له إعداداته الخاصة:
- `market_type`: spot أو futures
- `account_type`: demo أو real
- `trade_amount`: مبلغ التداول
- `leverage`: الرافعة المالية
- `exchange`: المنصة المفضلة (bybit, bitget, binance, okx)

### 4. 📊 **عزل الصفقات**
كل مستخدم له:
- قائمة صفقاته الخاصة في الذاكرة
- صفقاته في قاعدة البيانات مرتبطة بـ user_id
- لا يمكن لمستخدم أن يرى صفقات مستخدم آخر

### 5. 💰 **عزل الأرصدة**
كل مستخدم له:
- رصيد مستقل في الحسابات التجريبية
- رصيد مستقل في الحسابات الحقيقية
- تاريخ تداول منفصل

## 📋 هيكل قاعدة البيانات

### جدول `users`
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    api_key TEXT,                    -- مفاتيح عامة
    api_secret TEXT,
    
    -- مفاتيح Bybit
    bybit_api_key TEXT,
    bybit_api_secret TEXT,
    
    -- مفاتيح Bitget
    bitget_api_key TEXT,
    bitget_api_secret TEXT,
    
    -- مفاتيح Binance
    binance_api_key TEXT,
    binance_api_secret TEXT,
    
    -- مفاتيح OKX
    okx_api_key TEXT,
    okx_api_secret TEXT,
    
    exchange TEXT DEFAULT 'bybit',    -- المنصة المفضلة
    balance REAL DEFAULT 10000.0,
    is_active BOOLEAN DEFAULT 1,
    ...
)
```

### جدول `user_settings`
```sql
CREATE TABLE user_settings (
    user_id INTEGER PRIMARY KEY,
    market_type TEXT DEFAULT 'spot',
    trade_amount REAL DEFAULT 100.0,
    leverage INTEGER DEFAULT 10,
    account_type TEXT DEFAULT 'demo',
    ...
)
```

### جدول `orders`
```sql
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,         -- مرتبط بالمستخدم
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    ...
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
```

## 🔄 تدفق العمل

### عند إنشاء مستخدم جديد:
1. يتم إنشاء سجل في جدول `users`
2. يتم إنشاء إعدادات افتراضية في `user_settings`
3. يتم إنشاء حسابات تجريبية منفصلة (Spot + Futures)
4. يتم تهيئة قائمة صفقات فارغة للمستخدم

### عند تحميل المستخدمين:
```python
for user_data in users_data:
    user_id = user_data['user_id']
    
    # 1. تحميل بيانات المستخدم
    self.users[user_id] = user_data
    
    # 2. إنشاء حسابات تجريبية
    self._create_user_accounts(user_id, user_data)
    
    # 3. إنشاء API حسب المنصة
    exchange = user_data.get('exchange', 'bybit')
    if exchange == 'bybit':
        api_key = user_data.get('bybit_api_key')
    elif exchange == 'bitget':
        api_key = user_data.get('bitget_api_key')
    # ... إلخ
    
    # 4. تهيئة الحساب الحقيقي
    real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
```

### عند تنفيذ صفقة:
1. تحديد المستخدم من `user_id`
2. تحميل الإعدادات الخاصة بالمستخدم
3. استخدام الحساب الحقيقي للمستخدم
4. حفظ الصفقة مرتبطة بـ `user_id`

## 🛡️ ميزات الأمان

### 1. **العزل الكامل**
- لا يمكن لمستخدم الوصول لبيانات مستخدم آخر
- كل عمليات البحث مقيدة بـ `user_id`

### 2. **تشفير المفاتيح**
```python
# يتم تخزين المفاتيح كـ plain text حالياً
# يمكن إضافة تشفير لاحقاً
```

### 3. **الصلاحيات**
```python
# كل مستخدم يمكنه:
- عرض صفقاته فقط
- تعديل إعداداته فقط
- التنفيذ على حسابه فقط
```

## 📝 استخدام النظام

### إضافة مفاتيح API للمستخدم:
```python
from users.database import db_manager

# إضافة مفاتيح Bybit
db_manager.update_user_data(user_id, {
    'exchange': 'bybit',
    'bybit_api_key': 'your_api_key',
    'bybit_api_secret': 'your_api_secret'
})

# إضافة مفاتيح Bitget
db_manager.update_user_data(user_id, {
    'exchange': 'bitget',
    'bitget_api_key': 'your_api_key',
    'bitget_api_secret': 'your_api_secret'
})
```

### الحصول على بيانات المستخدم:
```python
from users.user_manager import user_manager

user_data = user_manager.get_user(user_id)
settings = user_manager.get_user_settings(user_id)
positions = user_manager.get_user_positions(user_id)
```

## 🎯 مثال عملي

### المستخدم 1:
- المنصة: Bybit
- نوع السوق: Futures
- المبلغ: 50 USDT
- الرافعة: 5x
- صفقاته: [BTCUSDT Long, ETHUSDT Short]

### المستخدم 2:
- المنصة: Bitget
- نوع السوق: Spot
- المبلغ: 100 USDT
- الرافعة: 1x (Spot)
- صفقاته: [BTCUSDT Buy, ETHUSDT Buy]

### المستخدم 3:
- المنصة: OKX
- نوع السوق: Futures
- المبلغ: 200 USDT
- الرافعة: 10x
- صفقاته: [SOLUSDT Long]

## ✅ النتيجة

كل مستخدم له:
- ✅ اتصاله الخاص بمنصته
- ✅ إعداداته الخاصة
- ✅ صفقاته الخاصة
- ✅ أرصدته الخاصة
- ✅ مفاتيح API الخاصة
- ✅ حساب تجريبي منفصل
- ✅ حساب حقيقي منفصل

**العزل كامل 100%** 🎉

