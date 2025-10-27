# 🤖 بوت التداول على Bybit

## 📋 نظرة عامة

بوت تداول ذكي يقوم بتنفيذ إشارات التداول تلقائياً على منصة Bybit عبر Telegram و TradingView Webhooks.

---

## 📁 هيكل المشروع المنظم

```
botbybit/
├── 📱 ملفات التشغيل
│   ├── app.py              # نقطة البداية - Flask Server
│   ├── bybit_trading_bot.py # بوت Telegram
│   ├── config.py           # الإعدادات
│   ├── database.py         # قاعدة البيانات
│   └── user_manager.py     # إدارة المستخدمين
│
├── 🔌 api/                 # واجهات API
│   ├── __init__.py
│   └── bybit_api.py        # Bybit API (BybitRealAccount + RealAccountManager)
│
├── 🚀 systems/             # الأنظمة المحسنة
│   ├── __init__.py
│   ├── simple_enhanced_system.py        # ⭐ النظام النشط
│   ├── enhanced_portfolio_manager.py    # إدارة المحفظة
│   └── integrated_signal_system.py      # نظام متكامل
│
├── 📡 signals/             # أنظمة الإشارات
│   ├── __init__.py
│   ├── signal_converter.py       # تحويل الإشارات
│   ├── signal_executor.py       # ⭐ تنفيذ الإشارات (الأهم)
│   ├── signal_id_manager.py      # إدارة المعرفات
│   └── signal_position_manager.py # ربط الصفقات بالإشارات
│
├── 👥 developers/          # نظام المطورين
│   ├── __init__.py
│   ├── developer_manager.py
│   ├── developer_config.py
│   ├── developer_example.py
│   └── init_developers.py
│
├── 📊 البيانات
│   ├── *.json              # أزواج التداول
│   ├── trading_bot.db      # قاعدة البيانات
│   └── trading_bot.log     # السجل
│
└── 🚂 النشر (Railway)
    ├── railway.toml
    ├── railway_start.sh
    ├── Dockerfile
    └── requirements.txt
```

---

## 🎯 **المجلدات الرئيسية**

### 🔌 **api/** - واجهات API
**الغرض**: جميع اتصالات API بالمنصات

**الملفات**:
- `bybit_api.py` - Bybit API الكامل
  - `BybitRealAccount`: العمليات الحقيقية
  - `RealAccountManager`: المدير العام

**لإضافة منصة جديدة**:
```
api/
├── bybit_api.py      ← موجود ✅
├── binance_api.py    ← أضف هنا 🔜
└── okx_api.py        ← أضف هنا 🔜
```

---

### 🚀 **systems/** - الأنظمة المحسنة
**الغرض**: الأنظمة المحسنة للبوت

**الملفات**:
1. **`simple_enhanced_system.py`** ⭐ **النشط**
   - يحسن معالجة الإشارات
   - يقيم المخاطر
   - يخطط التنفيذ

2. `enhanced_portfolio_manager.py`
   - يدير المحفظة الإجمالية
   - يحسب الربح/الخسارة

3. `integrated_signal_system.py`
   - يختار أفضل نظام

---

### 📡 **signals/** - أنظمة الإشارات
**الغرض**: معالجة وتنفيذ الإشارات

**الملفات**:
1. **`signal_executor.py`** ⭐ **الأهم**
   - ينفذ الإشارات على Bybit
   - يحسب الكميات
   - يطبق TP/SL

2. `signal_converter.py`
   - يحول تنسيق الإشارات

3. `signal_id_manager.py`
   - يدير المعرفات الفريدة

4. `signal_position_manager.py`
   - يربط الصفقات بالإشارات

---

### 👥 **developers/** - نظام المطورين
**الغرض**: نظام الإشارات الجماعية

**الملفات**:
- `developer_manager.py`
- `developer_config.py`
- `developer_example.py`
- `init_developers.py`

---

## 🔄 **تدفق العمل**

```
1. TradingView → Webhook → app.py
2. app.py → signals/signal_executor.py
3. signal_executor.py → systems/simple_enhanced_system.py (يحسن)
4. signal_executor.py → api/bybit_api.py (ينفذ)
5. api/bybit_api.py → Bybit Platform (صفقة حقيقية)
6. database.py (يحفظ النتيجة)
7. bybit_trading_bot.py (يخبر المستخدم على Telegram)
```

---

## 🚀 **التشغيل**

### متطلبات:
```bash
pip install -r requirements.txt
```

### الإعداد:
1. نسخ `.env` من `env.example`
2. تعديل المتغيرات:
   - `TELEGRAM_TOKEN`
   - `BYBIT_API_KEY`
   - `BYBIT_API_SECRET`

### تشغيل:
```bash
python app.py
```

### النشر على Railway:
1. اربط GitHub
2. Railway سيستخدم `railway.toml` تلقائياً
3. أضف المتغيرات البيئية
4. جاهز! 🚀

---

## 📝 **ملاحظات**

✅ **تم حذف جميع الأنظمة غير المكتملة**
✅ **المشروع منظم 100%**
✅ **جاهز لإضافة منصات جديدة**
✅ **لا توجد عجقة**

---

## 🎯 **إضافة منصة جديدة**

لإضافة Binance مثلاً:

1. **أنشئ** `api/binance_api.py`
2. **أنسخ** من `api/bybit_api.py` وعدّل
3. **أضف** في `real_account_manager`:
   ```python
   elif exchange.lower() == 'binance':
       self.accounts[user_id] = BinanceRealAccount(api_key, api_secret)
   ```
4. **جاهز!** ✅

---

## 📊 **الميزات**

✨ **تداول تلقائي**
✨ **إدارة مخاطر ذكية**
✨ **إحصائيات شاملة**
✨ **دعم حساب تجريبي وحقيقي**
✨ **Spot & Futures**
✨ **نظام إشارات متقدم**

---

## 📞 **الدعم**

للدعم: [@nagdatbasheer](https://t.me/nagdatbasheer)

---

## 📄 **الترخيص**

المشروع للمطور @nagdatbasheer

**حظاً موفقاً في التداول! 📈**

