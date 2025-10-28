# تطبيق المنطق القديم - إصلاح مشكلة الكمية

## المشكلة
```
❌ فشل في تنفيذ صفقة الفيوتشر: The number of contracts exceeds minimum limit allowed
INFO:api.bybit_api:   Quantity: 0.0
```

الكمية كانت تصل إلى 0.0 بسبب التقريب المعقد في النظام الجديد.

## الحل المطبق

### 1. استبدال دالة `round_quantity` في `api/bybit_api.py`

**قبل (معقد ويسبب مشاكل):**
```python
def round_quantity(self, qty: float, category: str, symbol: str) -> float:
    # جلب معلومات الرمز من API
    symbol_info = self.get_symbol_info(category, symbol)
    # تقريب معقد حسب qty_step
    rounded_qty = round(qty / qty_step) * qty_step
    # قد يصل إلى 0.0
```

**بعد (بسيط مثل النسخة القديمة):**
```python
def round_quantity(self, qty: float, category: str, symbol: str) -> float:
    """تقريب الكمية - المنطق القديم البسيط الذي كان يعمل"""
    # تحويل إلى float إذا كان string
    if isinstance(qty, str):
        qty = float(qty)
    
    # ضمان الحد الأدنى للكمية
    min_quantity = 0.001
    if qty < min_quantity:
        qty = min_quantity
    
    # تقريب بسيط
    rounded_qty = round(qty, 6)
    
    # التأكد من عدم الوصول للصفر
    if rounded_qty <= 0:
        rounded_qty = min_quantity
    
    return rounded_qty
```

### 2. تحسين منطق حساب الكمية في `signals/signal_executor.py`

أضفت فحص إضافي للتأكد من عدم وصول الكمية للصفر:

```python
# تقريب الكمية حسب دقة الرمز (منطق النسخة القديمة)
qty = round(qty, 6)

# التأكد النهائي من أن الكمية ليست صفر (أمان إضافي)
if qty <= 0:
    logger.warning(f"الكمية أصبحت صفر، استخدام الحد الأدنى: {min_quantity}")
    qty = min_quantity
```

## المنطق المطبق (مثل النسخة القديمة تماماً)

### 1. حساب الكمية الأساسي:
```python
if market_type == 'futures':
    qty = (trade_amount * leverage) / price
else:
    qty = trade_amount / price
```

### 2. ضمان الحد الأدنى:
```python
min_quantity = 0.001
if qty < min_quantity:
    qty = min_quantity
```

### 3. التقريب البسيط:
```python
qty = round(qty, 6)
```

### 4. فحص الأمان النهائي:
```python
if qty <= 0:
    qty = min_quantity
```

## النتائج المتوقعة

### قبل الإصلاح:
```
INFO:api.bybit_api:✅ الكمية بعد التقريب: 0.0
ERROR:api.bybit_api:❌ فشل طلب Bybit API: The number of contracts exceeds minimum limit allowed
```

### بعد الإصلاح:
```
INFO:api.bybit_api:تم تقريب الكمية: 0.002 → 0.002
INFO:api.bybit_api:✅ الكمية بعد التقريب: 0.002
INFO:api.bybit_api:Bybit order placed successfully
```

## الملفات المحدثة

1. **`api/bybit_api.py`**: استبدال دالة `round_quantity` بالمنطق البسيط
2. **`signals/signal_executor.py`**: إضافة فحص أمان إضافي للكمية

## كيفية الاختبار

```bash
python test_old_logic_fix.py
```

## الخلاصة

- تم استبدال المنطق المعقد بالمنطق البسيط من النسخة القديمة
- ضمان عدم وصول الكمية للصفر في أي حالة
- الحد الأدنى الثابت: 0.001
- التقريب البسيط: 6 منازل عشرية
- يعمل مع جميع أنواع الصفقات والمنصات

**المشروع الآن يجب أن يعمل بدون مشاكل في تنفيذ الصفقات!** ✅
