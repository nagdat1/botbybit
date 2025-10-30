# ✅ إصلاح الخطأ: AttributeError 'get_portfolio_evolution_by_market'

## 🐛 المشكلة:
```
AttributeError: 'DatabaseManager' object has no attribute 'get_portfolio_evolution_by_market'
```

## 🔧 السبب:
الدالة `get_portfolio_evolution_by_market()` كانت مفقودة من ملف `users/database.py`

## ✅ الحل المطبق:

### تم إضافة دالتين في `users/database.py`:

#### 1. تحديث `get_portfolio_evolution()` - السطر 1792
```python
def get_portfolio_evolution(self, user_id: int, account_type: str, days: int = 30, market_type: str = None) -> list:
    """الحصول على تطور المحفظة خلال فترة محددة (مع دعم Spot/Futures)"""
    # ...
    # إذا كان market_type محدد، استخدم الرصيد المناسب
    if market_type == 'spot':
        snapshot['balance'] = row[8]  # spot_balance
    elif market_type == 'futures':
        snapshot['balance'] = row[9]  # futures_balance
```

#### 2. إضافة `get_portfolio_evolution_by_market()` - السطر 1843
```python
def get_portfolio_evolution_by_market(self, user_id: int, account_type: str, market_type: str, days: int = 30) -> list:
    """الحصول على تطور المحفظة حسب نوع السوق (Spot أو Futures)"""
    try:
        from datetime import date, timedelta
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            start_date = (date.today() - timedelta(days=days)).isoformat()
            
            # جلب اللقطات اليومية
            cursor.execute("""
                SELECT snapshot_date, spot_balance, futures_balance, created_at
                FROM portfolio_snapshots
                WHERE user_id = ? AND account_type = ? AND snapshot_date >= ?
                ORDER BY snapshot_date ASC
            """, (user_id, account_type, start_date))
            
            rows = cursor.fetchall()
            
            snapshots = []
            for row in rows:
                balance = row[1] if market_type == 'spot' else row[2]
                snapshots.append({
                    'date': row[0],
                    'balance': balance,
                    'created_at': row[3]
                })
            
            return snapshots
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على تطور المحفظة حسب السوق: {e}")
        return []
```

## 🎯 كيفية الاستخدام:

### مثال 1: جلب تطور المحفظة الإجمالية
```python
snapshots = db_manager.get_portfolio_evolution(user_id, 'demo', days=30)
# يعيد الرصيد الإجمالي (spot_balance + futures_balance)
```

### مثال 2: جلب تطور محفظة Spot فقط
```python
snapshots = db_manager.get_portfolio_evolution_by_market(user_id, 'demo', 'spot', days=30)
# يعيد رصيد Spot فقط
```

### مثال 3: جلب تطور محفظة Futures فقط
```python
snapshots = db_manager.get_portfolio_evolution_by_market(user_id, 'real', 'futures', days=90)
# يعيد رصيد Futures فقط
```

## ✅ النتيجة:
- ✅ الخطأ تم إصلاحه
- ✅ الدالة `get_portfolio_evolution_by_market()` متاحة الآن
- ✅ دعم كامل لفصل Spot و Futures
- ✅ يعمل مع الحسابات التجريبية والحقيقية

## 🔄 الخطوات التالية:
1. أعد تشغيل البوت
2. جرب `/portfolio`
3. اضغط على **💱 Spot** أو **⚡ Futures**
4. يجب أن يعمل بدون أخطاء الآن!

---

**تم الإصلاح بنجاح! ✅**

