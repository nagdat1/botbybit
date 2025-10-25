# نظام إصلاح مشكلة عدم كفاية الرصيد

## نظرة عامة

هذا النظام يحل مشكلة "الرصيد غير كافي" التي تحدث عند تنفيذ الإشارات على Bybit. النظام يوفر:

- ✅ تحقق محسن من الرصيد قبل تنفيذ الأوامر
- ✅ اقتراحات ذكية للكميات المثلى
- ✅ معالجة شاملة للأخطاء
- ✅ نظام fallback متعدد المستويات
- ✅ تشخيص مفصل لمشاكل الرصيد

## الملفات المضافة

### 1. `balance_fix_system.py`
النظام الأساسي للتحقق من الرصيد:
- `BalanceValidator`: مدقق الرصيد المحسن
- `EnhancedSignalExecutor`: منفذ الإشارات مع التحقق من الرصيد

### 2. `comprehensive_balance_fix.py`
النظام الشامل الذي يدمج جميع الحلول:
- `ComprehensiveBalanceFix`: النظام الرئيسي للإصلاح الشامل
- دعم متعدد المستويات مع fallback
- اقتراحات ذكية للمستخدم

### 3. `test_balance_fix.py`
ملف اختبار للنظام الأساسي

### 4. `run_balance_fix_test.py`
ملف تشغيل سريع لاختبار النظام

## كيفية الاستخدام

### 1. التشغيل التلقائي
النظام يعمل تلقائياً عند تنفيذ الإشارات. لا حاجة لتعديل الكود الحالي.

### 2. الاختبار اليدوي
```bash
python run_balance_fix_test.py
```

### 3. الاستخدام المباشر
```python
from comprehensive_balance_fix import comprehensive_balance_fix

# تنفيذ إشارة مع الإصلاح الشامل
result = await comprehensive_balance_fix.execute_signal_with_comprehensive_fix(
    user_id, signal_data, user_data
)

# تشخيص مشكلة الرصيد
diagnosis = await comprehensive_balance_fix.diagnose_balance_issue(user_id)
```

## الميزات الجديدة

### 1. التحقق المحسن من الرصيد
- فحص دقيق للرصيد المتاح
- حساب الهامش المطلوب بدقة
- إضافة هامش أمان (5%)
- دعم أنواع مختلفة من الحسابات (Spot, Futures, Unified)

### 2. اقتراحات ذكية
عند عدم كفاية الرصيد، النظام يقترح:
- كمية مثلى بناءً على الرصيد المتاح
- تقليل الرافعة المالية
- تقليل مبلغ التداول
- إيداع المزيد من USDT

### 3. معالجة شاملة للأخطاء
- نظام متعدد المستويات مع fallback
- رسائل خطأ واضحة باللغة العربية
- تشخيص مفصل للمشاكل
- حلول مقترحة لكل مشكلة

### 4. دعم متعدد المنصات
- Bybit (Spot & Futures)
- MEXC (Spot)
- قابل للتوسع لمنصات أخرى

## أمثلة على الاستخدام

### مثال 1: إشارة شراء BTCUSDT
```python
signal_data = {
    'action': 'buy',
    'symbol': 'BTCUSDT',
    'price': 111084.4,
    'signal_id': '4',
    'has_signal_id': True
}

user_data = {
    'account_type': 'real',
    'exchange': 'bybit',
    'market_type': 'futures',
    'trade_amount': 55.0,
    'leverage': 1
}

result = await comprehensive_balance_fix.execute_signal_with_comprehensive_fix(
    user_id, signal_data, user_data
)
```

### مثال 2: تشخيص مشكلة الرصيد
```python
diagnosis = await comprehensive_balance_fix.diagnose_balance_issue(user_id)

if not diagnosis['success']:
    print(f"المشكلة: {diagnosis['message']}")
    for solution in diagnosis['solutions']:
        print(f"- {solution}")
```

## رسائل الخطأ المحسنة

### قبل الإصلاح
```
Failed to place order on Bybit: الرصيد غير كافي
```

### بعد الإصلاح
```
الرصيد غير كافي. متاح: 50.00 USDT، مطلوب: 61.10 USDT
الكمية المقترحة: 0.000405 BTC | أودع المزيد من USDT | قلل الرافعة المالية من 1x إلى 1x | قلل مبلغ التداول من 55 إلى 25
```

## التكامل مع النظام الحالي

النظام الجديد متكامل تماماً مع النظام الحالي:

1. **لا يحتاج تعديل**: يعمل تلقائياً مع `signal_executor.py`
2. **Fallback آمن**: إذا فشل النظام الجديد، يعود للنظام العادي
3. **متوافق**: يعمل مع جميع أنواع الإشارات والإعدادات الموجودة

## استكشاف الأخطاء

### مشكلة: النظام لا يعمل
```bash
# تحقق من الاستيراد
python -c "from comprehensive_balance_fix import comprehensive_balance_fix; print('OK')"
```

### مشكلة: أخطاء في مفاتيح API
- تأكد من صحة مفاتيح Bybit API
- تحقق من صلاحيات التداول
- تأكد من تفعيل الحساب الحقيقي

### مشكلة: الرصيد لا يظهر
- تحقق من وجود USDT في الحساب
- تأكد من نوع الحساب (Spot/Futures)
- تحقق من إعدادات الحساب الموحد

## الدعم

إذا واجهت مشاكل:
1. تحقق من السجلات (`trading_bot.log`)
2. استخدم `run_balance_fix_test.py` للاختبار
3. تأكد من إعدادات الحساب الحقيقي
4. تحقق من مفاتيح API

## التحديثات المستقبلية

- دعم المزيد من المنصات
- تحسين خوارزميات اقتراح الكميات
- إضافة إشعارات ذكية
- دعم العملات المتعددة
- تحليل الاتجاهات والأنماط
