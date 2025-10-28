# إضافة منصة جديدة - دليل سريع

## 🔧 دالة التقريب الأساسية

كل منصة يجب أن تنفذ دالة `get_symbol_info` و `round_quantity` للمعالجة الصحيحة للكميات.

### مثال Bybit (مطبّق)

```python
# في BybitRealAccount
def get_symbol_info(self, category: str, symbol: str) -> Optional[Dict]:
    """الحصول على معلومات الرمز من Bybit API"""
    # ... code ...
    return {
        'qty_step': '0.001',
        'min_qty': 0.001,
        'max_qty': 1000.0,
        'qty_precision': 3,
    }

def round_quantity(self, qty: float, category: str, symbol: str) -> float:
    """تقريب الكمية بناءً على قواعد Bybit"""
    symbol_info = self.get_symbol_info(category, symbol)
    qty_step = float(symbol_info.get('qty_step', '0.001'))
    rounded_qty = round(qty / qty_step) * qty_step
    return round(rounded_qty, symbol_info.get('qty_precision', 6))
```

### للمنصات الجديدة (Binance, OKX, Bitget, ...)

#### 1️⃣ إنشاء ملف المنصة
```python
# api/exchanges/your_exchange.py
from api.exchange_base import ExchangeBase

class YourExchange(ExchangeBase):
    def get_symbol_info(self, market_type: str, symbol: str) -> Optional[Dict]:
        """
        الحصول على معلومات الرمز
        
        يجب أن يرجع:
        {
            'qty_step': '0.001',      # الخطوة المسموحة
            'min_qty': 0.001,          # الحد الأدنى
            'max_qty': 1000.0,         # الحد الأقصى
            'qty_precision': 3,       # دقة الكمية
        }
        """
        # استدعي API المنصة لجلب معلومات الرمز
        # ...
        
    def round_quantity(self, qty: float, market_type: str, symbol: str) -> float:
        """
        تقريب الكمية بناءً على قواعد المنصة
        
        المنطق:
        1. اجلب معلومات الرمز
        2. قرّب حسب qty_step
        3. تأكد من الحدود
        4. رجع الكمية المقربة
        """
        # يمكن استخدام الدالة من ExchangeBase أو تنفيذ خاص
        return super().round_quantity(qty, market_type, symbol)
```

#### 2️⃣ المفاتيح المطلوبة في get_symbol_info

| المفتاح | الوصف | مثال |
|---------|-------|------|
| `qty_step` | الخطوة المسموحة للكمية | `'0.001'` |
| `min_qty` | الحد الأدنى المسموح | `0.001` |
| `max_qty` | الحد الأقصى المسموح | `1000.0` |
| `qty_precision` | عدد المنازل العشرية | `3` |

#### 3️⃣ كيفية العمل

```
الإشارة → حساب الكمية → place_order → round_quantity
                                            ↓
                                    جلب معلومات الرمز من API
                                            ↓
                                    تقريب حسب qty_step
                                            ↓
                                    التحقق من الحدود
                                            ↓
                               ✅ كمية صالحة
```

## ✅ الفوائد

1. **تقريب موحد**: نفس المنطق لجميع المنصات
2. **تجنب الأخطاء**: لا مزيد من "Qty invalid"
3. **سهولة الإضافة**: فقط نفذ `get_symbol_info`
4. **توافق عام**: يعمل تلقائياً مع النظام الأساسي

## 📝 مثال كامل: Binance

```python
class BinanceExchange(ExchangeBase):
    def get_symbol_info(self, market_type: str, symbol: str):
        # استدعي Binance API
        result = self._make_request('GET', '/api/v3/exchangeInfo', {'symbol': symbol})
        
        filters = result['symbols'][0]['filters']
        lot_size = next(f for f in filters if f['filterType'] == 'LOT_SIZE')
        
        return {
            'qty_step': lot_size['stepSize'],
            'min_qty': float(lot_size['minQty']),
            'max_qty': float(lot_size['maxQty']),
            'qty_precision': len(lot_size['stepSize'].split('.')[-1]),
        }
```

## 🎯 الخلاصة

**دالة التقريب الأساسية جاهزة في ExchangeBase** - كل ما تحتاجه هو تنفيذ `get_symbol_info` في منصتك، والباقي يعمل تلقائياً!

